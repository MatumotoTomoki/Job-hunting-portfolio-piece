import math

import unreal


LEVEL_PATH = "/Game/ThirdPerson/Lvl_ThirdPerson"
START_LOCATION = unreal.Vector(8820.0, 1450.0, 4350.0)
LABEL_PREFIX = "UpperExtension_45mLeft_"


def distance_between(first, second):
    offset = first - second
    return math.sqrt(offset.x * offset.x + offset.y * offset.y + offset.z * offset.z)


def find_template():
    closest_actor = None
    closest_distance = None
    for actor in ACTOR_SUBSYSTEM.get_all_level_actors():
        if not isinstance(actor, unreal.StaticMeshActor):
            continue
        distance = distance_between(actor.get_actor_location(), START_LOCATION)
        if closest_distance is None or distance < closest_distance:
            closest_actor = actor
            closest_distance = distance
    if not closest_actor or closest_distance > 20.0:
        raise RuntimeError("Could not find the 45m platform at (8820, 1450, 4350)")
    return closest_actor


def remove_previous_extension():
    for actor in list(ACTOR_SUBSYSTEM.get_all_level_actors()):
        if actor.get_actor_label().startswith(LABEL_PREFIX):
            ACTOR_SUBSYSTEM.destroy_actor(actor)


def make_platform(index, location, scale, template):
    actor = ACTOR_SUBSYSTEM.spawn_actor_from_class(
        unreal.StaticMeshActor,
        unreal.Vector(*location),
    )
    if not actor:
        raise RuntimeError("Could not spawn platform {}".format(index))

    actor.set_actor_label("{}{:02d}".format(LABEL_PREFIX, index))
    mesh = template.static_mesh_component.get_editor_property("static_mesh")
    actor.static_mesh_component.set_static_mesh(mesh)
    actor.set_actor_scale3d(unreal.Vector(*scale))
    actor.static_mesh_component.set_mobility(unreal.ComponentMobility.STATIC)
    for material_index in range(template.static_mesh_component.get_num_materials()):
        material = template.static_mesh_component.get_material(material_index)
        if material:
            actor.static_mesh_component.set_material(material_index, material)


unreal.EditorLoadingAndSavingUtils.load_map(LEVEL_PATH)
ACTOR_SUBSYSTEM = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
template = find_template()
remove_previous_extension()

# Move left by reducing Y while climbing from 45m to 50m.
steps = [
    ((8820, 890, 4450), (1.0, 1.0, 0.25)),
    ((8820, 330, 4550), (1.0, 1.0, 0.25)),
    ((8820, -230, 4650), (0.6, 1.0, 0.25)),
    ((8820, -790, 4750), (1.0, 1.0, 0.25)),
    ((8820, -1350, 4850), (2.5, 2.5, 0.25)),
]

for index, (location, scale) in enumerate(steps, 1):
    make_platform(index, location, scale, template)

unreal.EditorAssetLibrary.save_asset(LEVEL_PATH, True)
unreal.log("45m to 50m left extension created: {} platforms".format(len(steps)))
