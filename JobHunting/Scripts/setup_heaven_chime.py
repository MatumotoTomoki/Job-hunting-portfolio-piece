# Area 4's ringing jewels (the west wing), in /Game/ThirdPerson/Blueprints/Gimmicks/Heaven:
#   S_Chime          the bell (SourceArt/Sounds/S_Chime.wav from make_chime_sound.ps1), SA_Chime its attenuation
#                    (full within 4 m, silent past 30 m).
#   BP_ChimeJewel    a jewel pad, 100 cm across and 100 cm tall around its origin (scale the actor). All jewels keep one
#                    beat (BeatSeconds, from the game clock). Out of every LoopBeats beats it rings for RingBeats beats
#                    from beat StartBeat: it chimes at Pitch (1 = A5) and is solid; otherwise it is a faint outline the
#                    player falls through, glowing brighter on the beat just before it rings. Jewels with the same
#                    BeatSeconds / LoopBeats and StartBeats in a row play a melody the player follows.
# Graph: BP_ChimeJewel_EventGraph.txt from gen_heaven_chime.ps1. Safe to run again. With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_heaven_chime.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven"
GLOW = "/Game/ThirdPerson/Blueprints/Gimmicks/Hell/M_HellGlow"
GHOST = "/Game/ThirdPerson/Blueprints/Gimmicks/Machine/M_SwitchGhost"
CYLINDER = "/Engine/BasicShapes/Cylinder"
SOUND_FILE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Sounds", "S_Chime.wav")

library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
pins = unreal.BlueprintEditorLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []

REAL = pins.get_basic_type_by_name("real")
BOOL = pins.get_basic_type_by_name("bool")
INT = pins.get_basic_type_by_name("int")


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


def add_component(blueprint, component_class, name, parent=None):
    existing = components(blueprint)
    if name in existing:
        return existing[name][1], False
    parent_handle = existing[parent][0] if parent else subsystem.k2_gather_subobject_data_for_blueprint(blueprint)[0]
    params = unreal.AddNewSubobjectParams(parent_handle=parent_handle, new_class=component_class, blueprint_context=blueprint)
    handle, _ = subsystem.add_new_subobject(params)
    if not data_library.is_handle_valid(handle):
        raise RuntimeError("Could not add {} to {}".format(name, blueprint.get_name()))
    subsystem.rename_subobject(handle, unreal.Text(name))
    lines.append("{}: component {}".format(blueprint.get_name(), name))
    return data_library.get_associated_object(data_library.get_data(handle)), True


def instance(name, parent, vectors=(), scalars=()):
    path = DIR + "/" + name
    if library.does_asset_exist(path):
        return unreal.load_asset(path)
    made = tools.create_asset(name, DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    editing.set_material_instance_parent(made, unreal.load_asset(parent))
    for key, color in vectors:
        editing.set_material_instance_vector_parameter_value(made, key, unreal.LinearColor(color[0], color[1], color[2], 1.0))
    for key, value in scalars:
        editing.set_material_instance_scalar_parameter_value(made, key, value)
    library.save_asset(path, False)
    lines.append("created " + path)
    return made


JEWEL = (0.45, 0.85, 1.0)
solid_look = instance("MI_JewelSolid", GLOW, [("Color", JEWEL)], [("Glow", 3.0)])
ghost_look = instance("MI_JewelGhost", GHOST, [("Color", JEWEL)], [("Opacity", 0.1)])
hint_look = instance("MI_JewelHint", GHOST, [("Color", (0.8, 0.95, 1.0))], [("Opacity", 0.4)])

# ----- the bell -----
task = unreal.AssetImportTask()
task.filename = SOUND_FILE
task.destination_path = DIR
task.destination_name = "S_Chime"
task.automated = True
task.save = True
task.replace_existing = True
tools.import_asset_tasks([task])
chime = unreal.load_asset(DIR + "/S_Chime")
if chime is None:
    raise RuntimeError("S_Chime did not import from " + SOUND_FILE)
lines.append("imported {}/S_Chime ({} s)".format(DIR, chime.get_editor_property("duration")))

path = DIR + "/SA_Chime"
if library.does_asset_exist(path):
    attenuation = unreal.load_asset(path)
else:
    attenuation = tools.create_asset("SA_Chime", DIR, unreal.SoundAttenuation, unreal.SoundAttenuationFactory())
    settings = attenuation.get_editor_property("attenuation")
    settings.set_editor_property("attenuation_shape_extents", unreal.Vector(400.0, 0.0, 0.0))
    settings.set_editor_property("falloff_distance", 2600.0)
    attenuation.set_editor_property("attenuation", settings)
    library.save_asset(path, False)
    lines.append("created " + path)

# ----- BP_ChimeJewel -----
JEWEL_BP = DIR + "/BP_ChimeJewel"
if library.does_asset_exist(JEWEL_BP):
    jewel = unreal.load_asset(JEWEL_BP)
else:
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    jewel = tools.create_asset("BP_ChimeJewel", DIR, unreal.Blueprint, factory)
    lines.append("created " + JEWEL_BP)
for name, look, collide, visible in (("Solid", solid_look, True, True), ("Ghost", ghost_look, False, False),
                                     ("Hint", hint_look, False, False)):
    part, made = add_component(jewel, unreal.StaticMeshComponent, name)
    if made:
        part.set_editor_property("static_mesh", unreal.load_asset(CYLINDER))
        part.set_material(0, look)
        part.set_editor_property("visible", visible)
        if not collide:
            part.set_collision_profile_name("NoCollision")
            part.set_editor_property("cast_shadow", False)
defaults = add_variables(jewel, [
    ("BeatSeconds", REAL, True), ("LoopBeats", INT, True), ("StartBeat", INT, True), ("RingBeats", INT, True),
    ("Pitch", REAL, True), ("ChimeSound", pins.get_object_reference_type(unreal.SoundBase.static_class()), True),
    ("ChimeAttenuation", pins.get_object_reference_type(unreal.SoundAttenuation.static_class()), True),
    ("Ringing", BOOL, False),
])
for name, value in (("BeatSeconds", 0.7), ("Pitch", 1.0)):
    if defaults.get_editor_property(name) == 0.0:
        defaults.set_editor_property(name, value)
for name, value in (("LoopBeats", 8), ("RingBeats", 2)):
    if defaults.get_editor_property(name) == 0:
        defaults.set_editor_property(name, value)
if defaults.get_editor_property("ChimeSound") is None:
    defaults.set_editor_property("ChimeSound", chime)
if defaults.get_editor_property("ChimeAttenuation") is None:
    defaults.set_editor_property("ChimeAttenuation", attenuation)
pins.compile_blueprint(jewel)
library.save_asset(JEWEL_BP, False)
lines.append("defaults sound {} attenuation {}".format(defaults.get_editor_property("ChimeSound"),
                                                       defaults.get_editor_property("ChimeAttenuation")))

with open(os.path.join(unreal.Paths.project_saved_dir(), "heaven_chime.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
