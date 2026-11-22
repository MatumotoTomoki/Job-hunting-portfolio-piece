# Builds /Game/LV_Secret2, hidden area 2: area 2 itself, collapsed (the user, 2026-11-22): area 2's own goal kept (the
# roof's lever, the drawer steps, the catapult on the spire - sunk until a hidden lever raises it, then on to
# LV_Secret3) and the way there made longer and stranger. LV_Area2_Tower is copied with save_map (never changed) and
# each section moved whole by the offsets secret2_collapse.py works out (art, collision, gimmicks, lamps, wall gears;
# B+C and F+G as one); the engine room is broken open (secret2_engine.py, its own art SM_SecretTower_A). On arrival
# (area 2's own BP_GearArrival, from hidden stage 1's gear) the doomed catapult is smashed by a pillar of light
# (BP_CatapultSmash; the pillar is a false goal). Area 2's sky is taken out. New pieces are labelled "S2 ...". Run
# with the editor closed (it deletes and re-copies LV_Secret2):
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\build_secret2_stage.py -unattended -nop4 -nosplash -stdout
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
import secret2_engine  # noqa: E402
import secret2_layout  # noqa: E402
import secret2_collapse  # noqa: E402
for module in (area3_layout, area4_layout, secret_town, secret_collapse, secret2_engine, secret2_layout, secret2_collapse):
    importlib.reload(module)

LEVEL = "/Game/LV_Secret2"
SOURCE = "/Game/LV_Area2_Tower"
NEXT_LEVEL = "/Game/LV_Secret3"
PARKING = "/Game/LV_Title"
AREA = "/Game/ThirdPerson/Blueprints/Gimmicks/Area"
SKY = "/Game/ThirdPerson/Blueprints/Gimmicks/Sky"
MACHINE = "/Game/ThirdPerson/Blueprints/Gimmicks/Machine"
HEAVEN = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven"
GIMMICKS = "/Game/ThirdPerson/Blueprints/Gimmicks"
HELL = GIMMICKS + "/Hell"
ITEMS = "/Game/ThirdPerson/Item"
COIN = "/Game/ThirdPerson/Coin/StarCoin/BP_StarCoin"
CAGE_DOOR = "/Game/Prototype/Birdcage/BP_BirdcageDoor_Blender"
GAME_MODE = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonGameMode"
FALLBACK_CHARACTER = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter1"
CUBE = "/Engine/BasicShapes/Cube"
CYLINDER = "/Engine/BasicShapes/Cylinder"
SPHERE = "/Engine/BasicShapes/Sphere"
PREFIX = "S2 "
B = 0.0                        # area 1's ground
MIST = 3000.0                  # the red haze far below

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
        raise RuntimeError("Missing " + path + " (run setup_area4_assets.py first)")
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


move = player_defaults().get_editor_property("character_movement")
PLAT = elevator_half()
route = secret2_collapse.build(B, move.get_editor_property("jump_z_velocity"), 980.0 * move.get_editor_property("gravity_scale"),
                           move.get_editor_property("max_walk_speed"), 2.0 * PLAT.x)
# ----- the level: a fresh copy of area 2, its sections torn apart -----
# (Not delete + duplicate_asset + load: the duplicated world stayed in memory and the next map load crashed the editor
# on a "world memory leak", 2026-11-22. Instead area 2 is opened, saved as LV_Secret2 and the copy opened; if the
# copy is not what is open, nothing is changed.)
level_subsystem.load_level(PARKING)
if library.does_asset_exist(LEVEL) and not library.delete_asset(LEVEL):
    raise RuntimeError("Could not delete the old " + LEVEL)
if not level_subsystem.load_level(SOURCE):
    raise RuntimeError("Could not open " + SOURCE)
editor_world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if not unreal.EditorLoadingAndSavingUtils.save_map(editor_world, LEVEL):
    raise RuntimeError("Could not save {} as {}".format(SOURCE, LEVEL))
# save_map writes the copy but leaves area 1 open: open the copy.
if not level_subsystem.load_level(LEVEL):
    raise RuntimeError("Could not open " + LEVEL)
now_open = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name()
if not now_open.startswith(LEVEL + "."):
    raise RuntimeError("{} is open, not {}: stopped before changing anything".format(now_open, LEVEL))
OFFSETS = route.section_offsets
moved, removed = 0, 0
for actor in actors.get_all_level_actors():
    label, path = actor.get_actor_label(), str(actor.get_folder_path())
    kind = actor.get_class().get_name()
    if path.startswith("Area2/Sky") or kind in ("BP_SteamCatapult_C",):
        actors.destroy_actor(actor)
        removed += 1
        continue
    if label in secret2_collapse.MOVE_WITH:
        section = secret2_collapse.MOVE_WITH[label]
    elif path.startswith("Area2/Art") and len(label.split(" ")) > 2 and label.split(" ")[2][:1] in OFFSETS:
        section = label.split(" ")[2][0]
    elif path.startswith("Area2/") and path[6:7] in OFFSETS:
        section = path[6]
    else:
        continue
    dx, dy, dz = OFFSETS[section]
    if dx or dy or dz:
        where = actor.get_actor_location()
        actor.set_actor_location(unreal.Vector(where.x + dx, where.y + dy, where.z + dz), False, False)
        moved += 1
