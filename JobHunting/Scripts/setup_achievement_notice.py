# Achievements, step 2: the corner notice and its sound (Achievements_Plan.md).
#   Achievements/S_AchievementGet   the "kirin!" (SourceArt/Sounds/S_AchievementGet.wav from make_achievement_sound.ps1)
#   BP_MyGameInstance AchievementQueue (Text[])   names waiting to be shown; UnlockAchievement adds to it
#   /Game/UI/WBP_AchievementNotice  the notice, placed in the HUD (WBP_Height) by hand at the top right. Variables:
#       Showing (bool), Age (real: seconds shown), NoticeSound (SoundBase, S_AchievementGet). Its designer part
#       (a TextBlock named NoticeText, Is Variable on) is made by hand; its graph is WBP_AchievementNotice_EventGraph.txt
#       from Generators/gen_achievements.ps1.
# Safe to run again. Editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_achievement_notice.py -unattended -nop4 -nosplash -stdout
import os

import unreal

FOLDER = "/Game/ThirdPerson/Blueprints/Achievements"
GAME_INSTANCE = "/Game/ThirdPerson/Blueprints/BP_MyGameInstance"
WIDGET = "/Game/UI/WBP_AchievementNotice"
SOUND_FILE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Sounds", "S_AchievementGet.wav")

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
pins = unreal.BlueprintEditorLibrary
lines = []


def add_variables(bp, path, variables):
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
    return unreal.get_default_object(bp.generated_class())


# ----- the sound -----
task = unreal.AssetImportTask()
task.filename = SOUND_FILE
task.destination_path = FOLDER
task.destination_name = "S_AchievementGet"
task.automated = True
task.save = True
task.replace_existing = True
tools.import_asset_tasks([task])
sound = unreal.load_asset(FOLDER + "/S_AchievementGet")
if sound is None:
    raise RuntimeError("S_AchievementGet did not import from " + SOUND_FILE)
lines.append("imported S_AchievementGet ({} s)".format(sound.get_editor_property("duration")))

# ----- the game instance's queue -----
gi_bp = unreal.load_asset(GAME_INSTANCE)
add_variables(gi_bp, GAME_INSTANCE, [("AchievementQueue", pins.get_array_type(pins.get_basic_type_by_name("text")))])
library.save_asset(GAME_INSTANCE, False)

# ----- the notice widget -----
if library.does_asset_exist(WIDGET):
    widget = unreal.load_asset(WIDGET)
else:
    factory = unreal.WidgetBlueprintFactory()
    factory.set_editor_property("parent_class", unreal.UserWidget)
    widget = tools.create_asset("WBP_AchievementNotice", "/Game/UI", unreal.WidgetBlueprint, factory)
    lines.append("created " + WIDGET)
defaults = add_variables(widget, WIDGET, [
    ("Showing", pins.get_basic_type_by_name("bool")), ("Age", pins.get_basic_type_by_name("real")),
    ("NoticeSound", pins.get_object_reference_type(unreal.SoundBase.static_class())),
])
if defaults.get_editor_property("NoticeSound") is None:
    defaults.set_editor_property("NoticeSound", sound)
pins.compile_blueprint(widget)
library.save_asset(WIDGET, False)
lines.append("NoticeSound = {}".format(unreal.get_default_object(unreal.load_asset(WIDGET).generated_class()).get_editor_property("NoticeSound")))

with open(os.path.join(unreal.Paths.project_saved_dir(), "setup_achievement_notice.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
