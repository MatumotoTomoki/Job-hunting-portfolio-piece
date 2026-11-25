# Pause menu リセット (the user, 2026-11-25): the stage starts over as it was entered - its coins, items, flags,
# the achievements taken since entering it, and the item effects (as they were on entering). BP_MyGameInstance keeps a
# snapshot taken when a stage (LV_Area*, LV_Secret*) is entered (not again on a hell return or a reset: same level):
#   SnapshotLevel (Name), StageCoinIds (String), StageItems, StageFlags, StageAchievements (Name[]), StageFreeCount (int),
#   StageHasStats (bool), StageWalkSpeed, StageJumpZ (real), StageJumpCount (int),
#   StageRunFell, StageRunUsedFlag, StageRunTookItem (bool)
# Graphs (Generators/gen_stage_reset.ps1): GI_StageReset.txt (custom events SnapshotStage and ResetStage, pasted into
# BP_MyGameInstance's EventGraph), AreaStart_Snapshot.txt (BP_AreaStart Begin Play calls SnapshotStage).
# Safe to run again. Editor closed (it changes the game instance), as a commandlet:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_stage_reset.py -unattended -nop4 -nosplash -stdout
import os

import unreal

GAME_INSTANCE = "/Game/ThirdPerson/Blueprints/BP_MyGameInstance"
pins = unreal.BlueprintEditorLibrary
NAME = pins.get_basic_type_by_name("name")
TYPES = {"name": NAME, "names": pins.get_array_type(NAME), "string": pins.get_basic_type_by_name("string"),
         "int": pins.get_basic_type_by_name("int"), "bool": pins.get_basic_type_by_name("bool"),
         "real": pins.get_basic_type_by_name("real")}
VARIABLES = [("SnapshotLevel", "name"), ("StageCoinIds", "string"), ("StageItems", "names"), ("StageFlags", "names"),
             ("StageAchievements", "names"), ("StageFreeCount", "int"), ("StageHasStats", "bool"),
             ("StageWalkSpeed", "real"), ("StageJumpZ", "real"), ("StageJumpCount", "int"),
             ("StageRunFell", "bool"), ("StageRunUsedFlag", "bool"), ("StageRunTookItem", "bool")]

bp = unreal.load_asset(GAME_INSTANCE)
defaults = unreal.get_default_object(bp.generated_class())
added = []
for name, kind in VARIABLES:
    try:
        defaults.get_editor_property(name)     # add_member_variable would add Name_0 next to an existing one
        continue
    except Exception:
        pass
    if not pins.add_member_variable(bp, name, TYPES[kind]):
        raise RuntimeError("Could not add " + name)
    added.append(name)
pins.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_asset(GAME_INSTANCE, False)
line = "BP_MyGameInstance: " + (("added " + ", ".join(added)) if added else "all stage reset variables already there")
with open(os.path.join(unreal.Paths.project_saved_dir(), "stage_reset.txt"), "w", encoding="utf-8") as out:
    out.write(line + "\n")
unreal.log(line)
