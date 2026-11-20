# Builds area 3's "garden ruins" art in Blender, straight from area3_layout.py (no Unreal needed): floating islands
# turned into hanging gardens - grass and flowers on top, pale layered rock below with roots, vines and small
# waterfalls, trees growing out of the cliffs - with the white marble and gold of an old sky temple scattered over
# them (paving, broken columns on the rims, blocks in the rock). The marble pieces of the route (gateways, beams,
# the summit column and gate) become carved temple stone. Static pieces only: gimmicks (vanishing clouds, wind,
# moving islands, ...) and the solid clouds are left alone.
#   SourceArt/Models/Sky/Art/SM_Sky_<section letter>.fbx    one mesh per section, world positioned, pivot at the origin
#                                                           slots: Grass Rock Marble Gold Leaf Bark Blossom Water
#                                                           (named M_SkyArt<Slot>)
#   SourceArt/Models/Sky/Art/sky_art_<letter>.json          which kinds of actor the mesh replaces (import_sky_art.py
#                                                           hides those; they stay as the collision)
#   SourceArt/Models/Sky/Art/Textures/T_SkyArt<Slot>_C/_N/_E.png   tileable 1024 colour, normal, glow-mask maps
# What the player stands on stays exactly where the collision is: an island's top is flat at its top over the whole
# collision circle (0.48 x size) and only rolls off beyond it; things on a walkable top are at most a few cm high
# (flowers, tufts, paving 1 cm proud) and anything bigger (columns, trees) stands outside the circle.
# A UE point (x, y, z) cm is put at (x, -y, z) / 100 m here (the FBX import flips Y back).
#   blender --background --factory-startup --python build_sky_art_blender.py -- A [B ...] [--preview out.png cx,cy,cz lx,ly,lz]
import json
import math
import os
import random
import sys
import zlib

import bmesh
import bpy
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import area3_layout  # noqa: E402

OUT_DIR = os.path.join(os.path.dirname(HERE), "SourceArt", "Models", "Sky", "Art")
TEX_DIR = os.path.join(OUT_DIR, "Textures")
SLOTS = ["Grass", "Rock", "Marble", "Gold", "Leaf", "Bark", "Blossom", "Water"]
S = {name: i for i, name in enumerate(SLOTS)}
TEX = 1024
TILE = 2.0
B = 14960.0
MIST = B - 1200.0

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
PREVIEW = None
if "--preview" in args:
    i = args.index("--preview")
    PREVIEW = (args[i + 1], [float(v) for v in args[i + 2].split(",")], [float(v) for v in args[i + 3].split(",")])
    args = args[:i] + args[i + 4:]
SECTIONS = [a.upper() for a in args] or ["A"]


# ===================================================================================================== textures
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


def write_png(name, rgb):
    size = rgb.shape[0]
    image = bpy.data.images.new(name, size, size, alpha=False)
    rgba = np.ones((size, size, 4), dtype=np.float32)
    rgba[:, :, :3] = np.clip(rgb, 0.0, 1.0)
    image.pixels.foreach_set(rgba[::-1].reshape(-1))
    image.filepath_raw = os.path.join(TEX_DIR, name + ".png")
    image.file_format = "PNG"
    image.save()


def normal_from(height, strength):
    dx = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) * strength
    dy = (np.roll(height, -1, 0) - np.roll(height, 1, 0)) * strength
    n = np.dstack((-dx, dy, np.ones_like(height)))
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return n * 0.5 + 0.5


def save(name, rgb, height=None, strength=6.0, mask=None):
    write_png("T_SkyArt" + name + "_C", rgb)
    if height is not None:
        write_png("T_SkyArt" + name + "_N", normal_from(height, strength))
    if mask is not None:
        write_png("T_SkyArt" + name + "_E", np.dstack([mask] * 3))


def tint(base, amount):
    return np.dstack([base[i] * amount for i in range(3)])


def make_textures():
    os.makedirs(TEX_DIR, exist_ok=True)
    yy, xx = np.mgrid[0:TEX, 0:TEX] / TEX
    fine = noise(TEX, 2, 1)
    # Grass: fresh meadow green, lighter clover patches, darker damp hollows, a speckle of blades.
    patches = fbm(TEX, 11, (160, 60, 20, 6))
    clover = np.clip((noise(TEX, 14, 12) - 0.6) * 5.0, 0.0, 1.0)
    blades = noise(TEX, 1.2, 13)
    colour = tint(np.array([0.34, 0.6, 0.2]), (0.7 + 0.45 * patches) * (0.85 + 0.3 * blades))
    colour = colour * (1.0 - 0.35 * clover[..., None]) + tint(np.array([0.55, 0.75, 0.3]), 0.9 + 0.2 * blades) * 0.35 * clover[..., None]
    save("Grass", colour, patches * 0.3 + blades * 0.7, 3.0)
    # Rock: pale warm layered stone (the strata run across the texture: side faces map height to V).
    warp = noise(TEX, 40, 21)
    v = (yy + 0.06 * warp) * 6.0
    layer = np.floor(v)
    shade = np.random.default_rng(22).uniform(0.82, 1.08, 64)[(layer.astype(int)) % 64]
    seam = np.clip(np.abs(v - np.round(v)) * 18.0, 0.0, 1.0)
    grain = fbm(TEX, 23)
    cracks = np.clip(np.abs(noise(TEX, 30, 24) - 0.5) * 25.0, 0.0, 1.0)
    colour = tint(np.array([0.72, 0.64, 0.53]), shade * (0.78 + 0.3 * grain) * (0.6 + 0.4 * seam) * (0.75 + 0.25 * cracks))
    save("Rock", colour, seam * 0.4 + grain * 0.4 - (1.0 - cracks) * 0.25 + fine * 0.1, 5.0)
    # Marble: white with soft grey-gold veins and a faint warm cloudiness.
    clouds = fbm(TEX, 31, (200, 80, 30, 10))
    vein1 = np.clip(1.0 - np.abs(fbm(TEX, 32, (90, 40, 12, 4)) - 0.5) * 60.0, 0.0, 1.0)
    vein2 = np.clip(1.0 - np.abs(noise(TEX, 25, 33) - 0.5) * 90.0, 0.0, 1.0) * 0.6
    veins = np.maximum(vein1, vein2)
    colour = tint(np.array([0.94, 0.93, 0.9]), 0.92 + 0.08 * clouds)
    colour = colour * (1.0 - 0.4 * veins[..., None]) + tint(np.array([0.62, 0.58, 0.52]), np.ones((TEX, TEX))) * 0.4 * veins[..., None]
    save("Marble", colour, clouds * 0.1 - veins * 0.1 + fine * 0.02, 2.0)
    # Gold: polished, a little uneven.
    save("Gold", tint(np.array([0.98, 0.78, 0.38]), 0.9 + 0.12 * noise(TEX, 8, 41)), noise(TEX, 8, 41) * 0.1, 1.0)
    # Leaf: clumps of leaves, light tops and dark gaps.
    clump = noise(TEX, 5, 51)
    leaves = np.clip((clump - 0.35) * 3.0, 0.0, 1.0)
    colour = tint(np.array([0.36, 0.62, 0.24]), (0.35 + 0.75 * leaves) * (0.85 + 0.3 * fbm(TEX, 52)))
    save("Leaf", colour, leaves, 6.0)
    # Bark: grey-brown with long vertical furrows.
    furrow = 0.5 + 0.5 * np.sin(xx * 2.0 * math.pi * 18.0 + 4.0 * noise(TEX, 30, 61))
    colour = tint(np.array([0.42, 0.34, 0.27]), (0.6 + 0.4 * furrow) * (0.85 + 0.3 * noise(TEX, 6, 62)))
    save("Bark", colour, furrow * 0.7 + fine * 0.2, 5.0)
    # Blossom: near white; the vertex colour gives each flower its colour.
    save("Blossom", tint(np.array([0.97, 0.96, 0.95]), 0.88 + 0.12 * noise(TEX, 4, 71)))
    # Water: pale blue-white falling streaks; the streaks glow a little (mask).
    streak = np.clip(noise(TEX, 3, 81)[:, :] * 0.0 + 0.5 + 0.5 * np.sin(xx * 2.0 * math.pi * 30.0 + 6.0 * noise(TEX, 20, 82)), 0.0, 1.0)
    colour = tint(np.array([0.72, 0.86, 0.96]), 0.8 + 0.25 * streak)
    save("Water", colour, streak * 0.3, 2.0, streak * 0.8 + 0.2)
    write_png("T_SkyArtBlack_E", np.zeros((64, 64, 3)))


