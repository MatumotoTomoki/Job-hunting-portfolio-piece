# Coyote time for the player (the user, 2026-11-20): a jump pressed just after walking off an edge (within CoyoteTime
# seconds) still jumps, once. Adds the character variables CoyoteTime (editable, 0.1 s; 0 turns it off), CoyoteReady
# and LeftGroundAt. The graph comes from CoyoteTime_Character.txt (Generators/gen_coyote_time.ps1). Safe to run again.
# With the editor closed:
#   UnrealEditor-Cmd.exe <full path>\JobHunting.uproject -run=pythonscript -script=<full path>\setup_coyote_time.py -unattended -nop4 -nosplash -stdout
import os

import unreal

CHARACTER_PATH = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter1"
library = unreal.EditorAssetLibrary
bp_library = unreal.BlueprintEditorLibrary
lines = []

character = unreal.load_asset(CHARACTER_PATH)
defaults = unreal.get_default_object(character.generated_class())
real = bp_library.get_basic_type_by_name("real")
for name, pin_type, editable in (("CoyoteTime", real, True), ("CoyoteReady", bp_library.get_basic_type_by_name("bool"), False),
                                 ("LeftGroundAt", real, False)):
    # add_member_variable would quietly add Name_0 next to an existing one, so check first.
    try:
        defaults.get_editor_property(name)
        lines.append("character {}: already there".format(name))
    except Exception:
        added = bp_library.add_member_variable(character, name, pin_type)
        if added and editable:
            bp_library.set_blueprint_variable_instance_editable(character, name, True)
        lines.append("character {}: {}".format(name, "added" if added else "NOT added"))
bp_library.compile_blueprint(character)
defaults = unreal.get_default_object(character.generated_class())
if "character CoyoteTime: added" in lines:
    defaults.set_editor_property("CoyoteTime", 0.1)
lines.append("CoyoteTime = {}".format(defaults.get_editor_property("CoyoteTime")))
library.save_asset(CHARACTER_PATH, False)

with open(os.path.join(unreal.Paths.project_saved_dir(), "coyote_time.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
