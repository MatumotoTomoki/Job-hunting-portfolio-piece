# Brings in area 4's "palace of heaven" art from build_heaven_art_blender.py and puts it in LV_Area4_Heaven:
#   /Game/Art/Heaven/Textures/T_HeavenArt*_C / _N / _E   colour, normal and glow-mask maps
#   /Game/Art/Heaven/MI_HeavenArt<Slot>                 Pearl Gold Channel Stone Crystal Dark, children of area 2's
#                                                       /Game/Art/Tower/M_TowerSurface (Color x vertex colour, Normal,
#                                                       Roughness, Metallic, Emissive = Mask x GlowColor x Glow)
#   /Game/Art/Heaven/SM_Heaven_<number>                 one mesh per section, world positioned, no collision
# In the level: for every section with a mesh, the "A4 ..." StaticMeshActors in that section's folder named in
# heaven_art_<number>.json (Island, Thread Ledge, ...) stay as the collision but are hidden, and the mesh is placed at
# the origin as "A4 Art <number>". Gimmicks (BP actors) are left as they are. Run it again after build_area4_heaven.py
# (which removes everything labelled "A4 "). With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\import_heaven_art.py -unattended -nop4 -nosplash -stdout
import glob
import json
import os

import unreal

SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Models", "Heaven", "Art")
DIR = "/Game/Art/Heaven"
TEX_DIR = DIR + "/Textures"
PARENT = "/Game/Art/Tower/M_TowerSurface"
LEVEL = "/Game/LV_Area4_Heaven"
SLOTS = ["Pearl", "Gold", "Channel", "Stone", "Crystal", "Dark", "DarkBand"]
WARM = (1.0, 0.85, 0.55)
LOOK = {   # roughness, metallic, glow, glow colour - the channels and veins only faintly lit: heaven has lost its light
    "Pearl": (0.3, 0.0, 0.0, WARM), "Gold": (0.25, 1.0, 0.0, WARM), "Channel": (0.3, 0.0, 1.5, WARM),
    "Stone": (0.75, 0.0, 0.8, WARM), "Crystal": (0.1, 0.0, 4.0, WARM), "Dark": (0.7, 0.0, 0.0, WARM),
    "DarkBand": (0.5, 0.0, 0.4, WARM),      # the dark tower's meander: its light all but gone
}

unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")   # keep vertex colours
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


textures = {}
for path in sorted(glob.glob(os.path.join(SOURCE, "Textures", "T_HeavenArt*.png"))):
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

parent = unreal.load_asset(PARENT)
if not parent:
    raise RuntimeError("Missing " + PARENT + " (made by import_tower_art.py)")
instances = {}
for slot in SLOTS:
    mi_path = DIR + "/MI_HeavenArt" + slot
    if library.does_asset_exist(mi_path):
        mi = unreal.load_asset(mi_path)
    else:
        mi = tools.create_asset("MI_HeavenArt" + slot, DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    editing.set_material_instance_parent(mi, parent)
    roughness, metallic, glow_value, glow_color = LOOK[slot]
    editing.set_material_instance_texture_parameter_value(mi, "Color", textures["T_HeavenArt" + slot + "_C"])
    if "T_HeavenArt" + slot + "_N" in textures:
        editing.set_material_instance_texture_parameter_value(mi, "Normal", textures["T_HeavenArt" + slot + "_N"])
    editing.set_material_instance_texture_parameter_value(mi, "Mask", textures.get("T_HeavenArt" + slot + "_E", textures["T_HeavenArtBlack_E"]))
    editing.set_material_instance_scalar_parameter_value(mi, "Roughness", roughness)
    editing.set_material_instance_scalar_parameter_value(mi, "Metallic", metallic)
    editing.set_material_instance_scalar_parameter_value(mi, "Glow", glow_value)
    editing.set_material_instance_vector_parameter_value(mi, "GlowColor", unreal.LinearColor(glow_color[0], glow_color[1], glow_color[2], 1.0))
    library.save_asset(mi_path, False)
    instances["M_HeavenArt" + slot] = mi


def import_mesh(path, destination, materials):
    options = unreal.FbxImportUI()
    options.set_editor_property("import_materials", False)
    options.set_editor_property("import_textures", False)
    data = options.get_editor_property("static_mesh_import_data")
    data.set_editor_property("auto_generate_collision", False)
    data.set_editor_property("combine_meshes", True)
    data.set_editor_property("generate_lightmap_u_vs", False)
    data.set_editor_property("vertex_color_import_option", unreal.VertexColorImportOption.REPLACE)
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
for path in sorted(glob.glob(os.path.join(SOURCE, "SM_Heaven_*.fbx"))):
    number = os.path.splitext(os.path.basename(path))[0].rsplit("_", 1)[1]
    asset_path, mesh = import_mesh(path, DIR, instances)
    replaces = json.load(open(os.path.join(SOURCE, "heaven_art_" + number + ".json"), encoding="utf-8"))["replaces"]
    meshes[number] = (mesh, replaces)
    lines.append("imported {} (replaces {})".format(asset_path, ", ".join(replaces)))

level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not level.load_level(LEVEL):
    raise RuntimeError("Could not open " + LEVEL)
for actor in actors.get_all_level_actors():
    if actor.get_actor_label().startswith("A4 Art "):
        actors.destroy_actor(actor)
for number, (mesh, replaces) in sorted(meshes.items()):
    hidden = 0
    for actor in actors.get_all_level_actors():
        label = actor.get_actor_label()
        if not label.startswith("A4 ") or not isinstance(actor, unreal.StaticMeshActor):
            continue
        if not str(actor.get_folder_path()).startswith("Area4/" + number + " "):
            continue
        if len(label.split(" ", 2)) < 3 or label.split(" ", 2)[2] not in replaces:     # "A4 012 Thread Ledge"
            continue
        actor.get_editor_property("static_mesh_component").set_editor_property("visible", False)
        actor.set_actor_hidden_in_game(True)
        hidden += 1
    art = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator(0.0, 0.0, 0.0))
    art.set_actor_label("A4 Art " + number)
    art.set_folder_path("Area4/Art")
    component = art.get_editor_property("static_mesh_component")
    component.set_static_mesh(mesh)
    component.set_collision_profile_name("NoCollision")
    lines.append("section {}: {} actors hidden".format(number, hidden))
lines.append("{} saved {}".format(LEVEL, level.save_current_level()))

with open(os.path.join(unreal.Paths.project_saved_dir(), "heaven_art.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
