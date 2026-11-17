# Builds area 2's "ancient machine" tower art in Blender from SourceArt/Models/Tower/area2_layout.json
# (export_area2_layout.py): old stone being taken over by machinery - grey ashlar, riveted iron ribs, verdigris bronze
# pipes, and channels cut into the stone that glow a dim orange. Every static box of the chosen sections becomes a
# dressed piece of the same size - surfaces the player stands on stay exactly at the boxes' tops (the boxes stay in the
# level as the invisible collision) - and all of a section is one mesh, in world position, pivot at the origin:
#   SourceArt/Models/Tower/SM_Tower_<section letter>.fbx    slots: Masonry Flagstone Iron Bronze Brass Glyph Ember
#                                                            Shadow (named M_Tower<Slot>)
#   SourceArt/Models/Tower/SM_TowerGear_<letter><n>.fbx      the great wall gears, one mesh each (they turn in UE),
#   SourceArt/Models/Tower/tower_gears_<letter>.json          and where they go
#   SourceArt/Models/Tower/SM_TowerLamps_<letter>.fbx         the hanging lamps (world positioned; no shadows in UE)
#   SourceArt/Models/Tower/Textures/T_Tower<Slot>_C/_N/_E.png   tileable 1024 colour, normal and glow-mask maps
#                                                                (2 m of surface per tile)
# Gimmicks (BP actors) are not touched. Decorations never make new ledges at walkable heights: anything sideways is
# thin, and anything on a walkable top sits 1 cm proud of it (no coplanar faces: they flicker).
# A UE point (x, y, z) cm is put at (x, -y, z) / 100 m here (the FBX import flips Y back).
# Run without opening Blender (sections: the letters, default A):
#   blender --background --factory-startup --python build_tower_blender.py -- A [B C ...] [--preview out.png cx,cy,cz lx,ly,lz]
# --preview also renders the first section from camera point c looking at l (UE cm), with the lamps lit, for a check.
import glob
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
OUT_DIR = os.path.join(os.path.dirname(HERE), "SourceArt", "Models", "Tower")
TEX_DIR = os.path.join(OUT_DIR, "Textures")
SLOTS = ["Masonry", "Flagstone", "Iron", "Bronze", "Brass", "Glyph", "Ember", "Shadow"]
S = {name: i for i, name in enumerate(SLOTS)}
KEEP = {S["Brass"], S["Ember"], S["Shadow"]}     # slots whose colour the vertex tint leaves alone
TEX = 1024
TILE = 2.0          # metres of surface per texture tile
FLOOR_TILE = 3.6    # flagstone floors repeat less often
BASE = 72.60        # area 2's floor (m): glyph bands and iron bands line up on heights counted from here

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
PREVIEW = None
if "--preview" in args:
    i = args.index("--preview")
    PREVIEW = (args[i + 1], [float(v) for v in args[i + 2].split(",")], [float(v) for v in args[i + 3].split(",")])
    args = args[:i] + args[i + 4:]
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


def write_png(name, rgb):
    size = rgb.shape[0]
    image = bpy.data.images.new(name, size, size, alpha=False)
    rgba = np.ones((size, size, 4), dtype=np.float32)
    rgba[:, :, :3] = np.clip(rgb, 0.0, 1.0)
    image.pixels.foreach_set(rgba[::-1].reshape(-1))     # Blender rows run bottom to top
    image.filepath_raw = os.path.join(TEX_DIR, name + ".png")
    image.file_format = "PNG"
    image.save()
    return image


def normal_from(height, strength):
    dx = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) * strength
    dy = (np.roll(height, -1, 0) - np.roll(height, 1, 0)) * strength
    n = np.dstack((-dx, dy, np.ones_like(height)))
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return n * 0.5 + 0.5


def save(name, rgb, height=None, strength=6.0, mask=None):
    write_png("T_Tower" + name + "_C", rgb)
    if height is not None:
        write_png("T_Tower" + name + "_N", normal_from(height, strength))
    if mask is not None:
        write_png("T_Tower" + name + "_E", np.dstack([mask] * 3))


def tint(base, amount):
    return np.dstack([base[i] * amount for i in range(3)])