# ===================================================================================================== meshes
def bl(x, y, z):
    return Vector((x / 100.0, -y / 100.0, z / 100.0))


ROCK_TONES = [(1.0, 0.96, 0.9), (0.93, 0.92, 0.95), (1.0, 0.9, 0.78), (0.9, 0.86, 0.8)]
GRASS_TONES = [(1.0, 1.0, 0.85), (0.86, 1.0, 0.9), (0.95, 0.95, 0.75), (0.9, 1.0, 0.8)]
MARBLE_TONES = [(1.0, 0.99, 0.96), (0.95, 0.96, 1.0), (1.0, 0.96, 0.9)]
LEAF_TONES = [(1.0, 1.0, 0.85), (0.85, 1.0, 0.88), (1.0, 0.92, 0.7)]
FLOWERS = [(1.0, 0.62, 0.75), (1.0, 0.9, 0.45), (1.0, 1.0, 1.0), (0.7, 0.78, 1.0), (1.0, 0.75, 0.55)]


def wash(c):
    s = (math.sin(c.x * 1.3 + c.y * 0.5 + 1.3) * math.sin(c.z * 1.7 - c.x * 0.4 + 0.7)
         + 0.7 * math.sin(c.y * 2.1 - c.z * 0.8 + 2.1) * math.sin(c.x * 2.5 + c.z * 1.1))
    return 0.9 + 0.08 * s