lines.append("{} copied from {}: {} actors moved, {} taken out".format(LEVEL, SOURCE, moved, removed))

# ----- the engine room broken open (secret2_engine.py) -----
for actor in actors.get_all_level_actors():
    if actor.get_actor_label() in secret2_engine.REMOVE + secret2_engine.REMOVE_ART:
        actors.destroy_actor(actor)
cube = unreal.load_asset("/Engine/BasicShapes/Cube")
for label, x0, x1, y0, y1, z0, z1 in secret2_engine.added_boxes():
    box_actor = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0),
                                              unreal.Rotator(0.0, 0.0, 0.0))
    box_actor.get_editor_property("static_mesh_component").set_static_mesh(cube)
    box_actor.set_actor_scale3d(unreal.Vector((x1 - x0) / 100.0, (y1 - y0) / 100.0, (z1 - z0) / 100.0))
    box_actor.set_actor_label(label)
    box_actor.set_folder_path("Area2/A Engine Room")
    box_actor.set_actor_hidden_in_game(True)
engine_fbx = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Models", "Tower", "SM_SecretTower_A.fbx")
if os.path.exists(engine_fbx):
    options = unreal.FbxImportUI()
    options.set_editor_property("import_materials", False)
    options.set_editor_property("import_textures", False)
    mesh_data = options.get_editor_property("static_mesh_import_data")
    mesh_data.set_editor_property("auto_generate_collision", False)
    mesh_data.set_editor_property("combine_meshes", True)
    mesh_data.set_editor_property("generate_lightmap_u_vs", False)
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", engine_fbx)
    task.set_editor_property("destination_path", "/Game/Art/Tower/Secret")
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("automated", True)
    task.set_editor_property("save", False)
    task.set_editor_property("options", options)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    engine_mesh = unreal.load_asset("/Game/Art/Tower/Secret/SM_SecretTower_A")
    for i, slot in enumerate(engine_mesh.get_editor_property("static_materials")):
        name = str(slot.get_editor_property("material_slot_name"))
        if name.startswith("M_Tower"):
            engine_mesh.set_material(i, unreal.load_asset("/Game/Art/Tower/MI_Tower" + name[len("M_Tower"):]))
    library.save_asset("/Game/Art/Tower/Secret/SM_SecretTower_A", False)
    for actor in actors.get_all_level_actors():
        if actor.get_actor_label() == "A2 Art A":
            actors.destroy_actor(actor)
    art = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator(0.0, 0.0, 0.0))
    art.get_editor_property("static_mesh_component").set_static_mesh(engine_mesh)
    art.get_editor_property("static_mesh_component").set_collision_profile_name("NoCollision")
    art.set_actor_label("S2 Art Engine Room")
    art.set_folder_path("Area2/Art")
    lines.append("engine room broken open: {} boxes added, art SM_SecretTower_A".format(len(secret2_engine.added_boxes())))
else:
    lines.append("SM_SecretTower_A.fbx missing: area 2's engine room art left (run build_tower_blender.py)")
# Effekseer draws every effect relative to the level's BP_EffekseerSystem: it must stay at the origin (it sat in area 1's
# lower-town folder and was moved with a chunk, so every effect was off - the user, 2026-11-22).
for actor in actors.get_all_level_actors():
    if actor.get_class().get_name() == "BP_EffekseerSystem_C":
        actor.set_actor_location(unreal.Vector(0.0, 0.0, 0.0), False, False)
# The flipping floor's size and where its top is, measured on a spawned one.
probe = actors.spawn_actor_from_class(bp_class(GIMMICKS + "/BP_RotatingFloor"), unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator(0.0, 0.0, 0.0))
origin, extent = probe.get_actor_bounds(False)
ROT_SIZE = 2.0 * min(extent.x, extent.y)
ROT_TOP = origin.z + extent.z
actors.destroy_actor(probe)
lines.append("flipping floor {:.0f} across, top {:.0f} above its origin".format(ROT_SIZE, ROT_TOP))


lines.append("jump {:.0f}, walk {:.0f}, platform {:.0f}".format(move.get_editor_property("jump_z_velocity"), move.get_editor_property("max_walk_speed"), 2.0 * PLAT.x))

