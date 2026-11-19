# Area 2 -> 3 (the user, 2026-11-18): a steam catapult on top of the machine tower shoots the player into the sky,
# and they drop out of the clouds onto area 3's cloud harbour.
#   BP_SteamCatapult (Gimmicks/Area), area 2's exit: an iron base with four bronze steam vents, a bronze pad on a
#     piston with a gold ring. Step onto the ring: held still (no pause either), a clunk, the pad sinks as steam
#     jets from the vents and the pressure sound climbs; then BOOM - the pad kicks up, the player is launched
#     straight up (LaunchCharacter), a column of steam, the screen goes white (into the clouds), the item effects
#     are saved, ChangingArea and CatapultArrival are set and NextLevel opens.
#   BP_SkyLanding (Gimmicks/Area), on area 3's start: only after the catapult (the game instance's CatapultArrival):
#     the screen clears from white, the player starts DropHeight up and falls on lighter gravity (FallGravity),
#     held still; on landing a puff of cloud and a soft thump, gravity back, input back.
#   Effects /Game/FX/Effekseer/Catapult (build_catapult_effect.ps1): CatapultCharge (loop), CatapultBlast;
#     landing uses GearSteamBurst. Sounds (make_catapult_sounds.ps1): S_CatapultCharge, S_CatapultBoom, S_CloudLand.
#   BP_MyGameInstance: CatapultArrival.
#   LV_Area2_Tower: the old BP_AreaExit under the gate gives way to the catapult 11 m further on (clear of the gate's
#     lintel); LV_Area3_Sky: BP_SkyLanding at the PlayerStart.
# Graphs: BP_SteamCatapult_EventGraph.txt, BP_SkyLanding_EventGraph.txt (Generators/gen_steam_catapult.ps1).
# Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_steam_catapult.py -unattended -nop4 -nosplash -stdout
import os

import unreal

AREA = "/Game/ThirdPerson/Blueprints/Gimmicks/Area"
FX = "/Game/FX/Effekseer/Catapult"
TOWER = "/Game/Art/Tower"
GAME_INSTANCE = "/Game/ThirdPerson/Blueprints/BP_MyGameInstance"
PROJECT = os.path.abspath(unreal.Paths.project_dir())
FX_SOURCE = os.path.join(PROJECT, "SourceArt", "Effects", "Catapult")
SOUND_SOURCE = os.path.join(PROJECT, "SourceArt", "Sounds")
CYLINDER = "/Engine/BasicShapes/Cylinder"
BEYOND_GATE = 1100.0     # how far past the old exit (under the gate) the catapult stands

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
TYPES = {"bool": pins.get_basic_type_by_name("bool"), "real": pins.get_basic_type_by_name("real"),
         "name": pins.get_basic_type_by_name("name")}
lines = []


def import_file(path, destination, replace=True):
    asset_path = destination + "/" + os.path.splitext(os.path.basename(path))[0]
    if library.does_asset_exist(asset_path) and not replace:
        return unreal.load_asset(asset_path)
    task = unreal.AssetImportTask()
    task.filename = path
    task.destination_path = destination
    task.automated = True
    task.save = True
    task.replace_existing = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    lines.append("imported " + asset_path)
    return unreal.load_asset(asset_path)


# ----- effects and sounds -----
import_file(os.path.join(FX_SOURCE, "Texture", "SteamPuff.png"), FX + "/Texture", replace=False)
charge_fx = import_file(os.path.join(FX_SOURCE, "CatapultCharge.efk"), FX)
blast_fx = import_file(os.path.join(FX_SOURCE, "CatapultBlast.efk"), FX)
land_fx = unreal.load_asset("/Game/FX/Effekseer/GearSteam/GearSteamBurst")
sounds = {}
for name in ("S_CatapultCharge", "S_CatapultBoom", "S_CloudLand"):
    sounds[name] = import_file(os.path.join(SOUND_SOURCE, name + ".wav"), AREA)
sounds["S_GearClunk"] = unreal.load_asset(AREA + "/S_GearClunk")

# ----- the game instance's flag -----
gi_bp = unreal.load_asset(GAME_INSTANCE)
try:
    unreal.get_default_object(gi_bp.generated_class()).get_editor_property("CatapultArrival")