class Builder:
    # One bmesh per section, in Blender metres. Every vertex gets a colour (layer "Col") that the UE material
    # multiplies in: a tone per piece and slot, the rock darkening and warming towards an island's tip, faint
    # strata and a slow wash. Pieces shift their UVs at random so the 2 m tiles don't line up.
    def __init__(self):
        self.bm = bmesh.new()
        self.top, self.depth = 0.0, 1.0
        self.tones = {}
        self.uv = (0.0, 0.0)
        self.paint = None
        self.cyl = None     # (x, y, radius) of the island being built: its rock is wrapped round that axis

    def begin(self, key, top, depth):
        rng = random.Random(zlib.crc32(key.encode("utf-8")))
        self.tones = {S["Rock"]: rng.choice(ROCK_TONES), S["Grass"]: rng.choice(GRASS_TONES),
                      S["Marble"]: rng.choice(MARBLE_TONES), S["Leaf"]: rng.choice(LEAF_TONES), S["Bark"]: (1.0, 1.0, 1.0)}
        self.top, self.depth = top, max(depth, 0.5)
        self.uv = (rng.random(), rng.random())
        self.cyl = None
        return rng

    def shade(self, slot, c):
        if self.paint is not None:
            return self.paint
        if slot not in self.tones:
            return (1.0, 1.0, 1.0, 1.0)
        tone = self.tones[slot]
        f = wash(c)
        if slot == S["Rock"]:
            t = min(1.0, max(0.0, (self.top - c.z) / self.depth))       # 0 at the top, 1 at the tip
            f *= (1.0 - 0.45 * t) * (0.93 + 0.07 * math.sin(c.z * 9.0 + c.x * 0.3))
            tone = (tone[0], tone[1] * (1.0 - 0.06 * t), tone[2] * (1.0 - 0.14 * t))
        elif slot == S["Grass"] and c.z < self.top - 0.02:
            f *= 0.8                                                       # the turf hanging over the edge
        return tuple(min(1.0, v * f) for v in tone) + (1.0,)

    def add(self, new, slot=None):
        # UVs by the face's main direction (tops: X/Y, sides: across/height), colours, then into the section mesh.
        uv = new.loops.layers.uv.new("UVMap")
        col = new.loops.layers.color.new("Col")
        ou, ov = self.uv
        for face in new.faces:
            if slot is not None:
                face.material_index = slot
            n = face.normal
            if face.material_index == S["Rock"] and self.cyl is not None:
                # Island rock: wrapped round the island's axis, so the strata run level all the way round.
                cx, cy, radius = self.cyl
                first = math.atan2(face.loops[0].vert.co.y - cy, face.loops[0].vert.co.x - cx)
                for loop in face.loops:
                    c = loop.vert.co
                    ang = math.atan2(c.y - cy, c.x - cx)
                    ang += 2.0 * math.pi * round((first - ang) / (2.0 * math.pi))
                    loop[uv].uv = (ang * radius / TILE + ou, c.z / TILE + ov)
                    loop[col] = self.shade(face.material_index, c)
                continue
            for loop in face.loops:
                c = loop.vert.co
                if abs(n.z) > 0.7:
                    loop[uv].uv = (c.x / TILE + ou, c.y / TILE + ov)
                elif abs(n.x) > abs(n.y):
                    loop[uv].uv = (c.y / TILE + ou, c.z / TILE + ov)
                else:
                    loop[uv].uv = (c.x / TILE + ou, c.z / TILE + ov)
                loop[col] = self.shade(face.material_index, c)
        mesh = bpy.data.meshes.new("piece")
        new.to_mesh(mesh)
        new.free()
        self.bm.from_mesh(mesh)
        bpy.data.meshes.remove(mesh)

    def box(self, lo, hi, slot, yaw=0.0, centre=None):
        # An axis box (Blender metres), optionally turned by yaw about centre.
        new = bmesh.new()
        bmesh.ops.create_cube(new, size=1.0)
        for v in new.verts:
            v.co = Vector((lo.x if v.co.x < 0 else hi.x, lo.y if v.co.y < 0 else hi.y, lo.z if v.co.z < 0 else hi.z))
        if yaw:
            c = centre or (lo + hi) / 2.0
            ca, sa = math.cos(yaw), math.sin(yaw)
            for v in new.verts:
                d = v.co - c
                v.co = Vector((c.x + d.x * ca - d.y * sa, c.y + d.x * sa + d.y * ca, v.co.z))
        new.normal_update()
        self.add(new, slot)

    def tube(self, a, b, r, slot, segments=10, r_end=None, flutes=0, jag=0.0, rng=None):
        # A cylinder or cone from a to b; flutes: that many grooves round it (columns); jag: a broken, uneven top.
        a, b = Vector(a), Vector(b)
        axis = b - a
        if axis.length < 1e-4:
            return
        axis.normalize()
        helper = Vector((0.0, 0.0, 1.0)) if abs(axis.z) < 0.9 else Vector((1.0, 0.0, 0.0))
        u = axis.cross(helper).normalized()
        w = axis.cross(u)
        n = flutes * 2 if flutes else segments
        new = bmesh.new()
        lo, hi = [], []
        for i in range(n):
            ang = 2.0 * math.pi * i / n
            k = (0.9 if i % 2 else 1.0) if flutes else 1.0
            ring = u * math.cos(ang) + w * math.sin(ang)
            lo.append(new.verts.new(a + ring * r * k))
            top = b + axis * ((rng.uniform(-jag, jag)) if jag and rng else 0.0)
            hi.append(new.verts.new(top + ring * (r if r_end is None else r_end) * k))
        for i in range(n):
            new.faces.new((lo[i], lo[(i + 1) % n], hi[(i + 1) % n], hi[i]))
        new.faces.new(list(reversed(lo)))
        new.faces.new(hi)
        bmesh.ops.recalc_face_normals(new, faces=new.faces)
        self.add(new, slot)

    def blob(self, c, radii, slot, seed, bumps=0.25, subdivisions=2):
        new = bmesh.new()
        bmesh.ops.create_icosphere(new, subdivisions=subdivisions, radius=1.0)
        rng = random.Random(seed)
        p = [rng.uniform(0.0, 6.28) for _ in range(3)]
        for v in new.verts:
            d = v.co.normalized()
            k = 1.0 + bumps * (math.sin(d.x * 3.1 + p[0]) * math.sin(d.y * 2.7 + p[1]) + 0.5 * math.sin(d.z * 4.3 + p[2]))
            v.co = Vector((c[0] + d.x * radii[0] * k, c[1] + d.y * radii[1] * k, c[2] + d.z * radii[2] * k))
        new.normal_update()
        self.add(new, slot)

    def finish(self, name):
        mesh = bpy.data.meshes.new(name)
        self.bm.to_mesh(mesh)
        self.bm.free()
        if mesh.color_attributes:
            mesh.color_attributes.active_color_index = 0
            mesh.color_attributes.render_color_index = 0
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.scene.collection.objects.link(obj)
        for slot in SLOTS:
            obj.data.materials.append(bpy.data.materials.get("M_SkyArt" + slot) or bpy.data.materials.new("M_SkyArt" + slot))
        for p in obj.data.polygons:
            p.use_smooth = p.material_index in (S["Leaf"], S["Rock"], S["Blossom"])
        return obj


# ----------------------------------------------------------------------------------------------- the islands
def clear_angle(a, blocked, width=0.6):
    # Turn a rim angle away from the directions the route comes in or leaves by (columns and trees stay out of the
    # way of a jump): step round until it is more than `width` radians from all of them.
    for _ in range(24):
        if all(abs((a - b_ + math.pi) % (2.0 * math.pi) - math.pi) > width for b_ in blocked):
            return a
        a += 0.27
    return a


