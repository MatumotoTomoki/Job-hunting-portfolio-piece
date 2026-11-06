# Points the player's AnimBP and blend space at the handmade animations from build_player_anims.py, by consolidating:
# every reference to an old retargeted animation is moved to its handmade replacement, and the old one is deleted
# (they are in git). Also makes AM_DoubleJump_Handmade, a montage on DefaultSlot for the double jump.
# Run once, with the editor closed:
#   UnrealEditor-Cmd.exe JobHunting.uproject -run=pythonscript -script=swap_player_anims.py -unattended -nop4 -nosplash -stdout
import os

import unreal

BASE = "/Game/ThirdPerson/Blueprints/Plaey/"
ANIM_DIR = BASE + "Anim/"
library = unreal.EditorAssetLibrary
lines = []

# The retargeted walk and jog samples never moved this character's legs; every direction and speed now uses the run.
directions = ["Fwd", "Fwd_Left", "Fwd_Right", "Left", "Right", "Bwd", "Bwd_Left", "Bwd_Right"]
swaps = {
    "MM_Run_Handmade": ["MF_Unarmed_{}_{}_nokusia".format(gait, d) for gait in ("Walk", "Jog") for d in directions],
    "MM_Jump_Handmade": ["MM_Jump_nokusia"],
    "MM_Fall_Handmade": ["MM_Fall_Loop_nokusia"],
}
for new_name, old_names in swaps.items():
    new_asset = unreal.load_asset(ANIM_DIR + new_name)
    if not new_asset:
        raise RuntimeError("Missing " + ANIM_DIR + new_name + ": run build_player_anims.py first")
    old_assets = [unreal.load_asset(BASE + n) for n in old_names if library.does_asset_exist(BASE + n)]
    if old_assets:
        lines.append("{} <- {}: {}".format(new_name, [a.get_name() for a in old_assets], library.consolidate_assets(new_asset, old_assets)))
    else:
        lines.append("{}: nothing left to replace".format(new_name))

montage_path = ANIM_DIR + "AM_DoubleJump_Handmade"
if not library.does_asset_exist(montage_path):
    factory = unreal.AnimMontageFactory()
    factory.set_editor_property("source_animation", unreal.load_asset(ANIM_DIR + "MM_DoubleJump_Handmade"))
    montage = unreal.AssetToolsHelpers.get_asset_tools().create_asset("AM_DoubleJump_Handmade", ANIM_DIR.rstrip("/"), unreal.AnimMontage, factory)
    library.save_asset(montage_path, False)
    lines.append("montage created: {}".format(montage))

for path in (BASE + "ABP_Unarmed_nokusia", BASE + "BS_Idle_Walk_Run_nokusia"):
    asset = unreal.load_asset(path)
    if isinstance(asset, unreal.Blueprint):
        unreal.BlueprintEditorLibrary.compile_blueprint(asset)
    library.save_asset(path, False)

blend = unreal.load_asset(BASE + "BS_Idle_Walk_Run_nokusia")
lines.append("blend space now: {}".format(sorted({s.get_editor_property("animation").get_name() for s in blend.get_editor_property("sample_data")})))
registry = unreal.AssetRegistryHelpers.get_asset_registry()
lines.append("abp uses: {}".format([str(d) for d in registry.get_dependencies(BASE + "ABP_Unarmed_nokusia", unreal.AssetRegistryDependencyOptions()) if "Anim" in str(d) or "MM_" in str(d) or "BS_" in str(d)]))
montage = unreal.load_asset(montage_path)
lines.append("montage slot: {}".format([t.get_editor_property("slot_name") for t in montage.get_editor_property("slot_anim_tracks")]))
lines.append("left in Plaey: {}".format(sorted(p.split(".")[-1] for p in library.list_assets(BASE, recursive=False) if "nokusia" in p)))
with open(os.path.join(unreal.Paths.project_saved_dir(), "swap_player_anims.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
