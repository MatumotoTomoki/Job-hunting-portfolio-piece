import unreal


BLUEPRINT_DIR = "/Game/ThirdPerson/Blueprints"
MATERIAL_NAME = "M_Halo"
MATERIAL_PATH = "{}/{}".format(BLUEPRINT_DIR, MATERIAL_NAME)
TORUS_BP_PATH = "{}/BP_Torus".format(BLUEPRINT_DIR)

# Warm gold; Glow multiplies it into the emissive channel so bloom makes the ring shine.
HALO_COLOR = unreal.LinearColor(1.0, 0.82, 0.35, 1.0)
GLOW_STRENGTH = 8.0


def create_halo_material():
    # Never recreate an existing asset: that would wipe edits made in the material editor.
    if unreal.EditorAssetLibrary.does_asset_exist(MATERIAL_PATH):
        unreal.log("{} already exists, reusing it".format(MATERIAL_PATH))
        return unreal.EditorAssetLibrary.load_asset(MATERIAL_PATH)

    material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        MATERIAL_NAME, BLUEPRINT_DIR, unreal.Material, unreal.MaterialFactoryNew()
    )
    if not material:
        raise RuntimeError("Could not create {}".format(MATERIAL_PATH))

    editing = unreal.MaterialEditingLibrary
    color = editing.create_material_expression(material, unreal.MaterialExpressionVectorParameter, -700, 0)
    color.set_editor_property("parameter_name", "Color")
    color.set_editor_property("default_value", HALO_COLOR)

    glow = editing.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -700, 250)
    glow.set_editor_property("parameter_name", "Glow")
    glow.set_editor_property("default_value", GLOW_STRENGTH)

    emissive = editing.create_material_expression(material, unreal.MaterialExpressionMultiply, -350, 150)
    editing.connect_material_expressions(color, "", emissive, "A")
    editing.connect_material_expressions(glow, "", emissive, "B")

    editing.connect_material_property(color, "", unreal.MaterialProperty.MP_BASE_COLOR)
    editing.connect_material_property(emissive, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)

    editing.recompile_material(material)
    unreal.EditorAssetLibrary.save_asset(MATERIAL_PATH, False)
    return material


def apply_to_torus(material):
    torus = unreal.EditorAssetLibrary.load_asset(TORUS_BP_PATH)
    if not torus:
        raise RuntimeError("Could not find {}; run build_torus.py first".format(TORUS_BP_PATH))

    subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    applied = 0
    for handle in subsystem.k2_gather_subobject_data_for_blueprint(torus):
        data = unreal.SubobjectDataBlueprintFunctionLibrary.get_data(handle)
        component = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(data)
        if isinstance(component, unreal.StaticMeshComponent):
            component.set_material(0, material)
            applied += 1
    if not applied:
        raise RuntimeError("No static mesh component found in {}".format(TORUS_BP_PATH))

    unreal.BlueprintEditorLibrary.compile_blueprint(torus)
    unreal.EditorAssetLibrary.save_asset(TORUS_BP_PATH, False)


halo_material = create_halo_material()
apply_to_torus(halo_material)
unreal.log("M_Halo applied to BP_Torus")
