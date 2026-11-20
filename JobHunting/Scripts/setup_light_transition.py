# Area 3 -> 4 (the user, 2026-11-20): a pillar of light comes down through area 3's summit gate; stepping into it, the
# player floats up and melts into white; in area 4 they come down inside the pillar, and then the light thins away to
# nothing, leaving the dim heaven ("the heaven that lost its light").
#   Gimmicks/Area/M_LightShaft + MI_LightShaft  additive, unlit, two-sided: Color x Intensity x Opacity, soft at its
#       edges (1 - Fresnel) and at both ends (UV V), with light drifting up inside it (CloudPuff panned upward)
#   BP_LightGate (area 3's exit, in place of BP_AreaExit): Shaft (the pillar, grown down from ShaftHeight by the
#       graph), Approach (walking near brings the light down), Center (stepping into it), MotesFx (LightMotes), sounds
#       DescendSound, AscendSound. Then: held still, floated up RiseHeight over RiseSeconds; from FadeAt of that, white,
#       the item effects saved, ChangingArea and LightArrival set, NextLevel.
#   BP_LightArrival (area 4, at the PlayerStart): only after the gate (LightArrival): from white, the player comes down
#       DescendHeight inside the pillar, lands, the pillar thins and fades over VanishSeconds, then control.
#   BP_MyGameInstance: LightArrival.  Effects /Game/FX/Effekseer/LightMotes; sounds S_BeamDescend/Ascend/Fade.
# Graphs: BP_LightGate_EventGraph.txt, BP_LightArrival_EventGraph.txt (Generators/gen_light_transition.ps1).
# Levels are changed only with --levels (LV_Area3_Sky's exit swapped, LV_Area4_Heaven's arrival placed). Editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript "-script=<full path>\setup_light_transition.py [--levels]" -unattended -nop4 -nosplash -stdout
import os
import sys

import unreal

AREA = "/Game/ThirdPerson/Blueprints/Gimmicks/Area"
FX = "/Game/FX/Effekseer/LightMotes"
GAME_INSTANCE = "/Game/ThirdPerson/Blueprints/BP_MyGameInstance"
PROJECT = os.path.abspath(unreal.Paths.project_dir())
CYLINDER = "/Engine/BasicShapes/Cylinder"
LEVELS = "--levels" in " ".join(sys.argv)

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
TYPES = {"bool": pins.get_basic_type_by_name("bool"), "real": pins.get_basic_type_by_name("real"),
         "name": pins.get_basic_type_by_name("name"), "vector": pins.get_struct_type(unreal.Vector.static_struct())}
lines = []


def import_file(path, destination):
    task = unreal.AssetImportTask()
    task.filename = path
    task.destination_path = destination
    task.automated = True
    task.save = True
    task.replace_existing = True
    tools.import_asset_tasks([task])
    asset = destination + "/" + os.path.splitext(os.path.basename(path))[0]
    lines.append("imported " + asset)
    return unreal.load_asset(asset)


# ----- effects, sounds -----
for name in ("CloudPuff", "Glint"):
    import_file(os.path.join(PROJECT, "SourceArt", "Effects", "LightMotes", "Texture", name + ".png"), FX + "/Texture")
motes = import_file(os.path.join(PROJECT, "SourceArt", "Effects", "LightMotes", "LightMotes.efk"), FX)
sounds = {n: import_file(os.path.join(PROJECT, "SourceArt", "Sounds", n + ".wav"), AREA) for n in ("S_BeamDescend", "S_BeamAscend", "S_BeamFade")}