def island(b, x, y, top, size, key, blocked=()):
    # SM_SkyIsland's collision is a cylinder r 0.48 x size under a flat top: keep the grass flat over all of it.
    # blocked: angles (Blender frame) towards the neighbouring footholds; columns and trees keep clear of them.
    R = size / 200.0
    flat = 0.965 * R
    c0 = bl(x, y, top)
    zt = c0.z
    depth = 1.4 * R                       # as deep as the old island (Z scale 0.7 x size)
    rng = b.begin(key, zt, depth)
    b.cyl = (c0.x, c0.y, R)
    p = [rng.uniform(0.0, 6.28) for _ in range(4)]

    def edge(a):
        return R * (1.035 + 0.03 * math.sin(3 * a + p[0]) + 0.02 * math.sin(5 * a + p[1]) + 0.012 * math.sin(11 * a + p[2]))

    n = min(120, max(28, int(2.0 * math.pi * R / 0.3)))
    angles = [2.0 * math.pi * i / n for i in range(n)]
    new = bmesh.new()

    def ring(radius_of, z_of):
        return [new.verts.new((c0.x + math.cos(a) * radius_of(a), c0.y + math.sin(a) * radius_of(a), z_of(a))) for a in angles]

    rings, slots = [], []
    inner = max(2, int(flat / 1.1))
    for k in range(1, inner + 1):
        f = k / inner
        rings.append(ring(lambda a, f=f: min(flat, edge(a) - 0.02) * f, lambda a: zt))
        slots.append(S["Grass"])
    # The rim rolls off, the turf hangs over a little, then the rock.
    rings.append(ring(lambda a: edge(a) - 0.005, lambda a: zt - 0.05))
    slots.append(S["Grass"])
    rings.append(ring(lambda a: edge(a) + 0.03, lambda a: zt - 0.16 - 0.06 * math.sin(7 * a + p[3])))
    slots.append(S["Grass"])
    rings.append(ring(lambda a: edge(a) + 0.01, lambda a: zt - 0.3 - 0.05 * math.sin(4 * a + p[0])))
    slots.append(S["Rock"])

    def profile(t):
        return (1.0 - t) ** 0.75

    jitter = [[rng.uniform(0.88, 1.08) for _ in angles] for _ in range(8)]
    levels = [0.1, 0.22, 0.36, 0.5, 0.63, 0.75, 0.86, 0.94]
    for li, t in enumerate(levels):
        ledge = 1.0 + (0.06 if li in (1, 3) else 0.0)        # strata that stick out a little
        rings.append(ring(lambda a, t=t, li=li: edge(a) * profile(t) * ledge * jitter[li][angles.index(a)] + 0.01,
                          lambda a, t=t: zt - 0.3 - t * (depth - 0.3) + 0.06 * math.sin(5 * a + t * 9.0)))
        slots.append(S["Rock"])
    centre = new.verts.new((c0.x, c0.y, zt))
    tip = new.verts.new((c0.x + rng.uniform(-0.1, 0.1) * R, c0.y + rng.uniform(-0.1, 0.1) * R, zt - depth))
    for i in range(n):
        j = (i + 1) % n
        f = new.faces.new((centre, rings[0][i], rings[0][j]))
        f.material_index = S["Grass"]
    for k in range(len(rings) - 1):
        for i in range(n):
            j = (i + 1) % n
            f = new.faces.new((rings[k][i], rings[k + 1][i], rings[k + 1][j], rings[k][j]))
            f.material_index = slots[k + 1] if slots[k + 1] == S["Rock"] else slots[k]
    for i in range(n):
        j = (i + 1) % n
        f = new.faces.new((rings[-1][i], tip, rings[-1][j]))
        f.material_index = S["Rock"]
    bmesh.ops.recalc_face_normals(new, faces=new.faces)
    b.add(new)

    def side(a, t):
        # A point on the rock side at depth fraction t, angle a.
        r = edge(a) * profile(t)
        return Vector((c0.x + math.cos(a) * r, c0.y + math.sin(a) * r, zt - 0.3 - t * (depth - 0.3)))

    # Smaller spurs hanging under the main cone.
    for _ in range(2 + int(R / 2.5)):
        a = rng.uniform(0.0, 2.0 * math.pi)
        t = rng.uniform(0.3, 0.6)
        start = side(a, t) - Vector((math.cos(a), math.sin(a), 0.0)) * 0.3 * R
        b.tube(start, start + Vector((0.0, 0.0, -rng.uniform(0.35, 0.6) * depth)), rng.uniform(0.18, 0.3) * R, S["Rock"],
               segments=9, r_end=0.02)
    # Roots and vines down the rock; some vines carry leaves.
    for _ in range(int(6 + 2.2 * R)):
        a = rng.uniform(0.0, 2.0 * math.pi)
        length = rng.uniform(0.25, 0.75)
        sway = rng.uniform(-0.04, 0.04)
        points = []
        for s in range(7):
            t = length * s / 6.0
            q = side(a + sway * s, t) + Vector((math.cos(a), math.sin(a), 0.0)) * (0.03 + 0.02 * s)
            points.append(q)
        points[0] = Vector((c0.x + math.cos(a) * (edge(a) + 0.02), c0.y + math.sin(a) * (edge(a) + 0.02), zt - 0.12))
        r = rng.uniform(0.018, 0.04)
        for s in range(len(points) - 1):
            b.tube(points[s], points[s + 1], r * (1.0 - 0.1 * s), S["Bark"], segments=5)
        if rng.random() < 0.55:
            for s in range(1, len(points), 1):
                q = points[s]
                b.blob((q.x, q.y, q.z), (0.11, 0.11, 0.08), S["Leaf"], rng.randrange(1 << 30), 0.3, 1)
    # Waterfall: a spring out of the rock running off the island, falling past the tip into the mist.
    if size >= 550.0 and rng.random() < 0.7:
        a = rng.uniform(0.0, 2.0 * math.pi)
        width = rng.uniform(0.3, 0.55)
        out = Vector((math.cos(a), math.sin(a), 0.0))
        across = Vector((-math.sin(a), math.cos(a), 0.0))
        start = side(a, 0.05) + out * 0.04
        fall = depth + rng.uniform(4.0, 7.0)
        new = bmesh.new()
        verts = []
        steps = 10
        for s in range(steps + 1):
            t = s / steps
            centre_q = start + out * (0.12 * t + 0.35 * t * t) + Vector((0.0, 0.0, -fall * t))
            w = width * (1.0 + 0.8 * t)
            back = centre_q - out * 0.01             # the back sheet: the water is seen from both sides
            verts.append((new.verts.new(centre_q - across * w / 2.0), new.verts.new(centre_q + across * w / 2.0),
                          new.verts.new(back - across * w / 2.0), new.verts.new(back + across * w / 2.0)))
        for s in range(steps):
            (a0, a1, c0_, c1), (b0, b1, d0, d1) = verts[s], verts[s + 1]
            new.faces.new((a0, a1, b1, b0))
            new.faces.new((c0_, d0, d1, c1))
        new.normal_update()
        b.add(new, S["Water"])
        # The spring's mouth: a dark wet notch of rock round it.
        b.blob((start.x, start.y, start.z + 0.05), (width * 0.7, width * 0.7, 0.18), S["Rock"], rng.randrange(1 << 30), 0.2, 1)
    # Paving of the old temple, flush with the grass (1 cm proud), some slabs missing.
    if size >= 550.0:
        a = rng.uniform(0.0, 2.0 * math.pi)
        d = rng.uniform(0.1, 0.45) * R
        px, py = c0.x + math.cos(a) * d, c0.y + math.sin(a) * d
        yaw = rng.uniform(0.0, math.pi)
        cols, rows_ = rng.randint(3, 5), rng.randint(2, 4)
        slab = rng.uniform(0.7, 0.95)
        for i in range(cols):
            for j in range(rows_):
                if rng.random() < 0.25:
                    continue
                ox, oy = (i - (cols - 1) / 2.0) * slab, (j - (rows_ - 1) / 2.0) * slab
                ca, sa = math.cos(yaw), math.sin(yaw)
                qx, qy = px + ox * ca - oy * sa, py + ox * sa + oy * ca
                if math.hypot(qx - c0.x, qy - c0.y) > flat - slab:
                    continue
                g = 0.03
                b.box(Vector((qx - slab / 2 + g, qy - slab / 2 + g, zt - 0.06)), Vector((qx + slab / 2 - g, qy + slab / 2 - g, zt + 0.01)),
                      S["Marble"], yaw + rng.uniform(-0.04, 0.04), Vector((qx, qy, zt)))
    # Broken columns standing on the rim, just outside the footing; their feet sunk into the rock.
    count = 0 if size < 500.0 else (1 if size < 900.0 else 3)
    for k in range(count):
        a = rng.uniform(0.0, 2.0 * math.pi) if k == 0 else a + rng.uniform(0.5, 1.4)
        a = clear_angle(a, blocked)
        r_col = rng.uniform(0.22, 0.32)
        at = Vector((c0.x + math.cos(a) * (edge(a) + r_col + 0.05), c0.y + math.sin(a) * (edge(a) + r_col + 0.05), 0.0))
        h = rng.uniform(0.6, 2.8)
        lean = Vector((math.cos(a), math.sin(a), 0.0)) * rng.uniform(0.0, 0.12) * h
        foot = Vector((at.x, at.y, zt - 0.9))
        b.box(Vector((at.x - r_col * 1.3, at.y - r_col * 1.3, zt - 0.9)), Vector((at.x + r_col * 1.3, at.y + r_col * 1.3, zt - 0.55)), S["Marble"], a)
        head = Vector((at.x, at.y, zt + h)) + lean
        b.tube(foot, head, r_col, S["Marble"], flutes=10, jag=0.12 * r_col, rng=rng)
        if h > 2.2:                                   # a whole one: its gold necking ring and a capital
            b.tube(head - Vector((0.0, 0.0, 0.12)), head - Vector((0.0, 0.0, 0.04)), r_col * 1.06, S["Gold"], segments=16)
            b.box(Vector((head.x - r_col * 1.35, head.y - r_col * 1.35, head.z)), Vector((head.x + r_col * 1.35, head.y + r_col * 1.35, head.z + 0.16)), S["Marble"], a)
        # a fallen drum beside it, half in the turf over the edge
        if rng.random() < 0.6:
            a2 = a + rng.choice((-1, 1)) * 0.12 * R / max(R, 1.0)
            q = Vector((c0.x + math.cos(a2) * (edge(a2) + 0.3), c0.y + math.sin(a2) * (edge(a2) + 0.3), zt - 0.2))
            along = Vector((-math.sin(a2), math.cos(a2), rng.uniform(-0.2, 0.0))).normalized() * 0.45
            b.tube(q - along, q + along, r_col * 0.95, S["Marble"], flutes=10)
    # Marble blocks caught in the rock, as if the island grew round the temple.
    for _ in range(1 + int(R / 3.0)):
        a = rng.uniform(0.0, 2.0 * math.pi)
        t = rng.uniform(0.12, 0.4)
        q = side(a, t)
        s = rng.uniform(0.35, 0.7)
        b.box(q - Vector((s, s * 0.6, s * 0.4)), q + Vector((s * 0.4, s * 0.6, s * 0.4)), S["Marble"], a + rng.uniform(-0.3, 0.3), q)
    # Trees growing out of the cliff below the rim and leaning out over the drop, canopy high over the edge.
    trees = 0 if size < 500.0 else (1 if size < 900.0 else 3)
    for k in range(trees):
        a = clear_angle(rng.uniform(0.0, 2.0 * math.pi), blocked)
        out = Vector((math.cos(a), math.sin(a), 0.0))
        root = side(a, 0.08) - out * 0.15
        pts = [root, root + out * 0.4 + Vector((0, 0, 0.5)), root + out * 0.75 + Vector((0, 0, 1.6)),
               root + out * 1.0 + Vector((0, 0, 2.7)), root + out * 1.1 + Vector((0, 0, 3.6))]
        rt = rng.uniform(0.14, 0.22)
        for s in range(len(pts) - 1):
            b.tube(pts[s], pts[s + 1], rt * (1.0 - 0.15 * s), S["Bark"], segments=8, r_end=rt * (1.0 - 0.15 * (s + 1)))
        crown = pts[-1]
        for _ in range(7):
            q = crown + Vector((rng.uniform(-1.1, 1.1), rng.uniform(-1.1, 1.1), rng.uniform(-0.3, 0.8)))
            q = q if q.z > zt + 2.4 else Vector((q.x, q.y, zt + 2.4))
            r = rng.uniform(0.7, 1.15)
            b.blob((q.x, q.y, q.z), (r, r, r * 0.75), S["Leaf"], rng.randrange(1 << 30), 0.22, 2)
        # a few blossoms in the crown
        for _ in range(10):
            q = crown + Vector((rng.uniform(-1.4, 1.4), rng.uniform(-1.4, 1.4), rng.uniform(-0.2, 1.0)))
            b.paint = rng.choice(FLOWERS[:3]) + (1.0,)
            b.blob((q.x, q.y, max(q.z, zt + 2.4)), (0.12, 0.12, 0.1), S["Blossom"], rng.randrange(1 << 30), 0.2, 1)
            b.paint = None
    # Flowers and tufts on the grass: a few cm high, walked through.
    area = math.pi * flat * flat
    for _ in range(int(area / 2.5)):
        a = rng.uniform(0.0, 2.0 * math.pi)
        d = flat * math.sqrt(rng.random())
        qx, qy = c0.x + math.cos(a) * d, c0.y + math.sin(a) * d
        if rng.random() < 0.5:
            colour = rng.choice(FLOWERS)
            for _ in range(rng.randint(3, 7)):
                fx, fy = qx + rng.uniform(-0.25, 0.25), qy + rng.uniform(-0.25, 0.25)
                b.paint = colour + (1.0,)
                b.blob((fx, fy, zt + 0.05), (0.04, 0.04, 0.025), S["Blossom"], rng.randrange(1 << 30), 0.3, 1)
                b.paint = None
                b.tube((fx, fy, zt - 0.01), (fx, fy, zt + 0.04), 0.006, S["Grass"], segments=4)
        else:
            for _ in range(rng.randint(3, 6)):
                fx, fy = qx + rng.uniform(-0.15, 0.15), qy + rng.uniform(-0.15, 0.15)
                b.tube((fx, fy, zt - 0.01), (fx + rng.uniform(-0.03, 0.03), fy + rng.uniform(-0.03, 0.03), zt + rng.uniform(0.08, 0.15)),
                       0.025, S["Grass"], segments=4, r_end=0.002)
    return "Island"


