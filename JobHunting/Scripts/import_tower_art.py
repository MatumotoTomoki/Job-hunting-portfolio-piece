# Brings in area 2's "ancient machine" art from build_tower_blender.py and puts it in LV_Area2_Tower:
#   /Game/Art/Tower/Textures/T_Tower*_C / _N / _E   the painted colour, normal and glow-mask maps
#   /Game/Art/Tower/M_TowerSurface                  Color x Tint, Normal, Roughness, Metallic, Emissive = Mask x GlowColor x Glow
#   /Game/Art/Tower/MI_Tower<Slot>                  one per slot of the meshes (Masonry, Flagstone, Iron, ...)
#   /Game/Art/Tower/SM_Tower_<letter>               one mesh per section, world positioned, no collision
#   /Game/Art/Tower/Gears/SM_TowerGear_<letter><n>  the great wall gears, placed as "A2 Gear <letter><n>"; their
#                                                   MI_TowerGear<Slot> materials turn them (Spin, SpinSpeed)
# In the level: for every section that has a mesh, its plain boxes (the "A2 ..." StaticMeshActors in that section's
# folder) stay as the collision but are hidden, and the mesh is placed at the origin as "A2 Art <letter>". Gimmicks
# (BP actors) are left exactly as they are. Run it again after build_area2_tower.py (which brings the plain boxes back
# and removes the art: everything labelled "A2 " is rebuilt). With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\import_tower_art.py -unattended -nop4 -nosplash -stdout
import glob
import json
import os

import unreal

SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Models", "Tower")
DIR = "/Game/Art/Tower"
TEX_DIR = DIR + "/Textures"
LEVEL = "/Game/LV_Area2_Tower"
SLOTS = ["Masonry", "Flagstone", "Iron", "Bronze", "Brass", "Glyph", "Ember", "Shadow"]
ORANGE = (1.0, 0.45, 0.12)
LOOK = {   # roughness, metallic, glow, glow colour
    "Masonry": (0.85, 0.0, 0.0, ORANGE), "Flagstone": (0.8, 0.0, 0.0, ORANGE), "Iron": (0.55, 0.75, 0.0, ORANGE),
    "Bronze": (0.45, 0.7, 0.0, ORANGE), "Brass": (0.3, 1.0, 0.0, ORANGE), "Glyph": (0.8, 0.0, 3.0, ORANGE),
    "Ember": (1.0, 0.0, 6.0, ORANGE), "Shadow": (1.0, 0.0, 0.0, ORANGE),
}

# UE 5.6 reads FBX through Interchange, which ignores the FbxImportUI options below (the vertex colours were dropped):
# use the classic FBX importer for this run.
unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
lines = []


def import_file(path, destination, options=None):
    task = unreal.AssetImportTask()
    task.filename = path
    task.destination_path = destination
    task.automated = True
    task.save = True
    task.replace_existing = True
    if options:
        task.options = options
    tools.import_asset_tasks([task])
    return destination + "/" + os.path.splitext(os.path.basename(path))[0]


# ----- textures -----
textures = {}
for path in sorted(glob.glob(os.path.join(SOURCE, "Textures", "T_Tower*.png"))):
    asset_path = import_file(path, TEX_DIR)
    texture = unreal.load_asset(asset_path)
    if asset_path.endswith("_N"):
        texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
        texture.set_editor_property("srgb", False)
    elif asset_path.endswith("_E"):
        texture.set_editor_property("srgb", False)
    library.save_asset(asset_path, False)
    textures[os.path.basename(asset_path)] = texture
lines.append("{} textures".format(len(textures)))

# ----- the surface material (its graph is rebuilt every run, so changes here reach the existing asset) -----
path = DIR + "/M_TowerSurface"
if library.does_asset_exist(path):
    material = unreal.load_asset(path)
    editing.delete_all_material_expressions(material)
else:
    material = tools.create_asset("M_TowerSurface", DIR, unreal.Material, unreal.MaterialFactoryNew())
