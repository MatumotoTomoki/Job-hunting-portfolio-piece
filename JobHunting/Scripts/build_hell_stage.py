# Builds the hell stage in LV_Hell: rock pillars standing in a lava sea, a run of six sections, and the exit at the top.
#   BP_HellLava   the lava sea: a glowing Surface and a KillZone above it. Touching it sends the player back to
#                 RespawnLocation (hell's PlayerStart) behind a quick fade.
#   BP_FlameJet   a vent that keeps erupting: the CageFire effect flares up for WarnSeconds, then the Jet (FlameJet
#                 effect, import_flame_jet.py) stands for BurnSeconds (touching it while Burning sends the player back like the lava), then OffSeconds of
#                 nothing. StartDelay staggers a row of them.
#   M_HellGlow    an unlit-looking glow (Color x Glow into Emissive), with MI_HellLava and MI_HellFlame.
# The sections reuse BP_FallingFloor, BP_MovingPlatform and BP_TimedPlatform. Gaps and rises come from the player's
# own jump (JumpZVelocity, gravity, walk speed), measured without any item, so every jump can be made with none.
# Everything this script places is labelled "HS ..." and is rebuilt on every run; the old placeholder steps are
# removed; Hell Exit, the lights, the fog and the PlayerStart are kept (the exit is moved to the top).
# The graphs come from BP_HellLava_EventGraph.txt and BP_FlameJet_EventGraph.txt. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\build_hell_stage.py -unattended -nop4 -nosplash -stdout
import math
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Hell"
LAVA = DIR + "/BP_HellLava"
FLAME = DIR + "/BP_FlameJet"
GLOW = DIR + "/M_HellGlow"
HELL_LEVEL = "/Game/LV_Hell"
GIMMICKS = "/Game/ThirdPerson/Blueprints/Gimmicks"
ELEVATOR = GIMMICKS + "/BP_Elevator"
CUBE = "/Engine/BasicShapes/Cube"
CYLINDER = "/Engine/BasicShapes/Cylinder"
CAGE_FIRE = "/Game/FX/Effekseer/CageFire/CageFire"
GAME_MODE = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonGameMode"
FALLBACK_CHARACTER = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter1"

START = unreal.Vector(0.0, 0.0, 100.0)   # hell's PlayerStart
LAVA_Z = -250.0                          # the lava surface
PILLAR_FOOT = LAVA_Z - 150.0             # pillars stand in the lava down to here
PREFIX = "HS "

library = unreal.EditorAssetLibrary
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
materials = unreal.MaterialEditingLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
lines = []

REAL = pins.get_basic_type_by_name("real")
BOOL = pins.get_basic_type_by_name("bool")
VECTOR = pins.get_struct_type(unreal.Vector.static_struct())


# ----- what a plain jump can do -----
def player_defaults():
    pawn_class = None
    try:
        mode = unreal.load_asset(GAME_MODE)
        pawn_class = unreal.get_default_object(mode.generated_class()).get_editor_property("default_pawn_class")
    except Exception as error:
        lines.append("game mode pawn not read: {}".format(error))
    if pawn_class is None:
        pawn_class = unreal.load_asset(FALLBACK_CHARACTER).generated_class()
    return pawn_class, unreal.get_default_object(pawn_class)


pawn_class, pawn = player_defaults()
move = pawn.get_editor_property("character_movement")
jump_z = move.get_editor_property("jump_z_velocity")
gravity = 980.0 * move.get_editor_property("gravity_scale")
speed = move.get_editor_property("max_walk_speed")
air_time = 2.0 * jump_z / gravity
REACH = speed * air_time                 # flat jump, running, edge to edge
APEX = jump_z * jump_z / (2.0 * gravity)
lines.append("player {}: JumpZ {:.0f}, gravity {:.0f}, walk {:.0f}, jumps {} -> reach {:.0f} cm, apex {:.0f} cm".format(
    pawn_class.get_name(), jump_z, gravity, speed, pawn.get_editor_property("jump_max_count"), REACH, APEX))
# A rise of r shortens the reach: the player lands earlier on the way down.
def reach_up(rise):
    fall = APEX - rise
    if fall <= 0:
        return 0.0
    return speed * (jump_z / gravity + math.sqrt(2.0 * fall / gravity))


# ----- blueprint helpers -----
def add_variables(blueprint, variables):
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
    return unreal.get_default_object(blueprint.generated_class())


def components(blueprint):
    found = {}
    for handle in subsystem.k2_gather_subobject_data_for_blueprint(blueprint):
        component = data_library.get_associated_object(data_library.get_data(handle))
        if component is not None:
            found[component.get_name().replace("_GEN_VARIABLE", "")] = (handle, component)
    return found


