# Builds /Game/LV_Secret4, hidden area 4, the last hidden stage: area 4 itself, collapsed (the user, 2026-11-23).
# LV_Area4_Heaven is copied with save_map (never changed) and each section moved whole by the offsets secret4_collapse.py
# works out (art, collision, gimmicks; 4+5 as one); the stretches between them are added ("S4 ..."). At the end the
# gate's island and the one before it are gone (and the last updraft): a stair of crumbling floors leads up to a pad at
# the gate, section 6's art is SM_SecretHeaven_6 (build_heaven_art_blender.py -- 6 --skip 232,233 --prefix
# SM_SecretHeaven_), and the gate is BP_SecretGate (setup_secret_gate.py: ACH_SECRET_CLEAR, then the title).
# The arrival is area 4's own (hidden area 3's light gate). Area 4's sky, its course gates (main achievements) and its
# fall catcher are taken out. Run with the editor closed (it deletes and re-copies LV_Secret4):
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\build_secret4_stage.py -unattended -nop4 -nosplash -stdout
import math
import os
import random
import sys

import unreal

sys.path.insert(0, os.path.join(os.path.abspath(unreal.Paths.project_dir()), "Scripts"))
import importlib  # noqa: E402
import area3_layout  # noqa: E402
import area4_layout  # noqa: E402
import secret_town  # noqa: E402
import secret_collapse  # noqa: E402
import secret4_collapse  # noqa: E402
for module in (area3_layout, area4_layout, secret_town, secret_collapse, secret4_collapse):
    importlib.reload(module)

LEVEL = "/Game/LV_Secret4"
SOURCE = "/Game/LV_Area4_Heaven"
PARKING = "/Game/LV_Title"
AREA = "/Game/ThirdPerson/Blueprints/Gimmicks/Area"
SKY = "/Game/ThirdPerson/Blueprints/Gimmicks/Sky"
MACHINE = "/Game/ThirdPerson/Blueprints/Gimmicks/Machine"
HEAVEN = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven"
GIMMICKS = "/Game/ThirdPerson/Blueprints/Gimmicks"
HELL = GIMMICKS + "/Hell"
ITEMS = "/Game/ThirdPerson/Item"
COIN = "/Game/ThirdPerson/Coin/StarCoin/BP_StarCoin"
GAME_MODE = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonGameMode"
FALLBACK_CHARACTER = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter1"
CUBE = "/Engine/BasicShapes/Cube"
PREFIX = "S4 "
B = 22610.0                    # area 4's start
MIST = 18500.0                 # the red haze far below
ART_FBX = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Models", "Heaven", "Art", "SM_SecretHeaven_6.fbx")
ART_DIR = "/Game/Art/Heaven/Secret"
# area 4's spots, by the section they stand in
SPOT_SECTION = {"start": "1", "jewel": "2", "flip": "3", "tower door": "4", "tower": "4", "wings": "4"}

library = unreal.EditorAssetLibrary
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []


def bp_class(path):
    asset = unreal.load_asset(path)
    if not asset:
        raise RuntimeError("Missing " + path)
    return asset.generated_class()


def load(path):
    asset = unreal.load_asset(path)
    if not asset:
        raise RuntimeError("Missing " + path)
    return asset


def player_defaults():
    pawn_class = None
    try:
        pawn_class = unreal.get_default_object(unreal.load_asset(GAME_MODE).generated_class()).get_editor_property("default_pawn_class")
    except Exception as error:
        lines.append("game mode pawn not read: {}".format(error))
    if pawn_class is None:
        pawn_class = unreal.load_asset(FALLBACK_CHARACTER).generated_class()
    return unreal.get_default_object(pawn_class)


def elevator_half():
    source = unreal.load_asset(GIMMICKS + "/BP_Elevator")
    for handle in subsystem.k2_gather_subobject_data_for_blueprint(source):
        component = data_library.get_object(data_library.get_data(handle))
        if isinstance(component, unreal.StaticMeshComponent):
            scale = component.get_editor_property("relative_scale3d")
            extent = component.get_editor_property("static_mesh").get_bounds().box_extent
            return unreal.Vector(extent.x * scale.x, extent.y * scale.y, extent.z * scale.z)
    raise RuntimeError("No floor in BP_Elevator")


