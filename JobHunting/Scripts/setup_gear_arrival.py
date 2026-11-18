# Area 2's arrival through the floor (the user, 2026-11-18): area 1's gear exit carries the player up, and in area 2
# the same gear comes up through the engine room's floor seal. The seal splits in two halves that sink and slide into
# the floor, the gear rises with the player on it and stops flush with the floor; once the player has stepped off,
# the gear turns and goes back down and the seal closes. Only when arriving through BP_GearExit (the game instance's
# GearArrival, set by BP_GearExit's graph); otherwise the seal stays shut.
#   /Game/Art/Tower/SM_TowerSealLid   one half of the seal (build_tower_blender.py makes it and the floor's hole)
#   BP_MyGameInstance: GearArrival (bool)
#   Gimmicks/Area/BP_GearArrival: a copy of BP_GearExit (gear, gold ring, glow, axle, steam, sounds) with
#     LidPlus / LidMinus (the halves; root), ShowCam (a fixed camera for the arrival shot; root), OnGear (box over the
#     gear, for "has the player stepped off"), SteamBurst moved to floor level; the orbit camera, the floor sparks,
#     their sound, Center and Label removed. The axle hangs under the gear (a long shaft into the dark).
#   LV_Area2_Tower: BP_GearArrival on the seal ("A2 010 Room Floor"'s centre, on its top); that floor box loses its
#     collision and "Seal Floor ..." boxes (hidden, no "A2 " label so the art pipeline ignores them) are the floor
#     round the hole instead. build_area2_tower.py would bring the floor box's collision back: run this again after it.
# Graph: BP_GearArrival_EventGraph.txt (Scripts/Generators/gen_gear_arrival.ps1). Safe to run again. Editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_gear_arrival.py -unattended -nop4 -nosplash -stdout
import math
import os

import unreal

AREA = "/Game/ThirdPerson/Blueprints/Gimmicks/Area"
EXIT = AREA + "/BP_GearExit"
ARRIVAL = AREA + "/BP_GearArrival"
GAME_INSTANCE = "/Game/ThirdPerson/Blueprints/BP_MyGameInstance"
TOWER = "/Game/Art/Tower"
LEVEL = "/Game/LV_Area2_Tower"
FLOOR_LABEL = "A2 010 Room Floor"
SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Models", "Tower", "SM_TowerSealLid.fbx")
CUBE = "/Engine/BasicShapes/Cube"
HOLE = 264.0          # the hole's radius (build_tower_blender: 3.0 m x 0.88)
GEAR_TOP = 45.0       # the gear's rim above Lift (centre 22.5 + half its thickness 15 x 1.5)
LAND_Z = -GEAR_TOP    # Lift's height when the rim is flush with the floor
DEPTH = 250.0         # how far below that the gear waits (400 put the player inside BP_FallCatcher, whose top is
                      # 3 m under the floor's top, and it sent them straight back to the PlayerStart)
VARIABLES = [         # name, type, editable, default
    ("Arriving", "bool", False, None), ("ArriveAt", "real", False, None), ("Landed", "bool", False, None),
    ("OffSince", "real", False, None), ("GoingDown", "bool", False, None), ("DownAt", "real", False, None),
    ("Closed", "bool", False, None),
    ("Depth", "real", True, DEPTH), ("LandZ", "real", True, LAND_Z), ("DownSeconds", "real", True, 2.5),
    ("LidSlide", "real", True, 290.0), ("LidSink", "real", True, 12.0), ("LidSeconds", "real", True, 1.2),
    ("OpenDelay", "real", True, 1.0),
]

unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")   # keep vertex colours
library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
TYPES = {"bool": pins.get_basic_type_by_name("bool"), "real": pins.get_basic_type_by_name("real")}
lines = []

# ----- the seal's half -----
if not os.path.isfile(SOURCE):
    raise RuntimeError("Missing " + SOURCE + "; run build_tower_blender.py -- A")
lid_path = TOWER + "/SM_TowerSealLid"
if library.does_asset_exist(lid_path):
    library.delete_asset(lid_path)
task = unreal.AssetImportTask()
task.filename = SOURCE
task.destination_path = TOWER
task.automated = True
task.save = True
task.replace_existing = True
options = unreal.FbxImportUI()
options.set_editor_property("import_materials", False)
options.set_editor_property("import_textures", False)
mesh_data = options.get_editor_property("static_mesh_import_data")
mesh_data.set_editor_property("combine_meshes", True)
mesh_data.set_editor_property("vertex_color_import_option", unreal.VertexColorImportOption.REPLACE)
task.options = options
tools.import_asset_tasks([task])
lid = unreal.load_asset(lid_path)
if lid is None:
    raise RuntimeError("SM_TowerSealLid did not import")