except Exception:
    if not pins.add_member_variable(gi_bp, "CatapultArrival", TYPES["bool"]):
        raise RuntimeError("Could not add CatapultArrival")
    pins.compile_blueprint(gi_bp)
    library.save_asset(GAME_INSTANCE, False)
    lines.append("BP_MyGameInstance: CatapultArrival added")


def actor_blueprint(name):
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


def add(bp, component_class, name, parent=None):
    found = gather(bp)
    if name in found:
        return found[name][1], False
    parent_handle = found[parent][0] if parent else found["DefaultSceneRoot"][0] if "DefaultSceneRoot" in found else subsystem.k2_gather_subobject_data_for_blueprint(bp)[0]
    params = unreal.AddNewSubobjectParams(parent_handle=parent_handle, new_class=component_class, blueprint_context=bp)
    handle, _ = subsystem.add_new_subobject(params)
    subsystem.rename_subobject(handle, unreal.Text(name))
    lines.append("{}: component {}".format(bp.get_name(), name))
    return data_library.get_associated_object(data_library.get_data(handle)), True


def shape(component, mesh, material, location, scale, collide):
    component.set_editor_property("static_mesh", unreal.load_asset(mesh))
    component.set_material(0, material)
    component.set_editor_property("relative_location", location)
    component.set_editor_property("relative_scale3d", scale)
    component.set_collision_profile_name("BlockAll" if collide else "NoCollision")


def variables(bp, items):
    defaults = unreal.get_default_object(bp.generated_class())
    for name, kind, editable, value in items:
        try:
            defaults.get_editor_property(name)
        except Exception:
            if not pins.add_member_variable(bp, name, TYPES[kind]):
                raise RuntimeError("Could not add " + name)
            if editable:
                pins.set_blueprint_variable_instance_editable(bp, name, True)
            lines.append("{}: variable {}".format(bp.get_name(), name))
    pins.compile_blueprint(bp)
    defaults = unreal.get_default_object(bp.generated_class())
    for name, kind, editable, value in items:
        if value is not None:
            defaults.set_editor_property(name, value)


def emitter(bp, name, effect, location, looping, parent=None):
    component, made = add(bp, unreal.load_class(None, "/Script/Effekseer.EffekseerEmitterComponent"), name, parent)
    component.set_editor_property("relative_location", location)
    component.set_editor_property("Effect", effect)
    component.set_editor_property("IsLooping", looping)
    component.set_editor_property("auto_activate", False)


def audio(bp, name, sound):
    component, made = add(bp, unreal.AudioComponent, name)
    component.set_editor_property("sound", sound)
    component.set_editor_property("auto_activate", False)
    component.set_editor_property("allow_spatialization", False)


iron = unreal.load_asset(TOWER + "/MI_TowerIron")
bronze = unreal.load_asset(TOWER + "/MI_TowerBronze")
gold = unreal.load_asset(AREA + "/MI_GearExitGold")

# ----- BP_SteamCatapult -----
cat = actor_blueprint("BP_SteamCatapult")
add(cat, unreal.SceneComponent, "DefaultSceneRoot")
base, made = add(cat, unreal.StaticMeshComponent, "Base")
shape(base, CYLINDER, iron, unreal.Vector(0.0, 0.0, 25.0), unreal.Vector(5.6, 5.6, 0.5), True)
for k in range(4):
    import math
    a = math.radians(45.0 + 90.0 * k)
    vent, made = add(cat, unreal.StaticMeshComponent, "Vent{}".format(k))
    shape(vent, CYLINDER, bronze, unreal.Vector(280.0 * math.cos(a), 280.0 * math.sin(a), 60.0), unreal.Vector(0.6, 0.6, 1.2), True)
