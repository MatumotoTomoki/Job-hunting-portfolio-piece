# Area 4's ending (2026-11-22, the user's pick: "the gate opens into the light"). Heaven's Gate (area4_layout.py
# section 6: two gold pillars at y +-350..500 round the island's middle, a lintel at +1200) gets two doors that swing
# away from the player, light pouring out between them; the player walks into it, the screen goes white and the
# game is cleared as BP_GoalItem did (ShowGameClear, best time), with the clear-time achievements.
#   Heaven/M_HeavenGateLight   unlit additive two-sided, Color * Glow (scalar) * a soft radial falloff
#   Heaven/BP_HeavenGate       (its origin = the gate's middle on the island floor; +X = through the gate)
#       HingeL (y -350) > DoorL,  HingeR (y +350) > DoorR   white-and-gold slabs, 350 x 1200 x 30, they block
#       Veil        the light in the opening (Glow 0 until the doors part)
#       GateLight   point light behind the doors (intensity 0 until then)
#       Trigger     in front of the gate: the player walking up starts the ending
#       ShowCamera  in front, looking at the gate
#       Variables   Started, StartedAt, ClearTime; OpenSeconds 3, OpenAngle 105, WalkFrom 4.5, MaxGlow 40,
#                   MaxLight 8000, TargetSeconds 900 (ACH_TIME; instance editable, decide after a playtest)
#   Graph: Scripts/BP_HeavenGate_EventGraph.txt (Generators/gen_heaven_gate.ps1)
#   LV_Area4_Heaven: one "A4 Heaven Gate" at the Goal Spot (goal = gate + 200 in x, 100 up); the placeholder
#       "GOAL (coming soon)" text is removed. An existing gate actor is moved there again.
# Safe to run again. Saves LV_Area4_Heaven, so save your work first. From the Output Log (Python):
#   exec(open(r'C:\Git\Job-hunting-portfolio-piece\JobHunting\Scripts\setup_heaven_gate.py', encoding='utf-8').read())
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven"
PATH = DIR + "/BP_HeavenGate"
LIGHT_MAT = DIR + "/M_HeavenGateLight"
LEVEL = "/Game/LV_Area4_Heaven"
LABEL = "A4 Heaven Gate"
DOOR_MAT = "/Game/Art/HeavenDebris/MI_HeavenHoly"

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
level_editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
lines = []
REAL = pins.get_basic_type_by_name("real")
BOOL = pins.get_basic_type_by_name("bool")

# ----- the light material -----
if library.does_asset_exist(LIGHT_MAT):
    light_mat = unreal.load_asset(LIGHT_MAT)
else:
    light_mat = tools.create_asset("M_HeavenGateLight", DIR, unreal.Material, unreal.MaterialFactoryNew())
    light_mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    light_mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE)
    light_mat.set_editor_property("two_sided", True)
    color = editing.create_material_expression(light_mat, unreal.MaterialExpressionVectorParameter, -900, 0)
    color.set_editor_property("parameter_name", "Color")
    color.set_editor_property("default_value", unreal.LinearColor(1.0, 0.9, 0.65, 1.0))
    glow = editing.create_material_expression(light_mat, unreal.MaterialExpressionScalarParameter, -900, 250)
    glow.set_editor_property("parameter_name", "Glow")
    glow.set_editor_property("default_value", 0.0)
    falloff = editing.create_material_expression(light_mat, unreal.MaterialExpressionMaterialFunctionCall, -900, 450)
    falloff.set_editor_property("material_function", unreal.load_asset(
        "/Engine/Functions/Engine_MaterialFunctions01/Gradient/RadialGradientExponential"))
    first = editing.create_material_expression(light_mat, unreal.MaterialExpressionMultiply, -550, 100)
    editing.connect_material_expressions(color, "", first, "A")
    editing.connect_material_expressions(glow, "", first, "B")
    second = editing.create_material_expression(light_mat, unreal.MaterialExpressionMultiply, -300, 200)
    editing.connect_material_expressions(first, "", second, "A")
    editing.connect_material_expressions(falloff, "", second, "B")
    editing.connect_material_property(second, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    editing.recompile_material(light_mat)
    library.save_asset(LIGHT_MAT, False)
    lines.append("created " + LIGHT_MAT)

# ----- BP_HeavenGate -----
if library.does_asset_exist(PATH):
    bp = unreal.load_asset(PATH)
else:
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    bp = tools.create_asset("BP_HeavenGate", DIR, unreal.Blueprint, factory)
    lines.append("created " + PATH)


def components():
    found = {}
    for handle in subsystem.k2_gather_subobject_data_for_blueprint(bp):
        component = data_library.get_associated_object(data_library.get_data(handle))
        if component is not None:
            found[component.get_name().replace("_GEN_VARIABLE", "")] = (handle, component)
    return found


def add(cls, name, parent=None):
    existing = components()
    if name in existing:
        return existing[name][1], False
    parent_handle = existing[parent][0] if parent else subsystem.k2_gather_subobject_data_for_blueprint(bp)[0]
    handle, _ = subsystem.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=parent_handle, new_class=cls, blueprint_context=bp))
    if not data_library.is_handle_valid(handle):
        raise RuntimeError("Could not add " + name)
    subsystem.rename_subobject(handle, unreal.Text(name))
    lines.append("BP_HeavenGate: component " + name)
    return data_library.get_associated_object(data_library.get_data(handle)), True