CLOUD_MESH = load(SKY + "/SM_SkyCloud")
ISLAND_MESH = load(SKY + "/SM_SkyIsland")
CLOUD_WHITE = load(SKY + "/MI_SkyCloud")
GOLD = load(SKY + "/MI_SkyGold")
LOOKS = {
    "marble": load(HEAVEN + "/MI_HeavenMarble"), "gold": GOLD, "stone": load(HEAVEN + "/MI_HeavenStone"),
    "darkstone": load(HEAVEN + "/MI_HeavenDarkStone"), "sky": load(HEAVEN + "/MI_HeavenSky"),
    "ember": load(AREA + "/MI_RuinsEmber"), "glow": load(HEAVEN + "/MI_HeavenGlow"),
}
for look, name in (("ruin", "Ashlar"), ("plaster", "Plaster"), ("tile", "Terracotta"), ("paving", "Paving"), ("rock", "Rock"),
                   ("wood", "Wood"), ("bronze", "Bronze")):
    LOOKS[look] = load("/Game/Art/Ruins/MI_Ruins" + name)
LOOKS["iron"] = load(MACHINE + "/MI_MachineIron")
SHAFT = load(HEAVEN + "/MI_LightShaft")
RED_SOLID, BLUE_SOLID = load(MACHINE + "/MI_SwitchRed"), load(MACHINE + "/MI_SwitchBlue")
RED_GHOST, BLUE_GHOST = load(MACHINE + "/MI_SwitchGhostRed"), load(MACHINE + "/MI_SwitchGhostBlue")
IRON = load(MACHINE + "/MI_MachineIron")

counter = [0]
folder = ["Sky"]


def spawn(actor_class, location, name, rotation=None):
    actor = actors.spawn_actor_from_class(actor_class, location, rotation or unreal.Rotator(0.0, 0.0, 0.0))
    if not actor:
        raise RuntimeError("Could not spawn " + name)
    counter[0] += 1
    actor.set_actor_label("{}{:03d} {}".format(PREFIX, counter[0], name))
    actor.set_folder_path("Secret2/" + folder[0])
    return actor


def yaw(degrees):
    return unreal.Rotator(roll=0.0, pitch=0.0, yaw=degrees)


def mesh_actor(mesh, location, scale, name, material=None, collide=True, rotation=None, shadow=True):
    actor = spawn(unreal.StaticMeshActor, location, name, rotation)
    component = actor.get_editor_property("static_mesh_component")
    component.set_static_mesh(mesh)
    if material:
        for slot in range(max(1, component.get_num_materials())):
            component.set_material(slot, material)
    if not collide:
        component.set_collision_profile_name("NoCollision")
    if not collide or not shadow:
        component.set_editor_property("cast_shadow", False)
    actor.set_actor_scale3d(scale)
    return actor


def box(x0, x1, y0, y1, z0, z1, name, material, mesh=CUBE, collide=True):
    return mesh_actor(unreal.load_asset(mesh), unreal.Vector((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0),
                      unreal.Vector((x1 - x0) / 100.0, (y1 - y0) / 100.0, (z1 - z0) / 100.0), name, material, collide)


def configure(actor, settings):
    for key, value in settings:
        actor.set_editor_property(key, value)
    return actor


def text(x, y, z, facing, words, size=60.0):
    actor = spawn(unreal.TextRenderActor, unreal.Vector(x, y, z), "Sign", yaw(facing))
    render = actor.get_editor_property("text_render")
    render.set_text(unreal.Text(words))
    render.set_editor_property("world_size", size)
    render.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)
    return actor


def lamp(x, y, z, color, strength=5000.0, radius=1800.0):
    mesh_actor(unreal.load_asset(SPHERE), unreal.Vector(x, y, z), unreal.Vector(0.3, 0.3, 0.3), "Lamp", LOOKS["glow"], collide=False)
    light = spawn(unreal.PointLight, unreal.Vector(x, y, z), "Lamp Light")
    component = light.get_editor_property("point_light_component")
    component.set_editor_property("intensity", strength)
    component.set_editor_property("attenuation_radius", radius)
    component.set_editor_property("light_color", unreal.Color(r=color[0], g=color[1], b=color[2], a=255))
    component.set_editor_property("cast_shadows", False)


def shaft(x, y, z_top, z_bottom, radius):
    length = z_top - z_bottom
    mesh_actor(unreal.load_asset(CYLINDER), unreal.Vector(x, y, (z_top + z_bottom) / 2.0),
               unreal.Vector(2.0 * radius / 100.0, 2.0 * radius / 100.0, length / 100.0), "Light Shaft", SHAFT, collide=False)
    light = spawn(unreal.SpotLight, unreal.Vector(x, y, z_top - 20.0), "Shaft Light", unreal.Rotator(roll=0.0, pitch=-90.0, yaw=0.0))
    component = light.get_editor_property("spot_light_component")
    component.set_editor_property("intensity", 60000.0)
    component.set_editor_property("attenuation_radius", length + 400.0)
    cone = math.degrees(math.atan2(1.6 * radius, length))
    component.set_editor_property("outer_cone_angle", max(cone, 4.0))
    component.set_editor_property("inner_cone_angle", max(cone * 0.5, 2.0))
    component.set_editor_property("light_color", unreal.Color(r=255, g=236, b=200, a=255))
    component.set_editor_property("cast_shadows", False)


def platform(class_path, x, y, top, name, settings=()):
    actor = spawn(bp_class(class_path), unreal.Vector(x, y, top - PLAT.z), name)
    return configure(actor, settings)


