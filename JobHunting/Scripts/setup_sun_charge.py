# Turns BP_Sun into the charging-sun gimmick and places it in LV_Debug. The Event Graph comes from
# BP_Sun_EventGraph.txt. What it sets up:
#   BP_Sun   an Area box like the Time Rewind Area's (10 m, sitting on the actor's origin), the sun (SunMesh) raised to
#            HOME_HEIGHT inside it, and the SunFire flames re-attached to SunMesh so they travel with it; the actor
#            itself never moves or turns, only SunMesh does, so the Area stays put. A level Platform box on top of the
#            ball to ride on. Plus the variables of the charge, the ride and the anger.
#   LV_Debug the sun after the Time Rewind Area with room for both 10 m boxes, its label beside the box like the
#            Time Rewind Area's, the goal one step past it and the floor long enough.
# Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe JobHunting.uproject -run=pythonscript -script=setup_sun_charge.py -unattended -nop4 -nosplash -stdout
import os

import unreal

BLUEPRINT_PATH = "/Game/ThirdPerson/Blueprints/Gimmicks/Sun/BP_Sun"
HALF_SIZE = 500.0
HOME_HEIGHT = 700.0
# Per placed sun: seconds to aim (it tracks the player, locking on at the end), to charge, to stay, to rise back; how
# hard a hit throws the player along the charge and up; how close counts as a hit (the 50 cm ball plus the capsule).
SETTINGS = {
    "AimSeconds": 1.0, "ChargeSeconds": 1.0, "StaySeconds": 1.0, "ReturnSeconds": 2.0,
    "KnockbackStrength": 1500.0, "KnockbackUp": 600.0, "HitRadius": 110.0,
    # How far below the player's capsule centre the ball aims, so it lands on the ground (capsule half 96 - ball 50)
    # and a player who dodged can jump on top; how fast a rider is thrown up at the top; how near the Platform counts
    # as riding; how much faster every phase gets per step of anger.
    "LandDrop": 45.0, "RideLaunch": 1400.0, "RideRadius": 140.0, "AngerPace": 1.25,
}
INT_SETTINGS = {"MaxAnger": 3}   # Missed charges in a row before it is at its fastest and the face stays (╯‵□′)╯.
# The rideable top: a level box over the ball (it does not turn with SunMesh), solid only while it stays and rises.
PLATFORM_EXTENT = unreal.Vector(45.0, 45.0, 8.0)
PLATFORM_ABOVE = 42.0     # Its top on the ball's top; the Event Graph uses the same number.
AREA_X = 10400.0          # The Time Rewind Area (setup_time_rewind.py).
SUN_X = AREA_X + 2 * HALF_SIZE + 200.0
GOAL_X = SUN_X + HALF_SIZE + 700.0
FLOOR_END = GOAL_X + 800.0
library = unreal.EditorAssetLibrary
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []

blueprint = unreal.load_asset(BLUEPRINT_PATH)
handles = {}
for handle in subsystem.k2_gather_subobject_data_for_blueprint(blueprint):
    component = data_library.get_object(data_library.get_data(handle))
    if component is not None:
        handles[component.get_name().replace("_GEN_VARIABLE", "")] = (handle, component)
root = subsystem.k2_gather_subobject_data_for_blueprint(blueprint)[0]

if "Area" not in handles:
    params = unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.BoxComponent, blueprint_context=blueprint)
    handle, _ = subsystem.add_new_subobject(params)
    subsystem.rename_subobject(handle, unreal.Text("Area"))
    area = data_library.get_object(data_library.get_data(handle))
    area.set_editor_property("box_extent", unreal.Vector(HALF_SIZE, HALF_SIZE, HALF_SIZE))
    area.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, HALF_SIZE))
    # Outline shown in game while this is a trial, in the sun's orange.
    area.set_editor_property("hidden_in_game", False)
    area.set_editor_property("line_thickness", 4.0)
    area.set_editor_property("shape_color", unreal.Color(r=255, g=140, b=40, a=255))
    lines.append("BP_Sun: Area added")
if "Platform" not in handles:
    params = unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.BoxComponent, blueprint_context=blueprint)
    handle, _ = subsystem.add_new_subobject(params)
    subsystem.rename_subobject(handle, unreal.Text("Platform"))
    platform = data_library.get_object(data_library.get_data(handle))
    platform.set_editor_property("box_extent", PLATFORM_EXTENT)
    platform.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, HOME_HEIGHT + PLATFORM_ABOVE))
    platform.set_collision_profile_name("BlockAllDynamic")   # Begin Play turns it off until the sun stays.
    lines.append("BP_Sun: Platform added")
handles["SunMesh"][1].set_editor_property("relative_location", unreal.Vector(0.0, 0.0, HOME_HEIGHT))
if "SunFire" in handles and subsystem.attach_subobject(handles["SunMesh"][0], handles["SunFire"][0]):
    lines.append("BP_Sun: SunFire attached to SunMesh")

