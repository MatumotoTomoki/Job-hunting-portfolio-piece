# The heaven area's (area 4, the last one) route as plain data, checked jump by jump; build_area4_heaven.py places it.
# No Unreal here, so it can be checked on its own:
#   python area4_layout.py          (prints every jump; fails on one out of reach)
# "Heaven that lost its light", climbed layer on layer (agreed 2026-11-15: a climbing game ends climbing). The light has
# hidden in the Iwato on top of the dark tower; heaven is dim until it opens.
#   1 Spider Threads  from area 3's cloud sea up three threads (two swinging, two that snap) to the forest's floor; a
#                     star coin on a perch only a leap off the second thread reaches.
#   2 Jewel Forest    south, climbing: a melody stair, vanishing clouds in a crosswind, flag 1; two ways up: a rising
#                     melody net (timing) or marble posts (precision); a fast rising melody to shard 1 (a star coin on a
#                     jewel that rings rarely); a thread up to the next layer.
#   3 Upside Down     east, climbing by falling up: walk off a ledge into a gravity zone, fall up to the ceiling, cross it
#                     upside down, walk out of the zone and drop onto a ledge higher than the last. Flag 2 on the first
#                     landing; two lanes for the middle two zones (gears, gaps and fading steps / red and blue blocks
#                     with a ceiling switch); shard 2 on the last landing; a star coin on a side ceiling.
#   4 Dark Tower      inside, two ways to the middle floor (flag 3): light platforms blinking one after another, or dark
#                     ledges and ledge grabs; then platforms lit by two beams in turn, a sweeping beam and a last climb
#                     to the top floor (shard 3) and up through a hole onto the roof. A star coin on a rarely lit
#                     platform.
#   5 Iwato           on the roof: the rock blocks the way to the sky; all three shards open it, the level lights up,
#                     the wings lie behind it (flag 4).
#   6 Heaven's Gate   glide out to updrafts and ride them up island by island to the gate (the goal, a placeholder);
#                     a star coin on a side island.
# Pieces (heights are the top a player stands on unless said otherwise; x, y the middle). As in area 3 / the first
# area 4 (see git) plus:
#   ("beam", name, x, y, z0, z1, width, on, off, delay, (dx, dy, dz), move_seconds)     BP_LightBeam
#   ("lplat", beam, x, y, top, size)                     BP_LightPlatform (40 thick), solid while its beam is lit
#   ("jewel", x, y, top, r, start, ring, loop, beat, pitch)   BP_ChimeJewel (40 thick)
#   ("thread", x, y, anchor, length, swing_deg, swing_sec, offset, hold, yaw)   BP_SpiderThread (yaw turns the swing)
#   ("gzone", x0, x1, y0, y1, z0, z1, (dx, dy, dz))      BP_GravityZone
#   ("under", x0, x1, y0, y1, under, thick, look, name)  a slab walked on upside down: `under` is its underside
#   ("gear_flip", x, y, under, r, spin), ("sblock_flip", x, y, under, size, red), ("switch_flip", x, y, under),
#   ("timed_flip", x, y, under, delay), ("switch", x, y, top)
#   ("shard", name, x, y, top), ("wings", x, y, top), ("hidden_lever", name, x, y, z)
#   ("iwato", x, y, z, yaw, lever, (eye), (look))        BP_Iwato counting shards 1..3
import math

from area3_layout import Route as SkyRoute, rect, circle, middle, gap, beyond

HARD, MID, EASY = 0.9, 0.75, 0.6
GRAB_MIN, GRAB_MAX = 160.0, 230.0
E, N, W, S = (1, 0), (0, 1), (-1, 0), (0, -1)
PENTA = (1.0, 9.0 / 8.0, 5.0 / 4.0, 3.0 / 2.0, 5.0 / 3.0, 2.0)
THREAD_HANG = 210.0          # a player at the top of a thread stands this far below its anchor
LEAP_SIDE, LEAP_UP = 450.0, 520.0
GLIDE_FALL = 160.0


