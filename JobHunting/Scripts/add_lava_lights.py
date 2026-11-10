# Lets the lava light up hell: a row of red point lights just over the lava sea of LV_Hell, so the rock pillars and
# platforms glow from below. The lava's own look (MI_HellLavaLiquid) is not touched. No shadows, movable: cheap, and
# they overlap freely. Labelled "Lava Light NN" and rebuilt on every run (build_hell_stage.py does not place them;
# run this again after it). With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\add_lava_lights.py -unattended -nop4 -nosplash -stdout
import os

import unreal

HELL_LEVEL = "/Game/LV_Hell"
SPACING = 1200.0            # cm between lights along the stage
HEIGHT = 120.0              # above the lava surface
INTENSITY = 80.0            # candelas each (tuned for the fixed exposure of EV100 1)
RADIUS = 1600.0             # how far each one reaches
COLOR = unreal.Color(r=255, g=70, b=25, a=255)
PREFIX = "Lava Light"

level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
lines = []
if not level.load_level(HELL_LEVEL):
    raise RuntimeError("Could not open " + HELL_LEVEL)
for actor in actors.get_all_level_actors():
    if actor.get_actor_label().startswith(PREFIX):
        actors.destroy_actor(actor)

sea = next((a for a in actors.get_all_level_actors() if a.get_actor_label().endswith("Lava Sea")), None)
if not sea:
    raise RuntimeError("No Lava Sea in LV_Hell")
center = sea.get_actor_location()
length = sea.get_actor_scale3d().x * 100.0
start_x = center.x - length / 2.0 + SPACING / 2.0
count = int(length // SPACING)
for i in range(count):
    location = unreal.Vector(start_x + SPACING * i, 0.0, center.z + HEIGHT)
    light = actors.spawn_actor_from_class(unreal.PointLight, location)
    light.set_actor_label("{} {:02d}".format(PREFIX, i + 1))
    light.set_folder_path("HellStage/Lava Lights")
    component = light.get_editor_property("point_light_component")
    component.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    component.set_editor_property("intensity_units", unreal.LightUnits.CANDELAS)
    component.set_editor_property("intensity", INTENSITY)
    component.set_editor_property("light_color", COLOR)
    component.set_editor_property("attenuation_radius", RADIUS)
    component.set_editor_property("source_radius", 200.0)
    component.set_editor_property("cast_shadows", False)
lines.append("{} lava lights from x {:.0f}, every {:.0f} cm, {:.0f} cm over the lava (z {:.0f}), {} cd, radius {}".format(
    count, start_x, SPACING, HEIGHT, center.z + HEIGHT, INTENSITY, RADIUS))
lines.append("LV_Hell saved {}".format(level.save_current_level()))
with open(os.path.join(unreal.Paths.project_saved_dir(), "lava_lights.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
