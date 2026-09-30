# 📋 BẢNG THEO DÕI TIẾN ĐỘ DỰ ÁN (TODO TRACKER)

**Đề tài:** Phân tích hành vi Khách hàng trên Dữ liệu Thương mại Điện tử quy mô lớn bằng Google BigQuery SQL & Python (GA4 Dataset)  
**Cập nhật lần cuối:** 2026-09-29 (Dự án đã hoàn thành 100%)

---

## 📊 TỔNG QUAN TIẾN ĐỘ THỰC HIỆN

| Giai đoạn | Tên Giai đoạn | Số Task | Trạng thái | Tiến độ |
| :---: | :--- | :---: | :---: | :---: |
| **Giai đoạn 1** | Chuẩn bị Môi trường & Thiết lập Hạ tầng Kết nối | 4/4 | ✅ Đã hoàn thành | 100% |
| **Giai đoạn 2** | Xây dựng Bộ Truy vấn Xử lý Dữ liệu Lớn BigQuery SQL | 4/4 | ✅ Đã hoàn thành | 100% |
| **Giai đoạn 3** | Xây dựng Pipeline Machine Learning & Phân cụm Khách hàng | 4/4 | ✅ Đã hoàn thành | 100% |
| **Giai đoạn 4** | Xây dựng Ứng dụng Web Dashboard Trực quan hóa (FastAPI & React) | 4/4 | ✅ Đã hoàn thành | 100% |
| **Giai đoạn 5** | Xây dựng Bộ 2 Jupyter Notebooks Chuẩn nộp bài | 2/2 | ✅ Đã hoàn thành | 100% |
| **Giai đoạn 6** | Kiểm thử Toàn diện & Xuất Tài liệu Báo cáo Word 5 Chương | 3/3 | ✅ Đã hoàn thành | 100% |
| **TỔNG CỘNG** | **Toàn bộ Dự án** | **21/21** | 🏆 **HOÀN THÀNH 100%** | **100%** |

---

## 📝 CHI TIẾT TỪNG TASK THEO GIAI ĐOẠN

### 🔹 GIAI ĐOẠN 1: MÔI TRƯỜNG & THIẾT LẬP KẾT NỐI BIGQUERY
- [x] **Task 1.1:** Tạo file `requirements.txt` khai báo đầy đủ các thư viện (`google-cloud-bigquery`, `pandas`, `scikit-learn`, `fastapi`, `recharts`).  
  *Trạng thái: ✅ Đã hoàn thành*
- [x] **Task 1.2:** Khởi tạo cấu trúc các thư mục dự án (`config/`, `sql/`, `src/`, `backend/`, `frontend/`, `notebooks/`, `app/`, `data/cache/`).  
  *Trạng thái: ✅ Đã hoàn thành*
- [x] **Task 1.3:** Xây dựng module `config/settings.py` quản lý biến môi trường, Dataset ID, hằng số phân tích RFM và Persona palette.  
  *Trạng thái: ✅ Đã hoàn thành*
- [x] **Task 1.4:** Xây dựng module `src/bq_client.py` hỗ trợ truy vấn BigQuery từ xa, tự động cache dữ liệu tinh gọn và tạo sample dataset chuẩn GA4.  
  *Trạng thái: ✅ Đã hoàn thành & Đã kiểm tra chạy thử nghiệm (`exit code 0`)*

---

### 🔹 GIAI ĐOẠN 2: BỘ TRUY VẤN XỬ LÝ DỮ LIỆU LỚN BIGQUERY SQL
- [x] **Task 2.1:** Viết file `sql/01_eda_overview.sql`  
  *Nhiệm vụ:* Truy vấn tổng quan KPI (Users, Sessions, Pageviews, Revenue), phân tích đa chiều theo Kênh tiếp thị, Thiết bị và Quốc gia.  
  *Trạng thái: ✅ Đã hoàn thành & Đã kiểm tra chạy thử nghiệm (`exit code 0`)*
- [x] **Task 2.2:** Viết file `sql/02_funnel_analysis.sql`  
  *Nhiệm vụ:* Truy vấn phễu mua sắm 4 bước (`view_item` $\to$ `add_to_cart` $\to$ `begin_checkout` $\to$ `purchase`), tính Conversion Rate, Drop-off Rate và so sánh Mobile vs Desktop.  
  *Trạng thái: ✅ Đã hoàn thành & Đã kiểm tra chạy thử nghiệm (`exit code 0`)*
- [x] **Task 2.3:** Viết file `sql/03_rfm_features.sql`  
  *Nhiệm vụ:* Kỹ thuật tổng hợp đặc trưng RFM + 6 chỉ số hành vi tương tác ở cấp độ từng người dùng (`user_pseudo_id`).  
  *Trạng thái: ✅ Đã hoàn thành & Đã kiểm tra chạy thử nghiệm (`exit code 0`)*
- [x] **Task 2.4:** Viết file `sql/04_market_basket.sql`  
  *Nhiệm vụ:* Bóc tách `UNNEST(items)` trong các đơn hàng mua thành công để lấy danh sách sản phẩm cùng giỏ hàng.  
  *Trạng thái: ✅ Đã hoàn thành & Đã kiểm tra chạy thử nghiệm (`exit code 0`)*

---

