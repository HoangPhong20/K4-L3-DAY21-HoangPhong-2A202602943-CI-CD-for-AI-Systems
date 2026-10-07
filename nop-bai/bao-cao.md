# Báo Cáo Lab Day 21 - CI/CD cho AI Systems

| | |
|---|---|
| Họ và tên | Hoàng Phong |
| MSSV | 2A202602943 |
| Lớp / Khóa | K4 |
| Repo GitHub | https://github.com/HoangPhong20/K4-L3-DAY21-HoangPhong-2A202602943-CI-CD-for-AI-Systems |
| Ngày nộp | 07/10/2026 |

## 1. Bộ Siêu Tham Số Đã Chọn và Lý Do

| Lần chạy | n_estimators | learning_rate | max_depth | f1_score | accuracy |
|---|---|---|---|---|---|
| 1 | 100 | 0.1 | 3 | 0.7109 | 0.8780 |
| 2 | 100 | 0.1 | 3 | 0.7109 | 0.8780 |
| 3 | 50 | 0.05 | 2 | 0.6051 | 0.8460 |
| 4 | 200 | 0.1 | 5 | 0.7149 | 0.8740 |

**Bộ siêu tham số đã chọn:** `n_estimators=200`, `learning_rate=0.1`, `max_depth=5`.

**Lý do:** MLflow ghi nhận lần 4 đạt F1 cao nhất (0.7149), vượt ngưỡng 0.65. Lần 1 và 2 cùng cấu hình, đạt accuracy cao nhất nhưng F1 thấp hơn. Lần 3 đạt F1 0.6051 nên chưa đủ ngưỡng. Learning_rate nhỏ thường cần nhiều cây hơn, tăng chi phí huấn luyện; cây sâu học quan hệ phức tạp hơn nhưng dễ quá khớp. Cấu hình được chọn ưu tiên F1 của lớp dương. Vì các tham số thay đổi đồng thời, chưa thể tách tác động riêng.

## 2. Vì Sao Ngưỡng Chất Lượng Đặt Trên F1 Chứ Không Phải Accuracy

Lớp thu nhập trên 50K chỉ chiếm khoảng 24.8% dữ liệu. Mô hình luôn dự đoán thu nhập thấp vẫn đạt accuracy khoảng 75.2%, dù bỏ sót toàn bộ lớp dương và có F1 bằng 0. F1 là trung bình điều hòa của precision và recall, phản ánh cả dự đoán nhầm lẫn bỏ sót. Lab dùng `f1_score` mặc định với lớp dương `target=1`. Không dùng `average="weighted"` vì lớp đông có thể che khuất kết quả kém của lớp thiểu số; `average="macro"` đánh giá trung bình hai lớp, khác mục tiêu kiểm tra riêng lớp thu nhập cao. Quality Gate yêu cầu F1 ≥ 0.65 trước khi cho phép Release.

## 3. Khó Khăn Gặp Phải và Cách Giải Quyết

| Khó khăn | Nguyên nhân | Cách giải quyết |
|---|---|---|
| Lệnh kiểm tra dữ liệu báo SyntaxError. | Chuỗi truyền qua `python -c` bị thiếu dấu nháy hoặc cắt khi nhập. | Tôi kiểm tra số mẫu bằng lệnh đếm dòng CSV rồi ghép dữ liệu. |
| Lệnh curl và kết quả khó đọc khi chụp ảnh. | JSON không có ký tự xuống dòng cuối. | Tôi thêm `; echo` sau mỗi lệnh curl trong Cloud Shell. |

## 4. So Sánh Bước 2 và Bước 3

| | f1_score | accuracy |
|---|---|---|
| Bước 2 (22.361 mẫu) | 0.7149 | 0.8740 |
| Bước 3 (44.722 mẫu) | 0.7354 | 0.8820 |

**Nhận xét:** Sau khi thêm 22.361 mẫu, F1 tăng khoảng 0.0205 và accuracy tăng 0.0080; cả hai lần đều vượt ngưỡng F1 0.65. Mức cải thiện vừa phải phù hợp với dữ liệu bổ sung từ cùng nguồn, nhưng thêm dữ liệu không đảm bảo chỉ số luôn tăng. Pipeline đã chạy thành công sau commit dữ liệu; API trên VM trả về `status=ok` và nhãn `thu_nhap_cao` cho mẫu kiểm tra sau triển khai.
