# Achievements, step 1: the foundation (Achievements_Plan.md, 2026-11-20).
#   /Game/ThirdPerson/Blueprints/Achievements/BP_AchievementSave   a SaveGame of its own (slot "Achievements"; the team's
#       BP_HeightSave is left alone): Unlocked (array of Name), FreeCount (int)
#   BP_MyGameInstance:
#     the list, one entry per achievement, in the order the list screen shows them (defaults set here, from ACHIEVEMENTS):
#       AchievementIds (Name[]), AchievementNames (Text[]), AchievementDescriptions (Text[]), AchievementKinds (String[]),
#       HiddenAchievements (Name[]: conditions shown as ??? until taken), FreeAchievements (Name[]: count for the hidden
#       stage's free slots)
#     the state: UnlockedAchievements (Name[]), FreeAchievementCount (int), AchievementsLoaded (bool),
#       LastAchievement (Name: the one UnlockAchievement was last called with)
#     the run's flags (reset when a run starts - step 4): RunFell, RunUsedFlag, RunTookItem (bool)
#     function graphs UnlockAchievement and LoadAchievements (empty: their bodies are pasted, see
#       Generators/gen_achievements.ps1; UnlockAchievement's input ID (Name) is added by hand)
# Safe to run again: existing variables keep their place, the list's defaults are rewritten. Editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_achievements.py -unattended -nop4 -nosplash -stdout
import os

import unreal

FOLDER = "/Game/ThirdPerson/Blueprints/Achievements"
SAVE = FOLDER + "/BP_AchievementSave"
GAME_INSTANCE = "/Game/ThirdPerson/Blueprints/BP_MyGameInstance"

# id, name, condition, kind, hidden, free (counts towards the hidden stage's 12)
ACHIEVEMENTS = [
    ("ACH_AREA2", "歯車は回る", "大歯車でエリア1からエリア2へ上がる", "進行", False, False),
    ("ACH_AREA3", "人間大砲", "蒸気カタパルトでエリア2からエリア3へ飛ぶ", "進行", False, False),
    ("ACH_AREA4", "光の導き", "光の柱でエリア3からエリア4へ昇る", "進行", False, False),
    ("ACH_IWATO", "岩戸開き", "天の岩戸を開ける", "進行", False, False),
    ("ACH_WINGS", "天使の翼", "翼を手に入れる", "進行", False, False),
    ("ACH_CLEAR", "天国の門", "ゲームをクリアする", "進行", False, False),
    ("ACH_COIN_A1", "遺跡の宝", "エリア1のスターコインを全部集める", "収集", False, False),
    ("ACH_COIN_A2", "塔の宝", "エリア2のスターコインを全部集める", "収集", False, False),
    ("ACH_COIN_A3", "空の宝", "エリア3のスターコインを全部集める", "収集", False, False),
    ("ACH_COIN_A4", "天上の宝", "エリア4のスターコインを全部集める", "収集", False, False),
    ("ACH_COIN_ALL", "星を集める者", "全エリアのスターコインを全部集める", "収集", False, False),
    ("ACH_ITEM_ALL", "コレクター", "アイテムを全部回収する", "収集", False, True),
    ("ACH_SHARDS", "光を集めて", "光のかけらを 3 つ集める", "収集", False, True),
    ("ACH_FLAGS", "旗を掲げよ", "全部のチェックポイント旗を立てる", "収集", False, True),
    ("ACH_FIRST_FALL", "はじめての転落", "はじめて落ちる", "失敗", False, True),
    ("ACH_HELL", "地獄へようこそ", "地獄に落ちる", "失敗", False, True),
    ("ACH_HELL_BACK", "地獄からの生還", "地獄から戻る", "失敗", False, True),
    ("ACH_WRONG_CAGE", "選択を誤った", "鳥籠で外れを選ぶ", "失敗", False, True),
    ("ACH_SUN_GRAB", "お日さまに捕まった", "大塔の太陽に捕まってカゴに入れられる", "失敗", False, True),
    ("ACH_THREAD", "糸が切れた", "蜘蛛の糸が切れて落ちる", "失敗", False, True),
    ("ACH_SO_CLOSE", "あと一歩", "ゴールのすぐ手前から落ちる", "失敗", False, True),
    ("ACH_NO_FALL", "落ちない者", "一度も落ちずにクリアする", "腕前", False, False),
    ("ACH_TIME", "天への近道", "目標タイム以内にクリアする", "腕前", False, True),
    ("ACH_NO_FLAG", "旗いらず", "一度も旗から復活せずにクリアする", "腕前", False, True),
    ("ACH_PURIST", "アイテムなぞ！！使ってんじゃ！！！ねいええええぇぇ！！！！",
     "アイテムを一度も拾わず、旗からも一度も復活せずにクリアする", "腕前", False, False),
    ("ACH_SUN_DODGE", "太陽をかわせ", "暗い塔の太陽の突進を一度も受けずに塔を抜ける", "腕前", False, True),
    ("ACH_MELODY", "完璧な演奏", "旋律の宝石の道を一度も落ちずに抜ける", "腕前", False, True),
    ("ACH_BREAK_FLAG", "自ら折る", "立てた旗を自分で折る", "隠し", True, True),
    ("ACH_LEDGE", "崖っぷち", "崖につかまって登る", "隠し", True, True),
    ("ACH_REWIND", "時を戻す者", "時間巻き戻しエリアを使う", "隠し", True, True),
    ("ACH_DANGER", "押すなよ", "危険ボタンを押す", "隠し", True, True),
]

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
pins = unreal.BlueprintEditorLibrary
NAME, TEXT, STRING = (pins.get_basic_type_by_name(t) for t in ("name", "text", "string"))
TYPES = {
    "bool": pins.get_basic_type_by_name("bool"), "int": pins.get_basic_type_by_name("int"),
    "name": NAME, "names": pins.get_array_type(NAME), "texts": pins.get_array_type(TEXT), "strings": pins.get_array_type(STRING),
}
lines = []


