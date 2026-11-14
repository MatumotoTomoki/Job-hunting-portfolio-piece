# The heaven area's (area 4, the last one) route as plain data, checked jump by jump; build_area4_heaven.py places it.
# No Unreal here, so it can be checked on its own:
#   python area4_layout.py          (prints every jump; fails on one out of reach)
# A hub and three wings, played in any order; each wing ends in a lever that sinks one of the three doors of the great
# gate (the area's big mechanism). Behind the last door: the sanctum, where the goal will be (a placeholder for now).
#   Hub  Heaven's Plaza   the start; exits west (Sky Spire), east (Golden Clockwork), south (Underworks); the gate on the
#                         north: a sealed building with the three doors one behind the other. Star coin 4 on a pinnacle
#                         beside the gate roof (where the Sky Spire's gondola comes back).
#   West Sky Spire (up)   vanishing clouds, an island ferry, flag 1 on the fork island; up to the sun terrace either by a
#                         gusty updraft (quick) or a spiral of clouds and fading steps (safe); across it either riding the
#                         sun's launch (quick) or a ledge-grab tower (safe); crosswind beams (a trap island, star coin 1
#                         downwind), headwind storm steps, the summit with lever 1; a gondola back to the gate roof.
#   East Golden Clockwork spinning gears down to the switch hall (flag 2); two ways north: red blocks and flipping
#        (down, then up) floors, or a switch flip, blue blocks and a long narrow beam; the clock landing (time rewind);
#                         a gondola north and up to the balcony (a cage trap doorway, the speed item on a dead end,
#                         star coin 2 over a gap only a speed run clears); west by a piston and gears to the clock top with
#                         lever 2, which also raises a brass stair back down to the plaza.
#   South Underworks      a dark hall hanging under the plaza, lit by shafts of light through glazed holes in its roof.
#        (down, then up)  Down either by drop ledges (a hidden ledge with star coin 5) or a slow lift; flag 3; over the
#                         pit either along a flame bridge or on stones a pressure plate raises for a while; up either
#                         through the heaven-or-hell birdcages or a ledge-grab chimney; star coin 3 past flame jets on
#                         the gallery; fading steps and a piston up to lever 3, which raises a stone bridge back to the
#                         entrance.
# Pieces (heights are the top a player stands on unless said otherwise; x, y the middle):
#   area 3's: island, cloud, vanish, mover, timed, falling, wind, coin, flag, trap, lure, sign, marble
#   ("block", x0, x1, y0, y1, z0, z1, look, name)    a solid box; looks: marble, gold, stone, darkstone, sky, ember, glow
#   ("glass", x0, x1, y0, y1, z0, z1)                 an unseen solid box
#   ("disk", x, y, top, r, thick, look, name)         a solid cylinder
#   ("gear", x, y, top, r, spin), ("sblock", x, y, top, size, red), ("switch", x, y, top)
#   ("moving", x, y, top, (dx, dy, dz), seconds, wait)   BP_MovingPlatform; ("rotating", x, y, top) BP_RotatingFloor
#   ("gondola", x, y, top, (dx, dy, dz), seconds)
#   ("flame", x, y, top, yaw, delay, warn, burn, off, respawn)    respawn: a spot's name
#   ("sun", x, y, top, respawn), ("rewind", x, y, top), ("cages", x, y, top, (x, y, z) destination, pair id)
#   ("speed", x, y, top), ("spot", name, x, y, top)   a named respawn point
#   ("lever", name, x, y, top, yaw, reset)            reset > 0: a pressure plate that springs back after that long
#   ("mech", lever, x, y, top, (sx, sy, sz), (dx, dy, dz), delay, seconds, back, look, name)
#                                                     BP_Mechanism, origin on its top; back: None or (after, seconds)
#   ("door", lever, x, y, (sx, sy, sz), look)         a gate door that sinks into the floor when the lever is pulled
#   ("camera", lever, (x, y, z) eye, (x, y, z) look, seconds)
#   ("shaft", x, y, z_top, z_bottom, r)               a shaft of light (glow cylinder + spot light)
#   ("lamp", x, y, z, (r, g, b)), ("start", x, y, top, yaw), ("goal", x, y, top), ("catcher", x0, x1, y0, y1, z)
#   ("island_deco", x, y, top, size), ("section", name)
import math

from area3_layout import Route as SkyRoute, rect, circle, middle, gap, beyond

HARD, MID, EASY = 0.9, 0.75, 0.6
GRAB_MIN, GRAB_MAX = 160.0, 230.0
SPEED_ITEM_SPEED = 1500.0
E, N, W, S = (1, 0), (0, 1), (-1, 0), (0, -1)


