# Brings in area 1's Roman ruins art from build_ruins_blender.py and puts it in LV_Area1_Ruins:
#   /Game/Art/Ruins/Textures/T_Ruins*_C / _N     the painted colour and normal maps
#   /Game/Art/Ruins/M_RuinsSurface               Color x Tint, Normal, Roughness, Metallic, Emissive (x Color)
#   /Game/Art/Ruins/MI_Ruins<Slot>               one per slot of the meshes (Ashlar, Paving, Plaster, ...)
#   /Game/Art/Ruins/SM_Ruins_<letter>            one mesh per section, world positioned, no collision
# In the level: for every section that has a mesh, its plain boxes (the "A1 ..." StaticMeshActors in that section's
# folder) stay as the collision but are hidden, and the mesh is placed at the origin as "A1 Art <letter>". Run it again
# after build_area1_ruins.py (which brings the plain boxes back). With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\import_ruins_art.py -unattended -nop4 -nosplash -stdout
import glob
import os

import unreal

SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Models", "Ruins")
DIR = "/Game/Art/Ruins"
TEX_DIR = DIR + "/Textures"
LEVEL = "/Game/LV_Area1_Ruins"
SLOTS = ["Ashlar", "Paving", "Plaster", "Terracotta", "Wood", "Marble", "Rock", "Bronze", "Ember"]
LOOK = {   # roughness, metallic, emissive, tint
    "Ashlar": (0.85, 0.0, 0.0, (1.0, 1.0, 1.0)), "Paving": (0.8, 0.0, 0.0, (1.0, 1.0, 1.0)),
    "Plaster": (0.9, 0.0, 0.0, (1.0, 1.0, 1.0)), "Terracotta": (0.7, 0.0, 0.0, (1.0, 1.0, 1.0)),
    "Wood": (0.75, 0.0, 0.0, (1.0, 1.0, 1.0)), "Marble": (0.45, 0.0, 0.0, (1.0, 1.0, 1.0)),
    "Rock": (0.9, 0.0, 0.0, (1.0, 1.0, 1.0)), "Bronze": (0.4, 0.8, 0.0, (1.0, 1.0, 1.0)),
    "Ember": (1.0, 0.0, 6.0, (1.0, 1.0, 1.0)),
}

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
lines = []


def import_file(path, destination, options=None, name=None):
    task = unreal.AssetImportTask()
    task.filename = path
    task.destination_path = destination
    if name:
        task.destination_name = name
    task.automated = True
    task.save = True
    task.replace_existing = True
    if options:
        task.options = options
    tools.import_asset_tasks([task])
    return destination + "/" + (name or os.path.splitext(os.path.basename(path))[0])


# ----- textures -----
textures = {}
for path in sorted(glob.glob(os.path.join(SOURCE, "Textures", "T_Ruins*.png"))):
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

