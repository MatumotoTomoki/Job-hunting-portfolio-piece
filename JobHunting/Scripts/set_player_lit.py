# Lets the player character take light (the lava lights in hell, and every light elsewhere): the character's
# VRM4U MToon material instances in Chara01 are moved from the Unlit parents to the matching Lit ones
# (MI_VrmMToonOptUnlitOpaque -> MI_VrmMToonOptLitOpaque, and the same for TwoSided, Outline and Translucent).
# Their own parameters stay as they are. Set REVERT = True to move them back to Unlit.
# With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\set_player_lit.py -unattended -nop4 -nosplash -stdout
import os

import unreal

REVERT = False
FOLDER = "/Game/ThirdPerson/Blueprints/Chara01"
VRM = "/VRM4U/MaterialUtil/UE5/Material/"
FROM, TO = ("OptLit", "OptUnlit") if REVERT else ("OptUnlit", "OptLit")

library = unreal.EditorAssetLibrary
edit = unreal.MaterialEditingLibrary
lines = []
for path in library.list_assets(FOLDER, recursive=True, include_folder=False):
    asset = unreal.load_asset(path)
    if not isinstance(asset, unreal.MaterialInstanceConstant):
        continue
    parent = asset.get_editor_property("parent")
    if parent is None:
        continue
    parent_path = parent.get_path_name().split(".")[0]
    name = parent_path.rsplit("/", 1)[-1]
    if not parent_path.startswith(VRM) or FROM not in name:
        lines.append("kept   {} (parent {})".format(asset.get_name(), name))
        continue
    target_path = VRM + name.replace(FROM, TO)
    target = unreal.load_asset(target_path)
    if target is None:
        lines.append("NO MATCH {} (parent {}, wanted {})".format(asset.get_name(), name, target_path))
        continue
    edit.set_material_instance_parent(asset, target)
    library.save_asset(path.split(".")[0], False)
    lines.append("moved  {}: {} -> {}".format(asset.get_name(), name, target.get_name()))

with open(os.path.join(unreal.Paths.project_saved_dir(), "player_lit.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(lines))
unreal.log("\n".join(lines))