# ----- first: the named spots and the levers, which other pieces point at -----
folder[0] = "Spots"
spots = {}
spot_points = {}
for piece in route.pieces:
    if piece[0] == "spot":
        _, name, x, y, top = piece
        spots[name] = unreal.Vector(x, y, top + 100.0)
        spot_points[name] = spawn(unreal.TargetPoint, spots[name], "Respawn " + name)
START = spots["start"]
levers = {}
cameras = {}
section = "Spots"
for piece in route.pieces:
    if piece[0] == "section":
        section = piece[1]
    elif piece[0] == "lever":
        _, name, x, y, top, facing, reset = piece
        folder[0] = section
        lever = spawn(bp_class(AREA + "/BP_Lever"), unreal.Vector(x, y, top), "Pressure Plate" if reset else "Lever " + name, yaw(facing))
        if reset:
            for component in lever.get_components_by_class(unreal.StaticMeshComponent):
                part = component.get_name()
                if part.startswith("Handle") or part.startswith("Knob"):
                    component.set_visibility(False, False)
                    component.set_hidden_in_game(True, False)
                    component.set_collision_profile_name("NoCollision")
                elif part.startswith("Base"):
                    component.set_editor_property("relative_scale3d", unreal.Vector(1.8, 1.8, 0.06))
                    component.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 3.0))
                    component.set_material(0, LOOKS["ember"])
            for component in lever.get_components_by_class(unreal.BoxComponent):
                component.set_editor_property("box_extent", unreal.Vector(90.0, 90.0, 40.0))
                component.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 40.0))
            lever.set_editor_property("ShowCamera", None)
            lever.set_editor_property("ResetAfter", reset)
        levers[name] = lever
    elif piece[0] == "hidden_lever":
        # Pulled by a script (the Iwato), never by the player: out of reach and unseen.
        _, name, x, y, z = piece
        folder[0] = section
        lever = spawn(bp_class(AREA + "/BP_Lever"), unreal.Vector(x, y, z), "Hidden Lever " + name)
        lever.set_actor_hidden_in_game(True)
        levers[name] = lever
# The light beams, which light platforms point at.
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
shards = {}
iwato_pieces = []

