"""Execute the two modular notebooks and prepare report figures from their outputs."""

from __future__ import annotations

import contextlib
import io
import json
import os
import sys
from pathlib import Path

os.environ["MPLBACKEND"] = "Agg"
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

import pandas as pd
import plotly.graph_objects as go


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "report_assets" / "chapter4"
OUT.mkdir(parents=True, exist_ok=True)
NOTEBOOKS = [
    ROOT / "notebooks" / "01_eda_and_funnel.ipynb",
    ROOT / "notebooks" / "02_rfm_kmeans_clustering.ipynb",
]


def make_html(name: str, figure: go.Figure, caption: str) -> None:
    figure.update_layout(width=1120, height=650, margin=dict(l=70, r=70, t=80, b=65))
    chart = figure.to_html(full_html=False, include_plotlyjs=True)
    html = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<style>body{{margin:0;background:#fff;font-family:Arial,sans-serif;color:#111}}
.page{{width:1180px;margin:0 auto;padding:24px 30px}}
.caption{{font-size:19px;font-weight:700;margin-bottom:12px}}
.source{{font-size:13px;color:#5b6470;margin-top:8px}}
</style></head><body><div class="page"><div class="caption">{caption}</div>
{chart}<div class="source">Nguồn: Kết quả thực thi notebook trên dữ liệu mẫu hiện có của đồ án.</div>
</div></body></html>"""
    (OUT / f"{name}.html").write_text(html, encoding="utf-8")


def run_notebook(path: Path) -> tuple[dict, list[str]]:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    env = {"__name__": "__main__", "__file__": str(path)}
    figures: list[go.Figure] = []
    errors: list[str] = []
    old_cwd = Path.cwd()
    original_show = go.Figure.show
    cell_outputs: list[dict] = []

    def show(figure: go.Figure, *args, **kwargs) -> None:
        figures.append(figure)
        cell_outputs.append({
            "output_type": "display_data",
            "data": {"application/vnd.plotly.v1+json": json.loads(figure.to_json())},
            "metadata": {},
        })

    def display(value) -> None:
        if isinstance(value, pd.DataFrame):
            data = {"text/plain": value.to_string(index=False), "text/html": value.to_html(index=False)}
        else:
            data = {"text/plain": repr(value)}
        cell_outputs.append({"output_type": "display_data", "data": data, "metadata": {}})

    env["display"] = display
    go.Figure.show = show
    os.chdir(path.parent)
    try:
        for index, cell in enumerate(notebook["cells"]):
            if cell["cell_type"] != "code":
                continue
            code = "".join(cell["source"])
            cell_outputs = []
            stream = io.StringIO()
            try:
                with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
                    exec(compile(code, f"{path.name}:cell_{index}", "exec"), env)
                status = "ok"
            except Exception as exc:
                status = f"{type(exc).__name__}: {exc}"
                errors.append(f"cell {index}: {status}")
                error_name = type(exc).__name__
                error_value = str(exc)
            output = stream.getvalue()
            if output:
                cell_outputs.insert(0, {"output_type": "stream", "name": "stdout", "text": output})
            if status != "ok":
                cell_outputs.append({"output_type": "error", "ename": error_name, "evalue": error_value, "traceback": []})
            cell["outputs"] = cell_outputs
            cell["execution_count"] = index
            print(f"{path.name}: cell {index}: {status}", flush=True)
            if output:
                print(output[-900:], flush=True)
            if status != "ok":
                break
    finally:
        go.Figure.show = original_show
        os.chdir(old_cwd)

    output_path = OUT / path.name.replace(".ipynb", "_executed.ipynb")
    output_path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")

    if path.name.startswith("01_") and not errors:
        make_html("hinh_4_1_kenh_tiep_thi", figures[0], "Hình 4.1. Doanh thu và tỷ lệ chuyển đổi theo kênh tiếp thị")
        make_html("hinh_4_2_pheu_mua_hang", figures[1], "Hình 4.2. Phễu chuyển đổi mua hàng trên các thiết bị")
    if path.name.startswith("02_") and not errors:
        make_html("hinh_4_3_chon_k", figures[0], "Hình 4.3. Đánh giá số cụm bằng Inertia và Silhouette")
        make_html("hinh_4_4_pca", figures[1], "Hình 4.4. Phân bố bốn nhóm khách hàng trong không gian PCA")

    return env, errors


def main() -> int:
    results = {}
    all_errors = []
    for path in NOTEBOOKS:
        env, errors = run_notebook(path)
        all_errors.extend(f"{path.name}: {e}" for e in errors)
        if path.name.startswith("01_") and not errors:
            results["eda"] = env["df_eda"].to_dict(orient="records")
            results["funnel"] = env["df_funnel"].to_dict(orient="records")
        if path.name.startswith("02_") and not errors:
            results["cluster_evaluation"] = env["eval_res"]
            results["cluster_summary"] = env["cluster_summary"]
            results["personas"] = env["df_persona_table"].to_dict(orient="records")
            results["basket_rules"] = env["rules"].head(10).to_dict(orient="records")
            results["basket_recommendations"] = env["df_recs"].to_dict(orient="records")
            results["basket_order_count"] = env["n_valid"]
    results["errors"] = all_errors
    (OUT / "execution_summary.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2, default=lambda value: value.item() if hasattr(value, "item") else str(value)), encoding="utf-8"
    )
    print(f"Saved execution summary to {OUT / 'execution_summary.json'}")
    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main())