# ----------------------------------------------------------------------------------------------- temple stone
def gate_pillar(b, lo, hi, key):
    # A column inside the old box: square plinth, fluted shaft, gold necking, square capital; ivy up one side.
    rng = b.begin(key, hi.z, hi.z - lo.z)
    cx, cy = (lo.x + hi.x) / 2.0, (lo.y + hi.y) / 2.0
    half = min(hi.x - lo.x, hi.y - lo.y) / 2.0
    b.box(Vector((cx - half, cy - half, lo.z)), Vector((cx + half, cy + half, lo.z + 0.3)), S["Marble"])
    b.box(Vector((cx - half * 0.85, cy - half * 0.85, lo.z + 0.3)), Vector((cx + half * 0.85, cy + half * 0.85, lo.z + 0.42)), S["Marble"])
    r = half * 0.72
    b.tube((cx, cy, lo.z + 0.42), (cx, cy, hi.z - 0.3), r, S["Marble"], flutes=12)
    b.tube((cx, cy, hi.z - 0.36), (cx, cy, hi.z - 0.3), r * 1.08, S["Gold"], segments=20)
    b.tube((cx, cy, hi.z - 0.3), (cx, cy, hi.z - 0.16), r, S["Marble"], segments=20, r_end=half * 0.95)
    b.box(Vector((cx - half, cy - half, hi.z - 0.16)), Vector((cx + half, cy + half, hi.z)), S["Marble"])
    ivy(b, cx, cy, lo.z, hi.z, r + 0.02, rng)
    return "Old Gate"


