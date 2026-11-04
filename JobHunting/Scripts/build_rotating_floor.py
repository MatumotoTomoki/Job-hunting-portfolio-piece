# Creates BP_RotatingFloor with the same mesh, materials and size as the SM_Door25 placed in the open level.
# Run in the editor's Python console with Lvl_ThirdPerson open:
#   exec(open(r"C:\Git\Job-hunting-portfolio-piece\JobHunting\Scripts\build_rotating_floor.py", encoding="utf-8").read())
# The Event Graph comes from BP_RotatingFloor_EventGraph.txt, which relies on the component name Pivot.
import unreal

SOURCE_LABEL = "SM_Door25"
BLUEPRINT_DIR = "/Game/ThirdPerson/Blueprints/Gimmicks"
BLUEPRINT_NAME = "BP_RotatingFloor"
BLUEPRINT_PATH = "{}/{}".format(BLUEPRINT_DIR, BLUEPRINT_NAME)
PIVOT_NAME = "Pivot"
MESH_NAME = "FloorMesh"


def add_component(blueprint, parent_handle, component_class, name):
    params = unreal.AddNewSubobjectParams(
        parent_handle=parent_handle,
        new_class=component_class,
        blueprint_context=blueprint,
    )
    handle, _ = SUBOBJECT_SUBSYSTEM.add_new_subobject(params)
    if not unreal.SubobjectDataBlueprintFunctionLibrary.is_handle_valid(handle):
        raise RuntimeError("Could not add component {}".format(name))
    SUBOBJECT_SUBSYSTEM.rename_subobject(handle, unreal.Text(name))
    data = unreal.SubobjectDataBlueprintFunctionLibrary.get_data(handle)
    return handle, unreal.SubobjectDataBlueprintFunctionLibrary.get_object(data)


# Never recreate an existing asset: that would wipe the Event Graph pasted into it.
if unreal.EditorAssetLibrary.does_asset_exist(BLUEPRINT_PATH):
    raise RuntimeError(BLUEPRINT_PATH + " already exists")

ACTOR_SUBSYSTEM = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
SUBOBJECT_SUBSYSTEM = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)

source = next((a for a in ACTOR_SUBSYSTEM.get_all_level_actors() if a.get_actor_label() == SOURCE_LABEL), None)
if not source:
    raise RuntimeError(SOURCE_LABEL + " is not loaded; open Lvl_ThirdPerson and load the area around it")
source_mesh = source.get_editor_property("static_mesh_component")
mesh_asset = source_mesh.get_editor_property("static_mesh")
scale = source.get_actor_scale3d()

factory = unreal.BlueprintFactory()
factory.set_editor_property("parent_class", unreal.Actor)
blueprint = unreal.AssetToolsHelpers.get_asset_tools().create_asset(BLUEPRINT_NAME, BLUEPRINT_DIR, unreal.Blueprint, factory)
if not blueprint:
    raise RuntimeError("Could not create " + BLUEPRINT_PATH)

root_handle = SUBOBJECT_SUBSYSTEM.k2_gather_subobject_data_for_blueprint(blueprint)[0]

# Pivot is the part that turns; the mesh rides on it, offset so the floor turns around its own center.
pivot_handle, pivot = add_component(blueprint, root_handle, unreal.SceneComponent, PIVOT_NAME)
pivot.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)

_, floor = add_component(blueprint, pivot_handle, unreal.StaticMeshComponent, MESH_NAME)
floor.set_editor_property("static_mesh", mesh_asset)
for index, material in enumerate(source_mesh.get_materials()):
    floor.set_material(index, material)
center = mesh_asset.get_bounds().origin
floor.set_editor_property("relative_location", unreal.Vector(-center.x * scale.x, -center.y * scale.y, -center.z * scale.z))
floor.set_editor_property("relative_scale3d", scale)
floor.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)

unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
unreal.EditorAssetLibrary.save_asset(BLUEPRINT_PATH, False)
unreal.log("Created {} from {}: mesh {}, scale {}".format(BLUEPRINT_PATH, SOURCE_LABEL, mesh_asset.get_name(), scale))