### 🔹 GIAI ĐOẠN 3: MACHINE LEARNING PIPELINE & PHÂN CỤM KHÁCH HÀNG
- [x] **Task 3.1:** Xây dựng module `src/data_processor.py`  
  *Nhiệm vụ:* Xử lý ngoại lai (IQR clipping), phép biến đổi Logarit (`np.log1p`), chuẩn hóa dữ liệu bằng `StandardScaler`.  
  *Trạng thái: ✅ Đã hoàn thành & Đã kiểm tra chạy thử nghiệm (`exit code 0`)*
- [x] **Task 3.2:** Xây dựng module `src/clustering.py`  
  *Nhiệm vụ:* Hiện thực hóa thuật toán Elbow Method (Inertia), tính Silhouette Scores từ $K=2$ đến $8$, huấn luyện K-Means ($K=4$), giảm chiều dữ liệu bằng PCA 2D/3D.  
  *Trạng thái: ✅ Đã hoàn thành & Đã kiểm tra chạy thử nghiệm (`Silhouette = 0.4797 > 0.35`)*
- [x] **Task 3.3:** Xây dựng hàm định danh Chân dung Khách hàng `profile_personas()`  
  *Nhiệm vụ:* Tự động gán nhãn 4 nhóm: *VIPs / Loyal Champions, Potential Loyalists, Cart Abandoners / Window Shoppers, At-Risk / Inactive*.  
  *Trạng thái: ✅ Đã hoàn thành & Đã kiểm tra chạy thử nghiệm (`exit code 0`)*
- [x] **Task 3.4:** Xây dựng module `src/market_basket.py`  
  *Nhiệm vụ:* Chuyển đổi giỏ hàng sang One-Hot Matrix, chạy thuật toán Apriori, tính toán 3 chỉ số Support, Confidence, Lift.  
  *Trạng thái: ✅ Đã hoàn thành & Đã kiểm tra chạy thử nghiệm (`exit code 0`)*

---

### 🔹 GIAI ĐOẠN 4: ỨNG DỤNG WEB DASHBOARD TRỰC QUAN HÓA (FASTAPI & REACT)
- [x] **Task 4.1:** Xây dựng Backend FastAPI `backend/api.py` và Frontend React + TypeScript + TailwindCSS.  
  *Trạng thái: ✅ Đã hoàn thành & Đã kiểm tra chạy thử nghiệm (`exit code 0`)*
- [x] **Task 4.2:** Xây dựng Tab 1: Executive Overview & KPI Cards + Traffic Chart.  
  *Trạng thái: ✅ Đã hoàn thành & Đã kiểm tra chạy thử nghiệm (`exit code 0`)*
- [x] **Task 4.3:** Xây dựng Tab 2: Funnel Diagnostics (Bộ lọc thiết bị, Drop-off & Cart Abandonment).  
  *Trạng thái: ✅ Đã hoàn thành & Đã kiểm tra chạy thử nghiệm (`exit code 0`)*
- [x] **Task 4.4:** Xây dựng Tab 3 (Personas & PCA Scatter & User Lookup) và Tab 4 (Market Basket & Action Matrix).  
  *Trạng thái: ✅ Đã hoàn thành & Đã kiểm tra chạy thử nghiệm (`exit code 0`)*

---

### 🔹 GIAI ĐOẠN 5: BỘ 2 JUPYTER NOTEBOOKS CHUẨN NỘP BÀI
- [x] **Task 5.1:** Xây dựng `notebooks/01_eda_and_funnel.ipynb` (EDA & Phân tích Phễu).  
  *Trạng thái: ✅ Đã hoàn thành*
- [x] **Task 5.2:** Xây dựng `notebooks/02_rfm_kmeans_clustering.ipynb` (K-Means, PCA, Apriori).  
  *Trạng thái: ✅ Đã hoàn thành*

---

### 🔹 GIAI ĐOẠN 6: KIỂM THỬ TOÀN DIỆN & TÀI LIỆU BÁO CÁO WORD 5 CHƯƠNG
- [x] **Task 6.1:** Xây dựng & Chạy End-to-End Test toàn bộ mã nguồn (`tests/test_pipeline_e2e.py` & `run_tests.py`).  
  *Nhiệm vụ:* Tự động hóa kiểm tra tính toàn vẹn từ SQL $\to$ Processor $\to$ ML Clustering $\to$ Market Basket $\to$ FastAPI REST API $\to$ Notebooks Syntax.  
  *Trạng thái: ✅ Đã hoàn thành (7/7 tests passed, `exit code 0`)*
- [x] **Task 6.2:** Tạo script khởi chạy nhanh Web Dashboard `run_dashboard.py` (FastAPI & React trên Localhost:8000).  
  *Trạng thái: ✅ Đã hoàn thành*
- [x] **Task 6.3:** Xuất file Tài liệu Báo cáo Mẫu Chi tiết 5 Chương chuẩn học thuật [BAO_CAO_DO_AN_BIG_DATA_5_CHUONG.md](file:///Users/minhkhanhnguyen/Downloads/cu%E1%BB%91i%20k%C3%AC%20Bigdata/BAO_CAO_DO_AN_BIG_DATA_5_CHUONG.md).  
  *Trạng thái: ✅ Đã hoàn thành*
