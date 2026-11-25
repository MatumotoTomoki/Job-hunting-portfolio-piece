# Achievements step 5b (2026-11-21): imports Scripts/Art/T_Label_Achievements.png (make_pause_labels.ps1 -Only
# T_Label_Achievements) next to the team's other pause labels in /Game/UI/画像, with the same UI texture settings as
# import_pause_title.py. Safe to run again. From the Output Log:
#   exec(open(r"<full path>\import_pause_achievement_label.py", encoding="utf-8").read())
import os

import unreal

FOLDER = "/Game/UI/画像"
# Any other label too (11-25: タイトルに戻る): set LABEL first, e.g.
#   LABEL='T_Label_Title'; exec(open(r"<full path>\import_pause_achievement_label.py", encoding="utf-8").read())
NAME = globals().get("LABEL", "T_Label_Achievements")
SOURCE = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()), "Scripts", "Art", NAME + ".png")

if not os.path.exists(SOURCE):
    raise RuntimeError(SOURCE + " not found; run make_pause_labels.ps1 -Only T_Label_Achievements first")
task = unreal.AssetImportTask()
task.filename = SOURCE
task.destination_path = FOLDER
task.destination_name = NAME
task.automated = True
task.replace_existing = True
task.save = False
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

path = FOLDER + "/" + NAME
texture = unreal.EditorAssetLibrary.load_asset(path)
if not isinstance(texture, unreal.Texture2D):
    raise RuntimeError("Could not import " + SOURCE)
texture.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_UI)
texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_EDITOR_ICON)
texture.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
texture.set_editor_property("never_stream", True)
unreal.EditorAssetLibrary.save_asset(path, False)
unreal.log(path + " imported for the pause menu")