if not library.does_asset_exist(HEAVEN + "/BP_SecretGate"):
    raise RuntimeError("Missing BP_SecretGate (run setup_secret_gate.py first)")
if not library.does_asset_exist(AREA + "/BP_TrialPortal"):
    raise RuntimeError("Missing BP_TrialPortal (run setup_trial_portal.py first)")
move = player_defaults().get_editor_property("character_movement")
PLAT = elevator_half()
route = secret4_collapse.build(B, move.get_editor_property("jump_z_velocity"), 980.0 * move.get_editor_property("gravity_scale"),
                               move.get_editor_property("max_walk_speed"), 2.0 * PLAT.x)

# ----- section 6's art without the two lost islands (imported before the level is opened) -----
art_mesh = None
if os.path.exists(ART_FBX) and secret4_collapse.REMOVE:   # (11-23: section 6 kept whole - its own art stays)
    unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")   # keep vertex colours
    options = unreal.FbxImportUI()
    options.set_editor_property("import_materials", False)
    options.set_editor_property("import_textures", False)
    mesh_data = options.get_editor_property("static_mesh_import_data")
    mesh_data.set_editor_property("auto_generate_collision", False)
    mesh_data.set_editor_property("combine_meshes", True)
    mesh_data.set_editor_property("generate_lightmap_u_vs", False)
    mesh_data.set_editor_property("vertex_color_import_option", unreal.VertexColorImportOption.REPLACE)
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", ART_FBX)
    task.set_editor_property("destination_path", ART_DIR)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("automated", True)
    task.set_editor_property("save", False)
    task.set_editor_property("options", options)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    art_mesh = unreal.load_asset(ART_DIR + "/SM_SecretHeaven_6")
    for i, slot in enumerate(art_mesh.get_editor_property("static_materials")):
        name = str(slot.get_editor_property("material_slot_name"))
        if name.startswith("M_HeavenArt"):
            art_mesh.set_material(i, unreal.load_asset("/Game/Art/Heaven/MI_HeavenArt" + name[len("M_HeavenArt"):]))
    library.save_asset(ART_DIR + "/SM_SecretHeaven_6", False)
elif secret4_collapse.REMOVE:
    lines.append("SM_SecretHeaven_6.fbx missing: area 4's gate art left (run build_heaven_art_blender.py)")

# ----- the level: a fresh copy of area 4, its sections torn apart -----
# (save_map, then open the copy and check it is what is open: delete + duplicate_asset + load crashed the editor.)
level_subsystem.load_level(PARKING)
if library.does_asset_exist(LEVEL) and not library.delete_asset(LEVEL):
    raise RuntimeError("Could not delete the old " + LEVEL)
if not level_subsystem.load_level(SOURCE):
    raise RuntimeError("Could not open " + SOURCE)
editor_world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if not unreal.EditorLoadingAndSavingUtils.save_map(editor_world, LEVEL):
    raise RuntimeError("Could not save {} as {}".format(SOURCE, LEVEL))
if not level_subsystem.load_level(LEVEL):
    raise RuntimeError("Could not open " + LEVEL)
now_open = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name()
if not now_open.startswith(LEVEL + "."):
    raise RuntimeError("{} is open, not {}: stopped before changing anything".format(now_open, LEVEL))
