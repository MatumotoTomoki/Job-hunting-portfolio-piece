import unreal


level_path = "/Game/Lvl_ThirdPerson"
unreal.EditorLoadingAndSavingUtils.load_map(level_path)
actors = unreal.EditorLevelLibrary.get_all_level_actors()

for actor in actors:
    location = actor.get_actor_location()
    bounds_origin, bounds_extent = actor.get_actor_bounds(False)
    unreal.log(
        "LEVEL_ACTOR|{}|loc=({:.1f},{:.1f},{:.1f})|extent=({:.1f},{:.1f},{:.1f})".format(
            actor.get_name(),
            location.x,
            location.y,
            location.z,
            bounds_extent.x,
            bounds_extent.y,
            bounds_extent.z,
        )
    )