add(cat, unreal.SceneComponent, "Piston")
found = gather(cat)
found["Piston"][1].set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 50.0))
pad, made = add(cat, unreal.StaticMeshComponent, "Pad", "Piston")
shape(pad, CYLINDER, bronze, unreal.Vector(0.0, 0.0, 15.0), unreal.Vector(4.0, 4.0, 0.3), True)
ring, made = add(cat, unreal.StaticMeshComponent, "Ring", "Piston")
shape(ring, CYLINDER, gold, unreal.Vector(0.0, 0.0, 31.0), unreal.Vector(1.4, 1.4, 0.02), False)
ring.set_editor_property("cast_shadow", False)
trigger, made = add(cat, unreal.BoxComponent, "PadTrigger", "Piston")
trigger.set_editor_property("box_extent", unreal.Vector(30.0, 30.0, 60.0))
trigger.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 90.0))
trigger.set_collision_profile_name("OverlapOnlyPawn")
emitter(cat, "ChargeFx", charge_fx, unreal.Vector(0.0, 0.0, 30.0), True)
emitter(cat, "BlastFx", blast_fx, unreal.Vector(0.0, 0.0, 80.0), False)
audio(cat, "ClunkSound", sounds["S_GearClunk"])
audio(cat, "ChargeSound", sounds["S_CatapultCharge"])
audio(cat, "BoomSound", sounds["S_CatapultBoom"])
variables(cat, [
    ("NextLevel", "name", True, None), ("Started", "bool", False, None), ("StartedAt", "real", False, None),
    ("Launched", "bool", False, None), ("Leaving", "bool", False, None),
    ("ChargeSeconds", "real", True, 1.5), ("CompressDepth", "real", True, 25.0), ("PadKick", "real", True, 60.0),
    ("LaunchSpeed", "real", True, 3200.0), ("FadeAfter", "real", True, 0.35),
])
library.save_asset(AREA + "/BP_SteamCatapult", False)

# ----- BP_SkyLanding -----
land = actor_blueprint("BP_SkyLanding")
add(land, unreal.SceneComponent, "DefaultSceneRoot")
icon, made = add(land, unreal.BillboardComponent, "Icon")
emitter(land, "LandFx", land_fx, unreal.Vector(0.0, 0.0, 0.0), False)
audio(land, "LandSound", sounds["S_CloudLand"])
variables(land, [
    ("Falling", "bool", False, None), ("FallAt", "real", False, None), ("OldGravity", "real", False, None),
    ("DropHeight", "real", True, 2500.0), ("FallGravity", "real", True, 0.45),
])
library.save_asset(AREA + "/BP_SkyLanding", False)

# ----- the levels -----
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not level.load_level("/Game/LV_Area2_Tower"):
    raise RuntimeError("Could not open LV_Area2_Tower")
old, placed = None, None
for actor in actors.get_all_level_actors():
    name = actor.get_class().get_name()
    if name == "BP_AreaExit_C":
        old = actor
    elif name == "BP_SteamCatapult_C":
        placed = actor
if old is not None:
    spot = old.get_actor_location()
    spot = unreal.Vector(spot.x + BEYOND_GATE, spot.y, spot.z)
    next_level = old.get_editor_property("NextLevel")
    folder, label = old.get_folder_path(), old.get_actor_label().replace("Exit", "Steam Catapult")
    if placed is not None:
        actors.destroy_actor(placed)
    actors.destroy_actor(old)
    catapult = actors.spawn_actor_from_class(cat.generated_class(), spot, unreal.Rotator(0.0, 0.0, 0.0))
    catapult.set_actor_label(label)
    catapult.set_folder_path(str(folder))
    catapult.set_editor_property("NextLevel", next_level)
    lines.append("area 2: {} at {} -> {}".format(label, spot, next_level))
elif placed is not None:
    lines.append("area 2: kept " + placed.get_actor_label())
else:
    raise RuntimeError("No exit in LV_Area2_Tower")
lines.append("LV_Area2_Tower saved {}".format(level.save_current_level()))

if not level.load_level("/Game/LV_Area3_Sky"):
    raise RuntimeError("Could not open LV_Area3_Sky")
start = None
for actor in actors.get_all_level_actors():
    if actor.get_class().get_name() == "BP_SkyLanding_C":
        actors.destroy_actor(actor)
    elif actor.get_class().get_name() == "PlayerStart":
        start = actor
if start is None:
    raise RuntimeError("No PlayerStart in LV_Area3_Sky")
where = start.get_actor_location()
landing = actors.spawn_actor_from_class(land.generated_class(), unreal.Vector(where.x, where.y, where.z - 90.0), unreal.Rotator(0.0, 0.0, 0.0))
landing.set_actor_label("A3 Sky Landing")
landing.set_folder_path(str(start.get_folder_path()))
lines.append("area 3: Sky Landing at the PlayerStart {}".format(where))
lines.append("LV_Area3_Sky saved {}".format(level.save_current_level()))

with open(os.path.join(unreal.Paths.project_saved_dir(), "steam_catapult.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
