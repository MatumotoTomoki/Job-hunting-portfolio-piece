# The sky area's (area 3) route as plain data, checked jump by jump; build_area3_sky.py places it. No Unreal here, so it
# can be checked on its own:
#   python area3_layout.py          (prints the route and every jump; fails on one out of reach)
# Pieces (all heights are the top a player stands on; x, y the middle):
#   ("island", x, y, top, size)                 SM_SkyIsland, size across; footing a circle 0.48 * size
#   ("cloud", x, y, top, size)                  solid SM_SkyCloud; footing a square 0.8 * size
#   ("vanish", x, y, top, size, stay, gone)     BP_VanishCloud
#   ("mover", x, y, top, (dx, dy, dz), seconds, wait)   BP_MovingIsland (350 across)
#   ("timed", x, y, top, delay)                 BP_TimedPlatform; ("falling", x, y, top) BP_FallingFloor
#   ("marble", x0, x1, y0, y1, top, thick)      a marble block
#   ("wind", x, y, z, along, width, height, yaw, pitch, strength, max_speed, on, off, delay)  BP_WindZone (middle)
#   ("coin", x, y, top), ("flag", x, y, top), ("trap", x0, x1, y0, y1, top), ("sign", x, y, z, yaw, text)
#   ("start", x, y, top), ("lever", x, y, top, yaw), ("stair", x, y, top, size, index), ("gate", x, y, top)
import math

ISLAND_FOOT = 0.48
CLOUD_FOOT = 0.8
MOVER_SIZE = 350.0
HARD = 0.9


class Route:
    def __init__(self, base, jump_z, gravity, walk, plat):
        self.base, self.jump_z, self.gravity, self.walk, self.plat = base, jump_z, gravity, walk, plat
        self.apex = jump_z * jump_z / (2.0 * gravity)
        self.pieces = []
        self.checks = []

    # ----- what a jump can do -----
    def reach(self, rise, speed=None):
        fall = self.apex - rise
        if fall <= 0:
            return 0.0
        return (speed or self.walk) * (self.jump_z / self.gravity + math.sqrt(2.0 * fall / self.gravity))

    def jump(self, name, a, b, rise, ratio=HARD):
        g = gap(a, b)
        limit = ratio * self.reach(rise)   # a drop (rise below 0) gives a longer jump
        self.checks.append((name, g, rise, limit))
        if rise > 0.8 * self.apex or g > limit:
            raise RuntimeError("Out of reach: {} gap {:.0f} rise {:.0f} (limit {:.0f})".format(name, g, rise, limit))

    def lift(self, name, column, column_top, ledge, ledge_top):
        # Carried up an updraft, then over onto a ledge just under the column's top.
        g = gap(column, ledge)
        self.checks.append((name + " (updraft)", g, ledge_top - column_top, 300.0))
        if ledge_top > column_top - 50.0 or g > 300.0:
            raise RuntimeError("Updraft can't make it: {} gap {:.0f}, ledge {:.0f} vs column top {:.0f}".format(name, g, ledge_top, column_top))

    # ----- pieces; each returns its footing -----
    def add(self, *piece):
        self.pieces.append(piece)

    def island(self, x, y, top, size):
        self.add("island", x, y, top, size)
        return circle(x, y, ISLAND_FOOT * size)

    def cloud(self, x, y, top, size):
        self.add("cloud", x, y, top, size)
        return rect(x, y, CLOUD_FOOT * size)

    def vanish(self, x, y, top, size, stay=0.6, gone=2.5):
        self.add("vanish", x, y, top, size, stay, gone)
        return rect(x, y, CLOUD_FOOT * size)

    def mover(self, x, y, top, offset, seconds, wait):
        self.add("mover", x, y, top, offset, seconds, wait)
        r = ISLAND_FOOT * MOVER_SIZE
        return circle(x, y, r), circle(x + offset[0], y + offset[1], r)

    def timed(self, x, y, top, delay):
        self.add("timed", x, y, top, delay)
        return rect(x, y, self.plat)

    def falling(self, x, y, top):
        self.add("falling", x, y, top)
        return rect(x, y, self.plat)

    def marble(self, x0, x1, y0, y1, top, thick=80.0):
        self.add("marble", x0, x1, y0, y1, top, thick)
        return ("rect", x0, x1, y0, y1)

    def bridge(self, name, a, a_top, b, b_top, count, size):
        # `count` solid clouds evenly between a and b (middle to middle), climbing evenly from a_top to b_top.
        (ax, ay), (bx, by) = middle(a), middle(b)
        previous, previous_top = a, a_top
        for i in range(1, count + 1):
            t = i / (count + 1.0)
            here_top = a_top + (b_top - a_top) * t
            here_top = round(here_top / 10.0) * 10.0
            here = self.cloud(ax + (bx - ax) * t, ay + (by - ay) * t, here_top, size)
            self.jump("{} {}".format(name, i), previous, here, here_top - previous_top)
            previous, previous_top = here, here_top
        self.jump("{} end".format(name), previous, b, b_top - previous_top)

    def wind(self, x, y, z, along, width, height, yaw, pitch, strength, max_speed, on=0.0, off=0.0, delay=0.0):
        self.add("wind", x, y, z, along, width, height, yaw, pitch, strength, max_speed, on, off, delay)


