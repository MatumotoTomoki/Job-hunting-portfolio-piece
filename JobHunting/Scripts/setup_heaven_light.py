# Area 4's light gimmicks, in /Game/ThirdPerson/Blueprints/Gimmicks/Heaven (run setup_area4_assets.py first):
#   BP_LightBeam      a shaft of light, 100 cm across and 100 cm tall around its origin (scale the actor). With
#                     OffSeconds above 0 it shines OnSeconds and is dark OffSeconds, from StartDelay on. With MoveSeconds
#                     above 0 it sways to MoveOffset and back, MoveSeconds each way. Lit while it shines.
#   BP_LightPlatform  a 100 cm block (scale the actor) that is solid only while its Beam is Lit and touching it;
#                     otherwise a faint outline the player falls through.
#   BP_LightShard     a shard of light to pick up (remembered for the run like a star coin, but not counted as one).
#   BP_Iwato          the stone door's keeper: once its Shard1..3 are all taken it pulls its Lever (so the
#                     BP_Mechanisms on that lever move, the rock and anything else), cuts to ShowCamera for ShowSeconds,
#                     and over BlendSeconds turns the level's sun from DarkRotation / DarkSun to BrightRotation /
#                     BrightSun and the sky light from DarkSky to BrightSky. Its Counter shows "taken / 3".
# Graphs: BP_*_EventGraph.txt from gen_heaven_light.ps1. Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_heaven_light.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven"
LEVER = "/Game/ThirdPerson/Blueprints/Gimmicks/Area/BP_Lever"
GLOW = "/Game/ThirdPerson/Blueprints/Gimmicks/Hell/M_HellGlow"
GHOST = "/Game/ThirdPerson/Blueprints/Gimmicks/Machine/M_SwitchGhost"
CUBE = "/Engine/BasicShapes/Cube"
CYLINDER = "/Engine/BasicShapes/Cylinder"

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []

REAL = pins.get_basic_type_by_name("real")
BOOL = pins.get_basic_type_by_name("bool")
STRING = pins.get_basic_type_by_name("string")
VECTOR = pins.get_struct_type(unreal.Vector.static_struct())
ROTATOR = pins.get_struct_type(unreal.Rotator.static_struct())


def ref(cls):
    return pins.get_object_reference_type(cls)


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


def set_defaults(defaults, values):
    # Only where still unset, so values tuned in the editor stay.
    for name, value in values:
        current = defaults.get_editor_property(name)
        if isinstance(value, unreal.Rotator):
            if current.pitch == 0.0 and current.yaw == 0.0 and current.roll == 0.0:
                defaults.set_editor_property(name, value)
        elif current == 0.0:
            defaults.set_editor_property(name, value)


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


