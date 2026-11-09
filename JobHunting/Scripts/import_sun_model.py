# Imports the Blender sun from build_sun_blender.py into the gimmicks folder: SM_Sun with an unlit glowing body
# (M_SunBody, colour and brightness as parameters) and a face patch (M_SunFace) that shows one face of the atlas
# T_SunFaces (build_sun_faces.ps1), picked by its FaceIndex parameter; and BP_Sun, an actor holding the mesh, with the
# variables its Event Graph (BP_Sun_EventGraph.txt) uses to switch faces. SM_Sun is re-imported every run, so a rebuilt
# model comes through; other assets that already exist are left alone. With the editor closed:
#   UnrealEditor-Cmd.exe JobHunting.uproject -run=pythonscript -script=import_sun_model.py -unattended -nop4 -nosplash -stdout
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Sun"
SOURCE = os.path.join(os.path.abspath(unreal.Paths.project_dir()), "SourceArt", "Models", "Sun")
library = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
editing = unreal.MaterialEditingLibrary
data_library = unreal.SubobjectDataBlueprintFunctionLibrary
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lines = []


FACE_COLUMNS = 4
FACE_ROWS = 2
# Per placed sun: which face shows (0 the first face, then (´Д｀), (╯‵□′)╯, (＃°Д°), (´。＿。｀)), and every how many
# seconds it changes to another one at random (0 keeps FaceIndex).
SETTINGS = {"FaceIndex": 0, "AutoSwitchSeconds": 3.0}


def mesh():
    path = DIR + "/SM_Sun"
    task = unreal.AssetImportTask()
    task.filename = os.path.join(SOURCE, "SM_Sun.fbx")
    task.destination_path = DIR
    task.destination_name = "SM_Sun"
    task.automated = True
    task.save = True
    task.replace_existing = True
    # Its materials would take the names M_SunBody and M_SunFace; ours are made below.
    options = unreal.FbxImportUI()
    options.set_editor_property("import_materials", False)
    options.set_editor_property("import_textures", False)
    task.options = options
    tools.import_asset_tasks([task])
    lines.append("imported " + str(list(task.imported_object_paths)))
    return unreal.load_asset(path)


