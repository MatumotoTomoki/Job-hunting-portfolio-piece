# Hidden stage 1 (LV_Secret) as area 1 itself, collapsed (the user, 2026-11-22): the real area 1 broken apart, its own
# goal kept (the twelve giant steps up the Great Wall and the gear, now on to hidden area 2), and the way there made
# longer - "the way, not past the goal" - with stretches of gimmicks between the torn-apart sections and new gimmicks
# laid over the old ones, so it does not feel like area 1. build_secret_stage.py copies LV_Area1_Ruins and moves each
# section whole by route.section_offsets (worked out here: each section is put just past the stretch before it), the
# lower town broken up by secret_town.py. Checked jump by jump:
#   blender -b --factory-startup --python secret_collapse.py
#   A Lower Town   (start; flame jets by the crack)
#   1 Dust Clouds  vanishing dust clouds in a crosswind, two rising roof islands         -> B Roofs (a crosswind over them)
#   2 Hell Rift    flame jets on burnt slabs, then the cages: heaven carries on (flag)  -> C Aqueduct (flame jets on its decks)
#   3 Fallen Tower two gravity zones walked on the ceiling (flag)                      -> D Great Tower (flame jets inside)
#   4 Dark Cliff   stones lit by beams taking turns, two ledge grabs                   -> E Cliff (gusts off the ledges)
#   5 Time Rift    gondolas, pistons, the clock wreck (flag, time rewind), gears, fading steps
#                                                                                      -> F Courtyard (the sun loose in it)
#   and area 1's own end: the lever, the giant steps, the gear on the Great Wall (to LV_Secret2).
# The pieces the stretches start from and end on are area 1's (Saved/level_dump_LV_Area1_Ruins.json, 2026-11-22).
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from area3_layout import rect, circle, middle, gap, beyond
from area4_layout import Route, ceiling_run, THREAD_HANG, HARD, MID, EASY, PENTA, E, N, W, S
import secret_town

# (section, x0, x1, y0, y1, top) in area 1.
HALL_ROOF = ("H", -2600.0, -1400.0, 0.0, 700.0, 960.0)          # A1 054 Hall Roof
HOUSE = ("B", -1020.0, -500.0, -500.0, 300.0, 1020.0)           # A1 081 House (the roofs' west end)
LIFT_TOP = ("B", 1400.0, 1700.0, -150.0, 150.0, 1500.0)         # A1 089 Lift, up
DECK_1 = ("C", 1700.0, 2800.0, -150.0, 150.0, 1500.0)           # A1 090 Deck
DECK_2 = ("C", 3900.0, 4800.0, -150.0, 150.0, 1500.0)           # A1 091 Deck
DOOR = ("D", 4800.0, 5100.0, -200.0, 200.0, 1500.0)             # the tower door's sill (A1 107 Wall's top)
BREACH = ("D", 6900.0, 7200.0, 200.0, 700.0, 4200.0)            # the breach's sill (A1 121 Wall's top)
BRIDGE = ("E", 7300.0, 7700.0, 200.0, 700.0, 4200.0)            # A1 181 Broken Bridge
LEDGE = ("E", 8220.0, 8400.0, 300.0, 480.0, 5860.0)             # A1 191 Cliff Ledge (the last)
OVERHANG_X1 = 8400.0                                            # A1 182 Overhang (E) ends here
COURTYARD = ("F", 8400.0, 12500.0, -2000.0, 2000.0, 5960.0)     # A1 195 Cliff and Courtyard