# ----- everything else -----
coins = 0
for piece in route.pieces:
    kind = piece[0]
    if kind == "section":
        folder[0] = piece[1]
    elif kind in ("spot", "lever", "hidden_lever", "beam"):
        pass
    elif kind == "iwato":
        iwato_pieces.append((piece, folder[0]))
    elif kind == "under":
        _, x0, x1, y0, y1, under, thick, look, name = piece
        box(x0, x1, y0, y1, under, under + thick, name, LOOKS[look])
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
    elif kind == "thread":
        _, x, y, anchor, length, swing, seconds, offset, hold, facing = piece
        actor = spawn(bp_class(HEAVEN + "/BP_SpiderThread"), unreal.Vector(x, y, anchor), "Spider Thread", yaw(facing))
        configure(actor, (("Length", length), ("SwingDegrees", swing), ("SwingSeconds", seconds), ("SwingOffset", offset),
                          ("HoldSeconds", hold)))
        mesh_actor(unreal.load_asset(SPHERE), unreal.Vector(x, y, anchor + 30.0), unreal.Vector(0.6, 0.6, 0.6), "Thread Knot", LOOKS["glow"], collide=False)
    elif kind == "gzone":
        _, x0, x1, y0, y1, z0, z1, direction = piece
        actor = spawn(bp_class(HEAVEN + "/BP_GravityZone"), unreal.Vector((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0), "Gravity Zone")
        actor.set_actor_scale3d(unreal.Vector((x1 - x0) / 100.0, (y1 - y0) / 100.0, (z1 - z0) / 100.0))
        actor.set_editor_property("Direction", unreal.Vector(*direction))
    elif kind == "gear_flip":
        _, x, y, under, r, spin = piece
        actor = spawn(bp_class(MACHINE + "/BP_SpinGear"), unreal.Vector(x, y, under + 15.0), "Upside-down Gear",
                      unreal.Rotator(roll=180.0, pitch=0.0, yaw=0.0))
        actor.set_actor_scale3d(unreal.Vector(r / 100.0, r / 100.0, 1.0))
        actor.set_editor_property("SpinSpeed", spin)
        box(x - 18.0, x + 18.0, y - 18.0, y + 18.0, under + 40.0, under + 1500.0, "Axle", IRON, CYLINDER)
    elif kind == "sblock_flip":
        _, x, y, under, size, red = piece
        thick = 60.0
        actor = spawn(bp_class(MACHINE + "/BP_SwitchBlock"), unreal.Vector(x, y, under + thick / 2.0), "Red Block" if red else "Blue Block")
        actor.set_actor_scale3d(unreal.Vector(size / 100.0, size / 100.0, thick / 100.0))
        actor.set_editor_property("IsRed", red)
        for component in actor.get_components_by_class(unreal.StaticMeshComponent):
            solid = component.get_name().startswith("Solid")
            component.set_material(0, (RED_SOLID if red else BLUE_SOLID) if solid else (RED_GHOST if red else BLUE_GHOST))
    elif kind == "switch_flip":
        _, x, y, under = piece
        spawn(bp_class(MACHINE + "/BP_ToggleSwitch"), unreal.Vector(x, y, under), "Ceiling Switch", unreal.Rotator(roll=180.0, pitch=0.0, yaw=0.0))
    elif kind == "timed_flip":
        _, x, y, under, delay = piece
        actor = spawn(bp_class(GIMMICKS + "/BP_TimedPlatform"), unreal.Vector(x, y, under + PLAT.z), "Fading Ceiling Step")
        configure(actor, (("VisibleSeconds", 1.8), ("HiddenSeconds", 1.2), ("FadeSeconds", 0.4), ("StartDelay", delay)))
    elif kind == "shard":
        _, name, x, y, top = piece
        shards[name] = spawn(bp_class(HEAVEN + "/BP_LightShard"), unreal.Vector(x, y, top + 120.0), "Light Shard " + name)
    elif kind == "wings":
        _, x, y, top = piece
        spawn(bp_class(HEAVEN + "/BP_Wings"), unreal.Vector(x, y, top + 60.0), "Wings")
    elif kind == "start":
        _, x, y, top, facing = piece
        spawn(unreal.PlayerStart, unreal.Vector(x, y, top + 100.0), "PlayerStart", yaw(facing))
        area_start = spawn(bp_class(AREA + "/BP_AreaStart"), unreal.Vector(x + 300.0, y, top + 200.0), "Area Start")

        try:
            area_start.set_editor_property("AreaCoins", sum(1 for p in route.pieces if p[0] == "coin"))
        except Exception as error:
            lines.append("AreaCoins not set: {}".format(error))
        spawn(bp_class("/Effekseer/BluePrints/BP_EffekseerSystem"), unreal.Vector(0.0, 0.0, 0.0), "Effekseer System")
    elif kind == "block":
        _, x0, x1, y0, y1, z0, z1, look, name = piece
        box(x0, x1, y0, y1, z0, z1, name, LOOKS[look])
    elif kind == "glass":
        _, x0, x1, y0, y1, z0, z1 = piece
        pane = box(x0, x1, y0, y1, z0, z1, "Glass", SHAFT)
        pane.set_actor_hidden_in_game(True)
        pane.get_editor_property("static_mesh_component").set_editor_property("cast_shadow", False)
    elif kind == "disk":
        _, x, y, top, r, thick, look, name = piece
        mesh_actor(unreal.load_asset(CYLINDER), unreal.Vector(x, y, top - thick / 2.0), unreal.Vector(2.0 * r / 100.0, 2.0 * r / 100.0, thick / 100.0), name, LOOKS[look])
    elif kind == "island_deco":
        _, x, y, top, size = piece
        mesh_actor(ISLAND_MESH, unreal.Vector(x, y, top), unreal.Vector(size / 100.0, size / 100.0, size / 100.0 * 0.5), "Plaza Rock", collide=False)
    elif kind == "island":
        _, x, y, top, size = piece
        mesh_actor(ISLAND_MESH, unreal.Vector(x, y, top), unreal.Vector(size / 100.0, size / 100.0, size / 100.0 * 0.7), "Island")
    elif kind == "cloud":
        _, x, y, top, size = piece
        mesh_actor(CLOUD_MESH, unreal.Vector(x, y, top), unreal.Vector(size / 100.0, size / 100.0, 1.2), "Cloud")
    elif kind == "vanish":
        _, x, y, top, size, stay, gone = piece
        actor = spawn(bp_class(SKY + "/BP_VanishCloud"), unreal.Vector(x, y, top), "Vanishing Cloud")
        actor.set_actor_scale3d(unreal.Vector(size / 100.0, size / 100.0, 1.0))
        configure(actor, (("StaySeconds", stay), ("GoneSeconds", gone)))
    elif kind == "mover":
        _, x, y, top, offset, seconds, wait = piece
        actor = spawn(bp_class(SKY + "/BP_MovingIsland"), unreal.Vector(x, y, top), "Moving Island")
        configure(actor, (("MoveOffset", unreal.Vector(*offset)), ("MoveSeconds", seconds), ("WaitSeconds", wait)))
    elif kind == "moving":
        _, x, y, top, offset, seconds, wait = piece[:7]
        actor = platform(GIMMICKS + "/BP_MovingPlatform", x, y, top, "Piston" if offset[2] else "Moving Platform",
                         (("MoveOffset", unreal.Vector(*offset)), ("MoveSeconds", seconds), ("WaitSeconds", wait)))
        if len(piece) > 7:
            # Wider: scaled across only, so the straight-up move keeps its height.
            across = piece[7] / (2.0 * PLAT.x)
            actor.set_actor_scale3d(unreal.Vector(across, across, 1.0))
    elif kind == "timed":
        _, x, y, top, delay = piece
        platform(GIMMICKS + "/BP_TimedPlatform", x, y, top, "Fading Step",
                 (("VisibleSeconds", 1.8), ("HiddenSeconds", 1.2), ("FadeSeconds", 0.4), ("StartDelay", delay)))
    elif kind == "falling":
        _, x, y, top = piece
        platform(GIMMICKS + "/BP_FallingFloor", x, y, top, "Crumbling Floor")
    elif kind == "rotating":
        _, x, y, top = piece
        spawn(bp_class(GIMMICKS + "/BP_RotatingFloor"), unreal.Vector(x, y, top - ROT_TOP), "Flipping Floor")
    elif kind == "marble":
        _, x0, x1, y0, y1, top, thick = piece
        box(x0, x1, y0, y1, top - thick, top, "Marble", LOOKS["marble"])
    elif kind == "wind":
        _, x, y, z, along, width, height, facing, pitch, strength, max_speed, on, off, delay = piece
        actor = spawn(bp_class(SKY + "/BP_WindZone"), unreal.Vector(x, y, z), "Updraft" if pitch else "Wind",
                      unreal.Rotator(roll=0.0, pitch=pitch, yaw=facing))
        actor.set_actor_scale3d(unreal.Vector(along / 100.0, width / 100.0, height / 100.0))
        configure(actor, (("Strength", strength), ("MaxSpeed", max_speed), ("GustOn", on), ("GustOff", off), ("StartDelay", delay)))
    elif kind == "gear":
        _, x, y, top, r, spin = piece
        actor = spawn(bp_class(MACHINE + "/BP_SpinGear"), unreal.Vector(x, y, top - 15.0), "Spinning Gear")
        actor.set_actor_scale3d(unreal.Vector(r / 100.0, r / 100.0, 1.0))
        actor.set_editor_property("SpinSpeed", spin)
        box(x - 18.0, x + 18.0, y - 18.0, y + 18.0, top - 1500.0, top - 40.0, "Axle", IRON, CYLINDER)
    elif kind == "sblock":
        _, x, y, top, size, red = piece
        thick = 60.0
        actor = spawn(bp_class(MACHINE + "/BP_SwitchBlock"), unreal.Vector(x, y, top - thick / 2.0), "Red Block" if red else "Blue Block")
        actor.set_actor_scale3d(unreal.Vector(size / 100.0, size / 100.0, thick / 100.0))
        actor.set_editor_property("IsRed", red)
        for component in actor.get_components_by_class(unreal.StaticMeshComponent):
            solid = component.get_name().startswith("Solid")
            component.set_material(0, (RED_SOLID if red else BLUE_SOLID) if solid else (RED_GHOST if red else BLUE_GHOST))
    elif kind == "switch":
        _, x, y, top = piece
        spawn(bp_class(MACHINE + "/BP_ToggleSwitch"), unreal.Vector(x, y, top), "Switch")
    elif kind == "gondola":
        _, x, y, top, offset, seconds = piece
        actor = spawn(bp_class(MACHINE + "/BP_Gondola"), unreal.Vector(x, y, top), "Gondola")
        configure(actor, (("TravelOffset", unreal.Vector(*offset)), ("TravelSeconds", seconds), ("WaitSeconds", 2.5)))
        hang, reach = 440.0, 600.0
        length = math.sqrt(sum(c * c for c in offset))
        ux, uy, uz = offset[0] / length, offset[1] / length, offset[2] / length
        a = unreal.Vector(x - ux * reach, y - uy * reach, top + hang - uz * reach)
        b = unreal.Vector(x + offset[0] + ux * reach, y + offset[1] + uy * reach, top + offset[2] + hang + uz * reach)
        d = unreal.Vector(b.x - a.x, b.y - a.y, b.z - a.z)
        cable = mesh_actor(unreal.load_asset(CYLINDER), unreal.Vector((a.x + b.x) / 2.0, (a.y + b.y) / 2.0, (a.z + b.z) / 2.0),
                           unreal.Vector(0.08, 0.08, math.sqrt(d.x * d.x + d.y * d.y + d.z * d.z) / 100.0), "Cable", IRON,
                           collide=False, rotation=unreal.MathLibrary.make_rot_from_z(d))
    elif kind == "flame":
        _, x, y, top, facing, delay, warn, burn, off, respawn = piece
        actor = spawn(bp_class(HELL + "/BP_FlameJet"), unreal.Vector(x, y, top), "Flame Jet", yaw(facing))
        configure(actor, (("StartDelay", delay), ("WarnSeconds", warn), ("BurnSeconds", burn), ("OffSeconds", off), ("RespawnLocation", spots[respawn])))
    elif kind == "sun":
        _, x, y, top, respawn = piece[:5]
        # A sun with a bigger range (the layout gives its size) is BP_TowerSun, made by setup_tower_sun.py: sizes set
        # on a placed BP_Sun's components did not stick.
        path = HEAVEN + "/BP_TowerSun" if len(piece) > 5 else GIMMICKS + "/Sun/BP_Sun"
        actor = spawn(bp_class(path), unreal.Vector(x, y, top), "Sun")
        actor.set_editor_property("RespawnPoint", spot_points[respawn])
        if len(piece) > 5:
            actor.set_editor_property("GrabChance", 0.3)   # (the user's choice for the tower, 2026-11-16)
            # Where it is about to land, shown on the ground while it aims and charges (setup_sun_marker.py).
            marker = spawn(bp_class(HEAVEN + "/BP_SunMarker"), unreal.Vector(x, y, top), "Sun Marker")
            marker.set_editor_property("Sun", actor)
    elif kind == "rewind":
        _, x, y, top = piece
        actor = spawn(bp_class(GIMMICKS + "/BP_TimeRewindArea"), unreal.Vector(x, y, top), "Time Rewind Area")
        configure(actor, (("CountSeconds", 3.0), ("CooldownSeconds", 10.0), ("NightSunPitch", 15.0), ("NightBlendSpeed", 1.0), ("TextHeight", 140.0)))
    elif kind == "cages":
        _, x, y, top, dest, pair_id = piece
        target = spawn(unreal.TargetPoint, unreal.Vector(*dest), "Cage Destination")
        cage_class = bp_class(CAGE_DOOR)
        cage_a = spawn(cage_class, unreal.Vector(x - 300.0, y, top), "Choice Cage A")
        cage_b = spawn(cage_class, unreal.Vector(x + 300.0, y, top), "Choice Cage B")
        for cage in (cage_a, cage_b):
            cage.set_editor_property("Destination", target)
        pair = spawn(bp_class(HELL + "/BP_CagePair"), unreal.Vector(x, y, top + 150.0), "Cage Pair")
        configure(pair, (("CageA", cage_a), ("CageB", cage_b), ("PairId", pair_id)))
    elif kind == "speed":
        _, x, y, top = piece
        spawn(bp_class(ITEMS + "/BP_Item"), unreal.Vector(x, y, top + 100.0), "Speed Item")
    elif kind == "coin":
        _, x, y, top = piece
        spawn(bp_class(COIN), unreal.Vector(x, y, top + 100.0), "Star Coin")
        coins += 1
    elif kind == "flag":
        _, x, y, top = piece
        # a flag stuck in the ground, broken until touched (since 2026-11-19; was a pickup item)
        spawn(bp_class(ITEMS + "/Checkpoint/BP_CheckpointFlag"), unreal.Vector(x, y, top), "Checkpoint Flag")
    elif kind == "trap":
        _, x0, x1, y0, y1, top = piece
        actor = spawn(bp_class(MACHINE + "/BP_CageTrap"), unreal.Vector((x0 + x1) / 2.0, (y0 + y1) / 2.0, top), "Cage Trap")
        for component in actor.get_components_by_class(unreal.BoxComponent):
            component.set_editor_property("box_extent", unreal.Vector((x1 - x0) / 2.0, (y1 - y0) / 2.0, 100.0))
        configure(actor, (("RespawnLocation", START), ("RespawnYaw", 90.0)))
    elif kind == "lure":
        _, x, y, top = piece
        box(x - 50.0, x + 50.0, y - 50.0, y + 50.0, top, top + 70.0, "Gold Pedestal", GOLD)
        mesh_actor(unreal.load_asset(SPHERE), unreal.Vector(x, y, top + 70.0), unreal.Vector(0.6, 0.6, 0.6), "Gold Ball", GOLD)
    elif kind in ("mech", "door"):
        if kind == "door":
            _, lever_name, x, y, size, look = piece
            top, offset, delay, seconds, back, name = B + size[2], (0.0, 0.0, -size[2] - 50.0), 1.0, 3.0, None, "Gate Door"
        else:
            _, lever_name, x, y, top, size, offset, delay, seconds, back, look, name = piece
        actor = spawn(bp_class(AREA + "/BP_Mechanism"), unreal.Vector(x, y, top), name)
        actor.set_actor_scale3d(unreal.Vector(size[0] / 100.0, size[1] / 100.0, size[2] / 100.0))
        configure(actor, (("Lever", levers[lever_name]), ("MoveOffset", unreal.Vector(*offset)), ("StartDelay", delay),
                          ("Duration", seconds), ("Returns", back is not None)))
        if back:
            configure(actor, (("ReturnAfter", back[0]), ("ReturnSeconds", back[1])))
        for component in actor.get_components_by_class(unreal.StaticMeshComponent):
            component.set_material(0, LOOKS[look])
    elif kind == "camera":
        _, lever_name, eye, look_at, seconds = piece
        eye_v, look_v = unreal.Vector(*eye), unreal.Vector(*look_at)
        camera = spawn(unreal.CameraActor, eye_v, "Show Camera " + lever_name, unreal.MathLibrary.find_look_at_rotation(eye_v, look_v))
        camera.get_editor_property("camera_component").set_editor_property("constrain_aspect_ratio", False)
        configure(levers[lever_name], (("ShowCamera", camera), ("ShowSeconds", seconds)))
    elif kind == "shaft":
        _, x, y, z_top, z_bottom, r = piece
        shaft(x, y, z_top, z_bottom, r)
    elif kind == "lamp":
        _, x, y, z, color = piece
        lamp(x, y, z, color)
    elif kind == "sign":
        _, x, y, z, facing, words = piece
        text(x, y, z, facing, words)
    elif kind == "goal":
        # On to hidden area 2 the way area 1 goes on to area 2: the gear (BP_GearExit; its arrival is in LV_Secret2).
        _, x, y, top = piece
        spawn(unreal.TargetPoint, unreal.Vector(x, y, top + 100.0), "Goal Spot")
        exit_gear = spawn(bp_class(AREA + "/BP_GearExit"), unreal.Vector(x, y, top), "Gear Exit")
        exit_gear.set_editor_property("NextLevel", "LV_Secret2")
    elif kind == "doomed":
        _, x, y, top, respawn, lever_name = piece
        doomed = spawn(bp_class(AREA + "/BP_SteamCatapult"), unreal.Vector(x, y, top), "Doomed Catapult")
        if library.does_asset_exist(AREA + "/BP_CatapultSmash"):
            smash = spawn(bp_class(AREA + "/BP_CatapultSmash"), unreal.Vector(x, y, top), "Catapult Smash")
            configure(smash, (("Catapult", doomed), ("Respawn", spot_points[respawn]), ("Lever", levers[lever_name])))
            for other in actors.get_all_level_actors():
                if other.get_class().get_name() == "BP_GearArrival_C":
                    smash.set_editor_property("Arrival", other)
        else:
            lines.append("BP_CatapultSmash not made yet: the catapult stays whole")
    elif kind == "exit_catapult":
        _, x, y, top, sink, lever_name = piece
        catapult = spawn(bp_class(AREA + "/BP_SteamCatapult"), unreal.Vector(x, y, top - sink), "Exit Catapult")
        catapult.set_editor_property("NextLevel", NEXT_LEVEL.split("/")[-1])
        riser = spawn(bp_class(AREA + "/BP_ActorRiser"), unreal.Vector(x, y, top), "Catapult Riser")
        configure(riser, (("Lever", levers[lever_name]), ("Target", catapult), ("RiseOffset", unreal.Vector(0.0, 0.0, sink)),
                          ("RiseSeconds", 4.0)))
    elif kind == "debris":
        _, x, y, z, size, d_yaw, d_pitch, d_roll, look = piece
        mesh_actor(unreal.load_asset(CUBE), unreal.Vector(x, y, z), unreal.Vector(size / 100.0, size / 100.0, size / 100.0),
                   "Debris", LOOKS[look], collide=False, rotation=unreal.Rotator(roll=d_roll, pitch=d_pitch, yaw=d_yaw))
    elif kind == "catcher":
        _, x0, x1, y0, y1, z = piece
        catcher = spawn(bp_class(MACHINE + "/BP_FallCatcher"), unreal.Vector((x0 + x1) / 2.0, (y0 + y1) / 2.0, z), "Fall Catcher")
        catcher.set_actor_scale3d(unreal.Vector((x1 - x0) / 100.0, (y1 - y0) / 100.0, 4.0))
    else:
        raise RuntimeError("Unknown piece " + kind)

# ----- area 1's own start: every star coin of the level counted; the hidden stage's track -----
all_coins = [a for a in actors.get_all_level_actors() if a.get_class().get_name() == "BP_StarCoin_C"]
for actor in actors.get_all_level_actors():
    kind = actor.get_class().get_name()
    if kind == "BP_AreaStart_C":
        actor.set_editor_property("AreaCoins", len(all_coins))
    elif kind == "BP_AreaBgm_C":
        actor.set_editor_property("AreaBgm", unreal.load_asset("/Game/Sound/BGM/BGM_Secret"))
lines.append("{} star coins in all".format(len(all_coins)))

# ===== sky: a blood-red dusk, the sun just under the horizon, red haze below, wreckage everywhere =====
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

# Wreckage: loose blocks of the old town tumbling near the route (well below or aside of it), and big ones far out.
X0, X1, Y0, Y1 = route.bounds
rand = random.Random(11)
looks = ("ruin", "plaster", "tile", "paving", "rock", "ruin", "ruin")
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
    lines.append("  {:<40} gap {:>5.0f} rise {:>6.0f} (limit {:>5.0f})".format(name, g, rise, limit))
for name, z in route.heights.items():
    lines.append("  {:<18} {:>7.0f}  ({:+.0f} from the start)".format(name, z, z - B))
lines.append("{} coins; {} jumps; {} actors".format(coins, len(route.checks), counter[0]))
lines.append("{} saved {}".format(LEVEL, level_subsystem.save_current_level()))

with open(os.path.join(unreal.Paths.project_saved_dir(), "secret2_build.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
