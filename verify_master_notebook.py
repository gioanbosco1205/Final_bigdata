"""Run every block in a fresh kernel; --mode live (default) or --mode fixture.
Fixture outputs are isolated in report_assets and never overwrite data/.
"""
from __future__ import annotations
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
LOCAL_PACKAGES = ROOT.parent / '.verification' / 'packages'
if LOCAL_PACKAGES.exists():
    sys.path.insert(0, str(LOCAL_PACKAGES))
    os.environ['PYTHONPATH'] = os.pathsep.join([str(LOCAL_PACKAGES), str(ROOT), os.environ.get('PYTHONPATH', '')])
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['live', 'fixture'], default='live')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    output = (args.output or ROOT / 'report_assets' / 'notebook_review_2026-10-03' / args.mode).resolve()
    output.mkdir(parents=True, exist_ok=True)
    source = ROOT / 'DoAn-BigData-GA4-SourceCode-Final.ipynb'
    notebook = nbformat.read(source, as_version=4)
    for cell in notebook.cells:
        if cell.cell_type == 'code':
            cell.outputs, cell.execution_count = [], None
    mode_note = ('DỮ LIỆU KIỂM THỬ TỔNG HỢP — không phải kết quả BigQuery/GA4.' if args.mode == 'fixture'
                 else 'CHẠY BIGQUERY THẬT — xem summary.json để biết block thành công hoặc lỗi.')
    notebook.cells.insert(0, nbformat.v4.new_markdown_cell(f'> **{mode_note}**\n\n'
        'Bản này lưu output từ một kernel Jupyter mới.'))
    if args.mode == 'fixture':
        notebook.cells.insert(1, nbformat.v4.new_code_cell(
            'from tests.notebook_fixtures import install_notebook_fixtures\n'
            '_fixture_patches = install_notebook_fixtures()\n'))
    notebook.metadata['verification'] = {
        'mode': args.mode, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'started_at_utc': datetime.now(timezone.utc).isoformat(), 'synthetic_data': args.mode == 'fixture',
    }
    jupyter_data = output / 'jupyter'
    kernel_folder = jupyter_data / 'kernels' / 'ga4-review'
    kernel_folder.mkdir(parents=True, exist_ok=True)
    (kernel_folder / 'kernel.json').write_text(json.dumps({
        'argv': [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
        'display_name': 'GA4 review (Python)', 'language': 'python',
    }), encoding='utf-8')
    for key, subdir in [('JUPYTER_RUNTIME_DIR', 'runtime'), ('MPLCONFIGDIR', 'matplotlib'), ('IPYTHONDIR', 'ipython')]:
        os.environ[key] = str(output / subdir)
    data_paths = [str(jupyter_data)]
    for location in (LOCAL_PACKAGES, ROOT.parent / '.verification' / 'nbconvert_assets'):
        if (location / 'share' / 'jupyter').exists():
            data_paths.append(str(location / 'share' / 'jupyter'))
    os.environ['JUPYTER_PATH'] = os.pathsep.join(data_paths)
    os.environ['MPLBACKEND'] = 'module://matplotlib_inline.backend_inline'
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['GCP_PROJECT_ID'] = ('test-fixture-project' if args.mode == 'fixture'
                                    else os.environ.get('GCP_PROJECT_ID', 'bigdata-510510'))
    destination = output / f'DoAn-BigData-GA4-SourceCode-Final_{args.mode}_executed.ipynb'

    def on_cell_executed(cell, cell_index, **kwargs):
        errors = [o for o in cell.get('outputs', []) if o.output_type == 'error']
        print(f'{args.mode}: cell {cell_index}: {errors[0].ename if errors else "OK"}', flush=True)
        nbformat.write(notebook, destination)

    client = NotebookClient(notebook, timeout=600, kernel_name='ga4-review', allow_errors=True,
                            resources={'metadata': {'path': str(output)}}, on_cell_executed=on_cell_executed)
    fatal_error = None
    try:
        client.execute()
    except Exception as exc:
        fatal_error = f'{type(exc).__name__}: {exc}'
    nbformat.write(notebook, destination)
    nbformat.validate(notebook)
    blocks = []
    offset = 2 if args.mode == 'fixture' else 1
    for index, cell in enumerate(notebook.cells):
        if cell.cell_type != 'code' or index < offset:
            continue
        source_index = index - offset
        errors = [{'name': o.ename, 'message': o.evalue} for o in cell.outputs if o.output_type == 'error']
        state = 'error' if errors else ('ok' if cell.execution_count is not None else 'not_executed')
        blocks.append({'block': (source_index - 2) // 2, 'source_cell_index': source_index,
                       'execution_count': cell.execution_count, 'status': state, 'errors': errors})
        for plot_index, out in enumerate(cell.outputs):
            if out.output_type in ('display_data', 'execute_result') and 'image/png' in out.data:
                (output / f'block_{(source_index - 2) // 2:02d}_plot_{plot_index}.png').write_bytes(
                    base64.b64decode(out.data['image/png']))
    summary = {
        **dict(notebook.metadata['verification']), 'finished_at_utc': datetime.now(timezone.utc).isoformat(),
        'python_executable': sys.executable, 'executed_notebook': str(destination),
        'total_blocks': len(blocks), 'successful_blocks': sum(b['status'] == 'ok' for b in blocks),
        'failed_blocks': sum(b['status'] == 'error' for b in blocks), 'blocks': blocks, 'fatal_error': fatal_error,
        'limitation': ('Fixtures validate Python execution/export; SQL is not run by BigQuery.' if args.mode == 'fixture'
                       else 'Authentication/query errors prevent live result validation.'),
    }
    (output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    html, _ = HTMLExporter().from_notebook_node(notebook)
    (output / 'notebook.html').write_text(html, encoding='utf-8')
    print(json.dumps({k: summary[k] for k in ('mode', 'total_blocks', 'successful_blocks', 'failed_blocks', 'fatal_error')},
                     ensure_ascii=False), flush=True)
    return 0 if summary['successful_blocks'] == 12 and not fatal_error else 1


if __name__ == '__main__':
    raise SystemExit(main())
