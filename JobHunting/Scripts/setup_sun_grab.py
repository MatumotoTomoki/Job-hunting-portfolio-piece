# Prepares BP_Sun for the grab in BP_Sun_EventGraph.txt (phases 5-11): when the sun is at full anger, GrabChance of its
# charges grab the player instead of knocking them back. The player is laid on the sun's back, flailing; a black
# birdcage drops beside the sun, opens, the player is thrown in, it shuts, burns and fades away, and the player is
# back at the level's PlayerStart. What it sets up:
#   BP_Sun   TrapCage, the black birdcage (SK_Birdcage with the black materials of make_black_birdcage.py, door
#            animation loaded but still, CageScale times its size, no collision, hidden until used) and TrapFire, the
#            CageFire effect on it (import_cage_fire.py; plays only while the cage burns). The grab's variables.
#   LV_Debug the placed sun's RespawnPoint: the level's PlayerStart.
# Safe to run again. Run after setup_sun_charge.py, with the editor closed:
#   UnrealEditor-Cmd.exe JobHunting.uproject -run=pythonscript -script=setup_sun_grab.py -unattended -nop4 -nosplash -stdout
import os

import unreal

BLUEPRINT_PATH = "/Game/ThirdPerson/Blueprints/Gimmicks/Sun/BP_Sun"
CAGE_DIR = "/Game/Prototype/Birdcage"
CAGE_FIRE = "/Game/FX/Effekseer/CageFire/CageFire"
FLAIL_ANIM = "/Game/ThirdPerson/Blueprints/Plaey/Anim/MM_Fall_Handmade"   # The player's own fall loop.
CAGE_SCALE = 2.0   # The cage is 69 cm wide and 112 cm tall; the player is 180 cm.
# Per placed sun: the chance a full-anger charge grabs; how much brighter such a charge glows (the warning); seconds to
# lift the player home, drop the cage, open its door, throw, shut it, burn the cage away and fade the screen; how
# high the cage drops from; how high the throw arcs; how high the player lies above the ball's centre; how far the
# player is turned onto their back (-90 if they end up face down); where the cage lands, from the actor.
SETTINGS = {
    "GrabChance": 0.5, "GrabGlowBoost": 2.5,
    "LiftSeconds": 1.2, "DropSeconds": 0.8, "DoorSeconds": 0.8, "ThrowSeconds": 0.8, "CloseSeconds": 0.8,
    "BurnSeconds": 2.0, "FadeSeconds": 0.6,
    "DropHeight": 1200.0, "ThrowArc": 250.0, "HoldHeight": 80.0, "LieRoll": 90.0,
    "CageOffsetX": -350.0, "CageOffsetY": 0.0,
}
library = unreal.EditorAssetLibrary
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []

blueprint = unreal.load_asset(BLUEPRINT_PATH)


def gather():
    found = {}
    for h in subsystem.k2_gather_subobject_data_for_blueprint(blueprint):
        component = data_library.get_associated_object(data_library.get_data(h))
        if component is not None:
            found[component.get_name().replace("_GEN_VARIABLE", "")] = (h, component)
    return found


def add(parent_handle, component_class, name):
    params = unreal.AddNewSubobjectParams(parent_handle=parent_handle, new_class=component_class, blueprint_context=blueprint)
    handle, _ = subsystem.add_new_subobject(params)
    subsystem.rename_subobject(handle, unreal.Text(name))
    lines.append("BP_Sun: {} added".format(name))
    return handle, data_library.get_associated_object(data_library.get_data(handle))


root = subsystem.k2_gather_subobject_data_for_blueprint(blueprint)[0]
components = gather()
cage_mesh = unreal.load_asset(CAGE_DIR + "/SK_Birdcage")
door = unreal.load_asset(CAGE_DIR + "/SK_Birdcage_Anim")
brass = unreal.load_asset(CAGE_DIR + "/M_Birdcage_Brass_Black")
wood = unreal.load_asset(CAGE_DIR + "/M_Birdcage_Wood_Black")
if "TrapCage" in components:
    cage_handle, cage = components["TrapCage"]
else:
    cage_handle, cage = add(root, unreal.SkeletalMeshComponent, "TrapCage")
cage.set_editor_property("skeletal_mesh_asset", cage_mesh)
cage.set_editor_property("override_materials", [wood if "wood" in str(s.get_editor_property("material_slot_name")).lower() else brass for s in cage_mesh.get_editor_property("materials")])
cage.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
play_data = cage.get_editor_property("animation_data")
play_data.set_editor_property("anim_to_play", door)
play_data.set_editor_property("saved_looping", False)
play_data.set_editor_property("saved_playing", False)
cage.set_editor_property("animation_data", play_data)
cage.set_editor_property("relative_scale3d", unreal.Vector(CAGE_SCALE, CAGE_SCALE, CAGE_SCALE))
cage.set_collision_profile_name("NoCollision")
cage.set_editor_property("visible", False)
door_seconds = door.get_play_length()
lines.append("door animation {:.2f} s".format(door_seconds))

components = gather()
if "TrapFire" in components:
    fire = components["TrapFire"][1]
else:
    _, fire = add(cage_handle, unreal.load_class(None, "/Script/Effekseer.EffekseerEmitterComponent"), "TrapFire")
fire.set_editor_property("Effect", unreal.load_asset(CAGE_FIRE))
fire.set_editor_property("IsLooping", True)
fire.set_editor_property("auto_activate", False)

variables = [(name, pins.get_basic_type_by_name("real"), True) for name in SETTINGS] + [
    ("RespawnPoint", pins.get_object_reference_type(unreal.Actor), True),
    ("FlailAnim", pins.get_object_reference_type(unreal.AnimationAsset), True),
    ("GrabCharge", pins.get_basic_type_by_name("bool"), False),
    ("ThrowFrom", pins.get_struct_type(unreal.Vector.static_struct()), False),
    ("CageGround", pins.get_struct_type(unreal.Vector.static_struct()), False),
    ("CageTop", pins.get_struct_type(unreal.Vector.static_struct()), False),
    ("MeshRest", pins.get_struct_type(unreal.Transform.static_struct()), False),
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
# The door's open and shut waits follow its animation.
settings = dict(SETTINGS, DoorSeconds=door_seconds + 0.1, CloseSeconds=door_seconds + 0.1)
for name, value in settings.items():
    defaults.set_editor_property(name, value)
defaults.set_editor_property("FlailAnim", unreal.load_asset(FLAIL_ANIM))
library.save_asset(BLUEPRINT_PATH, False)

level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not level.load_level("/Game/LV_Debug"):
    raise RuntimeError("Could not open LV_Debug")
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
start = next((a for a in actors if isinstance(a, unreal.PlayerStart)), None)
for sun in [a for a in actors if a.get_class().get_name().startswith("BP_Sun")]:
    sun.set_editor_property("RespawnPoint", start)
    lines.append("LV_Debug: {} returns players to {}".format(sun.get_actor_label(), start.get_actor_label() if start else None))
lines.append("LV_Debug saved {}".format(level.save_current_level()))
with open(os.path.join(unreal.Paths.project_saved_dir(), "sun_grab_setup.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