def has_variable(bp, name):
    # add_member_variable would quietly add Name_0 next to an existing one, so check the CDO first.
    try:
        unreal.get_default_object(bp.generated_class()).get_editor_property(name)
        return True
    except Exception:
        return False


def add_variables(bp, path, variables):
    added = []
    for name, kind in variables:
        if has_variable(bp, name):
            continue
        if not pins.add_member_variable(bp, name, TYPES[kind]):
            raise RuntimeError("Could not add {} to {}".format(name, path))
        added.append(name)
    pins.compile_blueprint(bp)
    library.save_asset(path, False)
    lines.append("{}: {}".format(path.rsplit("/", 1)[1], ("added " + ", ".join(added)) if added else "variables already there"))


# ----- the save -----
if not library.does_asset_exist(SAVE):
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.SaveGame)
    tools.create_asset("BP_AchievementSave", FOLDER, unreal.Blueprint, factory)
    lines.append("BP_AchievementSave created")
save_bp = unreal.load_asset(SAVE)
add_variables(save_bp, SAVE, [("Unlocked", "names"), ("FreeCount", "int")])

# ----- the game instance -----
gi_bp = unreal.load_asset(GAME_INSTANCE)
add_variables(gi_bp, GAME_INSTANCE, [
    ("AchievementIds", "names"), ("AchievementNames", "texts"), ("AchievementDescriptions", "texts"),
    ("AchievementKinds", "strings"), ("HiddenAchievements", "names"), ("FreeAchievements", "names"),
    ("UnlockedAchievements", "names"), ("FreeAchievementCount", "int"), ("AchievementsLoaded", "bool"),
    ("LastAchievement", "name"), ("RunFell", "bool"), ("RunUsedFlag", "bool"), ("RunTookItem", "bool"),
])
for graph_name in ("UnlockAchievement", "LoadAchievements"):
    if pins.find_graph(gi_bp, graph_name) is None:
        pins.add_function_graph(gi_bp, graph_name)
        lines.append("BP_MyGameInstance: function {} added".format(graph_name))
pins.compile_blueprint(gi_bp)

gi = unreal.get_default_object(gi_bp.generated_class())
gi.set_editor_property("AchievementIds", [unreal.Name(a[0]) for a in ACHIEVEMENTS])
gi.set_editor_property("AchievementNames", [unreal.Text(a[1]) for a in ACHIEVEMENTS])
gi.set_editor_property("AchievementDescriptions", [unreal.Text(a[2]) for a in ACHIEVEMENTS])
gi.set_editor_property("AchievementKinds", [a[3] for a in ACHIEVEMENTS])
gi.set_editor_property("HiddenAchievements", [unreal.Name(a[0]) for a in ACHIEVEMENTS if a[4]])
gi.set_editor_property("FreeAchievements", [unreal.Name(a[0]) for a in ACHIEVEMENTS if a[5]])
library.save_asset(GAME_INSTANCE, False)
lines.append("list: {} achievements, {} hidden, {} free".format(
    len(ACHIEVEMENTS), sum(1 for a in ACHIEVEMENTS if a[4]), sum(1 for a in ACHIEVEMENTS if a[5])))

# read back what was saved
gi = unreal.get_default_object(unreal.load_asset(GAME_INSTANCE).generated_class())
names = gi.get_editor_property("AchievementNames")
lines.append("read back: {} ids, first name {}, last name {}".format(
    len(gi.get_editor_property("AchievementIds")), names[0] if names else None, names[-1] if names else None))

with open(os.path.join(unreal.Paths.project_saved_dir(), "setup_achievements.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