def ivy(b, cx, cy, z0, z1, r, rng):
    a = rng.uniform(0.0, 2.0 * math.pi)
    z = z0
    prev = None
    while z < z0 + (z1 - z0) * rng.uniform(0.5, 0.9):
        a += rng.uniform(0.25, 0.5)
        q = Vector((cx + math.cos(a) * r, cy + math.sin(a) * r, z))
        if prev is not None:
            b.tube(prev, q, 0.015, S["Bark"], segments=4)
        b.blob((q.x + math.cos(a) * 0.04, q.y + math.sin(a) * 0.04, q.z), (0.12, 0.12, 0.1), S["Leaf"], rng.randrange(1 << 30), 0.3, 1)
        if rng.random() < 0.3:
            b.paint = rng.choice(FLOWERS) + (1.0,)
            b.blob((q.x + math.cos(a) * 0.12, q.y + math.sin(a) * 0.12, q.z + 0.05), (0.05, 0.05, 0.04), S["Blossom"], rng.randrange(1 << 30), 0.2, 1)
            b.paint = None
        prev = q
        z += rng.uniform(0.18, 0.3)


def lintel(b, lo, hi, key):
    # The beam over the gate: architrave in two fasciae, a gold band, a cornice; vines hanging off it.
    rng = b.begin(key, hi.z, hi.z - lo.z)
    h = hi.z - lo.z
    d = 0.04
    b.box(Vector((lo.x + d, lo.y, lo.z)), Vector((hi.x - d, hi.y, lo.z + h * 0.35)), S["Marble"])
    b.box(Vector((lo.x + d * 0.5, lo.y, lo.z + h * 0.35)), Vector((hi.x - d * 0.5, hi.y, lo.z + h * 0.62)), S["Marble"])
    b.box(Vector((lo.x + d * 0.3, lo.y + 0.01, lo.z + h * 0.62)), Vector((hi.x - d * 0.3, hi.y - 0.01, lo.z + h * 0.72)), S["Gold"])
    b.box(Vector((lo.x, lo.y, lo.z + h * 0.72)), Vector((hi.x, hi.y, hi.z)), S["Marble"])
    # vines hanging from the beam
    for _ in range(int((hi.y - lo.y) / 0.6)):
        y = rng.uniform(lo.y + 0.2, hi.y - 0.2)
        x = rng.choice((lo.x - 0.02, hi.x + 0.02))
        length = rng.uniform(0.4, 1.6)
        prev = Vector((x, y, lo.z + h * 0.7))
        for s in range(1, 5):
            q = Vector((x + rng.uniform(-0.02, 0.02), y + rng.uniform(-0.05, 0.05), lo.z + h * 0.7 - length * s / 4.0))
            b.tube(prev, q, 0.012, S["Bark"], segments=4)
            b.blob((q.x, q.y, q.z), (0.1, 0.1, 0.09), S["Leaf"], rng.randrange(1 << 30), 0.3, 1)
            prev = q
    return "Old Gate"


def marble_beam(b, lo, hi, key):
    # A piece of the old temple's entablature, flying on its own. The top is the box's top exactly, over the whole
    # footprint (cut into blocks with 1 cm joints along the long side); nothing reaches outside the footprint, so no
    # new ledges. Under the top course: an inset architrave with a gold band and a row of dentils; the ends broken
    # off underneath; ivy hanging from the sides and a few tufts in the joints.
    rng = b.begin(key, hi.z, hi.z - lo.z)
    long_x = (hi.x - lo.x) >= (hi.y - lo.y)
    length = (hi.x - lo.x) if long_x else (hi.y - lo.y)
    width = (hi.y - lo.y) if long_x else (hi.x - lo.x)
    h = hi.z - lo.z

    def rect(a0, a1, w0, w1, z0, z1, slot):
        # a box in the beam's own frame: a along its length (from lo), w across it (from lo)
        if long_x:
            b.box(Vector((lo.x + a0, lo.y + w0, z0)), Vector((lo.x + a1, lo.y + w1, z1)), slot)
        else:
            b.box(Vector((lo.x + w0, lo.y + a0, z0)), Vector((lo.x + w1, lo.y + a1, z1)), slot)

    def point(a, w, z):
        return Vector((lo.x + a, lo.y + w, z)) if long_x else Vector((lo.x + w, lo.y + a, z))

    course = min(0.3, h * 0.45)
    blocks = max(1, int(round(length / rng.uniform(1.1, 1.6))))
    for k in range(blocks):
        a0, a1 = length * k / blocks, length * (k + 1) / blocks
        rect(a0 + (0.005 if k else 0.0), a1 - (0.005 if k < blocks - 1 else 0.0), 0.0, width, hi.z - course, hi.z, S["Marble"])
    inset = min(0.06, width * 0.08)
    body = hi.z - course
    # architrave, gold band, dentils
    rect(0.04, length - 0.04, inset, width - inset, lo.z, body, S["Marble"])
    rect(0.05, length - 0.05, inset - 0.012, width - inset + 0.012, body - 0.07, body - 0.03, S["Gold"])
    teeth = int((length - 0.2) / 0.16)
    for k in range(teeth):
        a = 0.1 + k * (length - 0.2) / max(teeth, 1)
        for w0, w1 in ((inset - 0.035, inset), (width - inset, width - inset + 0.035)):
            rect(a, a + 0.08, w0, w1, body - 0.03 - 0.07 - 0.08, body - 0.1, S["Marble"])
    # broken ends: the underside hangs on in ragged chunks below the beam
    for end in (0.0, length):
        for _ in range(rng.randint(1, 3)):
            s = rng.uniform(0.15, 0.3) * min(width, 0.8)
            a = end + (s if end == 0.0 else -s) * rng.uniform(1.0, 2.5)
            w = rng.uniform(inset + s, width - inset - s) if width - 2 * (inset + s) > 0 else width / 2.0
            q = point(a, w, lo.z - s * 0.6)
            b.box(q - Vector((s, s, s)), q + Vector((s, s, s * 0.6)), S["Marble"], rng.uniform(-0.5, 0.5), q)
    # ivy hanging from the sides
    for _ in range(int(length / 0.9)):
        a = rng.uniform(0.2, length - 0.2)
        w = rng.choice((inset - 0.04, width - inset + 0.04))
        hang = rng.uniform(0.3, 1.2)
        prev = point(a, w, body - 0.02)
        for s in range(1, 5):
            q = point(a + rng.uniform(-0.04, 0.04), w, body - 0.02 - hang * s / 4.0)
            b.tube(prev, q, 0.01, S["Bark"], segments=4)
            b.blob((q.x, q.y, q.z), (0.09, 0.09, 0.08), S["Leaf"], rng.randrange(1 << 30), 0.3, 1)
            prev = q
        if rng.random() < 0.35:
            b.paint = rng.choice(FLOWERS) + (1.0,)
            b.blob((prev.x, prev.y, prev.z - 0.06), (0.05, 0.05, 0.04), S["Blossom"], rng.randrange(1 << 30), 0.2, 1)
            b.paint = None
    # tufts and a flower or two in the joints on top (a few cm, walked through)
    for k in range(1, blocks):
        a = length * k / blocks
        for _ in range(rng.randint(1, 3)):
            q = point(a + rng.uniform(-0.03, 0.03), rng.uniform(0.1, width - 0.1), hi.z)
            b.tube((q.x, q.y, q.z - 0.01), (q.x, q.y, q.z + rng.uniform(0.06, 0.12)), 0.02, S["Grass"], segments=4, r_end=0.002)
    return "Marble"


