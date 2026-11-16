# Builds area 1's Roman ruins art in Blender from SourceArt/Models/Ruins/area1_layout.json (export_area1_layout.py):
# every static box of the chosen sections becomes a dressed piece of the same size - the surfaces the player stands on
# stay exactly where the boxes' tops are (the boxes stay in the level as the invisible collision) - and all of a
# section is one mesh, in world position, its pivot at the origin:
#   SourceArt/Models/Ruins/SM_Ruins_<section letter>.fbx   slots: Ashlar Paving Plaster Terracotta Wood Marble Rock
#                                                          Bronze Ember (named M_Ruins<Slot>)
#   SourceArt/Models/Ruins/Textures/T_Ruins<Slot>_C.png / _N.png   tileable 1024 colour and normal maps, painted here
#                                                                   (2 m of surface per tile)
# What becomes what (by the actor's label): Wall, Hall Stair, Wall Stone, Pier, Arch, Gate Tower... -> beveled ashlar
# with a plinth and a band under the top; Town Ground, Cliff... -> paving on top, rock on the sides; Column -> a
# fluted marble column with base and capital; Roof -> terracotta tiles on top, plaster sides, eaves; Crate -> a
# framed wooden crate; Brazier -> a bronze bowl on a tripod with glowing coals. UE's FBX import flips Y, so a UE point
# (x, y, z) cm is put at (x, -y, z) / 100 m here.
# Run without opening Blender (sections: the letters, default A):
#   blender --background --factory-startup --python build_ruins_blender.py -- A [B C ...]
import json
import math
import os
import random
import sys

import bmesh
import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(os.path.dirname(HERE), "SourceArt", "Models", "Ruins")
TEX_DIR = os.path.join(OUT_DIR, "Textures")
SLOTS = ["Ashlar", "Paving", "Plaster", "Terracotta", "Wood", "Marble", "Rock", "Bronze", "Ember"]
S = {name: i for i, name in enumerate(SLOTS)}
TEX = 1024
TILE = 2.0          # metres of surface per texture tile

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SECTIONS = [a.upper() for a in args] or ["A"]


# ===================================================================================================== textures
def noise(size, scale, seed):
    # Tileable noise: random spectrum, low-passed (scale = feature size in pixels).
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


def save(name, rgb, height=None, strength=6.0):
    for suffix, data in (("_C", rgb), ("_N", None if height is None else normal_from(height, strength))):
        if data is None:
            continue
        image = bpy.data.images.new("T_Ruins" + name + suffix, TEX, TEX, alpha=False)
        rgba = np.ones((TEX, TEX, 4), dtype=np.float32)
        rgba[:, :, :3] = np.clip(data, 0.0, 1.0)
        image.pixels.foreach_set(rgba[::-1].reshape(-1))     # Blender rows run bottom to top
        image.filepath_raw = os.path.join(TEX_DIR, "T_Ruins" + name + suffix + ".png")
        image.file_format = "PNG"
        image.save()


def normal_from(height, strength):
    dx = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) * strength
    dy = (np.roll(height, -1, 0) - np.roll(height, 1, 0)) * strength
    n = np.dstack((-dx, dy, np.ones_like(height)))
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return n * 0.5 + 0.5


def tint(base, amount):
    return np.dstack([base[i] * amount for i in range(3)])


