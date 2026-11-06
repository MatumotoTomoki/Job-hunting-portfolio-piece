# Creates BP_MovingPlatform: a platform with BP_Elevator's look that goes back and forth between where it is placed and
# MoveOffset from there, pausing at each end. MoveOffset, MoveSeconds and WaitSeconds can be set per placed platform.
# Run in the editor's Python console:
#   exec(open(r"C:\Git\Job-hunting-portfolio-piece\JobHunting\Scripts\build_moving_platform.py", encoding="utf-8").read())
# The Event Graph comes from BP_MovingPlatform_EventGraph.txt, which relies on the names Lift, MoveOffset, MoveSeconds
# and WaitSeconds.
import unreal

SOURCE_PATH = "/Game/ThirdPerson/Blueprints/Gimmicks/BP_Elevator"
BLUEPRINT_DIR = "/Game/ThirdPerson/Blueprints/Gimmicks"
BLUEPRINT_NAME = "BP_MovingPlatform"
BLUEPRINT_PATH = "{}/{}".format(BLUEPRINT_DIR, BLUEPRINT_NAME)
DEFAULT_OFFSET = unreal.Vector(0.0, 600.0, 0.0)
DEFAULT_MOVE_SECONDS = 3.0
DEFAULT_WAIT_SECONDS = 1.0

DATA_LIBRARY = unreal.SubobjectDataBlueprintFunctionLibrary
LIBRARY = unreal.BlueprintEditorLibrary


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


# Never recreate an existing asset: that would wipe the Event Graph pasted into it.
if unreal.EditorAssetLibrary.does_asset_exist(BLUEPRINT_PATH):
    raise RuntimeError(BLUEPRINT_PATH + " already exists")

SUBOBJECT_SUBSYSTEM = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
source_mesh = find_source_mesh()
mesh_asset = source_mesh.get_editor_property("static_mesh")
scale = source_mesh.get_editor_property("relative_scale3d")

factory = unreal.BlueprintFactory()
factory.set_editor_property("parent_class", unreal.Actor)
blueprint = unreal.AssetToolsHelpers.get_asset_tools().create_asset(BLUEPRINT_NAME, BLUEPRINT_DIR, unreal.Blueprint, factory)
if not blueprint:
    raise RuntimeError("Could not create " + BLUEPRINT_PATH)

root_handle = SUBOBJECT_SUBSYSTEM.k2_gather_subobject_data_for_blueprint(blueprint)[0]

# Lift is the part that moves; the mesh rides on it. A moving component carries a player standing on it.
lift_handle, lift = add_component(blueprint, root_handle, unreal.SceneComponent, "Lift")
lift.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
_, floor = add_component(blueprint, lift_handle, unreal.StaticMeshComponent, "FloorMesh")
floor.set_editor_property("static_mesh", mesh_asset)
for index, material in enumerate(source_mesh.get_materials()):
    floor.set_material(index, material)
center = mesh_asset.get_bounds().origin
floor.set_editor_property("relative_location", unreal.Vector(-center.x * scale.x, -center.y * scale.y, -center.z * scale.z))
floor.set_editor_property("relative_scale3d", scale)
floor.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)

for name, pin_type in (
    ("MoveOffset", LIBRARY.get_struct_type(unreal.Vector.static_struct())),
    ("MoveSeconds", LIBRARY.get_basic_type_by_name("real")),
    ("WaitSeconds", LIBRARY.get_basic_type_by_name("real")),
):
    LIBRARY.add_member_variable(blueprint, name, pin_type)
    LIBRARY.set_blueprint_variable_instance_editable(blueprint, name, True)
LIBRARY.compile_blueprint(blueprint)

defaults = unreal.get_default_object(blueprint.generated_class())
defaults.set_editor_property("MoveOffset", DEFAULT_OFFSET)
defaults.set_editor_property("MoveSeconds", DEFAULT_MOVE_SECONDS)
defaults.set_editor_property("WaitSeconds", DEFAULT_WAIT_SECONDS)
unreal.EditorAssetLibrary.save_asset(BLUEPRINT_PATH, False)
unreal.log("Created {}: mesh {}, offset {}, {} s, wait {} s".format(BLUEPRINT_PATH, mesh_asset.get_name(), DEFAULT_OFFSET, DEFAULT_MOVE_SECONDS, DEFAULT_WAIT_SECONDS))
