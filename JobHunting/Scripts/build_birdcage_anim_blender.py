# Rigs the birdcage with a door bone and keys Door_Open, saving SourceArt/Models/Birdcage/BirdcageAnim.blend and
# SK_Birdcage.fbx. Run without opening Blender:
#   blender --background --factory-startup --python build_birdcage_anim_blender.py
import math
import os
import sys

import bpy

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Keeps a __pycache__ folder out of Scripts.
sys.dont_write_bytecode = True
sys.path.insert(0, SCRIPT_DIR)
import build_birdcage_blender as shape

FPS = 30
# (frame, door angle): swings past fully open, then settles. Playing it backwards closes the door.
DOOR_KEYS = [(0, 0.0), (14, 98.0), (20, 87.0), (25, 91.0), (30, 90.0)]
PREVIEW_FRAMES = (0, 8, 14, 30)


def add_weights(obj, group_name):
    group = obj.vertex_groups.new(name=group_name)
    group.add(list(range(len(obj.data.vertices))), 1.0, "REPLACE")


def build_skinned_mesh(brass, wood):
    # The door stays closed in the mesh: the bone does all of the opening.
    shape.DOOR_OPEN_DEGREES = 0.0
    body, _ = shape.join_parts(shape.build_body(brass, wood))
    add_weights(body, "Root")
    door, _ = shape.join_parts(shape.build_door(brass))
    add_weights(door, "Door")
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    door.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.join()
    body.name = "SK_Birdcage"
    body.data.name = "SK_Birdcage"
    return body


def build_armature(mesh):
    data = bpy.data.armatures.new("Armature")
    rig = bpy.data.objects.new("Armature", data)
    bpy.context.collection.objects.link(rig)
    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    root = data.edit_bones.new("Root")
    root.head = (0.0, 0.0, 0.0)
    root.tail = (0.0, 0.0, 0.1)
    door = data.edit_bones.new("Door")
    hinge = shape.door_hinge()
    door.head = (hinge.x, hinge.y, shape.DOOR_BOTTOM)
    door.tail = (hinge.x, hinge.y, shape.DOOR_TOP)
    door.parent = root
    bpy.ops.object.mode_set(mode="OBJECT")
    mesh.parent = rig
    modifier = mesh.modifiers.new("Armature", "ARMATURE")
    modifier.object = rig
    return rig


def key_door(rig):
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start = DOOR_KEYS[0][0]
    scene.frame_end = DOOR_KEYS[-1][0]
    bone = rig.pose.bones["Door"]
    bone.rotation_mode = "XYZ"
    for frame, degrees in DOOR_KEYS:
        # The bone's Y axis points up; a negative turn is clockwise from above, the opening direction.
        bone.rotation_euler = (0.0, math.radians(-degrees), 0.0)
        bone.keyframe_insert("rotation_euler", index=1, frame=frame)
    rig.animation_data.action.name = "Door_Open"


if __name__ == "__main__":
    os.makedirs(shape.OUT_DIR, exist_ok=True)
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj)

    brass_material = shape.new_material("M_Brass", (0.78, 0.56, 0.22), 1.0, 0.28)
    wood_material = shape.new_material("M_Wood", (0.33, 0.17, 0.07), 0.0, 0.55)
    cage = build_skinned_mesh(brass_material, wood_material)
    armature = build_armature(cage)
    key_door(armature)

    bpy.ops.object.select_all(action="DESELECT")
    cage.select_set(True)
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.export_scene.fbx(
        filepath=os.path.join(shape.OUT_DIR, "SK_Birdcage.fbx"), use_selection=True, object_types={"ARMATURE", "MESH"},
        apply_unit_scale=True, add_leaf_bones=False, mesh_smooth_type="EDGE", use_armature_deform_only=False,
        bake_anim=True, bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False, bake_anim_force_startend_keying=True,
    )
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(shape.OUT_DIR, "BirdcageAnim.blend"))

    # Previews of the keyed motion: the scene is not saved again after this, so the floor and lights stay out of the .blend.
    preview_dir = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else shape.OUT_DIR
    scene = bpy.context.scene
    scene.frame_set(PREVIEW_FRAMES[0])
    shape.setup_render(os.path.join(preview_dir, "door_{:02d}.png".format(PREVIEW_FRAMES[0])))
    for preview_frame in PREVIEW_FRAMES[1:]:
        scene.frame_set(preview_frame)
        scene.render.filepath = os.path.join(preview_dir, "door_{:02d}.png".format(preview_frame))
        bpy.ops.render.render(write_still=True)
    print("BIRDCAGE ANIM done")