class Route(SkyRoute):
    def __init__(self, base, jump_z, gravity, walk, plat):
        SkyRoute.__init__(self, base, jump_z, gravity, walk, plat)

    # ----- checks -----
    def jump(self, name, a, b, rise, ratio=HARD):
        g = gap(a, b)
        limit = ratio * self.reach(rise) + 1.0
        self.checks.append((name, g, rise, limit))
        if rise > 0.8 * self.apex or g > limit:
            raise RuntimeError("Out of reach: {} gap {:.0f} rise {:.0f} (limit {:.0f})".format(name, g, rise, limit))

    def flipped(self, name, a, a_under, b, b_under, ratio=HARD):
        # A jump walking upside down: "up" is down in the world.
        self.jump(name + " (upside down)", a, b, a_under - b_under, ratio)

    def at(self, previous, direction, ratio, rise, size_half, side=0.0):
        return beyond(previous, direction, ratio * self.reach(rise), size_half, side)

    def grab(self, name, a, b, rise):
        g = gap(a, b)
        self.checks.append((name + " (grab)", g, rise, 60.0))
        if not GRAB_MIN <= rise <= GRAB_MAX or g > 60.0:
            raise RuntimeError("Can't grab: {} gap {:.0f} rise {:.0f}".format(name, g, rise))

    def walk_on(self, name, a, b, rise=0.0):
        g = gap(a, b)
        self.checks.append((name + " (walk)", g, rise, 40.0))
        if g > 40.0 or rise > 60.0:
            raise RuntimeError("Not joined: {} gap {:.0f} rise {:.0f}".format(name, g, rise))

    def catch(self, name, a, a_top, x, y, bottom, ratio=HARD):
        # Jumping off a ledge at a thread: its bottom must hang no higher than a jump, it must be in reach.
        g = gap(a, circle(x, y, 40.0))
        limit = ratio * self.reach(0.0) + 1.0
        self.checks.append((name + " (catch)", g, bottom - a_top, limit))
        if bottom > a_top + 150.0 or g > limit:
            raise RuntimeError("Can't catch: {} gap {:.0f}, thread bottom {:.0f} over the ledge".format(name, g, bottom - a_top))

    def leap(self, name, x, y, anchor, b, b_top, ratio=HARD):
        # Letting go at the top of a thread: launched LEAP_SIDE along, LEAP_UP up (the swing not counted).
        rise = b_top - (anchor - THREAD_HANG)
        up = LEAP_UP * LEAP_UP / (2.0 * self.gravity)
        g = gap(circle(x, y, 40.0), b)
        limit = 0.0 if rise > 0.8 * up else ratio * LEAP_SIDE * (LEAP_UP / self.gravity + math.sqrt(2.0 * (up - rise) / self.gravity)) + 1.0
        self.checks.append((name + " (leap)", g, rise, limit))
        if g > limit:
            raise RuntimeError("Can't leap: {} gap {:.0f} rise {:.0f} (limit {:.0f})".format(name, g, rise, limit))

    def glide(self, name, a, a_top, b, b_top, ratio=0.8):
        # With the wings: a jump, then held to GLIDE_FALL on the way down.
        drop = a_top - b_top
        limit = 0.0 if drop < -0.6 * self.apex else ratio * self.walk * (self.jump_z / self.gravity + (self.apex + drop) / GLIDE_FALL) + 1.0
        g = gap(a, b)
        self.checks.append((name + " (glide)", g, -drop, limit))
        if g > limit:
            raise RuntimeError("Can't glide: {} gap {:.0f} drop {:.0f} (limit {:.0f})".format(name, g, drop, limit))

    # ----- pieces -----
    def block(self, x0, x1, y0, y1, z0, z1, look="marble", name="Block"):
        self.add("block", x0, x1, y0, y1, z0, z1, look, name)
        return ("rect", x0, x1, y0, y1)

    def disk(self, x, y, top, r, thick=200.0, look="marble", name="Disk"):
        self.add("disk", x, y, top, r, thick, look, name)
        return circle(x, y, r)

    def under(self, x0, x1, y0, y1, under, thick=100.0, look="stone", name="Ceiling"):
        self.add("under", x0, x1, y0, y1, under, thick, look, name)
        return ("rect", x0, x1, y0, y1)

    def jewel(self, x, y, top, r, start, ring=2, loop=8, beat=0.7, pitch=1.0):
        self.add("jewel", x, y, top, r, start, ring, loop, beat, pitch)
        return circle(x, y, r)

    def lplat(self, beam, x, y, top, size):
        self.add("lplat", beam, x, y, top, size)
        return rect(x, y, size)

    def beam(self, name, x, y, z0, z1, width, on=0.0, off=0.0, delay=0.0, move=(0.0, 0.0, 0.0), move_seconds=0.0):
        self.add("beam", name, x, y, z0, z1, width, on, off, delay, move, move_seconds)

    def thread(self, x, y, anchor, length, swing=0.0, seconds=3.5, offset=0.0, hold=0.0, yaw=0.0):
        self.add("thread", x, y, anchor, length, swing, seconds, offset, hold, yaw)

    def gzone(self, x0, x1, y0, y1, z0, z1, direction=(0.0, 0.0, 1.0)):
        self.add("gzone", x0, x1, y0, y1, z0, z1, direction)

    def moving(self, x, y, top, offset, seconds, wait, size=None):
        # size: a bigger floor (the actor scaled across; only straight-up moves then, as the offset scales too).
        if size:
            if offset[0] or offset[1]:
                raise RuntimeError("A resized moving platform can only move up and down")
            self.add("moving", x, y, top, offset, seconds, wait, size)
        else:
            self.add("moving", x, y, top, offset, seconds, wait)
        s = size or self.plat
        return rect(x, y, s), rect(x + offset[0], y + offset[1], s)

    def gondola(self, x, y, top, offset, seconds):
        self.add("gondola", x, y, top, offset, seconds)
        return rect(x, y, self.plat), rect(x + offset[0], y + offset[1], self.plat)

    def lamp(self, x, y, z, color=(255, 214, 160)):
        self.add("lamp", x, y, z, color)

    def shaft(self, x, y, z_top, z_bottom, r=160.0):
        self.add("shaft", x, y, z_top, z_bottom, r)