def add_component(blueprint, component_class, name):
    existing = components(blueprint)
    if name in existing:
        return existing[name][1], False
    root = subsystem.k2_gather_subobject_data_for_blueprint(blueprint)[0]
    params = unreal.AddNewSubobjectParams(parent_handle=root, new_class=component_class, blueprint_context=blueprint)
    handle, _ = subsystem.add_new_subobject(params)
    if not data_library.is_handle_valid(handle):
        raise RuntimeError("Could not add {} to {}".format(name, blueprint.get_name()))
    subsystem.rename_subobject(handle, unreal.Text(name))
    lines.append("{}: component {}".format(blueprint.get_name(), name))
    return data_library.get_associated_object(data_library.get_data(handle)), True


def actor_blueprint(path):
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    folder, name = path.rsplit("/", 1)
    lines.append("created " + path)
    return tools.create_asset(name, folder, unreal.Blueprint, factory)


def shape(component, mesh_path, material, location, scale):
    component.set_editor_property("static_mesh", unreal.load_asset(mesh_path))
    component.set_material(0, material)
    component.set_editor_property("relative_location", location)
    component.set_editor_property("relative_scale3d", scale)
    component.set_collision_profile_name("NoCollision")


# ----- the glow material -----
def glow_material():
    if library.does_asset_exist(GLOW):
        return unreal.load_asset(GLOW)
    folder, name = GLOW.rsplit("/", 1)
    material = tools.create_asset(name, folder, unreal.Material, unreal.MaterialFactoryNew())
    color = materials.create_material_expression(material, unreal.MaterialExpressionVectorParameter, -600, 0)
    color.set_editor_property("parameter_name", "Color")
    color.set_editor_property("default_value", unreal.LinearColor(1.0, 0.3, 0.02, 1.0))
    glow = materials.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -600, 250)
    glow.set_editor_property("parameter_name", "Glow")
    glow.set_editor_property("default_value", 5.0)
    times = materials.create_material_expression(material, unreal.MaterialExpressionMultiply, -300, 100)
    materials.connect_material_expressions(color, "", times, "A")
    materials.connect_material_expressions(glow, "", times, "B")
    materials.connect_material_property(color, "", unreal.MaterialProperty.MP_BASE_COLOR)
    materials.connect_material_property(times, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    materials.recompile_material(material)
    library.save_asset(GLOW, False)
    lines.append("created " + GLOW)
    return material


def glow_instance(name, color, strength):
    path = "{}/{}".format(DIR, name)
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    instance = tools.create_asset(name, DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    materials.set_material_instance_parent(instance, glow_material())
    materials.set_material_instance_vector_parameter_value(instance, "Color", unreal.LinearColor(color[0], color[1], color[2], 1.0))
    materials.set_material_instance_scalar_parameter_value(instance, "Glow", strength)
    library.save_asset(path, False)
    lines.append("created " + path)
    return instance


lava_look = glow_instance("MI_HellLava", (1.0, 0.22, 0.02), 4.0)
flame_look = glow_instance("MI_HellFlame", (1.0, 0.45, 0.06), 10.0)
rock = unreal.load_asset(DIR + "/MI_HellRock")

# ----- BP_HellLava: scale the actor in X and Y to cover the stage -----
lava_bp = actor_blueprint(LAVA)
surface, made = add_component(lava_bp, unreal.StaticMeshComponent, "Surface")
if made:
    shape(surface, CUBE, lava_look, unreal.Vector(0.0, 0.0, -5.0), unreal.Vector(1.0, 1.0, 0.1))
kill, made = add_component(lava_bp, unreal.BoxComponent, "KillZone")
if made:
    # From 50 cm above the surface down: the player is caught as they sink in.
    kill.set_editor_property("box_extent", unreal.Vector(50.0, 50.0, 150.0))
    kill.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, -100.0))
    kill.set_collision_profile_name("OverlapOnlyPawn")
lava_defaults = add_variables(lava_bp, [("RespawnLocation", VECTOR, True), ("Busy", BOOL, False)])
lava_defaults.set_editor_property("RespawnLocation", START)
library.save_asset(LAVA, False)

# ----- BP_FlameJet -----
flame_bp = actor_blueprint(FLAME)
vent, made = add_component(flame_bp, unreal.StaticMeshComponent, "Vent")
if made:
    shape(vent, CYLINDER, rock, unreal.Vector(0.0, 0.0, 2.0), unreal.Vector(1.4, 1.4, 0.04))
# The fire column itself is the Jet emitter (FlameJet effect), added by import_flame_jet.py.
hit, made = add_component(flame_bp, unreal.BoxComponent, "HitBox")
if made:
    # Across the whole 200 cm walkway; 2 x 90 cm along it.
    hit.set_editor_property("box_extent", unreal.Vector(90.0, 140.0, 200.0))
    hit.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 200.0))
    hit.set_collision_profile_name("OverlapOnlyPawn")