def blocks(rows, widths, mortar, seed, jitter=0.0):
    # Running-bond blocks over the tile: per pixel the block's id and its distance to the nearest joint (0..1 tile).
    rng = random.Random(seed)
    ids = np.zeros((TEX, TEX), dtype=np.int32)
    edge = np.ones((TEX, TEX))
    row_h = TEX // rows
    count = 0
    for r in range(rows):
        y0 = r * row_h
        x = rng.randint(0, TEX // 2)
        bounds = []
        while len(bounds) == 0 or sum(b for b in bounds) < TEX:
            bounds.append(int(TEX * rng.uniform(*widths)))
        pos = x
        for w in bounds:
            xs = (np.arange(pos, pos + w) % TEX)
            for yy in range(y0, y0 + row_h):
                ids[yy, xs] = count
            # distance to the joint, in pixels
            local_x = np.minimum(np.arange(w), w - 1 - np.arange(w))
            for yy in range(y0, y0 + row_h):
                local_y = min(yy - y0, y0 + row_h - 1 - yy)
                edge[yy, xs] = np.minimum(local_x, local_y)
            pos += w
            count += 1
    return ids, edge, count


def make_textures():
    os.makedirs(TEX_DIR, exist_ok=True)
    grain = fbm(TEX, 1)
    fine = noise(TEX, 3, 2)
    # Ashlar: warm sandstone blocks in running bond, recessed mortar, worn edges.
    ids, edge, n = blocks(6, (0.18, 0.34), 10, 7)
    rng = np.random.default_rng(3)
    shade = rng.uniform(0.82, 1.08, n)[ids]
    joint = np.clip(edge / 9.0, 0.0, 1.0)
    height = np.clip(edge / 14.0, 0.0, 1.0) * 0.6 + grain * 0.3 + fine * 0.1
    base = np.array([0.72, 0.58, 0.42])
    colour = tint(base, (shade * (0.78 + 0.3 * grain)) * (0.55 + 0.45 * joint))
    save("Ashlar", np.transpose(colour, (0, 1, 2)), height, 5.0)
    # Paving: big square-ish slabs, grey-buff, dark gaps.
    ids, edge, n = blocks(4, (0.22, 0.32), 6, 11)
    shade = np.random.default_rng(5).uniform(0.78, 1.05, n)[ids]
    joint = np.clip(edge / 6.0, 0.0, 1.0)
    height = np.clip(edge / 10.0, 0.0, 1.0) * 0.5 + fbm(TEX, 9) * 0.4 + fine * 0.1
    colour = tint(np.array([0.62, 0.56, 0.47]), shade * (0.8 + 0.3 * fbm(TEX, 13)) * (0.45 + 0.55 * joint))
    save("Paving", colour, height, 4.0)
    # Plaster: cream lime plaster, blotchy, with patches worn through to brick.
    blot = fbm(TEX, 21, (200, 60, 20, 6))
    worn = np.clip((noise(TEX, 90, 23) - 0.62) * 8.0, 0.0, 1.0)
    plaster = tint(np.array([0.86, 0.79, 0.66]), 0.82 + 0.25 * blot)
    brick = tint(np.array([0.62, 0.32, 0.2]), 0.8 + 0.3 * fine)
    colour = plaster * (1.0 - worn[..., None]) + brick * worn[..., None]
    save("Plaster", colour, blot * 0.3 + worn * -0.4 + fine * 0.1, 3.0)
    # Terracotta: rows of curved tiles, each row half a tile over the last.
    yy, xx = np.mgrid[0:TEX, 0:TEX] / TEX
    rows, cols = 8, 6
    shift = (np.floor(yy * rows) % 2) * 0.5 / cols
    u = ((xx + shift) * cols) % 1.0
    v = (yy * rows) % 1.0
    curve = np.sin(u * math.pi)
    lap = np.clip(v * 3.0, 0.0, 1.0)
    tile_id = (np.floor((xx + shift) * cols) + 97 * np.floor(yy * rows)).astype(int)
    shade = np.random.default_rng(31).uniform(0.8, 1.1, tile_id.max() + 1)[tile_id]
    height = curve * 0.7 * lap + (1 - lap) * 0.2 + fine * 0.05
    colour = tint(np.array([0.72, 0.33, 0.18]), shade * (0.55 + 0.45 * curve) * (0.6 + 0.4 * lap) * (0.85 + 0.25 * fbm(TEX, 33)))
    save("Terracotta", colour, height, 6.0)
    # Wood: horizontal planks with grain.
    planks = 5
    plank = np.floor(yy * planks)
    streak = noise(TEX, 4, 41)
    stretched = np.repeat(noise(TEX, 30, 43)[:, :1], TEX, axis=1)
    g = 0.6 * stretched + 0.4 * np.roll(streak, 0, 1)
    seam = np.clip(np.abs(((yy * planks) % 1.0) - 0.5) * 2.0, 0.0, 1.0)
    seam = np.clip((1.0 - seam) * 12.0, 0.0, 1.0)
    shade = np.random.default_rng(45).uniform(0.8, 1.1, planks)[plank.astype(int)]
    colour = tint(np.array([0.42, 0.27, 0.15]), shade * (0.7 + 0.4 * g) * (0.4 + 0.6 * seam))
    save("Wood", colour, g * 0.3 + seam * 0.6, 4.0)
    # Marble: white with soft grey veins.
    warp = fbm(TEX, 51, (160, 60, 20, 8))
    veins = np.abs(np.sin((xx * 3.0 + yy * 1.5 + warp * 2.5) * math.pi * 2.0)) ** 0.25
    colour = tint(np.array([0.92, 0.9, 0.86]), 0.75 + 0.25 * veins)
    save("Marble", colour, veins * 0.1 + fine * 0.05, 2.0)
    # Rock: weathered buff rock, cracks.
    rock = fbm(TEX, 61, (220, 80, 24, 8))
    cracks = np.clip((np.abs(noise(TEX, 40, 63) - 0.5) * 18.0), 0.0, 1.0)
    colour = tint(np.array([0.56, 0.47, 0.37]), (0.65 + 0.45 * rock) * (0.5 + 0.5 * cracks))
    save("Rock", colour, rock * 0.8 + cracks * 0.3, 7.0)
    # Heaven's debris (area 1's moving pieces, on the engine cube whose faces each span the texture once):
    # weathered white marble, a gold band round every face's edge (its glow mask in _E), chips and grime.
    warp = fbm(TEX, 81, (160, 60, 20, 8))
    veins = np.abs(np.sin((xx * 2.0 + yy * 3.0 + warp * 3.0) * math.pi * 2.0)) ** 0.3
    border = np.minimum(np.minimum(xx, 1.0 - xx), np.minimum(yy, 1.0 - yy))
    band = ((border > 0.025) & (border < 0.085)).astype(float)
    groove = ((border > 0.085) & (border < 0.1)).astype(float)
    chips = np.clip((noise(TEX, 25, 83) - 0.7) * 10.0, 0.0, 1.0) * (border > 0.1)
    grime = fbm(TEX, 85, (240, 90, 30, 10))
    marble = tint(np.array([0.93, 0.91, 0.87]), (0.78 + 0.22 * veins) * (0.8 + 0.25 * grime))
    marble = marble * (1.0 - 0.45 * chips[..., None]) * (1.0 - 0.35 * groove[..., None])
    gold = tint(np.array([0.95, 0.72, 0.3]), 0.8 + 0.3 * noise(TEX, 6, 87))
    colour = marble * (1.0 - band[..., None]) + gold * band[..., None]
    save("Debris", colour, veins * 0.05 + band * 0.4 - groove * 0.3 - chips * 0.4 + fine * 0.05, 5.0)
    mask = np.dstack([band * (0.7 + 0.3 * noise(TEX, 10, 89))] * 3)
    image = bpy.data.images.new("T_RuinsDebris_E", TEX, TEX, alpha=False)
    rgba = np.ones((TEX, TEX, 4), dtype=np.float32)
    rgba[:, :, :3] = mask
    image.pixels.foreach_set(rgba[::-1].reshape(-1))
    image.filepath_raw = os.path.join(TEX_DIR, "T_RuinsDebris_E.png")
    image.file_format = "PNG"
    image.save()
    # Bronze and ember: plain colour cards (the material does the rest).
    save("Bronze", tint(np.array([0.45, 0.3, 0.14]), 0.8 + 0.3 * grain), grain * 0.2, 2.0)
    save("Ember", tint(np.array([1.0, 0.45, 0.12]), 0.7 + 0.5 * noise(TEX, 20, 71)), None)


# ===================================================================================================== meshes
def to_blender(x, y, z):
    return (x / 100.0, -y / 100.0, z / 100.0)


class Builder:
    # One bmesh for the whole section; pieces are added in Blender metres.
    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")

    def box(self, x0, x1, y0, y1, z0, z1, side, top=None, bottom=None, bevel=0.0):
        # x/y/z in Blender metres, x0 < x1 etc.
        new = bmesh.new()
        bmesh.ops.create_cube(new, size=1.0)
        for v in new.verts:
            v.co.x = x0 if v.co.x < 0 else x1
            v.co.y = y0 if v.co.y < 0 else y1
            v.co.z = z0 if v.co.z < 0 else z1
        if bevel > 0.0:
            limit = min(x1 - x0, y1 - y0, z1 - z0) * 0.3
            bmesh.ops.bevel(new, geom=list(new.edges), offset=min(bevel, limit), segments=2, profile=0.5, affect="EDGES")
        self.take(new, side, top if top is not None else side, bottom if bottom is not None else side)

    def take(self, new, side, top, bottom):
        uv = new.loops.layers.uv.new("UVMap")
        for face in new.faces:
            n = face.normal
            face.material_index = top if n.z > 0.7 else (bottom if n.z < -0.7 else side)
            for loop in face.loops:
                c = loop.vert.co
                if abs(n.z) > 0.7:
                    loop[uv].uv = (c.x / TILE, c.y / TILE)
                elif abs(n.x) > abs(n.y):
                    loop[uv].uv = (c.y / TILE, c.z / TILE)
                else:
                    loop[uv].uv = (c.x / TILE, c.z / TILE)
        mesh = bpy.data.meshes.new("piece")
        new.to_mesh(mesh)
        new.free()
        self.bm.from_mesh(mesh)
        bpy.data.meshes.remove(mesh)

    def cylinder(self, cx, cy, z0, z1, r, slot, segments=24, flutes=0, top=None):
        new = bmesh.new()
        ring_lo, ring_hi = [], []
        for i in range(segments):
            a = 2.0 * math.pi * i / segments
            rr = r * (1.0 - 0.06 * max(0.0, math.cos(a * flutes))) if flutes else r
            ring_lo.append(new.verts.new((cx + rr * math.cos(a), cy + rr * math.sin(a), z0)))
            ring_hi.append(new.verts.new((cx + rr * math.cos(a), cy + rr * math.sin(a), z1)))
        for i in range(segments):
            j = (i + 1) % segments
            new.faces.new((ring_lo[i], ring_lo[j], ring_hi[j], ring_hi[i]))
        new.faces.new(list(reversed(ring_lo)))
        new.faces.new(ring_hi)
        bmesh.ops.recalc_face_normals(new, faces=new.faces)
        # Cylinder sides: wrap U round the column.
        uv = new.loops.layers.uv.new("UVMap")
        for face in new.faces:
            face.material_index = slot if top is None or abs(face.normal.z) < 0.7 else top
            for loop in face.loops:
                c = loop.vert.co
                if abs(face.normal.z) > 0.7:
                    loop[uv].uv = (c.x / TILE, c.y / TILE)
                else:
                    a = math.atan2(c.y - cy, c.x - cx)
                    loop[uv].uv = (a * r / TILE, c.z / TILE)
        mesh = bpy.data.meshes.new("piece")
        new.to_mesh(mesh)
        new.free()
        self.bm.from_mesh(mesh)
        bpy.data.meshes.remove(mesh)

    def finish(self, name):
        mesh = bpy.data.meshes.new(name)
        self.bm.to_mesh(mesh)
        self.bm.free()
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.scene.collection.objects.link(obj)
        for slot in SLOTS:
            material = bpy.data.materials.get("M_Ruins" + slot) or bpy.data.materials.new("M_Ruins" + slot)
            obj.data.materials.append(material)
        return obj


def bounds(row):
    (x0, y0, z0), (x1, y1, z1) = row["min"], row["max"]
    a, b = to_blender(x0, y0, z0), to_blender(x1, y1, z1)
    return min(a[0], b[0]), max(a[0], b[0]), min(a[1], b[1]), max(a[1], b[1]), a[2], b[2]


def role(label):
    name = label.split(" ", 2)[-1].rstrip("0123456789 ").strip()
    return name


def dress(builder, row, rng):
    x0, x1, y0, y1, z0, z1 = bounds(row)
    name = role(row["label"])
    w, d, h = x1 - x0, y1 - y0, z1 - z0
    if name in ("Column",):
        cx, cy, r = (x0 + x1) / 2.0, (y0 + y1) / 2.0, min(w, d) / 2.0
        base = min(0.25, h * 0.08)
        builder.box(cx - r * 1.3, cx + r * 1.3, cy - r * 1.3, cy + r * 1.3, z0, z0 + base, S["Marble"], bevel=0.03)
        builder.cylinder(cx, cy, z0 + base, z1 - 0.3 * base - base, r * 0.92, S["Marble"], 24, 12)
        builder.cylinder(cx, cy, z1 - 1.3 * base, z1 - base, r * 1.08, S["Marble"], 24)
        builder.box(cx - r * 1.25, cx + r * 1.25, cy - r * 1.25, cy + r * 1.25, z1 - base, z1, S["Marble"], bevel=0.02)
    elif ("Roof" in name and "Broken" not in name) or name in ("House", "Long House"):
        # Houses are walked on along their tops: tiled roof terraces over plaster walls, eaves round them.
        builder.box(x0, x1, y0, y1, z0, z1, S["Plaster"], S["Terracotta"], bevel=0.02)
        eave = 0.18
        builder.box(x0 - eave, x1 + eave, y0 - eave, y1 + eave, z1 - 0.12, z1 - 0.04, S["Terracotta"], bevel=0.02)
        if h > 2.0:
            builder.box(x0 - 0.05, x1 + 0.05, y0 - 0.05, y1 + 0.05, z0, z0 + 0.4, S["Ashlar"], bevel=0.02)
    elif name in ("Deck", "Broken Bridge", "Broken Roof") or name.startswith("Story"):
        # Floors and decks: paving to walk on, ashlar edges.
        builder.box(x0, x1, y0, y1, z0, z1, S["Ashlar"], S["Paving"], bevel=0.04)
    elif name in ("Cliff Ledge", "Overhang"):
        builder.box(x0, x1, y0, y1, z0, z1, S["Rock"], bevel=0.08)
    elif name == "Gate Lintel":
        builder.box(x0, x1, y0, y1, z0, z1, S["Marble"], bevel=0.04)
    elif name == "Crate":
        builder.box(x0 + 0.03, x1 - 0.03, y0 + 0.03, y1 - 0.03, z0, z1 - 0.01, S["Wood"])
        f = 0.06
        for xa, xb in ((x0, x0 + f), (x1 - f, x1)):
            for ya, yb in ((y0, y0 + f), (y1 - f, y1)):
                builder.box(xa, xb, ya, yb, z0, z1, S["Wood"], bevel=0.01)
        for za, zb in ((z0, z0 + f), (z1 - f, z1)):
            builder.box(x0, x1, y0, y0 + f, za, zb, S["Wood"], bevel=0.01)
            builder.box(x0, x1, y1 - f, y1, za, zb, S["Wood"], bevel=0.01)
            builder.box(x0, x0 + f, y0, y1, za, zb, S["Wood"], bevel=0.01)
            builder.box(x1 - f, x1, y0, y1, za, zb, S["Wood"], bevel=0.01)
    elif name == "Brazier":
        cx, cy, r = (x0 + x1) / 2.0, (y0 + y1) / 2.0, min(w, d) / 2.0
        for k in range(3):
            a = 2.0 * math.pi * k / 3.0
            lx, ly = cx + 0.7 * r * math.cos(a), cy + 0.7 * r * math.sin(a)
            builder.cylinder(lx, ly, z0, z0 + 0.7 * h, 0.04, S["Bronze"], 8)
        builder.cylinder(cx, cy, z0 + 0.6 * h, z1 - 0.05, r, S["Bronze"], 20)
        builder.cylinder(cx, cy, z1 - 0.06, z1, r * 0.85, S["Ember"], 20)
    elif name in ("Town Ground", "Cliff and Courtyard", "Ground") or "Ground" in name:
        builder.box(x0, x1, y0, y1, z0, z1, S["Rock"], S["Paving"], bevel=0.05)
    elif name in ("Hall Stair",):
        builder.box(x0, x1, y0, y1, z0, z1, S["Ashlar"], S["Paving"], bevel=0.03)
    else:
        # Walls and the rest: ashlar, a plinth at the foot, a band just under the top.
        builder.box(x0, x1, y0, y1, z0, z1, S["Ashlar"], bevel=0.04)
        if h > 1.2 and min(w, d) > 0.25:
            out = 0.06
            builder.box(x0 - out, x1 + out, y0 - out, y1 + out, z0, z0 + 0.35, S["Ashlar"], bevel=0.03)
            if h > 2.0:
                builder.box(x0 - 0.04, x1 + 0.04, y0 - 0.04, y1 + 0.04, z1 - 0.32, z1 - 0.2, S["Marble"], bevel=0.015)
            # Ruin: a few fallen stones at the foot, along the long sides (no collision; small enough to walk over).
            long_x = w >= d
            for k in range(rng.randint(0, 3)):
                t = rng.uniform(0.1, 0.9)
                s = rng.uniform(0.1, 0.22)
                side = rng.choice((-1.0, 1.0))
                if long_x:
                    px, py = x0 + t * w, (y1 + 0.12 + s) if side > 0 else (y0 - 0.12 - s)
                else:
                    px, py = (x1 + 0.12 + s) if side > 0 else (x0 - 0.12 - s), y0 + t * d
                builder.box(px - s, px + s * rng.uniform(0.7, 1.3), py - s * rng.uniform(0.6, 1.0), py + s, z0, z0 + s * rng.uniform(0.6, 1.1), S["Ashlar"], bevel=0.03)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    make_textures()
    rows = json.load(open(os.path.join(OUT_DIR, "area1_layout.json"), encoding="utf-8"))
    report = []
    for letter in SECTIONS:
        builder = Builder()
        rng = random.Random(ord(letter))
        count = 0
        for row in rows:
            section = row["folder"].split("/")[1] if "/" in row["folder"] else ""
            if not section.startswith(letter + " ") or row["class"] != "StaticMeshActor" or row["hidden"]:
                continue
            dress(builder, row, rng)
            count += 1
        name = "SM_Ruins_" + letter
        obj = builder.finish(name)
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.export_scene.fbx(filepath=os.path.join(OUT_DIR, name + ".fbx"), use_selection=True, apply_unit_scale=True,
                                 mesh_smooth_type="FACE", use_mesh_modifiers=False)
        report.append("{}: {} pieces, {} vertices".format(name, count, len(obj.data.vertices)))
    with open(os.path.join(OUT_DIR, "ruins_build.txt"), "w", encoding="utf-8") as out:
        out.write("\n".join(report) + "\n")
    print("\n".join(report))


main()
