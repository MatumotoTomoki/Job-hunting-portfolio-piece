# Makes LV_Hell dark like the Time Rewind Area's night: Hell Light (the red sun) turned under the horizon (pitch above
# 0), so the sky goes dark; Hell Fog no longer glows orange on its own. Auto exposure would brighten the dark back up,
# so the level's Post Process Volume (added if there is none) fixes the exposure: Min and Max EV100 the same.
# With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\set_hell_night.py -unattended -nop4 -nosplash -stdout
import os

import unreal

HELL_LEVEL = "/Game/LV_Hell"
NIGHT_PITCH = 10.0
FOG_GLOW = unreal.LinearColor(0.06, 0.006, 0.002, 1.0)
EXPOSURE_EV100 = 1.0     # used only when this script adds the volume; an existing one keeps its values

level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
lines = []
if not level.load_level(HELL_LEVEL):
    raise RuntimeError("Could not open " + HELL_LEVEL)
by_label = {a.get_actor_label(): a for a in actors.get_all_level_actors()}

light = by_label.get("Hell Light")
if light:
    before = light.get_actor_rotation()
    light.set_actor_rotation(unreal.Rotator(roll=before.roll, pitch=NIGHT_PITCH, yaw=before.yaw), False)
    lines.append("Hell Light rotation {} -> {}".format(before, light.get_actor_rotation()))
else:
    lines.append("WARNING: Hell Light not found")

fog = by_label.get("Hell Fog")
if fog:
    component = fog.get_editor_property("component")
    lines.append("Hell Fog inscattering {} -> {}".format(component.get_editor_property("fog_inscattering_luminance"), FOG_GLOW))
    component.set_editor_property("fog_inscattering_luminance", FOG_GLOW)
else:
    lines.append("WARNING: Hell Fog not found")

volumes = [a for a in actors.get_all_level_actors() if isinstance(a, unreal.PostProcessVolume)]
if volumes:
    for volume in volumes:
        settings = volume.get_editor_property("settings")
        lines.append("Post Process Volume '{}': unbound {}, EV100 min {} ({}) max {} ({})".format(
            volume.get_actor_label(), volume.get_editor_property("unbound"),
            settings.get_editor_property("auto_exposure_min_brightness"), settings.get_editor_property("override_auto_exposure_min_brightness"),
            settings.get_editor_property("auto_exposure_max_brightness"), settings.get_editor_property("override_auto_exposure_max_brightness")))
else:
    volume = actors.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0.0, 0.0, 0.0))
    volume.set_actor_label("Hell Exposure")
    volume.set_editor_property("unbound", True)
    settings = volume.get_editor_property("settings")
    for name, value in (("auto_exposure_min_brightness", EXPOSURE_EV100), ("auto_exposure_max_brightness", EXPOSURE_EV100)):
        settings.set_editor_property("override_" + name, True)
        settings.set_editor_property(name, value)
    volume.set_editor_property("settings", settings)
    lines.append("added Post Process Volume 'Hell Exposure': unbound, EV100 fixed at {}".format(EXPOSURE_EV100))

lines.append("LV_Hell saved {}".format(level.save_current_level()))
with open(os.path.join(unreal.Paths.project_saved_dir(), "hell_night.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
