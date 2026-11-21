# Places the two remaining power-up items (the user, 2026-11-21; ACH_ITEM_ALL counts them):
#   LV_Area3_Sky     BP_Item2 (jump power up) on the flag island at the end of B Crosswind Beams, east of the flag
#   LV_Area4_Heaven  BP_2jump (double jump) on the Upside Down Floor, just before the first gravity zone
# Placed by finding what is already in the level (the flag in the B section folder; the floor by its label), so the
# levels are not rebuilt and the art imported over them stays. An item already there (same label) is left alone.
# Editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\place_items.py -unattended -nop4 -nosplash -stdout
import os

import unreal

ITEMS = "/Game/ThirdPerson/Item"
FLAG = ITEMS + "/Checkpoint/BP_CheckpointFlag"
ABOVE = 100.0   # items float this far over the floor, as the speed item does

level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
lines = []


def top_of(actor):
    origin, extent = actor.get_actor_bounds(False)
    return origin, origin.z + extent.z


def place(item_path, location, label, folder):
    existing = [a for a in actors.get_all_level_actors() if a.get_actor_label() == label]
    if existing:
        lines.append("{}: already there at {}".format(label, existing[0].get_actor_location()))
        return
    actor = actors.spawn_actor_from_class(unreal.load_asset(item_path).generated_class(), location, unreal.Rotator(0.0, 0.0, 0.0))
    actor.set_actor_label(label)
    actor.set_folder_path(folder)
    lines.append("{}: placed at {}".format(label, location))


# ----- area 3: the jump item beside flag 1 -----
if not level.load_level("/Game/LV_Area3_Sky"):
    raise RuntimeError("Could not open LV_Area3_Sky")
flag_class = unreal.load_asset(FLAG).generated_class()
flags = [a for a in actors.get_all_level_actors() if a.get_class() == flag_class and "B Crosswind" in str(a.get_folder_path())]
if len(flags) != 1:
    raise RuntimeError("Expected one flag in B Crosswind Beams, found {}".format(len(flags)))
spot = flags[0].get_actor_location()
# The flag stands 150 west of the island's middle: the item goes 150 east of it, the island's top under both.
place(ITEMS + "/BP_Item2", unreal.Vector(spot.x + 300.0, spot.y, spot.z + ABOVE), "A3 Jump Item", "Area3/B Crosswind Beams")
lines.append("LV_Area3_Sky saved {}".format(level.save_current_level()))

# ----- area 4: the double jump before the first gravity zone -----
if not level.load_level("/Game/LV_Area4_Heaven"):
    raise RuntimeError("Could not open LV_Area4_Heaven")
floors = [a for a in actors.get_all_level_actors() if a.get_actor_label().endswith("Upside Down Floor")]
if len(floors) != 1:
    raise RuntimeError("Expected one Upside Down Floor, found {}".format(len(floors)))
middle, top = top_of(floors[0])
place(ITEMS + "/BP_2jump", unreal.Vector(middle.x, middle.y, top + ABOVE), "A4 Double Jump Item", str(floors[0].get_folder_path()))
lines.append("LV_Area4_Heaven saved {}".format(level.save_current_level()))

with open(os.path.join(unreal.Paths.project_saved_dir(), "place_items.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