class Route(SkyRoute):
    def __init__(self, base, jump_z, gravity, walk, plat, rot):
        SkyRoute.__init__(self, base, jump_z, gravity, walk, plat)
        self.rot = rot

    # ----- checks -----
    def jump(self, name, a, b, rise, ratio=HARD):
        # As area 3's, with a centimetre to spare for pieces placed at exactly the checked ratio.
        g = gap(a, b)
        limit = ratio * self.reach(rise) + 1.0
        self.checks.append((name, g, rise, limit))
        if rise > 0.8 * self.apex or g > limit:
            raise RuntimeError("Out of reach: {} gap {:.0f} rise {:.0f} (limit {:.0f})".format(name, g, rise, limit))

    def at(self, previous, direction, ratio, rise, size_half, side=0.0):
        # Where the next piece goes: `ratio` of the jump's reach clear of `previous`.
        return beyond(previous, direction, ratio * self.reach(rise), size_half, side)

    def grab(self, name, a, b, rise):
        # Hanging from the ledge (Q) and climbing up: the wall right in front, a little too high to jump.
        g = gap(a, b)
        self.checks.append((name + " (grab)", g, rise, 60.0))
        if not GRAB_MIN <= rise <= GRAB_MAX or g > 60.0:
            raise RuntimeError("Can't grab: {} gap {:.0f} rise {:.0f}".format(name, g, rise))

    def walk_on(self, name, a, b, rise=0.0):
        # Joined pieces: walked across, at most a small step up.
        g = gap(a, b)
        self.checks.append((name + " (walk)", g, rise, 40.0))
        if g > 40.0 or rise > 60.0:
            raise RuntimeError("Not joined: {} gap {:.0f} rise {:.0f}".format(name, g, rise))

    # ----- pieces -----
    def block(self, x0, x1, y0, y1, z0, z1, look="marble", name="Block"):
        self.add("block", x0, x1, y0, y1, z0, z1, look, name)
        return ("rect", x0, x1, y0, y1)

    def disk(self, x, y, top, r, thick=200.0, look="marble", name="Disk"):
        self.add("disk", x, y, top, r, thick, look, name)
        return circle(x, y, r)

    def gear(self, x, y, top, r, spin):
        self.add("gear", x, y, top, r, spin)
        return circle(x, y, 0.92 * r)

    def sblock(self, x, y, top, size, red):
        self.add("sblock", x, y, top, size, red)
        return rect(x, y, size)

    def moving(self, x, y, top, offset, seconds, wait):
        self.add("moving", x, y, top, offset, seconds, wait)
        return rect(x, y, self.plat), rect(x + offset[0], y + offset[1], self.plat)

    def rotating(self, x, y, top):
        self.add("rotating", x, y, top)
        return rect(x, y, self.rot)

    def gondola(self, x, y, top, offset, seconds):
        self.add("gondola", x, y, top, offset, seconds)
        return rect(x, y, self.plat), rect(x + offset[0], y + offset[1], self.plat)

    def lamp(self, x, y, z, color=(255, 214, 160)):
        self.add("lamp", x, y, z, color)

    def shaft(self, x, y, z_top, z_bottom, r=160.0):
        self.add("shaft", x, y, z_top, z_bottom, r)

    def stair(self, lever, name, a_shape, a_top, b_shape, b_top, a, b, count, size, thick, rise, delay, look):
        # `count` mechanism steps evenly from point a to point b (between two pieces), each rising `rise` into place.
        previous, prev_top = a_shape, a_top
        for i in range(count):
            t = (i + 1.0) / (count + 1.0)
            x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            step_top = round((a_top + (b_top - a_top) * t) / 10.0) * 10.0
            here = rect(x, y, size)
            self.add("mech", lever, x, y, step_top - rise, (size, size, thick), (0.0, 0.0, rise), 1.0 + delay * i, 1.4, None, look, name)
            self.jump("{} {}".format(name.lower(), i + 1), previous, here, step_top - prev_top)
            previous, prev_top = here, step_top
        self.jump("{} -> end".format(name.lower()), previous, b_shape, b_top - prev_top)
        return 1.0 + delay * (count - 1) + 1.4


def subtract(box, hole):
    # The parts of rect `box` (x0, x1, y0, y1) outside rect `hole`.
    x0, x1, y0, y1 = box
    h0, h1, k0, k1 = max(hole[0], x0), min(hole[1], x1), max(hole[2], y0), min(hole[3], y1)
    if h0 >= h1 or k0 >= k1:
        return [box]
    parts = [(x0, x1, y0, k0), (x0, x1, k1, y1), (x0, h0, k0, k1), (h1, x1, k0, k1)]
    return [p for p in parts if p[1] - p[0] > 1.0 and p[3] - p[2] > 1.0]


def with_holes(box, holes):
    parts = [box]
    for hole in holes:
        parts = [piece for part in parts for piece in subtract(part, hole)]
    return parts


