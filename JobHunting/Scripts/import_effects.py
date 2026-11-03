# Imports the Effekseer effects: textures first, then the .efk files that refer to them.
# Effekseer looks textures up relative to the effect, so Texture/Smoke.png in an effect at
# /Game/FX/Effekseer must be the asset /Game/FX/Effekseer/Texture/Smoke.
import os
import unreal

EFFECT_DIR = "/Game/FX/Effekseer"
TEXTURE_DIR = EFFECT_DIR + "/Texture"
PROJECT_DIR = os.path.abspath(unreal.Paths.project_dir())
# Kept outside Content: the editor auto-imports source files it finds under Content.
SOURCE_DIR = os.path.join(PROJECT_DIR, "SourceArt", "Effects")

TEXTURES = [
    os.path.join(SOURCE_DIR, "FootRingSmoke", "Texture", "Smoke.png"),
    os.path.join(SOURCE_DIR, "FeatherGold", "Texture", "Feather.png"),
    os.path.join(SOURCE_DIR, "FeatherGold", "Texture", "Particle_Soft.png"),
    os.path.join(SOURCE_DIR, "FeatherGold", "Texture", "Star.png"),
]
EFFECTS = [
    os.path.join(SOURCE_DIR, "FootRingSmoke", "NS_JumpPuff.efk"),
    os.path.join(SOURCE_DIR, "FeatherGold", "NS_DoubleJumpFeather.efk"),
]


def import_files(paths, destination):
    tasks = []
    for path in paths:
        if not os.path.isfile(path):
            raise RuntimeError("Missing file: " + path)
        task = unreal.AssetImportTask()
        task.filename = path
        task.destination_path = destination
        task.automated = True
        task.save = True
        task.replace_existing = True
        tasks.append(task)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    return [task.get_editor_property("imported_object_paths") for task in tasks]


report = []
report.append("textures: " + str(import_files(TEXTURES, TEXTURE_DIR)))
report.append("effects: " + str(import_files(EFFECTS, EFFECT_DIR)))

for name in ("NS_JumpPuff", "NS_DoubleJumpFeather"):
    effect = unreal.load_asset(EFFECT_DIR + "/" + name)
    report.append("%s: %s" % (name, effect))
    if effect:
        report.append("  class: " + effect.get_class().get_path_name())
        for prop in ("Scale", "ColorTextures"):
            try:
                report.append("  %s: %s" % (prop, effect.get_editor_property(prop)))
            except Exception as error:
                report.append("  %s: unreadable (%s)" % (prop, error))

system = unreal.load_asset("/Effekseer/BluePrints/BP_EffekseerSystem")
report.append("system bp: %s" % system)
if system:
    report.append("  generated: " + system.generated_class().get_path_name())
report.append("system component class: %s" % unreal.load_class(None, "/Script/Effekseer.EffekseerSystemComponent"))

with open(os.path.join(unreal.Paths.project_saved_dir(), "effekseer_import_report.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(report))
unreal.log("\n".join(report))
