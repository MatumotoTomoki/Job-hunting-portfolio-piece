# Hidden area 2's arrival show and its way out (the user, 2026-11-22). Area 2's own blueprints are not changed.
#   Gimmicks/Area/BP_CatapultSmash  placed on the doomed catapult (build_secret2_stage.py sets Catapult, Respawn).
#       A few seconds into the level the view cuts to ShowCamera: the sun's target ring (Marker, area 4's MI_SunSigil)
#       spreads on the catapult and charges, a pillar of light (Pillar) drops onto it - a blast (ImpactFx, area 4's
#       SunImpact), the catapult gone, its wreck (Wreck1..4) left - and the pillar stays. It looks like the goal;
#       walking into it (Trap) whites the screen out and puts the player back at Respawn.
#       Variables Catapult, Respawn, Arrival (instance editable), StartDelay (4), Started, StartedAt, Smashed, Busy.
#       It waits for Arrival (the BP_GearArrival bringing the player up) to finish first (2026-11-22: the two shows clashed).
#       Lever (the hidden lever, 2026-11-22: the doomed catapult stands at the goal): once pulled, the pillar goes out and
#       the trap stops (Busy for good) - the real catapult comes up there (BP_ActorRiser).
#   Gimmicks/Area/BP_ActorRiser     raises Target by RiseOffset over RiseSeconds once Lever is pulled (BP_Lever's
#       Pulled), with a rumble. Variables Lever, Target, RiseOffset, RiseSeconds (instance editable), Started,
#       StartedAt, StartLocation.
# Graphs: BP_CatapultSmash_EventGraph.txt, BP_ActorRiser_EventGraph.txt (Generators/gen_catapult_smash.ps1).
# Safe to run again. From the Output Log (Python):
#   exec(open(r'C:\Git\Job-hunting-portfolio-piece\JobHunting\Scripts\setup_catapult_smash.py', encoding='utf-8').read())
import os

import unreal

AREA = "/Game/ThirdPerson/Blueprints/Gimmicks/Area"
HEAVEN = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven"
MACHINE = "/Game/ThirdPerson/Blueprints/Gimmicks/Machine"
library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []
TYPES = {"bool": pins.get_basic_type_by_name("bool"), "real": pins.get_basic_type_by_name("real"),
         "vector": pins.get_struct_type(unreal.Vector.static_struct()),
         "actor": pins.get_object_reference_type(unreal.Actor.static_class())}
emitter_class = unreal.load_class(None, "/Script/Effekseer.EffekseerEmitterComponent")
lever_class = unreal.load_asset(AREA + "/BP_Lever").generated_class()
TYPES["lever"] = pins.get_object_reference_type(lever_class)
TYPES["arrival"] = pins.get_object_reference_type(unreal.load_asset(AREA + "/BP_GearArrival").generated_class())


def blueprint(name):
    path = AREA + "/" + name
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    lines.append("created " + path)
    return tools.create_asset(name, AREA, unreal.Blueprint, factory)


def gather(bp):
    found = {}
    for h in subsystem.k2_gather_subobject_data_for_blueprint(bp):
        c = data_library.get_associated_object(data_library.get_data(h))
        if c is not None:
            found[c.get_name().replace("_GEN_VARIABLE", "")] = (h, c)
    return found


def add(bp, component_class, name):
    found = gather(bp)
    if name in found:
        return found[name][1], False
    root = found["DefaultSceneRoot"][0] if "DefaultSceneRoot" in found else subsystem.k2_gather_subobject_data_for_blueprint(bp)[0]
    handle, _ = subsystem.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root, new_class=component_class, blueprint_context=bp))
    if not data_library.is_handle_valid(handle):
        raise RuntimeError("Could not add " + name)
    subsystem.rename_subobject(handle, unreal.Text(name))
    lines.append("{}: component {}".format(bp.get_name(), name))
    return data_library.get_associated_object(data_library.get_data(handle)), True


def variables(bp, spec):
    defaults = unreal.get_default_object(bp.generated_class())
    for name, kind, editable in spec:
        try:
            defaults.get_editor_property(name)
            continue
        except Exception:
            pass
        if not pins.add_member_variable(bp, name, TYPES[kind]):
            raise RuntimeError("Could not add " + name)
        if editable:
            pins.set_blueprint_variable_instance_editable(bp, name, True)
        lines.append("{}: variable {}".format(bp.get_name(), name))
    pins.compile_blueprint(bp)
    return unreal.get_default_object(bp.generated_class())


def mesh(bp, name, shape, material, where, scale, rotation=None, hidden=False):
    part, made = add(bp, unreal.StaticMeshComponent, name)
    if made:
        part.set_editor_property("static_mesh", unreal.load_asset("/Engine/BasicShapes/" + shape))
        part.set_material(0, material)
        part.set_editor_property("relative_location", where)
        part.set_editor_property("relative_scale3d", scale)
        if rotation is not None:
            part.set_editor_property("relative_rotation", rotation)
        part.set_collision_profile_name("NoCollision")
        part.set_editor_property("cast_shadow", False)
        part.set_editor_property("visible", not hidden)
    return part