def blocks(rows, widths, seed, uneven=False):
    # Running-bond blocks over the tile: per pixel the block's id and its distance to the nearest joint (pixels).
    # uneven: the rows get different heights too (flagstones), so the courses don't read as a grid.
    rng = random.Random(seed)
    ids = np.zeros((TEX, TEX), dtype=np.int32)
    edge = np.ones((TEX, TEX))
    if uneven:
        raw = [rng.uniform(0.6, 1.4) for _ in range(rows)]
        tops = [int(TEX * sum(raw[:r]) / sum(raw)) for r in range(rows)] + [TEX]
    else:
        tops = [r * (TEX // rows) for r in range(rows)] + [TEX]
    count = 0
    for r in range(rows):
        y0 = tops[r]
        row_h = tops[r + 1] - y0
        bounds = []
        while not bounds or sum(bounds) < TEX:
            bounds.append(int(TEX * rng.uniform(*widths)))
        bounds[-1] -= sum(bounds) - TEX          # the row closes on itself: tileable
        pos = rng.randint(0, TEX // 2)
        local_y = np.minimum(np.arange(row_h), row_h - 1 - np.arange(row_h))
        for w in bounds:
            if w <= 0:
                continue
            xs = np.arange(pos, pos + w) % TEX
            local_x = np.minimum(np.arange(w), w - 1 - np.arange(w))
            ids[y0:y0 + row_h][:, xs] = count
            edge[y0:y0 + row_h][:, xs] = np.minimum(local_x[None, :], local_y[:, None])
            pos += w
            count += 1
    return ids, edge, count


def glyph_channels(seed):
    # Right-angled channels on a 16 x 16 grid, ending in rings: the "circuits" cut into the old stone.
    rng = random.Random(seed)
    mask = np.zeros((TEX, TEX))
    cell = TEX // 16
    half = 4
    for _ in range(18):
        i, j = rng.randrange(16), rng.randrange(16)
        for _step in range(rng.randint(3, 7)):
            di, dj = rng.choice(((1, 0), (-1, 0), (0, 1), (0, -1)))
            n = rng.randint(1, 3)
            a, b = (i * cell, j * cell), ((i + di * n) * cell, (j + dj * n) * cell)
            xs = np.arange(min(a[0], b[0]) - half, max(a[0], b[0]) + half + 1) % TEX
            ys = np.arange(min(a[1], b[1]) - half, max(a[1], b[1]) + half + 1) % TEX
            mask[np.ix_(ys, xs)] = 1.0
            i, j = (i + di * n) % 16, (j + dj * n) % 16
        # a ring at the end
        cx, cy = i * cell, j * cell
        r = np.arange(-18, 19)
        dx, dy = np.meshgrid(r, r)
        d = np.sqrt(dx * dx + dy * dy)
        ring = ((d > 9) & (d < 15)) | (d < 4)
        ys, xs = (cy + dy) % TEX, (cx + dx) % TEX
        mask[ys[ring], xs[ring]] = 1.0
    return mask


def make_textures():
    os.makedirs(TEX_DIR, exist_ok=True)
    fine = noise(TEX, 3, 2)
    yy, xx = np.mgrid[0:TEX, 0:TEX] / TEX
    # Masonry: big grey-ochre blocks, worn joints, cracks and grime.
    ids, edge, n = blocks(3, (0.3, 0.55), 101)     # 67 cm courses: big ancient blocks, not bricks
    shade = np.random.default_rng(102).uniform(0.8, 1.1, n)[ids]
    joint = np.clip(edge / 7.0, 0.0, 1.0)
    grain = fbm(TEX, 103)
    cracks = np.clip(np.abs(noise(TEX, 35, 105) - 0.5) * 22.0, 0.0, 1.0)
    grime = fbm(TEX, 107, (220, 80, 24, 8))
    height = np.clip(edge / 12.0, 0.0, 1.0) * 0.6 + grain * 0.3 + fine * 0.1 - (1.0 - cracks) * 0.2
    colour = tint(np.array([0.5, 0.46, 0.4]), shade * (0.75 + 0.35 * grain) * (0.5 + 0.5 * joint) * (0.7 + 0.3 * cracks) * (0.8 + 0.25 * grime))
    save("Masonry", colour, height, 5.0)
    # Flagstone: large worn slabs, darker grey.
    ids, edge, n = blocks(4, (0.14, 0.4), 111, uneven=True)     # over 3.6 m (FLOOR_TILE): 0.5-1.4 m slabs, uneven
    shade = np.random.default_rng(112).uniform(0.8, 1.06, n)[ids]
    joint = np.clip(edge / 6.0, 0.0, 1.0)
    wear = fbm(TEX, 113)
    height = np.clip(edge / 10.0, 0.0, 1.0) * 0.5 + wear * 0.4 + fine * 0.1
    colour = tint(np.array([0.44, 0.42, 0.39]), shade * (0.8 + 0.3 * wear) * (0.45 + 0.55 * joint))
    save("Flagstone", colour, height, 4.0)
    # Iron: staggered 1 m plates, rivet rows along the seams, rust.
    plates = 2
    u = (xx * plates + 0.5 * (np.floor(yy * plates) % 2)) % 1.0
    v = (yy * plates) % 1.0
    size = TEX / plates
    px, py = u * size, v * size
    seam = np.clip(np.minimum(np.minimum(px, size - px), np.minimum(py, size - py)) / 3.0, 0.0, 1.0)
    ex, ey = np.minimum(px, size - px), np.minimum(py, size - py)
    d1 = np.sqrt(((px % 32) - 16) ** 2 + (ey - 14) ** 2)
    d2 = np.sqrt(((py % 32) - 16) ** 2 + (ex - 14) ** 2)
    rivet = np.clip(1.0 - np.minimum(d1, d2) / 5.0, 0.0, 1.0)
    rust = np.clip((fbm(TEX, 121, (180, 60, 20, 6)) - 0.55) * 4.0, 0.0, 1.0)
    metal = tint(np.array([0.24, 0.24, 0.25]), 0.85 + 0.25 * fbm(TEX, 123))
    brown = tint(np.array([0.4, 0.21, 0.1]), 0.8 + 0.4 * fine)
    colour = (metal * (1.0 - rust[..., None]) + brown * rust[..., None]) * (0.45 + 0.55 * seam[..., None]) * (1.0 + 0.35 * rivet[..., None])
    save("Iron", colour, seam * 0.5 + rivet * 0.8 + rust * 0.1 + fine * 0.05, 5.0)
    # Bronze: old bronze with verdigris in blotches.
    patina = np.clip((fbm(TEX, 131, (120, 40, 14, 5)) - 0.5) * 3.0, 0.0, 1.0)
    bronze = tint(np.array([0.5, 0.33, 0.16]), 0.8 + 0.3 * grain)
    verd = tint(np.array([0.25, 0.48, 0.42]), 0.85 + 0.3 * fine)
    save("Bronze", bronze * (1.0 - patina[..., None]) + verd * patina[..., None], grain * 0.2 + patina * 0.2, 2.0)
    # Brass: kept bright - it marks the special footholds (coins, the speed item).
    save("Brass", tint(np.array([0.8, 0.62, 0.3]), 0.9 + 0.15 * noise(TEX, 8, 141)), noise(TEX, 8, 141) * 0.1, 1.0)
    # Glyph stone: darker stone with channels cut in; the channels glow (mask _E).
    ids, edge, n = blocks(2, (0.45, 0.6), 151)
    shade = np.random.default_rng(152).uniform(0.85, 1.05, n)[ids]
    joint = np.clip(edge / 6.0, 0.0, 1.0)
    channels = glyph_channels(153)
    stone = tint(np.array([0.32, 0.3, 0.28]), shade * (0.8 + 0.3 * grain) * (0.55 + 0.45 * joint))
    copper = tint(np.array([0.55, 0.26, 0.09]), 0.9 + 0.2 * fine)
    colour = stone * (1.0 - channels[..., None]) + copper * channels[..., None]
    save("Glyph", colour, np.clip(edge / 10.0, 0.0, 1.0) * 0.3 + grain * 0.2 - channels * 0.5, 5.0, channels * (0.75 + 0.25 * noise(TEX, 10, 155)))
    # Ember: glowing coals of the lanterns (all of it glows).
    save("Ember", tint(np.array([1.0, 0.45, 0.12]), 0.7 + 0.5 * noise(TEX, 20, 71)), None, mask=np.ones((TEX, TEX)))
    # Shadow: the black of a doorway.
    save("Shadow", tint(np.array([0.02, 0.02, 0.025]), np.ones((TEX, TEX))))
    write_png("T_TowerBlack_E", np.zeros((64, 64, 3)))


# ===================================================================================================== meshes
def to_blender(x, y, z):
    return (x / 100.0, -y / 100.0, z / 100.0)


TONES = [   # per-piece stone tints (vertex colour, multiplied over the texture): warm, cool, damp, sooty, plain
    (1.0, 0.8, 0.58), (0.68, 0.76, 0.9), (0.66, 0.8, 0.64), (0.5, 0.47, 0.45), (1.0, 0.98, 0.94),
]
CELL = 1.3   # metres: big faces are cut this fine so stains can vary across them


def stain(x, y, z):
    # Smooth blotches 1-3 m across (0.6 .. 1.05): damp patches, soot, worn spots. Sums of skewed sines, so no grid shows.
    s = (math.sin(x * 1.7 + y * 0.6 + 1.3) * math.sin(z * 1.9 - x * 0.4 + 0.7)
         + 0.7 * math.sin(y * 2.3 - z * 0.8 + 2.1) * math.sin(x * 2.9 + z * 1.1)
         + 0.5 * math.sin((x + y) * 3.7 + z * 2.6))
    return 0.83 + 0.11 * s


class Builder:
    # One bmesh for the whole section; pieces are added in Blender metres. Every vertex gets a colour (layer "Col")
    # that the UE material multiplies in: a tint per piece, grime towards the piece's foot and a slow wash of light
    # and dark over the world, so neighbouring blocks don't read as one flat print. Each piece also shifts its UVs
    # by a random amount, so the 2 m texture doesn't line up from block to block.
    def __init__(self):
        self.bm = bmesh.new()
        self.tone, self.z0, self.z1, self.uv = (1.0, 1.0, 1.0), 0.0, 1.0, (0.0, 0.0)
        self.gears = []     # (centre, normal, radius, tone) of the great wall gears, built as their own meshes
        self.lamps = None   # a second Builder for the hanging lamps (set by main)

    def begin(self, row, z0, z1):
        rng = random.Random(zlib.crc32(row["label"].encode("utf-8")))
        self.tone = rng.choice(TONES)
        self.z0, self.z1 = z0, z1
        self.uv = (rng.random(), rng.random())

    def shade(self, slot, c):
        if slot in KEEP:
            return (1.0, 1.0, 1.0, 1.0)
        h = self.z1 - self.z0
        t = min(1.0, max(0.0, (c.z - self.z0) / h)) if h > 1e-3 else 1.0
        foot = 0.3 + 0.7 * t ** 0.7 if h > 2.0 else 0.85                      # dark, damp foot; lighter up high
        wash = 0.85 + 0.25 * math.sin(c.x * 0.41 + c.z * 0.23) * math.cos(c.y * 0.37 - c.z * 0.17)
        wash *= stain(c.x, c.y, c.z)
        tone = self.tone
        if slot not in (S["Masonry"], S["Flagstone"], S["Glyph"]):            # metal: half the tint, less grime
            tone = tuple(0.5 + 0.5 * v for v in tone)
            foot = 0.7 + 0.3 * foot
        return tuple(min(1.0, v * foot * wash) for v in tone) + (1.0,)

    def box(self, x0, x1, y0, y1, z0, z1, side, top=None, bottom=None, bevel=0.0):
        if x1 - x0 < 1e-4 or y1 - y0 < 1e-4 or z1 - z0 < 1e-4:
            return
        new = bmesh.new()
        bmesh.ops.create_cube(new, size=1.0)
        for v in new.verts:
            v.co.x = x0 if v.co.x < 0 else x1
            v.co.y = y0 if v.co.y < 0 else y1
            v.co.z = z0 if v.co.z < 0 else z1
        if bevel > 0.0:
            limit = min(x1 - x0, y1 - y0, z1 - z0) * 0.3
            bmesh.ops.bevel(new, geom=list(new.edges), offset=min(bevel, limit), segments=2, profile=0.5, affect="EDGES")
        # Big faces are cut into ~1.3 m cells so the vertex colour can carry stains across them, not just one tint.
        for axis, lo, hi in ((0, x0, x1), (1, y0, y1), (2, z0, z1)):
            n = int((hi - lo) / CELL)
            for k in range(1, n):
                co = [0.0, 0.0, 0.0]
                no = [0.0, 0.0, 0.0]
                co[axis], no[axis] = lo + k * (hi - lo) / n, 1.0
                geom = list(new.verts) + list(new.edges) + list(new.faces)
                bmesh.ops.bisect_plane(new, geom=geom, plane_co=co, plane_no=no)
        self.take(new, side, top if top is not None else side, bottom if bottom is not None else side)

    def take(self, new, side, top, bottom):
        uv = new.loops.layers.uv.new("UVMap")
        col = new.loops.layers.color.new("Col")
        ou, ov = self.uv
        for face in new.faces:
            n = face.normal
            face.material_index = top if n.z > 0.7 else (bottom if n.z < -0.7 else side)
            tile = FLOOR_TILE if face.material_index == S["Flagstone"] else TILE
            for loop in face.loops:
                c = loop.vert.co
                if abs(n.z) > 0.7:
                    loop[uv].uv = (c.x / tile + ou, c.y / tile + ov)
                elif abs(n.x) > abs(n.y):
                    loop[uv].uv = (c.y / TILE + ou, c.z / TILE + ov)
                else:
                    loop[uv].uv = (c.x / TILE + ou, c.z / TILE + ov)
                loop[col] = self.shade(face.material_index, c)
        self.merge(new)

    def merge(self, new):
        mesh = bpy.data.meshes.new("piece")
        new.to_mesh(mesh)
        new.free()
        self.bm.from_mesh(mesh)
        bpy.data.meshes.remove(mesh)

    def tube(self, a, b, r, slot, segments=12, cap_slot=None, r_end=None):
        # A cylinder from point a to point b (metres), any direction; with r_end, a cone or frustum (radius r at a).
        a, b = Vector(a), Vector(b)
        axis = b - a
        length = axis.length
        if length < 1e-4:
            return
        axis.normalize()
        helper = Vector((0.0, 0.0, 1.0)) if abs(axis.z) < 0.9 else Vector((1.0, 0.0, 0.0))
        u = axis.cross(helper).normalized()
        w = axis.cross(u)
        new = bmesh.new()
        lo, hi = [], []
        for i in range(segments):
            ang = 2.0 * math.pi * (i + 0.5) / segments
            ring = u * math.cos(ang) + w * math.sin(ang)
            lo.append(new.verts.new(a + ring * r))
            hi.append(new.verts.new(b + ring * (r if r_end is None else r_end)))
        sides = [new.faces.new((lo[i], lo[(i + 1) % segments], hi[(i + 1) % segments], hi[i])) for i in range(segments)]
        caps = [new.faces.new(list(reversed(lo))), new.faces.new(hi)]
        bmesh.ops.recalc_face_normals(new, faces=new.faces)
        uvl = new.loops.layers.uv.new("UVMap")
        col = new.loops.layers.color.new("Col")
        ou, ov = self.uv
        for k, face in enumerate(sides):
            face.material_index = slot
            for loop in face.loops:
                idx = lo.index(loop.vert) if loop.vert in lo else hi.index(loop.vert)
                seam_fix = segments if (k == segments - 1 and idx == 0) else idx
                t = 0.0 if loop.vert in lo else length
                loop[uvl].uv = (seam_fix * 2.0 * math.pi * r / segments / TILE + ou, t / TILE + ov)
                loop[col] = self.shade(slot, loop.vert.co)
        for face in caps:
            face.material_index = slot if cap_slot is None else cap_slot
            for loop in face.loops:
                c = loop.vert.co - a
                loop[uvl].uv = (c.dot(u) / TILE + ou, c.dot(w) / TILE + ov)
                loop[col] = self.shade(face.material_index, loop.vert.co)
        self.merge(new)

    def cylinder(self, cx, cy, z0, z1, r, slot, segments=24, top=None):
        self.tube((cx, cy, z0), (cx, cy, z1), r, slot, segments, top)

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
            material = bpy.data.materials.get("M_Tower" + slot) or bpy.data.materials.new("M_Tower" + slot)
            obj.data.materials.append(material)
        return obj


def bounds(row):
    (x0, y0, z0), (x1, y1, z1) = row["min"], row["max"]
    a, b = to_blender(x0, y0, z0), to_blender(x1, y1, z1)
    return min(a[0], b[0]), max(a[0], b[0]), min(a[1], b[1]), max(a[1], b[1]), a[2], b[2]


def role(label):
    return label.split(" ", 2)[-1].rstrip("0123456789 ").strip()


def heights(z0, z1, start, step, low_margin, high_margin):
    # World heights BASE + start + k * step that fit inside [z0 + low_margin, z1 - high_margin].
    out = []
    k = math.ceil((z0 + low_margin - BASE - start) / step)
    while BASE + start + k * step <= z1 - high_margin:
        out.append(BASE + start + k * step)
        k += 1
    return out


# ----- pieces -----
def ribs(b, x0, x1, y0, y1, z0, z1, spacing=3.6, min_len=5.0):
    # Riveted iron ribs up every long face, a verdigris pipe beside every other one.
    if z1 - z0 < 3.0:
        return
    for along, lo, hi, fixed, sign in (("x", x0, x1, y0, -1), ("x", x0, x1, y1, 1), ("y", y0, y1, x0, -1), ("y", y0, y1, x1, 1)):
        length = hi - lo
        if length < min_len:
            continue
        n = int(length // spacing)
        for i in range(n):
            c = lo + (i + 0.5) * length / n
            o0, o1 = (fixed - 0.12, fixed) if sign < 0 else (fixed, fixed + 0.12)
            if along == "x":
                b.box(c - 0.2, c + 0.2, o0, o1, z0, z1 - 0.1, S["Iron"], bevel=0.02)
            else:
                b.box(o0, o1, c - 0.2, c + 0.2, z0, z1 - 0.1, S["Iron"], bevel=0.02)
            if i % 2 == 0 and z1 - z0 > 4.0:
                p = c + 0.6
                off = fixed + sign * 0.11
                a = (p, off, z0 + 0.45) if along == "x" else (off, p, z0 + 0.45)
                e = (p, off, z1 - 0.6) if along == "x" else (off, p, z1 - 0.6)
                b.tube(a, e, 0.07, S["Bronze"], 10)
                # clamps holding it to the stone
                for zc in heights(z0, z1, 1.0, 3.0, 0.8, 0.8):
                    if along == "x":
                        b.box(p - 0.1, p + 0.1, min(fixed, off), max(fixed, off) + (0.0 if sign < 0 else 0.02), zc, zc + 0.08, S["Iron"])
                    else:
                        b.box(min(fixed, off), max(fixed, off) + (0.0 if sign < 0 else 0.02), p - 0.1, p + 0.1, zc, zc + 0.08, S["Iron"])


def gear_relief(b, centre, normal, radius):
    # A great gear set into the stone face: rim, teeth, spokes and hub, all standing a little out along `normal`.
    centre, normal = Vector(centre), Vector(normal)
    u = normal.cross(Vector((0.0, 0.0, 1.0))).normalized()
    v = Vector((0.0, 0.0, 1.0))
    back, front = centre + normal * 0.06, centre + normal * 0.2
    b.tube(back, front, radius, S["Iron"], 48)
    b.tube(back, front + normal * 0.01, radius * 0.78, S["Glyph"], 48)
    teeth = int(radius * 9)
    for k in range(teeth):
        a = 2.0 * math.pi * k / teeth
        d = u * math.cos(a) + v * math.sin(a)
        b.tube(centre + normal * 0.13 + d * (radius - 0.05), centre + normal * 0.13 + d * (radius + 0.28), 0.12, S["Iron"], 4)
    for k in range(6):
        a = 2.0 * math.pi * k / 6.0 + 0.3
        d = u * math.cos(a) + v * math.sin(a)
        b.tube(centre + normal * 0.23 + d * radius * 0.2, centre + normal * 0.23 + d * radius * 0.8, 0.1, S["Bronze"], 6)
    b.tube(back, front + normal * 0.1, radius * 0.22, S["Bronze"], 24)
    b.tube(front, front + normal * 0.16, radius * 0.08, S["Iron"], 12)


def gears(b, x0, x1, y0, y1, z0, z1):
    # One great gear on each broad, tall face, two-thirds of the way up.
    h = z1 - z0
    if h < 8.0:
        return
    r = min(2.6, h * 0.18)
    zc = z0 + h * 0.62
    for along, lo, hi, fixed, sign in (("x", x0, x1, y0, -1), ("x", x0, x1, y1, 1), ("y", y0, y1, x0, -1), ("y", y0, y1, x1, 1)):
        if hi - lo < 4.0 * r:
            continue
        c = (lo + hi) / 2.0
        # Not drawn into the section: each gear becomes its own mesh that turns in UE (build_gears below).
        if along == "x":
            b.gears.append(((c, fixed, zc), (0.0, sign, 0.0), r, b.tone))
        else:
            b.gears.append(((fixed, c, zc), (sign, 0.0, 0.0), r, b.tone))
        # a dark iron socket ring in the stone behind it, so the turning gear sits in something
        centre, normal = Vector(b.gears[-1][0]), Vector(b.gears[-1][1])
        b.tube(centre, centre + normal * 0.05, r + 0.4, S["Iron"], 48)
        b.tube(centre, centre + normal * 0.055, r * 0.8, S["Shadow"], 48)


def glyph_bands(b, x0, x1, y0, y1, z0, z1):
    # Glowing glyph friezes at fixed world heights, with thin bronze lines over and under.
    for zb in heights(z0, z1, 2.0, 6.0, 1.0, 1.2):
        b.box(x0 - 0.02, x1 + 0.02, y0 - 0.02, y1 + 0.02, zb, zb + 0.6, S["Glyph"])
        for za in (zb - 0.06, zb + 0.6):
            b.box(x0 - 0.04, x1 + 0.04, y0 - 0.04, y1 + 0.04, za, za + 0.06, S["Bronze"])


def wall_piece(b, x0, x1, y0, y1, z0, z1):
    w, d, h = x1 - x0, y1 - y0, z1 - z0
    top = S["Flagstone"] if min(w, d) >= 2.5 else S["Masonry"]
    b.box(x0, x1, y0, y1, z0, z1, S["Masonry"], top, bevel=0.04)
    if h < 1.2:
        return
    out = 0.06
    b.box(x0 - out, x1 + out, y0 - out, y1 + out, z0, z0 + min(0.45, h * 0.2), S["Masonry"], bevel=0.03)
    if h > 2.0:
        b.box(x0 - 0.05, x1 + 0.05, y0 - 0.05, y1 + 0.05, z1 - 0.32, z1 - 0.18, S["Bronze"], bevel=0.015)
    glyph_bands(b, x0, x1, y0, y1, z0, z1)
    ribs(b, x0, x1, y0, y1, z0, z1)
    gears(b, x0, x1, y0, y1, z0, z1)


def room_floor(b, x0, x1, y0, y1, z0, z1):
    b.box(x0, x1, y0, y1, z0, z1, S["Masonry"], S["Flagstone"], bevel=0.03)
    # An inlaid machine seal in the middle: bronze, a glyph ring, a bronze hub (each a little above the last).
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    r = min(3.0, min(x1 - x0, y1 - y0) * 0.15)
    b.cylinder(cx, cy, z1 - 0.02, z1 + 0.01, r, S["Bronze"], 48)
    b.cylinder(cx, cy, z1 - 0.02, z1 + 0.016, r * 0.88, S["Glyph"], 48)
    b.cylinder(cx, cy, z1 - 0.02, z1 + 0.022, r * 0.3, S["Bronze"], 32)
    for k in range(12):
        a = 2.0 * math.pi * k / 12.0
        b.tube((cx + r * 0.3 * math.cos(a), cy + r * 0.3 * math.sin(a), z1 + 0.012),
               (cx + r * 0.86 * math.cos(a), cy + r * 0.86 * math.sin(a), z1 + 0.012), 0.04, S["Bronze"], 6)


def ceiling(b, x0, x1, y0, y1, z0, z1):
    b.box(x0, x1, y0, y1, z0, z1, S["Masonry"], S["Masonry"], S["Iron"], bevel=0.03)
    # Iron beams under it, across the short way, and one down the middle.
    w, d = x1 - x0, y1 - y0
    if w >= d:
        n = max(1, int(w // 4.0))
        for i in range(1, n):
            c = x0 + i * w / n
            b.box(c - 0.2, c + 0.2, y0, y1, z0 - 0.35, z0, S["Iron"], bevel=0.02)
        b.box(x0, x1, (y0 + y1) / 2.0 - 0.25, (y0 + y1) / 2.0 + 0.25, z0 - 0.25, z0, S["Iron"], bevel=0.02)
    else:
        n = max(1, int(d // 4.0))
        for i in range(1, n):
            c = y0 + i * d / n
            b.box(x0, x1, c - 0.2, c + 0.2, z0 - 0.35, z0, S["Iron"], bevel=0.02)
        b.box((x0 + x1) / 2.0 - 0.25, (x0 + x1) / 2.0 + 0.25, y0, y1, z0 - 0.25, z0, S["Iron"], bevel=0.02)


def roof(b, x0, x1, y0, y1, z0, z1):
    b.box(x0, x1, y0, y1, z0, z1, S["Masonry"], S["Flagstone"], S["Iron"], bevel=0.03)
    b.box(x0 - 0.03, x1 + 0.03, y0 - 0.03, y1 + 0.03, z1 - 0.16, z1 - 0.06, S["Bronze"], bevel=0.01)


def slab(b, x0, x1, y0, y1, z0, z1):
    # A stone landing: flagstone to stand on, a bronze band round it, bronze caps on the corners.
    h = z1 - z0
    b.box(x0, x1, y0, y1, z0, z1, S["Masonry"], S["Flagstone"], bevel=0.03)
    if h >= 0.3:
        b.box(x0 - 0.03, x1 + 0.03, y0 - 0.03, y1 + 0.03, z1 - 0.14, z1 - 0.05, S["Bronze"], bevel=0.01)
    if h > 0.8:
        b.box(x0 + 0.05, x1 - 0.05, y0 + 0.05, y1 - 0.05, z0 - 0.01, z0 + 0.05, S["Iron"])
    c = 0.16
    for xa, xb in ((x0 - 0.02, x0 + c), (x1 - c, x1 + 0.02)):
        for ya, yb in ((y0 - 0.02, y0 + c), (y1 - c, y1 + 0.02)):
            b.box(xa, xb, ya, yb, z1 - min(0.25, h * 0.6), z1 + 0.01, S["Bronze"], bevel=0.015)
    if h > 2.0:
        glyph_bands(b, x0, x1, y0, y1, z0, z1)


def bracket(b, x0, x1, y0, y1, z0, z1):
    h = z1 - z0
    b.box(x0, x1, y0, y1, z0, z1, S["Iron"], bevel=0.02)
    c = 0.12
    for xa, xb in ((x0 - 0.02, x0 + c), (x1 - c, x1 + 0.02)):
        for ya, yb in ((y0 - 0.02, y0 + c), (y1 - c, y1 + 0.02)):
            b.box(xa, xb, ya, yb, z1 - min(0.15, h * 0.6), z1 + 0.01, S["Bronze"], bevel=0.01)


def ibeam(b, x0, x1, y0, y1, z0, z1):
    # An I-beam along its long side: flanges top and bottom, a web, stiffeners.
    t = min(0.08, (z1 - z0) * 0.2)
    b.box(x0, x1, y0, y1, z1 - t, z1, S["Iron"], bevel=0.01)
    b.box(x0, x1, y0, y1, z0, z0 + t, S["Iron"], bevel=0.01)
    along_x = (x1 - x0) >= (y1 - y0)
    if along_x:
        cy, half = (y0 + y1) / 2.0, (y1 - y0) * 0.15
        b.box(x0, x1, cy - half, cy + half, z0 + t, z1 - t, S["Iron"])
        n = max(1, int((x1 - x0) // 1.2))
        for i in range(n + 1):
            c = x0 + 0.03 + i * (x1 - x0 - 0.06) / n
            b.box(c - 0.015, c + 0.015, y0 + 0.02, y1 - 0.02, z0 + t, z1 - t, S["Iron"])
    else:
        cx, half = (x0 + x1) / 2.0, (x1 - x0) * 0.15
        b.box(cx - half, cx + half, y0, y1, z0 + t, z1 - t, S["Iron"])
        n = max(1, int((y1 - y0) // 1.2))
        for i in range(n + 1):
            c = y0 + 0.03 + i * (y1 - y0 - 0.06) / n
            b.box(x0 + 0.02, x1 - 0.02, c - 0.015, c + 0.015, z0 + t, z1 - t, S["Iron"])


def girder(b, x0, x1, y0, y1, z0, z1):
    # A lattice mast: four corner angles, X bracing on every face.
    c = 0.07
    for xa in (x0, x1 - c):
        for ya in (y0, y1 - c):
            b.box(xa, xa + c, ya, ya + c, z0, z1, S["Iron"])
    h = z1 - z0
    n = max(1, int(h // 1.0))
    xi0, xi1, yi0, yi1 = x0 + c / 2.0, x1 - c / 2.0, y0 + c / 2.0, y1 - c / 2.0
    for k in range(n):
        za, zb = z0 + k * h / n, z0 + (k + 1) * h / n
        if k % 2:
            za, zb = zb, za
        b.tube((xi0, yi0, za), (xi1, yi0, zb), 0.018, S["Iron"], 4)
        b.tube((xi1, yi1, za), (xi0, yi1, zb), 0.018, S["Iron"], 4)
        b.tube((xi0, yi1, za), (xi0, yi0, zb), 0.018, S["Iron"], 4)
        b.tube((xi1, yi0, za), (xi1, yi1, zb), 0.018, S["Iron"], 4)


def wall_stone(b, x0, x1, y0, y1, z0, z1):
    # Old stone with an iron plate bolted on top.
    b.box(x0, x1, y0, y1, z0, z1 - 0.08, S["Masonry"], bevel=0.03)
    b.box(x0 - 0.02, x1 + 0.02, y0 - 0.02, y1 + 0.02, z1 - 0.08, z1, S["Iron"], bevel=0.01)


def column(b, x0, x1, y0, y1, z0, z1):
    cx, cy, r = (x0 + x1) / 2.0, (y0 + y1) / 2.0, min(x1 - x0, y1 - y0) / 2.0
    b.cylinder(cx, cy, z0, z1, r, S["Masonry"], 8)
    for zb in heights(z0, z1, 1.5, 3.0, 0.5, 0.5):
        b.cylinder(cx, cy, zb, zb + 0.3, r * 1.1, S["Iron"], 8)
    b.cylinder(cx, cy, z1 - 0.3, z1, r * 1.25, S["Bronze"], 16)


def pillar(b, x0, x1, y0, y1, z0, z1):
    # A tall stone pier caged in iron: corner angles and bands.
    b.box(x0 + 0.05, x1 - 0.05, y0 + 0.05, y1 - 0.05, z0, z1, S["Masonry"], bevel=0.03)
    c = min(0.25, (x1 - x0) * 0.2)
    for xa, xb in ((x0 - 0.02, x0 + c), (x1 - c, x1 + 0.02)):
        for ya, yb in ((y0 - 0.02, y0 + c), (y1 - c, y1 + 0.02)):
            b.box(xa, xb, ya, yb, z0, z1, S["Iron"], bevel=0.015)
    for zb in heights(z0, z1, 1.0, 2.0, 0.5, 0.5):
        b.box(x0, x1, y0, y1, zb, zb + 0.2, S["Iron"], bevel=0.01)
    b.box(x0 - 0.04, x1 + 0.04, y0 - 0.04, y1 + 0.04, z1 - 0.2, z1 + 0.01, S["Bronze"], bevel=0.015)


def brass_piece(b, x0, x1, y0, y1, z0, z1):
    b.box(x0, x1, y0, y1, z0, z1, S["Brass"], bevel=0.03)
    b.box(x0 - 0.02, x1 + 0.02, y0 - 0.02, y1 + 0.02, z0, z0 + min(0.06, (z1 - z0) * 0.3), S["Iron"], bevel=0.01)


def dark_door(b, x0, x1, y0, y1, z0, z1):
    b.box(x0, x1, y0, y1, z0, z1, S["Shadow"])
    f, out = 0.12, 0.04
    along_x = (x1 - x0) >= (y1 - y0)
    if along_x:
        for xa, xb in ((x0 - f, x0), (x1, x1 + f)):
            b.box(xa, xb, y0 - out, y1 + out, z0, z1 + f, S["Bronze"], bevel=0.015)
        b.box(x0 - f, x1 + f, y0 - out, y1 + out, z1, z1 + f, S["Bronze"], bevel=0.015)
    else:
        for ya, yb in ((y0 - f, y0), (y1, y1 + f)):
            b.box(x0 - out, x1 + out, ya, yb, z0, z1 + f, S["Bronze"], bevel=0.015)
        b.box(x0 - out, x1 + out, y0 - f, y1 + f, z1, z1 + f, S["Bronze"], bevel=0.015)


def chain(b, a, e, link=0.075, width=0.04, wire=0.008):
    # Iron chain from a to e: flat oval links, each turned 90 degrees from the last.
    a, e = Vector(a), Vector(e)
    axis = e - a
    length = axis.length
    if length < 1e-3:
        return
    axis.normalize()
    helper = Vector((0.0, 0.0, 1.0)) if abs(axis.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    side = axis.cross(helper).normalized()
    sides = (side, axis.cross(side).normalized())
    n = max(1, int(length / (link * 0.8)))
    for i in range(n):
        c = a + axis * (length * (i + 0.5) / n)
        p = sides[i % 2] * (width / 2.0)
        h = axis * (link / 2.0)
        corners = (c - h - p, c + h - p, c + h + p, c - h + p)
        for k in range(4):
            b.tube(corners[k], corners[(k + 1) % 4], wire, S["Iron"], 4)


def lantern(b, x0, x1, y0, y1, z0, z1, hang_to=None, arm_from=None):
    # An ancient machine lamp in place of the bulb: a bronze fire bowl with a glyph band, a cluster of glowing
    # crystals growing out of it and three bronze prongs round them, hung on three chains that meet in a ring above
    # the lamp's PointLight (left where it is, ~0.4 m over the box) and go on up to the ceiling as one chain.
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    zb, zr = z0 - 0.05, z0 + 0.18           # bowl foot and rim
    r_foot, r_rim = 0.12, 0.36

    def r_at(z):
        return r_foot + (r_rim - r_foot) * (z - zb) / (zr - zb)

    b.tube((cx, cy, zb - 0.06), (cx, cy, zb), 0.03, S["Bronze"], 8, r_end=0.07)                  # finial under it
    b.tube((cx, cy, zb), (cx, cy, zr), r_foot, S["Bronze"], 20, r_end=r_rim)
    za, zc = z0 + 0.03, z0 + 0.11
    b.tube((cx, cy, za), (cx, cy, zc), r_at(za) + 0.012, S["Glyph"], 20, r_end=r_at(zc) + 0.012)  # glowing band
    b.cylinder(cx, cy, zr - 0.02, zr + 0.025, r_rim + 0.025, S["Iron"], 20)                       # rim
    b.cylinder(cx, cy, zr + 0.025, zr + 0.035, r_rim - 0.03, S["Ember"], 20)                       # embers
    # crystals: one tall, five leaning round it
    rng = random.Random(int(cx * 100) * 7919 + int(cy * 100))
    base = Vector((cx, cy, zr + 0.02))
    b.tube(base, base + Vector((0.0, 0.0, 0.3)), 0.075, S["Ember"], 6, r_end=0.005)
    for k in range(5):
        ang = 2.0 * math.pi * k / 5.0 + rng.uniform(-0.3, 0.3)
        foot = base + Vector((math.cos(ang) * 0.12, math.sin(ang) * 0.12, 0.0))
        tip = foot + Vector((math.cos(ang) * 0.1, math.sin(ang) * 0.1, rng.uniform(0.12, 0.2)))
        b.tube(foot, tip, rng.uniform(0.035, 0.05), S["Ember"], 6, r_end=0.004)
    # prongs curling up round the crystals
    for k in range(3):
        ang = 2.0 * math.pi * (k + 0.5) / 3.0
        d = Vector((math.cos(ang), math.sin(ang), 0.0))
        p0 = base + d * (r_rim - 0.02)
        p1 = base + d * (r_rim + 0.04) + Vector((0.0, 0.0, 0.14))
        p2 = base + d * (r_rim - 0.08) + Vector((0.0, 0.0, 0.26))
        b.tube(p0, p1, 0.018, S["Bronze"], 6)
        b.tube(p1, p2, 0.018, S["Bronze"], 6, r_end=0.006)
    # three chains to a ring above the light, then one chain up
    apex = Vector((cx, cy, z0 + 1.0))
    for k in range(3):
        ang = 2.0 * math.pi * k / 3.0
        chain(b, (cx + math.cos(ang) * r_rim, cy + math.sin(ang) * r_rim, zr + 0.02), apex)
    b.cylinder(cx, cy, apex.z - 0.02, apex.z + 0.03, 0.05, S["Bronze"], 12)
    hung = hang_to is not None and hang_to > apex.z + 0.1
    if hung:
        chain(b, apex + Vector((0.0, 0.0, 0.03)), (cx, cy, hang_to))
        b.cylinder(cx, cy, hang_to - 0.04, hang_to, 0.12, S["Bronze"], 12)                        # ceiling rose
    elif arm_from is not None:
        # no ceiling: an iron arm out of the nearest wall or column, with a brace under it and a bronze plate
        (wx, wy, wz), out = arm_from
        wall = Vector((wx, wy, wz))
        hook = Vector((cx, cy, wz))
        chain(b, apex + Vector((0.0, 0.0, 0.03)), hook)
        b.tube(wall, hook + out * 0.08, 0.035, S["Iron"], 8)
        b.tube(wall - Vector((0.0, 0.0, 0.5)), wall + (hook - wall) * 0.6, 0.022, S["Iron"], 6)
        b.tube(hook + out * 0.08, hook + out * 0.08 - Vector((0.0, 0.0, 0.07)), 0.03, S["Bronze"], 8, r_end=0.005)
        b.tube(wall - out * 0.01, wall + out * 0.03, 0.16, S["Bronze"], 6)
        b.tube(wall - Vector((0.0, 0.0, 0.5)) - out * 0.01, wall - Vector((0.0, 0.0, 0.5)) + out * 0.03, 0.08, S["Bronze"], 6)
    else:
        # nothing to hang from nearby: a long chain up into the dark, as if from somewhere far above
        chain(b, apex + Vector((0.0, 0.0, 0.03)), (cx, cy, apex.z + 8.0))


def axle(b, x0, x1, y0, y1, z0, z1):
    cx, cy, r = (x0 + x1) / 2.0, (y0 + y1) / 2.0, min(x1 - x0, y1 - y0) / 2.0
    b.cylinder(cx, cy, z0, z1, r, S["Iron"], 12)
    for zb in heights(z0, z1, 0.5, 2.0, 0.3, 0.3):
        b.cylinder(cx, cy, zb, zb + 0.12, r * 1.4, S["Bronze"], 12)
    b.cylinder(cx, cy, z1 - 0.12, z1, r * 1.4, S["Bronze"], 12)


def cable(b, row):
    # A gondola cable: a thin cylinder turned along its rotation (UE's make_rot_from_z).
    roll, pitch, yaw = (math.radians(v) for v in row["rotation"])
    sp, cp, sy, cy, sr, cr = math.sin(pitch), math.cos(pitch), math.sin(yaw), math.cos(yaw), math.sin(roll), math.cos(roll)
    up = (-(cr * sp * cy + sr * sy), cy * sr - cr * sp * sy, cr * cp)
    half = row["scale"][2] * 50.0
    lx, ly, lz = row["location"]
    a = to_blender(lx - up[0] * half, ly - up[1] * half, lz - up[2] * half)
    e = to_blender(lx + up[0] * half, ly + up[1] * half, lz + up[2] * half)
    b.tube(a, e, row["scale"][0] * 0.5, S["Iron"], 8)


def ceiling_above(rows, row):
    # The underside of the nearest solid box straight above a lamp, within 8 m (metres), or None.
    (x0, y0, _), (x1, y1, z1) = row["min"], row["max"]
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    best = None
    for other in rows:
        if other is row or other["class"] != "StaticMeshActor" or not (other["mesh"] or "").endswith("/Cube.Cube"):
            continue
        (ox0, oy0, oz0), (ox1, oy1, _) = other["min"], other["max"]
        if ox0 <= cx <= ox1 and oy0 <= cy <= oy1 and oz0 >= z1 and (best is None or oz0 < best):
            best = oz0
    if best is None or best - z1 > 800.0:
        return None
    return best / 100.0


def support_beside(rows, row, z, reach=300.0):
    # For a lamp with no ceiling over it: the nearest point (metres, Blender) on the side of a solid box or column
    # that spans height z (metres) within `reach` cm of the lamp, and the outward direction there; else None.
    (x0, y0, _), (x1, y1, _) = row["min"], row["max"]
    cx, cy, zc = (x0 + x1) / 2.0, (y0 + y1) / 2.0, z * 100.0
    best = None
    for other in rows:
        mesh = other["mesh"] or ""
        if other is row or other["class"] != "StaticMeshActor" or role(other["label"]) == "Lamp":
            continue
        if not (mesh.endswith("/Cube.Cube") or mesh.endswith("/Cylinder.Cylinder")):
            continue
        (ox0, oy0, oz0), (ox1, oy1, oz1) = other["min"], other["max"]
        if not oz0 + 30.0 <= zc <= oz1 - 30.0:
            continue
        px, py = min(max(cx, ox0), ox1), min(max(cy, oy0), oy1)
        d = math.hypot(cx - px, cy - py)
        if 1.0 < d <= reach and (best is None or d < best[0]):
            best = (d, px, py)
    if best is None:
        return None
    _, px, py = best
    return to_blender(px, py, zc), Vector(((cx - px), -(cy - py), 0.0)).normalized()


def sink_shared_tops(rows):
    # Where two boxes' tops are at the same height and overlap (F's roof slabs over the tower walls), the two top
    # faces would fight. The lower-priority box (a wall under a roof or floor) gets a copy with its top 2 cm lower,
    # hidden under the other; the collision box in the level keeps the real height. Returns {label: copy}.
    def rank(row):
        return 1 if role(row["label"]) in ("Roof", "Room Ceiling") or row["material"] == "MI_TowerFloor" else 0

    boxes = [r for r in rows if r["class"] == "StaticMeshActor" and not r["hidden"] and (r["mesh"] or "").endswith("/Cube.Cube")]
    sunk = {}
    for i, p in enumerate(boxes):
        for q in boxes[i + 1:]:
            if abs(p["max"][2] - q["max"][2]) > 2.0:
                continue
            if min(p["max"][0], q["max"][0]) - max(p["min"][0], q["min"][0]) <= 1.0:
                continue
            if min(p["max"][1], q["max"][1]) - max(p["min"][1], q["min"][1]) <= 1.0:
                continue
            low = p if rank(p) < rank(q) else q
            sunk[low["label"]] = dict(low, max=[low["max"][0], low["max"][1], low["max"][2] - 2.0])
    return sunk


def dress(b, row, rows):
    x0, x1, y0, y1, z0, z1 = bounds(row)
    name, material, mesh = role(row["label"]), row["material"], row["mesh"] or ""
    w, d, h = x1 - x0, y1 - y0, z1 - z0
    if name == "Cable":
        cable(b, row)
    elif name == "Lamp" or material == "MI_RuinsEmber":
        # into the section's lamp mesh: its chains pass right by the PointLight, so in UE it casts no shadow
        b.lamps.uv = b.uv
        above = ceiling_above(rows, row)
        lantern(b.lamps, x0, x1, y0, y1, z0, z1, above,
                None if above is not None else support_beside(rows, row, z0 + 1.25))
    elif mesh.endswith("/Cylinder.Cylinder"):
        axle(b, x0, x1, y0, y1, z0, z1)
    elif material == "MI_TowerWall":
        if name == "Room Ceiling":
            ceiling(b, x0, x1, y0, y1, z0, z1)
        elif name == "Roof":
            roof(b, x0, x1, y0, y1, z0, z1)
        else:
            wall_piece(b, x0, x1, y0, y1, z0, z1)
    elif material == "MI_TowerFloor":
        if name == "Room Floor":
            room_floor(b, x0, x1, y0, y1, z0, z1)
        else:
            slab(b, x0, x1, y0, y1, z0, z1)
    elif material == "MI_MachineIron":
        if name == "Girder":
            girder(b, x0, x1, y0, y1, z0, z1)
        elif "Beam" in name:
            ibeam(b, x0, x1, y0, y1, z0, z1)
        elif name == "Wall Stone":
            wall_stone(b, x0, x1, y0, y1, z0, z1)
        elif name == "Column":
            column(b, x0, x1, y0, y1, z0, z1)
        elif h > 3.0 and min(w, d) >= 1.0:
            pillar(b, x0, x1, y0, y1, z0, z1)
        else:
            bracket(b, x0, x1, y0, y1, z0, z1)
    elif material == "MI_MachineBrass":
        brass_piece(b, x0, x1, y0, y1, z0, z1)
    elif material == "MI_MachineShadow":
        dark_door(b, x0, x1, y0, y1, z0, z1)
    else:
        b.box(x0, x1, y0, y1, z0, z1, S["Masonry"], bevel=0.03)
    return name


# ===================================================================================================== preview
def preview(obj, rows, letter, out, eye, look):
    # Simple node materials (colour, normal, glow), a dusk sun and the lamps, one Eevee frame.
    for slot in SLOTS:
        mat = bpy.data.materials["M_Tower" + slot]
        mat.use_nodes = True
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        bsdf = nodes.get("Principled BSDF")
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(os.path.join(TEX_DIR, "T_Tower" + slot + "_C.png"))
        vcol = nodes.new("ShaderNodeVertexColor")
        vcol.layer_name = "Col"
        mix = nodes.new("ShaderNodeVectorMath")
        mix.operation = "MULTIPLY"
        links.new(tex.outputs["Color"], mix.inputs[0])
        links.new(vcol.outputs["Color"], mix.inputs[1])
        links.new(mix.outputs[0], bsdf.inputs["Base Color"])
        normal_path = os.path.join(TEX_DIR, "T_Tower" + slot + "_N.png")
        if os.path.exists(normal_path):
            ntex = nodes.new("ShaderNodeTexImage")
            ntex.image = bpy.data.images.load(normal_path)
            ntex.image.colorspace_settings.name = "Non-Color"
            nmap = nodes.new("ShaderNodeNormalMap")
            links.new(ntex.outputs["Color"], nmap.inputs["Color"])
            links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
        mask_path = os.path.join(TEX_DIR, "T_Tower" + slot + "_E.png")
        if os.path.exists(mask_path):
            mtex = nodes.new("ShaderNodeTexImage")
            mtex.image = bpy.data.images.load(mask_path)
            mtex.image.colorspace_settings.name = "Non-Color"
            links.new(mtex.outputs["Color"], bsdf.inputs["Emission Strength"])
            bsdf.inputs["Emission Color"].default_value = (1.0, 0.45, 0.12, 1.0)
            bsdf.inputs["Emission Strength"].default_value = 1.0
            if slot == "Glyph":
                mul = nodes.new("ShaderNodeMath")
                mul.operation = "MULTIPLY"
                mul.inputs[1].default_value = 3.0
                links.new(mtex.outputs["Color"], mul.inputs[0])
                links.new(mul.outputs[0], bsdf.inputs["Emission Strength"])
            else:
                bsdf.inputs["Emission Strength"].default_value = 6.0
                links.remove(bsdf.inputs["Emission Strength"].links[0])
        rough, metal = {"Iron": (0.55, 0.75), "Bronze": (0.45, 0.7), "Brass": (0.3, 1.0)}.get(slot, (0.85, 0.0))
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
    scene = bpy.context.scene
    world = bpy.data.worlds.new("Dusk")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.09, 0.08, 0.12, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6
    scene.world = world
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 2.0
    sun.data.color = (1.0, 0.6, 0.5)
    sun.rotation_euler = (math.radians(70), 0.0, math.radians(-150))
    scene.collection.objects.link(sun)
    for row in rows:
        if row["class"] == "PointLight" and row["folder"].split("/")[-1].startswith(letter + " "):
            lx, ly, lz = row["location"]
            lamp = bpy.data.objects.new("Lamp", bpy.data.lights.new("Lamp", "POINT"))
            lamp.data.energy = 3000.0
            lamp.data.color = (1.0, 0.67, 0.35)
            lamp.location = to_blender(lx, ly, lz)
            scene.collection.objects.link(lamp)
    cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    cam.data.lens = 18.0
    cam.location = to_blender(*eye)
    direction = Vector(to_blender(*look)) - Vector(to_blender(*eye))
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(cam)
    scene.camera = cam
    for engine in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.filepath = out
    bpy.ops.render.render(write_still=True)


def export(obj, name):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT_DIR, name + ".fbx"), use_selection=True, apply_unit_scale=True,
                             mesh_smooth_type="FACE", use_mesh_modifiers=False)


def build_gears(letter, gears):
    # Each great wall gear as its own mesh, pivot at its hub, turning axis = local +X (UE's too: the FBX keeps X).
    # SM_TowerGear_<letter><n>.fbx, and tower_gears_<letter>.json with where each goes in UE (cm) and its yaw, for
    # import_tower_art.py; the UE material turns them about that axis (World Position Offset), so they need no BP.
    for old in glob.glob(os.path.join(OUT_DIR, "SM_TowerGear_" + letter + "*.fbx")):
        os.remove(old)
    placed = []
    for k, (centre, normal, radius, tone) in enumerate(gears, 1):
        g = Builder()
        g.tone, g.z0, g.z1 = tone, 0.0, 0.0
        gear_relief(g, (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), radius)
        name = "SM_TowerGear_{}{}".format(letter, k)
        obj = g.finish(name)
        export(obj, name)
        obj.location = centre                                    # for the preview only (exported at the origin)
        obj.rotation_euler = (0.0, 0.0, math.atan2(normal[1], normal[0]))
        placed.append({"name": name, "location": [centre[0] * 100.0, -centre[1] * 100.0, centre[2] * 100.0],
                       "yaw": math.degrees(math.atan2(-normal[1], normal[0])), "radius": radius * 100.0})
    with open(os.path.join(OUT_DIR, "tower_gears_" + letter + ".json"), "w", encoding="utf-8") as out:
        json.dump(placed, out, indent=1)
    return "{} gears: {}".format(letter, len(placed))


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    make_textures()
    rows = json.load(open(os.path.join(OUT_DIR, "area2_layout.json"), encoding="utf-8"))
    report = []
    built = []
    sunk = sink_shared_tops(rows)
    report.append("tops sunk 2 cm under a shared top: " + ", ".join(sorted(sunk)))
    for letter in SECTIONS:
        builder = Builder()
        builder.lamps = Builder()
        kinds = {}
        for row in rows:
            section = row["folder"].split("/")[1] if "/" in row["folder"] else ""
            if not section.startswith(letter + " ") or row["class"] != "StaticMeshActor" or row["hidden"]:
                continue
            row = sunk.get(row["label"], row)
            _, _, _, _, z0, z1 = bounds(row)
            builder.begin(row, z0, z1)
            name = dress(builder, row, rows)
            kinds[name] = kinds.get(name, 0) + 1
        name = "SM_Tower_" + letter
        obj = builder.finish(name)
        built.append((letter, obj))
        export(obj, name)
        report.append("{}: {} pieces ({}), {} vertices".format(name, sum(kinds.values()), ", ".join("{} {}".format(k, v) for k, v in sorted(kinds.items())), len(obj.data.vertices)))
        report.append(build_gears(letter, builder.gears))
        lamps_path = os.path.join(OUT_DIR, "SM_TowerLamps_" + letter + ".fbx")
        if os.path.exists(lamps_path):
            os.remove(lamps_path)
        if kinds.get("Lamp"):
            lamps = builder.lamps.finish("SM_TowerLamps_" + letter)
            lamps.visible_shadow = False                # as in UE, for the preview
            export(lamps, "SM_TowerLamps_" + letter)
        else:
            builder.lamps.bm.free()
    with open(os.path.join(OUT_DIR, "tower_build.txt"), "w", encoding="utf-8") as out:
        out.write("\n".join(report) + "\n")
    print("\n".join(report))
    if PREVIEW:
        preview(built[0][1], rows, built[0][0], *PREVIEW)


main()