def ceiling_run(r, y, x, under, items, label):
    # Upside-down pieces eastward from x (the west end of an 800 cm first slab, `under` its underside). Items:
    #   ("gap", du, length, ratio)   a slab `length` long        ("gear", du, radius, spin, ratio)
    #   ("fade", du, delay, ratio)   a fading step               ("red" / "blue", du, ratio)  a switch block
    #   ("switch", du, ratio)        a slab with a ceiling switch
    # du: the piece's underside above `under` (higher underside = a drop when upside down). Returns the last piece,
    # its underside and the run's east end.
    first = r.under(x, x + 800.0, y - 250.0, y + 250.0, under, look="stone", name="Ceiling")
    previous, prev_under, end = first, under, x + 800.0
    for n, item in enumerate(items):
        kind, du, ratio = item[0], item[1], item[-1]
        u = under + du
        g = ratio * r.reach(prev_under - u)
        if kind == "gap":
            here = r.under(end + g, end + g + item[2], y - 250.0, y + 250.0, u, look="stone", name="Ceiling")
            end += g + item[2]
        elif kind == "gear":
            radius = item[2]
            cx = end + g + 0.92 * radius
            r.add("gear_flip", cx, y, u, radius, item[3])
            here = circle(cx, y, 0.92 * radius)
            end = cx + 0.92 * radius
        elif kind == "fade":
            cx = end + g + r.plat / 2.0
            r.add("timed_flip", cx, y, u, item[2])
            here = rect(cx, y, r.plat)
            end = cx + r.plat / 2.0
        elif kind in ("red", "blue"):
            cx = end + g + 110.0
            r.add("sblock_flip", cx, y, u, 220.0, kind == "red")
            here = rect(cx, y, 220.0)
            end = cx + 110.0
        elif kind == "switch":
            here = r.under(end + g, end + g + 600.0, y - 250.0, y + 250.0, u, look="stone", name="Switch Ceiling")
            r.add("switch_flip", end + g + 300.0, y, u)
            end += g + 600.0
        else:
            raise RuntimeError("Unknown ceiling item " + kind)
        r.flipped("{} {}".format(label, n + 1), previous, prev_under, here, u, ratio)
        previous, prev_under = here, u
    return previous, prev_under, end


