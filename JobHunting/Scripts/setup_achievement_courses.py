# Achievements step 4c: the course achievements in area 4 (Achievements_Plan.md, 2026-11-21).
#   BP_MyGameInstance  FallCount, SunHitCount (int: every fall respawn / tower sun hit this game, counted by the pastes
#                      AchievementHooks/Count_Fall.txt and Count_SunHit.txt); CourseId (Name: the course running),
#                      CourseFalls, CourseHits (int: the counts when it started)
#   Achievements/BP_CourseGate  a box (Box, overlap only, hidden in game) the player walks into. Instance settings:
#                      IsGoal, AchievementId (Name), CheckFalls, CheckSunHits. Sized by the actor's scale (Box is 100
#                      across at scale 1). Its graph is Scripts/BP_CourseGate_EventGraph.txt (Generators/gen_achievement_hooks.ps1).
#   LV_Area4_Heaven    two courses, found from what the level already holds (labels / folders), nothing rebuilt:
#     ACH_MELODY     start on the Forest Floor (where the threads end), goal on shard 1's island: no fall between
#     ACH_SUN_DODGE  start on the landing outside the tower door, goal over the tower roof: no sun hit between (the sun's
#                    catch puts the player back inside the door, past the start, so it cannot reset a run)
# A gate already there (same label) is left alone. Safe to run again. Editor closed, or from the Output Log:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_achievement_courses.py -unattended -nop4 -nosplash -stdout
import os

import unreal

FOLDER = "/Game/ThirdPerson/Blueprints/Achievements"
GATE = FOLDER + "/BP_CourseGate"
GAME_INSTANCE = "/Game/ThirdPerson/Blueprints/BP_MyGameInstance"
LEVEL = "/Game/LV_Area4_Heaven"
SHARD = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven/BP_LightShard"
GATE_TALL = 300.0   # the boxes stand this high over the floor they are on

library = unreal.EditorAssetLibrary
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
INT, BOOL, NAME = (pins.get_basic_type_by_name(t) for t in ("int", "bool", "name"))
lines = []


def add_variables(blueprint, variables):
    # add_member_variable quietly adds Name_0 next to an existing one, so check the CDO first.
    defaults = unreal.get_default_object(blueprint.generated_class())
    for name, pin_type, editable in variables:
        try:
            defaults.get_editor_property(name)
            continue
        except Exception:
            pass
        if not pins.add_member_variable(blueprint, name, pin_type):
            raise RuntimeError("Could not add {} to {}".format(name, blueprint.get_name()))
        if editable:
            pins.set_blueprint_variable_instance_editable(blueprint, name, True)
        lines.append("{}: variable {}".format(blueprint.get_name(), name))
    pins.compile_blueprint(blueprint)


def components(blueprint):
    found = {}
    for handle in subsystem.k2_gather_subobject_data_for_blueprint(blueprint):
        component = data_library.get_associated_object(data_library.get_data(handle))
        if component is not None:
            found[component.get_name().replace("_GEN_VARIABLE", "")] = component
    return found


# ----- the game instance -----
gi_bp = unreal.load_asset(GAME_INSTANCE)
add_variables(gi_bp, [("FallCount", INT, False), ("SunHitCount", INT, False), ("CourseId", NAME, False),
                      ("CourseFalls", INT, False), ("CourseHits", INT, False)])
library.save_asset(GAME_INSTANCE, False)

# ----- BP_CourseGate -----
if library.does_asset_exist(GATE):
    gate_bp = unreal.load_asset(GATE)
else:
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    gate_bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset("BP_CourseGate", FOLDER, unreal.Blueprint, factory)
    lines.append("created " + GATE)
