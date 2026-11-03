# Creates BP_FallingFloor with the same mesh, materials and size as BP_Elevator's platform.
# Run in the editor's Python console:
#   exec(open(r"C:\Git\Job-hunting-portfolio-piece\JobHunting\Scripts\build_falling_floor.py", encoding="utf-8").read())
# The Event Graph comes from BP_FallingFloor_EventGraph.txt, which relies on the names Lift, FloorMesh and Trigger.
import unreal

SOURCE_PATH = "/Game/ThirdPerson/Blueprints/BP_Elevator"
BLUEPRINT_DIR = "/Game/ThirdPerson/Blueprints"
BLUEPRINT_NAME = "BP_FallingFloor"
BLUEPRINT_PATH = "{}/{}".format(BLUEPRINT_DIR, BLUEPRINT_NAME)
# The trigger is a thin slab on the top surface, inset from the edges: it fires when the player
# stands on the floor, not when brushing its side or bumping it from below.
TRIGGER_INSET = 20.0
TRIGGER_HALF_HEIGHT = 15.0

DATA_LIBRARY = unreal.SubobjectDataBlueprintFunctionLibrary


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
bounds = mesh_asset.get_bounds()
half = unreal.Vector(bounds.box_extent.x * scale.x, bounds.box_extent.y * scale.y, bounds.box_extent.z * scale.z)

factory = unreal.BlueprintFactory()
factory.set_editor_property("parent_class", unreal.Actor)
blueprint = unreal.AssetToolsHelpers.get_asset_tools().create_asset(BLUEPRINT_NAME, BLUEPRINT_DIR, unreal.Blueprint, factory)
if not blueprint:
    raise RuntimeError("Could not create " + BLUEPRINT_PATH)

root_handle = SUBOBJECT_SUBSYSTEM.k2_gather_subobject_data_for_blueprint(blueprint)[0]

# Lift is the part that shakes and falls; the mesh and trigger ride on it.
lift_handle, lift = add_component(blueprint, root_handle, unreal.SceneComponent, "Lift")
lift.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)

_, floor = add_component(blueprint, lift_handle, unreal.StaticMeshComponent, "FloorMesh")
floor.set_editor_property("static_mesh", mesh_asset)
for index, material in enumerate(source_mesh.get_materials()):
    floor.set_material(index, material)
# Centered on the actor, so the shake rocks the floor around its middle.
center = bounds.origin
floor.set_editor_property("relative_location", unreal.Vector(-center.x * scale.x, -center.y * scale.y, -center.z * scale.z))
floor.set_editor_property("relative_scale3d", scale)
floor.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)

_, trigger = add_component(blueprint, lift_handle, unreal.BoxComponent, "Trigger")
trigger.set_editor_property("box_extent", unreal.Vector(half.x - TRIGGER_INSET, half.y - TRIGGER_INSET, TRIGGER_HALF_HEIGHT))
trigger.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, half.z + TRIGGER_HALF_HEIGHT))
trigger.set_collision_profile_name("OverlapOnlyPawn")
trigger.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)

unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
unreal.EditorAssetLibrary.save_asset(BLUEPRINT_PATH, False)
unreal.log("Created {}: mesh {}, half size {}".format(BLUEPRINT_PATH, mesh_asset.get_name(), half))
