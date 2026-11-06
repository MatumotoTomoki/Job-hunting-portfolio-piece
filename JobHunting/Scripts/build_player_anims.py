# Keys the player's handmade animations for SK_matsumoto_kun_3D from code, into Plaey/Anim. Every listed animation is
# rekeyed on each run, in place, so whatever uses it keeps working. With the editor closed:
#   UnrealEditor-Cmd.exe JobHunting.uproject -run=pythonscript -script=build_player_anims.py -unattended -nop4 -nosplash -stdout -AllowCommandletRendering
# (-AllowCommandletRendering: without it, keying an animation trips an assert on preview meshes that cannot render.)
# Every bone of this skeleton has an identity reference rotation, so a bone's local rotation is a rotation about the
# mesh axes: +Y is where the character faces, +X is its left, +Z is up. Each animation is written as "controls"
# (angles in degrees, hip height in cm) per frame, and pose_from_controls turns those into bone rotations.
# To check one in Blender, set PLAYER_ANIM_EXPORT to a folder and PLAYER_ANIM_NAME to its name: it is exported as FBX
# with the mesh.
import math
import os

import unreal

SKELETAL_MESH = "/Game/ThirdPerson/Blueprints/Plaey/SK_matsumoto_kun_3D"
ANIM_DIR = "/Game/ThirdPerson/Blueprints/Plaey/Anim"
FPS = 30


def axis_angle(axis, degrees):
    half = math.radians(degrees) / 2.0
    s = math.sin(half)
    return (axis[0] * s, axis[1] * s, axis[2] * s, math.cos(half))


def multiply(a, b):
    # a * b: b is applied first, then a, both about the parent's axes.
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw,
            aw * bw - ax * bx - ay * by - az * bz)


def rotate(q, v):
    x, y, z, w = q
    r = multiply(multiply(q, (v[0], v[1], v[2], 0.0)), (-x, -y, -z, w))
    return (r[0], r[1], r[2])


# Which sign of a turn about X swings a hanging leg forward (+Y), and which turn about Y lowers the left arm (+X) to -Z:
# measured instead of assumed, so the keys do not depend on the handedness of the maths.
FORWARD = 1.0 if rotate(axis_angle((1, 0, 0), 30.0), (0.0, 0.0, -1.0))[1] > 0.0 else -1.0
LEFT_DOWN = 1.0 if rotate(axis_angle((0, 1, 0), 30.0), (1.0, 0.0, 0.0))[2] < 0.0 else -1.0
X_AXIS, Y_AXIS, Z_AXIS = (1, 0, 0), (0, 1, 0), (0, 0, 1)
IDENTITY = (0.0, 0.0, 0.0, 1.0)
# Reference-pose positions (mesh space, cm): the hip bone, and the middle of the big round body, which a flip turns
# around so the body spins in place instead of swinging around the hip.
HIP_REST = (0.0, 1.0, 16.7)
BODY_CENTER = (0.0, 1.2, 57.0)


def swing(degrees):
    return axis_angle(X_AXIS, FORWARD * degrees)