# ----- the material -----
path = AREA + "/M_LightShaft"
if not library.does_asset_exist(path):
    m = tools.create_asset("M_LightShaft", AREA, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE)
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    m.set_editor_property("two_sided", True)

    def node(kind, x, y):
        return editing.create_material_expression(m, kind, x, y)

    def param(kind, name, value, x, y):
        n = node(kind, x, y)
        n.set_editor_property("parameter_name", name)
        n.set_editor_property("default_value", value)
        return n

    def const(value, x, y):
        n = node(unreal.MaterialExpressionConstant, x, y)
        n.set_editor_property("r", value)
        return n

    def link(a, b, pin):
        editing.connect_material_expressions(a, "", b, pin)

    color = param(unreal.MaterialExpressionVectorParameter, "Color", unreal.LinearColor(1.0, 0.92, 0.72, 1.0), -1200, -300)
    intensity = param(unreal.MaterialExpressionScalarParameter, "Intensity", 2.5, -1200, -150)
    opacity = param(unreal.MaterialExpressionScalarParameter, "Opacity", 1.0, -1200, -50)
    uv = node(unreal.MaterialExpressionTextureCoordinate, -1200, 100)
    v = node(unreal.MaterialExpressionComponentMask, -1050, 100)
    for channel, on in (("r", False), ("g", True), ("b", False), ("a", False)):
        v.set_editor_property(channel, on)
    one_minus_v = node(unreal.MaterialExpressionOneMinus, -900, 150)
    ends = node(unreal.MaterialExpressionMultiply, -750, 100)
    ends4 = node(unreal.MaterialExpressionMultiply, -600, 100)
    fresnel = node(unreal.MaterialExpressionFresnel, -1050, 300)
    fresnel.set_editor_property("exponent", 1.5)
    edge = node(unreal.MaterialExpressionOneMinus, -900, 300)
    drift_uv = node(unreal.MaterialExpressionTextureCoordinate, -1200, 500)
    drift_uv.set_editor_property("u_tiling", 2.0)
    drift_uv.set_editor_property("v_tiling", 0.6)
    pan = node(unreal.MaterialExpressionPanner, -1050, 500)
    pan.set_editor_property("speed_x", 0.0)
    pan.set_editor_property("speed_y", -0.12)
    sample = node(unreal.MaterialExpressionTextureSample, -850, 500)
    sample.set_editor_property("texture", unreal.load_asset(FX + "/Texture/CloudPuff"))
    shimmer_part = node(unreal.MaterialExpressionMultiply, -650, 500)
    shimmer = node(unreal.MaterialExpressionAdd, -500, 500)
    a1 = node(unreal.MaterialExpressionMultiply, -900, -250)
    a2 = node(unreal.MaterialExpressionMultiply, -750, -200)
    a3 = node(unreal.MaterialExpressionMultiply, -450, -100)
    a4 = node(unreal.MaterialExpressionMultiply, -300, 0)
    a5 = node(unreal.MaterialExpressionMultiply, -150, 100)
    link(uv, v, "")
    link(v, one_minus_v, "")
    link(v, ends, "A")
    link(one_minus_v, ends, "B")
    link(ends, ends4, "A")
    link(const(4.0, -750, 200), ends4, "B")
    link(fresnel, edge, "")
    link(drift_uv, pan, "Coordinate")
    link(pan, sample, "UVs")
    editing.connect_material_expressions(sample, "R", shimmer_part, "A")
    link(const(0.45, -800, 650), shimmer_part, "B")
    link(shimmer_part, shimmer, "A")
    link(const(0.55, -650, 650), shimmer, "B")
    link(color, a1, "A")
    link(intensity, a1, "B")
    link(a1, a2, "A")
    link(opacity, a2, "B")
    link(a2, a3, "A")
    link(ends4, a3, "B")
    link(a3, a4, "A")
    link(edge, a4, "B")
    link(a4, a5, "A")
    link(shimmer, a5, "B")
    editing.connect_material_property(a5, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    editing.recompile_material(m)
    library.save_asset(path, False)
    lines.append("created " + path)
mi_path = AREA + "/MI_LightShaft"
if library.does_asset_exist(mi_path):
    shaft_mi = unreal.load_asset(mi_path)
else:
    shaft_mi = tools.create_asset("MI_LightShaft", AREA, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    editing.set_material_instance_parent(shaft_mi, unreal.load_asset(path))
    library.save_asset(mi_path, False)
    lines.append("created " + mi_path)

# ----- the game instance's flag -----
gi_bp = unreal.load_asset(GAME_INSTANCE)
try:
    unreal.get_default_object(gi_bp.generated_class()).get_editor_property("LightArrival")
except Exception:
    if not pins.add_member_variable(gi_bp, "LightArrival", TYPES["bool"]):
        raise RuntimeError("Could not add LightArrival")
    pins.compile_blueprint(gi_bp)
    library.save_asset(GAME_INSTANCE, False)
    lines.append("BP_MyGameInstance: LightArrival added")


def actor_blueprint(name):
    p = AREA + "/" + name
    if library.does_asset_exist(p):
        return unreal.load_asset(p)
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    lines.append("created " + p)
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
        return found[name][1]
    root = found["DefaultSceneRoot"][0] if "DefaultSceneRoot" in found else subsystem.k2_gather_subobject_data_for_blueprint(bp)[0]
    params = unreal.AddNewSubobjectParams(parent_handle=root, new_class=component_class, blueprint_context=bp)
    handle, _ = subsystem.add_new_subobject(params)
    subsystem.rename_subobject(handle, unreal.Text(name))
    lines.append("{}: component {}".format(bp.get_name(), name))
    return data_library.get_associated_object(data_library.get_data(handle))


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


def common(bp):
    shaft = add(bp, unreal.StaticMeshComponent, "Shaft")
    shaft.set_editor_property("static_mesh", unreal.load_asset(CYLINDER))
    shaft.set_material(0, shaft_mi)
    shaft.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 1500.0))
    shaft.set_editor_property("relative_scale3d", unreal.Vector(3.0, 3.0, 30.0))
    shaft.set_collision_profile_name("NoCollision")
    shaft.set_editor_property("cast_shadow", False)
    fx = add(bp, unreal.load_class(None, "/Script/Effekseer.EffekseerEmitterComponent"), "MotesFx")
    fx.set_editor_property("Effect", motes)
    fx.set_editor_property("IsLooping", True)
    fx.set_editor_property("auto_activate", False)


