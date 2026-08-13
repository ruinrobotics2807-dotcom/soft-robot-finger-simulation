# =====================================================================
# FILE: finger_model.py
# VAI TRÒ: Dựng Scene Graph cho Soft Finger Model (SOFA Framework v26+)
# =====================================================================
import Sofa.Core
from config import *

def createScene(rootNode, young_modulus=YOUNG_MODULUS):
    """
    Hàm khởi tạo mô hình ngón tay mềm.
    Nhận tham số young_modulus để phục vụ chạy khảo sát 3 đường đồ thị trong main.py.
    """
    # 1. NẠP CÁC PLUGIN BẮT BUỘC
    rootNode.addObject('RequiredPlugin', pluginName=[
        'Sofa.Component.AnimationLoop',
        'Sofa.Component.Constraint.Lagrangian.Correction',
        'Sofa.Component.Constraint.Lagrangian.Solver',
        'Sofa.Component.Constraint.Projective',
        'Sofa.Component.Engine.Select',
        'Sofa.Component.IO.Mesh',
        'Sofa.Component.LinearSolver.Direct',
        'Sofa.Component.Mapping.Linear',
        'Sofa.Component.Mass',
        'Sofa.Component.ODESolver.Backward',
        'Sofa.Component.SolidMechanics.FEM.Elastic',
        'Sofa.Component.StateContainer',
        'Sofa.Component.Topology.Container.Dynamic',
        'Sofa.Component.Topology.Container.Grid',
        'Sofa.Component.Topology.Mapping',
        'Sofa.Component.Visual',
        'Sofa.GL.Component.Rendering3D',  # Bắt buộc cho OglModel hiển thị 3D
        'SoftRobots'
    ])

    # 2. THIẾT LẬP THỜI GIAN & BỘ GIẢI RÀNG BUỘC
    rootNode.gravity = GRAVITY
    rootNode.dt = DT

    rootNode.addObject('FreeMotionAnimationLoop')
    rootNode.addObject('BlockGaussSeidelConstraintSolver', maxIterations=100, tolerance=1e-5)

    # 3. XÂY DỰNG MÔ HÌNH NGÓN TAY MỀM (SOFT FINGER NODE)
    finger = rootNode.addChild('SoftFinger')

    # Bộ giải ODESolver & LinearSolver
    finger.addObject('EulerImplicitSolver', name='odesolver', rayleighStiffness=0.1, rayleighMass=0.1)
    finger.addObject('SparseLDLSolver', name='linearsolver')

    # Lưới hình học ngón tay (RegularGridTopology: 20x20x100 mm)
    finger.addObject('RegularGridTopology', 
                     name='grid', 
                     min=[-10.0, -10.0, 0.0], 
                     max=[10.0, 10.0, 100.0], 
                     n=[5, 5, 21])

    # Khai báo bậc tự do
    finger.addObject('MechanicalObject', name='dof', template='Vec3d')

    # Khối lượng
    finger.addObject('UniformMass', totalMass=0.05)  # 50g

    # Mô hình hóa phần tử hữu hạn FEM Hexahedron
    finger.addObject('HexahedronFEMForceField', 
                     name='FEM', 
                     youngModulus=young_modulus, 
                     poissonRatio=POISSON_RATIO, 
                     method='large')

    # Cố định gốc ngón tay (BoxROI tại Z = 0)
    finger.addObject('BoxROI', name='baseROI', box=[-11.0, -11.0, -1.0, 11.0, 11.0, 1.0])
    finger.addObject('FixedConstraint', indices='@baseROI.indices')

    # Truyền lực từ bộ giải ràng buộc vào mô hình FEM
    finger.addObject('LinearSolverConstraintCorrection', linearSolver='@linearsolver')

    # Component xuất dữ liệu hình học 3D cho ParaView
    finger.addObject('VTKExporter', 
                     name='vtkExporter', 
                     filename='../results/finger_frame', 
                     hexas=True,                           # Chỉnh đúng thuộc tính hexas=True để xuất khối 3D (# of Cells > 0)
                     exportEveryNumberOfSteps=2,           # Tần suất xuất file 2 bước/frame
                     exportAtBegin=True)

    # 4. NODE HIỂN THỊ HÌNH ẢNH 3D (VISUAL MODEL)
    visual = finger.addChild('VisualModel')
    visual.addObject('OglModel', name='ogl', color=[0.2, 0.6, 0.9, 0.85])
    visual.addObject('IdentityMapping', input='@../dof', output='@ogl')

    # 5. THÊM DÂY CÁP KÉO (CABLE ACTUATOR)
    cable = finger.addChild('Cable')
    
    # Quỹ đạo dây cáp lệch tâm X = 6mm
    cable_path = [
        [6.0, 0.0, 0.0],
        [6.0, 0.0, 20.0],
        [6.0, 0.0, 40.0],
        [6.0, 0.0, 60.0],
        [6.0, 0.0, 80.0],
        [6.0, 0.0, 100.0]
    ]
    cable.addObject('MechanicalObject', name='cableDOF', position=cable_path)
    cable.addObject('CableConstraint', 
                    name='cableConstraint', 
                    indices=list(range(len(cable_path))),
                    pullPoint=[6.0, 0.0, 0.0],
                    valueType='displacement')
    cable.addObject('BarycentricMapping', name='mapping')

    return rootNode