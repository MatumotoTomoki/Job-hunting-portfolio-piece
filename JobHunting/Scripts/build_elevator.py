import unreal


LEVEL_PATH = "/Game/ThirdPerson/Lvl_ThirdPerson"
BLUEPRINT_DIR = "/Game/ThirdPerson/Blueprints"
BLUEPRINT_NAME = "BP_Elevator"
BLUEPRINT_PATH = "{}/{}".format(BLUEPRINT_DIR, BLUEPRINT_NAME)
PLATFORM_MESH_PATH = "/Engine/BasicShapes/Cube"
PLATFORM_MATERIAL_PATH = "/Game/ThirdPerson/MI_ThirdPersonColWay_Blue"
ACTOR_LABEL = "Elevator_10m"

# Set to unreal.Vector(x, y, z) to place the elevator explicitly.
# When None, it is placed 5m in front of the PlayerStart as a temporary spot.
ELEVATOR_LOCATION = None
PLAYER_START_OFFSET = unreal.Vector(500.0, 0.0, -90.0)

# The Event Graph paste text (BP_Elevator_EventGraph.txt) relies on these component names.
LIFT_NAME = "Lift"
PLATFORM_NAME = "Platform"
TRIGGER_NAME = "Trigger"


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


def create_blueprint():
    # Never recreate an existing asset: that would wipe the Event Graph pasted into it.
    if unreal.EditorAssetLibrary.does_asset_exist(BLUEPRINT_PATH):
        unreal.log("{} already exists, reusing it".format(BLUEPRINT_PATH))
        return unreal.EditorAssetLibrary.load_asset(BLUEPRINT_PATH)

    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    blueprint = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        BLUEPRINT_NAME, BLUEPRINT_DIR, unreal.Blueprint, factory
    )
    if not blueprint:
        raise RuntimeError("Could not create {}".format(BLUEPRINT_PATH))

    root_handle = SUBOBJECT_SUBSYSTEM.k2_gather_subobject_data_for_blueprint(blueprint)[0]

    # Lift is the part that moves; Platform and Trigger ride along with it.
    lift_handle, lift = add_component(blueprint, root_handle, unreal.SceneComponent, LIFT_NAME)
    lift.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)

    _, platform = add_component(blueprint, lift_handle, unreal.StaticMeshComponent, PLATFORM_NAME)
    platform.set_editor_property("static_mesh", unreal.EditorAssetLibrary.load_asset(PLATFORM_MESH_PATH))
    material = unreal.EditorAssetLibrary.load_asset(PLATFORM_MATERIAL_PATH)
    if material:
        platform.set_material(0, material)
    # 3m x 3m x 20cm floor whose bottom sits on the actor origin.
    platform.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 10.0))
    platform.set_editor_property("relative_scale3d", unreal.Vector(3.0, 3.0, 0.2))
    platform.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)

    # Detects the player standing on the floor (from the top surface up to 1m above it).
    _, trigger = add_component(blueprint, lift_handle, unreal.BoxComponent, TRIGGER_NAME)
    trigger.set_editor_property("box_extent", unreal.Vector(140.0, 140.0, 50.0))
    trigger.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 70.0))
    trigger.set_collision_profile_name("OverlapOnlyPawn")
    trigger.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)

    unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
    unreal.EditorAssetLibrary.save_asset(BLUEPRINT_PATH, False)
    return blueprint


def find_location():
    if ELEVATOR_LOCATION is not None:
        return ELEVATOR_LOCATION
    for actor in ACTOR_SUBSYSTEM.get_all_level_actors():
        if isinstance(actor, unreal.PlayerStart):
            return actor.get_actor_location() + PLAYER_START_OFFSET
    raise RuntimeError("No PlayerStart found; set ELEVATOR_LOCATION instead")


def remove_previous_elevator():
    for actor in list(ACTOR_SUBSYSTEM.get_all_level_actors()):
        if actor.get_actor_label() == ACTOR_LABEL:
            ACTOR_SUBSYSTEM.destroy_actor(actor)


unreal.EditorLoadingAndSavingUtils.load_map(LEVEL_PATH)
ACTOR_SUBSYSTEM = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
SUBOBJECT_SUBSYSTEM = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)

blueprint = create_blueprint()
remove_previous_elevator()
location = find_location()
elevator = ACTOR_SUBSYSTEM.spawn_actor_from_class(blueprint.generated_class(), location)
if not elevator:
    raise RuntimeError("Could not spawn {}".format(BLUEPRINT_NAME))
elevator.set_actor_label(ACTOR_LABEL)

unreal.EditorAssetLibrary.save_asset(LEVEL_PATH, True)
unreal.log("Elevator placed at {}".format(location))
