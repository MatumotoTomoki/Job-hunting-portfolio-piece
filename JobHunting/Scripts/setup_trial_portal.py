# Hidden area 4's trials (the user, 2026-11-23): before the crumbling gate, four gold footings in a row. Stepping on
# one raises a pillar of light that carries the player off to a small area (ruins, tower, sky, heaven); the light shard
# at its far end carries them back to the footing, and the next footing appears.
#   Gimmicks/Area/BP_TrialPortal (its origin = the footing's top middle):
#       Footing   a thin 400 x 400 gold seal on the island's top (no collision)
#       Touch     a box on the footing (overlaps the player)
#       Pillar    a pillar of light (MI_SmashPillar, no collision), hidden until a trip
#       Glow      a warm point light
#   Variables: Destination (Actor: where the small area starts), Shard (BP_LightShard at its end), Prev (BP_TrialPortal:
#       if set, this footing is hidden and not solid until Prev is Done), Flag (Actor: the checkpoint flag on this footing,
#       hidden with it), Started, Done, Shown.
#   Graph BP_TrialPortal_EventGraph.txt (Generators/gen_trial_portal.ps1).
# Safe to run again. From the Output Log (Python), or as a commandlet:
#   exec(open(r'C:\Git\Job-hunting-portfolio-piece\JobHunting\Scripts\setup_trial_portal.py', encoding='utf-8').read())
import os

import unreal

AREA = "/Game/ThirdPerson/Blueprints/Gimmicks/Area"
HEAVEN = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven"
PATH = AREA + "/BP_TrialPortal"
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
    bp = tools.create_asset("BP_TrialPortal", AREA, unreal.Blueprint, factory)
    lines.append("created " + PATH)


def add(cls, name):
    found = {}
    for h in subsystem.k2_gather_subobject_data_for_blueprint(bp):
        c = data_library.get_associated_object(data_library.get_data(h))
        if c is not None:
            found[c.get_name().replace("_GEN_VARIABLE", "")] = c
    if name in found:
        return found[name]
    handle, _ = subsystem.add_new_subobject(unreal.AddNewSubobjectParams(
        parent_handle=subsystem.k2_gather_subobject_data_for_blueprint(bp)[0], new_class=cls, blueprint_context=bp))
    if not data_library.is_handle_valid(handle):
        raise RuntimeError("Could not add " + name)
    subsystem.rename_subobject(handle, unreal.Text(name))
    lines.append("BP_TrialPortal: component " + name)
    return data_library.get_associated_object(data_library.get_data(handle))


footing = add(unreal.StaticMeshComponent, "Footing")
footing.set_editor_property("static_mesh", unreal.load_asset("/Engine/BasicShapes/Cube"))
footing.set_material(0, unreal.load_asset("/Game/ThirdPerson/Blueprints/Gimmicks/Sky/MI_SkyGold"))
# A thin gold seal laid on the island's top (the island itself carries the player; 11-23 the user wanted area 4's
# islands and updrafts kept as they are).
footing.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 0.0))
footing.set_editor_property("relative_scale3d", unreal.Vector(4.0, 4.0, 0.06))
footing.set_collision_profile_name("NoCollision")
footing.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)

touch = add(unreal.BoxComponent, "Touch")
touch.set_editor_property("box_extent", unreal.Vector(280.0, 280.0, 80.0))
touch.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 80.0))
touch.set_collision_profile_name("OverlapAllDynamic")
touch.set_editor_property("generate_overlap_events", True)
touch.set_editor_property("hidden_in_game", True)
touch.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)

pillar = add(unreal.StaticMeshComponent, "Pillar")
pillar.set_editor_property("static_mesh", unreal.load_asset("/Engine/BasicShapes/Cylinder"))
pillar.set_material(0, unreal.load_asset(AREA + "/MI_SmashPillar"))
pillar.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 2500.0))
pillar.set_editor_property("relative_scale3d", unreal.Vector(3.0, 3.0, 50.0))
pillar.set_collision_profile_name("NoCollision")
pillar.set_editor_property("cast_shadow", False)
pillar.set_editor_property("visible", False)
pillar.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)

glow = add(unreal.PointLightComponent, "Glow")
glow.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 250.0))
glow.set_editor_property("intensity", 4000.0)
glow.set_editor_property("attenuation_radius", 900.0)
glow.set_editor_property("light_color", unreal.Color(r=255, g=225, b=160, a=255))
glow.set_editor_property("cast_shadows", False)
glow.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)

shard_class = unreal.load_asset(HEAVEN + "/BP_LightShard").generated_class()
defaults = unreal.get_default_object(bp.generated_class())
for name, pin_type, editable in (("Destination", pins.get_object_reference_type(unreal.Actor), True),
                                 ("Shard", pins.get_object_reference_type(shard_class), True),
                                 ("Prev", pins.get_object_reference_type(bp.generated_class()), True),
                                 ("Flag", pins.get_object_reference_type(unreal.Actor), True),
                                 ("Wind", pins.get_object_reference_type(unreal.Actor), True),
                                 ("Started", pins.get_basic_type_by_name("bool"), False),
                                 ("Done", pins.get_basic_type_by_name("bool"), False),
                                 ("Shown", pins.get_basic_type_by_name("bool"), False)):
    try:
        defaults.get_editor_property(name)
        continue
    except Exception:
        pass
    if not pins.add_member_variable(bp, name, pin_type):
        raise RuntimeError("Could not add " + name)
    if editable:
        pins.set_blueprint_variable_instance_editable(bp, name, True)
    lines.append("BP_TrialPortal: variable " + name)
pins.compile_blueprint(bp)
library.save_asset(PATH, False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "trial_portal.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(lines) + "\n")
unreal.log("\n".join(lines))
