# Achievements step 6 (2026-11-21): the hidden stage's door, in the small house of area 1's lower town (the user's pick:
# the doorway between A1 077 / 078 / 079 Wall, x -3080..-2920, front face y -1000, room behind it to y -1450).
#   Achievements/M_SecretGlow   Color (vector) as base colour, Color * Glow (scalar) as emissive; Glow 0 = dull gold
#   Achievements/BP_SecretDoor  Door (stone slab in the doorway), Light00..Light11 (12 lamps round the doorway: one per
#       free achievement), Emblem0..Emblem3 (4 discs over the lintel: all star coins of area 1..4), ApproachBox (in
#       front: refresh the lamps when the player walks up), EnterBox (inside the room: go to LV_Secret when open).
#       Variables IsOpen (bool), NeedFree (int, 12, instance editable). Graph: Scripts/BP_SecretDoor_EventGraph.txt
#       (Generators/gen_secret_door.ps1).
#   LV_Area1_Ruins    one "A1 Secret Door" at (-3000, -1000, 0), facing +Y. Left alone when already there.
#   LV_Secret         a new empty level (floor, player start, light, sky) for the hidden stage, to fill in later.
# Safe to run again. Saves LV_Area1_Ruins and LV_Secret, and ends with LV_Area1_Ruins open. From the Output Log:
#   exec(open(r"<full path>\setup_secret_door.py", encoding="utf-8").read())
import os

import unreal

FOLDER = "/Game/ThirdPerson/Blueprints/Achievements"
DOOR = FOLDER + "/BP_SecretDoor"
GLOW = FOLDER + "/M_SecretGlow"
AREA1 = "/Game/LV_Area1_Ruins"
SECRET = "/Game/LV_Secret"
SLAB_MATERIAL = "/Game/Art/Ruins/MI_RuinsAshlar"
DOOR_LABEL = "A1 Secret Door"
DOOR_AT = unreal.Vector(-3000.0, -1000.0, 0.0)

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
lines = []

# ----- the glow material -----
if library.does_asset_exist(GLOW):
    glow = unreal.load_asset(GLOW)
else:
    glow = tools.create_asset("M_SecretGlow", FOLDER, unreal.Material, unreal.MaterialFactoryNew())
    mel = unreal.MaterialEditingLibrary
    color = mel.create_material_expression(glow, unreal.MaterialExpressionVectorParameter, -700, 0)
    color.set_editor_property("parameter_name", "Color")
    color.set_editor_property("default_value", unreal.LinearColor(1.0, 0.72, 0.28, 1.0))
    amount = mel.create_material_expression(glow, unreal.MaterialExpressionScalarParameter, -700, 300)
    amount.set_editor_property("parameter_name", "Glow")
    amount.set_editor_property("default_value", 0.0)
    times = mel.create_material_expression(glow, unreal.MaterialExpressionMultiply, -350, 200)
    mel.connect_material_expressions(color, "", times, "A")
    mel.connect_material_expressions(amount, "", times, "B")
    mel.connect_material_property(color, "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(times, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    metal = mel.create_material_expression(glow, unreal.MaterialExpressionConstant, -350, 450)
    metal.set_editor_property("r", 0.8)
    mel.connect_material_property(metal, "", unreal.MaterialProperty.MP_METALLIC)
    mel.recompile_material(glow)
    library.save_asset(GLOW, False)
    lines.append("created " + GLOW)


# ----- the door blueprint -----
def components(blueprint):
    found = {}
    for handle in subsystem.k2_gather_subobject_data_for_blueprint(blueprint):
        component = data_library.get_associated_object(data_library.get_data(handle))
        if component is not None:
            found[component.get_name().replace("_GEN_VARIABLE", "")] = component
    return found


if library.does_asset_exist(DOOR):
    door_bp = unreal.load_asset(DOOR)
else:
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    door_bp = tools.create_asset("BP_SecretDoor", FOLDER, unreal.Blueprint, factory)
    lines.append("created " + DOOR)

root = subsystem.k2_gather_subobject_data_for_blueprint(door_bp)[0]
have = components(door_bp)
SPHERE = unreal.load_asset("/Engine/BasicShapes/Sphere")
CUBE = unreal.load_asset("/Engine/BasicShapes/Cube")
CYLINDER = unreal.load_asset("/Engine/BasicShapes/Cylinder")


def add(name, cls):
    if name in have:
        return have[name]
    handle, _ = subsystem.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root, new_class=cls, blueprint_context=door_bp))
    if not data_library.is_handle_valid(handle):
        raise RuntimeError("Could not add {} to BP_SecretDoor".format(name))
    subsystem.rename_subobject(handle, unreal.Text(name))
    lines.append("BP_SecretDoor: component " + name)
    return data_library.get_associated_object(data_library.get_data(handle))