# Controls, all default 0: per side (_L, _R) thigh (+ forward), knee (+ folds the shin back), foot (+ toes up),
# arm_down (+ lowers the arm, - raises it), arm_swing (+ forward), elbow (+ bends the forearm forward);
# for the body: lean (+ forward), twist, roll, neck (+ nods forward), hip_z (cm up), flip (+ turns the whole
# character forward, head first, around BODY_CENTER).
def pose_from_controls(c):
    get = lambda name: c.get(name, 0.0)
    keys = {}
    for side, sign in (("L", 1.0), ("R", -1.0)):
        keys["up_leg_" + side] = (swing(get("thigh_" + side)), (0, 0, 0))
        keys["leg_" + side] = (swing(-get("knee_" + side)), (0, 0, 0))
        keys["foot_" + side] = (swing(get("foot_" + side)), (0, 0, 0))
        down = axis_angle(Y_AXIS, LEFT_DOWN * sign * get("arm_down_" + side))
        keys["up_arm_" + side] = (multiply(swing(get("arm_swing_" + side)), down), (0, 0, 0))
        keys["arm_" + side] = (multiply(swing(get("elbow_" + side)), axis_angle(Y_AXIS, LEFT_DOWN * sign * -10.0)), (0, 0, 0))
    # swing() turns a hanging limb forward, so it tips an upright body backward: the lean is a negative swing.
    keys["head"] = (multiply(axis_angle(Z_AXIS, get("twist")), multiply(axis_angle(Y_AXIS, get("roll")), swing(-get("lean")))), (0, 0, 0))
    keys["neck"] = (swing(-get("neck")), (0, 0, 0))
    # Turning the hip turns everything; moving it keeps BODY_CENTER where it was.
    flip = swing(-get("flip"))
    arm = (HIP_REST[0] - BODY_CENTER[0], HIP_REST[1] - BODY_CENTER[1], HIP_REST[2] - BODY_CENTER[2])
    turned = rotate(flip, arm)
    shift = (turned[0] - arm[0], turned[1] - arm[1], turned[2] - arm[2] + get("hip_z"))
    keys["hip"] = (flip, shift)
    return keys


def both(**values):
    # thigh=10 sets thigh_L and thigh_R; names that already end in _L/_R pass through.
    out = {}
    for name, value in values.items():
        if name.endswith("_L") or name.endswith("_R") or name in ("lean", "twist", "roll", "neck", "hip_z", "flip"):
            out[name] = value
        else:
            out[name + "_L"] = value
            out[name + "_R"] = value
    return out


def keyed(key_poses, frames):
    # Eases between key poses (frame, controls); a control missing from a key counts as 0.
    names = set()
    for _, pose in key_poses:
        names |= set(pose)
    result = []
    for frame in range(frames + 1):
        before = max((k for k in key_poses if k[0] <= frame), key=lambda k: k[0])
        after = min((k for k in key_poses if k[0] >= frame), key=lambda k: k[0])
        t = 0.0 if after[0] == before[0] else (frame - before[0]) / float(after[0] - before[0])
        t = t * t * (3.0 - 2.0 * t)
        result.append({n: before[1].get(n, 0.0) * (1.0 - t) + after[1].get(n, 0.0) * t for n in names})
    return result


# --- Run: one full stride in 0.4 s, quick little steps for short legs (loops) ---------------
def run_controls(frames):
    leg_swing, knee_lift, arm_down, arm_swing = 45.0, 55.0, 30.0, 50.0
    result = []
    for frame in range(frames + 1):
        phase = 2.0 * math.pi * frame / frames
        s, c = math.sin(phase), math.cos(phase)
        controls = {}
        for side, sign in (("L", 1.0), ("R", -1.0)):
            stride = sign * s  # +1: this leg reaching forward.
            # The knee folds most while the leg swings forward under the body, little while it pushes back.
            recovery = max(0.0, sign * c)
            controls["thigh_" + side] = leg_swing * stride + 0.35 * knee_lift * recovery
            controls["knee_" + side] = knee_lift * recovery
            controls["foot_" + side] = -0.4 * leg_swing * stride + 0.4 * knee_lift * recovery
            controls["arm_down_" + side] = arm_down
            controls["arm_swing_" + side] = -arm_swing * stride
            controls["elbow_" + side] = 30.0
        controls["lean"] = 12.0
        controls["twist"] = 7.0 * s
        controls["roll"] = 4.0 * s
        controls["neck"] = 2.0 - 2.0 * math.cos(2.0 * phase)
        # Two steps per cycle: lowest as each foot lands (s = 0), highest in between.
        controls["hip_z"] = 4.0 * (0.5 - 0.5 * math.cos(2.0 * phase))
        result.append(controls)
    return result


# --- Jump: a quick crouch, a stretch upward, then a tucked pose to carry into the fall (plays once) ---
def airborne():
    # The pose the jump ends on; the double jump starts and ends on it too, so they chain cleanly.
    pose = both(thigh=35.0, knee=60.0, foot=10.0, arm_down=-10.0, arm_swing=15.0, elbow=30.0, lean=4.0, neck=0.0, hip_z=2.0)
    pose["thigh_R"] = 20.0
    pose["knee_R"] = 40.0
    return pose


