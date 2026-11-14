# The sky area's (area 3) gimmicks and looks, in /Game/ThirdPerson/Blueprints/Gimmicks/Sky:
#   SM_SkyCloud, SM_SkyIsland  from build_sky_blender.py (re-imported every run); MI_Sky* flat colours for them.
#   T_WindStreak, M_WindStreak, MI_WindStreak   see-through white streaks scrolling along U (build_wind_texture.ps1).
#   BP_VanishCloud  a cloud to stand on (100 cm across; scale X/Y): stepped on, it sinks a little, and StaySeconds later
#                   it is gone (no collision) for GoneSeconds, then comes back.
#   BP_WindZone     a 100 cm box (scale the actor to size it) that pushes the player along the actor's forward (X)
#                   axis: Strength cm/s2, easing off as the player's speed along it nears MaxSpeed. Turn the actor to aim
#                   it; pitch 90 is an updraft. With GustOn and GustOff above 0 it blows GustOn seconds, rests GustOff
#                   seconds, from StartDelay. Its streaks show while it blows.
#   BP_MovingIsland a copy of BP_MovingPlatform (same graph and settings: MoveOffset, MoveSeconds, WaitSeconds) as a
#                   floating island 350 cm across, its grass top at the actor's origin.
# The VanishCloud and WindZone graphs come from gen_area3_gimmicks (BP_*_EventGraph.txt). Safe to run again. With the
# editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_area3_gimmicks.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Sky"
GIMMICKS = "/Game/ThirdPerson/Blueprints/Gimmicks"
FLAT_COLOR = "/Game/LevelPrototyping/Materials/M_FlatCol"
PLANE = "/Engine/BasicShapes/Plane"
SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Models", "Sky")
ISLAND_SIZE = 350.0

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []

REAL = pins.get_basic_type_by_name("real")
BOOL = pins.get_basic_type_by_name("bool")


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
        if isinstance(value, bool):
            continue
        if defaults.get_editor_property(name) == 0.0:
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


def import_file(name, mesh=True):
    task = unreal.AssetImportTask()
    task.filename = os.path.join(SOURCE, name)
    task.destination_path = DIR
    task.automated = True
    task.save = True
    task.replace_existing = True
    if mesh:
        options = unreal.FbxImportUI()
        options.set_editor_property("import_materials", False)
        options.set_editor_property("import_textures", False)
        options.get_editor_property("static_mesh_import_data").set_editor_property("auto_generate_collision", False)
        task.options = options
    tools.import_asset_tasks([task])
    path = DIR + "/" + os.path.splitext(name)[0]
    lines.append("imported " + path)
    return unreal.load_asset(path)


# ----- looks -----
cloud_white = flat("MI_SkyCloud", (0.92, 0.94, 1.0))
grass = flat("MI_SkyGrass", (0.25, 0.6, 0.2))
rock = flat("MI_SkyRock", (0.55, 0.5, 0.45))
flat("MI_SkyMarble", (0.88, 0.86, 0.8))
flat("MI_SkyGold", (0.9, 0.68, 0.2))

cloud_mesh = import_file("SM_SkyCloud.fbx")
cloud_mesh.set_material(0, cloud_white)
library.save_asset(DIR + "/SM_SkyCloud", False)
island_mesh = import_file("SM_SkyIsland.fbx")
island_mesh.set_material(0, grass)
island_mesh.set_material(1, rock)
library.save_asset(DIR + "/SM_SkyIsland", False)
# The FBX import drops the UBX_/UCX_ shapes, so the collision boxes are written in by hand.
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fix_sky_collision.py"), encoding="utf-8") as fix:
    exec(fix.read(), {"__name__": "fix_sky_collision"})
for mesh in (cloud_mesh, island_mesh):
    lines.append("{} bounds {} collision boxes {} convex {}".format(
        mesh.get_name(), mesh.get_bounds().box_extent,
        len(mesh.get_editor_property("body_setup").get_editor_property("agg_geom").get_editor_property("box_elems")),
        len(mesh.get_editor_property("body_setup").get_editor_property("agg_geom").get_editor_property("convex_elems"))))

streak_texture = import_file("T_WindStreak.png", mesh=False)
streak_texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_EDITOR_ICON)
library.save_asset(DIR + "/T_WindStreak", False)

