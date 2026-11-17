# BP_GearExit (Gimmicks/Area): area 1's way out to the machine tower. A big machine gear lies on the great wall,
# a glowing gold ring at its middle. Stand on the ring (Center) and the player is held still; the gear starts
# turning and rises RiseHeight over RiseSeconds on an iron axle that grows out of the floor; at the top the item
# effects are saved, ChangingArea is set, the screen goes black and NextLevel opens (as BP_AreaExit does).
#   Lift (scene, moves up) > Gear (SM_Gear, collides), RingGold + RingCore (the gold ring), Glow (light), Center
#   (box), Label;  Axle (cylinder, stretched by the graph under Lift).
#   MI_GearExitGold  Hell's M_HellGlow in gold.
# Then, in LV_Area1_Ruins, the old BP_AreaExit on the wall gives way to a BP_GearExit just past the gate (the lintel
# is not in its way). Graph: BP_GearExit_EventGraph.txt from gen_gear_exit.ps1. Safe to run again. Run after
# setup_area2_gimmicks.py (SM_Gear, MI_Machine*), with the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_gear_exit.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Area"
MACHINE = "/Game/ThirdPerson/Blueprints/Gimmicks/Machine"
GLOW = "/Game/ThirdPerson/Blueprints/Gimmicks/Hell/M_HellGlow"
CYLINDER = "/Engine/BasicShapes/Cylinder"
LEVEL = "/Game/LV_Area1_Ruins"
GEAR_X = 13450.0           # on the great wall (12500..13900), past the gate (its lintel ends at 13150)
GEAR_SCALE = 2.2           # SM_Gear: radius 100, 30 thick, hub 26 across raised 6 -> 440 across
GEAR_THICK = 1.5
GEAR_HALF = 15.0 * GEAR_THICK
HUB_TOP = (15.0 + 6.0) * GEAR_THICK   # 31.5: where the player stands in the middle

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []

REAL = pins.get_basic_type_by_name("real")
BOOL = pins.get_basic_type_by_name("bool")
NAME = pins.get_basic_type_by_name("name")


def components(blueprint):
    found = {}
    for handle in subsystem.k2_gather_subobject_data_for_blueprint(blueprint):
        component = data_library.get_associated_object(data_library.get_data(handle))
        if component is not None:
            found[component.get_name().replace("_GEN_VARIABLE", "")] = (handle, component)
    return found


def add_component(blueprint, component_class, name, parent=None):
    existing = components(blueprint)
    if name in existing:
        return existing[name][1], False
    parent_handle = existing[parent][0] if parent else subsystem.k2_gather_subobject_data_for_blueprint(blueprint)[0]
    params = unreal.AddNewSubobjectParams(parent_handle=parent_handle, new_class=component_class, blueprint_context=blueprint)
    handle, _ = subsystem.add_new_subobject(params)
    if not data_library.is_handle_valid(handle):
        raise RuntimeError("Could not add " + name)
    subsystem.rename_subobject(handle, unreal.Text(name))
    lines.append("BP_GearExit: component " + name)
    return data_library.get_associated_object(data_library.get_data(handle)), True


def add_variables(blueprint, variables):
    defaults = unreal.get_default_object(blueprint.generated_class())
    for name, pin_type, editable in variables:
        try:
            defaults.get_editor_property(name)
            continue
        except Exception:
            pass
        if not pins.add_member_variable(blueprint, name, pin_type):
            raise RuntimeError("Could not add " + name)
        if editable:
            pins.set_blueprint_variable_instance_editable(blueprint, name, True)
        lines.append("BP_GearExit: variable " + name)
    pins.compile_blueprint(blueprint)
    return unreal.get_default_object(blueprint.generated_class())


def disk(component, material, z, across, thick):
    component.set_editor_property("static_mesh", unreal.load_asset(CYLINDER))
    component.set_material(0, material)
    component.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, z + thick / 2.0))
    component.set_editor_property("relative_scale3d", unreal.Vector(across / 100.0, across / 100.0, thick / 100.0))
    component.set_collision_profile_name("NoCollision")
    component.set_editor_property("cast_shadow", False)


# ----- the gold -----
gold_path = DIR + "/MI_GearExitGold"
if library.does_asset_exist(gold_path):
    gold = unreal.load_asset(gold_path)
else:
    gold = tools.create_asset("MI_GearExitGold", DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    editing.set_material_instance_parent(gold, unreal.load_asset(GLOW))
    editing.set_material_instance_vector_parameter_value(gold, "Color", unreal.LinearColor(1.0, 0.72, 0.22, 1.0))
    editing.set_material_instance_scalar_parameter_value(gold, "Glow", 6.0)
    library.save_asset(gold_path, False)
    lines.append("created " + gold_path)
iron = unreal.load_asset(MACHINE + "/MI_MachineIron")
brass = unreal.load_asset(MACHINE + "/MI_MachineBrass")
shadow = unreal.load_asset(MACHINE + "/MI_MachineShadow")
gear_mesh = unreal.load_asset(MACHINE + "/SM_Gear")
if not (iron and brass and shadow and gear_mesh):
    raise RuntimeError("Run setup_area2_gimmicks.py first (SM_Gear, MI_Machine*)")

# ----- BP_GearExit -----
PATH = DIR + "/BP_GearExit"
if library.does_asset_exist(PATH):
    bp = unreal.load_asset(PATH)
else:
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    bp = tools.create_asset("BP_GearExit", DIR, unreal.Blueprint, factory)
    lines.append("created " + PATH)

add_component(bp, unreal.SceneComponent, "Lift")
gear, made = add_component(bp, unreal.StaticMeshComponent, "Gear", "Lift")
if made:
    gear.set_editor_property("static_mesh", gear_mesh)
    for slot, material in enumerate((iron, brass, shadow)):
        gear.set_material(slot, material)
    gear.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, GEAR_HALF))
    gear.set_editor_property("relative_scale3d", unreal.Vector(GEAR_SCALE, GEAR_SCALE, GEAR_THICK))
