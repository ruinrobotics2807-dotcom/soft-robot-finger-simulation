# =====================================================================
# FILE: main.py
# VAI TRÒ: Chạy mô phỏng, thực hiện khảo sát tham số và xuất đồ thị
# =====================================================================
import os
import sys

# 1. THIẾT LẬP ĐƯỜNG DẪN TƯƠNG ĐỐI CHO MÔI TRƯỜNG SOFA
SOFA_ROOT = os.environ.get("SOFA_ROOT", r"D:\Aira Lab\v26.06.00")
SOFAPYTHON3_ROOT = os.environ.get("SOFAPYTHON3_ROOT", r"D:\Aira Lab\v26.06.00\plugins\SofaPython3")

dll_directories = [
    os.path.join(SOFA_ROOT, "bin"),
    os.path.join(SOFA_ROOT, "lib"),
    os.path.join(SOFAPYTHON3_ROOT, "bin"),
    os.path.join(SOFAPYTHON3_ROOT, "lib"),
]

if hasattr(os, 'add_dll_directory'):
    for folder in dll_directories:
        if os.path.exists(folder):
            try:
                os.add_dll_directory(folder)
            except Exception:
                pass

site_packages = os.path.join(SOFAPYTHON3_ROOT, "lib", "python3", "site-packages")
if os.path.exists(site_packages) and site_packages not in sys.path:
    sys.path.insert(0, site_packages)

import Sofa
import Sofa.Core
import SofaRuntime
import matplotlib.pyplot as plt

from config import *
import finger_model

def run_simulation(young_modulus):
    """
    Chạy 1 phiên mô phỏng ứng với giá trị Young's Modulus cụ thể.
    """
    root = Sofa.Core.Node(f"root_{young_modulus}")
    finger_model.createScene(root, young_modulus=young_modulus)
    Sofa.Simulation.init(root)

    finger_dof = root.SoftFinger.dof
    cable_constraint = root.SoftFinger.Cable.cableConstraint

    init_positions = finger_dof.position.value
    tip_index = 0
    min_dist = float('inf')
    for idx, pos in enumerate(init_positions):
        dist = pos[0]**2 + pos[1]**2 + (pos[2] - 100.0)**2
        if dist < min_dist:
            min_dist = dist
            tip_index = idx

    initial_tip_x = init_positions[tip_index][0]

    time_steps = []
    tip_displacements = []
    total_steps = 200

    print(f"\n---> Chạy mô phỏng với Young's Modulus E = {young_modulus} kPa")
    for step in range(total_steps):
        current_displacement = (step / total_steps) * CABLE_DISPLACEMENT
        cable_constraint.findData('value').value = [current_displacement]

        Sofa.Simulation.animate(root, DT)
        time = step * DT
        
        current_pos = finger_dof.position.value[tip_index]
        delta_x = current_pos[0] - initial_tip_x
        
        time_steps.append(time)
        tip_displacements.append(delta_x)

    return time_steps, tip_displacements

def main():
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)

    plt.figure(figsize=(9, 5.5))
    colors = ['r', 'b', 'g']
    
    print("==================================================")
    print(" BẮT ĐẦU KHẢO SÁT THAM SỐ (PARAMETRIC STUDY)")
    print("==================================================")

    # Khảo sát 3 giá trị Young's Modulus E = 100, 150, 200 kPa
    for idx, E_val in enumerate(E_VALUES):
        time_steps, displacements = run_simulation(E_val)
        plt.plot(time_steps, displacements, label=f'E = {E_val} kPa', color=colors[idx], linewidth=2)

    plt.title("So sánh biến dạng đầu mút Ngón tay mềm theo độ cứng vật liệu (E)", fontsize=12)
    plt.xlabel("Thời gian (s)", fontsize=10)
    plt.ylabel("Độ dời biến dạng ΔX (mm)", fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=10)
    
    save_path = os.path.join(RESULTS_DIR, 'parametric_study.png')
    plt.savefig(save_path, dpi=300)
    
    print("\n==================================================")
    print(f" HOÀN TẤT! Đồ thị so sánh đã lưu tại: {save_path}")
    print("==================================================")

if __name__ == '__main__':
    main()          