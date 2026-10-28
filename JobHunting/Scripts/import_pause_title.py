import os

import unreal


UI_DIR = "/Game/UI"
# PNGs drawn by make_pause_title.ps1 and make_pause_labels.ps1.
TEXTURE_NAMES = ["T_PauseTitle", "T_Label_Volume", "T_Label_SE", "T_Label_Quit", "T_Arrow"]
ART_DIR = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()), "Scripts", "Art")


def import_ui_texture(name):
    source_png = os.path.join(ART_DIR, name + ".png")
    if not os.path.exists(source_png):
        raise RuntimeError("{} not found; run make_pause_title.ps1 / make_pause_labels.ps1 first".format(source_png))

    # Re-importing replaces the pixels only, so redrawing the PNG and running this again is safe.
    task = unreal.AssetImportTask()
    task.filename = source_png
    task.destination_path = UI_DIR
    task.destination_name = name
    task.automated = True
    task.replace_existing = True
    task.save = False
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

    texture_path = "{}/{}".format(UI_DIR, name)
    texture = unreal.EditorAssetLibrary.load_asset(texture_path)
    if not isinstance(texture, unreal.Texture2D):
        raise RuntimeError("Could not import {}".format(source_png))

    # UI settings: crisp, uncompressed alpha edges, no mip blur.
    texture.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_UI)
    texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_EDITOR_ICON)
    texture.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    texture.set_editor_property("never_stream", True)
    unreal.EditorAssetLibrary.save_asset(texture_path, False)


for texture_name in TEXTURE_NAMES:
    import_ui_texture(texture_name)
    unreal.log("{}/{} imported for the pause menu".format(UI_DIR, texture_name))
