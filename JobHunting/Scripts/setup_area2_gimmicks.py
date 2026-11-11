# The machine tower's (area 2) gimmicks, in /Game/ThirdPerson/Blueprints/Gimmicks/Machine:
#   SM_Gear          from build_gear_blender.py (re-imported every run)
#   BP_SpinGear      a gear that keeps turning about Z at SpinSpeed degrees a second; stand on it and it carries you.
#   BP_ToggleSwitch  touched by the player, it flips the game instance's SwitchRed; its button shows the colour now on.
#   BP_SwitchBlock   solid while SwitchRed matches its IsRed, a see-through ghost (no collision) otherwise.
#   BP_CageTrap      walk into its Trigger and a birdcage drops on the player from DropHeight; black; back at
#                    RespawnLocation (the area's start).
#   BP_Gondola       a cabin that leaves when the player steps in: TravelOffset away over TravelSeconds, waits
#                    WaitSeconds, comes back.
# The graphs come from gen_area2_gimmicks (BP_*_EventGraph.txt). Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_area2_gimmicks.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Machine"
GAME_INSTANCE = "/Game/ThirdPerson/Blueprints/BP_MyGameInstance"
FLAT_COLOR = "/Game/LevelPrototyping/Materials/M_FlatCol"
GLOW = "/Game/ThirdPerson/Blueprints/Gimmicks/Hell/M_HellGlow"
CAGE_MESH = "/Game/Prototype/Birdcage/SM_Birdcage_Blender"
CUBE = "/Engine/BasicShapes/Cube"
CYLINDER = "/Engine/BasicShapes/Cylinder"
GEAR_SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Models", "Gear", "SM_Gear.fbx")

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []

REAL = pins.get_basic_type_by_name("real")
BOOL = pins.get_basic_type_by_name("bool")
VECTOR = pins.get_struct_type(unreal.Vector.static_struct())


def add_variables(blueprint, variables):
    defaults = unreal.get_default_object(blueprint.generated_class())
    for name, pin_type, editable in variables:
        try:
            defaults.get_editor_property(name)
            continue
        except Exception:
            pass
        if not pins.add_member_variable(blueprint, name, pin_type):
            raise RuntimeError("Could not add {} to {}".format(name, blueprint.get_name()))
        if editable:
            pins.set_blueprint_variable_instance_editable(blueprint, name, True)
        lines.append("{}: variable {}".format(blueprint.get_name(), name))
    pins.compile_blueprint(blueprint)
    return unreal.get_default_object(blueprint.generated_class())


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
        raise RuntimeError("Could not add {} to {}".format(name, blueprint.get_name()))
    subsystem.rename_subobject(handle, unreal.Text(name))
    lines.append("{}: component {}".format(blueprint.get_name(), name))
    return data_library.get_associated_object(data_library.get_data(handle)), True


def actor_blueprint(name):
    path = DIR + "/" + name
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    lines.append("created " + path)
    return tools.create_asset(name, DIR, unreal.Blueprint, factory)


def save(blueprint):
    pins.compile_blueprint(blueprint)
    library.save_asset(DIR + "/" + blueprint.get_name(), False)


