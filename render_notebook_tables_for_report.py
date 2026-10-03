"""Render HTML tables captured from executed notebooks for report screenshots."""

import json
from pathlib import Path


root = Path(__file__).resolve().parent / "report_assets" / "chapter4"
path = root / "02_rfm_kmeans_clustering_executed.ipynb"
notebook = json.loads(path.read_text(encoding="utf-8"))

targets = {
    8: ("hinh_4_5_bang_phan_khuc", "Hình 4.5. Bảng đặc điểm bốn nhóm khách hàng"),
    12: ("hinh_4_6_luat_mua_kem", "Hình 4.6. Các luật gợi ý sản phẩm mua kèm"),
}

for index, (name, caption) in targets.items():
    outputs = notebook["cells"][index]["outputs"]
    tables = [output["data"]["text/html"] for output in outputs
              if output.get("output_type") == "display_data" and "text/html" in output.get("data", {})]
    if not tables:
        raise RuntimeError(f"No executed table output found in cell {index}")
    html = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<style>body{{margin:0;background:#fff;color:#17212f;font-family:Arial,sans-serif}}
.page{{width:1180px;margin:0 auto;padding:28px 30px}}
h1{{font-size:22px;margin:0 0 24px}}table{{border-collapse:collapse;width:100%;font-size:14px}}
th,td{{border:1px solid #cad2da;padding:9px 10px;text-align:left;vertical-align:top}}
th{{background:#edf2f7;font-weight:700}}tr:nth-child(even){{background:#f8fafc}}
.source{{font-size:13px;color:#64748b;margin-top:15px}}</style></head>
<body><div class="page"><h1>{caption}</h1>{tables[-1]}
<div class="source">Nguồn: Bảng kết quả được xuất khi thực thi notebook trên dữ liệu mẫu hiện có.</div>
</div></body></html>"""
    (root / f"{name}.html").write_text(html, encoding="utf-8")
    print(root / f"{name}.html")
