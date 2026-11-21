# Achievements step 4b: checks that each area's BP_AreaStart AreaCoins (the total the HUD and ACH_COIN_A1..A4 count
# against) matches the BP_StarCoin actors placed in that level, and lists the items and flags (4b-2). Changes nothing. Writes Saved/check_coin_totals.txt.
# Editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\check_coin_totals.py -unattended -nop4 -nosplash -stdout
import os

import unreal

LEVELS = ["/Game/LV_Area1_Ruins", "/Game/LV_Area2_Tower", "/Game/LV_Area3_Sky", "/Game/LV_Area4_Heaven"]
COIN = "/Game/ThirdPerson/Coin/StarCoin/BP_StarCoin"
AREA_START = "/Game/ThirdPerson/Blueprints/Gimmicks/Area/BP_AreaStart"

level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
coin_class = unreal.load_asset(COIN).generated_class()
start_class = unreal.load_asset(AREA_START).generated_class()
item_class = unreal.load_asset("/Game/ThirdPerson/Item/BP_Item").generated_class()
flag_class = unreal.load_asset("/Game/ThirdPerson/Item/Checkpoint/BP_CheckpointFlag").generated_class()
lines = []
for path in LEVELS:
    if not level.load_level(path):
        lines.append("{}: could not open".format(path))
        continue
    everything = actors.get_all_level_actors()
    coins = [a for a in everything if a.get_class() == coin_class]
    starts = [a for a in everything if a.get_class() == start_class]
    totals = [s.get_editor_property("AreaCoins") for s in starts]
    ok = len(starts) == 1 and totals[0] == len(coins)
    lines.append("{}: coins placed {}, AreaCoins {} -> {}".format(path.rsplit("/", 1)[1], len(coins), totals, "OK" if ok else "MISMATCH"))
    for c in coins:
        lines.append("    " + c.get_name())
    # For ACH_ITEM_ALL and ACH_FLAGS (step 4b-2): what else there is to collect.
    items = [a for a in everything if unreal.MathLibrary.class_is_child_of(a.get_class(), item_class)]
    flags = [a for a in everything if a.get_class() == flag_class]
    lines.append("    items {}: {}".format(len(items), ", ".join("{} ({})".format(a.get_name(), a.get_class().get_name()) for a in items)))
    lines.append("    flags {}: {}".format(len(flags), ", ".join(a.get_name() for a in flags)))

with open(os.path.join(unreal.Paths.project_saved_dir(), "check_coin_totals.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(lines) + "\n")
unreal.log("\n".join(lines))