def audio(bp, name, sound):
    a = add(bp, unreal.AudioComponent, name)
    a.set_editor_property("sound", sound)
    a.set_editor_property("auto_activate", False)
    a.set_editor_property("allow_spatialization", False)


# ----- BP_LightGate -----
gate = actor_blueprint("BP_LightGate")
add(gate, unreal.SceneComponent, "DefaultSceneRoot")
common(gate)
approach = add(gate, unreal.BoxComponent, "Approach")
approach.set_editor_property("box_extent", unreal.Vector(600.0, 600.0, 400.0))
approach.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 200.0))
approach.set_collision_profile_name("OverlapOnlyPawn")
center = add(gate, unreal.BoxComponent, "Center")
center.set_editor_property("box_extent", unreal.Vector(10.0, 10.0, 100.0))   # the user's value (2026-11-20; was 90)
center.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 100.0))
center.set_collision_profile_name("OverlapOnlyPawn")
audio(gate, "DescendSound", sounds["S_BeamDescend"])
audio(gate, "AscendSound", sounds["S_BeamAscend"])
variables(gate, [
    ("NextLevel", "name", True, None), ("Descended", "bool", False, None), ("DescendAt", "real", False, None),
    ("Ascending", "bool", False, None), ("AscendAt", "real", False, None), ("Leaving", "bool", False, None),
    ("StartLoc", "vector", False, None),
    ("ShaftHeight", "real", True, 3000.0), ("ShaftWidth", "real", True, 3.0), ("DescendSeconds", "real", True, 1.6),
    ("RiseHeight", "real", True, 450.0), ("RiseSeconds", "real", True, 3.5), ("FadeAt", "real", True, 0.45),
])
library.save_asset(AREA + "/BP_LightGate", False)

# ----- BP_LightArrival -----
arrival = actor_blueprint("BP_LightArrival")
add(arrival, unreal.SceneComponent, "DefaultSceneRoot")
add(arrival, unreal.BillboardComponent, "Icon")
common(arrival)
audio(arrival, "FadeSound", sounds["S_BeamFade"])
variables(arrival, [
    ("Arriving", "bool", False, None), ("ArriveAt", "real", False, None), ("Landed", "bool", False, None),
    ("LandAt", "real", False, None), ("Done", "bool", False, None),
    ("ShaftHeight", "real", True, 3000.0), ("ShaftWidth", "real", True, 3.0), ("DescendHeight", "real", True, 400.0),
    ("DescendSeconds", "real", True, 2.5), ("VanishSeconds", "real", True, 2.5),
])
library.save_asset(AREA + "/BP_LightArrival", False)

# ----- the levels (only with --levels) -----
if LEVELS:
    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    level.load_level("/Game/LV_Area3_Sky")
    old = next((a for a in actors.get_all_level_actors() if a.get_class().get_name() == "BP_AreaExit_C"), None)
    placed = next((a for a in actors.get_all_level_actors() if a.get_class().get_name() == "BP_LightGate_C"), None)
    if old is not None:
        where, turn, next_level = old.get_actor_location(), old.get_actor_rotation(), old.get_editor_property("NextLevel")
        label, folder = old.get_actor_label().replace("Exit", "Light Gate"), old.get_folder_path()
        if placed is not None:
            actors.destroy_actor(placed)
        actors.destroy_actor(old)
        new = actors.spawn_actor_from_class(gate.generated_class(), where, turn)
        new.set_actor_label(label)
        new.set_folder_path(str(folder))
        new.set_editor_property("NextLevel", next_level)
        lines.append("LV_Area3_Sky: {} at {} -> {}; saved {}".format(label, where, next_level, level.save_current_level()))
    else:
        lines.append("LV_Area3_Sky: no BP_AreaExit (kept {})".format(placed.get_actor_label() if placed else None))
    level.load_level("/Game/LV_Area4_Heaven")
    for a in actors.get_all_level_actors():
        if a.get_class().get_name() == "BP_LightArrival_C":
            actors.destroy_actor(a)
    start = next(a for a in actors.get_all_level_actors() if a.get_class().get_name() == "PlayerStart")
    where = start.get_actor_location()
    new = actors.spawn_actor_from_class(arrival.generated_class(), unreal.Vector(where.x, where.y, where.z - 100.0), unreal.Rotator(0.0, 0.0, 0.0))
    new.set_actor_label("A4 Light Arrival")
    new.set_folder_path(str(start.get_folder_path()))
    lines.append("LV_Area4_Heaven: Light Arrival at the PlayerStart's feet; saved {}".format(level.save_current_level()))

with open(os.path.join(unreal.Paths.project_saved_dir(), "light_transition.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
