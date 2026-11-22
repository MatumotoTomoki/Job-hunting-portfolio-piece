# BGM by area (the user, 2026-11-22: the levels are areas now, so the old height BGM no longer fits):
#   BP_AreaBgm (/Game/ThirdPerson/Blueprints)  variable AreaBgm (SoundBase, per placed actor). Its graph
#              (BP_AreaBgm_EventGraph.txt, Generators/gen_area_bgm.ps1) makes the player controller's HeightBgmList
#              just that track at Begin Play, so the controller's height-BGM Tick plays it (crossfading from the last).
#   One BP_AreaBgm in each area level (AREA_BGM below), set to its track; an existing one is reused and re-set.
# Every area and the hidden stage get their own free track (IMPORT_BGM, imported first).
# To change a track, edit AREA_BGM and run again.
# Levels are opened and saved one by one, so save your work first. Run it in the editor's Output Log (Python):
#   exec(open(r'C:\Git\Job-hunting-portfolio-piece\JobHunting\Scripts\setup_area_bgm.py', encoding='utf-8').read())
import os

import unreal

BP_PATH = "/Game/ThirdPerson/Blueprints/BP_AreaBgm"
BGM = "/Game/Sound/BGM/"
# Free tracks (OpenTracks, formerly DOVA-SYNDROME; in-game use OK, don't hand out the files themselves):
#   BGM_Ruins = "古代遺跡" (ancient ruins), BGM_Tower = "機械仕掛けの地底世界" (Mechanical Underground World),
#   BGM_Sky = "空中都市" (Aerial city), all マニーラ; BGM_Heaven = "神秘の世界" (なつこらーじゅ),
#   BGM_Hell = "闇に潜めし者" (マニーラ, loop version), BGM_Secret = "天空" (the hidden stage, chosen by the user 11-22).
# Decoded by decode_audio_blender.py --stereo, silence trimmed by trim_bgm_silence.ps1 (Ruins/Tower/Sky at
# -Threshold 100, cutting the reverb tail so the loop has no gap); imported looping.
IMPORT_BGM = ["BGM_Ruins", "BGM_Tower", "BGM_Sky", "BGM_Heaven", "BGM_Hell", "BGM_Secret"]
AREA_BGM = {
    "/Game/LV_Area1_Ruins": BGM + "BGM_Ruins",
    "/Game/LV_Area2_Tower": BGM + "BGM_Tower",
    "/Game/LV_Area3_Sky": BGM + "BGM_Sky",
    "/Game/LV_Area4_Heaven": BGM + "BGM_Heaven",
    "/Game/LV_Hell": BGM + "BGM_Hell",
    "/Game/LV_Secret": BGM + "BGM_Secret",
    "/Game/LV_Secret2": BGM + "BGM_Secret",   # (until hidden area 2 has its own track)
    "/Game/LV_Secret3": BGM + "BGM_Secret",   # (until hidden area 3 has its own track)
}
library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
pins = unreal.BlueprintEditorLibrary
level_editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
lines = []

SOURCE_BGM = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()), "SourceArt", "Sounds", "BGM")
for name in IMPORT_BGM:
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", os.path.join(SOURCE_BGM, name + ".wav"))
    task.set_editor_property("destination_path", BGM.rstrip("/"))
    task.set_editor_property("destination_name", name)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("automated", True)
    task.set_editor_property("save", False)
    tools.import_asset_tasks([task])
    wave = unreal.load_asset(BGM + name)
    if not wave:
        raise RuntimeError("Could not import " + name)
    wave.set_editor_property("looping", True)
    library.save_asset(BGM + name, False)
    lines.append("imported {} ({:.1f} s, looping)".format(BGM + name, wave.get_editor_property("duration")))

if library.does_asset_exist(BP_PATH):
    bp = unreal.load_asset(BP_PATH)
else:
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    bp = tools.create_asset("BP_AreaBgm", "/Game/ThirdPerson/Blueprints", unreal.Blueprint, factory)
    lines.append("created " + BP_PATH)
try:
    unreal.get_default_object(bp.generated_class()).get_editor_property("AreaBgm")
except Exception:
    if not pins.add_member_variable(bp, "AreaBgm", pins.get_object_reference_type(unreal.SoundBase.static_class())):
        raise RuntimeError("Could not add AreaBgm")
    pins.set_blueprint_variable_instance_editable(bp, "AreaBgm", True)
    lines.append("BP_AreaBgm: variable AreaBgm")
pins.compile_blueprint(bp)
library.save_asset(BP_PATH, False)
cls = bp.generated_class()

start_level = unreal.EditorLevelLibrary.get_editor_world().get_path_name().split(".")[0]
for level, track in AREA_BGM.items():
    if not library.does_asset_exist(level):
        lines.append("missing level " + level)
        continue
    sound = unreal.load_asset(track)
    level_editor.load_level(level)
    found = [a for a in actors.get_all_level_actors() if a.get_class() == cls]
    actor = found[0] if found else actors.spawn_actor_from_class(cls, unreal.Vector(0.0, 0.0, 0.0))
    for extra in found[1:]:
        actors.destroy_actor(extra)
    actor.set_actor_label("Area BGM")
    actor.set_editor_property("AreaBgm", sound)
    level_editor.save_current_level()
    lines.append("{}: {}{}".format(level, track, "" if found else " (placed)"))
if start_level and library.does_asset_exist(start_level):
    level_editor.load_level(start_level)

with open(os.path.join(unreal.Paths.project_saved_dir(), "area_bgm.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