def great_column(b, x, y, top, r, key):
    # The summit column: drums of fluted marble from the mist up, ivy winding round it, and a capital whose top is
    # the old gold disc's (r + 40 cm, flat at the top: the gate stands on it). Everything stays inside the old
    # cylinder (r) below the capital, and inside the disc's radius at it.
    c = bl(x, y, top)
    R, cap = r / 100.0, (r + 40.0) / 100.0
    zt, z0 = c.z, MIST / 100.0
    rng = b.begin(key, zt, zt - z0)
    neck = zt - 1.0
    z = z0
    while z < neck - 0.05:
        z1 = min(neck, z + rng.uniform(1.8, 2.4))
        b.tube((c.x, c.y, z), (c.x, c.y, z1 - 0.012), R, S["Marble"], flutes=24)
        z = z1
    b.tube((c.x, c.y, neck - 0.05), (c.x, c.y, neck + 0.12), R * 1.0, S["Gold"], segments=48)
    # echinus swelling out to the disc, an abacus slab, then the flat top with a gold rim (one lathe, no z-fight)
    b.tube((c.x, c.y, neck + 0.12), (c.x, c.y, zt - 0.45), R * 0.96, S["Marble"], segments=48, r_end=cap)
    b.tube((c.x, c.y, zt - 0.45), (c.x, c.y, zt - 0.06), cap, S["Marble"], segments=48)
    new = bmesh.new()
    n = 64
    centre = new.verts.new((c.x, c.y, zt))
    rings = []
    for rr, zz in ((cap * 0.55, zt), (cap * 0.86, zt), (cap * 0.9, zt), (cap, zt), (cap, zt - 0.06)):
        rings.append([new.verts.new((c.x + math.cos(2 * math.pi * i / n) * rr, c.y + math.sin(2 * math.pi * i / n) * rr, zz)) for i in range(n)])
    slots = [S["Marble"], S["Marble"], S["Gold"], S["Gold"], S["Gold"]]
    for i in range(n):
        new.faces.new((centre, rings[0][i], rings[0][(i + 1) % n])).material_index = S["Marble"]
    for k in range(len(rings) - 1):
        for i in range(n):
            j = (i + 1) % n
            new.faces.new((rings[k][i], rings[k + 1][i], rings[k + 1][j], rings[k][j])).material_index = slots[k + 1]
    bottom = new.faces.new(list(reversed(rings[-1])))
    bottom.material_index = S["Marble"]
    bmesh.ops.recalc_face_normals(new, faces=new.faces)
    b.add(new)
    # ivy winding up from the mist, thinning out towards the top; flowers here and there
    for strand in range(3):
        a = rng.uniform(0.0, 2.0 * math.pi)
        z = z0 + rng.uniform(0.0, 4.0)
        prev = None
        while z < neck - 1.0 - strand * 3.0:
            a += rng.uniform(0.08, 0.16)
            q = Vector((c.x + math.cos(a) * (R + 0.01), c.y + math.sin(a) * (R + 0.01), z))
            if prev is not None:
                b.tube(prev, q, 0.03, S["Bark"], segments=4)
            leaf = Vector((c.x + math.cos(a) * (R - 0.05), c.y + math.sin(a) * (R - 0.05), z))
            b.blob((leaf.x, leaf.y, leaf.z), (0.22, 0.22, 0.18), S["Leaf"], rng.randrange(1 << 30), 0.3, 1)
            if rng.random() < 0.15:
                b.paint = rng.choice(FLOWERS) + (1.0,)
                b.blob((c.x + math.cos(a) * (R + 0.02), c.y + math.sin(a) * (R + 0.02), z + 0.1), (0.08, 0.08, 0.06), S["Blossom"], rng.randrange(1 << 30), 0.2, 1)
                b.paint = None
            prev = q
            z += rng.uniform(0.25, 0.4)
    return "Column"


def heaven_gate(b, x, y, top, key):
    # The way to area 4: the two pillars and the lintel as in build_area3_sky.py, dressed as a temple gate, and a
    # pediment above with a gold sun (no collision: nothing there to stand on).
    for side in (-1, 1):
        gate_pillar(b, bl(x - 60.0, y + side * 250.0 + 60.0, top), bl(x + 60.0, y + side * 250.0 - 60.0, top + 700.0), key + str(side))
    lintel(b, bl(x - 80.0, y + 340.0, top + 700.0), bl(x + 80.0, y - 340.0, top + 800.0), key + "L")
    rng = b.begin(key + "P", (top + 1100.0) / 100.0, 3.0)
    c = bl(x, y, top + 800.0)
    new = bmesh.new()
    half, rise, depth = 3.4, 1.5, 0.7
    front, back = [], []
    for dx in (-depth / 2.0, depth / 2.0):
        tri = [new.verts.new((c.x + dx, c.y - half, c.z)), new.verts.new((c.x + dx, c.y + half, c.z)), new.verts.new((c.x + dx, c.y, c.z + rise))]
        (front if dx < 0 else back).append(tri)
    f, k = front[0], back[0]
    new.faces.new(f)
    new.faces.new(list(reversed(k)))
    for i in range(3):
        j = (i + 1) % 3
        new.faces.new((f[i], k[i], k[j], f[j]))
    bmesh.ops.recalc_face_normals(new, faces=new.faces)
    b.add(new, S["Marble"])
    # cornice along the sloping sides
    for sy in (-1, 1):
        b.tube((c.x, c.y + sy * (half + 0.1), c.z + 0.02), (c.x, c.y, c.z + rise + 0.12), 0.1, S["Gold"], segments=6)
    # the gold sun on both faces
    for dx in (-depth / 2.0 - 0.03, depth / 2.0):
        b.tube((c.x + dx, c.y, c.z + rise * 0.42), (c.x + dx + 0.03, c.y, c.z + rise * 0.42), 0.38, S["Gold"], segments=24)
        for i in range(12):
            a = 2.0 * math.pi * i / 12
            q0 = Vector((c.x + dx, c.y + math.cos(a) * 0.45, c.z + rise * 0.42 + math.sin(a) * 0.45))
            q1 = Vector((c.x + dx, c.y + math.cos(a) * 0.62, c.z + rise * 0.42 + math.sin(a) * 0.62))
            if q1.z < c.z + rise * (1.0 - abs(q1.y - c.y) / half) - 0.08 and q1.z > c.z + 0.05:
                b.tube(q0, q1, 0.035, S["Gold"], segments=5)
    return "Gate"