CUBE = unreal.load_asset("/Engine/BasicShapes/Cube")
PLANE = unreal.load_asset("/Engine/BasicShapes/Plane")
door_mat = unreal.load_asset(DOOR_MAT)
for side, y, sign in (("L", -350.0, 1.0), ("R", 350.0, -1.0)):
    hinge, made = add(unreal.SceneComponent, "Hinge" + side)
    if made:
        hinge.set_editor_property("relative_location", unreal.Vector(0.0, y, 0.0))
    door, made = add(unreal.StaticMeshComponent, "Door" + side, "Hinge" + side)
    if made:
        door.set_editor_property("static_mesh", CUBE)
        door.set_material(0, door_mat)
        # Reaches 175 from the hinge to the middle (2 cm short, so the two never touch), 1200 high, 30 thick.
        door.set_editor_property("relative_location", unreal.Vector(0.0, sign * 174.0, 600.0))
        door.set_editor_property("relative_scale3d", unreal.Vector(0.3, 3.48, 12.0))
veil, made = add(unreal.StaticMeshComponent, "Veil")
if made:
    veil.set_editor_property("static_mesh", PLANE)
    veil.set_material(0, light_mat)
    veil.set_editor_property("relative_location", unreal.Vector(60.0, 0.0, 600.0))
    veil.set_editor_property("relative_rotation", unreal.Rotator(roll=0.0, pitch=90.0, yaw=0.0))
    veil.set_editor_property("relative_scale3d", unreal.Vector(13.0, 8.0, 1.0))
    veil.set_collision_profile_name("NoCollision")
    veil.set_editor_property("cast_shadow", False)
light, made = add(unreal.PointLightComponent, "GateLight")
if made:
    light.set_editor_property("relative_location", unreal.Vector(400.0, 0.0, 500.0))
    light.set_editor_property("light_color", unreal.Color(r=255, g=235, b=190, a=255))
    light.set_editor_property("intensity", 0.0)
    light.set_editor_property("attenuation_radius", 4000.0)
    light.set_editor_property("cast_shadows", False)
trigger, made = add(unreal.BoxComponent, "Trigger")
if made:
    trigger.set_editor_property("box_extent", unreal.Vector(300.0, 600.0, 400.0))
    trigger.set_editor_property("relative_location", unreal.Vector(-330.0, 0.0, 400.0))
    trigger.set_collision_profile_name("OverlapOnlyPawn")
    trigger.set_editor_property("hidden_in_game", True)
camera, made = add(unreal.CameraComponent, "ShowCamera")
if made:
    camera.set_editor_property("relative_location", unreal.Vector(-1500.0, 0.0, 450.0))
    camera.set_editor_property("relative_rotation", unreal.Rotator(roll=0.0, pitch=4.0, yaw=0.0))
    camera.set_editor_property("field_of_view", 75.0)

defaults = unreal.get_default_object(bp.generated_class())
for name, pin_type, editable in (("Started", BOOL, False), ("StartedAt", REAL, False), ("ClearTime", REAL, False),
                                 ("OpenSeconds", REAL, True), ("OpenAngle", REAL, True), ("WalkFrom", REAL, True),
                                 ("MaxGlow", REAL, True), ("MaxLight", REAL, True), ("TargetSeconds", REAL, True)):
    try:
        defaults.get_editor_property(name)
        continue
    except Exception:
        pass
    if not pins.add_member_variable(bp, name, pin_type):
        raise RuntimeError("Could not add " + name)
    if editable:
        pins.set_blueprint_variable_instance_editable(bp, name, True)
    lines.append("BP_HeavenGate: variable " + name)
pins.compile_blueprint(bp)
defaults = unreal.get_default_object(bp.generated_class())
for name, value in (("OpenSeconds", 3.0), ("OpenAngle", 105.0), ("WalkFrom", 4.5), ("MaxGlow", 40.0),
                    ("MaxLight", 8000.0), ("TargetSeconds", 900.0)):
    if defaults.get_editor_property(name) == 0.0:
        defaults.set_editor_property(name, value)
pins.compile_blueprint(bp)
library.save_asset(PATH, False)

# ----- in area 4 -----
if not unreal.EditorLevelLibrary.get_editor_world().get_path_name().startswith(LEVEL + "."):
    if not level_editor.load_level(LEVEL):
        raise RuntimeError("Could not open " + LEVEL)
everything = actors.get_all_level_actors()
# build_area4_heaven.py labels it "<prefix><number> Goal Spot".
spot = [a for a in everything if a.get_actor_label().endswith("Goal Spot")]
if not spot:
    raise RuntimeError("No 'Goal Spot' in " + LEVEL)
s = spot[0].get_actor_location()
where = unreal.Vector(s.x - 200.0, s.y, s.z - 100.0)
for a in everything:
    if isinstance(a, unreal.TextRenderActor):
        words = str(a.text_render.get_editor_property("text"))
        if "GOAL" in words:
            lines.append("removed placeholder text '{}'".format(words))
            actors.destroy_actor(a)
gates = [a for a in everything if a.get_class() == bp.generated_class()]
gate = gates[0] if gates else actors.spawn_actor_from_class(bp.generated_class(), where, unreal.Rotator(0.0, 0.0, 0.0))
gate.set_actor_location(where, False, False)
gate.set_actor_rotation(unreal.Rotator(0.0, 0.0, 0.0), False)
gate.set_actor_label(LABEL)
gate.set_folder_path("Area4/Goal")
lines.append("{} at {} ({})".format(LABEL, where, "moved" if gates else "placed"))
lines.append("{} saved {}".format(LEVEL, level_editor.save_current_level()))

with open(os.path.join(unreal.Paths.project_saved_dir(), "setup_heaven_gate.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
