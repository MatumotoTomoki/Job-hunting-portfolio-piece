# Achievements step 5: the list screen, an icon grid (the user's layout, 2026-11-21: 8 columns of icons on the left,
# the chosen one's icon, name and condition large on the right).
#   /Game/UI/Achievements/T_AchIcon_*   the icons from SourceArt/UI/Achievements (make_achievement_icons.ps1: one per
#       kind + Unknown; an achievement's own T_AchIcon_<ID>.png, if there is one, is imported too and used instead)
#   BP_MyGameInstance  AchievementIcons (Texture2D[], one per achievement, in the list's order: its own picture or its
#       kind's), UnknownAchievementIcon (Texture2D: a hidden one not yet taken)
#   /Game/UI/WBP_AchievementSlot  one grid cell: Index (int: which achievement), Owner (the list). Designer by hand:
#       SlotButton (Button) holding IconImage (Image), both Is Variable.
#   /Game/UI/WBP_AchievementList  Row (int), FirstSlot (the first cell, focused on opening). Designer by hand: HeaderText,
#       Grid (Uniform Grid Panel), DetailIcon (Image), DetailName, DetailCondition, DetailKind (TextBlocks), BackButton.
# Graphs: Generators/gen_achievement_list.ps1. Safe to run again (new icons: run it again). Editor closed, or from the
# Output Log: exec(open(r"<full path>\setup_achievement_list.py", encoding="utf-8").read())
import glob
import os

import unreal

UI = "/Game/UI"
ICONS = UI + "/Achievements"
LIST = UI + "/WBP_AchievementList"
SLOT = UI + "/WBP_AchievementSlot"
GAME_INSTANCE = "/Game/ThirdPerson/Blueprints/BP_MyGameInstance"
SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "UI", "Achievements")
KIND_ICON = {"進行": "Progress", "収集": "Collect", "失敗": "Fail", "腕前": "Skill", "隠し": "Hidden"}

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
pins = unreal.BlueprintEditorLibrary
lines = []

# ----- the icons -----
tasks = []
for path in sorted(glob.glob(os.path.join(SOURCE, "T_AchIcon_*.png"))):
    task = unreal.AssetImportTask()
    task.filename = path
    task.destination_path = ICONS
    task.automated = True
    task.save = True
    task.replace_existing = True
    tasks.append(task)
tools.import_asset_tasks(tasks)
icons = {}
for task in tasks:
    name = os.path.splitext(os.path.basename(task.filename))[0]
    texture = unreal.load_asset(ICONS + "/" + name)
    if texture is None:
        raise RuntimeError("Did not import " + task.filename)
    texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_EDITOR_ICON)
    texture.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_UI)
    texture.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    library.save_asset(ICONS + "/" + name, False)
    icons[name[len("T_AchIcon_"):]] = texture
lines.append("icons: " + ", ".join(sorted(icons)))


def add_variables(bp, path, variables):
    # add_member_variable would quietly add Name_0 next to an existing one, so check the CDO first.
    defaults = unreal.get_default_object(bp.generated_class())
    for name, pin_type in variables:
        try:
            defaults.get_editor_property(name)
            continue
        except Exception:
            pass
        if not pins.add_member_variable(bp, name, pin_type):
            raise RuntimeError("Could not add {} to {}".format(name, path))
        lines.append("{}: variable {}".format(path.rsplit("/", 1)[1], name))
    pins.compile_blueprint(bp)
    library.save_asset(path, False)
    return unreal.get_default_object(bp.generated_class())


def widget(path):
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    factory = unreal.WidgetBlueprintFactory()
    factory.set_editor_property("parent_class", unreal.UserWidget)
    folder, name = path.rsplit("/", 1)
    lines.append("created " + path)
    return tools.create_asset(name, folder, unreal.WidgetBlueprint, factory)


# ----- the game instance: each achievement's icon -----
TEXTURE = pins.get_object_reference_type(unreal.Texture2D.static_class())
gi_bp = unreal.load_asset(GAME_INSTANCE)
gi = add_variables(gi_bp, GAME_INSTANCE, [("AchievementIcons", pins.get_array_type(TEXTURE)), ("UnknownAchievementIcon", TEXTURE)])
ids = [str(i) for i in gi.get_editor_property("AchievementIds")]
kinds = [str(k) for k in gi.get_editor_property("AchievementKinds")]
chosen = [icons.get(i) or icons[KIND_ICON[k]] for i, k in zip(ids, kinds)]
gi.set_editor_property("AchievementIcons", chosen)
gi.set_editor_property("UnknownAchievementIcon", icons["Unknown"])
library.save_asset(GAME_INSTANCE, False)
own = [i for i in ids if i in icons]
lines.append("AchievementIcons: {} ({} with their own picture{})".format(len(chosen), len(own), ": " + ", ".join(own) if own else ""))

# ----- the two widgets -----
list_bp = widget(LIST)
slot_bp = widget(SLOT)
INT = pins.get_basic_type_by_name("int")
add_variables(slot_bp, SLOT, [("Index", INT), ("Owner", pins.get_object_reference_type(list_bp.generated_class()))])
# RestoreGameInput: set by the pause menu (BP_ThirdPersonPlayerController), which hands the keys to the list; 戻る then
# gives them back (Set Input Mode Game Only). From the title it stays false.
add_variables(list_bp, LIST, [("Row", INT), ("FirstSlot", pins.get_object_reference_type(slot_bp.generated_class())),
                              ("RestoreGameInput", pins.get_basic_type_by_name("bool"))])

with open(os.path.join(unreal.Paths.project_saved_dir(), "setup_achievement_list.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(lines) + "\n")
unreal.log("\n".join(lines))