ring, made = add_component(bp, unreal.StaticMeshComponent, "RingGold", "Lift")
if made:
    disk(ring, gold, HUB_TOP + 1.0, 150.0, 2.0)
core, made = add_component(bp, unreal.StaticMeshComponent, "RingCore", "Lift")
if made:
    disk(core, iron, HUB_TOP + 1.0, 104.0, 3.0)   # 1 cm prouder than the gold: no shared face
light, made = add_component(bp, unreal.PointLightComponent, "Glow", "Lift")
if made:
    light.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, HUB_TOP + 60.0))
    light.set_editor_property("light_color", unreal.Color(r=255, g=190, b=90, a=255))
    light.set_editor_property("intensity", 6000.0)
    light.set_editor_property("attenuation_radius", 700.0)
    light.set_editor_property("cast_shadows", False)
center, made = add_component(bp, unreal.BoxComponent, "Center", "Lift")
if made:
    center.set_editor_property("box_extent", unreal.Vector(15.0, 15.0, 50.0))
    center.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, HUB_TOP + 50.0))
    center.set_collision_profile_name("OverlapOnlyPawn")
label, made = add_component(bp, unreal.TextRenderComponent, "Label", "Lift")
if made:
    label.set_editor_property("text", unreal.Text("NEXT AREA"))
    label.set_editor_property("world_size", 60.0)
    label.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)
    label.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 300.0))
    label.set_editor_property("relative_rotation", unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0))
# The ride's camera: CamPivot rides up with Lift; the graph swings it round (yaw 180 -> 180 + OrbitDegrees: it starts
# behind a player walking in through the gate), from low and looking up (pitch 15) to high and looking down (-25),
# and draws the arm out from 600 to 1100. Camera is shaken at the start.
pivot, made = add_component(bp, unreal.SceneComponent, "CamPivot", "Lift")
if made:
    pivot.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, HUB_TOP + 90.0))
    pivot.set_editor_property("relative_rotation", unreal.Rotator(roll=0.0, pitch=15.0, yaw=180.0))
arm, made = add_component(bp, unreal.SpringArmComponent, "CamArm", "CamPivot")
if made:
    arm.set_editor_property("target_arm_length", 600.0)
    arm.set_editor_property("do_collision_test", False)
add_component(bp, unreal.CameraComponent, "Camera", "CamArm")
axle, made = add_component(bp, unreal.StaticMeshComponent, "Axle")
if made:
    axle.set_editor_property("static_mesh", unreal.load_asset(CYLINDER))
    axle.set_material(0, iron)
    axle.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 0.0))
    axle.set_editor_property("relative_scale3d", unreal.Vector(0.9, 0.9, 0.01))
    axle.set_collision_profile_name("NoCollision")

defaults = add_variables(bp, [
    ("NextLevel", NAME, True), ("RiseHeight", REAL, True), ("RiseSeconds", REAL, True), ("SpinSpeed", REAL, True),
    ("Started", BOOL, False), ("StartedAt", REAL, False), ("Leaving", BOOL, False),
    ("StartDelay", REAL, True), ("OrbitDegrees", REAL, True), ("ShakeSize", REAL, True)])
for name, value in (("RiseHeight", 2500.0), ("RiseSeconds", 7.0), ("SpinSpeed", 45.0),
                    ("StartDelay", 0.6), ("OrbitDegrees", 150.0), ("ShakeSize", 8.0)):
    if defaults.get_editor_property(name) == 0.0:
        defaults.set_editor_property(name, value)
pins.compile_blueprint(bp)
library.save_asset(PATH, False)

# ----- in area 1 -----
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not level.load_level(LEVEL):
    raise RuntimeError("Could not open " + LEVEL)
old, placed = None, None
for actor in actors.get_all_level_actors():
    name = actor.get_class().get_name()
    if name == "BP_AreaExit_C":
        old = actor
    elif name == "BP_GearExit_C":
        placed = actor
source = old or placed
if source is None:
    raise RuntimeError("No exit in " + LEVEL)
wall_top = source.get_actor_location().z
next_level = source.get_editor_property("NextLevel")
folder = source.get_folder_path()
label_text = source.get_actor_label().replace("Gear Exit", "Exit").replace("Exit", "Gear Exit")
if old is None:
    # Already a gear exit: left as it is (and any values set on it in the editor).
    lines.append("kept {} -> {}".format(placed.get_actor_label(), next_level))
else:
    if placed is not None:
        actors.destroy_actor(placed)
    actors.destroy_actor(old)
    exit_actor = actors.spawn_actor_from_class(bp.generated_class(), unreal.Vector(GEAR_X, 0.0, wall_top),
                                               unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0))
    exit_actor.set_actor_label(label_text)
    exit_actor.set_folder_path(str(folder))
    exit_actor.set_editor_property("NextLevel", next_level)
    lines.append("placed {} at ({:.0f}, 0, {:.0f}) -> {}".format(label_text, GEAR_X, wall_top, next_level))
lines.append("{} saved {}".format(LEVEL, level.save_current_level()))

with open(os.path.join(unreal.Paths.project_saved_dir(), "gear_exit.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