def flat(name, color):
    path = DIR + "/" + name
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    instance = tools.create_asset(name, DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    editing.set_material_instance_parent(instance, unreal.load_asset(FLAT_COLOR))
    editing.set_material_instance_vector_parameter_value(instance, "Base Color", unreal.LinearColor(color[0], color[1], color[2], 1.0))
    library.save_asset(path, False)
    lines.append("created " + path)
    return instance


def glow(name, color, strength):
    path = DIR + "/" + name
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    instance = tools.create_asset(name, DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    editing.set_material_instance_parent(instance, unreal.load_asset(GLOW))
    editing.set_material_instance_vector_parameter_value(instance, "Color", unreal.LinearColor(color[0], color[1], color[2], 1.0))
    editing.set_material_instance_scalar_parameter_value(instance, "Glow", strength)
    library.save_asset(path, False)
    lines.append("created " + path)
    return instance


def ghost_material():
    # See-through and unlit: the outline of a block that is switched off.
    path = DIR + "/M_SwitchGhost"
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    material = tools.create_asset("M_SwitchGhost", DIR, unreal.Material, unreal.MaterialFactoryNew())
    material.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    material.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    color = editing.create_material_expression(material, unreal.MaterialExpressionVectorParameter, -600, 0)
    color.set_editor_property("parameter_name", "Color")
    color.set_editor_property("default_value", unreal.LinearColor(1.0, 0.2, 0.1, 1.0))
    opacity = editing.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -600, 250)
    opacity.set_editor_property("parameter_name", "Opacity")
    opacity.set_editor_property("default_value", 0.22)
    editing.connect_material_property(color, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    editing.connect_material_property(opacity, "", unreal.MaterialProperty.MP_OPACITY)
    editing.recompile_material(material)
    library.save_asset(path, False)
    lines.append("created " + path)
    return material


def ghost(name, color):
    path = DIR + "/" + name
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    instance = tools.create_asset(name, DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    editing.set_material_instance_parent(instance, ghost_material())
    editing.set_material_instance_vector_parameter_value(instance, "Color", unreal.LinearColor(color[0], color[1], color[2], 1.0))
    library.save_asset(path, False)
    lines.append("created " + path)
    return instance


def shape(component, mesh, material, location, scale, collide=False, rotation=None):
    component.set_editor_property("static_mesh", unreal.load_asset(mesh) if isinstance(mesh, str) else mesh)
    component.set_material(0, material)
    component.set_editor_property("relative_location", location)
    component.set_editor_property("relative_scale3d", scale)
    if rotation is not None:
        component.set_editor_property("relative_rotation", rotation)
    if not collide:
        component.set_collision_profile_name("NoCollision")


RED = (1.0, 0.12, 0.08)
BLUE = (0.1, 0.35, 1.0)
iron = flat("MI_MachineIron", (0.12, 0.12, 0.13))
brass = flat("MI_MachineBrass", (0.62, 0.42, 0.16))
shadow = flat("MI_MachineShadow", (0.02, 0.02, 0.02))
red_solid = glow("MI_SwitchRed", RED, 1.2)
blue_solid = glow("MI_SwitchBlue", BLUE, 1.2)
red_ghost = ghost("MI_SwitchGhostRed", RED)
blue_ghost = ghost("MI_SwitchGhostBlue", BLUE)

# ----- the gear mesh -----
task = unreal.AssetImportTask()
task.filename = GEAR_SOURCE
task.destination_path = DIR
task.destination_name = "SM_Gear"
task.automated = True
task.save = True
task.replace_existing = True
options = unreal.FbxImportUI()
options.set_editor_property("import_materials", False)
options.set_editor_property("import_textures", False)
task.options = options
tools.import_asset_tasks([task])
gear = unreal.load_asset(DIR + "/SM_Gear")
for slot, material in enumerate((iron, brass, shadow)):
    gear.set_material(slot, material)
# Collide with the gear's own shape, teeth and all, not a rough hull: the player stands on it.
gear.get_editor_property("body_setup").set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
library.save_asset(DIR + "/SM_Gear", False)
lines.append("gear bounds {}".format(gear.get_bounds().box_extent))

# ----- the run's switch -----
game_instance = unreal.load_asset(GAME_INSTANCE)
gi = add_variables(game_instance, [("SwitchRed", BOOL, False)])
gi.set_editor_property("SwitchRed", True)
library.save_asset(GAME_INSTANCE, False)

# ----- BP_SpinGear -----
spin = actor_blueprint("BP_SpinGear")
add_component(spin, unreal.SceneComponent, "Pivot")
wheel, made = add_component(spin, unreal.StaticMeshComponent, "Wheel", "Pivot")
if made:
    shape(wheel, gear, iron, unreal.Vector(0.0, 0.0, 0.0), unreal.Vector(1.0, 1.0, 1.0), collide=True)
    for slot, material in enumerate((iron, brass, shadow)):
        wheel.set_material(slot, material)
spin_defaults = add_variables(spin, [("SpinSpeed", REAL, True)])
if spin_defaults.get_editor_property("SpinSpeed") == 0.0:
    spin_defaults.set_editor_property("SpinSpeed", 30.0)
save(spin)

# ----- BP_ToggleSwitch -----
switch = actor_blueprint("BP_ToggleSwitch")
base, made = add_component(switch, unreal.StaticMeshComponent, "Base")
if made:
    shape(base, CYLINDER, iron, unreal.Vector(0.0, 0.0, 15.0), unreal.Vector(1.4, 1.4, 0.3), collide=True)
for name, material in (("ButtonRed", red_solid), ("ButtonBlue", blue_solid)):
    button, made = add_component(switch, unreal.StaticMeshComponent, name)
    if made:
        shape(button, CYLINDER, material, unreal.Vector(0.0, 0.0, 36.0), unreal.Vector(0.9, 0.9, 0.12))
trigger, made = add_component(switch, unreal.BoxComponent, "Trigger")
if made:
    trigger.set_editor_property("box_extent", unreal.Vector(80.0, 80.0, 60.0))
    trigger.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 60.0))
    trigger.set_collision_profile_name("OverlapOnlyPawn")
add_variables(switch, [("Busy", BOOL, False)])
save(switch)

# ----- BP_SwitchBlock: a 100 cm cube; scale the actor -----
block = actor_blueprint("BP_SwitchBlock")
solid, made = add_component(block, unreal.StaticMeshComponent, "Solid")
if made:
    shape(solid, CUBE, red_solid, unreal.Vector(0.0, 0.0, 0.0), unreal.Vector(1.0, 1.0, 1.0), collide=True)
ghost_part, made = add_component(block, unreal.StaticMeshComponent, "Ghost")
if made:
    shape(ghost_part, CUBE, red_ghost, unreal.Vector(0.0, 0.0, 0.0), unreal.Vector(1.0, 1.0, 1.0))
    ghost_part.set_editor_property("cast_shadow", False)
add_variables(block, [("IsRed", BOOL, True), ("Shown", BOOL, False), ("Ready", BOOL, False)])
save(block)

# ----- BP_CageTrap -----
trap = actor_blueprint("BP_CageTrap")
area, made = add_component(trap, unreal.BoxComponent, "Trigger")
if made:
    area.set_editor_property("box_extent", unreal.Vector(150.0, 150.0, 100.0))
    area.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 100.0))
    area.set_collision_profile_name("OverlapOnlyPawn")