fire, made = add_component(flame_bp, unreal.load_class(None, "/Script/Effekseer.EffekseerEmitterComponent"), "Fire")
if made:
    fire.set_editor_property("Effect", unreal.load_asset(CAGE_FIRE))
    fire.set_editor_property("IsLooping", True)
    fire.set_editor_property("auto_activate", False)
flame_defaults = add_variables(flame_bp, [
    ("StartDelay", REAL, True), ("WarnSeconds", REAL, True), ("BurnSeconds", REAL, True), ("OffSeconds", REAL, True),
    ("RespawnLocation", VECTOR, True), ("Burning", BOOL, False), ("Busy", BOOL, False),
])
for name, value in (("WarnSeconds", 0.6), ("BurnSeconds", 1.0), ("OffSeconds", 1.6)):
    if flame_defaults.get_editor_property(name) == 0.0:
        flame_defaults.set_editor_property(name, value)
flame_defaults.set_editor_property("RespawnLocation", START)
library.save_asset(FLAME, False)

# ----- the platform gimmicks: all share the elevator's floor, centred on the actor -----
def elevator_half():
    source = unreal.load_asset(ELEVATOR)
    for handle in subsystem.k2_gather_subobject_data_for_blueprint(source):
        component = data_library.get_object(data_library.get_data(handle))
        if isinstance(component, unreal.StaticMeshComponent):
            scale = component.get_editor_property("relative_scale3d")
            extent = component.get_editor_property("static_mesh").get_bounds().box_extent
            return unreal.Vector(extent.x * scale.x, extent.y * scale.y, extent.z * scale.z)
    raise RuntimeError("No floor in " + ELEVATOR)


PLAT = elevator_half()
lines.append("platform half size {}".format(PLAT))
falling_class = unreal.load_asset(GIMMICKS + "/BP_FallingFloor").generated_class()
moving_class = unreal.load_asset(GIMMICKS + "/BP_MovingPlatform").generated_class()
timed_class = unreal.load_asset(GIMMICKS + "/BP_TimedPlatform").generated_class()

# ----- LV_Hell -----
if not level_subsystem.load_level(HELL_LEVEL):
    raise RuntimeError("Could not open " + HELL_LEVEL)
for actor in actors.get_all_level_actors():
    label = actor.get_actor_label()
    if label.startswith(PREFIX) or label.startswith("Hell Step") or label in ("Hell Floor", "Hell Exit Floor"):
        actors.destroy_actor(actor)
by_label = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
counter = [0]


def spawn(actor_class, location, name, folder, yaw=0.0):
    actor = actors.spawn_actor_from_class(actor_class, location, unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw))
    if not actor:
        raise RuntimeError("Could not spawn " + name)
    counter[0] += 1
    actor.set_actor_label("{}{:02d} {}".format(PREFIX, counter[0], name))
    actor.set_folder_path("HellStage/" + folder)
    return actor


def pillar(x, y, top, size_x, size_y, folder, name="Pillar"):
    # A rock standing in the lava, its top at `top`.
    actor = spawn(unreal.StaticMeshActor, unreal.Vector(x, y, (top + PILLAR_FOOT) / 2.0), name, folder)
    mesh = actor.get_editor_property("static_mesh_component")
    mesh.set_static_mesh(unreal.load_asset(CUBE))
    mesh.set_material(0, rock)
    actor.set_actor_scale3d(unreal.Vector(size_x / 100.0, size_y / 100.0, (top - PILLAR_FOOT) / 100.0))
    return actor


def platform(actor_class, x, y, top, name, folder, settings=()):
    actor = spawn(actor_class, unreal.Vector(x, y, top - PLAT.z), name, folder)
    for key, value in settings:
        actor.set_editor_property(key, value)
    return actor


def flame(x, y, top, start_delay, folder, warn=0.6, burn=1.0, off=1.6):
    actor = spawn(flame_bp.generated_class(), unreal.Vector(x, y, top), "Flame Jet", folder)
    for key, value in (("StartDelay", start_delay), ("WarnSeconds", warn), ("BurnSeconds", burn), ("OffSeconds", off), ("RespawnLocation", START)):
        actor.set_editor_property(key, value)
    return actor


def rest(edge, top, folder, size=400.0):
    # A safe rock to catch the breath on; returns its far edge.
    pillar(edge + size / 2.0, 0.0, top, size, size, folder, "Rest")
    return edge + size


# The gaps, as parts of a plain running jump.
EASY, MID, HARD = 0.45 * REACH, 0.55 * REACH, 0.65 * REACH
RISE = 0.45 * APEX
lines.append("gaps {:.0f} / {:.0f} / {:.0f} cm, rise {:.0f} cm".format(EASY, MID, HARD, RISE))
top = 0.0

