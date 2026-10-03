"""Verify the standalone notebook without Google credentials or production exports.

All query results in these tests are explicit fixtures confined to temporary folders.
This suite does not claim to validate a live BigQuery run.
"""

import ast
import contextlib
import hashlib
import io
import json
import os
import runpy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

import nbformat
import duckdb
import numpy as np
import pandas as pd
import sqlglot

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK = ROOT / "DoAn-BigData-GA4-SourceCode-Final.ipynb"


class FixtureJob:
    job_id = "test-fixture-job"
    location = "US"
    total_bytes_processed = 100
    cache_hit = False

    def __init__(self, frame):
        self.frame = frame

    def result(self):
        return self

    def to_dataframe(self, create_bqstorage_client):
        assert create_bqstorage_client is False
        return self.frame.copy()


class FixtureClient:
    def __init__(self, frames, error=None):
        self.frames = frames
        self.error = error
        self.queries = []

    def query(self, sql, **kwargs):
        self.queries.append(sql)
        if self.error is not None:
            raise self.error
        return FixtureJob(self.frames[len(self.queries) - 1])


class TestMasterNotebook(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nb = nbformat.read(NOTEBOOK, as_version=4)

    def code(self, index):
        return "\n".join(line for line in self.nb.cells[index].source.splitlines()
                         if not line.lstrip().startswith(("!", "%")))

    def environment(self, directory, client):
        # Execute the actual notebook helper definitions, without authentication.
        from google.cloud import bigquery
        from datetime import datetime, timezone
        env = {
            "bigquery": bigquery, "datetime": datetime, "timezone": timezone,
            "hashlib": hashlib, "json": json, "pd": pd,
            "bq_client": client, "PROJECT_ID": "test-project",
            "SOURCE_TABLE": "bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*",
            "START_DATE": "20201101", "END_DATE": "20210131",
            "QUERY_MANIFEST": {}, "LOCAL_DATA_DIR": Path(directory),
        }
        tree = ast.parse(self.code(4))
        functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
        exec(compile(ast.Module(body=functions, type_ignores=[]), "notebook_helpers", "exec"), env)
        return env

    def test_schema_python_and_bigquery_sql(self):
        nbformat.validate(self.nb)
        sql_count = 0
        for index, cell in enumerate(self.nb.cells):
            if cell.cell_type != "code":
                continue
            tree = ast.parse(self.code(index))
            self.assertEqual(cell.outputs, [])
            self.assertIsNone(cell.execution_count)
            for node in tree.body:
                if not isinstance(node, ast.Assign):
                    continue
                if not any(isinstance(target, ast.Name) and target.id.startswith("sql_")
                           for target in node.targets):
                    continue
                sql = ast.literal_eval(node.value)
                sqlglot.parse_one(sql, read="bigquery")
                self.assertIn("_TABLE_SUFFIX BETWEEN '20201101' AND '20210131'", sql)
                sql_count += 1
        self.assertEqual(sql_count, 4)
        code = "\n".join(self.code(i) for i, c in enumerate(self.nb.cells) if c.cell_type == "code")
        for banned in ("ensure_sample_data_exists", "read_csv", "read_parquet", "np.random",
                       "84.89", "64.91", "DummyKey", "52.3, 43.1"):
            self.assertNotIn(banned, code)

    def test_query_failure_never_reads_existing_csv(self):
        with tempfile.TemporaryDirectory() as directory:
            sentinel = Path(directory) / "eda_overview.csv"
            sentinel.write_text("unverified-old-file", encoding="utf-8")
            client = FixtureClient([], error=PermissionError("denied"))
            env = self.environment(directory, client)
            env["QUERY_MANIFEST"]["eda_overview"] = {"job_id": "old-job"}
            with self.assertRaisesRegex(RuntimeError, "BigQuery thất bại"):
                env["query_bigquery"]("SELECT 1", "eda_overview")
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "unverified-old-file")
            self.assertNotIn("eda_overview", env["QUERY_MANIFEST"])
            self.assertFalse((Path(directory) / "eda_overview.metadata.json").exists())

    def test_missing_client_and_empty_results_raise(self):
        with tempfile.TemporaryDirectory() as directory:
            env = self.environment(directory, None)
            with self.assertRaisesRegex(RuntimeError, "Chưa kết nối"):
                env["query_bigquery"]("SELECT 1", "eda_overview")
            env["bq_client"] = FixtureClient([pd.DataFrame()])
            with self.assertRaisesRegex(ValueError, "không trả về dữ liệu"):
                env["query_bigquery"]("SELECT 1", "eda_overview")
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_exports_preserve_query_results_and_job_evidence(self):
        frame = pd.DataFrame({"id": ["fixture-a", "fixture-b"], "amount": [12.5, 0.0]})
        with tempfile.TemporaryDirectory() as directory:
            env = self.environment(directory, FixtureClient([frame]))
            sql = "SELECT 'fixture-a' AS id"
            result = env["query_bigquery"](sql, "rfm_features")
            pd.testing.assert_frame_equal(result, frame)
            pd.testing.assert_frame_equal(pd.read_csv(Path(directory) / "rfm_features.csv"), frame)
            pd.testing.assert_frame_equal(pd.read_parquet(Path(directory) / "rfm_features.parquet"), frame)
            metadata = json.loads((Path(directory) / "rfm_features.metadata.json").read_text())
            self.assertEqual(metadata["job_id"], "test-fixture-job")
            self.assertEqual(metadata["rows"], 2)
            self.assertEqual(metadata["query_sha256"], hashlib.sha256(sql.encode()).hexdigest())
            self.assertEqual((Path(directory) / "rfm_features.sql").read_text(), sql)

    def test_funnel_sql_groups_source_device_and_counts_users_once(self):
        tree = ast.parse(self.code(8))
        assignment = next(node for node in tree.body if isinstance(node, ast.Assign)
                          and any(isinstance(target, ast.Name) and target.id == "sql_funnel"
                                  for target in node.targets))
        query = sqlglot.parse_one(ast.literal_eval(assignment.value), read="bigquery")
        # SELECT aliases shadow unqualified FROM names in BigQuery. Grouping must
        # resolve to the source column, not the IF(GROUPING(...)) output alias.
        grouped_columns = list(query.args["group"].find_all(sqlglot.exp.Column))
        self.assertTrue(grouped_columns)
        self.assertTrue(all(column.table == "p" for column in grouped_columns))
        self.assertTrue(all(column.name == "device_category" for column in grouped_columns))
        # Execute the actual final aggregation with overlapping user IDs on two
        # devices, so the 'all' row cannot accidentally sum device user counts.
        query.set("with_", None)
        purchases = pd.DataFrame([
            ["fixture-a", "desktop", 1, 2, 3, 4],
            ["fixture-a", "mobile", 1, 2, None, None],
            ["fixture-b", "desktop", 1, None, None, None],
            ["fixture-c", "mobile", 1, 2, 3, None],
        ], columns=["user_pseudo_id", "device_category", "view_ts", "cart_ts", "checkout_ts", "purchase_ts"])
        with duckdb.connect() as connection:
            connection.register("purchases", purchases)
            result = connection.execute(query.sql(dialect="duckdb")).df().set_index("device_category")
        self.assertEqual(result.loc["all"].tolist(), [3, 2, 2, 1])
        self.assertEqual(result.loc["desktop"].tolist(), [2, 1, 1, 1])
        self.assertEqual(result.loc["mobile"].tolist(), [2, 2, 1, 0])

    def test_save_failure_does_not_record_success(self):
        with tempfile.TemporaryDirectory() as directory:
            env = self.environment(directory, FixtureClient([pd.DataFrame({"x": [1]})]))
            with patch.object(pd.DataFrame, "to_parquet", side_effect=OSError("disk full")):
                with self.assertRaisesRegex(RuntimeError, "không lưu được"):
                    env["query_bigquery"]("SELECT 1 AS x", "rfm_features")
            self.assertNotIn("rfm_features", env["QUERY_MANIFEST"])
            self.assertFalse((Path(directory) / "rfm_features.metadata.json").exists())

    def test_bad_project_stops_before_auth_and_clears_old_frames(self):
        for project in ("", "bigquery-public-data"):
            env = {"os": os, "Path": Path, "df_rfm": "stale", "bq_client": "stale"}
            with patch.dict(os.environ, {"GCP_PROJECT_ID": project}):
                with self.assertRaisesRegex(ValueError, "PROJECT_ID"):
                    exec(self.code(4), env)
            self.assertIsNone(env["bq_client"])
            self.assertNotIn("df_rfm", env)

    def test_builder_generates_the_same_cells(self):
        tree = ast.parse((ROOT / "build_final_notebook.py").read_text(encoding="utf-8"))
        calls = sorted((node for node in ast.walk(tree) if isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Name)
                        and node.func.id in {"new_code_cell", "new_markdown_cell"}),
                       key=lambda node: node.lineno)
        self.assertEqual(len(calls), len(self.nb.cells))
        for call, cell in zip(calls, self.nb.cells):
            self.assertEqual(ast.literal_eval(call.args[0]).strip(), cell.source.strip())
        with tempfile.TemporaryDirectory() as directory:
            previous_cwd = Path.cwd()
            try:
                os.chdir(directory)
                with contextlib.redirect_stdout(io.StringIO()):
                    runpy.run_path(str(ROOT / 'build_final_notebook.py'))
                generated = nbformat.read(Path(directory) / NOTEBOOK.name, as_version=4)
                nbformat.validate(generated)
                self.assertEqual(generated.metadata, self.nb.metadata)
                self.assertEqual([c.source for c in generated.cells], [c.source for c in self.nb.cells])
            finally:
                os.chdir(previous_cwd)

    def test_entire_analysis_pipeline_with_explicit_test_fixtures(self):
        eda = pd.DataFrame([
            ["overall", None, None, None, 60, 90, 200, 10, 250.0],
            ["channel", "organic", None, None, 40, 60, 140, 8, 200.0],
            ["channel", "direct", None, None, 30, 30, 60, 2, 50.0],
            ["device", None, "desktop", None, 40, 60, 140, 8, 200.0],
            ["device", None, "mobile", None, 30, 30, 60, 2, 50.0],
        ], columns=["aggregation_level", "traffic_medium", "device_category", "country",
                    "total_users", "total_sessions", "total_pageviews", "total_purchases", "total_revenue_usd"])
        funnel = pd.DataFrame([
            ["all", 60, 25, 15, 10], ["desktop", 40, 20, 12, 8], ["mobile", 30, 10, 5, 2]
        ], columns=["device_category", "step1_view_item", "step2_add_to_cart", "step3_begin_checkout", "step4_purchase"])
        rfm = pd.DataFrame([{
            "user_pseudo_id": f"fixture-{i}", "recency_days": i % 90,
            "frequency_sessions": 1 + i % 8, "monetary_usd": float((i % 5) * 50),
            "view_item_count": 1 + i % 20, "add_to_cart_count": i % 7,
            "checkout_count": i % 4, "purchase_count": int(i % 5 > 0),
            "cart_to_view_ratio": (i % 7) / (1 + i % 20),
            "total_engagement_time_sec": float(10 + (i * 37) % 900), "total_pageviews": 2 + i % 30,
        } for i in range(60)]).convert_dtypes()
        basket = pd.DataFrame([
            {"transaction_id": f"fixture-tx-{i}", "item_name": item,
             "event_timestamp": i + 1, "user_pseudo_id": f"fixture-{i}",
             "item_id": item, "price_in_usd": 10.0}
            for i in range(6) for item in (["A", "B"] if i < 3 else ["C", "D"])
        ])
        client = FixtureClient([eda, funnel, rfm, basket])
        with tempfile.TemporaryDirectory() as directory:
            env = self.environment(Path(directory) / "bigquery_exports", client)
            env["display"] = lambda *args, **kwargs: None
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            with patch.object(plt, "show"), contextlib.redirect_stdout(io.StringIO()):
                exec(self.code(2).replace("from IPython.display import display", ""), env)
                for i in (6, 8, 10, 12, 14, 16, 18, 20, 22, 24):
                    if i == 24:
                        (env["LOCAL_DATA_DIR"] / "old_mock.csv").write_text("old", encoding="utf-8")
                    exec(compile(self.code(i), f"notebook_cell_{i}", "exec"), env)
            plt.close("all")
            self.assertEqual(len(client.queries), 4)
            self.assertEqual(env["total_users"], 60)  # Not 70 from summed channel rows.
            self.assertEqual(env["s1"], 60)  # Not 70 from summed devices.
            self.assertEqual(len(env["df_segmented"]), 60)
            self.assertFalse(env["df_rules"].empty)
            self.assertIn("fixture-tx-", pd.read_csv(env["LOCAL_DATA_DIR"] / "market_basket.csv").iloc[0]["transaction_id"])
            self.assertTrue((env["LOCAL_DATA_DIR"] / "query_manifest.json").exists())
            self.assertTrue((Path(directory) / "ga4_bigquery_exports.zip").exists())
            with ZipFile(Path(directory) / "ga4_bigquery_exports.zip") as archive:
                self.assertNotIn("old_mock.csv", archive.namelist())
                self.assertIn("funnel_metrics.csv", archive.namelist())
                self.assertIn("analysis_metadata.json", archive.namelist())
                self.assertEqual(len(archive.namelist()), 26)

    def test_negative_features_are_rejected_without_modifying_source(self):
        from sklearn.preprocessing import StandardScaler
        features = ast.literal_eval(ast.parse(self.code(12)).body[0].value)
        frame = pd.DataFrame({col: [0.0, 1.0] for col in features})
        frame.loc[1, 'monetary_usd'] = -100
        original = frame.copy(deep=True)
        env = {'df_rfm': frame, 'pd': pd, 'np': np, 'StandardScaler': StandardScaler}
        with self.assertRaisesRegex(ValueError, 'giá trị âm'):
            exec(self.code(12), env)
        pd.testing.assert_frame_equal(frame, original)

    def test_zero_denominator_percentage_is_undefined(self):
        with tempfile.TemporaryDirectory() as directory:
            env = self.environment(directory, None)
            self.assertTrue(np.isnan(env['percentage'](0, 0)))
            self.assertEqual(env['percentage'](1, 4), 25)

    def test_export_rejects_modified_query_data(self):
        # All provenance gates are satisfied, but CSV bytes differ from saved hashes.
        with tempfile.TemporaryDirectory() as directory:
            client = FixtureClient([pd.DataFrame({'x': [1]})] * 4)
            env = self.environment(directory, client)
            for name in ('eda_overview', 'funnel_analysis', 'rfm_features', 'market_basket'):
                env['query_bigquery']('SELECT 1 AS x', name)
            env.update({'SEGMENTATION_JOB_ID': 'test-fixture-job',
                        'PCA_JOB_ID': 'test-fixture-job', 'RULES_JOB_ID': 'test-fixture-job'})
            (Path(directory) / 'eda_overview.csv').write_text('x\n999\n', encoding='utf-8')
            with self.assertRaisesRegex(RuntimeError, 'đã thay đổi'):
                exec(self.code(24), env)

    def test_basket_sql_separates_same_transaction_id_for_different_users(self):
        sql = next(ast.literal_eval(node.value) for node in ast.parse(self.code(20)).body
                   if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'sql_basket'
                                                          for t in node.targets))
        query = sqlglot.parse_one(sql, read='bigquery')
        purchases = query.args['with_'].expressions[1].this.copy()
        # Run the actual transaction identity expression against colliding IDs.
        data = pd.DataFrame({'event_timestamp': [1, 2], 'user_pseudo_id': ['user-a', 'user-b'],
                             'transaction_id': ['shared-order', 'shared-order'], 'items': ['A', 'B']})
        with duckdb.connect() as connection:
            connection.register('raw_purchases', data)
            result = connection.execute(purchases.sql(dialect='duckdb')).df()
        self.assertEqual(result['transaction_id'].nunique(), 2)

    def test_basket_rules_keep_full_precision_and_directions(self):
        # Eight of 201 orders: 3.9800995...%, displayed 3.98 without quantizing the export.
        rows = []
        for i in range(201):
            items = ['A', 'B'] if i < 9 else [f'rare-{i}-a', f'rare-{i}-b']
            rows.extend({'transaction_id': f'tx-{i}', 'item_name': item} for item in items)
        with tempfile.TemporaryDirectory() as directory:
            env = self.environment(directory, FixtureClient([pd.DataFrame(rows)]))
            env.update({'np': np, 'display': lambda *args: None})
            exec(self.code(20), env)
            self.assertEqual(len(env['df_rules']), 2)
            self.assertAlmostEqual(env['df_rules']['Support (%)'].iloc[0], 900 / 201, places=12)
            self.assertGreater(env['df_rules']['Lift (Độ Nâng)'].iloc[0], 1)

    def test_insights_reject_stale_query_results(self):
        env = {'QUERY_MANIFEST': {name: {'job_id': 'current'} for name in
               ('eda_overview', 'funnel_analysis', 'rfm_features', 'market_basket')},
               'SEGMENTATION_JOB_ID': 'old', 'RULES_JOB_ID': 'old'}
        with self.assertRaisesRegex(RuntimeError, 'không khớp'):
            exec(self.code(22), env)

    def test_preprocessing_accepts_bigquery_nullable_types_and_decimal_cap(self):
        from sklearn.preprocessing import StandardScaler
        tree = ast.parse(self.code(12))
        features = ast.literal_eval(tree.body[0].value)
        frame = pd.DataFrame({
            col: pd.Series([0] * 99 + [33, 91], dtype="Int64")
            for col in features
        })
        frame["monetary_usd"] = frame["monetary_usd"].astype("Float64")
        frame["cart_to_view_ratio"] = pd.Series([0.0] * 99 + [0.4, 0.8], dtype="Float64")
        frame.loc[0, "frequency_sessions"] = pd.NA
        raw = frame.copy(deep=True)
        # This cap reproduces the failure reported from Colab's BigQuery result.
        q1, q3 = frame["recency_days"].quantile([0.01, 0.99])
        cap = q3 + 1.5 * (q3 - q1)
        self.assertEqual(cap, 82.5)
        with self.assertRaisesRegex(TypeError, "82.5"):
            frame["recency_days"].clip(upper=cap)
        env = {"df_rfm": frame, "pd": pd, "np": np, "StandardScaler": StandardScaler}
        with contextlib.redirect_stdout(io.StringIO()):
            exec(self.code(12), env)
        self.assertEqual(env["df_clipped"]["recency_days"].iloc[-1], 82.5)
        self.assertEqual(env["df_clean"]["frequency_sessions"].iloc[0], 0.0)
        self.assertTrue(np.isfinite(env["X_scaled"]).all())
        self.assertEqual(env["X_scaled"].shape, (101, 9))
        pd.testing.assert_frame_equal(frame, raw)  # Source query results remain intact.

    def test_empty_rules_do_not_crash_or_invent_recommendations(self):
        rows = [{"transaction_id": f"tx-{i}", "item_name": f"item-{i}-{j}"}
                for i in range(30) for j in range(2)]
        with tempfile.TemporaryDirectory() as directory:
            env = self.environment(directory, FixtureClient([pd.DataFrame(rows)]))
            env.update({"np": np, "display": lambda *args: None})
            exec(self.code(20), env)
            self.assertEqual(env["num_tx"], 30)
            self.assertTrue(env["df_rules"].empty)
            self.assertEqual(list(env["df_rules"].columns), env["rule_columns"])

    def test_funnel_sql_respects_time_order_and_device(self):
        sql = next(ast.literal_eval(node.value) for node in ast.parse(self.code(8)).body
                   if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "sql_funnel"
                                                          for t in node.targets))
        query = sqlglot.parse_one(sql, read="bigquery")
        query.args["with_"].expressions[0].set("this", sqlglot.parse_one("SELECT * FROM fixture_events"))
        rows = []
        for user, device, sequence in [
            ("a", "desktop", [("view_item", 1), ("add_to_cart", 2), ("begin_checkout", 3), ("purchase", 4)]),
            ("a", "mobile", [("view_item", 1), ("add_to_cart", 2), ("begin_checkout", 3), ("purchase", 4)]),
            ("b", "desktop", [("add_to_cart", 1), ("view_item", 2), ("begin_checkout", 3), ("purchase", 4)]),
            ("c", "desktop", [("begin_checkout", 1), ("view_item", 2), ("add_to_cart", 3),
                                ("begin_checkout", 4), ("purchase", 5)]),
            ("d", "desktop", [("view_item", 1), ("add_to_cart", 2), ("begin_checkout", 3), ("purchase", 3)]),
            ("e", "desktop", [("view_item", 1)]),
            ("e", "mobile", [("add_to_cart", 2), ("begin_checkout", 3), ("purchase", 4)]),
            ("f", "desktop", [("view_item", 1), ("add_to_cart", 2), ("purchase", 3)]),
        ]:
            rows.extend([user, device, event, timestamp] for event, timestamp in sequence)
        events = pd.DataFrame(rows, columns=["user_pseudo_id", "device_category", "event_name", "event_timestamp"])
        with duckdb.connect() as connection:
            connection.register("fixture_events", events)
            result = connection.execute(query.sql(dialect="duckdb")).df().set_index("device_category")
        self.assertEqual(result.loc["all"].tolist(), [6, 4, 3, 2])
        self.assertEqual(result.loc["mobile"].tolist(), [1, 1, 1, 1])

    def test_sparse_purchase_feature_is_not_clipped_to_zero(self):
        from sklearn.preprocessing import StandardScaler
        features = ast.literal_eval(ast.parse(self.code(12)).body[0].value)
        frame = pd.DataFrame({col: np.zeros(200) for col in features})
        frame.loc[199, 'monetary_usd'] = 1000.0
        env = {"df_rfm": frame, "pd": pd, "np": np, "StandardScaler": StandardScaler}
        with contextlib.redirect_stdout(io.StringIO()):
            exec(self.code(12), env)
        self.assertEqual(env['df_clipped'].loc[199, 'monetary_usd'], 1000.0)
        self.assertIn('monetary_usd', env['sparse_features_preserved'])
        self.assertGreater(env['df_log'].loc[199, 'monetary_usd'], 0)
        self.assertTrue(np.isfinite(env['X_scaled']).all())

    def test_preprocessing_rejects_infinite_features(self):
        from sklearn.preprocessing import StandardScaler
        features = ast.literal_eval(ast.parse(self.code(12)).body[0].value)
        frame = pd.DataFrame({col: [0.0, 1.0] for col in features})
        for invalid in (np.inf, -np.inf):
            frame.loc[1, 'monetary_usd'] = invalid
            env = {"df_rfm": frame, "pd": pd, "np": np, "StandardScaler": StandardScaler}
            with self.assertRaisesRegex(ValueError, "vô cực"):
                exec(self.code(12), env)

    def test_silhouette_preserves_a_rare_cluster_with_bounded_memory(self):
        from sklearn.metrics import silhouette_score
        tree = ast.parse(self.code(14))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef))
        calls = []
        def capture(matrix, labels):
            calls.append((matrix.copy(), labels.copy()))
            return silhouette_score(matrix, labels)
        env = {'pd': pd, 'np': np, 'silhouette_score': capture}
        exec(compile(ast.Module(body=[function], type_ignores=[]), 'silhouette_helper', 'exec'), env)
        matrix = np.arange(6000, dtype=float).reshape(-1, 1)
        labels = np.array([0] * 5999 + [1])
        score = env['estimate_silhouette'](matrix, labels, max_samples=20)
        self.assertTrue(np.isfinite(score))
        self.assertEqual(len(calls[0][0]), 20)
        self.assertEqual(set(calls[0][1]), {0, 1})
        self.assertEqual(score, env['estimate_silhouette'](matrix, labels, max_samples=20))
        with self.assertRaisesRegex(ValueError, "Silhouette"):
            env['estimate_silhouette'](matrix, np.zeros(6000))

    def test_valid_empty_market_basket_is_exported_without_rules(self):
        empty = pd.DataFrame(columns=['transaction_id', 'item_name', 'item_id', 'user_pseudo_id',
                                      'event_timestamp', 'price_in_usd'])
        with tempfile.TemporaryDirectory() as directory:
            env = self.environment(directory, FixtureClient([empty]))
            env.update({'np': np, 'display': lambda *args: None})
            with contextlib.redirect_stdout(io.StringIO()):
                exec(self.code(20), env)
            self.assertTrue(env['df_rules'].empty)
            self.assertEqual(env['num_tx'], 0)
            self.assertEqual(env['QUERY_MANIFEST']['market_basket']['rows'], 0)
            self.assertTrue((Path(directory) / 'market_basket.metadata.json').exists())

    def test_failed_rfm_refresh_invalidates_dependent_models(self):
        with tempfile.TemporaryDirectory() as directory:
            env = self.environment(directory, FixtureClient([], error=PermissionError('denied')))
            env.update({'X_scaled': 'stale', 'df_segmented': 'stale', 'SEGMENTATION_JOB_ID': 'old'})
            with self.assertRaises(RuntimeError):
                env['query_bigquery']('SELECT 1', 'rfm_features')
            for variable in ('X_scaled', 'df_segmented', 'SEGMENTATION_JOB_ID'):
                self.assertNotIn(variable, env)

    def test_report_export_rejects_stale_models(self):
        env = {'QUERY_MANIFEST': {name: {'job_id': 'new'} for name in
               ('eda_overview', 'funnel_analysis', 'rfm_features', 'market_basket')},
               'SEGMENTATION_JOB_ID': 'old', 'PCA_JOB_ID': 'old'}
        with self.assertRaisesRegex(RuntimeError, "Phân cụm/PCA"):
            exec(self.code(24), env)

    def test_persona_requires_four_clusters_and_handles_no_revenue(self):
        tree = ast.parse(self.code(18))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef))
        env = {'pd': pd}
        exec(compile(ast.Module(body=[function], type_ignores=[]), 'persona_helper', 'exec'), env)
        frame = pd.DataFrame({'cluster': [0, 1, 2, 3], 'monetary_usd': [0.0] * 4,
                              'recency_days': [0, 1, 2, 3], 'frequency_sessions': [1] * 4,
                              'cart_to_view_ratio': [0.0] * 4})
        result = env['assign_persona_dynamically'](frame)
        self.assertEqual(result['persona'].nunique(), 4)
        self.assertTrue(result['persona'].str.contains('chưa có doanh thu').all())
        with self.assertRaisesRegex(ValueError, "đúng 4 cụm"):
            env['assign_persona_dynamically'](frame.iloc[:3])


if __name__ == "__main__":
    unittest.main(verbosity=2)