def instance(name, parent, vectors=(), scalars=()):
    path = DIR + "/" + name
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    made = tools.create_asset(name, DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    editing.set_material_instance_parent(made, unreal.load_asset(parent))
    for key, color in vectors:
        editing.set_material_instance_vector_parameter_value(made, key, unreal.LinearColor(color[0], color[1], color[2], 1.0))
    for key, value in scalars:
        editing.set_material_instance_scalar_parameter_value(made, key, value)
    library.save_asset(path, False)
    lines.append("created " + path)
    return made


def shape(component, mesh, material, location=None, scale=None, rotation=None, collide=False):
    component.set_editor_property("static_mesh", unreal.load_asset(mesh))
    component.set_material(0, material)
    if location is not None:
        component.set_editor_property("relative_location", location)
    if scale is not None:
        component.set_editor_property("relative_scale3d", scale)
    if rotation is not None:
        component.set_editor_property("relative_rotation", rotation)
    if not collide:
        component.set_collision_profile_name("NoCollision")
        component.set_editor_property("cast_shadow", False)


WARM = (1.0, 0.86, 0.55)
solid_look = instance("MI_LightSolid", GLOW, [("Color", WARM)], [("Glow", 2.5)])
ghost_look = instance("MI_LightGhost", GHOST, [("Color", (1.0, 0.8, 0.45))], [("Opacity", 0.12)])
shard_look = instance("MI_LightShard", GLOW, [("Color", (1.0, 0.95, 0.8))], [("Glow", 12.0)])
shaft_look = unreal.load_asset(DIR + "/MI_LightShaft")
if shaft_look is None:
    raise RuntimeError("Run setup_area4_assets.py first (no MI_LightShaft)")

# ----- BP_LightBeam -----
beam = actor_blueprint("BP_LightBeam")
shaft, made = add_component(beam, unreal.StaticMeshComponent, "Shaft")
if made:
    shape(shaft, CYLINDER, shaft_look)
area, made = add_component(beam, unreal.BoxComponent, "Area")
if made:
    area.set_editor_property("box_extent", unreal.Vector(50.0, 50.0, 50.0))
    area.set_collision_profile_name("OverlapAllDynamic")
    area.set_editor_property("generate_overlap_events", True)
add_variables(beam, [
    ("MoveOffset", VECTOR, True), ("MoveSeconds", REAL, True), ("OnSeconds", REAL, True), ("OffSeconds", REAL, True),
    ("StartDelay", REAL, True), ("Lit", BOOL, False), ("StartLocation", VECTOR, False),
])
save(beam)

# ----- BP_LightPlatform -----
platform = actor_blueprint("BP_LightPlatform")
solid, made = add_component(platform, unreal.StaticMeshComponent, "Solid")
if made:
    shape(solid, CUBE, solid_look, collide=True)
ghost, made = add_component(platform, unreal.StaticMeshComponent, "Ghost")
if made:
    shape(ghost, CUBE, ghost_look)
    ghost.set_editor_property("visible", False)
probe, made = add_component(platform, unreal.BoxComponent, "Probe")
if made:
    probe.set_editor_property("box_extent", unreal.Vector(50.0, 50.0, 50.0))
    probe.set_collision_profile_name("OverlapAllDynamic")
    probe.set_editor_property("generate_overlap_events", True)
add_variables(platform, [("Beam", ref(beam.generated_class()), True)])
save(platform)

# ----- BP_LightShard -----
shard = actor_blueprint("BP_LightShard")
add_component(shard, unreal.SceneComponent, "Pivot")
crystal, made = add_component(shard, unreal.StaticMeshComponent, "Mesh", "Pivot")
if made:
    # A cube stood on a corner reads as a crystal.
    shape(crystal, CUBE, shard_look, scale=unreal.Vector(0.32, 0.32, 0.32),
          rotation=unreal.Rotator(roll=35.26, pitch=45.0, yaw=0.0))
glow_light, made = add_component(shard, unreal.PointLightComponent, "Glow", "Pivot")
if made:
    glow_light.set_editor_property("intensity", 8000.0)
    glow_light.set_editor_property("attenuation_radius", 900.0)
    glow_light.set_editor_property("light_color", unreal.Color(r=255, g=236, b=190, a=255))
    glow_light.set_editor_property("cast_shadows", False)
grab, made = add_component(shard, unreal.SphereComponent, "Grab")
if made:
    grab.set_editor_property("sphere_radius", 90.0)
    grab.set_collision_profile_name("OverlapOnlyPawn")
shard_defaults = add_variables(shard, [
    ("SpinSpeed", REAL, True), ("Collected", BOOL, False), ("CollectedFor", REAL, False), ("CoinId", STRING, False),
])
set_defaults(shard_defaults, (("SpinSpeed", 120.0),))
save(shard)

# ----- BP_Iwato -----
iwato = actor_blueprint("BP_Iwato")
counter, made = add_component(iwato, unreal.TextRenderComponent, "Counter")
if made:
    counter.set_editor_property("text", unreal.Text("0 / 3"))
    counter.set_editor_property("world_size", 90.0)
    counter.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)
    counter.set_editor_property("text_render_color", unreal.Color(r=255, g=220, b=140, a=255))
lever_class = unreal.load_asset(LEVER).generated_class()
iwato_defaults = add_variables(iwato, [
    ("Shard1", ref(shard.generated_class()), True), ("Shard2", ref(shard.generated_class()), True),
    ("Shard3", ref(shard.generated_class()), True), ("Lever", ref(lever_class), True),
    ("ShowCamera", ref(unreal.Actor.static_class()), True), ("ShowSeconds", REAL, True),
    ("BlendSeconds", REAL, True), ("DarkRotation", ROTATOR, True), ("BrightRotation", ROTATOR, True),
    ("DarkSun", REAL, True), ("BrightSun", REAL, True), ("DarkSky", REAL, True), ("BrightSky", REAL, True),
    ("Opened", BOOL, False), ("LightAlpha", REAL, False),
    ("Sun", ref(unreal.DirectionalLight.static_class()), False), ("Sky", ref(unreal.SkyLight.static_class()), False),
])
set_defaults(iwato_defaults, (
    ("ShowSeconds", 6.0), ("BlendSeconds", 4.0),
    ("DarkRotation", unreal.Rotator(roll=0.0, pitch=-4.0, yaw=115.0)),
    ("BrightRotation", unreal.Rotator(roll=0.0, pitch=-62.0, yaw=115.0)),
    ("DarkSun", 0.6), ("BrightSun", 10.0), ("DarkSky", 0.25), ("BrightSky", 1.5),
))
save(iwato)

with open(os.path.join(unreal.Paths.project_saved_dir(), "heaven_light.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