def build(base, jump_z, gravity, walk, plat, rot=300.0):
    r = Route(base, jump_z, gravity, walk, plat, rot)
    T0 = base
    P = plat

    # =====================================================================================================
    # Hub: Heaven's Plaza and the great gate
    # =====================================================================================================
    r.add("section", "0 Plaza")
    PR = 1600.0
    plaza = r.disk(0.0, 0.0, T0, PR, 300.0, "marble", "Plaza")
    r.add("island_deco", 0.0, 0.0, T0 - 300.0, 3600.0)
    r.add("start", 0.0, -1100.0, T0, 90.0)
    r.add("spot", "start", 0.0, -1100.0, T0)
    for i in range(8):
        a = math.radians(22.5 + 45.0 * i)
        x, y = 1450.0 * math.cos(a), 1450.0 * math.sin(a)
        r.block(x - 60.0, x + 60.0, y - 60.0, y + 60.0, T0, T0 + 900.0, "marble", "Plaza Pillar")
        r.block(x - 80.0, x + 80.0, y - 80.0, y + 80.0, T0 + 900.0, T0 + 960.0, "gold", "Pillar Cap")
    r.disk(0.0, 0.0, T0 + 20.0, 300.0, 20.0, "gold", "Plaza Seal")
    r.shaft(0.0, 0.0, T0 + 4000.0, T0 + 20.0, 280.0)
    for text, x, y, yaw in (("Sky Spire", -1250.0, 0.0, 0.0), ("Golden Clockwork", 1250.0, 0.0, 180.0),
                            ("Underworks", 0.0, -1350.0, 90.0), ("Heaven's Gate", 0.0, 1250.0, -90.0)):
        r.add("sign", x, y, T0 + 380.0, yaw, text)

    # The gate: one sealed building, open only at the front; three doors one behind the other, then the sanctum.
    GX0, GX1, GY0, GY1 = -500.0, 500.0, 1500.0, 3300.0
    GATE_TOP = T0 + 1250.0
    r.block(GX0, GX1, GY0, GY1, T0 - 300.0, T0, "marble", "Gate Floor")
    r.block(GX0, -350.0, GY0, GY1, T0, T0 + 1100.0, "marble", "Gate Wall")
    r.block(350.0, GX1, GY0, GY1, T0, T0 + 1100.0, "marble", "Gate Wall")
    r.block(-350.0, 350.0, GY1 - 150.0, GY1, T0, T0 + 1100.0, "marble", "Gate Wall")
    gate_roof = r.block(GX0, GX1, GY0, GY1, T0 + 1100.0, GATE_TOP, "gold", "Gate Roof")
    for lever, y, look in (("sky", 1700.0, "sky"), ("clock", 1900.0, "gold"), ("under", 2100.0, "ember")):
        r.add("door", lever, 0.0, y, (700.0, 80.0, 1100.0), look)
        eye, look_at = (1100.0, 300.0, T0 + 700.0), (0.0, 1700.0, T0 + 450.0)
        r.add("camera", lever, eye, look_at, 5.0)
    r.disk(0.0, 2800.0, T0 + 20.0, 260.0, 20.0, "glow", "Goal Glow")
    r.add("goal", 0.0, 2800.0, T0)
    r.lamp(0.0, 2800.0, T0 + 900.0, (255, 236, 190))
    r.jump("gate roof -> plaza (drop)", gate_roof, plaza, -1250.0)
    # Star coin 4: a gold pinnacle off the roof's east side.
    pin = r.block(800.0, 950.0, 1830.0, 1980.0, T0 - 300.0, GATE_TOP + 100.0, "gold", "Pinnacle")
    r.jump("gate roof -> pinnacle", gate_roof, pin, 100.0)
    r.add("coin", 875.0, 1905.0, GATE_TOP + 100.0)

    # =====================================================================================================
    # West: Sky Spire
    # =====================================================================================================
    r.add("section", "1 Sky Spire")
    previous, top = plaza, T0
    for i in range(3):
        top += 100.0
        x, y = r.at(previous, W, 0.8, 100.0, 0.4 * 260.0, side=(120.0 if i % 2 else -120.0))
        here = r.vanish(x, y, top, 260.0, 0.6, 2.5)
        r.jump("sky cloud {}".format(i + 1), previous, here, 100.0)
        previous = here
    top += 100.0
    x, y = r.at(previous, W, 0.75, 100.0, 240.0)
    landing = r.island(x, y, top, 500.0)
    r.jump("cloud -> landing", previous, landing, 100.0)
    x, y = beyond(landing, W, 160.0, 168.0)
    ride, arrive = r.mover(x, y, top, (-1600.0, 0.0, 0.0), 3.5, 1.2)
    r.jump("landing -> ferry", landing, ride, 0.0)
    x, y = beyond(arrive, W, 300.0, 432.0)
    fork = r.island(x, y, top, 900.0)
    r.jump("ferry -> fork island", arrive, fork, 0.0)
    fx, fy = middle(fork)
    FORK_TOP = top
    r.add("flag", fx + 150.0, fy + 150.0, top)
    r.add("spot", "sky", fx, fy, top)
    r.add("sign", fx - 250.0, fy + 250.0, top + 350.0, 0.0, "Updraft  /  Cloud Spiral")

    # The sun terrace, reached two ways.
    STEPS = 16
    TS = FORK_TOP + 100.0 * (STEPS + 1)
    col = ("rect", fx - 432.0 - 60.0 - 300.0, fx - 432.0 - 60.0, fy - 150.0, fy + 150.0)
    col_top = TS + 150.0
    r.wind((col[1] + col[2]) / 2.0, fy, (FORK_TOP - 300.0 + col_top) / 2.0, col_top - FORK_TOP + 300.0, 300.0, 300.0,
           0.0, 90.0, 2200.0, 900.0, 3.0, 1.5, 0.0)
    r.jump("fork -> updraft", fork, col, 0.0)
    TX1 = col[1] - 150.0
    TX0 = TX1 - 2400.0
    TY0, TY1 = fy - 2600.0, fy + 300.0
    terrace = r.block(TX0, TX1, TY0, TY1, TS - 150.0, TS, "marble", "Sun Terrace")
    r.lift("updraft -> sun terrace", col, col_top, terrace, TS)
    # The safe way: a spiral of clouds round a pillar south of the fork, two of them fading steps.
    cx, cy = fx + 120.0, fy - 432.0 - 270.0 - 112.0 - 900.0
    r.disk(cx, cy, TS + 300.0, 450.0, TS + 300.0 - (T0 - 1800.0), "marble", "Spiral Pillar")
    previous, step_top = fork, FORK_TOP
    for i in range(STEPS):
        step_top += 100.0
        a = math.radians(90.0 + 32.0 * i)
        x, y = cx + 900.0 * math.cos(a), cy + 900.0 * math.sin(a)
        if i in (5, 11):
            here = r.timed(x, y, step_top, 0.0)
        else:
            here = r.cloud(x, y, step_top, 280.0)
        r.jump("spiral {}".format(i + 1), previous, here, 100.0, MID)
        previous = here
    r.jump("spiral -> sun terrace", previous, terrace, TS - step_top, MID)

    # The terrace: the sun in the middle. Up 11 m either on its back (its launch) or by the ledge-grab tower.
    stx, sty = (TX0 + TX1) / 2.0, (TY0 + TY1) / 2.0
    r.add("sun", stx, sty, TS, "sky")
    TU = TS + 1100.0
    upper = r.block(stx - 300.0, stx + 300.0, sty + 250.0, sty + 1350.0, TU - 100.0, TU, "marble", "Upper Terrace")
    r.add("sign", stx + 700.0, sty - 300.0, TS + 350.0, 0.0, "Ride the sun  /  Climb the tower (Q)")
    previous, top = terrace, TS
    for i in range(5):
        top += 220.0
        y0 = sty - 150.0 + 300.0 * i
        here = r.block(TX0 + 100.0, TX0 + 400.0, y0, y0 + 300.0, TS, top, "marble", "Grab Tower")
        r.grab("grab tower {}".format(i + 1), previous, here, 220.0)
        previous = here
    walk = r.block(TX0 + 400.0, stx - 300.0, sty + 1150.0, sty + 1250.0, TU - 60.0, TU, "marble", "Tower Walk")
    r.walk_on("grab tower -> walk", previous, walk)
    r.walk_on("walk -> upper terrace", walk, upper)

    # Crosswind beams going north (gusts blow +X); a gilded trap island off beam 3, star coin 1 downwind of beam 4.
    previous, top = upper, TU
    beams = []
    y_cursor = sty + 1350.0
    for i in range(5):
        top += 100.0
        y0 = y_cursor + 250.0
        here = r.marble(stx - 60.0, stx + 60.0, y0, y0 + 650.0, top)
        r.jump("gale beam {}".format(i + 1), previous, here, 100.0)
        beams.append((here, top))
        previous, y_cursor = here, y0 + 650.0
    span0, span1 = sty + 1350.0, y_cursor
    r.wind(stx, (span0 + span1) / 2.0, top - 150.0, 900.0, span1 - span0 + 200.0, 900.0, 0.0, 0.0, 700.0, 450.0, 1.8, 2.2, 0.0)
    b3, b3_top = beams[2]
    _, by = middle(b3)
    lure = r.island(stx - 60.0 - 260.0 - 300.0, by, b3_top, 600.0)
    r.jump("beam 3 -> lure island", b3, lure, 0.0)
    r.add("trap", stx - 60.0 - 260.0 - 520.0, stx - 60.0 - 260.0 - 80.0, by - 220.0, by + 220.0, b3_top)
    r.add("lure", stx - 60.0 - 260.0 - 300.0, by, b3_top)
    b4, b4_top = beams[3]
    _, cy4 = middle(b4)
    coin_cloud = r.cloud(stx + 60.0 + 560.0 + 80.0, cy4, b4_top - 100.0, 200.0)
    r.jump("beam 4 -> coin cloud (downwind)", b4, coin_cloud, -100.0)
    r.add("coin", stx + 60.0 + 560.0 + 80.0, cy4, b4_top - 100.0)
    top += 100.0
    x, y = beyond(previous, N, 330.0, 336.0)
    gale_end = r.island(x, y, top, 700.0)
    r.jump("beam 5 -> gale end", previous, gale_end, 100.0)
    r.bridge("coin cloud -> gale end", coin_cloud, b4_top - 100.0, gale_end, top, 3, 240.0)
    gx, gy = middle(gale_end)

    # Storm steps north into headwind gusts, then the summit.
    previous = gale_end
    first_y = None
    for i in range(6):
        top += 100.0
        y0 = (previous[4] if previous[0] == "rect" else previous[2] + previous[3]) + 300.0
        here = r.marble(gx - 110.0, gx + 110.0, y0, y0 + 220.0, top, 100.0)
        r.jump("storm step {}".format(i + 1), previous, here, 100.0)
        first_y = first_y or y0
        previous = here
    last_y = previous[4]
    r.wind(gx, (first_y + last_y) / 2.0 + 100.0, top - 250.0, last_y - first_y + 500.0, 700.0, 1100.0, -90.0, 0.0, 600.0, 400.0, 2.0, 2.0, 0.5)
    top += 100.0
    x, y = beyond(previous, N, 330.0, 576.0)
    summit = r.island(x, y, top, 1200.0)
    r.jump("storm step -> summit", previous, summit, 100.0)
    SUMMIT_TOP = top
    smx, smy = middle(summit)
    r.add("lever", "sky", smx - 200.0, smy, top, 0.0, 0.0)
    r.block(smx - 120.0, smx + 120.0, smy + 300.0, smy + 420.0, top, top + 600.0, "sky", "Summit Obelisk")
    r.shaft(smx, smy, top + 4000.0, top, 450.0)
    # The gondola back down, beside the gate roof.
    station = rect(smx + 576.0 + 40.0 + P / 2.0, smy, P)
    r.jump("summit -> gondola", summit, station, 0.0)
    sx_, sy_ = middle(station)
    dest = (GX0 - 40.0 - P / 2.0, 1900.0)
    offset = (dest[0] - sx_, dest[1] - sy_, GATE_TOP - SUMMIT_TOP)
    length = math.sqrt(sum(c * c for c in offset))
    ride, arrive = r.gondola(sx_, sy_, SUMMIT_TOP, offset, length / 700.0)
    r.jump("gondola -> gate roof", arrive, gate_roof, 0.0)

    # =====================================================================================================
    # East: Golden Clockwork
    # =====================================================================================================
    r.add("section", "2 Golden Clockwork")
    bridge_e = r.block(PR - 60.0, 2200.0, -200.0, 200.0, T0 - 80.0, T0, "gold", "East Bridge")
    r.walk_on("plaza -> east bridge", plaza, bridge_e)
    gear_gate = r.block(2200.0, 2800.0, -300.0, 300.0, T0 - 2600.0, T0, "marble", "Gear Gate")
    r.walk_on("east bridge -> gear gate", bridge_e, gear_gate)
    previous, top = gear_gate, T0
    for i, (radius, spin) in enumerate(((180.0, 35.0), (160.0, -45.0), (200.0, 30.0), (160.0, -50.0), (180.0, 40.0))):
        top -= 150.0
        x, y = r.at(previous, E, 0.75, -150.0, 0.92 * radius, side=((150.0 if i % 2 else -150.0) if i else 0.0))
        here = r.gear(x, y, top, radius, spin)
        r.jump("gear down {}".format(i + 1), previous, here, -150.0, 0.85)
        previous = here
    HALL_TOP = top
    x, y = r.at(previous, E, 0.8, 0.0, 700.0)
    hall = r.block(x - 700.0, x + 700.0, -700.0, 700.0, HALL_TOP - 2400.0, HALL_TOP, "marble", "Switch Hall")
    r.jump("gear -> switch hall", previous, hall, 0.0, 0.8)
    hx = x
    r.add("switch", hx - 300.0, -300.0, HALL_TOP)
    r.add("flag", hx + 200.0, -350.0, HALL_TOP)
    r.add("spot", "clock", hx, 0.0, HALL_TOP)
    r.add("sign", hx, 500.0, HALL_TOP + 350.0, -90.0, "Red: flipping floors  /  Blue: the beam")
    r.lamp(hx, 0.0, HALL_TOP + 500.0)
    # Red (east side): two red steps up, two flipping floors, two red steps up; blue (west side): a switch flip, four
    # small blue steps up, then a long narrow beam.
    previous, top = hall, HALL_TOP
    for i in range(2):
        top += 100.0
        x, y = r.at(previous, N, 0.8, 100.0, 150.0, side=(-450.0 if i == 0 else 0.0))
        here = r.sblock(x, y, top, 300.0, True)
        r.jump("red step {}".format(i + 1), previous, here, 100.0, 0.8)
        previous = here
    for i in range(2):
        x, y = r.at(previous, N, 0.6, 0.0, rot / 2.0)
        here = r.rotating(x, y, top)
        r.jump("flipping floor {}".format(i + 1), previous, here, 0.0, 0.6)
        previous = here
    for i in range(2):
        top += 100.0
        x, y = r.at(previous, N, 0.8, 100.0, 150.0)
        here = r.sblock(x, y, top, 300.0, True)
        r.jump("red step {}".format(i + 3), previous, here, 100.0, 0.8)
        previous = here
    LANDING_TOP = top
    x, y = r.at(previous, N, 0.8, 0.0, 400.0)
    clock_landing = r.block(hx - 800.0, hx + 800.0, y - 400.0, y + 400.0, LANDING_TOP - 2400.0, LANDING_TOP, "marble", "Clock Landing")
    r.jump("red step -> clock landing", previous, clock_landing, 0.0, 0.8)
    ly = y
    previous, top = hall, HALL_TOP
    for i in range(4):
        top += 100.0
        x, y = r.at(previous, N, HARD, 100.0, 110.0, side=(450.0 if i == 0 else 0.0))
        here = r.sblock(x, y, top, 220.0, False)
        r.jump("blue step {}".format(i + 1), previous, here, 100.0)
        previous = here
    if previous[4] >= clock_landing[3]:
        raise RuntimeError("The blue steps run past the clock landing")
    beam = r.block(hx - 500.0, hx - 400.0, previous[4], clock_landing[3], top - 60.0, top, "gold", "Narrow Beam")
    r.walk_on("blue step -> beam", previous, beam)
    r.walk_on("beam -> clock landing", beam, clock_landing, LANDING_TOP - top)
    r.add("switch", hx + 500.0, ly - 200.0, LANDING_TOP)
    r.add("rewind", hx, ly, LANDING_TOP)
    r.lamp(hx - 500.0, ly + 200.0, LANDING_TOP + 400.0)
    # The gondola north and up to the balcony; from there the way runs back west.
    station = rect(hx - 800.0 - 40.0 - P / 2.0, ly, P)
    r.jump("clock landing -> gondola", clock_landing, station, 0.0)
    sx_, sy_ = middle(station)
    ride, arrive = r.gondola(sx_, sy_, LANDING_TOP, (0.0, 2400.0, 950.0), 6.0)
    BALCONY_TOP = LANDING_TOP + 950.0
    ax0, ay = arrive[1], middle(arrive)[1]
    balcony = r.block(ax0 - 60.0 - 1500.0, ax0 - 60.0, ay - 600.0, ay + 600.0, BALCONY_TOP - 150.0, BALCONY_TOP, "marble", "Balcony")
    r.jump("gondola -> balcony", arrive, balcony, 0.0)
    bx0, bx1, by0, by1 = balcony[1:]
    r.lamp((bx0 + bx1) / 2.0, ay, BALCONY_TOP + 450.0)
    # Trap: a dark doorway south-east of the balcony.
    alcove = r.block(bx1 - 500.0, bx1, by0 - 220.0 - 500.0, by0 - 220.0, BALCONY_TOP - 100.0, BALCONY_TOP, "stone", "Alcove Floor")
    r.jump("balcony -> alcove", balcony, alcove, 0.0)
    r.block(bx1 - 500.0, bx1, by0 - 820.0, by0 - 720.0, BALCONY_TOP, BALCONY_TOP + 500.0, "stone", "Doorway Wall")
    r.block(bx1 - 350.0, bx1 - 150.0, by0 - 725.0, by0 - 715.0, BALCONY_TOP, BALCONY_TOP + 320.0, "darkstone", "Dark Door")
    r.add("trap", bx1 - 480.0, bx1 - 20.0, by0 - 700.0, by0 - 240.0, BALCONY_TOP)
    # Dead end: hard perches south-west to the speed item.
    previous, top = balcony, BALCONY_TOP
    for i in range(2):
        top += 100.0
        x, y = r.at(previous, S, HARD, 100.0, 80.0, side=((-(bx1 - bx0) / 2.0 + 150.0) if i == 0 else 0.0))
        here = r.block(x - 80.0, x + 80.0, y - 80.0, y + 80.0, top - 60.0, top, "gold", "Perch")
        r.jump("speed perch {}".format(i + 1), previous, here, 100.0)
        previous = here
    r.add("speed", x, y, top)
    # Star coin 2: a ledge north of the balcony, too far for a plain jump: a run with the speed item clears it.
    far = r.block(bx0 + 500.0, bx0 + 800.0, by1 + 820.0, by1 + 1120.0, BALCONY_TOP - 60.0, BALCONY_TOP, "gold", "Far Ledge")
    if gap(balcony, far) < r.reach(0.0):
        raise RuntimeError("The far ledge can be reached without the speed item")
    r.jump("balcony -> far ledge (speed run)", balcony, far, 0.0, 0.6 * SPEED_ITEM_SPEED / r.walk)
    r.add("coin", bx0 + 650.0, by1 + 970.0, BALCONY_TOP)
    # The way on: west, up a piston, two gears, a crumbling floor, the clock top.
    top = BALCONY_TOP
    x, y = r.at(balcony, W, EASY, 0.0, P / 2.0)
    piston, _ = r.moving(x, y, top, (0.0, 0.0, 500.0), 2.4, 1.0)
    r.jump("balcony -> piston", balcony, piston, 0.0, EASY)
    top += 500.0
    previous = piston
    for i, (radius, spin) in enumerate(((170.0, 35.0), (150.0, -45.0))):
        top += 100.0
        x, y = r.at(previous, W, 0.75, 100.0, 0.92 * radius, side=(-150.0 if i else 150.0))
        here = r.gear(x, y, top, radius, spin)
        r.jump("clock gear {}".format(i + 1), previous, here, 100.0, 0.85)
        previous = here
    x, y = r.at(previous, W, 0.8, 0.0, P / 2.0)
    crumble = r.falling(x, y, top)
    r.jump("gear -> crumbling floor", previous, crumble, 0.0, 0.8)
    top += 100.0
    x, y = r.at(crumble, W, 0.85, 100.0, 500.0)
    clock_top = r.block(x - 500.0, x + 500.0, y - 500.0, y + 500.0, top - 2600.0, top, "gold", "Clock Top")
    r.jump("crumbling floor -> clock top", crumble, clock_top, 100.0, 0.85)
    CLOCK_TOP = top
    ctx, cty = x, y
    r.add("lever", "clock", ctx + 200.0, cty + 200.0, top, 180.0, 0.0)
    r.lamp(ctx, cty, top + 500.0)
    # Lever 2 also raises a brass stair from the clock top's south edge back down to the plaza's north-east rim.
    rim = (PR * math.cos(math.radians(40.0)), PR * math.sin(math.radians(40.0)))
    r.stair("clock", "Brass Step", clock_top, CLOCK_TOP, plaza, T0, (ctx, clock_top[3]), rim, 18, 280.0, 80.0, 1600.0, 0.15, "gold")

    # =====================================================================================================
    # South: Underworks
    # =====================================================================================================
    r.add("section", "3 Underworks")
    UX0, UX1, UY0, UY1 = -3000.0, 3000.0, -9400.0, -2600.0
    UF = T0 - 3000.0
    CEIL = T0 - 300.0
    WALL_T = 200.0
    BOTTOM = UF - 1200.0
    DOOR_Z = T0 - 600.0
    holes = [(-1400.0, -1000.0, -4400.0, -4000.0), (1300.0, 1700.0, -6500.0, -6100.0), (-1700.0, -1300.0, -6500.0, -6100.0),
             (-200.0, 200.0, -8600.0, -8200.0), (2200.0, 2600.0, -5000.0, -4600.0), (-2600.0, -2200.0, -8000.0, -7600.0)]
    for part in with_holes((UX0 - WALL_T, UX1 + WALL_T, UY0 - WALL_T, UY1 + WALL_T), holes):
        r.block(part[0], part[1], part[2], part[3], CEIL, CEIL + 100.0, "stone", "Underworks Roof")
    for x0, x1, y0, y1 in holes:
        r.add("glass", x0, x1, y0, y1, CEIL, CEIL + 100.0)
        r.shaft((x0 + x1) / 2.0, (y0 + y1) / 2.0, CEIL + 100.0, UF, 170.0)
    r.block(UX0 - WALL_T, UX0, UY0 - WALL_T, UY1 + WALL_T, BOTTOM, CEIL, "stone", "Underworks Wall")
    r.block(UX1, UX1 + WALL_T, UY0 - WALL_T, UY1 + WALL_T, BOTTOM, CEIL, "stone", "Underworks Wall")
    r.block(UX0, UX1, UY0 - WALL_T, UY0, BOTTOM, CEIL, "stone", "Underworks Wall")
    # The north wall, with the doorway (x -300..300, from the sill up to the roof).
    r.block(UX0, -300.0, UY1, UY1 + WALL_T, BOTTOM, CEIL, "stone", "Underworks Wall")
    r.block(300.0, UX1, UY1, UY1 + WALL_T, BOTTOM, CEIL, "stone", "Underworks Wall")
    sill = r.block(-300.0, 300.0, UY1, UY1 + WALL_T, BOTTOM, DOOR_Z, "stone", "Door Sill")
    # Down from the plaza: eight steps south to the doorway.
    previous, top = plaza, T0
    for i in range(8):
        top -= 75.0
        y1 = -1600.0 - 100.0 * i + (40.0 if i == 0 else 0.0)
        here = r.block(-300.0, 300.0, -1700.0 - 100.0 * i, y1, top - 100.0, top, "marble", "Stair Down")
        r.jump("stair down {}".format(i + 1), previous, here, -75.0, EASY)
        previous = here
    r.walk_on("stair -> doorway", previous, sill, DOOR_Z - top)
    mouth = r.block(-600.0, 600.0, -3400.0, UY1, DOOR_Z - 200.0, DOOR_Z, "darkstone", "Well Mouth")
    r.walk_on("doorway -> well mouth", sill, mouth)
    r.lamp(0.0, -3000.0, DOOR_Z + 220.0, (140, 170, 255))
    r.add("sign", 0.0, -3350.0, DOOR_Z + 250.0, 90.0, "Drop ledges  /  Slow lift")
    # Down two ways: drop ledges, west then south then east (quick), or the slow lift (safe).
    previous, top = mouth, DOOR_Z
    drops = []
    for i, direction in enumerate((W, W, W, S, S, E, E)):
        top -= 300.0
        x, y = r.at(previous, direction, 0.5, -300.0, 150.0, side=(200.0 if i == 0 else 0.0))
        here = r.block(x - 150.0, x + 150.0, y - 150.0, y + 150.0, top - 100.0, top, "darkstone", "Drop Ledge")
        r.jump("drop ledge {}".format(i + 1), previous, here, -300.0, 0.5)
        drops.append((here, top))
        previous = here
    north_floor = r.block(UX0, UX1, -5200.0, UY1, BOTTOM, UF, "darkstone", "North Floor")
    r.jump("drop ledge -> floor", previous, north_floor, UF - top)
    # Star coin 5: a hidden ledge tucked in under drop ledge 3, a jump back north from ledge 4.
    l3, _ = drops[2]
    l4, l4_top = drops[3]
    hx3, hy3 = middle(l3)
    hidden = r.block(hx3 + 180.0 - 120.0, hx3 + 180.0 + 120.0, hy3 - 120.0, hy3 + 120.0, l4_top - 400.0, l4_top - 300.0, "darkstone", "Hidden Ledge")
    r.jump("drop ledge 4 -> hidden ledge", l4, hidden, -300.0, 0.6)
    r.add("coin", hx3 + 180.0, hy3, l4_top - 300.0)
    x, y = beyond(mouth, S, 60.0, P / 2.0)
    lift, _ = r.moving(x, y, DOOR_Z, (0.0, 0.0, UF - DOOR_Z), 7.0, 2.0)
    r.jump("well mouth -> slow lift", mouth, lift, 0.0)
    r.add("flag", 700.0, -4300.0, UF)
    r.add("spot", "under", 400.0, -4300.0, UF)
    r.lamp(700.0, -4300.0, UF + 400.0, (140, 170, 255))
    # The pit: along the flame bridge (east) or on stones a pressure plate raises for a while (west).
    PIT0, PIT1 = -7400.0, -5200.0
    south_floor = r.block(UX0, UX1, UY0, PIT0, BOTTOM, UF, "darkstone", "South Floor")
    r.add("catcher", UX0, UX1, PIT0, PIT1, BOTTOM - 200.0)
    flame_bridge = r.block(1400.0, 1600.0, PIT0, PIT1, BOTTOM, UF, "darkstone", "Flame Bridge")
    r.walk_on("north floor -> flame bridge", north_floor, flame_bridge)
    r.walk_on("flame bridge -> south floor", flame_bridge, south_floor)
    for i in range(5):
        r.add("flame", 1500.0, PIT1 - 250.0 - 425.0 * i, UF, 90.0, 0.45 * i, 0.6, 1.0, 1.6, "under")
    r.add("sign", 1500.0, -4900.0, UF + 350.0, 90.0, "Flames")
    r.add("lever", "plate", -1500.0, -4950.0, UF, 0.0, 9.0)
    r.add("sign", -1500.0, -4600.0, UF + 350.0, 90.0, "Stones")
    previous = north_floor
    stone_y = PIT1
    for i in range(3):
        y = stone_y - 325.0 - 150.0
        here = rect(-1500.0, y, 300.0)
        r.add("mech", "plate", -1500.0, y, UF - 800.0, (300.0, 300.0, 200.0), (0.0, 0.0, 800.0), 0.3 + 0.3 * i, 0.8, (6.0, 1.5), "stone", "Pit Stone")
        r.jump("pit stone {}".format(i + 1), previous, here, 0.0)
        previous, stone_y = here, y - 150.0
    r.jump("pit stone -> south floor", previous, south_floor, 0.0)
    # Up: the heaven-or-hell birdcages (the heaven one carries the player up to the gallery) or the ledge-grab chimney.
    GAL = UF + 1500.0
    gallery = r.block(-700.0, UX1, UY0, UY0 + 600.0, GAL - 200.0, GAL, "darkstone", "Gallery")
    walkway = r.block(UX0, -700.0, UY0 + 200.0, UY0 + 400.0, GAL - 100.0, GAL, "darkstone", "Gallery Walkway")
    r.walk_on("gallery -> walkway", gallery, walkway)
    r.add("cages", 0.0, -8000.0, UF, (300.0, UY0 + 300.0, GAL), 2)
    r.add("sign", 0.0, -7600.0, UF + 450.0, 90.0, "Heaven or Hell  /  Climb (Q)")
    previous, top = south_floor, UF
    for i, rise in enumerate((220.0, 220.0, 220.0, 220.0, 220.0, 220.0, 180.0)):
        top += rise
        x0 = -2500.0 + 300.0 * i
        here = r.block(x0, x0 + 300.0, UY0 + 600.0, UY0 + 900.0, UF, top, "stone", "Chimney Block")
        r.grab("chimney {}".format(i + 1), previous, here, rise)
        previous = here
    r.walk_on("chimney -> gallery", previous, gallery, GAL - top)
    r.lamp(-1500.0, UY0 + 300.0, GAL + 300.0, (140, 170, 255))
    # Star coin 3: the walkway's west end past three flame jets.
    for i in range(3):
        r.add("flame", -1100.0 - 500.0 * i, UY0 + 300.0, GAL, 0.0, 0.5 * i, 0.6, 1.0, 1.4, "under")
    r.add("coin", -2800.0, UY0 + 300.0, GAL)
    # North along the east side: fading steps, a piston, a crumbling floor, the lever gallery.
    previous, top = gallery, GAL
    gcx, _ = middle(gallery)
    for i in range(3):
        top += 100.0
        x, y = r.at(previous, N, 0.8, 100.0, P / 2.0, side=((gcx - 2500.0) if i == 0 else 0.0))
        here = r.timed(x, y, top, 0.6 * i)
        r.jump("fading step {}".format(i + 1), previous, here, 100.0, 0.8)
        previous = here
    x, y = r.at(previous, N, EASY, 0.0, P / 2.0)
    piston, _ = r.moving(x, y, top, (0.0, 0.0, 400.0), 2.6, 1.0)
    r.jump("fading step -> piston", previous, piston, 0.0, EASY)
    top += 400.0
    x, y = r.at(piston, N, 0.8, 100.0, P / 2.0)
    top += 100.0
    crumble = r.falling(x, y, top)
    r.jump("piston -> crumbling floor", piston, crumble, 100.0, 0.8)
    top += 100.0
    x, y = r.at(crumble, N, 0.8, 100.0, 500.0)
    lever_gallery = r.block(1900.0, UX1, y - 500.0, y + 500.0, top - 200.0, top, "darkstone", "Lever Gallery")
    r.jump("crumbling floor -> lever gallery", crumble, lever_gallery, 100.0, 0.8)
    LG_TOP = top
    lgx, lgy = (1900.0 + UX1) / 2.0, y
    if LG_TOP > CEIL - 250.0:
        raise RuntimeError("The lever gallery is too close under the roof: {:.0f}".format(CEIL - LG_TOP))
    r.add("lever", "under", lgx, lgy, LG_TOP, 90.0, 0.0)
    r.lamp(lgx, lgy, LG_TOP + 200.0, (140, 170, 255))
    # Lever 3 also raises a stone bridge from the lever gallery west to the well mouth.
    r.stair("under", "Bridge Stone", lever_gallery, LG_TOP, mouth, DOOR_Z, (1900.0, lgy), (600.0, -3000.0), 5, 260.0, 100.0, 1500.0, 0.25, "stone")

    # Catchers: under the sky and the clockwork, around the underworks (which has its own in the pit).
    xs = [p[1] for p in r.pieces if p[0] in ("island", "cloud", "vanish", "mover", "gear", "sblock", "timed", "falling")]
    ys = [p[2] for p in r.pieces if p[0] in ("island", "cloud", "vanish", "mover", "gear", "sblock", "timed", "falling")]
    X0, X1, Y0, Y1 = min(xs) - 3000.0, max(xs) + 3000.0, min(ys + [UY0]) - 3000.0, max(ys) + 3000.0
    M = 200.0
    r.add("catcher", X0, UX0 - WALL_T - M, Y0, Y1, T0 - 900.0)
    r.add("catcher", UX1 + WALL_T + M, X1, Y0, Y1, T0 - 1800.0)
    r.add("catcher", UX0 - WALL_T - M, UX1 + WALL_T + M, UY1 + WALL_T + M, Y1, T0 - 1800.0)
    r.add("catcher", UX0 - WALL_T - M, UX1 + WALL_T + M, Y0, UY0 - WALL_T - M, T0 - 1800.0)
    r.bounds = (X0, X1, Y0, Y1)
    r.under = (UX0 - WALL_T, UX1 + WALL_T, UY0 - WALL_T, UY1 + WALL_T)

    r.summit_top, r.gate_top = SUMMIT_TOP, GATE_TOP
    r.heights = {"plaza": T0, "fork": FORK_TOP, "sun terrace": TS, "upper terrace": TU, "summit": SUMMIT_TOP,
                 "switch hall": HALL_TOP, "clock landing": LANDING_TOP, "balcony": BALCONY_TOP, "clock top": CLOCK_TOP,
                 "underworks floor": UF, "gallery": GAL, "lever gallery": LG_TOP}
    return r


if __name__ == "__main__":
    route = build(22610.0, 500.9, 980.0, 600.0, 300.0)
    for name, g, rise, limit in route.checks:
        print("  {:<40} gap {:>5.0f} rise {:>6.0f} (limit {:>5.0f}){}".format(name, g, rise, limit, "  TIGHT" if g > 0.85 * limit else ""))
    for name, z in route.heights.items():
        print("  {:<18} {:>7.0f}  ({:+.0f} from the plaza)".format(name, z, z - route.heights["plaza"]))
    print("bounds {}".format(route.bounds))
    print("pieces {}, jumps {}".format(len(route.pieces), len(route.checks)))