# ----- the surface material -----
path = DIR + "/M_RuinsSurface"
if not library.does_asset_exist(path):
    material = tools.create_asset("M_RuinsSurface", DIR, unreal.Material, unreal.MaterialFactoryNew())

    def node(kind, x, y):
        return editing.create_material_expression(material, kind, x, y)

    color = node(unreal.MaterialExpressionTextureSampleParameter2D, -900, -200)
    color.set_editor_property("parameter_name", "Color")
    color.set_editor_property("texture", textures["T_RuinsAshlar_C"])
    tint = node(unreal.MaterialExpressionVectorParameter, -900, 50)
    tint.set_editor_property("parameter_name", "Tint")
    tint.set_editor_property("default_value", unreal.LinearColor(1.0, 1.0, 1.0, 1.0))
    tinted = node(unreal.MaterialExpressionMultiply, -600, -150)
    normal = node(unreal.MaterialExpressionTextureSampleParameter2D, -900, 250)
    normal.set_editor_property("parameter_name", "Normal")
    normal.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    normal.set_editor_property("texture", textures["T_RuinsAshlar_N"])
    rough = node(unreal.MaterialExpressionScalarParameter, -600, 100)
    rough.set_editor_property("parameter_name", "Roughness")
    rough.set_editor_property("default_value", 0.85)
    metal = node(unreal.MaterialExpressionScalarParameter, -600, 180)
    metal.set_editor_property("parameter_name", "Metallic")
    glow = node(unreal.MaterialExpressionScalarParameter, -600, 400)
    glow.set_editor_property("parameter_name", "Emissive")
    glowing = node(unreal.MaterialExpressionMultiply, -350, 350)
    editing.connect_material_expressions(color, "RGB", tinted, "A")
    editing.connect_material_expressions(tint, "", tinted, "B")
    editing.connect_material_expressions(tinted, "", glowing, "A")
    editing.connect_material_expressions(glow, "", glowing, "B")
    editing.connect_material_property(tinted, "", unreal.MaterialProperty.MP_BASE_COLOR)
    editing.connect_material_property(normal, "RGB", unreal.MaterialProperty.MP_NORMAL)
    editing.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    editing.connect_material_property(metal, "", unreal.MaterialProperty.MP_METALLIC)
    editing.connect_material_property(glowing, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    editing.recompile_material(material)
    library.save_asset(path, False)
    lines.append("created " + path)
surface = unreal.load_asset(path)

instances = {}
for slot in SLOTS:
    mi_path = DIR + "/MI_Ruins" + slot
    if library.does_asset_exist(mi_path):
        mi = unreal.load_asset(mi_path)
    else:
        mi = tools.create_asset("MI_Ruins" + slot, DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        editing.set_material_instance_parent(mi, surface)
    roughness, metallic, emissive, tint = LOOK[slot]
    editing.set_material_instance_texture_parameter_value(mi, "Color", textures["T_Ruins" + slot + "_C"])
    if "T_Ruins" + slot + "_N" in textures:
        editing.set_material_instance_texture_parameter_value(mi, "Normal", textures["T_Ruins" + slot + "_N"])
    editing.set_material_instance_scalar_parameter_value(mi, "Roughness", roughness)
    editing.set_material_instance_scalar_parameter_value(mi, "Metallic", metallic)
    editing.set_material_instance_scalar_parameter_value(mi, "Emissive", emissive)
    editing.set_material_instance_vector_parameter_value(mi, "Tint", unreal.LinearColor(tint[0], tint[1], tint[2], 1.0))
    library.save_asset(mi_path, False)
    instances["M_Ruins" + slot] = mi

# ----- heaven's debris: area 1's moving pieces (2026-11-16, the user's choice: they read as fallen from heaven) -----
# Weathered white marble, a gold band round each face that glows (Mask x GoldColor x Glow), and Fade with a dithered
# mask like M_FadingFlatCol's, so BP_TimedPlatform's fading still works.
path = DIR + "/M_HeavenDebris"
if not library.does_asset_exist(path):
    material = tools.create_asset("M_HeavenDebris", DIR, unreal.Material, unreal.MaterialFactoryNew())
    material.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)

    def dnode(kind, x, y):
        return editing.create_material_expression(material, kind, x, y)

    color = dnode(unreal.MaterialExpressionTextureSampleParameter2D, -900, -250)
    color.set_editor_property("parameter_name", "Color")
    color.set_editor_property("texture", textures["T_RuinsDebris_C"])
    normal = dnode(unreal.MaterialExpressionTextureSampleParameter2D, -900, 0)
    normal.set_editor_property("parameter_name", "Normal")
    normal.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    normal.set_editor_property("texture", textures["T_RuinsDebris_N"])
    mask = dnode(unreal.MaterialExpressionTextureSampleParameter2D, -900, 250)
    mask.set_editor_property("parameter_name", "Mask")
    mask.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
    mask.set_editor_property("texture", textures["T_RuinsDebris_E"])
    gold = dnode(unreal.MaterialExpressionVectorParameter, -650, 350)
    gold.set_editor_property("parameter_name", "GoldColor")
    gold.set_editor_property("default_value", unreal.LinearColor(1.0, 0.75, 0.35, 1.0))
    glow = dnode(unreal.MaterialExpressionScalarParameter, -650, 500)
    glow.set_editor_property("parameter_name", "Glow")
    glow.set_editor_property("default_value", 2.0)
    m1 = dnode(unreal.MaterialExpressionMultiply, -450, 300)
    m2 = dnode(unreal.MaterialExpressionMultiply, -300, 350)
    rough = dnode(unreal.MaterialExpressionScalarParameter, -450, 100)
    rough.set_editor_property("parameter_name", "Roughness")
    rough.set_editor_property("default_value", 0.5)
    fade = dnode(unreal.MaterialExpressionScalarParameter, -650, 650)
    fade.set_editor_property("parameter_name", "Fade")
    fade.set_editor_property("default_value", 1.0)
    dither = dnode(unreal.MaterialExpressionMaterialFunctionCall, -400, 650)
    dither.set_editor_property("material_function", unreal.load_asset("/Engine/Functions/Engine_MaterialFunctions02/Utility/DitherTemporalAA"))
    editing.connect_material_expressions(mask, "R", m1, "A")
    editing.connect_material_expressions(gold, "", m1, "B")
    editing.connect_material_expressions(m1, "", m2, "A")
    editing.connect_material_expressions(glow, "", m2, "B")
    editing.connect_material_expressions(fade, "", dither, "Alpha Threshold")
    editing.connect_material_property(color, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    editing.connect_material_property(normal, "RGB", unreal.MaterialProperty.MP_NORMAL)
    editing.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    editing.connect_material_property(m2, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    editing.connect_material_property(dither, "", unreal.MaterialProperty.MP_OPACITY_MASK)
    editing.recompile_material(material)
    library.save_asset(path, False)
    lines.append("created " + path)
debris_parent = unreal.load_asset(path)
debris = {}
for name, glow_value in (("MI_HeavenDebris", 2.0), ("MI_HeavenDebrisBright", 8.0)):
    mi_path = DIR + "/" + name
    if library.does_asset_exist(mi_path):
        mi = unreal.load_asset(mi_path)
    else:
        mi = tools.create_asset(name, DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        editing.set_material_instance_parent(mi, debris_parent)
    editing.set_material_instance_scalar_parameter_value(mi, "Glow", glow_value)
    library.save_asset(mi_path, False)
    debris[name] = mi
DEBRIS_CLASSES = ("BP_MovingPlatform_C", "BP_FallingFloor_C", "BP_TimedPlatform_C", "BP_Mechanism_C", "BP_Lever_C")   # (levers and plates too, 2026-11-16)

# ----- the meshes -----
meshes = {}
for path in sorted(glob.glob(os.path.join(SOURCE, "SM_Ruins_*.fbx"))):
    options = unreal.FbxImportUI()
    options.set_editor_property("import_materials", False)
    options.set_editor_property("import_textures", False)
    data = options.get_editor_property("static_mesh_import_data")
    data.set_editor_property("auto_generate_collision", False)
    data.set_editor_property("combine_meshes", True)
    data.set_editor_property("generate_lightmap_u_vs", False)
    asset_path = import_file(path, DIR, options)
    mesh = unreal.load_asset(asset_path)
    for i, static_material in enumerate(mesh.get_editor_property("static_materials")):
        name = str(static_material.get_editor_property("material_slot_name"))
        if name in instances:
            mesh.set_material(i, instances[name])
    library.save_asset(asset_path, False)
    letter = asset_path.rsplit("_", 1)[1]
    meshes[letter] = mesh
    lines.append("imported {} bounds {}".format(asset_path, mesh.get_bounds()))

# ----- the level -----
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not level.load_level(LEVEL):
    raise RuntimeError("Could not open " + LEVEL)
for actor in actors.get_all_level_actors():
    if actor.get_actor_label().startswith("A1 Art "):
        actors.destroy_actor(actor)
for letter, mesh in meshes.items():
    low = [1e9, 1e9, 1e9]
    high = [-1e9, -1e9, -1e9]
    hidden = 0
    for actor in actors.get_all_level_actors():
        folder = str(actor.get_folder_path())
        if not actor.get_actor_label().startswith("A1 ") or not isinstance(actor, unreal.StaticMeshActor):
            continue
        if not folder.startswith("Area1/" + letter + " "):
            continue
        origin, extent = actor.get_actor_bounds(False)
        for k, (o, e) in enumerate(((origin.x, extent.x), (origin.y, extent.y), (origin.z, extent.z))):
            low[k], high[k] = min(low[k], o - e), max(high[k], o + e)
        component = actor.get_editor_property("static_mesh_component")
        component.set_editor_property("visible", False)
        actor.set_actor_hidden_in_game(True)
        hidden += 1
    art = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator(0.0, 0.0, 0.0))
    art.set_actor_label("A1 Art " + letter)
    art.set_folder_path("Area1/Art")
    component = art.get_editor_property("static_mesh_component")
    component.set_static_mesh(mesh)
    component.set_collision_profile_name("NoCollision")
    a_origin, a_extent = art.get_actor_bounds(False)
    lines.append("section {}: {} boxes hidden; boxes x {:.0f}..{:.0f} y {:.0f}..{:.0f} z {:.0f}..{:.0f}".format(letter, hidden, low[0], high[0], low[1], high[1], low[2], high[2]))
    lines.append("           art   x {:.0f}..{:.0f} y {:.0f}..{:.0f} z {:.0f}..{:.0f}".format(
        a_origin.x - a_extent.x, a_origin.x + a_extent.x, a_origin.y - a_extent.y, a_origin.y + a_extent.y,
        a_origin.z - a_extent.z, a_origin.z + a_extent.z))
# Heaven's debris on the moving pieces; the giant steps (the big mechanism) glow brighter.
dressed = 0
for actor in actors.get_all_level_actors():
    if not actor.get_actor_label().startswith("A1 ") or actor.get_class().get_name() not in DEBRIS_CLASSES:
        continue
    look = debris["MI_HeavenDebrisBright" if "Giant Step" in actor.get_actor_label() else "MI_HeavenDebris"]
    for component in actor.get_components_by_class(unreal.StaticMeshComponent):
        if component.get_editor_property("static_mesh") is None:
            continue
        for i in range(component.get_num_materials()):
            component.set_material(i, look)
    dressed += 1
lines.append("{} moving pieces dressed as heaven's debris".format(dressed))
lines.append("{} saved {}".format(LEVEL, level.save_current_level()))
# Check it stuck: open the level again and read one back.
level.load_level(LEVEL)
for actor in actors.get_all_level_actors():
    if actor.get_actor_label().startswith("A1 ") and actor.get_class().get_name() in DEBRIS_CLASSES:
        component = actor.get_components_by_class(unreal.StaticMeshComponent)[0]
        lines.append("after reload {}: {}".format(actor.get_actor_label(), component.get_material(0).get_name() if component.get_material(0) else None))
        break

with open(os.path.join(unreal.Paths.project_saved_dir(), "ruins_art.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