# 0. The start.
edge = rest(-300.0, top, "0 Start", 600.0)

# 1. Stepping stones, weaving left and right.
for i, (side, lift) in enumerate(((0.0, 0.0), (140.0, RISE), (-140.0, RISE), (140.0, 0.0), (0.0, -RISE))):
    top += lift
    gap = HARD if i in (2, 3) else MID
    gap = min(gap, 0.8 * reach_up(max(lift, 0.0)))
    pillar(edge + gap + 90.0, side, top, 180.0, 180.0, "1 Stones", "Stone")
    edge += gap + 180.0
edge = rest(edge + MID, top, "1 Stones")

# 2. Falling floors: keep running.
for i in range(4):
    platform(falling_class, edge + EASY + PLAT.x, 0.0, top, "Falling Floor", "2 Falling")
    edge += EASY + 2.0 * PLAT.x
edge = rest(edge + EASY, top, "2 Falling")

# 3. Moving platforms swinging across a wide lava gap, out of step with each other.
SWING = 650.0
for i in range(3):
    y = -SWING / 2.0 if i % 2 == 0 else SWING / 2.0
    offset = unreal.Vector(0.0, SWING if i % 2 == 0 else -SWING, 0.0)
    platform(moving_class, edge + MID + PLAT.x, y, top, "Moving Platform", "3 Moving",
             (("MoveOffset", offset), ("MoveSeconds", 2.2 + 0.3 * i), ("WaitSeconds", 0.4)))
    edge += MID + 2.0 * PLAT.x
edge = rest(edge + MID, top, "3 Moving")

# 4. The flame bridge: a narrow walkway with a wave of jets.
BRIDGE = 3000.0
pillar(edge + BRIDGE / 2.0, 0.0, top, BRIDGE, 200.0, "4 Flames", "Bridge")
for i in range(6):
    flame(edge + 300.0 + 480.0 * i, 0.0, top, 0.45 * i, "4 Flames")
edge = rest(edge + BRIDGE, top, "4 Flames")

# 5. Up: a lift, then disappearing steps.
LIFT = 450.0
platform(moving_class, edge + EASY + PLAT.x, 0.0, top, "Lift", "5 Up",
         (("MoveOffset", unreal.Vector(0.0, 0.0, LIFT)), ("MoveSeconds", 2.5), ("WaitSeconds", 1.0)))
edge += EASY + 2.0 * PLAT.x
top += LIFT
pillar(edge + EASY + 150.0, 0.0, top, 300.0, 300.0, "5 Up", "Ledge")
edge += EASY + 300.0
for i in range(4):
    top += RISE
    platform(timed_class, edge + MID + PLAT.x, 0.0, top, "Timed Platform", "5 Up",
             (("VisibleSeconds", 2.0), ("HiddenSeconds", 1.2), ("FadeSeconds", 0.4), ("StartDelay", 0.6 * i)))
    edge += MID + 2.0 * PLAT.x
edge = rest(edge + MID, top, "5 Up")

# 6. The last climb: falling floors going up, then two jets guarding the way to the exit.
for i in range(3):
    top += RISE
    gap = min(MID, 0.8 * reach_up(RISE))
    platform(falling_class, edge + gap + PLAT.x, 0.0, top, "Falling Floor", "6 Final")
    edge += gap + 2.0 * PLAT.x
edge = rest(edge + EASY, top, "6 Final")
pillar(edge + 600.0, 0.0, top, 1200.0, 200.0, "6 Final", "Bridge")
flame(edge + 350.0, 0.0, top, 0.0, "6 Final", burn=1.2, off=1.2)
flame(edge + 850.0, 0.0, top, 1.0, "6 Final", burn=1.2, off=1.2)
edge += 1200.0
pillar(edge + 300.0, 0.0, top, 600.0, 600.0, "6 Final", "Exit Rock")
exit_actor = by_label.get("Hell Exit")
if exit_actor:
    exit_actor.set_actor_location(unreal.Vector(edge + 300.0, 0.0, top), False, False)
else:
    lines.append("WARNING: Hell Exit not found")
lines.append("stage length {:.0f} cm, exit top {:.0f} cm".format(edge + 600.0, top))

# The lava sea under all of it.
length = edge + 600.0 + 2000.0
sea = spawn(lava_bp.generated_class(), unreal.Vector(length / 2.0 - 1000.0, 0.0, LAVA_Z), "Lava Sea", "0 Start")
sea.set_actor_scale3d(unreal.Vector(length / 100.0, 40.0, 1.0))
sea.set_editor_property("RespawnLocation", START)

start = by_label.get("PlayerStart")
if start:
    start.set_actor_location(START, False, False)
lines.append("LV_Hell saved {}".format(level_subsystem.save_current_level()))

with open(os.path.join(unreal.Paths.project_saved_dir(), "hell_stage_build.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
