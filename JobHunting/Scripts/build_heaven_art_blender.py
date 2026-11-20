# Builds area 4's "palace of heaven" art in Blender, straight from area4_layout.py (no Unreal needed): white pearl
# marble and gold, a meander of light channels cut round every slab (dim and broken in places: heaven has lost its
# light), undersides stepping down to a hanging crystal. Static pieces only (blocks, islands); gimmicks are left alone.
#   SourceArt/Models/Heaven/Art/SM_Heaven_<section number>.fbx   one mesh per section, world positioned
#                                                                slots: Pearl Gold Channel Stone Crystal Dark
#                                                                (named M_HeavenArt<Slot>)
#   SourceArt/Models/Heaven/Art/heaven_art_<number>.json         the actor names the mesh replaces (import_heaven_art.py
#                                                                hides those; they stay as the collision)
#   SourceArt/Models/Heaven/Art/Textures/T_HeavenArt<Slot>_C/_N/_E.png
# What the player stands on stays where the collision is: a block's top is its box's top over the whole footprint,
# nothing sticks out sideways at a walkable height, and an island's top is flat over its collision circle (0.48 x
# size); posts on an island's rim stand outside the circle and turn away from the route.
# A UE point (x, y, z) cm is put at (x, -y, z) / 100 m here (the FBX import flips Y back).
#   blender --background --factory-startup --python build_heaven_art_blender.py -- 1 [2 ...] [--preview out.png cx,cy,cz lx,ly,lz]
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
import area4_layout  # noqa: E402

OUT_DIR = os.path.join(os.path.dirname(HERE), "SourceArt", "Models", "Heaven", "Art")
TEX_DIR = os.path.join(OUT_DIR, "Textures")
SLOTS = ["Pearl", "Gold", "Channel", "Stone", "Crystal", "Dark", "DarkBand"]
S = {name: i for i, name in enumerate(SLOTS)}
BANDS = (S["Channel"], S["DarkBand"])
LEVELS = []   # the dark tower's storey heights (m): its walls get a frieze at each
TEX = 1024
TILE = 2.0
B = 22610.0

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
PREVIEW = None
if "--preview" in args:
    i = args.index("--preview")
    PREVIEW = (args[i + 1], [float(v) for v in args[i + 2].split(",")], [float(v) for v in args[i + 3].split(",")])
    args = args[:i] + args[i + 4:]
SECTIONS = args or ["1"]


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
    write_png("T_HeavenArt" + name + "_C", rgb)
    if height is not None:
        write_png("T_HeavenArt" + name + "_N", normal_from(height, strength))
    if mask is not None:
        write_png("T_HeavenArt" + name + "_E", np.dstack([mask] * 3))


def tint(base, amount):
    return np.dstack([base[i] * amount for i in range(3)])


def meander(cells=4):
    # One row of a Greek key, `cells` keys across, filling the texture's height (the band's UVs run 0..1 up it).
    size = TEX // cells
    unit = size / 10.0
    cell = np.zeros((size, size))
    yy, xx = np.mgrid[0:size, 0:size] / unit         # grid units, y down from the top row

    def line(a, b, w=0.85):
        (x0, y0), (x1, y1) = a, b
        lo_x, hi_x, lo_y, hi_y = min(x0, x1) - w / 2, max(x0, x1) + w / 2, min(y0, y1) - w / 2, max(y0, y1) + w / 2
        cell[(xx >= lo_x) & (xx <= hi_x) & (yy >= lo_y) & (yy <= hi_y)] = 1.0

    line((0, 1), (10, 1))                             # the borders
    line((0, 9), (10, 9))
    path = [(1.5, 9), (1.5, 3), (8, 3), (8, 7), (4, 7), (4, 5), (6, 5)]
    for a, b in zip(path, path[1:]):
        line(a, b)
    row = np.tile(cell, (1, cells))
    return np.repeat(row, cells, axis=0)[:TEX, :TEX]