if "Box" not in components(gate_bp):
    root = subsystem.k2_gather_subobject_data_for_blueprint(gate_bp)[0]
    handle, _ = subsystem.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.BoxComponent, blueprint_context=gate_bp))
    if not data_library.is_handle_valid(handle):
        raise RuntimeError("Could not add Box to BP_CourseGate")
    subsystem.rename_subobject(handle, unreal.Text("Box"))
    box = data_library.get_associated_object(data_library.get_data(handle))
    box.set_editor_property("box_extent", unreal.Vector(50.0, 50.0, 50.0))
    box.set_collision_profile_name("OverlapOnlyPawn")
    box.set_editor_property("hidden_in_game", True)
    lines.append("BP_CourseGate: component Box")
add_variables(gate_bp, [("IsGoal", BOOL, True), ("AchievementId", NAME, True), ("CheckFalls", BOOL, True),
                        ("CheckSunHits", BOOL, True)])
library.save_asset(GATE, False)

# ----- the gates in area 4 -----
if not level.load_level(LEVEL):
    raise RuntimeError("Could not open " + LEVEL)
everything = actors.get_all_level_actors()
gate_class = unreal.load_asset(GATE).generated_class()


def labelled(suffix):
    found = [a for a in everything if a.get_actor_label().endswith(suffix)]
    if not found:
        raise RuntimeError("Nothing labelled ... " + suffix)
    return found


def bounds(group):
    lows, highs = [], []
    for a in group:
        origin, extent = a.get_actor_bounds(False)
        lows.append(origin - extent)
        highs.append(origin + extent)
    low = unreal.Vector(min(v.x for v in lows), min(v.y for v in lows), min(v.z for v in lows))
    high = unreal.Vector(max(v.x for v in highs), max(v.y for v in highs), max(v.z for v in highs))
    return low, high


def gate(label, x0, x1, y0, y1, floor, achievement, is_goal, falls, hits):
    if any(a.get_actor_label() == label for a in everything):
        lines.append("{}: already there".format(label))
        return
    where = unreal.Vector((x0 + x1) / 2.0, (y0 + y1) / 2.0, floor + GATE_TALL / 2.0)
    actor = actors.spawn_actor_from_class(gate_class, where, unreal.Rotator(0.0, 0.0, 0.0))
    actor.set_actor_label(label)
    actor.set_folder_path("Area4/Achievements")
    actor.set_actor_scale3d(unreal.Vector((x1 - x0) / 100.0, (y1 - y0) / 100.0, GATE_TALL / 100.0))
    for name, value in (("IsGoal", is_goal), ("AchievementId", achievement), ("CheckFalls", falls), ("CheckSunHits", hits)):
        actor.set_editor_property(name, value)
    lines.append("{}: {:.0f}..{:.0f}, {:.0f}..{:.0f}, floor {:.0f}".format(label, x0, x1, y0, y1, floor))


# Melody: the Forest Floor -> shard 1's island.
low, high = bounds(labelled("Forest Floor"))
gate("A4 Melody Start", low.x, high.x, low.y, high.y, high.z, "ACH_MELODY", False, True, False)
shard_class = unreal.load_asset(SHARD).generated_class()
shard1 = [a for a in everything if a.get_class() == shard_class and a.get_actor_label().endswith("shard1")]
if len(shard1) != 1:
    raise RuntimeError("Expected one Light Shard shard1, found {}".format(len(shard1)))
s = shard1[0].get_actor_location()
gate("A4 Melody Goal", s.x - 400.0, s.x + 400.0, s.y - 400.0, s.y + 400.0, s.z - 120.0, "ACH_MELODY", True, True, False)

# Sun dodge: the landing outside the door -> over the roof.
low, high = bounds(labelled("Tower Floor"))
middle_y = (low.y + high.y) / 2.0
gate("A4 Sun Dodge Start", low.x - 600.0, low.x - 100.0, middle_y - 400.0, middle_y + 400.0, high.z, "ACH_SUN_DODGE", False, False, True)
low, high = bounds(labelled("Tower Roof"))
gate("A4 Sun Dodge Goal", low.x, high.x, low.y, high.y, high.z, "ACH_SUN_DODGE", True, False, True)
lines.append("{} saved {}".format(LEVEL, level.save_current_level()))

with open(os.path.join(unreal.Paths.project_saved_dir(), "setup_achievement_courses.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