for i, static_material in enumerate(lid.get_editor_property("static_materials")):
    slot = str(static_material.get_editor_property("material_slot_name"))   # M_Tower<Slot>
    mi = unreal.load_asset(TOWER + "/MI_" + slot[2:]) if slot.startswith("M_") else None
    if mi:
        lid.set_material(i, mi)
lid.get_editor_property("body_setup").set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
library.save_asset(lid_path, False)
lines.append("imported SM_TowerSealLid, bounds {}".format(lid.get_bounds().box_extent))

# ----- the game instance's flag -----
gi_bp = unreal.load_asset(GAME_INSTANCE)
gi = unreal.get_default_object(gi_bp.generated_class())
try:
    gi.get_editor_property("GearArrival")
except Exception:
    if not pins.add_member_variable(gi_bp, "GearArrival", TYPES["bool"]):
        raise RuntimeError("Could not add GearArrival")
    pins.compile_blueprint(gi_bp)
    library.save_asset(GAME_INSTANCE, False)
    lines.append("BP_MyGameInstance: GearArrival added")

# ----- BP_GearArrival -----
if not library.does_asset_exist(ARRIVAL):
    library.duplicate_asset(EXIT, ARRIVAL)
    lines.append("BP_GearArrival copied from BP_GearExit")
bp = unreal.load_asset(ARRIVAL)


def gather():
    found = {}
    for h in subsystem.k2_gather_subobject_data_for_blueprint(bp):
        component = data_library.get_associated_object(data_library.get_data(h))
        if component is not None:
            found[component.get_name().replace("_GEN_VARIABLE", "")] = (h, component)
    return found


def add(component_class, name, parent):
    found = gather()
    if name in found:
        return found[name][1], False
    params = unreal.AddNewSubobjectParams(parent_handle=found[parent][0], new_class=component_class, blueprint_context=bp)
    handle, _ = subsystem.add_new_subobject(params)
    subsystem.rename_subobject(handle, unreal.Text(name))
    lines.append("BP_GearArrival: component " + name)
    return data_library.get_associated_object(data_library.get_data(handle)), True


found = gather()
gone = [found[n][0] for n in ("Camera", "CamArm", "CamPivot", "RiseFx", "SparkSound", "Center", "Label") if n in found]
if gone:
    subsystem.delete_subobjects(found["DefaultSceneRoot"][0], gone, bp)
    lines.append("BP_GearArrival: removed {} parts of the exit".format(len(gone)))
found = gather()
root = found["DefaultSceneRoot"][0]
subsystem.attach_subobject(root, found["SteamBurst"][0])       # the steam comes out round the opening
found["SteamBurst"][1].set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 5.0))
subsystem.attach_subobject(found["Lift"][0], found["Axle"][0])  # a long shaft under the gear, into the dark
axle = found["Axle"][1]
axle.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, -750.0))
axle.set_editor_property("relative_scale3d", unreal.Vector(0.9, 0.9, 15.0))
found["Lift"][1].set_editor_property("relative_location", unreal.Vector(0.0, 0.0, LAND_Z - DEPTH))

for name, yaw in (("LidPlus", 0.0), ("LidMinus", 180.0)):
    half, made = add(unreal.StaticMeshComponent, name, "DefaultSceneRoot")
    half.set_editor_property("static_mesh", lid)
    half.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 0.0))
    half.set_editor_property("relative_rotation", unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw))
    half.set_collision_profile_name("BlockAll")
# LidBlock: an invisible flat box over the whole hole, at the floor's top, so the shut seal is solid everywhere (the
# thin two-piece lid alone let the player slip through, 2026-11-18). The graph switches it off while the gear comes
# up and back on once the seal has shut.
block, made = add(unreal.BoxComponent, "LidBlock", "DefaultSceneRoot")
block.set_editor_property("box_extent", unreal.Vector(HOLE + 10.0, HOLE + 10.0, 10.0))
block.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, -10.0))
block.set_collision_profile_name("BlockAll")
cam, made = add(unreal.CameraComponent, "ShowCam", "DefaultSceneRoot")
eye, target = unreal.Vector(-950.0, -760.0, 430.0), unreal.Vector(0.0, 0.0, -40.0)
cam.set_editor_property("relative_location", eye)
cam.set_editor_property("relative_rotation", unreal.MathLibrary.find_look_at_rotation(eye, target))
cam.set_editor_property("constrain_aspect_ratio", False)
on_gear, made = add(unreal.BoxComponent, "OnGear", "Lift")
on_gear.set_editor_property("box_extent", unreal.Vector(235.0, 235.0, 120.0))
on_gear.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, GEAR_TOP + 110.0))
on_gear.set_collision_profile_name("OverlapOnlyPawn")

