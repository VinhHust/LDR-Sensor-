import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. ĐỌC DỮ LIỆU TỪ FILE CSV
csv_filename = "calibration_steps_data1.csv"
try:
    data = pd.read_csv(csv_filename)
except FileNotFoundError:
    print(f"Lỗi: Không tìm thấy file {csv_filename}. Hãy chắc chắn nó nằm cùng thư mục!")
    exit()

# 2. TÁCH LẤY 2 CỘT TỌA ĐỘ (X = Điện áp, Y = Lux)
# Lưu ý: Tên cột phải khớp chính xác 100% với file CSV
X = data['Điện_Áp_Trung_Bình(V)'].values
Y = data['Lux_Trung_Bình'].values

# 3. TÍNH TOÁN HỒI QUY TUYẾN TÍNH (LINEAR REGRESSION)
# Dùng hàm polyfit bậc 1 để tìm phương trình đường thẳng Y = aX + b
a, b = np.polyfit(X, Y, 1)

# Tính đường dự đoán và hệ số tin cậy R-squared (R²)
Y_pred = a * X + b
r_squared = 1 - (sum((Y - Y_pred)**2) / sum((Y - np.mean(Y))**2))

# In kết quả ra Terminal
print("\n" + "="*50)
print(" KẾT QUẢ HỒI QUY TUYẾN TÍNH")
print("="*50)
print(f"-> Phương trình: Lux = {a:.2f} * V + {b:.2f}")
print(f"-> Hệ số tin cậy (R²): {r_squared:.4f} (Càng gần 1.0 càng chuẩn)")
print("="*50 + "\n")

# 4. VẼ ĐỒ THỊ BÁO CÁO
plt.figure(figsize=(10, 6))

# Vẽ các điểm thực nghiệm (Scatter plot)
plt.scatter(X, Y, color='blue', s=80, edgecolor='black', label='Dữ liệu thực nghiệm', zorder=5)

# Vẽ đường thẳng xu hướng (Trendline)
plt.plot(X, Y_pred, color='red', linewidth=2, label='Đường hồi quy tuyến tính', zorder=4)

# Ghi chú phương trình lên góc đồ thị
equation_text = f"Phương trình: Lux = {a:.2f} * V {b:+.2f}\nĐộ tin cậy R² = {r_squared:.4f}"
plt.text(0.05, 0.95, equation_text, transform=plt.gca().transAxes, fontsize=12,
         verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', edgecolor='black'))

# Trang trí nhãn dán
plt.title('ĐỒ THỊ HIỆU CHUẨN CẢM BIẾN ÁNH SÁNG (LDR)', fontsize=14, fontweight='bold')
plt.xlabel('Điện áp đầu ra cảm biến - Vout (V)', fontsize=12)
plt.ylabel('Cường độ ánh sáng thực tế - (Lux)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(loc='lower right')

# Hiển thị đồ thị
plt.tight_layout()
plt.show()