def build(base, jump_z, gravity, walk, plat):
    r = Route(base, jump_z, gravity, walk, plat)
    B = base
    heights = {"start": B}

    # =====================================================================================================
    # 1 Spider Threads
    # =====================================================================================================
    r.add("section", "1 Spider Threads")
    start = r.island(-3000.0, 0.0, B, 1000.0)
    r.add("start", -3000.0, 0.0, B, 0.0)
    r.add("spot", "start", -3000.0, 0.0, B)
    r.add("sign", -2800.0, 300.0, B + 380.0, 180.0, "Climb the thread  (W / S,  Jump to let go)")
    JF = B + 4200.0
    threads = [(-2220.0, B + 100.0, B + 1600.0, 0.0, 3.5, 0.0, 0.0),
               (-1170.0, B + 1300.0, B + 3110.0, 22.0, 3.6, 0.0, 6.0),
               (-70.0, B + 2800.0, JF + 210.0, 26.0, 3.2, 1.0, 5.0)]
    ledges = [(-1870.0, -1570.0, B + 1400.0), (-790.0, -490.0, B + 2900.0), (310.0, 1500.0, JF)]
    previous, previous_top = start, B
    for i, (tx, bottom, anchor, swing, seconds, offset, hold) in enumerate(threads):
        r.thread(tx, 0.0, anchor, anchor - bottom, swing, seconds, offset, hold, 0.0)
        r.catch("thread {}".format(i + 1), previous, previous_top, tx, 0.0, bottom)
        x0, x1, top = ledges[i]
        ledge = r.block(x0, x1, -300.0 if i == 2 else -150.0, 300.0 if i == 2 else 150.0, top - 100.0, top,
                        "marble" if i < 2 else "gold", "Thread Ledge" if i < 2 else "Forest Floor")
        r.leap("thread {} -> ledge".format(i + 1), tx, 0.0, anchor, ledge, top)
        previous, previous_top = ledge, top
    forest_floor = previous
    perch = r.block(-1245.0, -1095.0, -650.0, -500.0, B + 2500.0, B + 2600.0, "gold", "Coin Perch")
    r.leap("thread 2 -> coin perch", threads[1][0], 0.0, threads[1][2], perch, B + 2600.0)
    r.catch("coin perch -> thread 2", perch, B + 2600.0, threads[1][0], 0.0, threads[1][1])
    r.add("coin", -1170.0, -575.0, B + 2600.0)
    heights["forest floor"] = JF

    # =====================================================================================================
    # 2 Jewel Forest (south, climbing)
    # =====================================================================================================
    r.add("section", "2 Jewel Forest")
    JR = 110.0
    previous, top = forest_floor, JF
    for i in range(6):
        top += 80.0
        x, y = r.at(previous, S, 0.45, 80.0, JR, side=(90.0 if i % 2 else -90.0))
        here = r.jewel(x, y, top, JR, i, beat=1.0, pitch=PENTA[i])   # (beats tuned by the user, 2026-11-16)
        r.jump("melody stair {}".format(i + 1), previous, here, 80.0, 0.5)
        previous = here
    top += 80.0
    x, y = r.at(previous, S, 0.7, 80.0, 0.48 * 700.0)
    rest = r.island(x, y, top, 700.0)
    r.jump("melody stair -> rest", previous, rest, 80.0, MID)
    previous = rest
    # Two moving islands carrying the player south and up (the vanishing clouds in a crosswind here were too much:
    # the user found them impossible, 2026-11-16).
    # Both move in step (same timing, from the level's start), so the second one runs the other way: it starts at its
    # far end and comes back to meet the first exactly when the first arrives (in step they never met, 2026-11-16).
    x, y = r.at(previous, S, 0.6, 0.0, 0.48 * 350.0)
    ride, arrive = r.mover(x, y, top, (0.0, -1100.0, 250.0), 4.0, 1.5)
    r.jump("rising island 1", previous, ride, 0.0, MID)
    top += 250.0
    x, y = r.at(arrive, S, 0.6, 0.0, 0.48 * 350.0)
    far, near = r.mover(x, y - 1100.0, top + 250.0, (0.0, 1100.0, -250.0), 4.0, 1.5)
    r.jump("rising island 1 -> 2 (they meet)", arrive, near, 0.0, MID)
    top += 250.0
    previous = far
    top += 100.0
    x, y = r.at(previous, S, 0.6, 100.0, 0.48 * 900.0)
    fork = r.island(x, y, top, 900.0)
    r.jump("rising island -> fork", previous, fork, 100.0, MID)
    FORK = top
    fx, fy = middle(fork)
    r.add("flag", fx + 150.0, fy, FORK)
    r.add("spot", "jewel", fx, fy, FORK)
    r.add("sign", fx - 250.0, fy, FORK + 380.0, 90.0, "Melody Net  /  High Posts")
    # Way A: a rising melody net, each jewel ringing one beat after the last (loop 6, two beats each).
    previous, top = fork, FORK
    for i in range(7):
        top += 70.0
        x, y = r.at(previous, S, 0.45, 70.0, JR, side=(-250.0 if i == 0 else (120.0 if i % 2 else -120.0)))
        here = r.jewel(x, y, top, JR, i % 6, 2, 6, 0.9, PENTA[i % 6])
        r.jump("melody net {}".format(i + 1), previous, here, 70.0, 0.55)
        previous = here
    MEET = top + 70.0
    x, y = r.at(previous, S, 0.6, 70.0, 0.48 * 1400.0, side=250.0)
    meet = r.island(x, y, MEET, 1400.0)
    r.jump("melody net -> meeting island", previous, meet, 70.0, MID)
    # Way B: marble posts east of the net, up 100 a post, then level ones until the meeting island is in reach.
    previous, top = fork, FORK
    y = fy - 150.0
    i = 0
    while True:
        step = min(100.0, MEET - top) if top < MEET else 0.0
        top += step
        here = r.block(fx + 650.0 - 70.0, fx + 650.0 + 70.0, y - 70.0, y + 70.0, top - 2500.0, top, "marble", "High Post")
        r.jump("high post {}".format(i + 1), previous, here, step, HARD)
        previous = here
        i += 1
        if gap(here, meet) <= 0.85 * r.reach(MEET - top) and top >= MEET:
            break
        y -= 140.0 + 0.85 * r.reach(min(100.0, MEET - top) if top < MEET else 0.0)
    r.jump("high post -> meeting island", previous, meet, MEET - top, HARD)
    # Up a fast melody to shard 1; a jewel ringing rarely beside it holds a star coin.
    previous, top = meet, MEET
    for i in range(6):
        top += 80.0
        x, y = r.at(previous, S, 0.45 if i == 0 else 0.5, 80.0, JR, side=(-250.0 if i == 0 else 0.0))
        here = r.jewel(x, y, top, JR, i, 2, 8, 0.85, PENTA[i])
        r.jump("fast melody {}".format(i + 1), previous, here, 80.0, 0.55)
        if i == 2:
            sx, sy = x - 2.0 * JR - 0.45 * r.reach(0.0), y
            side_jewel = r.jewel(sx, sy, top, JR, 10, 2, 16, 0.85, 2.0)
            r.jump("fast melody 3 -> coin jewel", here, side_jewel, 0.0, 0.5)
            r.add("coin", sx, sy, top)
        previous = here
    top += 80.0
    x, y = r.at(previous, S, 0.7, 80.0, 0.48 * 800.0)
    shard1 = r.island(x, y, top, 800.0)
    r.jump("fast melody -> shard island", previous, shard1, 80.0, MID)
    s1x, s1y = middle(shard1)
    r.add("shard", "shard1", s1x, s1y, top)
    r.lamp(s1x, s1y, top + 600.0, (190, 230, 255))
    heights["jewel fork"], heights["shard 1"] = FORK, top
    # A thread up off its east side to the next layer.
    tx, ty = s1x + 0.48 * 800.0 + 380.0, s1y
    bottom = top + 50.0
    anchor = bottom + 1700.0
    r.thread(tx, ty, anchor, anchor - bottom, 12.0, 4.0, 0.0, 0.0, 90.0)
    r.catch("shard island -> thread", shard1, top, tx, ty, bottom)
    F0 = anchor - THREAD_HANG
    floor = r.block(tx + 380.0, tx + 1180.0, ty - 400.0, ty + 400.0, F0 - 200.0, F0, "marble", "Upside Down Floor")
    r.leap("thread -> upside down floor", tx, ty, anchor, floor, F0)

    # =====================================================================================================
    # 3 Upside Down (east, climbing by falling up)
    # =====================================================================================================
    r.add("section", "3 Upside Down")
    LY = ty
    RISE = 900.0

    # Zone 1 (one lane).
    zx0 = tx + 1180.0 + 60.0
    cu = F0 + RISE
    last, last_u, end = ceiling_run(r, LY, tx + 1180.0 - 300.0, cu, (
        ("gap", -100.0, 400.0, 0.85), ("gear", -100.0, 240.0, 40.0, 0.75), ("fade", 0.0, 0.0, 0.8),
        ("gap", 0.0, 500.0, 0.85)), "ceiling 1")
    z_end = end + 200.0
    r.under(end, z_end + 400.0, LY - 250.0, LY + 250.0, last_u, look="stone", name="Ceiling")
    r.gzone(zx0, z_end, LY - 600.0, LY + 600.0, F0 - 400.0, cu + 800.0)
    r.add("catcher", zx0, z_end, LY - 600.0, LY + 600.0, cu + 450.0)   # fell up through a gap: back to the flag
    L1 = min(cu, last_u) - 350.0
    landing1 = r.block(z_end + 60.0, z_end + 960.0, LY - 1400.0, LY + 1500.0, L1 - 200.0, L1, "marble", "Landing")
    r.add("flag", z_end + 500.0, LY, L1)
    r.add("spot", "flip", z_end + 500.0, LY, L1)
    r.add("switch", z_end + 500.0, LY + 1100.0, L1)
    r.add("sign", z_end + 500.0, LY + 600.0, L1 + 380.0, 180.0, "Gears and gaps  /  Red and blue")
    heights["landing 1"] = L1
    # Zones 2 and 3: two lanes, south (gears, gaps, fading steps) and north (switch blocks).
    previous_landings = {LY - 800.0: (landing1, L1), LY + 900.0: (landing1, L1)}
    lane_items = {
        2: {LY - 800.0: (("gap", -100.0, 300.0, 0.88), ("fade", -100.0, 0.0, 0.85), ("gear", 0.0, 220.0, -50.0, 0.75),
                         ("fade", 0.0, 1.0, 0.85), ("gap", 100.0, 300.0, 0.88), ("gap", 0.0, 500.0, 0.85)),
            LY + 900.0: (("red", -100.0, 0.85), ("red", 0.0, 0.85), ("switch", 0.0, 0.7), ("blue", 100.0, 0.85),
                         ("blue", 0.0, 0.85), ("gap", 0.0, 500.0, 0.8))},
        3: {LY - 800.0: (("gear", -100.0, 200.0, 60.0, 0.75), ("gap", -100.0, 250.0, 0.88), ("gear", 0.0, 200.0, -60.0, 0.75),
                         ("fade", 0.0, 0.5, 0.85), ("gap", 100.0, 500.0, 0.85)),
            LY + 900.0: (("blue", -100.0, 0.85), ("blue", -100.0, 0.85), ("switch", 0.0, 0.7), ("red", 0.0, 0.85),
                         ("red", 100.0, 0.85), ("red", 0.0, 0.85), ("gap", 0.0, 500.0, 0.8))},
    }
    x_start = z_end + 960.0
    for zone in (2, 3):
        runs = []
        for lane_y, items in lane_items[zone].items():
            landing, ltop = previous_landings[lane_y]
            last, last_u, end = ceiling_run(r, lane_y, x_start - 300.0, ltop + RISE, items, "ceiling {}{}".format(zone, "a" if lane_y < LY else "b"))
            runs.append((lane_y, last, last_u, end, ltop))
        z_end = max(run[3] for run in runs) + 200.0
        new_landings = {}
        for lane_y, last, last_u, end, ltop in runs:
            r.under(end, z_end + 400.0, lane_y - 250.0, lane_y + 250.0, last_u, look="stone", name="Ceiling")
            r.gzone(x_start + 60.0, z_end, lane_y - 600.0, lane_y + 600.0, ltop - 400.0, ltop + RISE + 900.0)
            r.add("catcher", x_start + 60.0, z_end, lane_y - 600.0, lane_y + 600.0, ltop + RISE + 450.0)
            new_landings[lane_y] = min(last_u, ltop + RISE) - 350.0
        if zone == 2:
            for lane_y, ltop in new_landings.items():
                here = r.block(z_end + 60.0, z_end + 960.0, lane_y - 500.0, lane_y + 500.0, ltop - 200.0, ltop, "marble", "Landing")
                previous_landings[lane_y] = (here, ltop)
            x_start = z_end + 960.0
        else:
            L3 = min(new_landings.values())
            landing3 = r.block(z_end + 60.0, z_end + 960.0, LY - 1400.0, LY + 1500.0, L3 - 200.0, L3, "marble", "Landing")
            x_start = z_end + 960.0
    heights["landing 3"] = L3
    # Zone 4 (one lane), a star coin on a side ceiling.
    cu = L3 + RISE
    last, last_u, end = ceiling_run(r, LY, x_start - 300.0, cu, (
        ("gap", -100.0, 300.0, 0.88), ("gear", -100.0, 260.0, 70.0, 0.75), ("gap", 0.0, 300.0, 0.88),
        ("fade", 100.0, 0.0, 0.85), ("gap", 0.0, 600.0, 0.85)), "ceiling 4")
    coin_x = end - 300.0
    coin_ceiling = r.under(coin_x - 100.0, coin_x + 100.0, LY + 250.0 + 0.8 * r.reach(80.0), LY + 250.0 + 0.8 * r.reach(80.0) + 200.0, last_u + 80.0, look="gold", name="Coin Ceiling")
    r.flipped("ceiling 4 -> coin ceiling", last, last_u, coin_ceiling, last_u + 80.0, HARD)
    r.flipped("coin ceiling -> ceiling 4", coin_ceiling, last_u + 80.0, last, last_u, HARD)
    r.add("coin", coin_x, LY + 250.0 + 0.8 * r.reach(80.0) + 100.0, last_u + 80.0 - 330.0)
    z_end = end + 200.0
    r.under(end, z_end + 400.0, LY - 250.0, LY + 250.0, last_u, look="stone", name="Ceiling")
    r.gzone(x_start + 60.0, z_end, LY - 600.0, LY + 1100.0, L3 - 400.0, cu + 900.0)
    r.add("catcher", x_start + 60.0, z_end, LY - 600.0, LY + 1100.0, cu + 450.0)
    L4 = min(cu, last_u) - 350.0
    heights["landing 4"] = L4

    # =====================================================================================================
    # 4 Dark Tower
    # =====================================================================================================
    r.add("section", "4 Dark Tower")
    # Area 1's Great Tower remembered in light (2026-11-16): a big tower, two broken floors, the sun loose inside it
    # (its range the whole tower: it charges at the player all the way up; ridden, it throws them up).
    TF = L4
    TX0 = z_end + 960.0
    TX1, TY0, TY1 = TX0 + 4000.0, LY - 2000.0, LY + 2000.0
    landing4 = r.block(z_end + 60.0, TX0, LY - 400.0, LY + 400.0, TF - 200.0, TF, "marble", "Landing")
    r.add("shard", "shard2", z_end + 500.0, LY, TF)
    r.lamp(z_end + 500.0, LY, TF + 600.0, (210, 180, 255))
    tower_floor = r.block(TX0, TX1, TY0, TY1, TF - 200.0, TF, "darkstone", "Tower Floor")
    r.walk_on("landing -> tower floor", landing4, tower_floor)
    r.add("spot", "tower door", TX0 + 300.0, LY, TF)
    F1, F2, TOP_F = TF + 1300.0, TF + 2600.0, TF + 3600.0
    ROOF_U = TF + 4000.0
    WT = 100.0
    NW = 400.0   # the north wall is thick: the stepping stones wait inside it
    r.block(TX0 - WT, TX0, TY0 - WT, LY - 300.0, TF - 200.0, ROOF_U, "darkstone", "Tower Wall")
    r.block(TX0 - WT, TX0, LY + 300.0, TY1 + NW, TF - 200.0, ROOF_U, "darkstone", "Tower Wall")
    r.block(TX0 - WT, TX0, LY - 300.0, LY + 300.0, TF + 450.0, ROOF_U, "darkstone", "Tower Wall")
    r.block(TX1, TX1 + WT, TY0 - WT, TY1 + NW, TF - 200.0, ROOF_U, "darkstone", "Tower Wall")
    r.block(TX0, TX1, TY0 - WT, TY0, TF - 200.0, ROOF_U, "darkstone", "Tower Wall")
    r.block(TX0, TX1, TY1, TY1 + NW, TF - 200.0, ROOF_U, "darkstone", "Tower Wall")
    r.add("sign", TX0 + 300.0, LY + 500.0, TF + 380.0, 180.0, "Blinking Light  /  Stepping Stones (plate)")
    # The sun, high in the middle, its range the whole tower; caught, the player is back at the tower door.
    r.add("sun", TX0 + 2000.0, LY, TF, "tower door", (2000.0, 2000.0, 2000.0), 3000.0)
    # Broken floor 1: the east half, short of the north wall (the stepping stones run along it).
    floor1 = r.block(TX0 + 2000.0, TX1, TY0, TY1 - 600.0, F1 - 150.0, F1, "darkstone", "Broken Floor")
    r.add("flag", TX0 + 3400.0, LY - 900.0, F1)
    r.add("spot", "tower", TX0 + 3400.0, LY - 900.0, F1)
    # Way A: a helix of big light platforms round three columns by the south wall, each column's beam blinking in turn.
    cols = ((TX0 + 1100.0, LY - 1300.0), (TX0 + 1700.0, LY - 1300.0), (TX0 + 1400.0, LY - 1800.0))
    for k, (cx, cy) in enumerate(cols):
        r.beam("helix{}".format(k), cx, cy, TF, F1 + 300.0, 400.0, 2.6, 1.4, 4.0 / 3.0 * k)   # (slowed for the user, 2026-11-16)
    previous, top = tower_floor, TF
    for i in range(12):
        top += 100.0
        k = (i + 2) % 3        # (so the last one is the column by the broken floor)
        cx, cy = cols[k]
        here = r.lplat("helix{}".format(k), cx, cy, top, 300.0)
        r.jump("light helix {}".format(i + 1), previous, here, 100.0, 0.8)
        previous = here
    r.jump("light helix -> broken floor 1", previous, floor1, F1 - top, 0.85)
    # Way B: a pressure plate by the north wall slides twelve stones out of the wall, one after another, as a stair
    # along it; they slide back 10 s after the last one is out.
    r.add("lever", "stones", TX0 + 300.0, TY1 - 700.0, TF, 0.0, 16.0)
    previous, top = rect(TX0 + 300.0, TY1 - 700.0, 180.0), TF
    sx = TX0 + 350.0
    for i in range(12):
        top += 100.0
        sx += 280.0
        r.add("mech", "stones", sx, TY1 + 200.0, top, (180.0, 300.0, 100.0), (0.0, -450.0, 0.0), 0.3 * i, 0.5, (13.3 - 0.3 * i, 0.6), "stone", "Stepping Stone")
        here = rect(sx, TY1 - 250.0, 180.0, 300.0)
        r.jump("stepping stone {}".format(i + 1), previous, here, 100.0, 0.8)
        previous = here
    r.jump("stepping stone -> broken floor 1", previous, floor1, F1 - top, 0.85)
    # Broken floor 2: the west part.
    floor2 = r.block(TX0, TX0 + 1000.0, TY0, TY1 - 600.0, F2 - 150.0, F2, "darkstone", "Broken Floor")
    # Floor 1 -> 2: a lift at floor 1's west edge, then big platforms round two beams that take turns, westward.
    lift, lift_top = r.moving(TX0 + 1750.0, LY - 300.0, F1, (0.0, 0.0, 600.0), 3.5, 1.5, 500.0)   # (made bigger for the user, 2026-11-16)
    r.jump("broken floor 1 -> lift", floor1, lift, 0.0, MID)
    r.beam("turnA", TX0 + 1250.0, LY - 250.0, F1 + 400.0, F2 + 300.0, 450.0, 2.4, 2.4, 0.0)
    r.beam("turnB", TX0 + 1250.0, LY + 250.0, F1 + 400.0, F2 + 300.0, 450.0, 2.4, 2.4, 2.4)
    spots = ((TX0 + 1250.0, LY + 250.0), (TX0 + 1250.0, LY - 250.0))
    previous, top = lift_top, F1 + 600.0
    for i in range(6):
        top += 100.0
        cx, cy = spots[i % 2]
        cx = cx + (-100.0 if (i // 2) % 2 else 100.0)
        here = r.lplat("turnB" if cy > LY else "turnA", cx, cy, top, 260.0)
        r.jump("turning light {}".format(i + 1), previous, here, 100.0, 0.8)
        previous = here
    r.jump("turning light -> broken floor 2", previous, floor2, F2 - top, 0.85)
    # Floor 2 -> the top floor: stones jutting from the south wall and crumbling floors, east, then north up the east
    # wall to the top floor in the north-east corner.
    previous, top = floor2, F2
    for i, direction in enumerate((E, E, E, E, N, N, N, N, N)):
        top += 100.0
        x, y = r.at(previous, direction, 0.72, 100.0, 120.0,
                    side=0.0)
        if i == 0:
            y = TY0 + 200.0
        if i in (2, 6):
            here = r.falling(x, y, top)
        else:
            here = r.block(x - 120.0, x + 120.0, y - 120.0, y + 120.0, top - 120.0, top, "stone", "Wall Stone")
        r.jump("wall stone {}".format(i + 1), previous, here, 100.0, 0.8)
        previous = here
    top_floor = r.block(TX0 + 2800.0, TX1, middle(previous)[1] + 0.6 * r.reach(100.0) + 120.0, TY1, TOP_F - 150.0, TOP_F, "darkstone", "Top Floor")
    r.jump("wall stone -> top floor", previous, top_floor, TOP_F - top, 0.8)
    r.add("shard", "shard3", TX1 - 300.0, TY1 - 300.0, TOP_F)
    r.lamp(TX1 - 300.0, TY1 - 300.0, TOP_F + 300.0, (255, 210, 150))
    # A star coin on a rarely lit platform west of the top floor.
    tf_y = (top_floor[3] + top_floor[4]) / 2.0
    rx = TX0 + 2800.0 - 0.5 * r.reach(0.0) - 120.0   # (the hole is at the east end)
    r.beam("rare", rx, tf_y, TOP_F - 300.0, ROOF_U, 300.0, 1.8, 5.0, 0.0)
    rare = r.lplat("rare", rx, tf_y, TOP_F, 220.0)
    r.jump("top floor -> rare light", top_floor, rare, 0.0, 0.6)
    r.add("coin", rx, tf_y, TOP_F)
    if TOP_F > ROOF_U - 350.0:
        raise RuntimeError("Top floor too close under the roof: {:.0f}".format(ROOF_U - TOP_F))
    # Up through a hole above the top floor's east end: two ledge grabs onto the roof.
    RT = ROOF_U + 100.0
    g1 = r.block(TX1 - 300.0, TX1, TY1 - 300.0, TY1, TOP_F - 150.0, TOP_F + 220.0, "stone", "Ruin Step")
    r.grab("top floor -> step 1", top_floor, g1, 220.0)
    g2_top = TOP_F + 440.0
    g2 = r.block(TX1 - 600.0, TX1 - 300.0, TY1 - 300.0, TY1, TOP_F - 150.0, g2_top, "stone", "Ruin Step")
    r.grab("step 1 -> step 2", g1, g2, 220.0)
    hole = (TX1 - 700.0, TX1, TY1 - 400.0, TY1)
    for x0, x1, y0, y1 in ((TX0 - WT, TX1 + WT, TY0 - WT, hole[2]), (TX0 - WT, hole[0], hole[2], TY1 + NW),
                           (hole[1], TX1 + WT, hole[2], TY1 + NW), (hole[0], hole[1], TY1, TY1 + NW)):
        if x1 - x0 > 1.0 and y1 - y0 > 1.0:
            r.block(x0, x1, y0, y1, ROOF_U, RT, "darkstone", "Tower Roof")
    roof = ("rect", TX0, TX1, TY0, hole[2])
    if RT - g2_top > 102.0 or g2_top < ROOF_U + 20.0:
        raise RuntimeError("Step 2 does not reach the roof: {:.0f}".format(RT - g2_top))
    r.jump("step 2 -> roof", g2, roof, RT - g2_top, 0.8)
    TY1 = TY1 + NW - WT   # (the roof's parapets go round the thick north wall)
    heights["tower floor 1"], heights["tower floor 2"], heights["tower top"], heights["roof"] = F1, F2, TOP_F, RT

    # =====================================================================================================
    # 5 Iwato (on the roof)
    # =====================================================================================================
    r.add("section", "5 Iwato")
    PAR = 1400.0
    # Parapets round the roof, open only into the corridor east.
    r.block(TX0 - WT, TX1 + WT, TY1, TY1 + WT, RT, RT + PAR, "marble", "Parapet")
    r.block(TX0 - WT, TX1 + WT, TY0 - WT, TY0, RT, RT + PAR, "marble", "Parapet")
    r.block(TX0 - WT, TX0, TY0, TY1, RT, RT + PAR, "marble", "Parapet")
    r.block(TX1, TX1 + WT, TY0, LY - 350.0, RT, RT + PAR, "marble", "Parapet")
    r.block(TX1, TX1 + WT, LY + 350.0, TY1, RT, RT + PAR, "marble", "Parapet")
    CX1 = TX1 + 1500.0
    corridor = r.block(TX1, CX1, LY - 350.0, LY + 350.0, RT - 200.0, RT, "marble", "Iwato Corridor")
    r.block(TX1, CX1, LY - 600.0, LY - 350.0, RT, RT + PAR, "marble", "Corridor Wall")
    r.block(TX1, CX1, LY + 350.0, LY + 600.0, RT, RT + PAR, "marble", "Corridor Wall")
    r.add("hidden_lever", "iwato", TX0 + 1500.0, LY, TF - 1500.0)
    r.add("mech", "iwato", TX1 + 300.0, LY, RT + 1300.0, (200.0, 700.0, 1300.0), (0.0, 0.0, -1350.0), 1.5, 4.0, None, "darkstone", "Iwato Rock")
    r.add("iwato", TX1 + 150.0, LY, RT + 1550.0, 180.0, "iwato", (TX1 - 1400.0, LY - 900.0, RT + 700.0), (TX1 + 300.0, LY, RT + 600.0))
    r.block(TX1 + 840.0, TX1 + 960.0, LY - 60.0, LY + 60.0, RT, RT + 80.0, "gold", "Wing Pedestal")
    r.add("wings", TX1 + 900.0, LY, RT + 80.0)
    r.add("flag", TX1 + 1200.0, LY, RT)
    r.add("spot", "wings", TX1 + 1200.0, LY, RT)
    r.lamp(TX0 + 1500.0, LY, RT + 900.0, (255, 230, 190))

    # =====================================================================================================
    # 6 Heaven's Gate (wings and updrafts)
    # =====================================================================================================
    r.add("section", "6 Heaven's Gate")
    previous, top = corridor, RT
    x, ly = CX1, LY
    hops = ((1000.0, 0.0, 0.0, 0.0), (1200.0, 600.0, 0.0, 0.0), (1400.0, -600.0, 3.0, 1.5),
            (1600.0, 0.0, 2.6, 1.6), (1700.0, 700.0, 2.4, 1.8), (1700.0, -700.0, 2.2, 1.8))
    for i, (distance, side, on, off) in enumerate(hops):
        ly += side
        x += distance
        column = rect(x + 150.0, ly, 300.0)
        bottom, column_top = top - 500.0, top + 1100.0
        r.wind(x + 150.0, ly, (bottom + column_top) / 2.0, column_top - bottom, 300.0, 300.0, 0.0, 90.0, 2200.0, 900.0, on, off)
        r.glide("wing hop {}".format(i + 1), previous, top, column, bottom + 100.0)
        island_top = column_top - 100.0
        isle_x = x + 300.0 + 60.0 + 0.48 * 700.0
        here = r.island(isle_x, ly, island_top, 700.0)
        r.lift("updraft {} -> island".format(i + 1), column, column_top, here, island_top)
        if i == 2:
            coin_isle = r.island(isle_x, ly + 1500.0, island_top - 300.0, 300.0)
            r.glide("island 3 -> coin isle", here, island_top, coin_isle, island_top - 300.0)
            r.add("coin", isle_x, ly + 1500.0, island_top - 300.0)
        previous, top = here, island_top
        x = isle_x + 0.48 * 700.0
    HG = top - 200.0
    gx, gy = x + 700.0 + 0.48 * 1600.0, ly
    gate = r.island(gx, gy, HG, 1600.0)
    r.glide("last island -> heaven's gate", previous, top, gate, HG)
    r.block(gx - 80.0, gx + 80.0, gy - 500.0, gy - 350.0, HG, HG + 1200.0, "gold", "Gate Pillar")
    r.block(gx - 80.0, gx + 80.0, gy + 350.0, gy + 500.0, HG, HG + 1200.0, "gold", "Gate Pillar")
    r.block(gx - 100.0, gx + 100.0, gy - 560.0, gy + 560.0, HG + 1200.0, HG + 1350.0, "gold", "Gate Lintel")
    r.add("goal", gx + 200.0, gy, HG)
    r.shaft(gx, gy, HG + 5000.0, HG, 500.0)
    heights["heaven's gate"] = HG

    # One catcher under everything (the tower has its own floor).
    xs = [p[1] for p in r.pieces if p[0] in ("island", "jewel")] + [TX0, TX1]
    ys = [p[2] for p in r.pieces if p[0] in ("island", "jewel")] + [TY0, TY1]
    X0, X1, Y0, Y1 = min(xs + [-4000.0]) - 3000.0, max(xs + [gx]) + 3000.0, min(ys) - 3000.0, max(ys) + 3000.0
    r.add("catcher", X0, X1, Y0, Y1, B - 1500.0)
    r.bounds = (X0, X1, Y0, Y1)
    r.under = (TX0 - WT, TX1 + WT, TY0 - WT, TY1 + WT)
    r.summit_top, r.gate_top = HG, HG
    r.heights = heights
    return r


if __name__ == "__main__":
    route = build(22610.0, 500.9, 980.0, 600.0, 300.0)
    for name, g, rise, limit in route.checks:
        print("  {:<42} gap {:>5.0f} rise {:>6.0f} (limit {:>5.0f}){}".format(name, g, rise, limit, "  TIGHT" if g > 0.85 * limit else ""))
    for name, z in route.heights.items():
        print("  {:<18} {:>7.0f}  ({:+.0f} from the start)".format(name, z, z - route.heights["start"]))
    print("bounds {}".format(route.bounds))
    print("pieces {}, jumps {}".format(len(route.pieces), len(route.checks)))
