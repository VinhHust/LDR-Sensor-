import requests
import time
import serial
import csv

# ================= CẤU HÌNH KẾT NỐI =================
URL_SENSOR = "http://192.168.1.3:8080/get?illum"
COM_PORT = "COM3"  # <-- Sửa lại đúng cổng COM Arduino của bạn
BAUD_RATE = 115200 # <-- ĐÃ SỬA: Đồng bộ tốc độ 115200 với Arduino
CSV_FILENAME = "calibration_steps_data.csv"

# Khởi tạo kết nối Serial với Arduino
try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=0.1)
    print(f"-> Đã kết nối thành công Arduino tại cổng {COM_PORT} (Baud: {BAUD_RATE}).")
    time.sleep(2)  # Chờ mạch khởi động ổn định
except Exception as e:
    print(f"LỖI: Không mở được {COM_PORT}. Hãy đóng Serial Monitor của Arduino IDE!")
    exit()

# Khởi tạo file CSV, đổi tên cột thành Điện Áp cho chuẩn
with open(CSV_FILENAME, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Lần_Đo', 'Điện_Áp_Trung_Bình(V)', 'Lux_Trung_Bình'])

# Các biến quản lý trạng thái máy
was_measuring = False
current_step_volt = [] # Đổi tên biến cho dễ hiểu (volt thay vì adc)
current_step_lux = []
step_counter = 0

try:
    while True:
        try:
            # --- 1. ĐỌC SERIAL TỪ ARDUINO ---
            volt_val = None
            if ser.in_waiting > 0:
                raw_serial = ser.readline().decode('utf-8', errors='ignore').strip()
                # ĐÃ SỬA: Ép kiểu float() thay vì dùng isdigit()
                try:
                    volt_val = float(raw_serial)
                except ValueError:
                    pass # Bỏ qua nếu dính rác truyền thông

            # --- 2. ĐỌC WI-FI TỪ PHYPHOX ---
            response = requests.get(URL_SENSOR, timeout=0.5).json()
            status = response.get("status", {})
            is_measuring = status.get("measuring", False)
            
            values = response.get("buffer", {}).get("illum", {}).get("value", [])
            lux_val = values[-1] if values else None

            # --- 3. LOGIC MÁY TRẠNG THÁI THEO NÚT BẤM ĐIỆN THOẠI ---
            
            # SƯỜN LÊN: Ngay khi bạn bấm PLAY trên điện thoại
            if is_measuring and not was_measuring:
                step_counter += 1
                current_step_volt.clear()
                current_step_lux.clear()
                print(f"⚙️  [LẦN {step_counter}]: Đang gom mẫu dữ liệu ngầm...")

            # ĐANG TRONG TRẠNG THÁI PLAY: Tích lũy dữ liệu vào mảng
            if is_measuring:
                if volt_val is not None:
                    current_step_volt.append(volt_val)
                if lux_val is not None:
                    current_step_lux.append(lux_val)
                # In số mẫu đã gom được trên cùng 1 dòng
                print(f"   -> Đã tích lũy: {len(current_step_volt)} mẫu Volt | {len(current_step_lux)} mẫu Lux", end='\r')

            # SƯỜN XUỐNG: Ngay khi bạn bấm PAUSE trên điện thoại -> XỬ LÝ TRUNG BÌNH & GHI FILE
            elif not is_measuring and was_measuring:
                print("\n🛑 Phát hiện lệnh PAUSE! Đang tính toán dữ liệu...")
                
                if len(current_step_volt) > 0 and len(current_step_lux) > 0:
                    # Tính trung bình cộng toán học
                    avg_volt = round(sum(current_step_volt) / len(current_step_volt), 3) # Lấy 3 chữ số
                    avg_lux = round(sum(current_step_lux) / len(current_step_lux), 2)    # Lấy 2 chữ số
                    
                    # Ghi nối tiếp vào CSV
                    with open(CSV_FILENAME, mode='a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow([f"Lần {step_counter}", avg_volt, avg_lux])
                    
                    print(f"✅ ĐÃ ĐẨY XUỐNG DÒNG: Lần {step_counter} | Áp_TB: {avg_volt} V | Lux_TB: {avg_lux}")
                    print(f"   Dữ liệu đã khóa và lưu vào '{CSV_FILENAME}'")
                    print("-" * 60)
                else:
                    print("⚠️ Thời gian bật PLAY quá ngắn, chưa kịp lấy đủ mẫu. Hủy lần này.\n")
                    step_counter -= 1

            # Lưu lại trạng thái vòng này để so sánh vòng sau
            was_measuring = is_measuring
            time.sleep(0.04) # Tần số quét tầm 25Hz để bắt trọn gói Serial

        except (requests.exceptions.RequestException, KeyError, IndexError):
            pass # Né crash khi rớt mạng Wi-Fi cục bộ

except KeyboardInterrupt:
    print(f"\n👋 Đã đóng trạm thu thập. File của bạn đã sẵn sàng lưu trữ tại: {CSV_FILENAME}")
    ser.close()