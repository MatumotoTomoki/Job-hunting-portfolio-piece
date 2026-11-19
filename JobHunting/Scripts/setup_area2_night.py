# Area 2's sky at night (the user, 2026-11-18: "the sky a night sky, with stars if possible").
#   - the "Sun" DirectionalLight becomes a moon: pale blue, weak, higher in the sky (the sky atmosphere then draws a
#     dark blue night and the light's disc as the moon);
#   - "A2 Night Stars": a huge sphere round the whole level with M_NightSky on its inside: T_NightStars
#     (build_night_stars.py: stars and a milky way, nothing below the horizon) x Brightness, unlit, two-sided, a sky
#     material (no aerial perspective over it).
#   /Game/Art/Sky: T_NightStars, M_NightSky.
# With --revert: the sun as build_area2_tower.py made it, and the stars removed. build_area2_tower.py also brings the
# old sun back: run this again after it. Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript "-script=<full path>\setup_area2_night.py [--revert]" -unattended -nop4 -nosplash -stdout
import os
import sys

import unreal

LEVEL = "/Game/LV_Area2_Tower"
DIR = "/Game/Art/Sky"
SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Textures", "Sky", "T_NightStars.png")
REVERT = "--revert" in " ".join(sys.argv)
# build_area2_tower.py's sun and mist, and the night. The mist ("Mist", ExponentialHeightFog) has its own glow colour,
# so at night it stayed a bright grey haze over everything - stars included (first try, 2026-11-18): at night it is a
# dark blue, and it stops at FOG_CUTOFF so the star sphere far beyond gets none.
DAY = {"pitch": -8.0, "yaw": 150.0, "intensity": 3.5, "color": (255, 150, 130), "fog": (0.22, 0.2, 0.3), "cutoff": 0.0}
NIGHT = {"pitch": -38.0, "yaw": 150.0, "intensity": 0.6, "color": (170, 195, 255), "fog": (0.012, 0.016, 0.04),
         "cutoff": 60000.0}
STAR_BRIGHTNESS = 4.0
SKY_RADIUS = 1500.0 * 100.0      # cm: well beyond the whole level

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
lines = []

material = None
if not REVERT:
    task = unreal.AssetImportTask()
    task.filename = SOURCE
    task.destination_path = DIR
    task.automated = True
    task.save = True
    task.replace_existing = True
    tools.import_asset_tasks([task])
    stars = unreal.load_asset(DIR + "/T_NightStars")
    stars.set_editor_property("never_stream", True)
    library.save_asset(DIR + "/T_NightStars", False)
    path = DIR + "/M_NightSky"
    if library.does_asset_exist(path):
        material = unreal.load_asset(path)
    else:
        material = tools.create_asset("M_NightSky", DIR, unreal.Material, unreal.MaterialFactoryNew())
        material.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
        material.set_editor_property("two_sided", True)
        material.set_editor_property("is_sky", True)
        sample = editing.create_material_expression(material, unreal.MaterialExpressionTextureSampleParameter2D, -600, 0)
        sample.set_editor_property("parameter_name", "Stars")
        sample.set_editor_property("texture", stars)
        bright = editing.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -600, 250)
        bright.set_editor_property("parameter_name", "Brightness")
        bright.set_editor_property("default_value", STAR_BRIGHTNESS)
        times = editing.create_material_expression(material, unreal.MaterialExpressionMultiply, -300, 100)
        editing.connect_material_expressions(sample, "RGB", times, "A")
        editing.connect_material_expressions(bright, "", times, "B")
        editing.connect_material_property(times, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        editing.recompile_material(material)
        library.save_asset(path, False)
        lines.append("created " + path)

level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not level.load_level(LEVEL):
    raise RuntimeError("Could not open " + LEVEL)
look = DAY if REVERT else NIGHT
xs, ys = [], []
for actor in actors.get_all_level_actors():
    label = actor.get_actor_label()
    if label.endswith("Night Stars"):
        actors.destroy_actor(actor)
        continue
    if isinstance(actor, unreal.DirectionalLight):
        actor.set_actor_rotation(unreal.Rotator(roll=0.0, pitch=look["pitch"], yaw=look["yaw"]), False)
        light = actor.get_editor_property("directional_light_component")
        light.set_editor_property("intensity", look["intensity"])
        r, g, b = look["color"]
        light.set_editor_property("light_color", unreal.Color(r=r, g=g, b=b, a=255))
        lines.append("{}: {}".format(label, "the sun again" if REVERT else "now the moon"))
    elif isinstance(actor, unreal.ExponentialHeightFog):
        fog = actor.get_editor_property("component")
        r, g, b = look["fog"]
        fog.set_editor_property("fog_inscattering_luminance", unreal.LinearColor(r, g, b, 1.0))
        fog.set_editor_property("fog_cutoff_distance", look["cutoff"])
        lines.append("{}: mist {} (cut off at {:.0f} cm)".format(label, look["fog"], look["cutoff"]))
    elif label.startswith("A2 ") and isinstance(actor, unreal.StaticMeshActor):
        where = actor.get_actor_location()
        xs.append(where.x)
        ys.append(where.y)
if not REVERT:
    centre = unreal.Vector((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0, 10000.0)
    dome = actors.spawn_actor_from_class(unreal.StaticMeshActor, centre, unreal.Rotator(0.0, 0.0, 0.0))
    dome.set_actor_label("A2 Night Stars")
    dome.set_folder_path("Area2/Sky")
    component = dome.get_editor_property("static_mesh_component")
    component.set_static_mesh(unreal.load_asset("/Engine/BasicShapes/Sphere"))
    component.set_material(0, material)
    component.set_collision_profile_name("NoCollision")
    component.set_editor_property("cast_shadow", False)
    dome.set_actor_scale3d(unreal.Vector(SKY_RADIUS / 50.0, SKY_RADIUS / 50.0, SKY_RADIUS / 50.0))
    lines.append("A2 Night Stars at {}, radius {:.0f} m".format(centre, SKY_RADIUS / 100.0))
lines.append("{} saved {}".format(LEVEL, level.save_current_level()))

with open(os.path.join(unreal.Paths.project_saved_dir(), "area2_night.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