# ----- footprints -----
def rect(cx, cy, sx, sy=None):
    sy = sx if sy is None else sy
    return ("rect", cx - sx / 2.0, cx + sx / 2.0, cy - sy / 2.0, cy + sy / 2.0)


def circle(cx, cy, r):
    return ("circle", cx, cy, r)


def middle(shape):
    if shape[0] == "rect":
        return (shape[1] + shape[2]) / 2.0, (shape[3] + shape[4]) / 2.0
    return shape[1], shape[2]


def half(shape, dx, dy):
    # How far the footing reaches from its middle along an axis direction (dx, dy one of the unit axes).
    if shape[0] == "circle":
        return shape[3]
    return (shape[2] - shape[1]) / 2.0 if dx else (shape[4] - shape[3]) / 2.0


def gap(a, b):
    def nearest(shape, px, py):
        if shape[0] == "rect":
            return min(max(px, shape[1]), shape[2]), min(max(py, shape[3]), shape[4])
        dx, dy = px - shape[1], py - shape[2]
        d = math.hypot(dx, dy) or 1.0
        return shape[1] + dx / d * min(d, shape[3]), shape[2] + dy / d * min(d, shape[3])

    if a[0] == "rect" and b[0] == "rect":
        gx = max(0.0, b[1] - a[2], a[1] - b[2])
        gy = max(0.0, b[3] - a[4], a[3] - b[4])
        return math.hypot(gx, gy)
    if a[0] == "circle" and b[0] == "circle":
        return max(0.0, math.hypot(a[1] - b[1], a[2] - b[2]) - a[3] - b[3])
    c, r = (a, b) if a[0] == "circle" else (b, a)
    px, py = nearest(r, c[1], c[2])
    return max(0.0, math.hypot(px - c[1], py - c[2]) - c[3])


def beyond(shape, direction, distance, size_half, side=0.0):
    # The middle of a new piece `distance` clear of `shape` along an axis direction, shifted `side` across it.
    dx, dy = direction
    cx, cy = middle(shape)
    reach = half(shape, dx, dy) + distance + size_half
    return cx + dx * reach - dy * side, cy + dy * reach + dx * side


