# Paints the "cleaner heaven's debris" textures for area 2's gimmicks (the user, 2026-11-17: heaven's debris, but a
# little more beautiful than area 1's - the higher the player climbs, the nearer heaven and the less worn its debris).
# Same layout as area 1's T_RuinsDebris (build_ruins_blender.py): the engine cube spans the texture once per face, a
# gold band round every face's edge glows through the _E mask. Here the marble is polished and unstained (fine soft
# veins, no chips or grime), the band is narrower and crisp with a fine inner gold line and small corner squares, and a
# thin dark groove sets the inlay off. Into SourceArt/Models/HeavenDebris/Textures (1024 PNG):
#   T_HeavenClean_C / _N / _E   white marble, gold inlay; _E = the inlay (glow mask)
#   T_HeavenTint_C              the same, inlay in pale platinum, for colour-glowing pieces (red/blue switch blocks)
#   T_HeavenMarble_C / _N       marble alone, no inlay (gears, posts: shapes whose UVs don't follow the cube's)
#   T_HeavenBlack_E             no glow
# With --preview <out.png> it also renders a check picture (Eevee) of a platform, a red and a blue block and a plain
# marble block. Run:
#   blender --background --factory-startup --python build_heaven_clean_textures.py -- [--preview out.png]
import math
import os
import sys

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(os.path.dirname(HERE), "SourceArt", "Models", "HeavenDebris", "Textures")
TEX = 1024
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
PREVIEW = args[args.index("--preview") + 1] if "--preview" in args else None
TIERS = "--tiers" in args   # with --preview: four platforms side by side, areas 1 to 4, left to right
RUINS_TEX = os.path.join(os.path.dirname(HERE), "SourceArt", "Models", "Ruins", "Textures")
os.makedirs(OUT_DIR, exist_ok=True)


def noise(size, scale, seed):
    rng = np.random.default_rng(seed)
    spectrum = np.fft.fft2(rng.standard_normal((size, size)))
    f = np.fft.fftfreq(size)
    fx, fy = np.meshgrid(f, f)
    spectrum *= np.exp(-(fx * fx + fy * fy) * (scale * scale) * 2.0)
    out = np.real(np.fft.ifft2(spectrum))
    out -= out.min()
    return out / max(out.max(), 1e-6)


def fbm(size, seed, scales=(128, 48, 16, 6), weights=(0.5, 0.25, 0.15, 0.1)):
    out = np.zeros((size, size))
    for i, (sc, w) in enumerate(zip(scales, weights)):
        out += w * noise(size, sc, seed + i)
    return out / sum(weights)


def normal_from(height, strength):
    dx = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) * strength
    dy = (np.roll(height, -1, 0) - np.roll(height, 1, 0)) * strength
    n = np.dstack((-dx, dy, np.ones_like(height)))
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return n * 0.5 + 0.5


def tint(base, amount):
    return np.dstack([base[i] * amount for i in range(3)])


def save(name, rgb):
    image = bpy.data.images.new(name, TEX, TEX, alpha=False)
    rgba = np.ones((TEX, TEX, 4), dtype=np.float32)
    rgba[:, :, :3] = np.clip(rgb, 0.0, 1.0)
    image.pixels.foreach_set(rgba[::-1].reshape(-1))     # Blender rows run bottom to top
    image.filepath_raw = os.path.join(OUT_DIR, name + ".png")
    image.file_format = "PNG"
    image.save()
    return image


yy, xx = np.mgrid[0:TEX, 0:TEX] / TEX
fine = noise(TEX, 2, 7)
# Polished marble: warm white, soft thin veins, a faint cloudiness - no stains or chips.
# Veins: long soft diagonal streaks (a gently warped sine, only its troughs show), one main set and a fainter one.
warp = fbm(TEX, 91, (300, 120, 40, 12))
main = np.abs(np.sin((xx * 1.2 + yy * 0.7 + warp * 0.9) * math.pi * 2.0))
faint = np.abs(np.sin((xx * 0.5 - yy * 1.9 + fbm(TEX, 93, (260, 90, 30, 10)) * 1.1) * math.pi * 3.0))
veins = 1.0 - (1.0 - main ** 0.15) * 0.3 - (1.0 - faint ** 0.1) * 0.12
cloud = fbm(TEX, 95, (260, 120, 40, 12))
marble = tint(np.array([0.95, 0.94, 0.91]), veins * (0.95 + 0.06 * cloud))