cage_mesh = unreal.load_asset(CAGE_MESH)
cage, made = add_component(trap, unreal.StaticMeshComponent, "Cage")
if made:
    cage.set_editor_property("static_mesh", cage_mesh)
    cage.set_collision_profile_name("NoCollision")
    cage.set_editor_property("visible", False)
# The birdcage model is 70 x 85 x 112 cm with its pivot at the bottom: big enough to shut the player in at x2.6.
cage.set_editor_property("relative_scale3d", unreal.Vector(2.6, 2.6, 2.6))
lines.append("cage mesh bounds origin {} extent {}".format(cage_mesh.get_bounds().origin, cage_mesh.get_bounds().box_extent))
trap_defaults = add_variables(trap, [("RespawnLocation", VECTOR, True), ("RespawnYaw", REAL, True), ("DropHeight", REAL, True), ("Busy", BOOL, False)])
if trap_defaults.get_editor_property("DropHeight") == 0.0:
    trap_defaults.set_editor_property("DropHeight", 1500.0)
save(trap)

# ----- BP_Gondola: a cabin hanging under a hanger; the cable itself is placed in the level -----
gondola = actor_blueprint("BP_Gondola")
add_component(gondola, unreal.SceneComponent, "Cabin")
floor, made = add_component(gondola, unreal.StaticMeshComponent, "Floor", "Cabin")
if made:
    shape(floor, CUBE, brass, unreal.Vector(0.0, 0.0, -10.0), unreal.Vector(3.0, 3.0, 0.2), collide=True)
for i, (x, y) in enumerate(((-140.0, -140.0), (140.0, -140.0), (-140.0, 140.0), (140.0, 140.0))):
    post, made = add_component(gondola, unreal.StaticMeshComponent, "Post{}".format(i + 1), "Cabin")
    if made:
        shape(post, CYLINDER, iron, unreal.Vector(x, y, 130.0), unreal.Vector(0.12, 0.12, 2.6))
roof, made = add_component(gondola, unreal.StaticMeshComponent, "Roof", "Cabin")
if made:
    shape(roof, CUBE, iron, unreal.Vector(0.0, 0.0, 265.0), unreal.Vector(3.1, 3.1, 0.1))
hanger, made = add_component(gondola, unreal.StaticMeshComponent, "Hanger", "Cabin")
if made:
    shape(hanger, CYLINDER, iron, unreal.Vector(0.0, 0.0, 340.0), unreal.Vector(0.15, 0.15, 1.5))
step, made = add_component(gondola, unreal.BoxComponent, "Trigger", "Cabin")
if made:
    step.set_editor_property("box_extent", unreal.Vector(140.0, 140.0, 60.0))
    step.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 60.0))
    step.set_collision_profile_name("OverlapOnlyPawn")
gondola_defaults = add_variables(gondola, [("TravelOffset", VECTOR, True), ("TravelSeconds", REAL, True), ("WaitSeconds", REAL, True), ("Moving", BOOL, False)])
for name, value in (("TravelSeconds", 6.0), ("WaitSeconds", 2.0)):
    if gondola_defaults.get_editor_property(name) == 0.0:
        gondola_defaults.set_editor_property(name, value)
save(gondola)

# ----- BP_FallCatcher: a big box under a high area; the player falling into it is dropped straight below -50 m,
# where the character's own fall check sends them to the flag or the PlayerStart (no long fall to wait through) -----
catcher = actor_blueprint("BP_FallCatcher")
net, made = add_component(catcher, unreal.BoxComponent, "Net")
if made:
    net.set_editor_property("box_extent", unreal.Vector(50.0, 50.0, 50.0))
    net.set_collision_profile_name("OverlapOnlyPawn")
save(catcher)

with open(os.path.join(unreal.Paths.project_saved_dir(), "area2_gimmicks.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