def material(name, color, glow, unlit):
    path = DIR + "/" + name
    if library.does_asset_exist(path):
        existing = unreal.load_asset(path)
        if "Color" in [str(n) for n in editing.get_vector_parameter_names(existing)]:
            return existing
        # A plain material an earlier FBX import left under this name: replace it.
        library.delete_asset(path)
        lines.append("replaced imported " + name)
    result = tools.create_asset(name, DIR, unreal.Material, unreal.MaterialFactoryNew())
    color_node = editing.create_material_expression(result, unreal.MaterialExpressionVectorParameter, -700, 0)
    color_node.set_editor_property("parameter_name", "Color")
    color_node.set_editor_property("default_value", color)
    if unlit:
        # Unlit, so night or day it shines the same; Glow above 1 lets bloom pick it up.
        result.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
        glow_node = editing.create_material_expression(result, unreal.MaterialExpressionScalarParameter, -700, 250)
        glow_node.set_editor_property("parameter_name", "Glow")
        glow_node.set_editor_property("default_value", glow)
        multiply = editing.create_material_expression(result, unreal.MaterialExpressionMultiply, -350, 100)
        editing.connect_material_expressions(color_node, "", multiply, "A")
        editing.connect_material_expressions(glow_node, "", multiply, "B")
        editing.connect_material_property(multiply, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    else:
        editing.connect_material_property(color_node, "", unreal.MaterialProperty.MP_BASE_COLOR)
        rough = editing.create_material_expression(result, unreal.MaterialExpressionConstant, -700, 250)
        rough.set_editor_property("r", 0.5)
        editing.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    editing.recompile_material(result)
    library.save_asset(path, False)
    lines.append("created " + name)
    return result


def face_texture():
    path = DIR + "/T_SunFaces"
    task = unreal.AssetImportTask()
    task.filename = os.path.join(SOURCE, "T_SunFaces.png")
    task.destination_path = DIR
    task.automated = True
    task.save = True
    task.replace_existing = True
    tools.import_asset_tasks([task])
    lines.append("imported T_SunFaces")
    return unreal.load_asset(path)


def face_material(texture):
    # Unlit and masked: the atlas cell for FaceIndex (column FaceIndex % 4, row FaceIndex / 4), cut out by its alpha.
    path = DIR + "/M_SunFace"
    if library.does_asset_exist(path):
        existing = unreal.load_asset(path)
        if "Faces" in [str(n) for n in editing.get_texture_parameter_names(existing)]:
            return existing
        library.delete_asset(path)  # The single-colour face from before the atlas.
        lines.append("replaced old M_SunFace")
    result = tools.create_asset("M_SunFace", DIR, unreal.Material, unreal.MaterialFactoryNew())
    result.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    result.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
    # SM_Sun is imported as a Nanite mesh; without this flag the editor warns and packaged builds may not draw the face.
    result.set_editor_property("used_with_nanite", True)

    def node(kind, x, y):
        return editing.create_material_expression(result, kind, x, y)

    def link(a, a_out, b, b_in):
        if not editing.connect_material_expressions(a, a_out, b, b_in):
            raise RuntimeError("M_SunFace: could not link into " + b_in)

    index = node(unreal.MaterialExpressionScalarParameter, -1700, 200)
    index.set_editor_property("parameter_name", "FaceIndex")
    columns = node(unreal.MaterialExpressionConstant, -1700, 350)
    columns.set_editor_property("r", float(FACE_COLUMNS))
    column = node(unreal.MaterialExpressionFmod, -1450, 150)
    link(index, "", column, "A")
    link(columns, "", column, "B")
    divided = node(unreal.MaterialExpressionDivide, -1450, 300)
    link(index, "", divided, "A")
    link(columns, "", divided, "B")
    row = node(unreal.MaterialExpressionFloor, -1250, 300)
    link(divided, "", row, "")
    cell = node(unreal.MaterialExpressionAppendVector, -1050, 200)
    link(column, "", cell, "A")
    link(row, "", cell, "B")
    coords = node(unreal.MaterialExpressionTextureCoordinate, -1050, 0)
    shifted = node(unreal.MaterialExpressionAdd, -850, 100)
    link(coords, "", shifted, "A")
    link(cell, "", shifted, "B")
    grid = node(unreal.MaterialExpressionConstant2Vector, -850, 300)
    grid.set_editor_property("r", float(FACE_COLUMNS))
    grid.set_editor_property("g", float(FACE_ROWS))
    uv = node(unreal.MaterialExpressionDivide, -650, 150)
    link(shifted, "", uv, "A")
    link(grid, "", uv, "B")
    sample = node(unreal.MaterialExpressionTextureSampleParameter2D, -450, 100)
    sample.set_editor_property("parameter_name", "Faces")
    sample.set_editor_property("texture", texture)
    link(uv, "", sample, "UVs")
    glow = node(unreal.MaterialExpressionScalarParameter, -450, 400)
    glow.set_editor_property("parameter_name", "Glow")
    glow.set_editor_property("default_value", 1.0)
    lit = node(unreal.MaterialExpressionMultiply, -200, 100)
    link(sample, "RGB", lit, "A")
    link(glow, "", lit, "B")
    editing.connect_material_property(lit, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    editing.connect_material_property(sample, "A", unreal.MaterialProperty.MP_OPACITY_MASK)
    editing.recompile_material(result)
    library.save_asset(path, False)
    lines.append("created M_SunFace")
    return result


def face_variables(bp):
    pins = unreal.BlueprintEditorLibrary
    variables = [
        ("FaceIndex", pins.get_basic_type_by_name("int"), True),
        ("AutoSwitchSeconds", pins.get_basic_type_by_name("real"), True),
        ("FaceTime", pins.get_basic_type_by_name("real"), False),
        ("FaceMaterial", pins.get_object_reference_type(unreal.MaterialInstanceDynamic), False),
    ]
    defaults = unreal.get_default_object(bp.generated_class())
    for name, pin_type, editable in variables:
        # add_member_variable would quietly add Name_0 next to an existing one, so check first.
        try:
            defaults.get_editor_property(name)
            continue
        except Exception:
            pass
        if not pins.add_member_variable(bp, name, pin_type):
            raise RuntimeError("Could not add " + name)
        if editable:
            pins.set_blueprint_variable_instance_editable(bp, name, True)
        lines.append("  variable " + name)
    pins.compile_blueprint(bp)
    defaults = unreal.get_default_object(bp.generated_class())
    for name, value in SETTINGS.items():
        defaults.set_editor_property(name, value)
    library.save_asset(DIR + "/BP_Sun", False)


def blueprint(sun_mesh):
    path = DIR + "/BP_Sun"
    if library.does_asset_exist(path):
        lines.append("BP_Sun: already there")
        face_variables(unreal.load_asset(path))
        return
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    bp = tools.create_asset("BP_Sun", DIR, unreal.Blueprint, factory)
    root = subsystem.k2_gather_subobject_data_for_blueprint(bp)[0]
    params = unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.StaticMeshComponent, blueprint_context=bp)
    handle, _ = subsystem.add_new_subobject(params)
    subsystem.rename_subobject(handle, unreal.Text("SunMesh"))
    component = data_library.get_object(data_library.get_data(handle))
    component.set_editor_property("static_mesh", sun_mesh)
    component.set_collision_profile_name("NoCollision")
    component.set_editor_property("cast_shadow", False)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    library.save_asset(path, False)
    lines.append("created BP_Sun")
    face_variables(bp)


sun = mesh()
body = material("M_SunBody", unreal.LinearColor(1.0, 0.42, 0.1, 1.0), 3.0, True)
face = face_material(face_texture())
# Slots by name, as the FBX named them; items of a struct array are copies, so each is written back.
slots = sun.get_editor_property("static_materials")
for index in range(len(slots)):
    slot = slots[index]
    slot.set_editor_property("material_interface", face if "Face" in str(slot.get_editor_property("material_slot_name")) else body)
    slots[index] = slot
    lines.append("slot {} {}".format(index, slot.get_editor_property("material_slot_name")))
sun.set_editor_property("static_materials", slots)
library.save_asset(DIR + "/SM_Sun", False)
blueprint(sun)

# The FBX import brings its own materials; the mesh now uses the ones above.
for path in library.list_assets(DIR, recursive=False):
    package = path.split(".")[0]
    name = package.split("/")[-1]
    asset_data = library.find_asset_data(package)
    if name not in ("M_SunBody", "M_SunFace") and str(asset_data.asset_class_path.asset_name) in ("Material", "MaterialInstanceConstant") and not library.find_package_referencers_for_asset(package):
        lines.append("removed import material {}: {}".format(name, library.delete_asset(package)))
bounds = sun.get_bounds()
lines.append("SM_Sun extent {}".format(bounds.box_extent))
lines.append("folder: {}".format([p.split(".")[-1] for p in library.list_assets(DIR, recursive=False)]))
with open(os.path.join(unreal.Paths.project_saved_dir(), "sun_import_report.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines))
unreal.log("\n".join(str(l) for l in lines))