# The inlay: a crisp band near the edge, a fine inner line, small squares in the corners; a dark groove outside each.
border = np.minimum(np.minimum(xx, 1.0 - xx), np.minimum(yy, 1.0 - yy))
corner = np.maximum(np.minimum(xx, 1.0 - xx), np.minimum(yy, 1.0 - yy))   # distance from the nearest corner, roughly
band = ((border > 0.03) & (border < 0.06)).astype(float)
line = ((border > 0.085) & (border < 0.092)).astype(float)
square = ((corner > 0.06) & (corner < 0.13) & (border > 0.06)).astype(float) * ((corner < 0.13)).astype(float)
square *= ((np.minimum(xx, 1.0 - xx) < 0.13) & (np.minimum(yy, 1.0 - yy) < 0.13)).astype(float)
inlay = np.clip(band + line + square, 0.0, 1.0)
groove = (((border > 0.025) & (border < 0.03)) | ((border > 0.06) & (border < 0.065))).astype(float)
groove = np.clip(groove - inlay, 0.0, 1.0)

for name, metal in (("Clean", np.array([0.92, 0.64, 0.24])), ("Tint", np.array([0.9, 0.9, 0.93]))):
    shine = tint(metal, 0.9 + 0.15 * noise(TEX, 8, 97))
    colour = marble * (1.0 - inlay[..., None]) + shine * inlay[..., None]
    colour = colour * (1.0 - 0.6 * groove[..., None])
    save("T_Heaven" + name + "_C", colour)
height = (1.0 - veins) * 0.02 + inlay * 0.25 - groove * 0.35 + fine * 0.02
save("T_HeavenClean_N", normal_from(height, 4.0))
save("T_HeavenClean_E", np.dstack([inlay * (0.85 + 0.15 * noise(TEX, 12, 99))] * 3))
save("T_HeavenMarble_C", marble)
save("T_HeavenMarble_N", normal_from((1.0 - veins) * 0.02 + fine * 0.02, 4.0))
save("T_HeavenBlack_E", np.zeros((TEX, TEX, 3)))
# Gold (gear hubs, gondola posts): faintly brushed, glowing softly all over through a white mask.
brushed = np.repeat(noise(TEX, 40, 101)[:, :1], TEX, axis=1) * 0.5 + noise(TEX, 3, 103) * 0.5
save("T_HeavenGold_C", tint(np.array([0.92, 0.64, 0.24]), 0.85 + 0.25 * brushed))
save("T_HeavenWhite_E", np.ones((TEX, TEX, 3)))

# ----- the higher areas: the debris gets cleaner the nearer heaven (the user, 2026-11-17) -----
# Area 3 "Pure": whiter marble, veins barely there; the inlay gains a second fine line and a small diamond at the
# middle of each edge. Area 4 "Holy": almost new, near-white marble that glows faintly itself; on top of area 3's
# inlay, a double ring medallion in the middle of every face.
along = np.where(np.minimum(yy, 1.0 - yy) <= np.minimum(xx, 1.0 - xx), xx, yy)   # position along the nearest edge
diamond = ((np.abs(along - 0.5) + np.abs(border - 0.075) * 1.6) < 0.035).astype(float)
line2 = ((border > 0.108) & (border < 0.113)).astype(float)
radius = np.sqrt((xx - 0.5) ** 2 + (yy - 0.5) ** 2)
rings = ((np.abs(radius - 0.2) < 0.007) | (np.abs(radius - 0.17) < 0.0035)).astype(float)
for name, base, vein_depth, extra, self_glow in (("Pure", [0.97, 0.96, 0.94], 0.12, diamond + line2, 0.0),
                                                ("Holy", [0.985, 0.975, 0.955], 0.05, diamond + line2 + rings, 0.06)):
    stone = tint(np.array(base), (1.0 - (1.0 - main ** 0.15) * vein_depth) * (0.97 + 0.04 * cloud))
    pattern = np.clip(inlay + extra, 0.0, 1.0)
    edge = np.clip(groove - pattern, 0.0, 1.0)
    shine = tint(np.array([0.95, 0.7, 0.28]), 0.92 + 0.12 * noise(TEX, 8, 97))
    colour = stone * (1.0 - pattern[..., None]) + shine * pattern[..., None]
    save("T_Heaven" + name + "_C", colour * (1.0 - 0.5 * edge[..., None]))
    save("T_Heaven" + name + "_N", normal_from((1.0 - main) * 0.01 + pattern * 0.25 - edge * 0.3 + fine * 0.01, 4.0))
    save("T_Heaven" + name + "_E", np.dstack([np.clip(pattern * (0.88 + 0.12 * noise(TEX, 12, 99)) + self_glow, 0.0, 1.0)] * 3))

