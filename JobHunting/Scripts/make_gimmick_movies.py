# Short showcase clips of the gimmicks (the user, 2026-11-18: "one clip per gimmick type, per area, separate files").
# For every area level, one placed actor of each gimmick class (the first visible one) gets its own level sequence:
# a camera circling it 60 degrees in 6 s, eased, looking at its middle, at a distance from its size; the start angle
# is the clearest one (line traces from the gimmick out to where the camera would be), so walls don't block the view.
# Each clip also gets its own Movie Render Queue preset (MP4, 1280 x 720, the file named after the clip).
#   /Game/Cinematics/Gimmicks/LS_<Area>_<Class>, MRQ_<Area>_<Class>
#   Saved/MovieRenders/Gimmicks/clips.txt   one line per clip: level path, sequence, preset, name (for the renderer,
#                                           Scripts/render_gimmick_movies.ps1)
# No player in the renders: gimmicks that move by themselves (gears, platforms, beams, jewels...) move; ones the player
# sets off (levers, cages, catapult...) stand still. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\make_gimmick_movies.py -unattended -nop4 -nosplash -stdout
import math
import os

import unreal

LEVELS = [("Area1", "/Game/LV_Area1_Ruins"), ("Area2", "/Game/LV_Area2_Tower"), ("Area3", "/Game/LV_Area3_Sky"),
          ("Area4", "/Game/LV_Area4_Heaven")]
DIR = "/Game/Cinematics/Gimmicks"
OUT = os.path.join(os.path.abspath(unreal.Paths.project_saved_dir()), "MovieRenders", "Gimmicks")
SKIP = {"BP_AreaStart", "BP_EffekseerSystem", "BP_FallCatcher", "BP_CagePair", "BP_SunMarker", "BP_SkyLanding",
        "BP_TimeRewindArea", "BP_GravityZone", "BP_WindZone"}
FPS, SECONDS, SWEEP = 30, 6, 60.0

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
os.makedirs(OUT, exist_ok=True)
for old in library.list_assets(DIR, recursive=False) if library.does_directory_exist(DIR) else []:
    library.delete_asset(old.split(".")[0])
lines, clips = [], []


def visible_bounds(actor):
    # The box round the actor's visible meshes (trigger boxes and sun areas left out).
    low, high = None, None
    for component in actor.get_components_by_class(unreal.MeshComponent):
        if not component.is_visible() or component.get_editor_property("hidden_in_game"):
            continue
        origin, extent, _ = unreal.SystemLibrary.get_component_bounds(component)
        lo = (origin.x - extent.x, origin.y - extent.y, origin.z - extent.z)
        hi = (origin.x + extent.x, origin.y + extent.y, origin.z + extent.z)
        low = lo if low is None else tuple(min(a, b) for a, b in zip(low, lo))
        high = hi if high is None else tuple(max(a, b) for a, b in zip(high, hi))
    if low is None:
        return None
    centre = unreal.Vector(*((a + b) / 2.0 for a, b in zip(low, high)))
    size = max(b - a for a, b in zip(low, high)) / 2.0
    return centre, size


def clear(world, start, end, ignore):
    hit = unreal.SystemLibrary.line_trace_single(world, start, end, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False,
                                                 [ignore], unreal.DrawDebugTrace.NONE, True)
    return hit is None or not hit.to_tuple()[0]


def best_view(world, actor, centre, size):
    # Distance from size; try a ring of start angles, keep the one whose 60-degree sweep is clearest; closer if none.
    for scale in (1.0, 0.7, 0.45):
        distance = max(450.0, min(4500.0, size * 2.6 + 300.0)) * scale
        rise = distance * 0.35
        best, best_score = None, -1
        for k in range(12):
            start = 30.0 * k
            score = 0
            for step in range(5):
                a = math.radians(start + SWEEP * step / 4.0)
                eye = unreal.Vector(centre.x + distance * math.cos(a), centre.y + distance * math.sin(a), centre.z + rise)
                score += 1 if clear(world, centre, eye, actor) else 0
            if score > best_score:
                best, best_score = start, score
        if best_score >= 4:
            return best, distance, rise
    return best, distance, rise


def make_clip(name, centre, start, distance, rise):
    seq = tools.create_asset("LS_" + name, DIR, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
    frames = FPS * SECONDS
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
        a = math.radians(start + SWEEP * t * t * (3.0 - 2.0 * t))
        eye = unreal.Vector(centre.x + distance * math.cos(a), centre.y + distance * math.sin(a), centre.z + rise)
        look = unreal.MathLibrary.find_look_at_rotation(eye, centre)
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
    folder.set_editor_property("path", OUT)
    output.set_editor_property("output_directory", folder)
    output.set_editor_property("output_resolution", unreal.IntPoint(1280, 720))
    output.set_editor_property("file_name_format", name)
    config.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
    config.find_or_add_setting_by_class(unreal.MoviePipelineMP4EncoderOutput)
    aa = config.find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting)
    aa.set_editor_property("engine_warm_up_count", 45)
    aa.set_editor_property("render_warm_up_count", 45)
    cvars = config.find_or_add_setting_by_class(unreal.MoviePipelineConsoleVariableSetting)
    cvars.add_or_update_console_variable("r.DepthOfFieldQuality", 0.0)
    game = config.find_or_add_setting_by_class(unreal.MoviePipelineGameOverrideSetting)
    game.set_editor_property("game_mode_override", unreal.MoviePipelineGameMode.static_class())
    library.save_asset(DIR + "/MRQ_" + name, False)


for area, level_path in LEVELS:
    if not level_subsystem.load_level(level_path):
        lines.append("could not open " + level_path)
        continue
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    seen = set()
    for actor in actors.get_all_level_actors():
        cls = actor.get_class()
        if not isinstance(cls, unreal.BlueprintGeneratedClass):
            continue
        cname = cls.get_name()[:-2]
        if cname in SKIP or cname in seen or not cls.get_path_name().startswith("/Game/"):
            continue
        if actor.is_hidden_ed() or actor.get_editor_property("hidden"):
            continue
        found = visible_bounds(actor)
        if found is None:
            continue
        centre, size = found
        start, distance, rise = best_view(world, actor, centre, size)
        name = "{}_{}".format(area, cname.replace("BP_", ""))
        make_clip(name, centre, start, distance, rise)
        seen.add(cname)
        clips.append("{}|{}|{}|{}".format(level_path, DIR + "/LS_" + name, DIR + "/MRQ_" + name, name))
        lines.append("{}: {} ({}, size {:.0f}, distance {:.0f}, from {:.0f} deg)".format(area, name, actor.get_actor_label(), size, distance, start))

with open(os.path.join(OUT, "clips.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(clips) + "\n")
with open(os.path.join(unreal.Paths.project_saved_dir(), "gimmick_movies.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n{} clips\n".format(len(clips)))
unreal.log("\n".join(str(l) for l in lines))
