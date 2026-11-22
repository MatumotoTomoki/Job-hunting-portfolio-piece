# Hidden area 3's locked light gate (the user, 2026-11-23: "a step more at the goal, not so easy"): the gate stays shut
# until the three light shards hidden off the way (secret3_collapse.py) are all taken.
#   Gimmicks/Area/BP_ShardLock, placed on the light gate by build_secret3_stage.py:
#       Seal (a plane of area 4's MI_HeavenSeal in the gate's opening, no collision), CounterFront / CounterBack ("n / 3"
#       above the gate, one facing each way). Variables Gate (BP_LightGate), Shard1..3 (BP_LightShard), Opened.
#   Graph BP_ShardLock_EventGraph.txt (Generators/gen_shard_lock.ps1): Begin Play - the gate's Tick off (no pillar, no
#   way in). Tick, until Opened - the shards gone (taken) counted, "n / 3" shown; all three: Opened, the gate's Tick on
#   (it works as ever), the seal and the counters gone, a swell of light.
# BP_LightGate itself is not changed. Safe to run again. From the Output Log (Python):
#   exec(open(r'C:\Git\Job-hunting-portfolio-piece\JobHunting\Scripts\setup_shard_lock.py', encoding='utf-8').read())
import os

import unreal

AREA = "/Game/ThirdPerson/Blueprints/Gimmicks/Area"
HEAVEN = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven"
PATH = AREA + "/BP_ShardLock"
library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []

if library.does_asset_exist(PATH):
    bp = unreal.load_asset(PATH)
else:
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    bp = tools.create_asset("BP_ShardLock", AREA, unreal.Blueprint, factory)
    lines.append("created " + PATH)


def add(cls, name):
    found = {}
    for h in subsystem.k2_gather_subobject_data_for_blueprint(bp):
        c = data_library.get_associated_object(data_library.get_data(h))
        if c is not None:
            found[c.get_name().replace("_GEN_VARIABLE", "")] = c
    if name in found:
        return found[name], False
    handle, _ = subsystem.add_new_subobject(unreal.AddNewSubobjectParams(
        parent_handle=subsystem.k2_gather_subobject_data_for_blueprint(bp)[0], new_class=cls, blueprint_context=bp))
    if not data_library.is_handle_valid(handle):
        raise RuntimeError("Could not add " + name)
    subsystem.rename_subobject(handle, unreal.Text(name))
    lines.append("BP_ShardLock: component " + name)
    return data_library.get_associated_object(data_library.get_data(handle)), True


# The gate's opening (area 3's Light Gate: pillars at y -250 and +250 of its middle, 700 high): the seal across it.
seal, made = add(unreal.StaticMeshComponent, "Seal")
seal.set_editor_property("static_mesh", unreal.load_asset("/Engine/BasicShapes/Plane"))
seal.set_material(0, unreal.load_asset(HEAVEN + "/MI_HeavenSeal"))
seal.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 350.0))
seal.set_editor_property("relative_rotation", unreal.Rotator(roll=0.0, pitch=90.0, yaw=0.0))
seal.set_editor_property("relative_scale3d", unreal.Vector(7.0, 3.8, 1.0))
seal.set_collision_profile_name("NoCollision")
seal.set_editor_property("cast_shadow", False)
for name, facing in (("CounterFront", 0.0), ("CounterBack", 180.0)):
    counter, made = add(unreal.TextRenderComponent, name)
    counter.set_editor_property("text", unreal.Text("0 / 3"))
    counter.set_editor_property("world_size", 120.0)
    counter.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)
    counter.set_editor_property("text_render_color", unreal.Color(r=255, g=230, b=170, a=255))
    counter.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 900.0))
    counter.set_editor_property("relative_rotation", unreal.Rotator(roll=0.0, pitch=0.0, yaw=facing))

gate_class = unreal.load_asset(AREA + "/BP_LightGate").generated_class()
shard_class = unreal.load_asset(HEAVEN + "/BP_LightShard").generated_class()
defaults = unreal.get_default_object(bp.generated_class())
for name, pin_type, editable in (("Gate", pins.get_object_reference_type(gate_class), True),
                                 ("Shard1", pins.get_object_reference_type(shard_class), True),
                                 ("Shard2", pins.get_object_reference_type(shard_class), True),
                                 ("Shard3", pins.get_object_reference_type(shard_class), True),
                                 ("Opened", pins.get_basic_type_by_name("bool"), False)):
    try:
        defaults.get_editor_property(name)
        continue
    except Exception:
        pass
    if not pins.add_member_variable(bp, name, pin_type):
        raise RuntimeError("Could not add " + name)
    if editable:
        pins.set_blueprint_variable_instance_editable(bp, name, True)
    lines.append("BP_ShardLock: variable " + name)
pins.compile_blueprint(bp)
library.save_asset(PATH, False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "shard_lock.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(lines) + "\n")
unreal.log("\n".join(lines))
