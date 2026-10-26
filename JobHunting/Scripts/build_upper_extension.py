import math

import unreal


LEVEL_PATH = "/Game/ThirdPerson/Lvl_ThirdPerson"
START_LOCATION = unreal.Vector(-180.0, 1070.0, 2500.0)


def find_template():
    closest_actor = None
    closest_distance = None
    for actor in ACTOR_SUBSYSTEM.get_all_level_actors():
        if not isinstance(actor, unreal.StaticMeshActor):
            continue
        offset = actor.get_actor_location() - START_LOCATION
        distance = math.sqrt(offset.x * offset.x + offset.y * offset.y + offset.z * offset.z)
        if closest_distance is None or distance < closest_distance:
            closest_actor = actor
            closest_distance = distance
    if not closest_actor or closest_distance > 10.0:
        raise RuntimeError("Could not find the platform at (-180, 1070, 2500)")
    return closest_actor


def make_platform(index, location, scale, template):
    actor = ACTOR_SUBSYSTEM.spawn_actor_from_class(
        unreal.StaticMeshActor,
        unreal.Vector(*location),
    )
    if not actor:
        raise RuntimeError("Could not spawn platform {}".format(index))

    actor.set_actor_label("UpperExtension_Platform_{:02d}".format(index))
    actor.static_mesh_component.set_static_mesh(
        template.static_mesh_component.get_editor_property("static_mesh")
    )
    actor.set_actor_scale3d(unreal.Vector(*scale))
    actor.static_mesh_component.set_mobility(unreal.ComponentMobility.STATIC)
    for material_index in range(template.static_mesh_component.get_num_materials()):
        material = template.static_mesh_component.get_material(material_index)
        if material:
            actor.static_mesh_component.set_material(material_index, material)
    return actor


unreal.EditorLoadingAndSavingUtils.load_map(LEVEL_PATH)
ACTOR_SUBSYSTEM = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
template = find_template()

# Continue from the platform shown in the second image.
# Each jump rises 70 cm and uses 200 cm platforms, matching the shared design notes.
steps = [
    ((420, 1070, 2570), (1.0, 1.0, 0.25)),
    ((980, 1070, 2640), (1.0, 1.0, 0.25)),
    ((980, 1450, 2710), (1.0, 1.0, 0.25)),
    ((1540, 1450, 2780), (2.0, 2.0, 0.25)),
    ((1540, 1050, 2850), (1.0, 1.0, 0.25)),
    ((2100, 1050, 2920), (1.0, 1.0, 0.25)),
    ((2100, 1450, 2990), (2.0, 2.0, 0.25)),
    ((2660, 1450, 3060), (1.0, 1.0, 0.25)),
    ((2660, 1050, 3130), (2.5, 2.5, 0.25)),
]

for index, (location, scale) in enumerate(steps, 1):
    make_platform(index, location, scale, template)

unreal.EditorAssetLibrary.save_asset(LEVEL_PATH, True)
unreal.log("Upper extension created from (-180, 1070, 2500): {} platforms".format(len(steps)))