def mesh(name, shape, material, where, scale, rotation=None, collide=False):
    part = add(name, unreal.StaticMeshComponent)
    part.set_editor_property("static_mesh", shape)
    part.set_material(0, material)
    part.set_editor_property("relative_location", where)
    part.set_editor_property("relative_scale3d", scale)
    if rotation is not None:
        part.set_editor_property("relative_rotation", rotation)
    if not collide:
        part.set_collision_profile_name("NoCollision")
    return part


def box(name, where, extent):
    part = add(name, unreal.BoxComponent)
    part.set_editor_property("box_extent", extent)
    part.set_editor_property("relative_location", where)
    part.set_collision_profile_name("OverlapOnlyPawn")
    part.set_editor_property("hidden_in_game", True)


# All in the door's space: x along the wall, -y into the room, z up from the floor. The doorway is x -80..80, z 0..280.
mesh("Door", CUBE, unreal.load_asset(SLAB_MATERIAL), unreal.Vector(0.0, -20.0, 140.0), unreal.Vector(1.6, 0.4, 2.8), collide=True)
lamps = [(-115.0, z) for z in (60.0, 120.0, 180.0, 240.0)] + [(x, 315.0) for x in (-60.0, -20.0, 20.0, 60.0)] + \
        [(115.0, z) for z in (240.0, 180.0, 120.0, 60.0)]
for i, (x, z) in enumerate(lamps):
    mesh("Light{:02d}".format(i), SPHERE, glow, unreal.Vector(x, 8.0, z), unreal.Vector(0.14, 0.14, 0.14))
for i, x in enumerate((-60.0, -20.0, 20.0, 60.0)):
    mesh("Emblem{}".format(i), CYLINDER, glow, unreal.Vector(x, 4.0, 400.0), unreal.Vector(0.32, 0.32, 0.06),
         rotation=unreal.Rotator(roll=90.0, pitch=0.0, yaw=0.0))
box("ApproachBox", unreal.Vector(0.0, 300.0, 150.0), unreal.Vector(400.0, 300.0, 150.0))
box("EnterBox", unreal.Vector(0.0, -300.0, 100.0), unreal.Vector(120.0, 120.0, 100.0))

defaults = unreal.get_default_object(door_bp.generated_class())
for name, pin_type, editable in (("IsOpen", pins.get_basic_type_by_name("bool"), False),
                                 ("NeedFree", pins.get_basic_type_by_name("int"), True)):
    try:
        defaults.get_editor_property(name)
        continue
    except Exception:
        pass
    if not pins.add_member_variable(door_bp, name, pin_type):
        raise RuntimeError("Could not add " + name)
    if editable:
        pins.set_blueprint_variable_instance_editable(door_bp, name, True)
    lines.append("BP_SecretDoor: variable " + name)
pins.compile_blueprint(door_bp)
unreal.get_default_object(door_bp.generated_class()).set_editor_property("NeedFree", 12)
library.save_asset(DOOR, False)

# ----- the door in area 1 -----
current = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name()
if not current.startswith(AREA1 + "."):
    if not level.load_level(AREA1):
        raise RuntimeError("Could not open " + AREA1)
if any(a.get_actor_label() == DOOR_LABEL for a in actors.get_all_level_actors()):
    lines.append(DOOR_LABEL + ": already there")
else:
    door = actors.spawn_actor_from_class(door_bp.generated_class(), DOOR_AT, unreal.Rotator(0.0, 0.0, 0.0))
    door.set_actor_label(DOOR_LABEL)
    door.set_folder_path("Area1/Achievements")
    lines.append(DOOR_LABEL + " at {}".format(DOOR_AT))
lines.append("{} saved {}".format(AREA1, level.save_current_level()))

# ----- the empty hidden stage -----
if library.does_asset_exist(SECRET):
    lines.append(SECRET + ": already there")
else:
    if not level.new_level(SECRET):
        raise RuntimeError("Could not create " + SECRET)
    floor = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0.0, 0.0, -50.0), unreal.Rotator(0.0, 0.0, 0.0))
    floor.static_mesh_component.set_static_mesh(CUBE)
    floor.set_actor_scale3d(unreal.Vector(30.0, 30.0, 1.0))
    floor.set_actor_label("Secret Floor")
    actors.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0.0, 0.0, 120.0), unreal.Rotator(0.0, 0.0, 0.0))
    sun = actors.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0.0, 0.0, 800.0), unreal.Rotator(0.0, -50.0, 30.0))
    sun.set_actor_label("Secret Sun")
    actors.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0.0, 0.0, 600.0), unreal.Rotator(0.0, 0.0, 0.0))
    actors.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator(0.0, 0.0, 0.0))
    lines.append("{} created, saved {}".format(SECRET, level.save_current_level()))
    level.load_level(AREA1)

with open(os.path.join(unreal.Paths.project_saved_dir(), "setup_secret_door.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
