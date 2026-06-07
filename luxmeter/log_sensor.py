import requests
import time
import matplotlib.pyplot as plt

# ==============================================================================
# CẤU HÌNH: Thay địa chỉ IP hiển thị trên App Phyphox (hoặc ứng dụng của bạn) vào đây
# ==============================================================================
URL_SENSOR = "http://192.168.1.5:8080/get?light"  # Bỏ chữ '=full' để lấy dữ liệu mới nhất cho nhanh

# Khởi tạo các mảng để lưu dữ liệu vẽ đồ thị
x_time = []
y_lux = []

# Cấu hình giao diện đồ thị Matplotlib
plt.ion() # Bật chế độ tương tác thời gian thực (Interactive Mode)
fig, ax = plt.subplots(figsize=(8, 5))
line, = ax.plot([], [], 'r-', linewidth=2, label='Độ rọi (Lux)')

ax.set_title("ĐỒ THỊ THEO DÕI ĐỘ SÁNG LUX THỜI GIAN THỰC", fontsize=12, fontweight='bold')
ax.set_xlabel("Thời gian (giây)", fontsize=10)
ax.set_ylabel("Cường độ ánh sáng (Lux)", fontsize=10)
ax.grid(True, linestyle='--', alpha=0.6)
ax.legend(loc='upper right')

start_time = time.time()
print("-> Bắt đầu hút dữ liệu Lux từ điện thoại... Ấn Ctrl+C ở Terminal để dừng.")

try:
    while True:
        try:
            # 1. Dùng requests gửi lệnh gọi qua Wi-Fi để lấy gói dữ liệu JSON
            response = requests.get(URL_SENSOR, timeout=1).json()
            
            # 2. Bóc tách lấy giá trị Lux mới nhất từ bộ đệm của Phyphox
            lux_val = response["buffer"]["light"]["value"][0]
            
            # Tính thời gian trôi qua kể từ lúc chạy code
            current_time = time.time() - start_time
            
            # 3. Lưu dữ liệu vào mảng
            x_time.append(current_time)
            y_lux.append(lux_val)
            
            # Giới hạn đồ thị chỉ hiển thị 50 điểm gần nhất cho đỡ lag
            if len(x_time) > 50:
                x_time.pop(0)
                y_lux.pop(0)
            
            # In ra Terminal để theo dõi số liệu thô
            print(f"Thời gian: {current_time:.1f}s | Độ sáng: {lux_val} Lux")
            
            # 4. Cập nhật dữ liệu mới lên đồ thị mà không cần vẽ lại từ đầu
            line.set_data(x_time, y_lux)
            ax.relim()
            ax.autoscale_view()
            
            # Yêu cầu Matplotlib vẽ ngay lập tức
            plt.draw()
            plt.pause(0.1) # Tương đương lấy mẫu khoảng 10 mẫu/giây (Tần suất mượt mà)
            
        except (requests.exceptions.RequestException, IndexError, KeyError):
            print("Lỗi kết nối Wi-Fi hoặc App chưa bật Remote Access! Đang thử lại...")
            time.sleep(1)

except KeyboardInterrupt:
    print("\n-> Đã dừng chương trình log dữ liệu.")
    plt.ioff() # Tắt chế độ tương tác
    plt.show() # Giữ lại đồ thị cuối cùng trên màn hình