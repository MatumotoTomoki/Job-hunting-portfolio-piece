# Writes the selected actors (label, class, folder, location, rotation, bounds) to Saved/print_selected.txt, for
# placing things next to them. Read-only. From the Output Log:
#   exec(open(r"<full path>\print_selected.py", encoding="utf-8").read())
import os

import unreal

actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
lines = ["level: " + world.get_path_name()]
for a in actors.get_selected_level_actors():
    origin, extent = a.get_actor_bounds(False)
    lines.append("{} | {} | {} | loc {} | rot {} | bounds center {} extent {}".format(
        a.get_actor_label(), a.get_class().get_name(), a.get_folder_path(), a.get_actor_location(),
        a.get_actor_rotation(), origin, extent))
if len(lines) == 1:
    lines.append("nothing selected")
# The viewport camera, and what it looks at (center of the screen), for places that cannot be clicked.
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
cam_loc, cam_rot = editor.get_level_viewport_camera_info()
lines.append("camera loc {} rot {}".format(cam_loc, cam_rot))
end = cam_loc + cam_rot.get_forward_vector() * 20000.0
try:
    hit = unreal.SystemLibrary.line_trace_single(world, cam_loc, end, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False,
                                                 [], unreal.DrawDebugTrace.NONE, True)
    if hit:
        t = hit.to_tuple()
        lines.append("center of screen hits {} at {} normal {}".format(
            t[9].get_actor_label() if t[9] else None, t[4], t[7]))
    else:
        lines.append("center of screen hits nothing")
except Exception as error:
    lines.append("trace failed: {}".format(error))
with open(os.path.join(unreal.Paths.project_saved_dir(), "print_selected.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(str(l) for l in lines) + "\n")
unreal.log("\n".join(str(l) for l in lines))