# ----- BP_CatapultSmash -----
smash = blueprint("BP_CatapultSmash")
sigil = unreal.load_asset(HEAVEN + "/MI_SunSigil")
shaft = unreal.load_asset(HEAVEN + "/MI_LightShaft")
iron = unreal.load_asset(MACHINE + "/MI_MachineIron")
if not (sigil and shaft and iron):
    raise RuntimeError("MI_SunSigil / MI_LightShaft / MI_MachineIron missing")
mesh(smash, "Marker", "Plane", sigil, unreal.Vector(0.0, 0.0, 8.0), unreal.Vector(6.0, 6.0, 1.0), hidden=True)
# The pillar glows all the way down (MI_LightShaft fades out towards its foot, so on the spire it could not be seen,
# the user 2026-11-22): MI_SmashPillar, Hell's M_HellGlow in a warm white.
glow_parent = unreal.load_asset("/Game/ThirdPerson/Blueprints/Gimmicks/Hell/M_HellGlow")
pillar_mi_path = AREA + "/MI_SmashPillar"
if library.does_asset_exist(pillar_mi_path):
    pillar_mi = unreal.load_asset(pillar_mi_path)
else:
    pillar_mi = tools.create_asset("MI_SmashPillar", AREA, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    lines.append("created " + pillar_mi_path)
editing = unreal.MaterialEditingLibrary
editing.set_material_instance_parent(pillar_mi, glow_parent)
editing.set_material_instance_vector_parameter_value(pillar_mi, "Color", unreal.LinearColor(1.0, 0.85, 0.55, 1.0))
editing.set_material_instance_scalar_parameter_value(pillar_mi, "Glow", 8.0)
library.save_asset(pillar_mi_path, False)
pillar = mesh(smash, "Pillar", "Cylinder", pillar_mi, unreal.Vector(0.0, 0.0, 11000.0), unreal.Vector(3.0, 3.0, 60.0), hidden=True)
pillar.set_material(0, pillar_mi)
pillar.set_editor_property("relative_scale3d", unreal.Vector(3.0, 3.0, 60.0))
for i, (x, y, z, s, rot) in enumerate(((-120.0, 80.0, 40.0, (1.4, 0.8, 0.6), (20.0, 10.0, 35.0)),
                                       (140.0, -60.0, 30.0, (1.0, 1.2, 0.5), (-15.0, 25.0, 120.0)),
                                       (30.0, 160.0, 25.0, (0.8, 0.6, 0.5), (35.0, -20.0, 200.0)),
                                       (-60.0, -150.0, 50.0, (1.6, 0.5, 0.9), (-30.0, 5.0, 300.0)))):
    mesh(smash, "Wreck{}".format(i + 1), "Cube", iron, unreal.Vector(x, y, z), unreal.Vector(*s),
         unreal.Rotator(roll=rot[0], pitch=rot[1], yaw=rot[2]), hidden=True)
trap, made = add(smash, unreal.BoxComponent, "Trap")
if made:
    trap.set_editor_property("box_extent", unreal.Vector(240.0, 240.0, 300.0))
    trap.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 300.0))
    trap.set_collision_profile_name("OverlapOnlyPawn")
    trap.set_editor_property("hidden_in_game", True)
camera, made = add(smash, unreal.CameraComponent, "ShowCamera")
if made:
    camera.set_editor_property("relative_location", unreal.Vector(-1500.0, -1500.0, 900.0))
    camera.set_editor_property("relative_rotation", unreal.Rotator(roll=0.0, pitch=-18.0, yaw=45.0))
    camera.set_editor_property("field_of_view", 80.0)
fx, made = add(smash, emitter_class, "ImpactFx")
if made:
    fx.set_editor_property("Effect", unreal.load_asset("/Game/FX/Effekseer/SunImpact/SunImpact"))
    fx.set_editor_property("IsLooping", False)
    fx.set_editor_property("auto_activate", False)
    fx.set_editor_property("absolute_scale", True)
    fx.set_editor_property("relative_scale3d", unreal.Vector(4.0, 4.0, 4.0))
    fx.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 30.0))
# Everything movable: the pillar is moved at run time (it stayed up in the sky otherwise, 2026-11-22).
for name, (handle, component) in gather(smash).items():
    if isinstance(component, unreal.SceneComponent):
        component.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
defaults = variables(smash, (("Catapult", "actor", True), ("Respawn", "actor", True), ("Arrival", "arrival", True),
                             ("Lever", "lever", True), ("StartDelay", "real", True),
                             ("Started", "bool", False), ("StartedAt", "real", False), ("Smashed", "bool", False),
                             ("Busy", "bool", False)))
if defaults.get_editor_property("StartDelay") == 0.0:
    defaults.set_editor_property("StartDelay", 4.0)
pins.compile_blueprint(smash)
library.save_asset(AREA + "/BP_CatapultSmash", False)

# ----- BP_ActorRiser -----
riser = blueprint("BP_ActorRiser")
defaults = variables(riser, (("Lever", "lever", True), ("Target", "actor", True), ("RiseOffset", "vector", True),
                             ("RiseSeconds", "real", True), ("Started", "bool", False), ("StartedAt", "real", False),
                             ("StartLocation", "vector", False)))
if defaults.get_editor_property("RiseSeconds") == 0.0:
    defaults.set_editor_property("RiseSeconds", 4.0)
pins.compile_blueprint(riser)
library.save_asset(AREA + "/BP_ActorRiser", False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "catapult_smash.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
