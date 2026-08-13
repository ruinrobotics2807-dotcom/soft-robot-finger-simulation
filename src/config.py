# =====================================================================
# FILE: config.py
# VAI TRÒ: Lưu trữ các tham số cấu hình vật liệu và mô phỏng
# =====================================================================
import os

# Thông số vật liệu mặc định (Silicone)
YOUNG_MODULUS = 150.0  # Mô-đun Young (kPa)
POISSON_RATIO = 0.45   # Hệ số Poisson
DENSITY = 1050.0       # Khối lượng riêng (kg/m^3)

# Danh sách tham số khảo sát (Young's Modulus)
E_VALUES = [100.0, 150.0, 200.0]  # kPa

# Thông số mô phỏng
DT = 0.01              # Bước thời gian (s)
GRAVITY = [0.0, -9810.0, 0.0]  # Trọng lực (mm/s^2)

# Thông số dây cáp
CABLE_DISPLACEMENT = 10.0  # Độ co tối đa của dây cáp (mm)

# Đường dẫn tương đối lưu kết quả
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "..", "results")