defaults = unreal.get_default_object(bp.generated_class())
for name, kind, editable, value in VARIABLES:
    try:
        defaults.get_editor_property(name)
    except Exception:
        if not pins.add_member_variable(bp, name, TYPES[kind]):
            raise RuntimeError("Could not add " + name)
        if editable:
            pins.set_blueprint_variable_instance_editable(bp, name, True)
        lines.append("BP_GearArrival: variable " + name)
pins.compile_blueprint(bp)
defaults = unreal.get_default_object(bp.generated_class())
for name, kind, editable, value in VARIABLES:
    if value is not None:
        defaults.set_editor_property(name, value)
defaults.set_editor_property("RiseSeconds", 2.5)
library.save_asset(ARRIVAL, False)

# ----- the level -----
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not level.load_level(LEVEL):
    raise RuntimeError("Could not open " + LEVEL)
floor = None
for actor in actors.get_all_level_actors():
    label = actor.get_actor_label()
    if label == FLOOR_LABEL:
        floor = actor
    elif label.startswith("Seal Floor") or actor.get_class().get_name() == "BP_GearArrival_C":
        actors.destroy_actor(actor)
if floor is None:
    raise RuntimeError(FLOOR_LABEL + " not found")
origin, extent = floor.get_actor_bounds(False)
cx, cy, top, bottom = origin.x, origin.y, origin.z + extent.z, origin.z - extent.z
floor.get_editor_property("static_mesh_component").set_collision_profile_name("NoCollision")
folder = floor.get_folder_path()


def collision_box(name, x0, x1, y0, y1, yaw=0.0, center=None):
    location = center or unreal.Vector((x0 + x1) / 2.0, (y0 + y1) / 2.0, (top + bottom) / 2.0)
    box = actors.spawn_actor_from_class(unreal.StaticMeshActor, location, unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw))
    box.set_actor_label("Seal Floor " + name)
    box.set_folder_path(str(folder))
    component = box.get_editor_property("static_mesh_component")
    component.set_static_mesh(unreal.load_asset(CUBE))
    component.set_editor_property("visible", False)
    box.set_actor_hidden_in_game(True)
    box.set_actor_scale3d(unreal.Vector((x1 - x0) / 100.0, (y1 - y0) / 100.0, (top - bottom) / 100.0))


x0, x1, y0, y1 = origin.x - extent.x, origin.x + extent.x, origin.y - extent.y, origin.y + extent.y
collision_box("N", x0, x1, cy + HOLE, y1)
collision_box("S", x0, x1, y0, cy - HOLE)
collision_box("W", x0, cx - HOLE, cy - HOLE, cy + HOLE)
collision_box("E", cx + HOLE, x1, cy - HOLE, cy + HOLE)
# The square hole's corners, outside the round one: a box turned 45 degrees in each, its inner face on the line that
# touches the circle at 45 degrees (what is left uncovered between it and the circle is under 15 cm).
size = 200.0
reach = (HOLE * math.sqrt(2.0) + size / 2.0) / math.sqrt(2.0)
for name, sx, sy in (("NE", 1, 1), ("NW", -1, 1), ("SE", 1, -1), ("SW", -1, -1)):
    collision_box("Corner " + name, -size / 2.0, size / 2.0, -size / 2.0, size / 2.0, 45.0,
                  unreal.Vector(cx + sx * reach, cy + sy * reach, (top + bottom) / 2.0))
gear = actors.spawn_actor_from_class(bp.generated_class(), unreal.Vector(cx, cy, top), unreal.Rotator(0.0, 0.0, 0.0))
gear.set_actor_label("Gear Arrival")
gear.set_folder_path(str(folder))
lines.append("Gear Arrival at ({:.0f}, {:.0f}, {:.0f}); floor box collision off; 8 Seal Floor boxes".format(cx, cy, top))
lines.append("{} saved {}".format(LEVEL, level.save_current_level()))

with open(os.path.join(unreal.Paths.project_saved_dir(), "gear_arrival.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