OFFSETS = route.section_offsets
moved, removed = 0, 0
old_gate, old_art6 = None, None
for actor in actors.get_all_level_actors():
    label, path = actor.get_actor_label(), str(actor.get_folder_path())
    kind = actor.get_class().get_name()
    if (path.startswith("Area4/Sky") or path.startswith("Area4/Achievements") or label in secret4_collapse.REMOVE
            or kind == "BP_FallCatcher_C"):
        actors.destroy_actor(actor)
        removed += 1
        continue
    if kind == "BP_HeavenGate_C":
        section = "6"
        old_gate = actor
    elif path.startswith("Area4/Art") and label[-1:] in OFFSETS:
        section = label[-1]
        if section == "6":
            old_art6 = actor
    elif path.startswith("Area4/Spots") and label.startswith("A4 ") and label.split(" Respawn ", 1)[-1] in SPOT_SECTION:
        section = SPOT_SECTION[label.split(" Respawn ", 1)[-1]]
    elif path.startswith("Area4/") and path[6:7] in OFFSETS:
        section = path[6]
    else:
        continue
    dx, dy, dz = OFFSETS[section]
    if dx or dy or dz:
        where = actor.get_actor_location()
        actor.set_actor_location(unreal.Vector(where.x + dx, where.y + dy, where.z + dz), False, False)
        moved += 1
lines.append("{} copied from {}: {} actors moved, {} taken out".format(LEVEL, SOURCE, moved, removed))

# The gate: BP_SecretGate where area 4's stood.
if old_gate:
    gate = actors.spawn_actor_from_class(bp_class(HEAVEN + "/BP_SecretGate"), old_gate.get_actor_location(), old_gate.get_actor_rotation())
    gate.set_actor_label(PREFIX + "Secret Gate")
    gate.set_folder_path("Area4/Goal")
    actors.destroy_actor(old_gate)
    lines.append("secret gate at {}".format(gate.get_actor_location()))
else:
    lines.append("no BP_HeavenGate found: no secret gate placed")
# Section 6's art without the lost islands, where area 4's stood (moved with the section).
if art_mesh and old_art6:
    art = actors.spawn_actor_from_class(unreal.StaticMeshActor, old_art6.get_actor_location(), old_art6.get_actor_rotation())
    component = art.get_editor_property("static_mesh_component")
    component.set_static_mesh(art_mesh)
    component.set_collision_profile_name("NoCollision")
    art.set_actor_label(PREFIX + "Art 6")
    art.set_folder_path("Area4/Art")
    actors.destroy_actor(old_art6)
    lines.append("section 6 art: SM_SecretHeaven_6")

# Effekseer draws every effect relative to the level's BP_EffekseerSystem: it must stay at the origin.
for actor in actors.get_all_level_actors():
    if actor.get_class().get_name() == "BP_EffekseerSystem_C":
        actor.set_actor_location(unreal.Vector(0.0, 0.0, 0.0), False, False)
lines.append("jump {:.0f}, walk {:.0f}, platform {:.0f}".format(move.get_editor_property("jump_z_velocity"), move.get_editor_property("max_walk_speed"), 2.0 * PLAT.x))

LOOKS = {
    "marble": load(HEAVEN + "/MI_HeavenMarble"), "gold": load(SKY + "/MI_SkyGold"), "stone": load(HEAVEN + "/MI_HeavenStone"),
    "darkstone": load(HEAVEN + "/MI_HeavenDarkStone"), "sky": load(HEAVEN + "/MI_HeavenSky"),
}
for look, name in (("ruin", "Ashlar"), ("plaster", "Plaster"), ("tile", "Terracotta"), ("paving", "Paving"), ("bronze", "Bronze")):
    LOOKS[look] = load("/Game/Art/Ruins/MI_Ruins" + name)
IRON = load(MACHINE + "/MI_MachineIron")
LOOKS["iron"] = IRON
CLOUD_MESH = load(SKY + "/SM_SkyCloud")
CYLINDER = "/Engine/BasicShapes/Cylinder"

counter = [0]
folder = ["Sky"]


def spawn(actor_class, location, name, rotation=None):
    actor = actors.spawn_actor_from_class(actor_class, location, rotation or unreal.Rotator(0.0, 0.0, 0.0))
    if not actor:
        raise RuntimeError("Could not spawn " + name)
    counter[0] += 1
    actor.set_actor_label("{}{:03d} {}".format(PREFIX, counter[0], name))
    actor.set_folder_path("Secret4/" + folder[0])
    return actor


def yaw(degrees):
    return unreal.Rotator(roll=0.0, pitch=0.0, yaw=degrees)