if True:
    def node(kind, x, y):
        return editing.create_material_expression(material, kind, x, y)

    color = node(unreal.MaterialExpressionTextureSampleParameter2D, -900, -250)
    color.set_editor_property("parameter_name", "Color")
    color.set_editor_property("texture", textures["T_TowerMasonry_C"])
    tint = node(unreal.MaterialExpressionVectorParameter, -900, 0)
    tint.set_editor_property("parameter_name", "Tint")
    tint.set_editor_property("default_value", unreal.LinearColor(1.0, 1.0, 1.0, 1.0))
    tinted = node(unreal.MaterialExpressionMultiply, -600, -200)
    normal = node(unreal.MaterialExpressionTextureSampleParameter2D, -900, 200)
    normal.set_editor_property("parameter_name", "Normal")
    normal.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    normal.set_editor_property("texture", textures["T_TowerMasonry_N"])
    rough = node(unreal.MaterialExpressionScalarParameter, -600, 50)
    rough.set_editor_property("parameter_name", "Roughness")
    rough.set_editor_property("default_value", 0.85)
    metal = node(unreal.MaterialExpressionScalarParameter, -600, 130)
    metal.set_editor_property("parameter_name", "Metallic")
    mask = node(unreal.MaterialExpressionTextureSampleParameter2D, -900, 450)
    mask.set_editor_property("parameter_name", "Mask")
    mask.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
    mask.set_editor_property("texture", textures["T_TowerBlack_E"])
    glow_color = node(unreal.MaterialExpressionVectorParameter, -650, 550)
    glow_color.set_editor_property("parameter_name", "GlowColor")
    glow_color.set_editor_property("default_value", unreal.LinearColor(ORANGE[0], ORANGE[1], ORANGE[2], 1.0))
    glow = node(unreal.MaterialExpressionScalarParameter, -650, 700)
    glow.set_editor_property("parameter_name", "Glow")
    m1 = node(unreal.MaterialExpressionMultiply, -400, 480)
    m2 = node(unreal.MaterialExpressionMultiply, -250, 520)
    # the meshes' vertex colour: a tint per piece, grime at the foot, a slow light/dark wash (build_tower_blender.py)
    vertex = node(unreal.MaterialExpressionVertexColor, -900, -400)
    stained = node(unreal.MaterialExpressionMultiply, -450, -250)
    editing.connect_material_expressions(color, "RGB", tinted, "A")
    editing.connect_material_expressions(tint, "", tinted, "B")
    editing.connect_material_expressions(tinted, "", stained, "A")
    editing.connect_material_expressions(vertex, "", stained, "B")
    editing.connect_material_expressions(mask, "R", m1, "A")
    editing.connect_material_expressions(glow_color, "", m1, "B")
    editing.connect_material_expressions(m1, "", m2, "A")
    editing.connect_material_expressions(glow, "", m2, "B")
    editing.connect_material_property(stained, "", unreal.MaterialProperty.MP_BASE_COLOR)
    editing.connect_material_property(normal, "RGB", unreal.MaterialProperty.MP_NORMAL)
    editing.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    editing.connect_material_property(metal, "", unreal.MaterialProperty.MP_METALLIC)
    editing.connect_material_property(m2, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    # Spin (static switch, on only in the MI_TowerGear* instances): the mesh turns about its own +X axis through its
    # pivot, SpinSpeed turns per second - the great wall gears turn without a Blueprint.
    spin = node(unreal.MaterialExpressionStaticSwitchParameter, -250, 900)
    spin.set_editor_property("parameter_name", "Spin")
    speed = node(unreal.MaterialExpressionScalarParameter, -1100, 950)
    speed.set_editor_property("parameter_name", "SpinSpeed")
    speed.set_editor_property("default_value", 0.015)
    clock = node(unreal.MaterialExpressionTime, -1100, 870)
    angle = node(unreal.MaterialExpressionMultiply, -900, 900)
    local_x = node(unreal.MaterialExpressionConstant3Vector, -1100, 1050)
    local_x.set_editor_property("constant", unreal.LinearColor(1.0, 0.0, 0.0, 0.0))
    to_world = node(unreal.MaterialExpressionTransform, -900, 1050)
    to_world.set_editor_property("transform_source_type", unreal.MaterialVectorCoordTransformSource.TRANSFORMSOURCE_LOCAL)
    to_world.set_editor_property("transform_type", unreal.MaterialVectorCoordTransform.TRANSFORM_WORLD)
    axis = node(unreal.MaterialExpressionNormalize, -700, 1050)
    pivot = node(unreal.MaterialExpressionObjectPositionWS, -700, 1150)
    position = node(unreal.MaterialExpressionWorldPosition, -700, 1230)
    turn = node(unreal.MaterialExpressionRotateAboutAxis, -450, 1000)
    still = node(unreal.MaterialExpressionConstant, -450, 1200)
    editing.connect_material_expressions(clock, "", angle, "A")
    editing.connect_material_expressions(speed, "", angle, "B")
    editing.connect_material_expressions(local_x, "", to_world, "")
    editing.connect_material_expressions(to_world, "", axis, "")
    editing.connect_material_expressions(axis, "", turn, "NormalizedRotationAxis")
    editing.connect_material_expressions(angle, "", turn, "RotationAngle")
    editing.connect_material_expressions(pivot, "", turn, "PivotPoint")
    editing.connect_material_expressions(position, "", turn, "Position")
    editing.connect_material_expressions(turn, "", spin, "True")
    editing.connect_material_expressions(still, "", spin, "False")
    editing.connect_material_property(spin, "", unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
    editing.recompile_material(material)
    library.save_asset(path, False)
    lines.append("built " + path)
surface = unreal.load_asset(path)

instances = {}
gear_instances = {}
for slot in SLOTS:
    mi_path = DIR + "/MI_Tower" + slot
    if library.does_asset_exist(mi_path):
        mi = unreal.load_asset(mi_path)
    else:
        mi = tools.create_asset("MI_Tower" + slot, DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        editing.set_material_instance_parent(mi, surface)
    roughness, metallic, glow_value, glow_color = LOOK[slot]
    editing.set_material_instance_texture_parameter_value(mi, "Color", textures["T_Tower" + slot + "_C"])
    if "T_Tower" + slot + "_N" in textures:
        editing.set_material_instance_texture_parameter_value(mi, "Normal", textures["T_Tower" + slot + "_N"])
    editing.set_material_instance_texture_parameter_value(mi, "Mask", textures.get("T_Tower" + slot + "_E", textures["T_TowerBlack_E"]))
    editing.set_material_instance_scalar_parameter_value(mi, "Roughness", roughness)
    editing.set_material_instance_scalar_parameter_value(mi, "Metallic", metallic)
    editing.set_material_instance_scalar_parameter_value(mi, "Glow", glow_value)
    editing.set_material_instance_vector_parameter_value(mi, "GlowColor", unreal.LinearColor(glow_color[0], glow_color[1], glow_color[2], 1.0))
    library.save_asset(mi_path, False)
    instances["M_Tower" + slot] = mi
    # the turning version for the wall gears: same look, Spin on
    gear_path = DIR + "/MI_TowerGear" + slot
    if library.does_asset_exist(gear_path):
        gear_mi = unreal.load_asset(gear_path)
    else:
        gear_mi = tools.create_asset("MI_TowerGear" + slot, DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    editing.set_material_instance_parent(gear_mi, mi)
    editing.set_material_instance_static_switch_parameter_value(gear_mi, "Spin", True)
    editing.update_material_instance(gear_mi)
    library.save_asset(gear_path, False)
    gear_instances["M_Tower" + slot] = gear_mi

# ----- the meshes -----
def import_mesh(path, destination, materials):
    options = unreal.FbxImportUI()
    options.set_editor_property("import_materials", False)
    options.set_editor_property("import_textures", False)
    data = options.get_editor_property("static_mesh_import_data")
    data.set_editor_property("auto_generate_collision", False)
    data.set_editor_property("combine_meshes", True)
    data.set_editor_property("generate_lightmap_u_vs", False)
    data.set_editor_property("vertex_color_import_option", unreal.VertexColorImportOption.REPLACE)
    # A re-import over the old asset keeps the old asset's import settings (vertex colours ignored): start fresh.
    # The level's "A2 Art" actors are placed again below, so nothing is left pointing at the deleted mesh.
    old = destination + "/" + os.path.splitext(os.path.basename(path))[0]
    if library.does_asset_exist(old):
        library.delete_asset(old)
    asset_path = import_file(path, destination, options)
    mesh = unreal.load_asset(asset_path)
    for i, static_material in enumerate(mesh.get_editor_property("static_materials")):
        name = str(static_material.get_editor_property("material_slot_name"))
        if name in materials:
            mesh.set_material(i, materials[name])
    library.save_asset(asset_path, False)
    return asset_path, mesh


meshes = {}
for path in sorted(glob.glob(os.path.join(SOURCE, "SM_Tower_*.fbx"))):
    asset_path, mesh = import_mesh(path, DIR, instances)
    meshes[asset_path.rsplit("_", 1)[1]] = mesh
    lines.append("imported {} bounds {}".format(asset_path, mesh.get_bounds()))

# the great wall gears (turning: MI_TowerGear*), and where each goes (tower_gears_<letter>.json)
gears = []
for path in sorted(glob.glob(os.path.join(SOURCE, "tower_gears_*.json"))):
    for spec in json.load(open(path, encoding="utf-8")):
        _, mesh = import_mesh(os.path.join(SOURCE, spec["name"] + ".fbx"), DIR + "/Gears", gear_instances)
        gears.append((spec, mesh))
lines.append("{} gears imported".format(len(gears)))

# ----- the level -----
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not level.load_level(LEVEL):
    raise RuntimeError("Could not open " + LEVEL)
for actor in actors.get_all_level_actors():
    if actor.get_actor_label().startswith(("A2 Art ", "A2 Gear ")):
        actors.destroy_actor(actor)
for spec, mesh in gears:
    x, y, z = spec["location"]
    gear = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z), unreal.Rotator(0.0, 0.0, spec["yaw"]))
    gear.set_actor_label("A2 Gear " + spec["name"].rsplit("_", 1)[1])
    gear.set_folder_path("Area2/Art")
    component = gear.get_editor_property("static_mesh_component")
    component.set_static_mesh(mesh)
    component.set_collision_profile_name("NoCollision")
    component.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
for letter, mesh in sorted(meshes.items()):
    low = [1e9, 1e9, 1e9]
    high = [-1e9, -1e9, -1e9]
    hidden = 0
    for actor in actors.get_all_level_actors():
        folder = str(actor.get_folder_path())
        if not actor.get_actor_label().startswith("A2 ") or not isinstance(actor, unreal.StaticMeshActor):
            continue
        if not folder.startswith("Area2/" + letter + " "):
            continue
        origin, extent = actor.get_actor_bounds(False)
        for k, (o, e) in enumerate(((origin.x, extent.x), (origin.y, extent.y), (origin.z, extent.z))):
            low[k], high[k] = min(low[k], o - e), max(high[k], o + e)
        component = actor.get_editor_property("static_mesh_component")
        component.set_editor_property("visible", False)
        actor.set_actor_hidden_in_game(True)
        hidden += 1
    art = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator(0.0, 0.0, 0.0))
    art.set_actor_label("A2 Art " + letter)
    art.set_folder_path("Area2/Art")
    component = art.get_editor_property("static_mesh_component")
    component.set_static_mesh(mesh)
    component.set_collision_profile_name("NoCollision")
    a_origin, a_extent = art.get_actor_bounds(False)
    lines.append("section {}: {} boxes hidden; boxes x {:.0f}..{:.0f} y {:.0f}..{:.0f} z {:.0f}..{:.0f}".format(letter, hidden, low[0], high[0], low[1], high[1], low[2], high[2]))
    lines.append("           art   x {:.0f}..{:.0f} y {:.0f}..{:.0f} z {:.0f}..{:.0f}".format(
        a_origin.x - a_extent.x, a_origin.x + a_extent.x, a_origin.y - a_extent.y, a_origin.y + a_extent.y,
        a_origin.z - a_extent.z, a_origin.z + a_extent.z))
lines.append("{} saved {}".format(LEVEL, level.save_current_level()))

with open(os.path.join(unreal.Paths.project_saved_dir(), "tower_art.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