path = DIR + "/M_WindStreak"
if not library.does_asset_exist(path):
    material = tools.create_asset("M_WindStreak", DIR, unreal.Material, unreal.MaterialFactoryNew())
    material.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    material.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    material.set_editor_property("two_sided", True)
    # UV + (Time * Speed, 0): the streaks run along U.
    uv = editing.create_material_expression(material, unreal.MaterialExpressionTextureCoordinate, -1200, 0)
    time = editing.create_material_expression(material, unreal.MaterialExpressionTime, -1200, 200)
    speed = editing.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1200, 300)
    speed.set_editor_property("parameter_name", "Speed")
    speed.set_editor_property("default_value", 1.2)
    scroll = editing.create_material_expression(material, unreal.MaterialExpressionMultiply, -1000, 250)
    zero = editing.create_material_expression(material, unreal.MaterialExpressionConstant, -1000, 400)
    sideways = editing.create_material_expression(material, unreal.MaterialExpressionAppendVector, -850, 300)
    moved = editing.create_material_expression(material, unreal.MaterialExpressionAdd, -700, 100)
    sample = editing.create_material_expression(material, unreal.MaterialExpressionTextureSampleParameter2D, -500, 100)
    sample.set_editor_property("parameter_name", "Streaks")
    sample.set_editor_property("texture", streak_texture)
    color = editing.create_material_expression(material, unreal.MaterialExpressionVectorParameter, -500, 400)
    color.set_editor_property("parameter_name", "Color")
    color.set_editor_property("default_value", unreal.LinearColor(1.0, 1.0, 1.0, 1.0))
    opacity = editing.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -500, 550)
    opacity.set_editor_property("parameter_name", "Opacity")
    opacity.set_editor_property("default_value", 0.7)
    tint = editing.create_material_expression(material, unreal.MaterialExpressionMultiply, -250, 200)
    see = editing.create_material_expression(material, unreal.MaterialExpressionMultiply, -250, 450)
    editing.connect_material_expressions(time, "", scroll, "A")
    editing.connect_material_expressions(speed, "", scroll, "B")
    editing.connect_material_expressions(scroll, "", sideways, "A")
    editing.connect_material_expressions(zero, "", sideways, "B")
    editing.connect_material_expressions(uv, "", moved, "A")
    editing.connect_material_expressions(sideways, "", moved, "B")
    editing.connect_material_expressions(moved, "", sample, "UVs")
    editing.connect_material_expressions(sample, "RGB", tint, "A")
    editing.connect_material_expressions(color, "", tint, "B")
    editing.connect_material_expressions(sample, "A", see, "A")
    editing.connect_material_expressions(opacity, "", see, "B")
    editing.connect_material_property(tint, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    editing.connect_material_property(see, "", unreal.MaterialProperty.MP_OPACITY)
    editing.recompile_material(material)
    library.save_asset(path, False)
    lines.append("created " + path)
streak = unreal.load_asset(DIR + "/MI_WindStreak") if library.does_asset_exist(DIR + "/MI_WindStreak") else None
if streak is None:
    streak = tools.create_asset("MI_WindStreak", DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    editing.set_material_instance_parent(streak, unreal.load_asset(path))
    library.save_asset(DIR + "/MI_WindStreak", False)
    lines.append("created " + DIR + "/MI_WindStreak")

# ----- BP_VanishCloud -----
vanish = actor_blueprint("BP_VanishCloud")
cloud, made = add_component(vanish, unreal.StaticMeshComponent, "Cloud")
if made:
    cloud.set_editor_property("static_mesh", cloud_mesh)
    cloud.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
trigger, made = add_component(vanish, unreal.BoxComponent, "Trigger")
if made:
    trigger.set_editor_property("box_extent", unreal.Vector(42.0, 42.0, 30.0))
    trigger.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 30.0))
    trigger.set_collision_profile_name("OverlapOnlyPawn")
vanish_defaults = add_variables(vanish, [("StaySeconds", REAL, True), ("GoneSeconds", REAL, True), ("Busy", BOOL, False)])
set_defaults(vanish_defaults, (("StaySeconds", 0.7), ("GoneSeconds", 3.0)))
save(vanish)

# ----- BP_WindZone -----
wind = actor_blueprint("BP_WindZone")
zone, made = add_component(wind, unreal.BoxComponent, "Zone")
if made:
    zone.set_editor_property("box_extent", unreal.Vector(50.0, 50.0, 50.0))
    zone.set_collision_profile_name("OverlapOnlyPawn")
plane = unreal.load_asset(PLANE)
for name, location, rotation in (("StreaksSide", unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator(roll=90.0, pitch=0.0, yaw=0.0)),
                                 ("StreaksTop", unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0))):
    part, made = add_component(wind, unreal.StaticMeshComponent, name)
    if made:
        part.set_editor_property("static_mesh", plane)
        part.set_material(0, streak)
        part.set_editor_property("relative_location", location)
        part.set_editor_property("relative_rotation", rotation)
        part.set_collision_profile_name("NoCollision")
        part.set_editor_property("cast_shadow", False)
wind_defaults = add_variables(wind, [("Strength", REAL, True), ("MaxSpeed", REAL, True), ("GustOn", REAL, True),
                                     ("GustOff", REAL, True), ("StartDelay", REAL, True), ("Active", BOOL, False)])
set_defaults(wind_defaults, (("Strength", 900.0), ("MaxSpeed", 600.0)))
wind_defaults.set_editor_property("Active", True)
save(wind)

# ----- BP_MovingIsland: BP_MovingPlatform's graph with an island for a floor -----
island_path = DIR + "/BP_MovingIsland"
if not library.does_asset_exist(island_path):
    library.duplicate_asset(GIMMICKS + "/BP_MovingPlatform", island_path)
    lines.append("created " + island_path + " from BP_MovingPlatform")
moving = unreal.load_asset(island_path)
floor = components(moving).get("FloorMesh")
if floor is None:
    raise RuntimeError("BP_MovingIsland has no FloorMesh")
floor = floor[1]
floor.set_editor_property("static_mesh", island_mesh)
floor.set_material(0, grass)
floor.set_material(1, rock)
floor.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 0.0))
floor.set_editor_property("relative_scale3d", unreal.Vector(ISLAND_SIZE / 100.0, ISLAND_SIZE / 100.0, 2.5))
save(moving)

with open(os.path.join(unreal.Paths.project_saved_dir(), "area3_gimmicks.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
