# Creates BP_TimedPlatform: a platform with BP_Elevator's look that keeps fading out, staying gone, and fading back in.
# Its material is a fading copy of the elevator's (M_FadingFlatCol + MI_TimedPlatform), so other floors are left alone.
# VisibleSeconds, HiddenSeconds, FadeSeconds and StartDelay can be set per placed platform; StartDelay staggers a row.
# Run in the editor's Python console:
#   exec(open(r"C:\Git\Job-hunting-portfolio-piece\JobHunting\Scripts\build_timed_platform.py", encoding="utf-8").read())
# The Event Graph comes from BP_TimedPlatform_EventGraph.txt, which relies on the names FloorMesh, Fade and the timings.
import unreal

SOURCE_PATH = "/Game/ThirdPerson/Blueprints/Gimmicks/BP_Elevator"
BLUEPRINT_DIR = "/Game/ThirdPerson/Blueprints/Gimmicks"
BLUEPRINT_NAME = "BP_TimedPlatform"
BLUEPRINT_PATH = "{}/{}".format(BLUEPRINT_DIR, BLUEPRINT_NAME)
MATERIAL_NAME = "M_FadingFlatCol"
INSTANCE_NAME = "MI_TimedPlatform"
DEFAULTS = {"VisibleSeconds": 2.0, "HiddenSeconds": 2.0, "FadeSeconds": 0.5, "StartDelay": 0.0}

DATA_LIBRARY = unreal.SubobjectDataBlueprintFunctionLibrary
LIBRARY = unreal.BlueprintEditorLibrary
EDITING = unreal.MaterialEditingLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()


def add_component(blueprint, parent_handle, component_class, name):
    params = unreal.AddNewSubobjectParams(
        parent_handle=parent_handle,
        new_class=component_class,
        blueprint_context=blueprint,
    )
    handle, _ = SUBOBJECT_SUBSYSTEM.add_new_subobject(params)
    if not DATA_LIBRARY.is_handle_valid(handle):
        raise RuntimeError("Could not add component {}".format(name))
    SUBOBJECT_SUBSYSTEM.rename_subobject(handle, unreal.Text(name))
    return handle, DATA_LIBRARY.get_object(DATA_LIBRARY.get_data(handle))


def find_source_mesh():
    source = unreal.load_asset(SOURCE_PATH)
    if not source:
        raise RuntimeError("Missing " + SOURCE_PATH)
    for handle in SUBOBJECT_SUBSYSTEM.k2_gather_subobject_data_for_blueprint(source):
        component = DATA_LIBRARY.get_object(DATA_LIBRARY.get_data(handle))
        if isinstance(component, unreal.StaticMeshComponent):
            return component
    raise RuntimeError("No static mesh in " + SOURCE_PATH)


def make_fading_material(look):
    # Same parameters as M_FlatCol, plus Fade: dithered rather than translucent, so it keeps its flat look while fading.
    material = TOOLS.create_asset(MATERIAL_NAME, BLUEPRINT_DIR, unreal.Material, unreal.MaterialFactoryNew())
    material.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
    color = EDITING.create_material_expression(material, unreal.MaterialExpressionVectorParameter, -600, 0)
    color.set_editor_property("parameter_name", "Base Color")
    color.set_editor_property("default_value", EDITING.get_material_instance_vector_parameter_value(look, "Base Color"))
    EDITING.connect_material_property(color, "", unreal.MaterialProperty.MP_BASE_COLOR)
    for name, target, y in (("Metallic", unreal.MaterialProperty.MP_METALLIC, 250), ("Roughness", unreal.MaterialProperty.MP_ROUGHNESS, 400)):
        scalar = EDITING.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -600, y)
        scalar.set_editor_property("parameter_name", name)
        scalar.set_editor_property("default_value", EDITING.get_material_instance_scalar_parameter_value(look, name))
        EDITING.connect_material_property(scalar, "", target)
    fade = EDITING.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -900, 600)
    fade.set_editor_property("parameter_name", "Fade")
    fade.set_editor_property("default_value", 1.0)
    dither = EDITING.create_material_expression(material, unreal.MaterialExpressionMaterialFunctionCall, -600, 600)
    dither.set_editor_property("material_function", unreal.load_asset("/Engine/Functions/Engine_MaterialFunctions02/Utility/DitherTemporalAA"))
    if not EDITING.connect_material_expressions(fade, "", dither, "Alpha Threshold") or not EDITING.connect_material_property(dither, "", unreal.MaterialProperty.MP_OPACITY_MASK):
        raise RuntimeError("Could not wire the fade of " + MATERIAL_NAME)
    EDITING.recompile_material(material)
    unreal.EditorAssetLibrary.save_asset(BLUEPRINT_DIR + "/" + MATERIAL_NAME, False)

    instance = TOOLS.create_asset(INSTANCE_NAME, BLUEPRINT_DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    EDITING.set_material_instance_parent(instance, material)
    unreal.EditorAssetLibrary.save_asset(BLUEPRINT_DIR + "/" + INSTANCE_NAME, False)
    return instance


# Never recreate an existing asset: that would wipe the Event Graph pasted into it.
for path in (BLUEPRINT_PATH, BLUEPRINT_DIR + "/" + MATERIAL_NAME, BLUEPRINT_DIR + "/" + INSTANCE_NAME):
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        raise RuntimeError(path + " already exists")

SUBOBJECT_SUBSYSTEM = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
source_mesh = find_source_mesh()
mesh_asset = source_mesh.get_editor_property("static_mesh")
scale = source_mesh.get_editor_property("relative_scale3d")
fading_look = make_fading_material(source_mesh.get_materials()[0])

factory = unreal.BlueprintFactory()
factory.set_editor_property("parent_class", unreal.Actor)
blueprint = TOOLS.create_asset(BLUEPRINT_NAME, BLUEPRINT_DIR, unreal.Blueprint, factory)
if not blueprint:
    raise RuntimeError("Could not create " + BLUEPRINT_PATH)

root_handle = SUBOBJECT_SUBSYSTEM.k2_gather_subobject_data_for_blueprint(blueprint)[0]
_, floor = add_component(blueprint, root_handle, unreal.StaticMeshComponent, "FloorMesh")
floor.set_editor_property("static_mesh", mesh_asset)
floor.set_material(0, fading_look)
center = mesh_asset.get_bounds().origin
floor.set_editor_property("relative_location", unreal.Vector(-center.x * scale.x, -center.y * scale.y, -center.z * scale.z))
floor.set_editor_property("relative_scale3d", scale)

for name in DEFAULTS:
    LIBRARY.add_member_variable(blueprint, name, LIBRARY.get_basic_type_by_name("real"))
    LIBRARY.set_blueprint_variable_instance_editable(blueprint, name, True)
# Where the fade is right now: 1 is fully there, 0 is gone. Not for setting by hand.
LIBRARY.add_member_variable(blueprint, "Fade", LIBRARY.get_basic_type_by_name("real"))
LIBRARY.compile_blueprint(blueprint)

defaults = unreal.get_default_object(blueprint.generated_class())
for name, value in DEFAULTS.items():
    defaults.set_editor_property(name, value)
defaults.set_editor_property("Fade", 1.0)
unreal.EditorAssetLibrary.save_asset(BLUEPRINT_PATH, False)
unreal.log("Created {}: mesh {}, material {}, {}".format(BLUEPRINT_PATH, mesh_asset.get_name(), INSTANCE_NAME, DEFAULTS))