# ----- the gear (SM_Gear, UVs seen from above: centre 0.5, 0.5, tooth tips at radius 0.5 = 100 cm) -----
# Area 2's clean debris as a wheel: polished marble with a gold band and a fine line inside the teeth, a ring round
# the hub, gold rims round the six (dark) spoke holes and thin gold spokes between them; a groove round the band.
gr = np.sqrt((xx - 0.5) ** 2 + (yy - 0.5) ** 2)
ga = np.arctan2(yy - 0.5, xx - 0.5)
g_band = ((gr > 0.372) & (gr < 0.394)).astype(float)
g_line = ((gr > 0.348) & (gr < 0.353)).astype(float)
g_hub = ((gr > 0.148) & (gr < 0.16)).astype(float)
g_holes = np.zeros_like(gr)
for k in range(6):
    a = math.radians(30.0 + 60.0 * k)
    d = np.sqrt((xx - 0.5 - 0.26 * math.cos(a)) ** 2 + (yy - 0.5 - 0.26 * math.sin(a)) ** 2)
    g_holes = np.maximum(g_holes, ((d > 0.065) & (d < 0.078)).astype(float))
spoke_angle = np.abs(((ga + math.pi / 6.0) % (math.pi / 3.0)) - math.pi / 6.0)   # distance to the nearest k x 60 deg
g_spokes = ((spoke_angle * gr < 0.0035) & (gr > 0.16) & (gr < 0.348)).astype(float)
g_inlay = np.clip(g_band + g_line + g_hub + g_holes + g_spokes, 0.0, 1.0)
g_groove = np.clip((((gr > 0.366) & (gr < 0.372)) | ((gr > 0.394) & (gr < 0.4))).astype(float) - g_inlay, 0.0, 1.0)
shine = tint(np.array([0.92, 0.64, 0.24]), 0.9 + 0.15 * noise(TEX, 8, 97))
colour = marble * (1.0 - g_inlay[..., None]) + shine * g_inlay[..., None]
save("T_HeavenGear_C", colour * (1.0 - 0.55 * g_groove[..., None]))
save("T_HeavenGear_N", normal_from((1.0 - veins) * 0.02 + g_inlay * 0.25 - g_groove * 0.3 + fine * 0.02, 4.0))
save("T_HeavenGear_E", np.dstack([g_inlay * (0.85 + 0.15 * noise(TEX, 12, 99))] * 3))
print("textures in", OUT_DIR)