FOOTHOLDS = ("island", "cloud", "vanish", "mover", "timed", "falling", "marble", "stair")


def neighbours(route, piece):
    # Directions (Blender frame: Y flipped) from an island to the footholds near it at about its height.
    _, x, y, top, size = piece
    out = []
    for other in route.pieces:
        if other is piece or other[0] not in FOOTHOLDS:
            continue
        if other[0] == "marble":
            ox, oy, otop = (other[1] + other[2]) / 2.0, (other[3] + other[4]) / 2.0, other[5]
        else:
            ox, oy, otop = other[1], other[2], other[3]
        if math.hypot(ox - x, oy - y) < size / 2.0 + 1300.0 and abs(otop - top) < 600.0:
            out.append(math.atan2(-(oy - y), ox - x))
        if other[0] == "mover":                      # where a mover's ride ends, too
            ex, ey = ox + other[4][0], oy + other[4][1]
            if math.hypot(ex - x, ey - y) < size / 2.0 + 1300.0:
                out.append(math.atan2(-(ey - y), ex - x))
    return out


def dress(b, piece, index, route=None):
    kind = piece[0]
    key = "{}:{}".format(index, kind)
    if kind == "island":
        _, x, y, top, size = piece
        return island(b, x, y, top, size, key, neighbours(route, piece) if route else ())
    if kind == "deco":
        _, x0, x1, y0, y1, z0, z1 = piece
        lo, hi = bl(x0, y1, z0), bl(x1, y0, z1)          # (Y flips: y1 becomes the low side)
        if z1 - z0 > 2.0 * (x1 - x0):
            return gate_pillar(b, lo, hi, key)
        return lintel(b, lo, hi, key)
    if kind == "marble":
        _, x0, x1, y0, y1, top, thick = piece
        return marble_beam(b, bl(x0, y1, top - thick), bl(x1, y0, top), key)
    if kind == "column":
        _, x, y, top, r = piece
        return great_column(b, x, y, top, r, key)
    if kind == "gate":
        _, x, y, top = piece
        return heaven_gate(b, x, y, top, key)
    return None


# ===================================================================================================== output
def preview(obj, out, eye, look):
    for slot in SLOTS:
        mat = bpy.data.materials["M_SkyArt" + slot]
        mat.use_nodes = True
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        bsdf = nodes.get("Principled BSDF")
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(os.path.join(TEX_DIR, "T_SkyArt" + slot + "_C.png"))
        vcol = nodes.new("ShaderNodeVertexColor")
        vcol.layer_name = "Col"
        mix = nodes.new("ShaderNodeVectorMath")
        mix.operation = "MULTIPLY"
        links.new(tex.outputs["Color"], mix.inputs[0])
        links.new(vcol.outputs["Color"], mix.inputs[1])
        links.new(mix.outputs[0], bsdf.inputs["Base Color"])
        normal_path = os.path.join(TEX_DIR, "T_SkyArt" + slot + "_N.png")
        if os.path.exists(normal_path):
            ntex = nodes.new("ShaderNodeTexImage")
            ntex.image = bpy.data.images.load(normal_path)
            ntex.image.colorspace_settings.name = "Non-Color"
            nmap = nodes.new("ShaderNodeNormalMap")
            links.new(ntex.outputs["Color"], nmap.inputs["Color"])
            links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
        rough, metal = {"Marble": (0.35, 0.0), "Gold": (0.25, 1.0), "Water": (0.1, 0.0)}.get(slot, (0.9, 0.0))
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
        if slot == "Water":
            bsdf.inputs["Emission Color"].default_value = (0.7, 0.9, 1.0, 1.0)
            bsdf.inputs["Emission Strength"].default_value = 0.5
    scene = bpy.context.scene
    world = bpy.data.worlds.new("Day")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.5, 0.7, 1.0, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
    scene.world = world
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 4.0
    sun.data.color = (1.0, 0.96, 0.9)
    sun.rotation_euler = (math.radians(40), 0.0, math.radians(-130))
    scene.collection.objects.link(sun)
    cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    cam.data.lens = 20.0
    cam.data.clip_end = 1000.0
    cam.location = bl(*eye)
    cam.rotation_euler = (bl(*look) - bl(*eye)).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(cam)
    scene.camera = cam
    for engine in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue
    scene.view_settings.view_transform = "Standard"
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.filepath = out
    bpy.ops.render.render(write_still=True)


def export(obj, name):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT_DIR, name + ".fbx"), use_selection=True, apply_unit_scale=True,
                             mesh_smooth_type="FACE", use_mesh_modifiers=False)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    make_textures()
    route = area3_layout.build(B, 500.9, 980.0, 600.0, 300.0)
    report = []
    built = []
    section = ""
    by_section = {}
    for index, piece in enumerate(route.pieces):
        if piece[0] == "section":
            section = piece[1][0]
            continue
        by_section.setdefault(section, []).append((index, piece))
    for letter in SECTIONS:
        builder = Builder()
        kinds = {}
        for index, piece in by_section.get(letter, []):
            name = dress(builder, piece, index, route)
            if name:
                kinds[name] = kinds.get(name, 0) + 1
        name = "SM_Sky_" + letter
        obj = builder.finish(name)
        built.append(obj)
        export(obj, name)
        with open(os.path.join(OUT_DIR, "sky_art_" + letter + ".json"), "w", encoding="utf-8") as out:
            labels = {"Column": ["Column", "Column Top"], "Gate": ["Gate Pillar", "Gate Lintel"]}   # build_area3_sky.py's names
            json.dump({"replaces": sorted(l for k in kinds for l in labels.get(k, [k]))}, out)
        report.append("{}: {} ({}), {} vertices".format(name, sum(kinds.values()), ", ".join("{} {}".format(k, v) for k, v in sorted(kinds.items())),
                                                        len(obj.data.vertices)))
    with open(os.path.join(OUT_DIR, "sky_art_build.txt"), "w", encoding="utf-8") as out:
        out.write("\n".join(report) + "\n")
    print("\n".join(report))
    if PREVIEW:
        preview(built[0], *PREVIEW)


main()
