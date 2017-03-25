import bpy
from .utils import *

PI = 3.14159
    
def addOneLegIK(context, object, L_R):    
    # create all the bones we need. These are created in a topologically sorted manner,
    # so that parents can be set correctly during creation of bones themselves.
    # MCH bones are mechanism bones which will be hidden from the user
    
    MCH_THIGH = 'MCH-thigh_' + L_R + '_IK'
    MCH_CALF = 'MCH-calf_' + L_R + '_IK'
    MCH_FOOT = 'MCH-foot_' + L_R + '_IK'
    MCH_FOOT_ROLL_PARENT = 'MCH-foot_roll_parent_' + L_R + '_IK'
    MCH_FOOT_ROCKER = 'MCH-foot_rocker_' + L_R + '_IK'
    FOOT_IK = 'foot_' + L_R + '_IK'
    TOES_IK = 'toes_' + L_R + '_IK'
    FOOT_ROLL_IK = 'foot_roll_' + L_R + '_IK'
    KNEE_TARGET_IK = 'knee_target_' + L_R + '_IK'
    
    PI = 3.14159
    
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)

    copyDeformationBone(object, MCH_THIGH, 'thigh_' + L_R, 'pelvis', False, 24)
    copyDeformationBone(object, MCH_CALF, 'calf_' + L_R, MCH_THIGH, True, 24)    
    copyDeformationBone(object, FOOT_IK, 'foot_' + L_R, 'root', False, 4)
    
    # Create the foot roll parent
    foot = object.data.edit_bones['foot_' + L_R]
    head = foot.tail.copy()
    tail = foot.head.copy()
    head.y = tail.y
    createNewBone(object, MCH_FOOT_ROLL_PARENT, FOOT_IK, False, head, tail, 0, 24)
    
    # Create the foot rocker Bone
    foot = object.data.edit_bones['foot_' + L_R]
    head = foot.tail.copy()
    tail = foot.head.copy()
    tail.z = head.z
    createNewBone(object, MCH_FOOT_ROCKER,  MCH_FOOT_ROLL_PARENT, False, head, tail, 0, 24)
    
    copyDeformationBone(object, MCH_FOOT, 'foot_' + L_R, MCH_FOOT_ROCKER, False, 24)    
    copyDeformationBone(object, TOES_IK, 'toes_' + L_R, MCH_FOOT_ROLL_PARENT, False, 4)

    # Create the foot roll control
    head = foot.tail.copy()
    head.y += 0.2
    tail = head.copy()
    tail.z += 0.08
    tail.y += 0.02
    createNewBone(object, FOOT_ROLL_IK, FOOT_IK, False, head, tail, 0, 4)
        
    # Create knee target IK control bone
    calf = object.data.edit_bones['calf_' + L_R]
    head = calf.head.copy()  # knee position
    head.y -= 0.7
    tail = head.copy()
    tail.y -= 0.1
    createNewBone(object, KNEE_TARGET_IK, MCH_FOOT, False, head, tail, 0, 4)
    
    # Switch to pose mode to add all the constraints
    bpy.ops.object.mode_set(mode='POSE', toggle=False)
    
    # first, set copy rotation constraints on deformation bones, to copy IK bones' rotations
    # also add drivers for FK --> IK Control
    DRIVER_TARGET = '["LegIk_' + L_R + '"]'
    
    pose_thigh = object.pose.bones['thigh_' + L_R]
    constraint = addCopyConstraint(object, pose_thigh, 'COPY_ROTATION', 'IK', 0.0, MCH_THIGH)
    if constraint:
        addDriver(constraint, 'influence', object, DRIVER_TARGET)
    
    pose_calf = object.pose.bones['calf_' + L_R]
    constraint = addCopyConstraint(object, pose_calf, 'COPY_ROTATION', 'IK', 0.0, MCH_CALF)
    if constraint:
        addDriver(constraint, 'influence', object, DRIVER_TARGET)
    
    pose_foot = object.pose.bones['foot_' + L_R]
    constraint = addCopyConstraint(object, pose_foot, 'COPY_ROTATION', 'IK', 0.0, MCH_FOOT)
    if constraint:
        addDriver(constraint, 'influence', object, DRIVER_TARGET)

    pose_toes = object.pose.bones['toes_' + L_R]
    constraint = addCopyConstraint(object, pose_toes, 'COPY_ROTATION', 'IK', 0.0, TOES_IK)
    if constraint:
        addDriver(constraint, 'influence', object, DRIVER_TARGET)
    
    # next, add the IK constraint itself
    pose_calf_IK = object.pose.bones[MCH_CALF]
    if 'IK' not in pose_calf_IK.constraints:
        constraint = pose_calf_IK.constraints.new('IK')
        constraint.name = 'IK'
        constraint.influence = 1.0
        constraint.target = object
        constraint.subtarget = MCH_FOOT
        constraint.pole_target = object
        constraint.pole_subtarget = KNEE_TARGET_IK
        constraint.pole_angle = PI / 2.0
        constraint.chain_count = 2
        pose_calf_IK.lock_ik_y = True
        pose_calf_IK.lock_ik_z = True

    # Create the foot roll mechanism
    pose_mch_foot_rocker = object.pose.bones[MCH_FOOT_ROCKER]
    copyConstraint = addCopyConstraint(object, pose_mch_foot_rocker, 'COPY_ROTATION', 'FOOT_ROLL',
        1.0, FOOT_ROLL_IK)
    if copyConstraint:
        copyConstraint.owner_space = 'LOCAL'
        copyConstraint.target_space = 'LOCAL'

    limitConstraint = addLimitConstraint(pose_mch_foot_rocker, 'LIMIT_ROTATION', 'FOOT_ROLL_LIMIT',
        1.0, [True, 0, PI / 2.0])
    if limitConstraint:
        limitConstraint.owner_space = 'LOCAL'
    
    pose_foot_roll_parent = object.pose.bones[MCH_FOOT_ROLL_PARENT]
    copyConstraint = addCopyConstraint(object, pose_foot_roll_parent, 'COPY_ROTATION', 'FOOT_ROLL',
        1.0, FOOT_ROLL_IK)
    if copyConstraint:        
        copyConstraint.owner_space = 'LOCAL'
        copyConstraint.target_space = 'LOCAL'
    
    limitConstraint = addLimitConstraint(pose_foot_roll_parent, 'LIMIT_ROTATION', 'FOOT_ROLL_LIMIT',
        1.0, [True, -1.0 * (PI / 2.0), 0])
    if limitConstraint:
        limitConstraint.owner_space = 'LOCAL'
    
    # Limit transformations
    pose_foot_ik = object.pose.bones[FOOT_IK]
    pose_foot_ik.lock_scale = [True, True, True]

    pose_knee_target_ik = object.pose.bones[KNEE_TARGET_IK]
    pose_knee_target_ik.lock_scale = [True, True, True]
    pose_knee_target_ik.rotation_mode = 'XYZ'
    pose_knee_target_ik.lock_rotation = [True, True, True]
    
    pose_foot_roll = object.pose.bones[FOOT_ROLL_IK]
    pose_foot_roll.rotation_mode = 'XYZ'
    pose_foot_roll.lock_scale = [True, True, True]
    pose_foot_roll.lock_location = [True, True, True]
    pose_foot_roll.lock_rotation = [False, True, True]
        
    pose_toes_IK = object.pose.bones[TOES_IK]
    pose_toes_IK.rotation_mode = 'YZX'
    pose_toes_IK.lock_scale = [True, True, True]
    pose_toes_IK.lock_location = [True, True, True]
    pose_toes_IK.lock_rotation = [False, True, True]
    
    