def build(base, jump_z, gravity, walk, plat):
    r = Route(base, jump_z, gravity, walk, plat)
    E, N, W, S = (1, 0), (0, 1), (-1, 0), (0, -1)
    top = base

    # ===== A. Cloud Harbor =====
    r.add("section", "A Cloud Harbor")
    home = r.island(0.0, 0.0, top, 1400.0)
    r.add("start", -300.0, 0.0, top)
    r.add("deco", -650.0, -550.0, -350.0, -250.0, top, top + 500.0)    # an old gateway behind the start
    r.add("deco", -650.0, -550.0, 250.0, 350.0, top, top + 500.0)
    r.add("deco", -660.0, -540.0, -360.0, 360.0, top + 500.0, top + 580.0)
    previous = home
    for i in range(5):
        top += 100.0
        x, y = beyond(previous, E, 320.0, 0.4 * 260.0, side=(-120.0 if i % 2 else 120.0))
        here = r.vanish(x, y, top, 260.0, 0.6, 2.5)
        r.jump("harbor cloud {}".format(i + 1), previous, here, 100.0)
        previous = here
    top += 100.0
    x, y = beyond(previous, E, 350.0, 240.0)
    landing = r.island(x, y, top, 500.0)
    r.jump("cloud -> landing", previous, landing, 100.0)
    x, y = beyond(landing, E, 160.0, 168.0)
    ride, arrive = r.mover(x, y, top, (1500.0, 0.0, 0.0), 3.5, 1.2)
    r.jump("landing -> island ferry", landing, ride, 0.0)
    top += 100.0
    x, y = beyond(arrive, E, 300.0, 288.0)
    harbor_top = r.island(x, y, top, 600.0)
    r.jump("ferry -> far island", arrive, harbor_top, 100.0)

    # ===== B. Crosswind Beams (gusts blow +X, across the beams running north) =====
    r.add("section", "B Crosswind Beams")
    previous = harbor_top
    hx, hy = middle(harbor_top)
    beams = []
    y_cursor = hy + 288.0
    for i in range(5):
        top += 100.0
        y0 = y_cursor + 250.0
        y1 = y0 + 650.0
        here = r.marble(hx - 60.0, hx + 60.0, y0, y1, top)
        r.jump("crosswind beam {}".format(i + 1), previous, here, 100.0)
        beams.append((here, top))
        previous, y_cursor = here, y1
    span0, span1 = hy + 288.0, y_cursor
    r.wind(hx, (span0 + span1) / 2.0, top - 150.0, 900.0, span1 - span0 + 200.0, 900.0, 0.0, 0.0, 700.0, 450.0, 1.8, 2.2, 0.0)
    # Trap: a gilded island off beam 3 to the west that looks like a way on.
    b3, b3_top = beams[2]
    bx, by = middle(b3)
    lure = r.island(hx - 60.0 - 260.0 - 300.0, by, b3_top, 600.0)
    r.jump("beam 3 -> lure island", b3, lure, 0.0)
    r.add("trap", hx - 60.0 - 260.0 - 520.0, hx - 60.0 - 260.0 - 80.0, by - 220.0, by + 220.0, b3_top)
    r.add("lure", hx - 60.0 - 260.0 - 300.0, by, b3_top)
    # Star coin 1: downwind off beam 4, a little cloud below; back by two clouds to the flag island.
    b4, b4_top = beams[3]
    cx4, cy4 = middle(b4)
    coin_cloud = r.cloud(hx + 60.0 + 560.0 + 80.0, cy4, b4_top - 100.0, 200.0)
    r.jump("beam 4 -> coin cloud (downwind)", b4, coin_cloud, -100.0)
    r.add("coin", hx + 60.0 + 560.0 + 80.0, cy4, b4_top - 100.0)
    top += 100.0
    x, y = beyond(previous, N, 330.0, 300.0)
    flag_island = r.island(x, y, top, 700.0)
    r.jump("beam 5 -> flag island", previous, flag_island, 100.0)
    r.bridge("coin cloud -> flag island", coin_cloud, b4_top - 100.0, flag_island, top, 3, 240.0)
    fx, fy = middle(flag_island)
    r.add("flag", fx - 150.0, fy, top)

    # ===== C. Updraft Gorge (going east again) =====
    r.add("section", "C Updraft Gorge")
    # Updraft 1: off the flag island's east edge, over the drop.
    col = ("rect", fx + 336.0 + 40.0, fx + 336.0 + 340.0, fy - 150.0, fy + 150.0)
    col_bottom, col_top = top - 300.0, top + 1000.0
    r.wind((col[1] + col[2]) / 2.0, fy, (col_bottom + col_top) / 2.0, col_top - col_bottom, 300.0, 300.0, 0.0, 90.0, 2200.0, 900.0)
    r.jump("flag island -> updraft", flag_island, col, 0.0)
    ledge_top = col_top - 150.0
    ledge = r.island(col[2] + 150.0 + 192.0, fy, ledge_top, 400.0)
    r.lift("updraft 1 -> ledge", col, col_top, ledge, ledge_top)
    top = ledge_top
    previous = ledge
    for i in range(3):
        top += 100.0
        x, y = beyond(previous, E, 350.0, 0.4 * 240.0, side=(100.0 if i % 2 else -100.0))
        here = r.vanish(x, y, top, 240.0, 0.5, 2.5)
        r.jump("gorge cloud {}".format(i + 1), previous, here, 100.0)
        previous = here
    # Updraft 2 gusts: ride it while it blows.
    px, py = middle(previous)
    col2 = ("rect", previous[2] + 60.0, previous[2] + 310.0, py - 125.0, py + 125.0)
    col2_bottom, col2_top = top - 300.0, top + 1100.0
    r.wind((col2[1] + col2[2]) / 2.0, py, (col2_bottom + col2_top) / 2.0, col2_top - col2_bottom, 250.0, 250.0, 0.0, 90.0, 2200.0, 900.0, 3.2, 1.6, 0.0)
    r.jump("cloud -> updraft 2", previous, col2, 0.0)
    perch_top = col2_top - 150.0
    perch = r.marble(col2[2] + 140.0, col2[2] + 360.0, py - 110.0, py + 110.0, perch_top, 120.0)
    r.lift("updraft 2 -> perch", col2, col2_top, perch, perch_top)
    top = perch_top
    # Star coin 2: a third, narrow updraft beside the perch, carrying far higher; the coin at its top on a little cloud.
    col3 = ("rect", perch[1] + 30.0, perch[2] - 30.0, py + 110.0 + 120.0, py + 110.0 + 280.0)
    col3_bottom, col3_top = top - 200.0, top + 1500.0
    r.wind((col3[1] + col3[2]) / 2.0, (col3[3] + col3[4]) / 2.0, (col3_bottom + col3_top) / 2.0, col3_top - col3_bottom, 160.0, 160.0, 0.0, 90.0, 2000.0, 800.0)
    r.jump("perch -> coin updraft", perch, col3, 0.0)
    coin2_top = col3_top - 150.0
    coin2 = r.cloud((col3[1] + col3[2]) / 2.0, col3[4] + 150.0 + 80.0, coin2_top, 200.0)
    r.lift("coin updraft -> coin cloud", col3, col3_top, coin2, coin2_top)
    r.add("coin", (col3[1] + col3[2]) / 2.0, col3[4] + 150.0 + 80.0, coin2_top)
    previous = perch

    # ===== D. Island Chain =====
    r.add("section", "D Island Chain")
    x, y = beyond(previous, E, 140.0, 168.0)
    lift_ride, lift_top_shape = r.mover(x, y, top, (0.0, 0.0, 800.0), 3.2, 1.2)
    r.jump("perch -> rising island", previous, lift_ride, 0.0)
    top += 800.0
    lx, ly = x, y
    x, y = beyond(lift_ride, E, 320.0, 216.0)
    d2 = r.island(x, y, top + 50.0, 450.0)
    r.jump("rising island (top) -> island", lift_ride, d2, 50.0)
    top += 50.0
    # Trap 2: a lone island south of d2 with something shiny on it.
    d2x, d2y = middle(d2)
    bait = r.island(d2x, d2y - 216.0 - 300.0 - 240.0, top, 500.0)
    r.jump("island -> bait island", d2, bait, 0.0)
    r.add("trap", d2x - 200.0, d2x + 200.0, d2y - 216.0 - 300.0 - 440.0, d2y - 216.0 - 300.0 - 40.0, top)
    r.add("lure", d2x, d2y - 216.0 - 300.0 - 240.0, top)
    previous = d2
    for i in range(3):
        top += 100.0
        x, y = beyond(previous, N, 340.0, r.plat / 2.0)
        here = r.timed(x, y, top, 0.6 * i)
        r.jump("fading step {}".format(i + 1), previous, here, 100.0)
        previous = here
    x, y = beyond(previous, N, 150.0, 168.0)
    ferry, ferry_end = r.mover(x, y, top, (0.0, 1600.0, 0.0), 4.0, 1.0)
    r.jump("fading step -> ferry", previous, ferry, 0.0)
    top += 100.0
    x, y = beyond(ferry_end, N, 330.0, 0.4 * 240.0)
    v = r.vanish(x, y, top, 240.0, 0.45, 2.5)
    r.jump("ferry -> vanishing cloud", ferry_end, v, 100.0)
    top += 100.0
    x, y = beyond(v, N, 340.0, r.plat / 2.0)
    crumble = r.falling(x, y, top)
    r.jump("cloud -> crumbling floor", v, crumble, 100.0)
    top += 100.0
    x, y = beyond(crumble, N, 330.0, 336.0)
    flag2 = r.island(x, y, top, 700.0)
    r.jump("crumbling floor -> flag island 2", crumble, flag2, 100.0)
    f2x, f2y = middle(flag2)
    r.add("flag", f2x, f2y + 100.0, top)

    # ===== E. Storm Stair (headwind gusts from the east, steps going east) =====
    r.add("section", "E Storm Stair")
    previous = flag2
    first_x = None
    for i in range(7):
        top += 100.0
        x0 = (previous[2] if previous[0] == "rect" else previous[1] + previous[3]) + 300.0
        here = r.marble(x0, x0 + 220.0, f2y - 110.0, f2y + 110.0, top, 100.0)
        r.jump("storm step {}".format(i + 1), previous, here, 100.0)
        first_x = first_x or x0
        previous = here
    last_x = previous[2]
    r.wind((first_x + last_x) / 2.0 - 100.0, f2y, top - 250.0, last_x - first_x + 500.0, 700.0, 1100.0, 180.0, 0.0, 600.0, 400.0, 2.0, 2.0, 0.5)
    # Star coin 3: up a long beam north from step 4 straight into a steady headwind, the coin at its end.
    s4 = r.pieces[[i for i, p in enumerate(r.pieces) if p[0] == "marble"][-4]]
    _, sx0, sx1, sy0, sy1, s4_top, _ = s4
    beam = r.marble((sx0 + sx1) / 2.0 - 50.0, (sx0 + sx1) / 2.0 + 50.0, sy1 + 260.0, sy1 + 260.0 + 1500.0, s4_top + 100.0, 60.0)
    r.jump("storm step 4 -> headwind beam", ("rect", sx0, sx1, sy0, sy1), beam, 100.0)
    r.wind((sx0 + sx1) / 2.0, sy1 + 260.0 + 750.0, s4_top + 350.0, 1500.0, 500.0, 600.0, -90.0, 0.0, 700.0, 350.0)
    r.add("coin", (sx0 + sx1) / 2.0, sy1 + 260.0 + 1450.0, s4_top + 100.0)
    # Then quick clouds up to the summit.
    for i in range(4):
        top += 100.0
        x, y = beyond(previous, E, 350.0, 0.4 * 240.0, side=(-130.0 if i % 2 else 130.0))
        here = r.vanish(x, y, top, 240.0, 0.4, 2.5)
        r.jump("summit cloud {}".format(i + 1), previous, here, 100.0)
        previous = here
    top += 100.0
    x, y = beyond(previous, E, 350.0, 720.0)
    summit = r.island(x, y, top, 1500.0)
    r.jump("cloud -> summit", previous, summit, 100.0)

    # ===== F. The Cloud Stair: the lever gathers clouds into a stair round a column up to the gate =====
    r.add("section", "F Cloud Stair")
    sx, sy = middle(summit)
    r.add("lever", sx - 300.0, sy - 300.0, top, 0.0)
    column_x, column_y = sx + 720.0 + 900.0, sy
    radius = 700.0
    steps = 15
    previous = summit
    step_top = top
    # Round the column counter-clockwise, starting on the summit's side.
    for i in range(steps):
        step_top += 100.0
        a = math.radians(180.0 - 32.0 * i)
        x, y = column_x + radius * math.cos(a), column_y + radius * math.sin(a)
        r.add("stair", x, y, step_top, 260.0, i)
        here = rect(x, y, CLOUD_FOOT * 260.0)
        r.jump("cloud stair {}".format(i + 1), previous, here, 100.0)
        previous = here
    gate_top = step_top + 100.0
    r.add("column", column_x, column_y, gate_top, 420.0)
    r.jump("cloud stair -> gate", previous, circle(column_x, column_y, 420.0), 100.0)
    r.add("gate", column_x, column_y, gate_top)
    r.summit_top, r.gate_top, r.column = top, gate_top, (column_x, column_y)
    return r