def jump_controls(frames):
    crouch = both(thigh=25.0, knee=45.0, foot=-15.0, arm_down=45.0, arm_swing=-35.0, elbow=20.0, lean=12.0, neck=4.0, hip_z=-3.5)
    stretch = both(thigh=-12.0, knee=5.0, foot=-35.0, arm_down=-45.0, arm_swing=30.0, elbow=10.0, lean=-6.0, neck=-6.0, hip_z=4.0)
    return keyed([(0, crouch), (3, stretch), (8, airborne()), (frames, airborne())], frames)


# --- Double jump: curls up into a ball and does one forward flip (plays once) -----------------
def double_jump_controls(frames):
    start = airborne()
    curled = both(thigh=70.0, knee=85.0, foot=20.0, arm_down=20.0, arm_swing=45.0, elbow=60.0, neck=6.0, hip_z=3.0)
    early = dict(curled, flip=40.0)
    late = dict(curled, flip=320.0)
    end = dict(airborne(), flip=360.0)
    return keyed([(0, start), (3, early), (10, late), (frames, end)], frames)


# --- Fall: arms up and flapping, legs dangling and paddling, the body swaying a little (loops) ---
def fall_controls(frames):
    result = []
    for frame in range(frames + 1):
        phase = 2.0 * math.pi * frame / frames
        s, c = math.sin(phase), math.cos(phase)
        flap = math.sin(2.0 * phase)
        controls = {}
        for side, sign in (("L", 1.0), ("R", -1.0)):
            # Short limbs need big angles to read at all.
            controls["thigh_" + side] = 15.0 + 25.0 * sign * s
            controls["knee_" + side] = 25.0 + 22.0 * sign * c
            controls["foot_" + side] = -10.0 + 12.0 * sign * s
            # Flapping out of step left to right, so it reads as flailing rather than flying.
            controls["arm_down_" + side] = -45.0 + 28.0 * math.sin(2.0 * phase + (0.0 if sign > 0 else math.pi / 2.0))
            controls["arm_swing_" + side] = 10.0 + 15.0 * sign * c
            controls["elbow_" + side] = 25.0
        controls["lean"] = -5.0 + 2.0 * flap
        controls["roll"] = 3.0 * s
        controls["twist"] = 2.0 * c
        controls["neck"] = -3.0
        controls["hip_z"] = 2.0 + 1.0 * flap
        result.append(controls)
    return result


# --- Ledge hang: both arms up and forward onto the edge, the body hanging and slowly swaying (loops) ---
# Climbing up is left for when the ledge-grab logic exists, so it can be timed to it.
def ledge_hang_controls(frames):
    result = []
    for frame in range(frames + 1):
        phase = 2.0 * math.pi * frame / frames
        s, c = math.sin(phase), math.cos(phase)
        controls = {}
        for side, sign in (("L", 1.0), ("R", -1.0)):
            # The short arms reach as high as they can, slightly forward, toward the edge in front.
            controls["arm_down_" + side] = -78.0 + 3.0 * sign * s
            controls["arm_swing_" + side] = 35.0
            controls["elbow_" + side] = 15.0 + 4.0 * c
            # Legs hang loose and drift gently, out of step with each other.
            controls["thigh_" + side] = 6.0 + 7.0 * sign * s
            controls["knee_" + side] = 18.0 + 6.0 * sign * c
            controls["foot_" + side] = -15.0
        # Leaning a little into the wall, with a slow pendulum sway.
        controls["lean"] = 6.0 + 1.5 * c
        controls["roll"] = 3.5 * s
        controls["twist"] = 1.5 * s
        controls["neck"] = -8.0
        controls["hip_z"] = 0.6 * math.cos(2.0 * phase)
        result.append(controls)
    return result


# name: (frames, controls builder, loops)
ANIMATIONS = {
    "MM_LedgeHang_Handmade": (30, ledge_hang_controls, True),
    "MM_Run_Handmade": (12, run_controls, True),
    "MM_Jump_Handmade": (12, jump_controls, False),
    "MM_DoubleJump_Handmade": (14, double_jump_controls, False),
    "MM_Fall_Handmade": (18, fall_controls, True),
}


