# The moving island in area 3's "garden ruins" look (the user, 2026-11-19: "make it look like the other islands"):
# one island exactly as build_sky_art_blender.py dresses the static ones (grass top kept flat, flowers, rock with
# strata, spurs, roots and vines, a marble block caught in the rock), built at the origin, 350 cm across (the size
# BP_MovingIsland's collision has), its grass top at Z 0. That script is only borrowed: its source is run here without
# its main(), and its island() is called once.
#   SourceArt/Models/Sky/Moving/SM_MovingIslandArt.fbx   slots M_SkyArt<Slot> (the same MI_SkyArt* in UE)
# With --preview <out.png> a check picture too. Run:
#   blender --background --factory-startup --python build_moving_island_art.py [-- --preview out.png]
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKY_ART = os.path.join(HERE, "build_sky_art_blender.py")
OUT = os.path.join(os.path.dirname(HERE), "SourceArt", "Models", "Sky", "Moving")
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
preview_out = args[args.index("--preview") + 1] if "--preview" in args else None

source = open(SKY_ART, encoding="utf-8").read()
source = source.rsplit("\nmain()", 1)[0]          # everything but the call that builds the sections
sys.argv = [sys.argv[0]]                           # (its own argument parsing sees none)
namespace = {"__file__": SKY_ART, "__name__": "sky_art"}
exec(compile(source, SKY_ART, "exec"), namespace)

bpy = namespace["bpy"]
bpy.ops.wm.read_factory_settings(use_empty=True)
os.makedirs(OUT, exist_ok=True)
builder = namespace["Builder"]()
namespace["island"](builder, 0.0, 0.0, 0.0, 350.0, "Moving Island")
obj = builder.finish("SM_MovingIslandArt")
namespace["OUT_DIR"] = OUT
namespace["export"](obj, "SM_MovingIslandArt")
print("moving island", os.path.join(OUT, "SM_MovingIslandArt.fbx"), len(obj.data.vertices), "vertices")
if preview_out:
    namespace["make_textures"]()
    namespace["preview"](obj, preview_out, (520.0, -620.0, 160.0), (0.0, 0.0, -90.0))