def footing(piece, plat):
    kind = piece[0]
    if kind in ("island", "stair_column"):
        return circle(piece[1], piece[2], ISLAND_FOOT * piece[4]), piece[3]
    if kind in ("cloud", "vanish"):
        return rect(piece[1], piece[2], piece[4]), piece[3]
    if kind == "stair":
        return rect(piece[1], piece[2], piece[4]), piece[3]
    if kind == "mover":
        return circle(piece[1], piece[2], 0.5 * MOVER_SIZE), piece[3]
    if kind in ("timed", "falling"):
        return rect(piece[1], piece[2], plat), piece[3]
    if kind == "marble":
        return ("rect", piece[1], piece[2], piece[3], piece[4]), piece[5]
    return None


def crowding(route):
    # Pieces whose footings overlap (or nearly) at heights close enough to get in the way: one sits in the other, or
    # its underside hits the head of a player standing on the lower one.
    found = []
    solid = [(i, footing(p, route.plat)) for i, p in enumerate(route.pieces)]
    solid = [(i, f) for i, f in solid if f]
    for a in range(len(solid)):
        for b in range(a + 1, len(solid)):
            (ia, (fa, ta)), (ib, (fb, tb)) = solid[a], solid[b]
            if abs(ta - tb) < 450.0 and gap(fa, fb) < 40.0:
                found.append((route.pieces[ia][:5], route.pieces[ib][:5]))
    return found


if __name__ == "__main__":
    route = build(14960.0, 500.9, 980.0, 600.0, 300.0)
    for a, b in crowding(route):
        print("  CROWDED", a, b)
    for name, g, rise, limit in route.checks:
        print("  {:<40} gap {:>5.0f} rise {:>5.0f} (limit {:>5.0f}){}".format(name, g, rise, limit, "  TIGHT" if g > 0.85 * limit else ""))
    print("summit {:.0f}, gate {:.0f}, pieces {}".format(route.summit_top, route.gate_top, len(route.pieces)))
