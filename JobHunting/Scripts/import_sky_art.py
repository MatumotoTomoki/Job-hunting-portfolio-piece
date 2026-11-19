# Brings in area 3's "garden ruins" art from build_sky_art_blender.py and puts it in LV_Area3_Sky:
#   /Game/Art/Sky/Textures/T_SkyArt*_C / _N / _E   colour, normal and glow-mask maps
#   /Game/Art/Sky/MI_SkyArt<Slot>                 one per slot (Grass Rock Marble Gold Leaf Bark Blossom Water), children
#                                                 of area 2's /Game/Art/Tower/M_TowerSurface (Color x Tint x vertex
#                                                 colour, Normal, Roughness, Metallic, Emissive = Mask x GlowColor x Glow)
#   /Game/Art/Sky/SM_Sky_<letter>                 one mesh per section, world positioned, no collision
# In the level: for every section with a mesh, the "A3 ..." StaticMeshActors in that section's folder whose kind the
# mesh replaces (sky_art_<letter>.json: Island, Old Gate, ...) stay as the collision but are hidden, and the mesh is
# placed at the origin as "A3 Art <letter>". Gimmicks (BP actors) and the clouds are left as they are.
# Run it again after build_area3_sky.py (which removes everything labelled "A3 "). With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\import_sky_art.py -unattended -nop4 -nosplash -stdout
import glob
import json
import os

import unreal

SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Models", "Sky", "Art")
DIR = "/Game/Art/Sky"
TEX_DIR = DIR + "/Textures"
PARENT = "/Game/Art/Tower/M_TowerSurface"
LEVEL = "/Game/LV_Area3_Sky"
SLOTS = ["Grass", "Rock", "Marble", "Gold", "Leaf", "Bark", "Blossom", "Water"]
LOOK = {   # roughness, metallic, glow, glow colour
    "Grass": (0.95, 0.0, 0.0, (1.0, 1.0, 1.0)), "Rock": (0.9, 0.0, 0.0, (1.0, 1.0, 1.0)),
    "Marble": (0.35, 0.0, 0.0, (1.0, 1.0, 1.0)), "Gold": (0.25, 1.0, 0.0, (1.0, 1.0, 1.0)),
    "Leaf": (0.8, 0.0, 0.0, (1.0, 1.0, 1.0)), "Bark": (0.9, 0.0, 0.0, (1.0, 1.0, 1.0)),
    "Blossom": (0.7, 0.0, 0.0, (1.0, 1.0, 1.0)), "Water": (0.1, 0.0, 0.6, (0.7, 0.9, 1.0)),
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


# ----- textures and material instances -----
textures = {}
for path in sorted(glob.glob(os.path.join(SOURCE, "Textures", "T_SkyArt*.png"))):
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
    mi_path = DIR + "/MI_SkyArt" + slot
    if library.does_asset_exist(mi_path):
        mi = unreal.load_asset(mi_path)
    else:
        mi = tools.create_asset("MI_SkyArt" + slot, DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    editing.set_material_instance_parent(mi, parent)
    roughness, metallic, glow_value, glow_color = LOOK[slot]
    editing.set_material_instance_texture_parameter_value(mi, "Color", textures["T_SkyArt" + slot + "_C"])
    if "T_SkyArt" + slot + "_N" in textures:
        editing.set_material_instance_texture_parameter_value(mi, "Normal", textures["T_SkyArt" + slot + "_N"])
    editing.set_material_instance_texture_parameter_value(mi, "Mask", textures.get("T_SkyArt" + slot + "_E", textures["T_SkyArtBlack_E"]))
    editing.set_material_instance_scalar_parameter_value(mi, "Roughness", roughness)
    editing.set_material_instance_scalar_parameter_value(mi, "Metallic", metallic)
    editing.set_material_instance_scalar_parameter_value(mi, "Glow", glow_value)
    editing.set_material_instance_vector_parameter_value(mi, "GlowColor", unreal.LinearColor(glow_color[0], glow_color[1], glow_color[2], 1.0))
    library.save_asset(mi_path, False)
    instances["M_SkyArt" + slot] = mi


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
    old = destination + "/" + os.path.splitext(os.path.basename(path))[0]
    if library.does_asset_exist(old):
        library.delete_asset(old)      # a re-import would keep the old import settings (vertex colours ignored)
    asset_path = import_file(path, destination, options)
    mesh = unreal.load_asset(asset_path)
    for i, static_material in enumerate(mesh.get_editor_property("static_materials")):
        name = str(static_material.get_editor_property("material_slot_name"))
        if name in materials:
            mesh.set_material(i, materials[name])
    library.save_asset(asset_path, False)
    return asset_path, mesh


meshes = {}
for path in sorted(glob.glob(os.path.join(SOURCE, "SM_Sky_*.fbx"))):
    letter = os.path.splitext(os.path.basename(path))[0].rsplit("_", 1)[1]
    asset_path, mesh = import_mesh(path, DIR, instances)
    replaces = json.load(open(os.path.join(SOURCE, "sky_art_" + letter + ".json"), encoding="utf-8"))["replaces"]
    meshes[letter] = (mesh, replaces)
    lines.append("imported {} bounds {} (replaces {})".format(asset_path, mesh.get_bounds(), ", ".join(replaces)))

# ----- the level -----
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not level.load_level(LEVEL):
    raise RuntimeError("Could not open " + LEVEL)
for actor in actors.get_all_level_actors():
    if actor.get_actor_label().startswith("A3 Art "):
        actors.destroy_actor(actor)
for letter, (mesh, replaces) in sorted(meshes.items()):
    hidden = 0
    for actor in actors.get_all_level_actors():
        label = actor.get_actor_label()
        if not label.startswith("A3 ") or not isinstance(actor, unreal.StaticMeshActor):
            continue
        if not str(actor.get_folder_path()).startswith("Area3/" + letter + " "):
            continue
        if label.split(" ", 2)[2] not in replaces:          # "A3 012 Island" -> "Island"
            continue
        actor.get_editor_property("static_mesh_component").set_editor_property("visible", False)
        actor.set_actor_hidden_in_game(True)
        hidden += 1
    art = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator(0.0, 0.0, 0.0))
    art.set_actor_label("A3 Art " + letter)
    art.set_folder_path("Area3/Art")
    component = art.get_editor_property("static_mesh_component")
    component.set_static_mesh(mesh)
    component.set_collision_profile_name("NoCollision")
    lines.append("section {}: {} actors hidden".format(letter, hidden))
lines.append("{} saved {}".format(LEVEL, level.save_current_level()))

with open(os.path.join(unreal.Paths.project_saved_dir(), "sky_art.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
