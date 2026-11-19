# A Movie Render Queue try-out (the user, 2026-11-18): a 10 s camera orbit round area 2's tower, written out as MP4.
#   /Game/Cinematics/LS_Area2Orbit   a level sequence: a spawned CineCamera circling the tower (120 degrees, eased
#                                     in and out), always looking at the tower's upper half; a camera cut to it.
#   /Game/Cinematics/MRQ_Area2Orbit  a Movie Render Queue preset: 1280 x 720, deferred lighting, MP4 out into
#                                     Saved/MovieRenders, warm-up frames so auto exposure settles, the game mode
#                                     overridden (no player, no HUD in the shot).
# This script only makes the two assets (editor closed):
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\make_orbit_movie.py -unattended -nop4 -nosplash -stdout
# Then render (a game window opens, renders and closes by itself):
#   UnrealEditor.exe <full path>\JobHunting.uproject /Game/LV_Area2_Tower -game -LevelSequence="/Game/Cinematics/LS_Area2Orbit" -MoviePipelineConfig="/Game/Cinematics/MRQ_Area2Orbit" -windowed -resx=1280 -resy=720 -log -nosplash -unattended
# In the editor the same sequence can be opened and rendered from Sequencer's clapperboard button.
import math
import os

import unreal

DIR = "/Game/Cinematics"
SEQ = "LS_Area2Orbit"
CFG = "MRQ_Area2Orbit"
FPS = 30
SECONDS = 10
CENTRE = unreal.Vector(7650.0, 3525.0, 11500.0)     # the tower's middle, a little high
RADIUS = 9000.0
HEIGHT = 15500.0
START_YAW, SWEEP = -60.0, 120.0

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
lines = []

for name in (SEQ, CFG):
    if library.does_asset_exist(DIR + "/" + name):
        library.delete_asset(DIR + "/" + name)

# ----- the sequence -----
try:
    factory = unreal.LevelSequenceFactoryNew()
except AttributeError:
    factory = None
seq = tools.create_asset(SEQ, DIR, unreal.LevelSequence, factory)
frames = FPS * SECONDS
seq.set_display_rate(unreal.FrameRate(FPS, 1))
seq.set_tick_resolution(unreal.FrameRate(FPS, 1))
seq.set_playback_start(0)
seq.set_playback_end(frames)

camera = seq.add_spawnable_from_class(unreal.CineCameraActor)
# (The spawned camera's template has no reachable component in a commandlet, so no focus settings here: the preset
# turns depth of field off with a console variable instead.)
track = camera.add_track(unreal.MovieScene3DTransformTrack)
section = track.add_section()
section.set_range(0, frames)
channels = section.get_all_channels()     # location x y z, rotation x(roll) y(pitch) z(yaw), scale x y z
prev_yaw = None
for f in range(0, frames + 1, 5):
    t = f / frames
    eased = t * t * (3.0 - 2.0 * t)
    a = math.radians(START_YAW + SWEEP * eased)
    eye = unreal.Vector(CENTRE.x + RADIUS * math.cos(a), CENTRE.y + RADIUS * math.sin(a), HEIGHT)
    look = unreal.MathLibrary.find_look_at_rotation(eye, CENTRE)
    yaw = look.yaw
    if prev_yaw is not None:
        while yaw - prev_yaw > 180.0:
            yaw -= 360.0
        while yaw - prev_yaw < -180.0:
            yaw += 360.0
    prev_yaw = yaw
    frame = unreal.FrameNumber(f)
    for channel, value in zip(channels[:6], (eye.x, eye.y, eye.z, 0.0, look.pitch, yaw)):
        channel.add_key(frame, value)
cut_track = seq.add_track(unreal.MovieSceneCameraCutTrack)
cut = cut_track.add_section()
cut.set_range(0, frames)
cut.set_camera_binding_id(seq.get_portable_binding_id(seq, camera) if hasattr(seq, "get_portable_binding_id") else seq.get_binding_id(camera))
library.save_asset(DIR + "/" + SEQ, False)
lines.append("sequence {} frames at {} fps".format(frames, FPS))

# ----- the render preset -----
config = tools.create_asset(CFG, DIR, unreal.MoviePipelinePrimaryConfig, unreal.MoviePipelinePrimaryConfigFactory())
output = config.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
folder = unreal.DirectoryPath()
folder.set_editor_property("path", os.path.join(os.path.abspath(unreal.Paths.project_saved_dir()), "MovieRenders"))
output.set_editor_property("output_directory", folder)
output.set_editor_property("output_resolution", unreal.IntPoint(1280, 720))
output.set_editor_property("file_name_format", "Area2Orbit")   # ({sequence_name} came out empty: the file was ".mp4")
config.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
config.find_or_add_setting_by_class(unreal.MoviePipelineMP4EncoderOutput)
aa = config.find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting)
aa.set_editor_property("engine_warm_up_count", 60)
aa.set_editor_property("render_warm_up_count", 60)
cvars = config.find_or_add_setting_by_class(unreal.MoviePipelineConsoleVariableSetting)
try:
    cvars.add_or_update_console_variable("r.DepthOfFieldQuality", 0.0)     # everything sharp
except Exception as error:
    lines.append("depth of field cvar not set: {}".format(error))
game = config.find_or_add_setting_by_class(unreal.MoviePipelineGameOverrideSetting)
game.set_editor_property("game_mode_override", unreal.MoviePipelineGameMode.static_class())
library.save_asset(DIR + "/" + CFG, False)
lines.append("preset saved; output " + folder.path)

with open(os.path.join(unreal.Paths.project_saved_dir(), "orbit_movie.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