variables = [(name, pins.get_basic_type_by_name("real"), True) for name in SETTINGS] + [
    (name, pins.get_basic_type_by_name("int"), True) for name in INT_SETTINGS] + [
    ("Anger", pins.get_basic_type_by_name("int"), False),
    ("BodyMaterial", pins.get_object_reference_type(unreal.MaterialInstanceDynamic), False),
    ("Phase", pins.get_basic_type_by_name("int"), False),          # 0 waiting, 1 aim, 2 charge, 3 stay, 4 rise back
    ("PhaseTime", pins.get_basic_type_by_name("real"), False),
    ("Target", pins.get_struct_type(unreal.Vector.static_struct()), False),
    ("ChargeFrom", pins.get_struct_type(unreal.Vector.static_struct()), False),
    ("HomeLocation", pins.get_struct_type(unreal.Vector.static_struct()), False),
    ("HitDone", pins.get_basic_type_by_name("bool"), False),
]
defaults = unreal.get_default_object(blueprint.generated_class())
for name, pin_type, editable in variables:
    # add_member_variable would quietly add Name_0 next to an existing one, so check first.
    try:
        defaults.get_editor_property(name)
        continue
    except Exception:
        pass
    if not pins.add_member_variable(blueprint, name, pin_type):
        raise RuntimeError("Could not add " + name)
    if editable:
        pins.set_blueprint_variable_instance_editable(blueprint, name, True)
    lines.append("  variable " + name)
pins.compile_blueprint(blueprint)
defaults = unreal.get_default_object(blueprint.generated_class())
for name, value in list(SETTINGS.items()) + list(INT_SETTINGS.items()):
    defaults.set_editor_property(name, value)
library.save_asset(BLUEPRINT_PATH, False)

level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if not world or world.get_name() != "LV_Debug":
    if not level.load_level("/Game/LV_Debug"):
        raise RuntimeError("Could not open LV_Debug")
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
existing = actors.get_all_level_actors()
labels = {a.get_actor_label(): a for a in existing}
if "Sun Face" in labels:
    actors.destroy_actor(labels.pop("Sun Face"))  # From the first, sky-placed version of place_sun.py.
suns = [a for a in existing if a.get_class().get_name().startswith("BP_Sun")]
sun = suns[0] if suns else actors.spawn_actor_from_class(blueprint.generated_class(), unreal.Vector(SUN_X, 0.0, 0.0))
sun.set_actor_label("Sun")
# On the ground, unturned and unscaled: the Area's floor on the floor, the ball HOME_HEIGHT up.
sun.set_actor_location_and_rotation(unreal.Vector(SUN_X, 0.0, 0.0), unreal.Rotator(0.0, 0.0, 0.0), False, False)
sun.set_actor_scale3d(unreal.Vector(1.0, 1.0, 1.0))
label = labels.get("Label Sun") or actors.spawn_actor_from_class(unreal.TextRenderActor, unreal.Vector(0.0, 0.0, 0.0))
label.set_actor_label("Label Sun")
# Like the Time Rewind Area's: just in front of the box, facing the PlayerStart side.
label.set_actor_location_and_rotation(unreal.Vector(SUN_X - HALF_SIZE - 20.0, 0.0, 320.0), unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0), False, False)
text = label.get_editor_property("text_render")
text.set_text(unreal.Text("Sun"))
text.set_editor_property("world_size", 50.0)
text.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)
for name in ("Goal", "Label Goal"):
    location = labels[name].get_actor_location()
    labels[name].set_actor_location(unreal.Vector(GOAL_X, location.y, location.z), False, False)
floor = labels["Floor"]
floor_start = -1600.0  # As build_debug_level.py: two steps behind the first gimmick.
floor.set_actor_location(unreal.Vector((floor_start + FLOOR_END) / 2.0, 0.0, -50.0), False, False)
floor.set_actor_scale3d(unreal.Vector((FLOOR_END - floor_start) / 100.0, 16.0, 1.0))
if not any("EffekseerSystem" in a.get_class().get_name() for a in existing):
    system_class = unreal.load_asset("/Effekseer/BluePrints/BP_EffekseerSystem").generated_class()
    actors.spawn_actor_from_class(system_class, unreal.Vector(0.0, 0.0, 0.0)).set_actor_label("Effekseer System")
    lines.append("LV_Debug: BP_EffekseerSystem added")
lines.append("LV_Debug: sun at x {}, goal at x {}, floor to x {}".format(SUN_X, GOAL_X, FLOOR_END))
lines.append("LV_Debug saved {}".format(level.save_current_level()))
with open(os.path.join(unreal.Paths.project_saved_dir(), "sun_charge_setup.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
