# Paints the night sky's stars for area 2 (the user, 2026-11-18: "the sky a night sky, with stars if possible"):
# SourceArt/Textures/Sky/T_NightStars.png, 4096 x 2048, equirectangular (u = longitude, v = from the zenith down), for
# the inside of a big sphere (the engine sphere's UVs run that way). Black, with ~9000 stars spread evenly over the
# sphere (a few bright, most faint; blue-white to warm), a faint milky way band with its own crowd of tiny stars and
# dust lanes, and nothing below the horizon (the lower quarter fades out: it would be hidden anyway).
# setup_area2_night.py imports it. Run (Blender's Python has numpy):
#   blender --background --factory-startup --python build_night_stars.py
import math
import os

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "SourceArt", "Textures", "Sky")
W, H = 4096, 2048
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(42)
img = np.zeros((H, W, 3), dtype=np.float32)


def noise(h, w, scale, seed):
    r = np.random.default_rng(seed)
    spectrum = np.fft.fft2(r.standard_normal((h, w)))
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    spectrum *= np.exp(-(fx * fx + fy * fy) * (scale * scale) * 2.0)
    out = np.real(np.fft.ifft2(spectrum))
    out -= out.min()
    return out / max(out.max(), 1e-6)


def stamp(x, y, radius, colour):
    # A soft round star, wrapping round in u.
    r = max(1, int(math.ceil(radius * 3)))
    for dy in range(-r, r + 1):
        yy = y + dy
        if yy < 0 or yy >= H:
            continue
        for dx in range(-r, r + 1):
            xx = (x + dx) % W
            d2 = (dx * dx + dy * dy) / (radius * radius)
            img[yy, xx] += colour * math.exp(-d2 * 1.5)


def place(count, size_range, bright_range, band=False):
    for _ in range(count):
        if band:
            # along the milky way: a great circle tilted 60 degrees, scattered either side of it
            lon = rng.uniform(0.0, 2.0 * math.pi)
            off = rng.normal(0.0, 0.12)
            lat = math.asin(max(-1.0, min(1.0, math.sin(lon) * math.sin(math.radians(60.0)) + off)))
        else:
            lat = math.asin(rng.uniform(-1.0, 1.0))          # even over the sphere
            lon = rng.uniform(0.0, 2.0 * math.pi)
        x = int(lon / (2.0 * math.pi) * W) % W
        y = int((0.5 - lat / math.pi) * H)
        if not 0 <= y < H:
            continue
        b = bright_range[0] + (bright_range[1] - bright_range[0]) * rng.random() ** 6     # most faint
        hue = rng.random()
        colour = np.array([0.75 + 0.25 * hue, 0.85, 1.0 - 0.3 * hue], dtype=np.float32) * b
        # stars are squeezed near the poles in an equirect map: widen them by 1/cos(lat) in u
        stamp(x, y, rng.uniform(*size_range), colour)


# the milky way glow first, then its tiny stars, then the stars everywhere
yy, xx = np.mgrid[0:H, 0:W]
lon = xx / W * 2.0 * math.pi
lat = (0.5 - yy / H) * math.pi
band_lat = np.arcsin(np.clip(np.sin(lon) * math.sin(math.radians(60.0)), -1.0, 1.0))
glow = np.exp(-((lat - band_lat) / 0.16) ** 2)
dust = noise(H, W, 18.0, 7) * 0.6 + noise(H, W, 6.0, 8) * 0.4
lanes = np.clip((noise(H, W, 10.0, 9) - 0.45) * 3.0, 0.0, 1.0)
milky = glow * (0.35 + 0.65 * dust) * (1.0 - 0.7 * lanes) * 0.16
img += np.dstack([milky * 0.85, milky * 0.9, milky * 1.1]).astype(np.float32)
place(5000, (0.5, 0.8), (0.15, 0.6), band=True)
place(9000, (0.5, 1.0), (0.2, 1.0))
place(60, (1.2, 1.8), (1.2, 2.2))
# below the horizon: fade to nothing
fade = np.clip((lat + 0.15) / 0.25, 0.0, 1.0)
img *= fade[..., None]

image = bpy.data.images.new("T_NightStars", W, H, alpha=False)
rgba = np.ones((H, W, 4), dtype=np.float32)
rgba[:, :, :3] = np.clip(img, 0.0, 1.0)
image.pixels.foreach_set(rgba[::-1].reshape(-1))
image.filepath_raw = os.path.join(OUT, "T_NightStars.png")
image.file_format = "PNG"
image.save()
print("stars", image.filepath_raw)