def make_textures():
    os.makedirs(TEX_DIR, exist_ok=True)
    fine = noise(TEX, 2, 1)
    # Pearl: white marble with a faint pearly shimmer (pink / blue clouds) and fine grey veins.
    clouds = fbm(TEX, 11, (220, 90, 30, 10))
    pink, blue = noise(TEX, 90, 12), noise(TEX, 110, 13)
    veins = np.clip(1.0 - np.abs(fbm(TEX, 14, (120, 50, 16, 5)) - 0.5) * 80.0, 0.0, 1.0) * 0.5
    base = np.dstack([0.95 + 0.03 * pink, 0.94 + 0.01 * clouds, 0.92 + 0.04 * blue]) * (0.96 + 0.04 * clouds[..., None])
    colour = base * (1.0 - 0.25 * veins[..., None])
    save("Pearl", colour, clouds * 0.05 - veins * 0.05 + fine * 0.01, 2.0)
    # Gold.
    save("Gold", tint(np.array([0.98, 0.78, 0.38]), 0.9 + 0.12 * noise(TEX, 8, 21)), noise(TEX, 8, 21) * 0.1, 1.0)
    # Channel: pearl with the Greek key cut in; the cut glows - unevenly, faded and broken in places (mask).
    key = meander()
    fade = np.clip(fbm(TEX, 31, (200, 80, 30, 10)) * 1.6 - 0.25, 0.08, 1.0)
    colour = base * (1.0 - key[..., None]) + tint(np.array([0.95, 0.8, 0.5]), 0.9 + 0.1 * fine) * key[..., None]
    save("Channel", colour, clouds * 0.05 - key * 0.6, 4.0, key * fade)
    # Stone: the warm pale stone of the foundations, soft courses, with thin veins of gold (glowing faintly).
    v = (np.mgrid[0:TEX, 0:TEX][0] / TEX + 0.04 * noise(TEX, 40, 41)) * 5.0
    seam = np.clip(np.abs(v - np.round(v)) * 25.0, 0.0, 1.0)
    grain = fbm(TEX, 42, (200, 90, 40, 20))
    gold_vein = np.clip(1.0 - np.abs(noise(TEX, 160, 43) - 0.5) * 160.0, 0.0, 1.0)
    gold_vein *= np.clip((noise(TEX, 120, 44) - 0.5) * 6.0, 0.0, 1.0)      # only here and there
    colour = tint(np.array([0.9, 0.85, 0.76]), (0.9 + 0.12 * grain) * (0.8 + 0.2 * seam))
    colour = colour * (1.0 - gold_vein[..., None]) + tint(np.array([0.95, 0.75, 0.35]), np.ones((TEX, TEX))) * gold_vein[..., None]
    save("Stone", colour, seam * 0.4 + grain * 0.3 - gold_vein * 0.3, 4.0, gold_vein)
    # Crystal: glows all over (mask), a little cloudy.
    save("Crystal", tint(np.array([0.95, 0.93, 0.85]), 0.85 + 0.15 * noise(TEX, 20, 51)), None, mask=0.7 + 0.3 * noise(TEX, 20, 51))
    # Dark: the dark tower's stone - blue-grey ashlar in 0.5 m courses, joints staggered, each block a shade apart.
    yy, xx = np.mgrid[0:TEX, 0:TEX]
    course, length = TEX // 4, TEX // 2
    row = yy // course
    shifted = xx + (row % 2) * (length // 2)
    tones = 0.82 + 0.3 * np.random.default_rng(62).random(8)
    tone = tones[(row % 4) * 2 + (shifted // length) % 2]
    jy = np.minimum(yy % course, course - yy % course)
    jx = np.minimum(shifted % length, length - shifted % length)
    joint = np.clip(np.minimum(jx, jy) / 4.0, 0.0, 1.0)              # 0 in a joint
    grain = fbm(TEX, 61)
    dark = np.array([0.2, 0.21, 0.27])
    save("Dark", tint(dark, tone * (0.85 + 0.3 * grain) * (0.45 + 0.55 * joint)), joint * 0.5 + grain * 0.2, 4.0)
    # DarkBand: the tower's meander - tarnished gold in dark stone, its light gone out but for a glimmer here and there.
    out_light = np.clip(fbm(TEX, 71, (200, 80, 30, 10)) * 1.8 - 0.55, 0.0, 1.0)
    colour = tint(dark, 0.85 + 0.3 * grain) * (1.0 - key[..., None]) + tint(np.array([0.55, 0.42, 0.22]), 0.9 + 0.1 * fine) * key[..., None]
    save("DarkBand", colour, grain * 0.1 - key * 0.5, 4.0, key * out_light)
    write_png("T_HeavenArtBlack_E", np.zeros((64, 64, 3)))


# ===================================================================================================== meshes
def bl(x, y, z):
    return Vector((x / 100.0, -y / 100.0, z / 100.0))


def wash(c):
    s = math.sin(c.x * 0.9 + c.y * 0.4 + 1.3) * math.sin(c.z * 1.1 - c.x * 0.3 + 0.7)
    return 0.95 + 0.05 * s


class Builder:
    # One bmesh per section, in Blender metres; vertex colour "Col" (multiplied in UE): a faint wash on stone and
    # pearl, a tone per piece, the underside's stone darkening towards its tip.
    def __init__(self):
        self.bm = bmesh.new()
        self.top, self.depth = 0.0, 1.0
        self.uv = (0.0, 0.0)
        self.tone = (1.0, 1.0, 1.0)

    def begin(self, key, top, depth):
        rng = random.Random(zlib.crc32(key.encode("utf-8")))
        self.top, self.depth = top, max(depth, 0.5)
        self.uv = (rng.random(), rng.random())
        self.tone = rng.choice([(1.0, 1.0, 1.0), (1.0, 0.98, 0.95), (0.97, 0.98, 1.0)])
        self.dim = 1.0          # < 1: the dark tower's tarnished gold and grimy marble
        return rng

    def shade(self, slot, c):
        if slot in (S["Crystal"],) + BANDS:
            return (1.0, 1.0, 1.0, 1.0)
        if slot == S["Gold"]:
            return (self.dim, self.dim, self.dim, 1.0)
        f = wash(c) * (self.dim if slot == S["Pearl"] else 1.0)
        if slot == S["Stone"]:
            t = min(1.0, max(0.0, (self.top - c.z) / self.depth))
            f *= 1.0 - 0.3 * t
        return tuple(min(1.0, v * f) for v in self.tone) + (1.0,)

    def add(self, new, slot=None, band=None):
        # band: (z0, z1, step) - side faces of a Channel band get V 0..1 up the band and U along it (one key per
        # band height), so the Greek key always fills the band exactly.
        uv = new.loops.layers.uv.new("UVMap")
        col = new.loops.layers.color.new("Col")
        ou, ov = self.uv
        for face in new.faces:
            if slot is not None:
                face.material_index = slot
            n = face.normal
            for loop in face.loops:
                c = loop.vert.co
                if band and face.material_index in BANDS and abs(n.z) < 0.7:
                    z0, z1 = band
                    along = c.y if abs(n.x) > abs(n.y) else c.x
                    loop[uv].uv = (along / (4.0 * (z1 - z0)), (c.z - z0) / (z1 - z0))
                elif abs(n.z) > 0.7:
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

    def box(self, lo, hi, slot, band=False):
        if hi.x - lo.x < 1e-4 or hi.y - lo.y < 1e-4 or hi.z - lo.z < 1e-4:
            return
        new = bmesh.new()
        bmesh.ops.create_cube(new, size=1.0)
        for v in new.verts:
            v.co = Vector((lo.x if v.co.x < 0 else hi.x, lo.y if v.co.y < 0 else hi.y, lo.z if v.co.z < 0 else hi.z))
        new.normal_update()
        self.add(new, slot, (lo.z, hi.z) if band else None)

    def tube(self, a, b, r, slot, segments=12, r_end=None, flutes=0, turn=0.0):
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
            ang = 2.0 * math.pi * i / n + turn
            k = (0.92 if i % 2 else 1.0) if flutes else 1.0
            ring = u * math.cos(ang) + w * math.sin(ang)
            lo.append(new.verts.new(a + ring * r * k))
            hi.append(new.verts.new(b + ring * (r if r_end is None else r_end) * k))
        for i in range(n):
            new.faces.new((lo[i], lo[(i + 1) % n], hi[(i + 1) % n], hi[i]))
        new.faces.new(list(reversed(lo)))
        new.faces.new(hi)
        bmesh.ops.recalc_face_normals(new, faces=new.faces)
        self.add(new, slot)

    def blob(self, c, radii, slot, subdivisions=2):
        new = bmesh.new()
        bmesh.ops.create_icosphere(new, subdivisions=subdivisions, radius=1.0)
        for v in new.verts:
            v.co = Vector((c[0] + v.co.x * radii[0], c[1] + v.co.y * radii[1], c[2] + v.co.z * radii[2]))
        new.normal_update()
        self.add(new, slot)

    def lathe(self, cx, cy, profile, n=64, cap_top=None):
        # A round solid from a profile [(radius, z, slot of the faces from the previous point), ...] going down;
        # cap_top: slot of a fan closing the first ring (a flat top), and the last point (radius 0) closes the bottom.
        new = bmesh.new()
        rings = []
        for r, z, _ in profile:
            if r < 1e-4:
                rings.append([new.verts.new((cx, cy, z))])
            else:
                rings.append([new.verts.new((cx + math.cos(2 * math.pi * i / n) * r, cy + math.sin(2 * math.pi * i / n) * r, z)) for i in range(n)])
        if cap_top is not None and len(rings[0]) > 1:
            centre = new.verts.new((cx, cy, profile[0][1]))
            for i in range(n):
                new.faces.new((centre, rings[0][i], rings[0][(i + 1) % n])).material_index = cap_top
        for k in range(1, len(rings)):
            a, b_ = rings[k - 1], rings[k]
            for i in range(n):
                j = (i + 1) % n
                if len(a) == 1:
                    f = new.faces.new((a[0], b_[i], b_[j]))
                elif len(b_) == 1:
                    f = new.faces.new((a[i], b_[0], a[j]))
                else:
                    f = new.faces.new((a[i], b_[i], b_[j], a[j]))
                f.material_index = profile[k][2]
        bmesh.ops.recalc_face_normals(new, faces=new.faces)
        self.add(new)

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
            obj.data.materials.append(bpy.data.materials.get("M_HeavenArt" + slot) or bpy.data.materials.new("M_HeavenArt" + slot))
        for p in obj.data.polygons:
            p.use_smooth = p.material_index == S["Crystal"]
        return obj


# ----------------------------------------------------------------------------------------------- pieces
def inlaid_top(b, lo, hi, z, field, rim, margin=0.1, strip=0.05):
    # The walked-on top as one flat grid (no faces over each other): a margin of `field`, a strip of `rim`, the field.
    xs = [lo.x, lo.x + margin, lo.x + margin + strip, hi.x - margin - strip, hi.x - margin, hi.x]
    ys = [lo.y, lo.y + margin, lo.y + margin + strip, hi.y - margin - strip, hi.y - margin, hi.y]
    if xs[2] >= xs[3] or ys[2] >= ys[3]:
        xs, ys = [lo.x, hi.x], [lo.y, hi.y]
    new = bmesh.new()
    grid = [[new.verts.new((x, y, z)) for x in xs] for y in ys]
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            f = new.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
            ring = len(xs) == 6 and ((i in (1, 3) and 1 <= j <= 3) or (j in (1, 3) and 1 <= i <= 3))
            f.material_index = rim if ring else field
    new.normal_update()
    b.add(new)


def corbel(b, lo, hi, z, rng, max_depth=2.2):
    # Under a slab: a gold-edged step, then an inverted pyramid down to a hanging crystal - all inside the footprint.
    w, d = hi.x - lo.x, hi.y - lo.y
    c = Vector(((lo.x + hi.x) / 2.0, (lo.y + hi.y) / 2.0, z))
    s1 = 0.12 * min(w, d)
    b.box(Vector((lo.x + s1, lo.y + s1, z - 0.12)), Vector((hi.x - s1, hi.y - s1, z)), S["Pearl"])
    b.box(Vector((lo.x + s1 + 0.02, lo.y + s1 + 0.02, z - 0.17)), Vector((hi.x - s1 - 0.02, hi.y - s1 - 0.02, z - 0.12)), S["Gold"])
    half = (min(w, d) / 2.0 - s1 - 0.04) * math.sqrt(2.0)
    depth = min(max_depth, 0.8 * min(w, d) + 0.2)
    top = Vector((c.x, c.y, z - 0.17))
    b.tube(top, top - Vector((0.0, 0.0, depth)), half, S["Pearl"], segments=4, r_end=0.03, turn=math.pi / 4.0)
    tip = top - Vector((0.0, 0.0, depth))
    b.tube(tip + Vector((0.0, 0.0, 0.05)), tip - Vector((0.0, 0.0, 0.1)), 0.05, S["Gold"], segments=8)
    crystal(b, tip - Vector((0.0, 0.0, 0.1)), rng.uniform(0.05, 0.08) * max(1.0, min(w, d)))


def crystal(b, at, r):
    # A hanging crystal: a six-sided double point below `at`, the lower point twice as long.
    mid = at - Vector((0.0, 0.0, r * 1.2))
    b.tube(mid, at, r, S["Crystal"], segments=6, r_end=0.005)
    b.tube(mid, mid - Vector((0.0, 0.0, r * 2.6)), r, S["Crystal"], segments=6, r_end=0.005)


def flipped_slab(b, lo, hi, look, key):
    # A slab walked on upside down (its underside): built as a slab in a builder of its own, then mirrored about its
    # middle, so the inlaid face is the underside and the corbel (kept short: 1 m) points up. The meander turns
    # over with it - the right way up for someone standing on the ceiling.
    sub = Builder()
    slab(sub, lo, hi, look, key, corbel_max=1.0)
    mid = lo.z + hi.z
    for v in sub.bm.verts:
        v.co.z = mid - v.co.z
    bmesh.ops.reverse_faces(sub.bm, faces=list(sub.bm.faces))
    mesh = bpy.data.meshes.new("flipped")
    sub.bm.to_mesh(mesh)
    sub.bm.free()
    b.bm.from_mesh(mesh)
    bpy.data.meshes.remove(mesh)


def slab(b, lo, hi, look, key, corbel_max=2.2):
    # A floor, ledge or step: inlaid top exactly at the box's top; under it a moulded edge, the meander band, a
    # gold fillet - all inside the footprint - and the corbel below.
    rng = b.begin(key, hi.z, hi.z - lo.z)
    field, rim = {"gold": (S["Gold"], S["Pearl"]), "stone": (S["Stone"], S["Gold"])}.get(look, (S["Pearl"], S["Gold"]))
    h = hi.z - lo.z
    cap = min(0.1, h * 0.25)
    inlaid_top(b, lo, hi, hi.z, field, rim, margin=min(0.12, 0.08 * min(hi.x - lo.x, hi.y - lo.y)))
    b.box(Vector((lo.x, lo.y, hi.z - cap)), Vector((hi.x, hi.y, hi.z - 0.01)), S["Pearl"])
    inset = min(0.04, 0.05 * min(hi.x - lo.x, hi.y - lo.y))
    band0, band1 = lo.z + 0.03, hi.z - cap
    if band1 - band0 > 0.08:
        b.box(Vector((lo.x + inset, lo.y + inset, band0)), Vector((hi.x - inset, hi.y - inset, band1)), S["Channel"], band=True)
    b.box(Vector((lo.x + inset * 0.5, lo.y + inset * 0.5, lo.z)), Vector((hi.x - inset * 0.5, hi.y - inset * 0.5, band0)), S["Gold"])
    if corbel_max > 0.0:
        corbel(b, lo + Vector((inset, inset, 0.0)), hi - Vector((inset, inset, 0.0)), lo.z, rng, corbel_max)
    return True


# ----------------------------------------------------------------------------------------------- the dark tower
def dark_slab(b, lo, hi, key):
    # A floor or roof of the dark tower: dark stone inlaid with tarnished gold, the dark meander round its edge, a
    # flat underside (people walk and jump under these floors).
    b.begin(key, hi.z, hi.z - lo.z)
    b.dim = 0.5
    h = hi.z - lo.z
    cap = min(0.06, h * 0.25)
    inlaid_top(b, lo, hi, hi.z, S["Dark"], S["Gold"], margin=min(0.3, 0.1 * min(hi.x - lo.x, hi.y - lo.y)), strip=0.06)
    b.box(Vector((lo.x, lo.y, hi.z - cap)), Vector((hi.x, hi.y, hi.z - 0.01)), S["Dark"])
    inset = min(0.03, 0.05 * min(hi.x - lo.x, hi.y - lo.y))
    band0, band1 = lo.z + 0.03, hi.z - cap
    if band1 - band0 > 0.06:
        b.box(Vector((lo.x + inset, lo.y + inset, band0)), Vector((hi.x - inset, hi.y - inset, band1)), S["DarkBand"], band=True)
    edge_lo, edge_hi = Vector((lo.x + inset * 0.5, lo.y + inset * 0.5, 0.0)), Vector((hi.x - inset * 0.5, hi.y - inset * 0.5, 0.0))
    b.box(Vector((edge_lo.x, edge_lo.y, lo.z + 0.015)), Vector((edge_hi.x, edge_hi.y, band0)), S["Gold"])    # a gold fillet,
    b.box(Vector((edge_lo.x, edge_lo.y, lo.z)), Vector((edge_hi.x, edge_hi.y, lo.z + 0.015)), S["Dark"])    # a dark underside
    return True


def dark_wall(b, lo, hi, key, light=False):
    # A wall of the dark tower, flush with its box: dark ashlar between grimy marble pilasters (every 8 m, on one
    # grid for all the walls), a plinth, a frieze of the dark meander at every storey and a cornice under the roof;
    # a wall that starts high (over the door) gets a gold lintel and a crystal keystone.
    # light: the palace wall out in the open (the roof's parapets, the Iwato corridor) - pearl between pilasters of
    # gold-veined stone, a stone plinth, the glowing meander as a frieze over head height and as the cornice, and a
    # cresting of gold knobs along the top.
    if light:
        return light_wall(b, lo, hi, key)
    b.begin(key, hi.z, hi.z - lo.z)
    b.dim = 0.4
    along_x = hi.x - lo.x >= hi.y - lo.y
    a0, a1 = (lo.x, hi.x) if along_x else (lo.y, hi.y)
    cuts = [a0]
    k = math.ceil((a0 + 0.8) / 8.0)
    while k * 8.0 + 0.6 < a1 - 0.2:
        cuts += [k * 8.0 - 0.6, k * 8.0 + 0.6]
        k += 1
    cuts.append(a1)
    columns = [(cuts[i], cuts[i + 1], i % 2 == 1) for i in range(len(cuts) - 1)]
    base = min(LEVELS) if LEVELS else lo.z
    rows = []
    if lo.z < base + 0.01:
        rows.append((lo.z, base + 0.5, "plinth"))
        rows.append((base + 0.5, base + 0.55, "gold"))
    else:
        rows.append((lo.z, lo.z + 0.2, "gold"))                    # the lintel over the door
    for level in LEVELS:
        if level > base + 0.01:
            rows += [(level, level + 0.05, "gold"), (level + 0.05, level + 0.45, "band"), (level + 0.45, level + 0.48, "gold")]
    if hi.z - lo.z > 3.0:
        rows += [(hi.z - 0.55, hi.z - 0.52, "gold"), (hi.z - 0.52, hi.z - 0.08, "band"), (hi.z - 0.08, hi.z, "gold")]
    clipped = []
    for z0, z1, kind in sorted(rows):
        z0, z1 = max(z0, lo.z, clipped[-1][1] if clipped else lo.z), min(z1, hi.z)
        if z1 - z0 > 1e-3:
            clipped.append((z0, z1, kind))
    filled, z = [], lo.z
    for z0, z1, kind in clipped:
        if z0 - z > 1e-3:
            filled.append((z, z0, "body"))
        filled.append((z0, z1, kind))
        z = z1
    if hi.z - z > 1e-3:
        filled.append((z, hi.z, "body"))
    for z0, z1, kind in filled:
        if kind == "body":
            for c0, c1, pilaster in columns:
                cell_lo = Vector((c0, lo.y, z0)) if along_x else Vector((lo.x, c0, z0))
                cell_hi = Vector((c1, hi.y, z1)) if along_x else Vector((hi.x, c1, z1))
                b.box(cell_lo, cell_hi, S["Pearl"] if pilaster else S["Dark"])
            continue
        slot = {"plinth": S["Dark"], "gold": S["Gold"], "band": S["DarkBand"]}[kind]
        if kind == "plinth":
            b.tone = (0.75, 0.75, 0.78)
        b.box(Vector((lo.x, lo.y, z0)), Vector((hi.x, hi.y, z1)), slot, band=kind == "band")
        b.tone = (1.0, 1.0, 1.0)
    if lo.z > base + 0.01:
        mid = (a0 + a1) / 2.0
        at = Vector((mid, (lo.y + hi.y) / 2.0, lo.z)) if along_x else Vector(((lo.x + hi.x) / 2.0, mid, lo.z))
        b.tube(at, at - Vector((0.0, 0.0, 0.06)), 0.07, S["Gold"], segments=8)
        crystal(b, at - Vector((0.0, 0.0, 0.06)), 0.07)
    return True


def light_wall(b, lo, hi, key):
    b.begin(key, hi.z, hi.z - lo.z)
    along_x = hi.x - lo.x >= hi.y - lo.y
    a0, a1 = (lo.x, hi.x) if along_x else (lo.y, hi.y)
    cuts = [a0]
    k = math.ceil((a0 + 0.8) / 8.0)
    while k * 8.0 + 0.6 < a1 - 0.2:
        cuts += [k * 8.0 - 0.6, k * 8.0 + 0.6]
        k += 1
    cuts.append(a1)
    columns = [(cuts[i], cuts[i + 1], i % 2 == 1) for i in range(len(cuts) - 1)]
    rows = [(lo.z, lo.z + 0.6, "plinth"), (lo.z + 0.6, lo.z + 0.66, "gold")]
    if hi.z - lo.z > 5.0:
        f = lo.z + 3.0
        rows += [(f, f + 0.05, "gold"), (f + 0.05, f + 0.5, "band"), (f + 0.5, f + 0.55, "gold")]
    rows += [(hi.z - 0.65, hi.z - 0.6, "gold"), (hi.z - 0.6, hi.z - 0.1, "band"), (hi.z - 0.1, hi.z, "gold")]
    filled, z = [], lo.z
    for z0, z1, kind in rows:
        z0, z1 = max(z0, z), min(z1, hi.z)
        if z1 - z0 < 1e-3:
            continue
        if z0 - z > 1e-3:
            filled.append((z, z0, "body"))
        filled.append((z0, z1, kind))
        z = z1
    if hi.z - z > 1e-3:
        filled.append((z, hi.z, "body"))
    for z0, z1, kind in filled:
        if kind == "body":
            for c0, c1, pilaster in columns:
                cell_lo = Vector((c0, lo.y, z0)) if along_x else Vector((lo.x, c0, z0))
                cell_hi = Vector((c1, hi.y, z1)) if along_x else Vector((hi.x, c1, z1))
                b.box(cell_lo, cell_hi, S["Stone"] if pilaster else S["Pearl"])
            continue
        slot = {"plinth": S["Stone"], "gold": S["Gold"], "band": S["Channel"]}[kind]
        b.box(Vector((lo.x, lo.y, z0)), Vector((hi.x, hi.y, z1)), slot, band=kind == "band")
    # the cresting: a gold knob on a little pearl stem every 2 m along the top (out of reach, 14 m up)
    thick = min(hi.x - lo.x, hi.y - lo.y, 1.0)
    n = max(1, int((a1 - a0) / 2.0))
    for i in range(n):
        a = a0 + (i + 0.5) * (a1 - a0) / n
        p = Vector((a, (lo.y + hi.y) / 2.0, hi.z)) if along_x else Vector(((lo.x + hi.x) / 2.0, a, hi.z))
        b.tube(p, p + Vector((0.0, 0.0, 0.18)), thick * 0.25, S["Pearl"], segments=8, r_end=thick * 0.15)
        b.blob((p.x, p.y, p.z + 0.26), (thick * 0.22, thick * 0.22, thick * 0.26), S["Gold"], 1)
    return True


def gate_crown(b, lo, hi):
    # Heaven's Gate: a pearl pediment on the lintel (out of reach, 13 m up) with a gold sun on each face, a crystal
    # at its heart - the light the player brings back.
    t, h = hi.z, 0.18 * (hi.y - lo.y)
    my = (lo.y + hi.y) / 2.0
    new = bmesh.new()
    west = [new.verts.new((lo.x, lo.y, t)), new.verts.new((lo.x, hi.y, t)), new.verts.new((lo.x, my, t + h))]
    east = [new.verts.new((hi.x, lo.y, t)), new.verts.new((hi.x, hi.y, t)), new.verts.new((hi.x, my, t + h))]
    new.faces.new(west)
    new.faces.new(list(reversed(east)))
    for i in range(3):
        j = (i + 1) % 3
        new.faces.new((west[j], west[i], east[i], east[j]))
    bmesh.ops.recalc_face_normals(new, faces=new.faces)
    b.add(new, S["Pearl"])
    cz = t + h * 0.4
    for x, out in ((lo.x, -1.0), (hi.x, 1.0)):
        b.tube((x, my, cz), (x + out * 0.06, my, cz), h * 0.32, S["Gold"], segments=32)
        b.tube((x + out * 0.06, my, cz), (x + out * 0.1, my, cz), h * 0.15, S["Crystal"], segments=24)
        for k in range(12):
            a = 2.0 * math.pi * k / 12.0
            d = Vector((0.0, math.cos(a), math.sin(a)))
            p = Vector((x + out * 0.03, my, cz))
            b.tube(p + d * h * 0.33, p + d * h * (0.52 if k % 2 else 0.62), 0.04, S["Gold"], segments=4, r_end=0.005)


def sun_dial(b, x, y, z, key):
    # Where the tower's sun waits: rings of tarnished gold laid on the floor round a crystal, 1 cm proud.
    b.begin(key, 0.0, 1.0)
    b.dim = 0.55
    c = bl(x, y, z)
    zt = c.z + 0.01
    G, D, DB, CR = S["Gold"], S["Dark"], S["DarkBand"], S["Crystal"]
    rings = [(0.3, zt, CR), (0.4, zt, G), (1.6, zt, D), (1.7, zt, G), (2.9, zt, D), (3.05, zt, G), (3.25, zt, D), (3.35, zt, G),
             (3.35, c.z, G), (0.0, c.z, D)]
    b.lathe(c.x, c.y, rings, n=96, cap_top=CR)
    for k in range(12):                                      # twelve rays between the inner rings, flush on the dial
        a = 2.0 * math.pi * k / 12.0
        p, q = Vector((math.cos(a), math.sin(a), 0.0)), Vector((-math.sin(a), math.cos(a), 0.0))
        w = 0.06 if k % 3 else 0.12
        new = bmesh.new()
        vs = [new.verts.new(Vector((c.x, c.y, zt + 0.004)) + p * r + q * s) for r, s in ((1.75, -w), (2.85, -0.01), (2.85, 0.01), (1.75, w))]
        face = new.faces.new(vs)
        new.normal_update()
        if face.normal.z < 0:
            bmesh.ops.reverse_faces(new, faces=list(new.faces))
        b.add(new, G)
    return None


def post(b, lo, hi, look, key):
    # A tall block (a post): square plinth and abacus at the box's size, fluted shaft inside, gold necking.
    rng = b.begin(key, hi.z, hi.z - lo.z)
    cx, cy = (lo.x + hi.x) / 2.0, (lo.y + hi.y) / 2.0
    half = min(hi.x - lo.x, hi.y - lo.y) / 2.0
    b.box(Vector((lo.x, lo.y, lo.z)), Vector((hi.x, hi.y, lo.z + 0.25)), S["Pearl"])
    r = half * 0.8
    b.tube((cx, cy, lo.z + 0.25), (cx, cy, hi.z - 0.3), r, S["Pearl"], flutes=10)
    z = hi.z - 0.3 - 3.0                              # tall posts: thin gold rings every 3 m down from the top
    while z > lo.z + 1.0:
        b.tube((cx, cy, z - 0.03), (cx, cy, z + 0.03), r * 1.04, S["Gold"], segments=16)
        z -= 3.0
    b.tube((cx, cy, hi.z - 0.36), (cx, cy, hi.z - 0.28), r * 1.08, S["Gold"], segments=16)
    b.tube((cx, cy, hi.z - 0.28), (cx, cy, hi.z - 0.12), r, S["Pearl"], segments=16, r_end=half * 0.98)
    # its foot hangs in the air: a gold-ringed point and a crystal under the plinth
    b.tube((cx, cy, lo.z), (cx, cy, lo.z - 0.06), half * 0.9, S["Gold"], segments=16)
    b.tube((cx, cy, lo.z - 0.06), (cx, cy, lo.z - 0.06 - half * 2.5), half * 0.85, S["Pearl"], segments=8, r_end=0.02)
    crystal(b, Vector((cx, cy, lo.z - 0.06 - half * 2.5)), 0.05 + 0.05 * half)
    inlaid_top(b, lo, hi, hi.z, S["Gold"] if look == "gold" else S["Pearl"], S["Gold"], margin=0.02, strip=0.02)
    b.box(Vector((lo.x, lo.y, hi.z - 0.12)), Vector((hi.x, hi.y, hi.z - 0.01)), S["Pearl"])
    return True


def clear_angle(a, blocked, width=0.5):
    for _ in range(24):
        if all(abs((a - b_ + math.pi) % (2.0 * math.pi) - math.pi) > width for b_ in blocked):
            return a
        a += 0.21
    return None


def terrace(b, x, y, top, size, key, blocked):
    # An island as a round terrace of heaven: rings of pearl and gold flush on top round a glowing rosette (the
    # light comes down there), a moulded rim, a stepped foundation of pale stone banded in gold down to a finial and
    # a crystal; slim gold-capped posts on the rim, outside the footing, away from the route.
    R = size / 200.0
    flat = 0.965 * R
    c = bl(x, y, top)
    zt = c.z
    depth = 1.4 * R
    rng = b.begin(key, zt, depth)
    P, G, ST, CR = S["Pearl"], S["Gold"], S["Stone"], S["Crystal"]
    top_rings = [(0.07 * R, zt, CR), (0.1 * R, zt, G), (0.32 * R, zt, P), (0.35 * R, zt, G), (0.62 * R, zt, P), (0.65 * R, zt, G),
                 (0.88 * R, zt, P), (0.92 * R, zt, G), (flat, zt, P)]
    rim = [(R, zt - 0.04, P), (R, zt - 0.22, P), (R * 0.985, zt - 0.24, G), (R * 0.985, zt - 0.32, G), (R * 0.95, zt - 0.34, P)]
    steps = []
    r, z = R * 0.95, zt - 0.34
    count = 4
    for k in range(count):
        z_next = z - (depth - 1.0) / count * rng.uniform(0.8, 1.1)
        steps += [(r, z_next, ST), (r * 0.97, z_next - 0.06, G), (r * 0.78, z_next - 0.08, ST)]
        r, z = r * 0.78, z_next - 0.08
    finial = [(r * 0.9, z - 0.12, G), (r * 0.55, z - 0.3, G), (r * 0.5, z - 0.5, ST), (0.0, z - 0.5 - 0.35 * R, ST)]
    b.lathe(c.x, c.y, top_rings + rim + steps + finial, n=max(48, int(R * 14)), cap_top=CR)
    tip = z - 0.5 - 0.35 * R
    crystal(b, Vector((c.x, c.y, tip)), 0.12 + 0.02 * R)
    # posts on the rim
    count = int(2.0 * math.pi * R / 2.2)
    for k in range(count):
        a = clear_angle(2.0 * math.pi * k / count, blocked)
        if a is None or abs(a - 2.0 * math.pi * k / count) > 1e-6:
            continue                                   # this one would stand in the way: leave a gap
        q = Vector((c.x + math.cos(a) * (R + 0.16), c.y + math.sin(a) * (R + 0.16), 0.0))
        b.tube((q.x, q.y, zt - 0.3), (q.x, q.y, zt + 0.75), 0.1, P, flutes=6)
        b.tube((q.x, q.y, zt + 0.75), (q.x, q.y, zt + 0.82), 0.14, G, segments=10)
        b.blob((q.x, q.y, zt + 0.92), (0.08, 0.08, 0.1), G, 1)
    return True


FOOTHOLDS = ("island", "cloud", "vanish", "mover", "timed", "falling", "marble", "block", "jewel", "lplat", "thread", "moving")


def where(piece):
    k = piece[0]
    if k in ("block",):
        return (piece[1] + piece[2]) / 2.0, (piece[3] + piece[4]) / 2.0, piece[6]
    if k == "marble":
        return (piece[1] + piece[2]) / 2.0, (piece[3] + piece[4]) / 2.0, piece[5]
    if k == "thread":
        return piece[1], piece[2], None
    if k == "lplat":                                   # ("lplat", beam, x, y, top, size)
        return piece[2], piece[3], piece[4]
    return piece[1], piece[2], piece[3]


def neighbours(route, piece, reach=1500.0):
    _, x, y, top, size = piece
    out = []
    for other in route.pieces:
        if other is piece or other[0] not in FOOTHOLDS:
            continue
        ox, oy, otop = where(other)
        if math.hypot(ox - x, oy - y) < size / 2.0 + reach and (otop is None or abs(otop - top) < 1500.0):
            out.append(math.atan2(-(oy - y), ox - x))
    return out


def dress(b, piece, index, route):
    kind = piece[0]
    key = "{}:{}".format(index, kind)
    if kind == "block" and piece[8] in os.environ.get("HEAVEN_ART_SKIP", "").split(","):
        return None                                    # (previews only: e.g. HEAVEN_ART_SKIP=Tower Roof to look inside)
    if kind == "island":
        _, x, y, top, size = piece
        terrace(b, x, y, top, size, key, neighbours(route, piece))
        return "Island"
    if kind == "block":
        _, x0, x1, y0, y1, z0, z1, look, name = piece
        lo, hi = bl(x0, y1, z0), bl(x1, y0, z1)
        tall = z1 - z0 > 2.5 * min(x1 - x0, y1 - y0)
        if look == "darkstone":
            if tall:
                dark_wall(b, lo, hi, key)
            else:
                dark_slab(b, lo, hi, key)
            return name
        if look not in ("marble", "gold", "stone"):
            return None                                # sky, glow, ember: later
        if tall and max(x1 - x0, y1 - y0) > 4.0 * min(x1 - x0, y1 - y0):
            dark_wall(b, lo, hi, key, light=True)          # a long wall (the parapets, the Iwato corridor)
        elif tall:
            post(b, lo, hi, look, key)
        else:
            # the tower's wall stones jut out short (jumped past from below); ruin steps and the wing pedestal stand
            # on a floor
            slab(b, lo, hi, look, key, corbel_max={"Wall Stone": 0.6, "Ruin Step": 0.0, "Wing Pedestal": 0.0}.get(name, 2.2))
            if name == "Gate Lintel":
                gate_crown(b, lo, hi)
        return name
    if kind == "sun":
        return sun_dial(b, piece[1], piece[2], piece[3], key)
    if kind == "under":
        _, x0, x1, y0, y1, under, thick, look, name = piece
        if look not in ("marble", "gold", "stone"):
            return None
        flipped_slab(b, bl(x0, y1, under), bl(x1, y0, under + thick), look, key)
        return name
    return None


# ===================================================================================================== output
def preview(out, eye, look):
    for slot in SLOTS:
        mat = bpy.data.materials["M_HeavenArt" + slot]
        mat.use_nodes = True
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        bsdf = nodes.get("Principled BSDF")
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(os.path.join(TEX_DIR, "T_HeavenArt" + slot + "_C.png"))
        vcol = nodes.new("ShaderNodeVertexColor")
        vcol.layer_name = "Col"
        mix = nodes.new("ShaderNodeVectorMath")
        mix.operation = "MULTIPLY"
        links.new(tex.outputs["Color"], mix.inputs[0])
        links.new(vcol.outputs["Color"], mix.inputs[1])
        links.new(mix.outputs[0], bsdf.inputs["Base Color"])
        mask_path = os.path.join(TEX_DIR, "T_HeavenArt" + slot + "_E.png")
        if os.path.exists(mask_path):
            mtex = nodes.new("ShaderNodeTexImage")
            mtex.image = bpy.data.images.load(mask_path)
            mtex.image.colorspace_settings.name = "Non-Color"
            mul = nodes.new("ShaderNodeMath")
            mul.operation = "MULTIPLY"
            mul.inputs[1].default_value = {"Crystal": 4.0, "Channel": 2.0, "Stone": 1.0, "DarkBand": 0.5}[slot]
            links.new(mtex.outputs["Color"], mul.inputs[0])
            links.new(mul.outputs[0], bsdf.inputs["Emission Strength"])
            bsdf.inputs["Emission Color"].default_value = (1.0, 0.85, 0.55, 1.0)
        rough, metal = {"Pearl": (0.3, 0.0), "Gold": (0.25, 1.0), "Channel": (0.3, 0.0)}.get(slot, (0.8, 0.0))
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
    scene = bpy.context.scene
    world = bpy.data.worlds.new("Dim")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.35, 0.38, 0.5, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.7
    scene.world = world
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 2.5
    sun.data.color = (1.0, 0.95, 0.88)
    sun.rotation_euler = (math.radians(45), 0.0, math.radians(-130))
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
    route = area4_layout.build(B, 500.9, 980.0, 600.0, 300.0)
    LEVELS[:] = sorted({round(p[6] / 100.0, 3) for p in route.pieces if p[0] == "block" and p[7] == "darkstone" and "Floor" in p[8]})
    report = []
    by_section = {}
    section = ""
    for index, piece in enumerate(route.pieces):
        if piece[0] == "section":
            section = piece[1].split(" ")[0]
            continue
        by_section.setdefault(section, []).append((index, piece))
    for number in SECTIONS:
        builder = Builder()
        names = {}
        for index, piece in by_section.get(number, []):
            name = dress(builder, piece, index, route)
            if name:
                names[name] = names.get(name, 0) + 1
        name = "SM_Heaven_" + number
        obj = builder.finish(name)
        export(obj, name)
        with open(os.path.join(OUT_DIR, "heaven_art_" + number + ".json"), "w", encoding="utf-8") as out:
            json.dump({"replaces": sorted(names)}, out)
        report.append("{}: {}, {} vertices".format(name, ", ".join("{} {}".format(k, v) for k, v in sorted(names.items())), len(obj.data.vertices)))
    with open(os.path.join(OUT_DIR, "heaven_art_build.txt"), "w", encoding="utf-8") as out:
        out.write("\n".join(report) + "\n")
    print("\n".join(report))
    if PREVIEW:
        preview(*PREVIEW)


main()