def mesh_actor(mesh, location, scale, name, material=None, collide=True, rotation=None):
    actor = spawn(unreal.StaticMeshActor, location, name, rotation)
    component = actor.get_editor_property("static_mesh_component")
    component.set_static_mesh(mesh)
    if material:
        for slot in range(max(1, component.get_num_materials())):
            component.set_material(slot, material)
    if not collide:
        component.set_collision_profile_name("NoCollision")
        component.set_editor_property("cast_shadow", False)
    actor.set_actor_scale3d(scale)
    return actor


def box(x0, x1, y0, y1, z0, z1, name, material):
    return mesh_actor(unreal.load_asset(CUBE), unreal.Vector((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0),
                      unreal.Vector((x1 - x0) / 100.0, (y1 - y0) / 100.0, (z1 - z0) / 100.0), name, material)


def configure(actor, settings):
    for key, value in settings:
        actor.set_editor_property(key, value)
    return actor


def platform(class_path, x, y, top, name, settings=()):
    actor = spawn(bp_class(class_path), unreal.Vector(x, y, top - PLAT.z), name)
    return configure(actor, settings)


# ----- first: the named spots and the light beams, which other pieces point at -----
folder[0] = "Spots"
spots, spot_points = {}, {}
for piece in route.pieces:
    if piece[0] == "spot":
        _, name, x, y, top = piece
        spots[name] = unreal.Vector(x, y, top + 100.0)
        spot_points[name] = spawn(unreal.TargetPoint, spots[name], "Respawn " + name)
beams = {}
section = "Spots"
for piece in route.pieces:
    if piece[0] == "section":
        section = piece[1]
    elif piece[0] == "beam":
        _, name, x, y, z0, z1, width, on, off, delay, offset, seconds = piece
        folder[0] = section
        beam = spawn(bp_class(HEAVEN + "/BP_LightBeam"), unreal.Vector(x, y, (z0 + z1) / 2.0), "Light Beam " + name)
        beam.set_actor_scale3d(unreal.Vector(width / 100.0, width / 100.0, (z1 - z0) / 100.0))
        configure(beam, (("OnSeconds", on), ("OffSeconds", off), ("StartDelay", delay),
                         ("MoveOffset", unreal.Vector(*offset)), ("MoveSeconds", seconds)))
        beams[name] = beam

# ----- everything else -----
coins = 0
portals, shards = {}, {}
for piece in route.pieces:
    kind = piece[0]
    if kind == "section":
        folder[0] = piece[1]
    elif kind in ("spot", "beam"):
        pass
    elif kind == "block":
        _, x0, x1, y0, y1, z0, z1, look, name = piece
        box(x0, x1, y0, y1, z0, z1, name, LOOKS[look])
    elif kind == "lplat":
        _, beam_name, x, y, top, size = piece
        actor = spawn(bp_class(HEAVEN + "/BP_LightPlatform"), unreal.Vector(x, y, top - 20.0), "Light Platform")
        actor.set_actor_scale3d(unreal.Vector(size / 100.0, size / 100.0, 0.4))
        actor.set_editor_property("Beam", beams[beam_name])
    elif kind == "jewel":
        _, x, y, top, radius, start_beat, ring, loop, beat, pitch = piece
        actor = spawn(bp_class(HEAVEN + "/BP_ChimeJewel"), unreal.Vector(x, y, top - 20.0), "Chime Jewel")
        actor.set_actor_scale3d(unreal.Vector(2.0 * radius / 100.0, 2.0 * radius / 100.0, 0.4))
        configure(actor, (("BeatSeconds", beat), ("LoopBeats", int(loop)), ("StartBeat", int(start_beat)),
                          ("RingBeats", int(ring)), ("Pitch", pitch)))
    elif kind == "vanish":
        _, x, y, top, size, stay, gone = piece
        actor = spawn(bp_class(SKY + "/BP_VanishCloud"), unreal.Vector(x, y, top), "Vanishing Cloud")
        actor.set_actor_scale3d(unreal.Vector(size / 100.0, size / 100.0, 1.0))
        configure(actor, (("StaySeconds", stay), ("GoneSeconds", gone)))
    elif kind == "falling":
        _, x, y, top = piece
        platform(GIMMICKS + "/BP_FallingFloor", x, y, top, "Crumbling Floor")
    elif kind == "wind":
        _, x, y, z, along, width, height, facing, pitch, strength, max_speed, on, off, delay = piece
        actor = spawn(bp_class(SKY + "/BP_WindZone"), unreal.Vector(x, y, z), "Updraft" if pitch else "Wind",
                      unreal.Rotator(roll=0.0, pitch=pitch, yaw=facing))
        actor.set_actor_scale3d(unreal.Vector(along / 100.0, width / 100.0, height / 100.0))
        configure(actor, (("Strength", strength), ("MaxSpeed", max_speed), ("GustOn", on), ("GustOff", off), ("StartDelay", delay)))
    elif kind == "flame":
        _, x, y, top, facing, delay, warn, burn, off, respawn = piece
        actor = spawn(bp_class(HELL + "/BP_FlameJet"), unreal.Vector(x, y, top), "Flame Jet", yaw(facing))
        configure(actor, (("StartDelay", delay), ("WarnSeconds", warn), ("BurnSeconds", burn), ("OffSeconds", off), ("RespawnLocation", spots[respawn])))
    elif kind == "sun":
        _, x, y, top, respawn = piece[:5]
        path = HEAVEN + "/BP_TowerSun" if len(piece) > 5 else GIMMICKS + "/Sun/BP_Sun"
        actor = spawn(bp_class(path), unreal.Vector(x, y, top), "Sun")
        actor.set_editor_property("RespawnPoint", spot_points[respawn])
        if len(piece) > 5:
            actor.set_editor_property("GrabChance", 0.3)
            marker = spawn(bp_class(HEAVEN + "/BP_SunMarker"), unreal.Vector(x, y, top), "Sun Marker")
            marker.set_editor_property("Sun", actor)
    elif kind == "coin":
        _, x, y, top = piece
        spawn(bp_class(COIN), unreal.Vector(x, y, top + 100.0), "Star Coin")
        coins += 1
    elif kind == "flag":
        _, x, y, top = piece
        spawn(bp_class(ITEMS + "/Checkpoint/BP_CheckpointFlag"), unreal.Vector(x, y, top), "Checkpoint Flag")
    elif kind == "catcher":
        _, x0, x1, y0, y1, z = piece
        catcher = spawn(bp_class(MACHINE + "/BP_FallCatcher"), unreal.Vector((x0 + x1) / 2.0, (y0 + y1) / 2.0, z), "Fall Catcher")
        catcher.set_actor_scale3d(unreal.Vector((x1 - x0) / 100.0, (y1 - y0) / 100.0, 4.0))
    elif kind == "portal":
        # A trial footing (BP_TrialPortal, its origin on the footing's top) and the flag on it; wired up below.
        _, number, x, y, top = piece
        portal = spawn(bp_class(AREA + "/BP_TrialPortal"), unreal.Vector(x, y, top), "Trial Footing {}".format(number))
        flag = spawn(bp_class(ITEMS + "/Checkpoint/BP_CheckpointFlag"), unreal.Vector(x, y, top), "Trial Flag {}".format(number))
        portals[number] = (portal, flag)
    elif kind == "shard":
        _, name, x, y, top = piece
        shards[name] = spawn(bp_class(HEAVEN + "/BP_LightShard"), unreal.Vector(x, y, top + 120.0), "Light Shard " + name)
    elif kind == "timed":
        _, x, y, top, delay = piece
        platform(GIMMICKS + "/BP_TimedPlatform", x, y, top, "Fading Step",
                 (("VisibleSeconds", 1.8), ("HiddenSeconds", 1.2), ("FadeSeconds", 0.4), ("StartDelay", delay)))
    elif kind == "moving":
        _, x, y, top, offset, seconds, wait = piece[:7]
        actor = platform(GIMMICKS + "/BP_MovingPlatform", x, y, top, "Piston" if offset[2] else "Moving Platform",
                         (("MoveOffset", unreal.Vector(*offset)), ("MoveSeconds", seconds), ("WaitSeconds", wait)))
        if len(piece) > 7:
            across = piece[7] / (2.0 * PLAT.x)
            actor.set_actor_scale3d(unreal.Vector(across, across, 1.0))
    elif kind == "gear":
        _, x, y, top, radius, spin = piece
        actor = spawn(bp_class(MACHINE + "/BP_SpinGear"), unreal.Vector(x, y, top - 15.0), "Spinning Gear")
        actor.set_actor_scale3d(unreal.Vector(radius / 100.0, radius / 100.0, 1.0))
        actor.set_editor_property("SpinSpeed", spin)
        mesh_actor(unreal.load_asset(CYLINDER), unreal.Vector(x, y, top - 770.0), unreal.Vector(0.36, 0.36, 14.6), "Axle", IRON)
    elif kind == "cloud":
        _, x, y, top, size = piece
        mesh_actor(CLOUD_MESH, unreal.Vector(x, y, top), unreal.Vector(size / 100.0, size / 100.0, 1.2), "Cloud")
    elif kind == "mover":
        _, x, y, top, offset, seconds, wait = piece
        actor = spawn(bp_class(SKY + "/BP_MovingIsland"), unreal.Vector(x, y, top), "Moving Island")
        configure(actor, (("MoveOffset", unreal.Vector(*offset)), ("MoveSeconds", seconds), ("WaitSeconds", wait)))
    else:
        raise RuntimeError("Unknown piece " + kind)

# ----- the trials wired: each footing to its small area's start and shard, each after the one before -----
# (11-23: the footings lie on area 4's own islands, all there from the start; each one's onward updraft sleeps until
# its trial is done - no Prev.)
by_label = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
for number, (portal, flag) in sorted(portals.items()):
    configure(portal, (("Destination", spot_points["trial{}".format(number)]), ("Shard", shards["trial{}".format(number)]),
                       ("Flag", flag)))
    wind = by_label.get(secret4_collapse.TRIAL_WINDS[number - 1])
    if wind is None:
        raise RuntimeError("Missing " + secret4_collapse.TRIAL_WINDS[number - 1])
    portal.set_editor_property("Wind", wind)
lines.append("{} trial footings".format(len(portals)))

# ----- area 4's own start: every star coin of the level counted; the hidden stages' track -----
all_coins = [a for a in actors.get_all_level_actors() if a.get_class().get_name() == "BP_StarCoin_C"]
for actor in actors.get_all_level_actors():
    kind = actor.get_class().get_name()
    if kind == "BP_AreaStart_C":
        actor.set_editor_property("AreaCoins", len(all_coins))
    elif kind == "BP_AreaBgm_C":
        actor.set_editor_property("AreaBgm", unreal.load_asset("/Game/Sound/BGM/BGM_Secret"))
lines.append("{} star coins in all".format(len(all_coins)))

# ===== sky: a blood-red dusk over the fallen heaven, red haze below, wreckage everywhere =====
folder[0] = "Sky"
sun = spawn(unreal.DirectionalLight, unreal.Vector(0.0, 0.0, B + 9000.0), "Sun", unreal.Rotator(roll=0.0, pitch=-4.0, yaw=200.0))
sun_light = sun.get_editor_property("directional_light_component")
sun_light.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
sun_light.set_editor_property("intensity", 4.0)
sun_light.set_editor_property("light_color", unreal.Color(r=255, g=90, b=50, a=255))
sun_light.set_editor_property("atmosphere_sun_light", True)
sky = spawn(unreal.SkyLight, unreal.Vector(0.0, 0.0, B + 9000.0), "Sky Light")
sky_light = sky.get_editor_property("light_component")
sky_light.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
sky_light.set_editor_property("real_time_capture", True)
sky_light.set_editor_property("intensity", 0.6)
atmosphere = spawn(unreal.SkyAtmosphere, unreal.Vector(0.0, 0.0, 0.0), "Sky Atmosphere")
try:
    atmo = atmosphere.get_editor_property("sky_atmosphere_component")
    atmo.set_editor_property("rayleigh_scattering", unreal.LinearColor(0.25, 0.04, 0.02, 1.0))
    atmo.set_editor_property("mie_scattering_scale", 0.02)
except Exception as error:
    lines.append("atmosphere not tinted: {}".format(error))
fog = spawn(unreal.ExponentialHeightFog, unreal.Vector(0.0, 0.0, MIST), "Red Haze")
fog_component = fog.get_editor_property("component")
fog_component.set_editor_property("fog_density", 0.05)
fog_component.set_editor_property("fog_height_falloff", 0.0015)
fog_component.set_editor_property("fog_inscattering_luminance", unreal.LinearColor(0.6, 0.12, 0.06, 1.0))
try:
    fog_component.set_editor_property("enable_volumetric_fog", True)
except Exception as error:
    lines.append("volumetric fog not set: {}".format(error))

# Wreckage of the palace: loose blocks tumbling near the route (well below or aside), big ones far out.
X0, X1, Y0, Y1 = route.bounds
rand = random.Random(17)
looks = ("marble", "stone", "marble", "gold", "darkstone")
solid = [p for p in route.pieces if p[0] == "block"]
for p in solid[::2]:
    _, x0, x1, y0, y1, z0, z1, look, name = p
    for k in range(rand.randint(1, 3)):
        a = rand.uniform(0.0, 2.0 * math.pi)
        d = rand.uniform(900.0, 2200.0)
        x, y = (x0 + x1) / 2.0 + math.cos(a) * d, (y0 + y1) / 2.0 + math.sin(a) * d
        z = z1 - rand.uniform(400.0, 2500.0)
        size = rand.uniform(80.0, 320.0)
        mesh_actor(unreal.load_asset(CUBE), unreal.Vector(x, y, z),
                   unreal.Vector(size / 100.0, size / 100.0 * rand.uniform(0.6, 1.4), size / 100.0 * rand.uniform(0.4, 1.0)),
                   "Wreckage", LOOKS[rand.choice(looks)], collide=False,
                   rotation=unreal.Rotator(roll=rand.uniform(-40.0, 40.0), pitch=rand.uniform(-40.0, 40.0), yaw=rand.uniform(0.0, 360.0)))
for i in range(60):
    a = rand.uniform(0.0, 2.0 * math.pi)
    x = (X0 + X1) / 2.0 + math.cos(a) * rand.uniform(0.55, 0.8) * (X1 - X0)
    y = (Y0 + Y1) / 2.0 + math.sin(a) * rand.uniform(0.55, 0.8) * (Y1 - Y0)
    size = rand.uniform(1200.0, 4000.0)
    mesh_actor(unreal.load_asset(CUBE), unreal.Vector(x, y, rand.uniform(B - 2000.0, route.summit_top + 2000.0)),
               unreal.Vector(size / 100.0, size / 100.0 * rand.uniform(0.5, 1.2), size / 100.0 * rand.uniform(0.3, 0.8)),
               "Far Wreckage", LOOKS[rand.choice(looks)], collide=False,
               rotation=unreal.Rotator(roll=rand.uniform(-30.0, 30.0), pitch=rand.uniform(-30.0, 30.0), yaw=rand.uniform(0.0, 360.0)))
for name, g, rise, limit in route.checks:
    lines.append("  {:<44} gap {:>5.0f} rise {:>6.0f} (limit {:>5.0f})".format(name, g, rise, limit))
for name, z in route.heights.items():
    lines.append("  {:<24} {:>7.0f}  ({:+.0f} from the start)".format(name, z, z - B))
lines.append("{} coins added; {} jumps added; {} actors".format(coins, len(route.checks), counter[0]))
lines.append("{} saved {}".format(LEVEL, level_subsystem.save_current_level()))

with open(os.path.join(unreal.Paths.project_saved_dir(), "secret4_build.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
