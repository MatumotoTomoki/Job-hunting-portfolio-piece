import os

import unreal


UI_DIR = "/Game/UI"
TEXTURE_NAME = "T_PauseTitle"
TEXTURE_PATH = "{}/{}".format(UI_DIR, TEXTURE_NAME)
SOURCE_PNG = os.path.join(
    unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()), "Scripts", "Art", TEXTURE_NAME + ".png"
)


def import_title_texture():
    if not os.path.exists(SOURCE_PNG):
        raise RuntimeError("{} not found; run make_pause_title.ps1 first".format(SOURCE_PNG))

    # Re-importing replaces the pixels only, so redrawing the PNG and running this again is safe.
    task = unreal.AssetImportTask()
    task.filename = SOURCE_PNG
    task.destination_path = UI_DIR
    task.destination_name = TEXTURE_NAME
    task.automated = True
    task.replace_existing = True
    task.save = False
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

    texture = unreal.EditorAssetLibrary.load_asset(TEXTURE_PATH)
    if not isinstance(texture, unreal.Texture2D):
        raise RuntimeError("Could not import {}".format(SOURCE_PNG))

    # UI settings: crisp, uncompressed alpha edges, no mip blur.
    texture.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_UI)
    texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_EDITOR_ICON)
    texture.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    texture.set_editor_property("never_stream", True)
    unreal.EditorAssetLibrary.save_asset(TEXTURE_PATH, False)
    return texture


import_title_texture()
unreal.log("{} imported for the pause menu title".format(TEXTURE_PATH))