def stair(r, name, a, a_top, b, b_top, kinds, look="ruin", size=300.0):
    # From a to b along the line between their facing edges. If the line is long enough for a stepped stair (at most
    # 100 up a step, at least 150 between pieces) the pieces cycle through kinds ("block", "falling", "timed");
    # otherwise pistons (400 across, each lifting an even share, at most 450) gain the height in fewer, wider jumps.
    (ax, ay), (bx, by) = middle(a), middle(b)
    d = math.hypot(bx - ax, by - ay) or 1.0
    ux, uy = (bx - ax) / d, (by - ay) / d
    sx, sy = ax + ux * _reach_out(a, ux, uy), ay + uy * _reach_out(a, ux, uy)
    ex, ey = bx - ux * _reach_out(b, -ux, -uy), by - uy * _reach_out(b, -ux, -uy)
    length = math.hypot(ex - sx, ey - sy)
    rise_total = b_top - a_top
    n = max(1, int(math.ceil(max(rise_total, 0.0) / 100.0)))
    count = 0
    if length >= n * 150.0 + (n - 1) * size:
        # stepped: as many pieces as the length needs for gaps no wider than 0.6 of a 100-rise jump
        while (length - (n - 1) * size) / n > 0.6 * r.reach(100.0):
            n += 1
        step = rise_total / n
        previous, previous_top = a, a_top
        for i in range(1, n):
            t = (i * (length - (n - 1) * size) / n + (i - 0.5) * size) / length
            x, y = sx + (ex - sx) * t, sy + (ey - sy) * t
            z = round((a_top + step * i) / 10.0) * 10.0
            kind = kinds[(i - 1) % len(kinds)]
            if kind == "falling":
                here = r.falling(x, y, z)
            elif kind == "timed":
                here = r.timed(x, y, z, 0.0 if i % 2 else 1.4)
            else:
                here = r.block(x - size / 2.0, x + size / 2.0, y - size / 2.0, y + size / 2.0, z - 250.0, z, look, "Rubble")
            r.jump("{} {}".format(name, i), previous, here, z - previous_top, HARD)
            previous, previous_top = here, z
            count += 1
        r.jump("{} end".format(name), previous, b, b_top - previous_top, HARD)
        return count
    # pistons
    m = max(1, int(math.ceil(rise_total / 450.0)))
    while (length - m * 400.0) / (m + 1) < 150.0 and m > 1:
        m -= 1
    h = rise_total / m
    if h > 600.0:
        raise RuntimeError("{}: too little room for {:.0f} up".format(name, rise_total))
    previous, previous_top = a, a_top
    for i in range(m):
        t = ((i + 1) * (length - m * 400.0) / (m + 1) + (i + 0.5) * 400.0) / length
        x, y = sx + (ex - sx) * t, sy + (ey - sy) * t
        low, high = r.moving(x, y, previous_top, (0.0, 0.0, h), 2.5, 1.5, 400.0)
        r.jump("{} piston {}".format(name, i + 1), previous, low, 0.0, HARD)
        previous, previous_top = high, previous_top + h
        count += 1
    r.jump("{} end".format(name), previous, b, b_top - previous_top, HARD)
    return count

def _reach_out(shape, ux, uy):
    # How far the footing reaches from its middle along (ux, uy).
    if shape[0] == "circle":
        return shape[3]
    hx, hy = (shape[2] - shape[1]) / 2.0, (shape[4] - shape[3]) / 2.0
    tx = hx / abs(ux) if abs(ux) > 1e-6 else 1e9
    ty = hy / abs(uy) if abs(uy) > 1e-6 else 1e9
    return min(tx, ty)