def build(name, frames, builder, mesh, skeleton):
    # An existing animation is rewritten in place: the AnimBP, blend space and montage refer to these assets, and
    # deleting one to recreate it would cut those references.
    library = unreal.EditorAssetLibrary
    path = ANIM_DIR + "/" + name
    if library.does_asset_exist(path):
        anim = unreal.load_asset(path)
    else:
        factory = unreal.AnimSequenceFactory()
        factory.set_editor_property("target_skeleton", skeleton)
        factory.set_editor_property("preview_skeletal_mesh", mesh)
        anim = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, ANIM_DIR, unreal.AnimSequence, factory)
    if not anim:
        raise RuntimeError("Could not create " + path)

    ext = unreal.AnimPoseExtensions
    reference = ext.get_reference_pose(skeleton)
    poses = [pose_from_controls(c) for c in builder(frames)]
    controller = anim.get_editor_property("controller")
    controller.open_bracket(unreal.Text("Handmade " + name), True)
    controller.remove_all_bone_tracks(True)
    controller.set_frame_rate(unreal.FrameRate(FPS, 1), True)
    controller.set_number_of_frames(unreal.FrameNumber(frames), True)
    for bone in poses[0]:
        rest = ext.get_bone_pose(reference, bone, unreal.AnimPoseSpaces.LOCAL).translation
        positions, rotations, scales = [], [], []
        for pose in poses:
            q, offset = pose[bone]
            positions.append(unreal.Vector(rest.x + offset[0], rest.y + offset[1], rest.z + offset[2]))
            rotations.append(unreal.Quat(q[0], q[1], q[2], q[3]))
            scales.append(unreal.Vector(1.0, 1.0, 1.0))
        controller.add_bone_curve(bone, True)
        controller.set_bone_track_keys(bone, positions, rotations, scales, True)
    controller.close_bracket(True)
    anim.set_editor_property("enable_root_motion", False)
    library.save_asset(path, False)
    return anim


player_mesh = unreal.load_asset(SKELETAL_MESH)
player_skeleton = player_mesh.get_editor_property("skeleton")
built = {name: build(name, frames, builder, player_mesh, player_skeleton) for name, (frames, builder, _) in ANIMATIONS.items()}

lines = ["signs: forward {} left_down {}".format(FORWARD, LEFT_DOWN)]
ext = unreal.AnimPoseExtensions
options = unreal.AnimPoseEvaluationOptions()
for name, anim in built.items():
    lines.append("{}: {:.2f} s, {} frames".format(name, anim.get_play_length(), unreal.AnimationLibrary.get_num_frames(anim)))
    for frame in (0, 3, 8):
        pose = ext.get_anim_pose_at_frame(anim, frame, options)
        row = ["  frame {}".format(frame)]
        for bone in ("foot_L", "foot_R", "hand_L", "hip", "head_001"):
            t = ext.get_bone_pose(pose, bone, unreal.AnimPoseSpaces.WORLD).translation
            row.append("{}({:.1f},{:.1f},{:.1f})".format(bone, t.x, t.y, t.z))
        lines.append(" ".join(row))

export_dir = os.environ.get("PLAYER_ANIM_EXPORT")
export_name = os.environ.get("PLAYER_ANIM_NAME")
if export_dir and export_name in built:
    task = unreal.AssetExportTask()
    task.object = built[export_name]
    task.filename = os.path.join(export_dir, "player_anim.fbx")
    task.automated = True
    task.replace_identical = True
    task.prompt = False
    task.exporter = unreal.AnimSequenceExporterFBX()
    fbx = unreal.FbxExportOption()
    fbx.set_editor_property("export_preview_mesh", True)
    task.options = fbx
    lines.append("export {}: {}".format(export_name, unreal.Exporter.run_asset_export_task(task)))
with open(os.path.join(unreal.Paths.project_saved_dir(), "player_anims_report.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(lines))
unreal.log("\n".join(lines))
