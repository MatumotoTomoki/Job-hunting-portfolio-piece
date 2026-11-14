# Gives the sky meshes simple collision (the FBX import did not bring the UBX_/UCX_ shapes in).
# The editor helper functions refuse to run in a commandlet, so the boxes are written into the body setup directly.
#   SM_SkyCloud : one flat box 80 x 80 cm, Z -30..0 (the feet stand on the top at Z 0)
#   SM_SkyIsland: six thin boxes turned 30 degrees apart - together a near-round top of radius 46..47.5, Z -40..0
# Writes Saved/sky_collision.txt.
import os
import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Sky"
lines = []


def box(cx, cy, cz, x, y, z, yaw=0.0):
    elem = unreal.KBoxElem()
    elem.set_editor_property("center", unreal.Vector(cx, cy, cz))
    elem.set_editor_property("rotation", unreal.Rotator(0.0, 0.0, yaw))
    elem.set_editor_property("x", x)
    elem.set_editor_property("y", y)
    elem.set_editor_property("z", z)
    return elem


def apply(name, boxes):
    path = DIR + "/" + name
    mesh = unreal.load_asset(path)
    body = mesh.get_editor_property("body_setup")
    geom = body.get_editor_property("agg_geom")
    geom.set_editor_property("box_elems", boxes)
    geom.set_editor_property("convex_elems", [])
    geom.set_editor_property("sphyl_elems", [])
    geom.set_editor_property("sphere_elems", [])
    body.set_editor_property("agg_geom", geom)
    body.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_DEFAULT)
    mesh.set_editor_property("body_setup", body)
    unreal.EditorAssetLibrary.save_asset(path, False)
    check = unreal.load_asset(path).get_editor_property("body_setup").get_editor_property("agg_geom")
    lines.append("{} boxes {} first {}".format(name, len(check.get_editor_property("box_elems")),
                                               check.get_editor_property("box_elems")[0].get_editor_property("center")))


apply("SM_SkyCloud", [box(0.0, 0.0, -15.0, 80.0, 80.0, 30.0)])
apply("SM_SkyIsland", [box(0.0, 0.0, -20.0, 92.0, 24.0, 40.0, yaw) for yaw in (0.0, 30.0, 60.0, 90.0, 120.0, 150.0)])

with open(os.path.join(unreal.Paths.project_saved_dir(), "sky_collision.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(lines) + "\n")