def build(base, jump_z, gravity, walk, plat):
    r = Route(base, jump_z, gravity, walk, plat)
    heights = {"start": 0.0}
    off = {"A": (0.0, 0.0, 0.0), "H": secret_town.HALL_OFFSET}
    r.section_offsets = off

    def moved(piece):
        section, x0, x1, y0, y1, top = piece
        dx, dy, dz = off[section]
        return ("rect", x0 + dx, x1 + dx, y0 + dy, y1 + dy), top + dz

    def place(piece, after, after_top, rise=0.0, ratio=0.6, touch=False):
        # Put piece's section just east of `after`: its west edge a jump (or nothing, touch) past after's east edge,
        # its middle level with after's in y, its top `rise` above after_top. Returns the moved piece and its top.
        section, x0, x1, y0, y1, top = piece
        g = 0.0 if touch else ratio * r.reach(rise)
        off[section] = (after[2] + g - x0, middle(after)[1] - (y0 + y1) / 2.0, after_top + rise - top)
        return moved(piece)

    r.add("spot", "start", -3600.0, 0.0, 0.0)
    # --- A: flame jets by the crack (in area 1's own place: A does not move) ---
    r.add("section", "A Lower Town")
    r.add("flame", -3050.0, 0.0, 0.0, 0.0, 0.0, 0.8, 1.4, 1.8, "start")
    r.add("flame", -3300.0, -600.0, 0.0, 0.0, 1.2, 0.8, 1.4, 1.8, "start")

    # =====================================================================================================
    # 1 Dust Clouds (hall roof -> the roofs)
    # =====================================================================================================
    r.add("section", "1 Dust Clouds")
    previous, top = moved(HALL_ROOF)
    LY = middle(previous)[1]
    first_x = previous[2]
    for i in range(6):
        x, y = r.at(previous, E, 0.55, 0.0, 0.4 * 450.0, side=(150.0 if i % 2 else -150.0))
        here = r.vanish(x, y, top, 450.0, 0.8, 2.0)
        r.jump("dust cloud {}".format(i + 1), previous, here, 0.0, HARD)
        previous = here
        if i == 3:
            cy = y + 180.0 + 0.5 * r.reach(0.0) + 140.0
            coin_cloud = r.vanish(x, cy, top, 350.0, 1.2, 2.0)
            r.jump("dust cloud 4 -> coin cloud", here, coin_cloud, 0.0, HARD)
            r.jump("coin cloud -> dust cloud 4", coin_cloud, here, 0.0, HARD)
            r.add("coin", x, cy, top)
    r.wind((first_x + previous[2]) / 2.0, LY, top - 150.0, previous[2] - first_x + 400.0, 1600.0, 900.0, -90.0, 0.0, 600.0, 400.0, 2.0, 2.2, 0.5)
    x, y = r.at(previous, E, 0.6, 0.0, 0.48 * 350.0)
    ride, arrive = r.mover(x, LY, top, (1100.0, 0.0, 300.0), 4.0, 1.5)
    r.jump("dust -> rising roof 1", previous, ride, 0.0, MID)
    top += 300.0
    x, y = r.at(arrive, E, 0.6, 0.0, 0.48 * 350.0)
    far, near = r.mover(x + 1100.0, LY, top + 300.0, (-1100.0, 0.0, -300.0), 4.0, 1.5)
    r.jump("rising roof 1 -> 2 (they meet)", arrive, near, 0.0, MID)
    top += 300.0
    top += 100.0
    x, y = r.at(far, E, 0.6, 100.0, 300.0)
    shard = r.block(x - 300.0, x + 300.0, LY - 300.0, LY + 300.0, top - 250.0, top, "tile", "Roof Shard")
    r.jump("rising roof 2 -> roof shard", far, shard, 100.0, MID)
    house, ht = place(HOUSE, shard, top)
    r.jump("roof shard -> the roofs", shard, house, 0.0, HARD)
    # B: a crosswind over its roofs (blowing north, in gusts)
    dx, dy, dz = off["B"]
    r.wind(340.0 + dx, 400.0 + dy, 1300.0 + dz, 2720.0, 1800.0, 700.0, 90.0, 0.0, 500.0, 350.0, 2.0, 2.5, 0.0)
    heights["roofs"] = ht

    # =====================================================================================================
    # 2 Hell Rift (the roofs' lift -> the aqueduct)
    # =====================================================================================================
    r.add("section", "2 Hell Rift")
    lift, top = moved(LIFT_TOP)
    x, y = r.at(lift, E, 0.6, 0.0, 400.0)
    edge = r.block(x - 400.0, x + 400.0, y - 400.0, y + 400.0, top - 300.0, top, "darkstone", "Rift Edge")
    r.jump("roofs' lift -> rift edge", lift, edge, 0.0, HARD)
    HY = y
    r.add("spot", "rift", x, y, top)
    r.add("sign", x, y + 300.0, top + 380.0, 180.0, "Hell burns below")
    previous = edge
    for i in range(6):
        x, y = r.at(previous, E, 0.6, 0.0, 300.0)
        slab = r.block(x - 300.0, x + 300.0, HY - 200.0, HY + 200.0, top - 200.0, top, "darkstone", "Burnt Slab")
        r.jump("burnt slab {}".format(i + 1), previous, slab, 0.0, HARD)
        r.add("flame", x, HY, top, 0.0, 0.8 * i, 0.8, 1.5, 1.5, "rift")
        previous = slab
        if i == 2:
            cx, cy = r.at(slab, N, 0.7, 100.0, 90.0)
            perch = r.block(cx - 90.0, cx + 90.0, cy - 90.0, cy + 90.0, top - 150.0, top + 100.0, "ember", "Coin Perch")
            r.jump("burnt slab 3 -> coin perch", slab, perch, 100.0, HARD)
            r.jump("coin perch -> burnt slab 3", perch, slab, -100.0, HARD)
            r.add("flame", cx, cy, top + 100.0, 0.0, 0.4, 0.8, 1.2, 2.5, "rift")
            r.add("coin", cx, cy, top + 100.0)
    x, y = r.at(previous, E, 0.6, 0.0, 700.0)
    choice = r.block(x - 700.0, x + 700.0, HY - 500.0, HY + 500.0, top - 300.0, top, "darkstone", "Cage Platform")
    r.jump("burnt slab -> cage platform", previous, choice, 0.0, HARD)
    WALL = 900.0
    r.block(x + 700.0, x + 800.0, HY - 600.0, HY + 600.0, top, top + WALL, "darkstone", "Rift Wall")
    r.block(x - 700.0, x + 700.0, HY + 500.0, HY + 600.0, top, top + WALL, "darkstone", "Rift Wall")
    r.block(x - 700.0, x + 700.0, HY - 600.0, HY - 500.0, top, top + WALL, "darkstone", "Rift Wall")
    far_x = x + 700.0 + 2000.0
    FAR = top + 600.0
    far = r.block(far_x, far_x + 1200.0, HY - 600.0, HY + 600.0, FAR - 400.0, FAR, "paving", "Far Ledge")
    if gap(choice, far) < 1.2 * r.reach(FAR - top):
        raise RuntimeError("The far ledge can be jumped to from the cage platform")
    r.add("cages", x + 200.0, HY, top, (far_x + 300.0, HY, FAR + 100.0), 7)
    r.add("flag", far_x + 300.0, HY - 300.0, FAR)
    r.add("spot", "far ledge", far_x + 300.0, HY - 300.0, FAR)
    deck, dt = place(DECK_1, far, FAR)
    r.jump("far ledge -> the aqueduct", far, deck, 0.0, HARD)
    dx, dy, dz = off["C"]
    r.add("spot", "aqueduct", 4500.0 + dx, dy, 1500.0 + dz)
    r.add("flame", 2250.0 + dx, dy, 1500.0 + dz, 0.0, 0.0, 0.8, 1.4, 1.8, "aqueduct")
    r.add("flame", 4150.0 + dx, dy, 1500.0 + dz, 0.0, 0.9, 0.8, 1.4, 1.8, "aqueduct")
    heights["aqueduct"] = dt

    # =====================================================================================================
    # 3 Fallen Tower (the aqueduct's far deck -> the tower door)
    # =====================================================================================================
    r.add("section", "3 Fallen Tower")
    deck2, top = moved(DECK_2)
    LY = middle(deck2)[1]
    start = r.block(deck2[2], deck2[2] + 900.0, LY - 450.0, LY + 450.0, top - 300.0, top, "ruin", "Deck Fragment")
    r.walk_on("aqueduct -> deck fragment", deck2, start)
    r.add("sign", deck2[2] + 300.0, LY + 500.0, top + 380.0, 180.0, "The tower hangs upside down")
    RISE = 900.0
    x_start = start[2]
    zones = (
        (("gap", -100.0, 400.0, 0.85), ("gear", -100.0, 240.0, 40.0, 0.75), ("fade", 0.0, 0.0, 0.8), ("gap", 0.0, 500.0, 0.85)),
        (("red", -100.0, 0.85), ("red", 0.0, 0.85), ("switch", 0.0, 0.7), ("blue", 100.0, 0.85), ("blue", 0.0, 0.85),
         ("fade", 0.0, 0.8, 0.85), ("gap", 0.0, 500.0, 0.8)),
    )
    ltop = top
    for z, items in enumerate(zones):
        cu = ltop + RISE
        last, last_u, end = ceiling_run(r, LY, x_start - 300.0, cu, items, "tower ceiling {}".format(z + 1))
        if z == 1:
            coin_x = end - 300.0
            cy0 = LY + 250.0 + 0.8 * r.reach(80.0)
            coin_ceiling = r.under(coin_x - 100.0, coin_x + 100.0, cy0, cy0 + 200.0, last_u + 80.0, look="bronze", name="Coin Ceiling")
            r.flipped("tower ceiling 2 -> coin ceiling", last, last_u, coin_ceiling, last_u + 80.0, HARD)
            r.flipped("coin ceiling -> tower ceiling 2", coin_ceiling, last_u + 80.0, last, last_u, HARD)
            r.add("coin", coin_x, cy0 + 100.0, last_u + 80.0 - 330.0)
        z_end = end + 200.0
        r.under(end, z_end + 400.0, LY - 250.0, LY + 250.0, last_u, look="ruin", name="Ceiling")
        r.gzone(x_start + 60.0, z_end, LY - 600.0, LY + (1100.0 if z == 1 else 600.0), ltop - 400.0, cu + 900.0)
        r.add("catcher", x_start + 60.0, z_end, LY - 600.0, LY + (1100.0 if z == 1 else 600.0), cu + 450.0)
        ltop = min(cu, last_u) - 350.0
        landing = r.block(z_end + 60.0, z_end + 960.0, LY - 600.0, LY + 600.0, ltop - 200.0, ltop, "plaster", "Landing")
        if z == 0:
            r.add("flag", z_end + 500.0, LY, ltop)
            r.add("spot", "tower ceiling", z_end + 500.0, LY, ltop)
            r.add("switch", z_end + 500.0, LY + 450.0, ltop)
        x_start = z_end + 960.0
    door, door_top = place(DOOR, landing, ltop, touch=True)
    r.walk_on("landing -> the tower door", landing, door)
    dx, dy, dz = off["D"]
    r.add("spot", "tower door", 5300.0 + dx, dy, 1500.0 + dz)
    r.add("flame", 5700.0 + dx, 300.0 + dy, 1500.0 + dz, 0.0, 0.0, 0.8, 1.4, 1.8, "tower door")
    r.add("flame", 6200.0 + dx, -300.0 + dy, 1500.0 + dz, 0.0, 1.0, 0.8, 1.4, 1.8, "tower door")
    heights["tower door"] = door_top

    # =====================================================================================================
    # 4 Dark Cliff (the breach -> the broken bridge)
    # =====================================================================================================
    r.add("section", "4 Dark Cliff")
    breach, top = moved(BREACH)
    LY = middle(breach)[1]
    ledge = r.block(breach[2], breach[2] + 500.0, LY - 300.0, LY + 300.0, top - 300.0, top, "rock", "Breach Ledge")
    r.walk_on("breach -> breach ledge", breach, ledge)
    previous = ledge
    for i in range(8):
        x, y = ledge[2] + 380.0 + 300.0 * i, LY + (-250.0 if i % 2 == 0 else 250.0)
        top += 100.0
        beam = "lit{}".format(i + 1)
        # A wave of light up the stones (each 0.9 s after the last, on 3 s of 5.4): two neighbours share 2.1 s lit.
        # (Turns of 2.8 / 2.0 left only 0.4 s to cross - "they are in step, I can't climb", the user 2026-11-22.)
        r.beam(beam, x, y, top - 300.0, top + 700.0, 400.0, 3.0, 2.4, 0.9 * i)
        here = r.lplat(beam, x, y, top, 260.0)
        r.jump("lit stone {}".format(i + 1), previous, here, 100.0, 0.8)
        previous = here
        if i == 5:
            rx, ry = x, y - 130.0 - 0.55 * r.reach(0.0) - 110.0
            r.beam("rare", rx, ry, top - 300.0, top + 700.0, 300.0, 1.6, 5.0, 0.0)
            rare = r.lplat("rare", rx, ry, top, 220.0)
            r.jump("lit stone 6 -> rare light", here, rare, 0.0, 0.7)
            r.add("coin", rx, ry, top)
    top += 100.0
    x, y = r.at(previous, E, 0.6, 100.0, 300.0)
    cliff = r.block(x - 300.0, x + 300.0, LY - 400.0, LY + 400.0, top - 400.0, top, "rock", "Cliff Ledge")
    r.jump("lit stone -> cliff ledge", previous, cliff, 100.0, 0.85)
    previous = cliff
    for i in range(2):
        here_top = top + 220.0
        here = r.block(previous[2], previous[2] + 400.0, previous[3], previous[4], here_top - 600.0, here_top, "rock", "Cliff Step")
        r.grab("cliff step {}".format(i + 1), previous, here, 220.0)
        previous, top = here, here_top
    bridge, bt = place(BRIDGE, previous, top)
    r.jump("cliff step -> the broken bridge", previous, bridge, 0.0, HARD)
    dx, dy, dz = off["E"]
    r.wind(8310.0 + dx, 200.0 + dy, 5100.0 + dz, 400.0, 3200.0, 1800.0, 0.0, 0.0, 350.0, 250.0, 1.5, 3.0, 0.0)
    heights["cliff"] = bt

    # =====================================================================================================
    # 5 Time Rift (the last cliff ledge -> the courtyard)
    # =====================================================================================================
    r.add("section", "5 Time Rift")
    last_ledge, top = moved(LEDGE)
    out_x = OVERHANG_X1 + off["E"][0] + 250.0
    clear = r.block(out_x - 150.0, out_x + 150.0, last_ledge[3] - 60.0, last_ledge[4] + 60.0, top - 250.0, top, "ruin", "Rubble")
    r.jump("cliff ledge -> past the overhang", last_ledge, clear, 0.0, HARD)
    TY = middle(clear)[1]
    x = clear[2] + 0.5 * r.reach(0.0) + 150.0
    g1, g1_end = r.gondola(x, TY, top, (1800.0, 0.0, 500.0), 6.0)
    r.jump("rubble -> gondola 1", clear, g1, 0.0, MID)
    top += 500.0
    x, y = r.at(g1_end, E, 0.6, 0.0, 150.0)
    stop = r.falling(x, y, top)
    r.jump("gondola 1 -> crumbling stop", g1_end, stop, 0.0, MID)
    x, y = r.at(stop, E, 0.6, 0.0, 150.0)
    g2, g2_end = r.gondola(x, y, top, (1800.0, 0.0, 400.0), 6.0)
    r.jump("crumbling stop -> gondola 2", stop, g2, 0.0, MID)
    top += 400.0
    previous = g2_end
    # Every other piston starts up and comes down: in step they were never level with each other ("they move in
    # step, I can't climb", the user 2026-11-22); this way one is down when the last is up.
    for i in range(3):
        x, y = r.at(previous, E, 0.6, 0.0, 200.0)
        if i % 2:
            piston_up, piston = r.moving(x, y, top + 500.0, (0.0, 0.0, -500.0), 2.5, 1.5, 400.0)
        else:
            piston, piston_up = r.moving(x, y, top, (0.0, 0.0, 500.0), 2.5, 1.5, 400.0)
        r.jump("piston {}".format(i + 1), previous, piston, 0.0, MID)
        top += 500.0
        previous = piston_up
    top += 100.0
    x, y = r.at(previous, E, 0.6, 100.0, 600.0)
    clock = r.block(x - 600.0, x + 600.0, y - 600.0, y + 600.0, top - 400.0, top, "bronze", "Clock Wreck")
    r.jump("piston -> clock wreck", previous, clock, 100.0, MID)
    kx, ky = middle(clock)
    r.add("flag", kx - 300.0, ky - 300.0, top)
    r.add("spot", "clock", kx - 300.0, ky - 300.0, top)
    r.add("rewind", kx + 200.0, ky + 250.0, top)
    r.lamp(kx, ky, top + 700.0, (255, 140, 90))
    cx, cy = r.at(clock, S, 0.75, 0.0, 90.0)
    perch = r.block(cx - 90.0, cx + 90.0, cy - 90.0, cy + 90.0, top - 150.0, top, "bronze", "Coin Perch")
    r.jump("clock wreck -> coin perch", clock, perch, 0.0, HARD)
    r.jump("coin perch -> clock wreck", perch, clock, 0.0, HARD)
    r.add("coin", cx, cy, top)
    heights["clock wreck"] = top
    previous = clock
    for i in range(4):
        x, y = r.at(previous, E, 0.65, 0.0, 0.92 * 220.0)
        r.add("gear", x, y, top, 220.0, 40.0 if i % 2 == 0 else -40.0)
        here = circle(x, y, 0.92 * 220.0)
        r.jump("clock gear {}".format(i + 1), previous, here, 0.0, HARD)
        previous = here
    for i in range(8):
        rise = 100.0 if i % 2 == 0 else 0.0
        top += rise
        x, y = r.at(previous, E, 0.65, rise, 150.0)
        here = r.timed(x, y, top, 0.5 * i)     # a wave (0.5 s apart): neighbours share 1.3 s (by turns left 0.3 s)
        r.jump("fading step {}".format(i + 1), previous, here, rise, HARD)
        previous = here
    top += 100.0
    x, y = r.at(previous, E, 0.6, 100.0, 300.0)
    rift_end = r.block(x - 300.0, x + 300.0, y - 300.0, y + 300.0, top - 300.0, top, "ruin", "Rift End")
    r.jump("fading step -> rift end", previous, rift_end, 100.0, HARD)
    court, ct = place(COURTYARD, rift_end, top)
    r.jump("rift end -> the courtyard", rift_end, court, 0.0, HARD)
    dx, dy, dz = off["F"]
    r.add("flag", 8900.0 + dx, 600.0 + dy, ct)
    r.add("spot", "courtyard", 8900.0 + dx, 600.0 + dy, ct)
    r.add("sun", 10450.0 + dx, dy, ct, "courtyard", (2200.0, 2200.0, 2200.0), 3000.0)
    heights["courtyard"] = ct
    heights["wall top (goal)"] = 7260.0 + dz

    xs = [p[1] for p in r.pieces if p[0] == "block"] + [p[2] for p in r.pieces if p[0] == "block"] + [-4000.0, 13900.0 + dx]
    ys = [p[3] for p in r.pieces if p[0] == "block"] + [p[4] for p in r.pieces if p[0] == "block"] + [-2000.0, 2000.0]
    X0, X1, Y0, Y1 = min(xs) - 3000.0, max(xs) + 3000.0, min(ys) - 3000.0, max(ys) + 3000.0
    r.add("catcher", X0, X1, Y0, Y1, -1000.0)
    r.bounds = (X0, X1, Y0, Y1)
    r.summit_top = 7260.0 + dz
    r.heights = heights
    return r


if __name__ == "__main__":
    route = build(0.0, 500.9, 980.0, 600.0, 300.0)
    for name, g, rise, limit in route.checks:
        if "->" in name or "TIGHT" in name:
            print("  {:<46} gap {:>5.0f} rise {:>6.0f} (limit {:>5.0f})".format(name, g, rise, limit))
    for name, z in route.heights.items():
        print("  {:<18} {:>7.0f}".format(name, z))
    for k, v in sorted(route.section_offsets.items()):
        print("  offset {} = ({:.0f}, {:.0f}, {:.0f})".format(k, *v))
    print("pieces {}, jumps {}".format(len(route.pieces), len(route.checks)))