def addOneArmIK(context, object, L_R):    
    MCH_UPPERARM = 'MCH-upperarm_' + L_R + '_IK'
    MCH_LOWERARM = 'MCH-lowerarm_' + L_R + '_IK'
    HAND_IK = 'hand_' + L_R + '_IK'
    ELBOW_TARGET_IK = 'elbow_target_' + L_R + '_IK'

    bpy.ops.object.mode_set(mode='EDIT', toggle=False)

    copyDeformationBone(object, MCH_UPPERARM, 'upperarm_' + L_R, 'clavicle_' + L_R, True, 24)
    copyDeformationBone(object, MCH_LOWERARM, 'lowerarm_' + L_R, MCH_UPPERARM, True, 24)    
    copyDeformationBone(object, HAND_IK, 'hand_' + L_R, 'root', False, 4)

    # Create knee target IK control bone
    lowerarm = object.data.edit_bones['lowerarm_' + L_R]
    head = lowerarm.head.copy()  # elbow position
    head.y += 0.7
    tail = head.copy()
    tail.y += 0.1
    createNewBone(object, ELBOW_TARGET_IK, HAND_IK, False, head, tail, 0, 4)
        
    # Switch to pose mode to add all the constraints
    bpy.ops.object.mode_set(mode='POSE', toggle=False)
    
    # first, set copy rotation constraints on deformation bones, to copy IK bones' rotations
    # also add drivers for FK --> IK Control
    DRIVER_TARGET = '["ArmIk_' + L_R + '"]'
    
    pose_upperarm = object.pose.bones['upperarm_' + L_R]
    constraint = addCopyConstraint(object, pose_upperarm, 'COPY_ROTATION', 'IK', 0.0, MCH_UPPERARM)
    if constraint:
        addDriver(constraint, 'influence', object, DRIVER_TARGET)
    
    pose_lowerarm = object.pose.bones['lowerarm_' + L_R]
    constraint = addCopyConstraint(object, pose_lowerarm, 'COPY_ROTATION', 'IK', 0.0, MCH_LOWERARM)
    if constraint:
        addDriver(constraint, 'influence', object, DRIVER_TARGET)
    
    pose_hand = object.pose.bones['hand_' + L_R]
    constraint = addCopyConstraint(object, pose_hand, 'COPY_ROTATION', 'IK', 0.0, HAND_IK)
    if constraint:
        addDriver(constraint, 'influence', object, DRIVER_TARGET)
    
    # next, add the IK constraint itself
    pose_lowerarm = object.pose.bones[MCH_LOWERARM]
    if 'IK' not in pose_lowerarm.constraints:
        constraint = pose_lowerarm.constraints.new('IK')
        constraint.name = 'IK'
        constraint.influence = 1.0
        constraint.target = object
        constraint.subtarget = HAND_IK
        constraint.pole_target = object
        constraint.pole_subtarget = ELBOW_TARGET_IK
        constraint.pole_angle = -PI / 2.0
        constraint.chain_count = 2
        pose_lowerarm.lock_ik_y = True
        pose_lowerarm.lock_ik_z = True

    # limit transformations
    pose_hand_ik = object.pose.bones[HAND_IK]
    pose_hand_ik.lock_scale = [True, True, True]

    pose_hand_target_ik = object.pose.bones[ELBOW_TARGET_IK]
    pose_hand_target_ik.lock_scale = [True, True, True]
    pose_hand_target_ik.rotation_mode = 'XYZ'
    pose_hand_target_ik.lock_rotation = [True, True, True]
        




