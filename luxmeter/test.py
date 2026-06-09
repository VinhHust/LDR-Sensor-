import requests
import time
import serial
import csv

URL_SENSOR = "http://192.168.1.3:8080/get?illum"
COM_PORT = "COM3"  
BAUD_RATE = 115200 
CSV_FILENAME = "calibration_steps_data.csv"

try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=0.1)
    print(f"-> Đã kết nối thành công Arduino tại cổng {COM_PORT} (Baud: {BAUD_RATE}).")
    time.sleep(2)  
    ser.reset_input_buffer() 
except Exception as e:
    print(f"LỖI KHỞI ĐỘNG: {e}")
    exit()

with open(CSV_FILENAME, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Lần_Đo', 'Điện_Áp_Trung_Bình(V)', 'Lux_Trung_Bình'])

was_measuring = False
current_step_volt = [] 
current_step_lux = []
step_counter = 0

print("\n--- BẮT ĐẦU QUÉT DỮ LIỆU (CHẾ ĐỘ GỠ LỖI) ---")

try:
    while True:
        try:
            # --- 1. ĐỌC SERIAL TỪ ARDUINO ---
            volt_val = None
            while ser.in_waiting > 0:
                raw_serial = ser.readline().decode('utf-8', errors='ignore').strip()
                if raw_serial: 
                    # X-QUANG 1: Xem Arduino đang thực sự gửi chữ gì lên
                    # print(f"[RAW COM3]: '{raw_serial}'") # Bỏ comment dòng này nếu muốn xem tất cả
                    
                    try:
                        volt_val = float(raw_serial) 
                    except ValueError:
                        print(f"❌ [LỖI SERIAL]: Arduino gửi lên '{raw_serial}' - Đây không phải là SỐ FLOAT, Python từ chối nhận!")

            # --- 2. ĐỌC WI-FI TỪ PHYPHOX ---
            response = requests.get(URL_SENSOR, timeout=0.5).json()
            
            if "status" not in response:
                print("⚠️ [LỖI WI-FI]: Mạng lag, rớt gói tin JSON!")
                continue 
                
            status = response.get("trạng thái", response.get("status", {}))
            is_measuring = status.get("measuring", False)
            
            values = response.get("buffer", {}).get("illum", {}).get("buffer", [])
            
            # X-QUANG 2: Kiểm tra mảng dữ liệu Lux
            if is_measuring and not values:
                print("⚠️ [LỖI PHYPHOX]: Trạng thái đang PLAY nhưng mảng dữ liệu Lux bị RỖNG!")
                
            lux_val = values[-1] if values else None

            # --- 3. LOGIC MÁY TRẠNG THÁI ---
            if is_measuring and not was_measuring:
                step_counter += 1
                current_step_volt.clear()
                current_step_lux.clear()
                print(f"\n⚙️  [LẦN {step_counter}]: Đang gom mẫu dữ liệu ngầm...")

            if is_measuring:
                if volt_val is not None:
                    current_step_volt.append(volt_val)
                if lux_val is not None:
                    current_step_lux.append(lux_val)
                print(f"   -> Đã tích lũy: {len(current_step_volt)} mẫu Volt | {len(current_step_lux)} mẫu Lux", end='\r')

            elif not is_measuring and was_measuring:
                print("\n🛑 Phát hiện lệnh PAUSE! Đang tính toán dữ liệu...")
                if len(current_step_volt) > 0 and len(current_step_lux) > 0:
                    avg_volt = round(sum(current_step_volt) / len(current_step_volt), 3) 
                    avg_lux = round(sum(current_step_lux) / len(current_step_lux), 2)    
                    
                    with open(CSV_FILENAME, mode='a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow([f"Lần {step_counter}", avg_volt, avg_lux])
                    
                    print(f"✅ ĐÃ ĐẨY XUỐNG DÒNG: Lần {step_counter} | Áp_TB: {avg_volt} V | Lux_TB: {avg_lux}")
                else:
                    print("⚠️ Thời gian quá ngắn hoặc DỮ LIỆU BỊ TỪ CHỐI, Hủy lần này.\n")
                    step_counter -= 1

            was_measuring = is_measuring
            time.sleep(0.04) 

        except requests.exceptions.RequestException as e:
            print(f"\n🔌 [LỖI MẠNG]: Mất kết nối tới điện thoại! Chi tiết: {e}")
        except Exception as e:
            pass # Lỗi lặt vặt bỏ qua

except KeyboardInterrupt:
    print(f"\n👋 Đã đóng trạm thu thập.")
    ser.close()