# A tour of a whole area as a movie (the user, 2026-11-18: "area 1's whole movie"): the camera circles the area once
# (300 degrees in TOUR_SECONDS, eased), rising from near its foot to above its top, always looking at the area's middle
# at a height that climbs with it - the way the player climbs. Made from the bounds of the area's "A<n> " actors.
#   /Game/Cinematics/LS_<Area>Tour, MRQ_<Area>Tour (1920 x 1080 MP4 into Saved/MovieRenders, file <Area>Tour.mp4)
# Make (editor closed; the area as the script's argument, Area1 .. Area4):
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript "-script=<full path>\make_area_movie.py Area1" -unattended -nop4 -nosplash -stdout
# Render (a game window opens and closes by itself):
#   UnrealEditor.exe <full path>\JobHunting.uproject /Game/LV_Area1_Ruins -game -LevelSequence="/Game/Cinematics/LS_Area1Tour" -MoviePipelineConfig="/Game/Cinematics/MRQ_Area1Tour" -windowed -resx=1920 -resy=1080 -log -nosplash -unattended
import math
import os
import sys

import unreal

AREAS = {"Area1": ("/Game/LV_Area1_Ruins", "A1 "), "Area2": ("/Game/LV_Area2_Tower", "A2 "),
         "Area3": ("/Game/LV_Area3_Sky", "A3 "), "Area4": ("/Game/LV_Area4_Heaven", "A4 ")}
AREA = next((a for a in sys.argv if a in AREAS), "Area1")
LEVEL, PREFIX = AREAS[AREA]
DIR = "/Game/Cinematics"
FPS, TOUR_SECONDS, SWEEP = 30, 20, 300.0

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not level.load_level(LEVEL):
    raise RuntimeError("Could not open " + LEVEL)
low, high = [1e12] * 3, [-1e12] * 3
tops = []
for actor in actors.get_all_level_actors():
    if not actor.get_actor_label().startswith(PREFIX) or not isinstance(actor, unreal.StaticMeshActor):
        continue
    o, e = actor.get_actor_bounds(False)
    if max(e.x, e.y) > 20000.0:          # skies, catchers, star domes
        continue
    for k, (c, h) in enumerate(((o.x, e.x), (o.y, e.y), (o.z, e.z))):
        low[k], high[k] = min(low[k], c - h), max(high[k], c + h)
    tops.append(o.z + e.z)
# The climb starts where most tops are low, not at the deepest cliff foot (area 1's goes 40 m under its town).
tops.sort()
low[2] = tops[len(tops) // 10]
centre = unreal.Vector((low[0] + high[0]) / 2.0, (low[1] + high[1]) / 2.0, (low[2] + high[2]) / 2.0)
span = math.hypot(high[0] - low[0], high[1] - low[1])
radius = span * 0.75 + 1500.0
z_from, z_to = low[2] + 800.0, high[2] + 2500.0
look_from, look_to = low[2] + 300.0, high[2] - 200.0

name = AREA + "Tour"
for asset in ("LS_" + name, "MRQ_" + name):
    if library.does_asset_exist(DIR + "/" + asset):
        library.delete_asset(DIR + "/" + asset)
seq = tools.create_asset("LS_" + name, DIR, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
frames = FPS * TOUR_SECONDS
seq.set_display_rate(unreal.FrameRate(FPS, 1))
seq.set_tick_resolution(unreal.FrameRate(FPS, 1))
seq.set_playback_start(0)
seq.set_playback_end(frames)
camera = seq.add_spawnable_from_class(unreal.CineCameraActor)
section = camera.add_track(unreal.MovieScene3DTransformTrack).add_section()
section.set_range(0, frames)
channels = section.get_all_channels()
prev = None
for f in range(0, frames + 1, 5):
    t = f / frames
    s = t * t * (3.0 - 2.0 * t)
    a = math.radians(200.0 + SWEEP * s)        # start on the side the area begins (its low west end)
    eye = unreal.Vector(centre.x + radius * math.cos(a), centre.y + radius * math.sin(a), z_from + (z_to - z_from) * s)
    target = unreal.Vector(centre.x, centre.y, look_from + (look_to - look_from) * s)
    look = unreal.MathLibrary.find_look_at_rotation(eye, target)
    yaw = look.yaw
    if prev is not None:
        while yaw - prev > 180.0:
            yaw -= 360.0
        while yaw - prev < -180.0:
            yaw += 360.0
    prev = yaw
    for channel, value in zip(channels[:6], (eye.x, eye.y, eye.z, 0.0, look.pitch, yaw)):
        channel.add_key(unreal.FrameNumber(f), value)
cut = seq.add_track(unreal.MovieSceneCameraCutTrack).add_section()
cut.set_range(0, frames)
cut.set_camera_binding_id(seq.get_portable_binding_id(seq, camera))
library.save_asset(DIR + "/LS_" + name, False)

config = tools.create_asset("MRQ_" + name, DIR, unreal.MoviePipelinePrimaryConfig, unreal.MoviePipelinePrimaryConfigFactory())
output = config.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
folder = unreal.DirectoryPath()
folder.set_editor_property("path", os.path.join(os.path.abspath(unreal.Paths.project_saved_dir()), "MovieRenders"))
output.set_editor_property("output_directory", folder)
output.set_editor_property("output_resolution", unreal.IntPoint(1920, 1080))
output.set_editor_property("file_name_format", name)
config.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
config.find_or_add_setting_by_class(unreal.MoviePipelineMP4EncoderOutput)
aa = config.find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting)
aa.set_editor_property("engine_warm_up_count", 60)
aa.set_editor_property("render_warm_up_count", 60)
cvars = config.find_or_add_setting_by_class(unreal.MoviePipelineConsoleVariableSetting)
cvars.add_or_update_console_variable("r.DepthOfFieldQuality", 0.0)
game = config.find_or_add_setting_by_class(unreal.MoviePipelineGameOverrideSetting)
game.set_editor_property("game_mode_override", unreal.MoviePipelineGameMode.static_class())
library.save_asset(DIR + "/MRQ_" + name, False)

report = "{}: bounds x {:.0f}..{:.0f} y {:.0f}..{:.0f} z {:.0f}..{:.0f}; radius {:.0f}, camera z {:.0f}..{:.0f}".format(
    name, low[0], high[0], low[1], high[1], low[2], high[2], radius, z_from, z_to)
with open(os.path.join(unreal.Paths.project_saved_dir(), "area_movie.txt"), "w", encoding="utf-8") as out:
    out.write(report + "\n")
unreal.log(report)
