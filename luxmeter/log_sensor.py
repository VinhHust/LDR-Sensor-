import requests
import time
import matplotlib.pyplot as plt

URL_SENSOR = "http://192.168.1.3:8080/get?illum"
URL_STATUS = "http://192.168.1.3:8080/get"

x_time = []
y_lux = []

plt.ion()
fig, ax = plt.subplots(figsize=(8, 5))
line, = ax.plot([], [], 'r-', linewidth=2, label='Độ rọi (Lux)')

ax.set_title("ĐỒ THỊ THEO DÕI ĐỘ SÁNG LUX", fontsize=12, fontweight='bold')
ax.set_xlabel("Thời gian (giây)", fontsize=10)
ax.set_ylabel("Cường độ ánh sáng (Lux)", fontsize=10)
ax.grid(True, linestyle='--', alpha=0.6)
ax.legend(loc='upper right')

start_time = time.time()
print("hút dữ liệu Lux")

try:
    while True:
        try:
            response = requests.get(URL_SENSOR, timeout=1).json()

            # Kiểm tra trạng thái đo từ Phyphox
            status = response.get("status", response.get("trạng thái", {}))
            measuring = status.get("measuring", True)

            values = response["buffer"]["illum"]["buffer"]

            if not measuring:
                print(f"Phyphox dang dung | Lux cuoi: {values[-1] if values else '---'} Lux", end='\r')
                plt.pause(0.5)
                continue

            if not values:
                print("Đang chờ dữ liệu từ cảm biến")
                time.sleep(0.5)
                continue

            lux_val = values[-1]
            current_time = time.time() - start_time

            x_time.append(current_time)
            y_lux.append(lux_val)

            if len(x_time) > 50:
                x_time.pop(0)
                y_lux.pop(0)

            print(f"Thời gian: {current_time:.1f}s | Độ sáng: {lux_val} Lux")

            line.set_data(x_time, y_lux)
            ax.relim()
            ax.autoscale_view()
            plt.draw()
            plt.pause(0.1)

        except (requests.exceptions.RequestException, KeyError) as e:
            print(f"Lỗi: {e}")
            time.sleep(1)

except KeyboardInterrupt:
    print("\nDừng")
    plt.ioff()
    plt.show()