# ----- a check picture -----
if PREVIEW:
    scene = bpy.context.scene
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj)
    scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720

    def load(name, colour=True):
        image = bpy.data.images.load(os.path.join(RUINS_TEX if name.startswith("T_Ruins") else OUT_DIR, name + ".png"))
        if not colour:
            image.colorspace_settings.name = "Non-Color"
        return image

    def material(name, color_tex, normal_tex, mask_tex, glow_rgb, glow, rough):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        bsdf = nodes["Principled BSDF"]
        c = nodes.new("ShaderNodeTexImage"); c.image = load(color_tex)
        n = nodes.new("ShaderNodeTexImage"); n.image = load(normal_tex, False)
        m = nodes.new("ShaderNodeTexImage"); m.image = load(mask_tex, False)
        nmap = nodes.new("ShaderNodeNormalMap")
        links.new(c.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(n.outputs["Color"], nmap.inputs["Color"])
        links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
        mul = nodes.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"; mul.inputs[0].default_value = 1.0
        links.new(m.outputs["Color"], mul.inputs[6])
        mul.inputs[7].default_value = (*glow_rgb, 1.0)
        links.new(mul.outputs[2], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = glow
        bsdf.inputs["Roughness"].default_value = rough
        return mat

    looks = {
        "clean": material("Clean", "T_HeavenClean_C", "T_HeavenClean_N", "T_HeavenClean_E", (1.0, 0.7, 0.3), 1.5, 0.3),
        "red": material("Red", "T_HeavenTint_C", "T_HeavenClean_N", "T_HeavenClean_E", (1.0, 0.12, 0.08), 4.0, 0.3),
        "blue": material("Blue", "T_HeavenTint_C", "T_HeavenClean_N", "T_HeavenClean_E", (0.1, 0.35, 1.0), 4.0, 0.3),
        "marble": material("Marble", "T_HeavenMarble_C", "T_HeavenMarble_N", "T_HeavenBlack_E", (0, 0, 0), 0.0, 0.3),
        "area1": material("Area1", "T_RuinsDebris_C", "T_RuinsDebris_N", "T_RuinsDebris_E", (1.0, 0.75, 0.35), 2.0, 0.5),
        "area3": material("Area3", "T_HeavenPure_C", "T_HeavenPure_N", "T_HeavenPure_E", (1.0, 0.72, 0.32), 1.2, 0.25),
        "area4": material("Area4", "T_HeavenHoly_C", "T_HeavenHoly_N", "T_HeavenHoly_E", (1.0, 0.78, 0.4), 1.6, 0.2),
    }

    def cube(loc, size, look):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
        obj = bpy.context.object
        obj.scale = size
        # As UE's engine cube: every face spans the whole texture once.
        uv = obj.data.uv_layers.active.data
        for poly in obj.data.polygons:
            for k, li in enumerate(poly.loop_indices):
                uv[li].uv = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))[k % 4]
        if look:
            obj.data.materials.append(looks[look])
        return obj

    if "--gear" in args:
        # SM_Gear (build_gear_blender.py) dressed as the spinning gear / great gear: the gear texture on the wheel,
        # gold on the hub and the tooth sides, dark spoke holes. One lying flat, one stood on edge.
        looks["gear"] = material("Gear", "T_HeavenGear_C", "T_HeavenGear_N", "T_HeavenGear_E", (1.0, 0.7, 0.3), 1.0, 0.3)
        looks["gold"] = material("Gold", "T_HeavenGold_C", "T_HeavenMarble_N", "T_HeavenWhite_E", (1.0, 0.7, 0.3), 0.15, 0.25)
        shadow = bpy.data.materials.new("Shadow"); shadow.use_nodes = True
        shadow.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1.0)
        gear_fbx = os.path.join(os.path.dirname(HERE), "SourceArt", "Models", "Gear", "SM_Gear.fbx")
        for loc, rot in (((-1.3, 0.0, 0.2), (0.0, 0.0, 0.0)), ((1.4, 0.6, 1.1), (math.radians(80), 0.0, math.radians(10)))):
            bpy.ops.import_scene.fbx(filepath=gear_fbx)
            obj = bpy.context.selected_objects[0]
            obj.location, obj.rotation_euler = loc, rot
            for i, mat in enumerate((looks["gear"], looks["gold"], shadow)):
                if i < len(obj.data.materials):
                    obj.data.materials[i] = mat
    elif TIERS:
        for i, look in enumerate(("area1", "clean", "area3", "area4")):   # 300 x 300 x 20 platforms, areas 1..4
            cube((-5.1 + i * 3.4, 0.0, 0.1), (3.0, 3.0, 0.2), look)
    else:
        cube((0.0, 0.0, 0.1), (3.0, 3.0, 0.2), "clean")          # a 300 x 300 x 20 platform
        cube((3.2, 0.5, 0.5), (1.0, 1.0, 1.0), "red")            # switch blocks (1 m cubes)
        cube((4.6, -0.6, 0.5), (1.0, 1.0, 1.0), "blue")
        cube((-2.6, -0.4, 0.5), (1.0, 1.0, 1.0), "marble")
    floor = cube((0.0, 0.0, -0.6), (30.0, 30.0, 0.1), None)
    dark = bpy.data.materials.new("Floor"); dark.use_nodes = True
    dark.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.12, 0.1, 0.08, 1.0)
    floor.data.materials.append(dark)
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(50), 0.0, math.radians(30)))
    bpy.context.object.data.energy = 3.0
    world = bpy.data.worlds.new("W"); scene.world = world; world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.35, 0.3, 0.25, 1.0)
    bpy.ops.object.empty_add(location=(0.0 if TIERS else 1.0, 0.0, 0.0 if TIERS else 0.3))
    target = bpy.context.object
    bpy.ops.object.camera_add(location=(0.0, -10.0, 8.0) if TIERS else (0.5, -6.5, 3.6))
    camera = bpy.context.object
    look_at = camera.constraints.new("TRACK_TO"); look_at.target = target
    camera.data.lens = 32
    scene.camera = camera
    scene.render.filepath = PREVIEW
    bpy.ops.render.render(write_still=True)
    print("preview", PREVIEW)
