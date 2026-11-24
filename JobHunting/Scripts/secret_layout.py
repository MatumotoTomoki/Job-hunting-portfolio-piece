# The hidden stage's (LV_Secret, behind area 1's secret door) route as plain data, checked jump by jump;
# build_secret_stage.py places it. No Unreal here, so it can be checked on its own (Blender's Python will do):
#   blender -b --factory-startup --python secret_layout.py
# "Area 1, collapsed" (the user, 2026-11-22): the ruined town torn apart and hanging in a blood-red dusk, climbed through
# its wreckage in the order area 1 was climbed. Longer than area 4; gimmicks from every area. Three flags; a star coin
# in each section.
#   1 Shattered Plaza   the lower town's plaza cracked open; rubble eastward, crumbling and fading among solid blocks
#   2 Drifting Roofs    north over roofs adrift: a ferrying platform, dust clouds in a crosswind, rising roof islands
#   3 Torn Aqueduct     east along deck pieces of the aqueduct, the gaps crossed on melody stones and hanging threads
#                       (flag 1)
#   4 Fallen Tower      the Great Tower snapped and hanging upside down: three gravity zones walked on the ceiling
#                       (gaps, gears, fading steps; red and blue blocks) (flag 2 after the first)
#   5 Dark Cliff        north up the cliff in the dark: platforms lit by beams taking turns, ledge grabs, more light
#   6 Time Rift         east: two gondolas, a crumbling stop, pistons up to the clock's wreck (time rewind, flag 3),
#                       a row of fading steps
#   7 Hell Rift         east over hell's glow: flame jets on the slabs, then the only way on is one of two cages
#   8 Floating Wall     the Great Wall's twelve giant steps, hanging loose: the lever raises them one after another;
#                       the wings on top, updrafts up to the goal
# Pieces: as area4_layout.py plus
#   ("debris", x, y, z, size, yaw, pitch, roll, look)   a loose block (no collision), for looks only
#   ("flame", x, y, top, yaw, delay, warn, burn, off, respawn_spot)   BP_FlameJet
#   ("cages", x, y, top, (dest), pair_id), ("rewind", x, y, top), ("goal", x, y, top)
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from area3_layout import rect, circle, middle, gap, beyond
from area4_layout import Route, ceiling_run, THREAD_HANG, HARD, MID, EASY, PENTA, E, N, W, S


def build(base, jump_z, gravity, walk, plat):
    r = Route(base, jump_z, gravity, walk, plat)
    B = base
    heights = {"start": B}

    # =====================================================================================================
    # 1 Shattered Plaza (east)
    # =====================================================================================================
    r.add("section", "1 Shattered Plaza")
    plaza = r.block(-1000.0, 1000.0, -1000.0, 1000.0, B - 300.0, B, "paving", "Broken Plaza")
    r.add("start", -600.0, 0.0, B, 0.0)
    r.add("spot", "start", -600.0, 0.0, B)
    for x, y, h in ((-700.0, -700.0, 500.0), (700.0, -650.0, 260.0), (-650.0, 700.0, 380.0)):
        r.block(x - 60.0, x + 60.0, y - 60.0, y + 60.0, B, B + h, "plaster", "Broken Column")
    r.add("sign", -300.0, 400.0, B + 380.0, 180.0, "The town that fell")
    previous, top = plaza, B
    kinds = ("block", "falling", "block", "timed", "timed", "block", "falling", "block", "timed", "block", "falling", "block", "timed", "block", "falling", "block", "timed", "block")
    rises = (100.0, 0.0, 100.0, 0.0, 0.0, 100.0, 0.0, 100.0, 0.0, 100.0, 0.0, 100.0, 0.0, 100.0, 0.0, 100.0, 0.0, 100.0)
    for i, (kind, rise) in enumerate(zip(kinds, rises)):
        top += rise
        x, y = r.at(previous, E, 0.72, rise, 150.0, side=(150.0 if i % 2 else -150.0))
        if kind == "falling":
            here = r.falling(x, y, top)
        elif kind == "timed":
            here = r.timed(x, y, top, 0.0 if i % 2 else 1.5)
        else:
            here = r.block(x - 150.0, x + 150.0, y - 150.0, y + 150.0, top - 250.0, top, "ruin", "Rubble")
        r.jump("rubble {}".format(i + 1), previous, here, rise, HARD)
        if i == 5:
            cx, cy = r.at(here, N, 0.7, 100.0, 90.0)
            perch = r.block(cx - 90.0, cx + 90.0, cy - 90.0, cy + 90.0, top - 150.0, top + 100.0, "bronze", "Coin Perch")
            r.jump("rubble 6 -> coin perch", here, perch, 100.0, HARD)
            r.jump("coin perch -> rubble 6", perch, here, -100.0, HARD)
            r.add("coin", cx, cy, top + 100.0)
        previous = here
    top += 100.0
    x, y = r.at(previous, E, 0.7, 100.0, 600.0)
    hall = r.block(x - 600.0, x + 600.0, y - 600.0, y + 600.0, top - 400.0, top, "plaster", "Hall Fragment")
    r.jump("rubble -> hall fragment", previous, hall, 100.0, HARD)
    HX, HY = x, y
    heights["hall fragment"] = top

    # =====================================================================================================
    # 2 Drifting Roofs (north)
    # =====================================================================================================
    r.add("section", "2 Drifting Roofs")
    previous = hall
    top += 100.0
    x, y = r.at(previous, N, 0.7, 100.0, 250.0)
    roof_a = r.block(x - 250.0, x + 250.0, y - 250.0, y + 250.0, top - 150.0, top, "tile", "Roof")
    r.jump("hall -> roof A", previous, roof_a, 100.0, HARD)
    # A platform ferrying the player 1200 north.
    x, y = r.at(roof_a, N, 0.6, 0.0, 150.0)
    ferry, ferry_end = r.moving(x, y, top, (0.0, 1200.0, 0.0), 3.5, 1.5)
    r.jump("roof A -> ferry", roof_a, ferry, 0.0, MID)
    top += 100.0
    x, y = r.at(ferry_end, N, 0.6, 100.0, 250.0)
    roof_b = r.block(x - 250.0, x + 250.0, y - 250.0, y + 250.0, top - 150.0, top, "tile", "Roof")
    r.jump("ferry -> roof B", ferry_end, roof_b, 100.0, HARD)
    # A crumbling stair of roof tiles, north.
    previous = roof_b
    for i in range(4):
        rise = 100.0 if i % 2 else 0.0
        top += rise
        x, y = r.at(previous, N, 0.7, rise, 150.0, side=(120.0 if i % 2 else -120.0))
        here = r.falling(x, y, top) if i % 2 == 0 else r.block(x - 150.0, x + 150.0, y - 150.0, y + 150.0, top - 150.0, top, "tile", "Roof Tile")
        r.jump("roof tile {}".format(i + 1), previous, here, rise, HARD)
        previous = here
    # Dust clouds in a gusting crosswind (blowing west), four of them north, then a roof.
    first_y = None
    for i in range(4):
        x, y = r.at(previous, N, 0.55, 0.0, 0.4 * 450.0)
        here = r.vanish(x, y, top, 450.0, 0.8, 2.0)
        r.jump("dust cloud {}".format(i + 1), previous, here, 0.0, HARD)
        first_y = first_y if first_y is not None else y
        previous = here
        if i == 2:
            cx, cy = x + 2.0 * 180.0 + 0.5 * r.reach(0.0), y
            coin_cloud = r.vanish(cx, cy, top, 350.0, 1.2, 2.0)
            r.jump("dust cloud 3 -> coin cloud (downwind is back)", here, coin_cloud, 0.0, HARD)
            r.jump("coin cloud -> dust cloud 3", coin_cloud, here, 0.0, HARD)
            r.add("coin", cx, cy, top)
    last_y = middle(previous)[1]
    top += 100.0
    x, y = r.at(previous, N, 0.65, 100.0, 300.0)
    roof_c = r.block(x - 300.0, x + 300.0, y - 300.0, y + 300.0, top - 150.0, top, "tile", "Roof")
    r.jump("dust cloud -> roof C", previous, roof_c, 100.0, HARD)
    r.wind(x, (first_y + last_y) / 2.0, top - 150.0, 1400.0, last_y - first_y + 600.0, 900.0, 180.0, 0.0, 600.0, 400.0, 2.0, 2.0, 0.5)
    # Two roof islands rising north in turn (they meet as area 4's do).
    x, y = r.at(roof_c, N, 0.6, 0.0, 0.48 * 350.0)
    ride, arrive = r.mover(x, y, top, (0.0, 1100.0, 300.0), 4.0, 1.5)
    r.jump("roof C -> rising roof 1", roof_c, ride, 0.0, MID)
    top += 300.0
    x, y = r.at(arrive, N, 0.6, 0.0, 0.48 * 350.0)
    far, near = r.mover(x, y + 1100.0, top + 300.0, (0.0, -1100.0, -300.0), 4.0, 1.5)
    r.jump("rising roof 1 -> 2 (they meet)", arrive, near, 0.0, MID)
    top += 300.0
    top += 100.0
    x, y = r.at(far, N, 0.6, 100.0, 500.0)
    tower_roof = r.block(x - 500.0, x + 500.0, y - 500.0, y + 500.0, top - 300.0, top, "tile", "Gatehouse Roof")
    r.jump("rising roof 2 -> gatehouse roof", far, tower_roof, 100.0, MID)
    heights["gatehouse roof"] = top

    # =====================================================================================================
    # 3 Torn Aqueduct (east)
    # =====================================================================================================
    r.add("section", "3 Torn Aqueduct")
    gx, gy = middle(tower_roof)
    r.add("flag", gx + 200.0, gy, top)
    r.add("spot", "aqueduct", gx + 200.0, gy, top)
    AY = gy
    previous = tower_roof

    def deck(x0, length, top, name="Aqueduct Deck"):
        here = r.block(x0, x0 + length, AY - 150.0, AY + 150.0, top - 120.0, top, "ruin", name)
        r.block(x0 + length / 2.0 - 120.0, x0 + length / 2.0 + 120.0, AY - 150.0, AY + 150.0, top - 1600.0, top - 120.0, "ruin", "Broken Arch")
        return here

    d = deck(previous[2] + 0.6 * r.reach(0.0), 900.0, top)
    r.jump("gatehouse roof -> deck 1", previous, d, 0.0, HARD)
    previous = d
    # Gap 1: melody stones, level.
    JR = 110.0
    for i in range(6):
        x, y = r.at(previous, E, 0.45, 0.0, JR, side=(80.0 if i % 2 else -80.0))
        here = r.jewel(x, y, top, JR, i, 2, 6, 0.8, PENTA[i])
        r.jump("melody stone {}".format(i + 1), previous, here, 0.0, 0.55)
        previous = here
    d = deck(previous[1] + 2.0 * JR + 0.5 * r.reach(0.0) - 2.0 * JR + JR, 700.0, top)
    r.jump("melody stone -> deck 2", previous, d, 0.0, MID)
    previous = d
    # Gap 2: a thread hanging from a broken arch above, up to a higher deck.
    tx = previous[2] + 0.55 * r.reach(0.0)
    bottom = top + 60.0
    anchor = bottom + 1100.0
    r.thread(tx, AY, anchor, anchor - bottom, 0.0, 3.5, 0.0, 0.0, 90.0)
    r.catch("deck 2 -> thread 1", previous, top, tx, AY, bottom)
    top = anchor - THREAD_HANG - 200.0
    d = deck(tx + 380.0, 800.0, top)
    r.leap("thread 1 -> deck 3", tx, AY, anchor, d, top)
    previous = d
    # Gap 3: crumbling stones.
    for i in range(5):
        x, y = r.at(previous, E, 0.7, 0.0, 150.0)
        here = r.falling(x, y, top)
        r.jump("crumbling stone {}".format(i + 1), previous, here, 0.0, HARD)
        previous = here
    d = deck(previous[2] + 0.65 * r.reach(0.0), 700.0, top)
    r.jump("crumbling stone -> deck 4", previous, d, 0.0, HARD)
    previous = d
    # Gap 4: a swinging thread, and a perch only a leap off it reaches (star coin).
    tx = previous[2] + 0.55 * r.reach(0.0)
    bottom = top + 60.0
    anchor = bottom + 1500.0
    r.thread(tx, AY, anchor, anchor - bottom, 24.0, 3.4, 0.0, 5.0, 90.0)
    r.catch("deck 4 -> thread 2", previous, top, tx, AY, bottom)
    perch_top = anchor - THREAD_HANG - 300.0
    perch = r.block(tx - 75.0, tx + 75.0, AY + 500.0, AY + 650.0, perch_top - 100.0, perch_top, "bronze", "Coin Perch")
    r.leap("thread 2 -> coin perch", tx, AY, anchor, perch, perch_top)
    r.catch("coin perch -> thread 2", perch, perch_top, tx, AY, bottom)
    r.add("coin", tx, AY + 575.0, perch_top)
    top = anchor - THREAD_HANG - 150.0
    d = deck(tx + 380.0, 700.0, top)
    r.leap("thread 2 -> deck 5", tx, AY, anchor, d, top)
    previous = d
    # Gap 5: melody stones rising.
    for i in range(5):
        top += 80.0
        x, y = r.at(previous, E, 0.45, 80.0, JR, side=(90.0 if i % 2 else -90.0))
        here = r.jewel(x, y, top, JR, i, 2, 5, 0.75, PENTA[i])
        r.jump("rising melody {}".format(i + 1), previous, here, 80.0, 0.55)
        previous = here
    top += 80.0
    x, y = r.at(previous, E, 0.7, 80.0, 450.0)
    aq_end = r.block(x - 450.0, x + 450.0, AY - 450.0, AY + 450.0, top - 300.0, top, "ruin", "Aqueduct End")
    r.jump("rising melody -> aqueduct end", previous, aq_end, 80.0, MID)
    heights["aqueduct end"] = top

    # =====================================================================================================
    # 4 Fallen Tower (east, upside down)
    # =====================================================================================================
    r.add("section", "4 Fallen Tower")
    LY = AY
    RISE = 900.0
    F0 = top
    x_start = aq_end[2]
    r.add("sign", x_start - 300.0, LY + 500.0, F0 + 380.0, 180.0, "The tower hangs upside down")
    zones = (
        (("gap", -100.0, 400.0, 0.85), ("gear", -100.0, 240.0, 40.0, 0.75), ("fade", 0.0, 0.0, 0.8), ("gap", 0.0, 500.0, 0.85)),
        (("red", -100.0, 0.85), ("red", 0.0, 0.85), ("switch", 0.0, 0.7), ("blue", 100.0, 0.85), ("blue", 0.0, 0.85),
         ("fade", 0.0, 0.8, 0.85), ("gap", 0.0, 500.0, 0.8)),
        (("gear", -100.0, 200.0, 60.0, 0.75), ("gap", -100.0, 250.0, 0.88), ("gear", 0.0, 200.0, -60.0, 0.75),
         ("fade", 0.0, 0.5, 0.85), ("gap", 100.0, 300.0, 0.88), ("fade", 0.0, 1.2, 0.85), ("gap", 0.0, 600.0, 0.85)),
    )
    ltop = F0
    for z, items in enumerate(zones):
        cu = ltop + RISE
        last, last_u, end = ceiling_run(r, LY, x_start - 300.0, cu, items, "tower ceiling {}".format(z + 1))
        if z == 2:
            coin_x = end - 300.0
            cy0 = LY + 250.0 + 0.8 * r.reach(80.0)
            coin_ceiling = r.under(coin_x - 100.0, coin_x + 100.0, cy0, cy0 + 200.0, last_u + 80.0, look="bronze", name="Coin Ceiling")
            r.flipped("tower ceiling 3 -> coin ceiling", last, last_u, coin_ceiling, last_u + 80.0, HARD)
            r.flipped("coin ceiling -> tower ceiling 3", coin_ceiling, last_u + 80.0, last, last_u, HARD)
            r.add("coin", coin_x, cy0 + 100.0, last_u + 80.0 - 330.0)
        z_end = end + 200.0
        r.under(end, z_end + 400.0, LY - 250.0, LY + 250.0, last_u, look="ruin", name="Ceiling")
        r.gzone(x_start + 60.0, z_end, LY - 600.0, LY + (1100.0 if z == 2 else 600.0), ltop - 400.0, cu + 900.0)
        r.add("catcher", x_start + 60.0, z_end, LY - 600.0, LY + (1100.0 if z == 2 else 600.0), cu + 450.0)
        ltop = min(cu, last_u) - 350.0
        landing = r.block(z_end + 60.0, z_end + 960.0, LY - 600.0, LY + 600.0, ltop - 200.0, ltop, "plaster", "Landing")
        if z == 0:
            r.add("flag", z_end + 500.0, LY, ltop)
            r.add("spot", "tower", z_end + 500.0, LY, ltop)
            r.add("switch", z_end + 500.0, LY + 450.0, ltop)
        x_start = z_end + 960.0
        heights["tower landing {}".format(z + 1)] = ltop
    top = ltop
    previous = landing

    # =====================================================================================================
    # 5 Dark Cliff (north, in the dark)
    # =====================================================================================================
    r.add("section", "5 Dark Cliff")
    lx, ly = middle(previous)
    r.add("sign", lx, ly + 400.0, top + 380.0, 180.0, "Only the lit stones hold")
    # Two beams taking turns, platforms between them climbing north.
    CX = lx
    y0 = previous[4]
    # Each stone has its own beam; the west ones and the east ones take turns (on 2.8 s of 4.8: 0.4 s overlap).
    for i in range(10):
        x, y = CX + (-250.0 if i % 2 == 0 else 250.0), y0 + 380.0 + 300.0 * i
        top += 100.0
        beam = "lit{}".format(i + 1)
        r.beam(beam, x, y, top - 300.0, top + 700.0, 400.0, 2.8, 2.0, 0.0 if i % 2 == 0 else 2.4)
        here = r.lplat(beam, x, y, top, 260.0)
        r.jump("lit stone {}".format(i + 1), previous, here, 100.0, 0.8)
        previous = here
    top += 100.0
    x, y = r.at(previous, N, 0.6, 100.0, 300.0)
    ledge = r.block(x - 400.0, x + 400.0, y - 300.0, y + 300.0, top - 400.0, top, "rock", "Cliff Ledge")
    r.jump("lit stone -> cliff ledge", previous, ledge, 100.0, 0.85)
    previous = ledge
    # Two ledge grabs up the cliff face.
    for i in range(2):
        here_top = top + 220.0
        y1 = previous[4]
        here = r.block(previous[1], previous[2], y1, y1 + 400.0, here_top - 600.0, here_top, "rock", "Cliff Step")
        r.grab("cliff step {}".format(i + 1), previous, here, 220.0)
        previous, top = here, here_top
    # Then one beam sweeping east and back over a row of platforms; a rarely lit one beside holds a star coin.
    cx, cy = middle(previous)
    row_y = previous[4] + 0.55 * r.reach(0.0) + 130.0
    r.beam("sweep", cx - 600.0, row_y, top - 300.0, top + 1200.0, 450.0, 0.0, 0.0, 0.0, (1200.0, 0.0, 0.0), 4.0)
    prev = previous
    first = None
    for i in range(4):
        here = r.lplat("sweep", cx - 600.0 + 400.0 * i, row_y, top, 260.0)
        r.jump("swept stone {}".format(i + 1), prev, here, 0.0, 0.8)
        first = first or here
        prev = here
    r.beam("rare", cx + 900.0 + 260.0, row_y, top - 300.0, top + 1200.0, 300.0, 1.6, 5.0, 0.0)
    rare = r.lplat("rare", cx + 900.0 + 260.0 + 0.0, row_y, top, 220.0)
    r.jump("swept stone 4 -> rare light", prev, rare, 0.0, 0.7)
    r.add("coin", cx + 1160.0, row_y, top)
    top += 100.0
    x, y = r.at(prev, N, 0.65, 100.0, 500.0)
    cliff_top = r.block(x - 900.0, x + 700.0, y - 500.0, y + 500.0, top - 500.0, top, "rock", "Cliff Top")
    r.jump("swept stone 4 -> cliff top", prev, cliff_top, 100.0, 0.85)
    heights["cliff top"] = top
    previous = cliff_top

    # =====================================================================================================
    # 6 Time Rift (east)
    # =====================================================================================================
    r.add("section", "6 Time Rift")
    TY = middle(previous)[1]
    x = previous[2] + 0.5 * r.reach(0.0) + 150.0
    g1, g1_end = r.gondola(x, TY, top, (1800.0, 0.0, 500.0), 6.0)
    r.jump("cliff top -> gondola 1", previous, g1, 0.0, MID)
    top += 500.0
    x, y = r.at(g1_end, E, 0.6, 0.0, 150.0)
    stop = r.falling(x, y, top)
    r.jump("gondola 1 -> crumbling stop", g1_end, stop, 0.0, MID)
    # a perch off the stop (star coin)
    cx, cy = r.at(stop, S, 0.75, 0.0, 90.0)
    perch = r.block(cx - 90.0, cx + 90.0, cy - 90.0, cy + 90.0, top - 150.0, top, "bronze", "Coin Perch")
    r.jump("crumbling stop -> coin perch", stop, perch, 0.0, HARD)
    r.add("coin", cx, cy, top)
    x, y = r.at(stop, E, 0.6, 0.0, 150.0)
    g2, g2_end = r.gondola(x, y, top, (1800.0, 0.0, 400.0), 6.0)
    r.jump("coin perch -> crumbling stop", perch, stop, 0.0, HARD)
    r.jump("crumbling stop -> gondola 2", stop, g2, 0.0, MID)
    top += 400.0
    previous = g2_end
    # Pistons up.
    for i in range(3):
        x, y = r.at(previous, E, 0.6, 0.0, 200.0)
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
    heights["clock wreck"] = top
    previous = clock
    # Gears off the clock, turning, east.
    for i in range(5):
        x, y = r.at(previous, E, 0.65, 0.0, 0.92 * 220.0)
        r.add("gear", x, y, top, 220.0, 40.0 if i % 2 == 0 else -40.0)
        here = circle(x, y, 0.92 * 220.0)
        r.jump("clock gear {}".format(i + 1), previous, here, 0.0, HARD)
        previous = here
    # A row of fading steps, east, taking turns.
    for i in range(10):
        rise = 100.0 if i % 2 == 0 else 0.0
        top += rise
        x, y = r.at(previous, E, 0.65, rise, 150.0)
        here = r.timed(x, y, top, 1.5 * (i % 2))
        r.jump("fading step {}".format(i + 1), previous, here, rise, HARD)
        previous = here

    # =====================================================================================================
    # 7 Hell Rift (east)
    # =====================================================================================================
    r.add("section", "7 Hell Rift")
    top += 100.0
    x, y = r.at(previous, E, 0.65, 100.0, 400.0)
    edge = r.block(x - 400.0, x + 400.0, y - 400.0, y + 400.0, top - 300.0, top, "darkstone", "Rift Edge")
    r.jump("fading step -> rift edge", previous, edge, 100.0, HARD)
    HY = y
    r.add("spot", "rift", x, y, top)
    r.add("sign", x, y + 300.0, top + 380.0, 180.0, "Hell burns below")
    previous = edge
    # Five slabs, a flame jet in the middle of each (taking turns).
    for i in range(8):
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
    CX0 = x
    # Walls round the platform: no jumping on; the heaven cage carries the player to the far side.
    WALL = 900.0
    r.block(x + 700.0, x + 800.0, HY - 600.0, HY + 600.0, top, top + WALL, "darkstone", "Rift Wall")
    r.block(x - 700.0, x + 700.0, HY + 500.0, HY + 600.0, top, top + WALL, "darkstone", "Rift Wall")
    r.block(x - 700.0, x + 700.0, HY - 600.0, HY - 500.0, top, top + WALL, "darkstone", "Rift Wall")
    far_x = x + 700.0 + 2000.0
    FAR = top + 600.0
    far = r.block(far_x, far_x + 1400.0, HY - 700.0, HY + 700.0, FAR - 400.0, FAR, "paving", "Courtyard")
    if gap(choice, far) < 1.2 * r.reach(FAR - top):
        raise RuntimeError("The courtyard can be jumped to from the cage platform")
    r.add("cages", x + 200.0, HY, top, (far_x + 300.0, HY, FAR + 100.0), 7)
    r.add("flag", far_x + 300.0, HY - 300.0, FAR)
    r.add("spot", "courtyard", far_x + 300.0, HY - 300.0, FAR)

    heights["courtyard"] = FAR
    top = FAR

    # =====================================================================================================
    # 8 Floating Wall
    # =====================================================================================================
    r.add("section", "8 Floating Wall")
    kx = far_x + 1100.0
    r.add("lever", "wall", kx, HY + 300.0, top, 0.0, 0.0)
    # Twelve giant steps, each risen from far below to its place one after another, eastward up to the wall top.
    previous = far
    sx = far_x + 1400.0
    step_top = top
    for i in range(12):
        step_top += 100.0
        x0 = sx + (0.0 if i == 0 else 0.0)
        here = rect(x0 + 200.0, HY, 400.0, 800.0)
        r.add("mech", "wall", x0 + 200.0, HY, step_top - 1500.0, (400.0, 800.0, 300.0), (0.0, 0.0, 1500.0), 0.5 + 0.35 * i, 1.0, None, "ruin", "Giant Step")
        r.jump("giant step {}".format(i + 1), previous, here, 100.0, 0.9)
        previous = here
        sx += 400.0 + 0.55 * r.reach(100.0)
    r.add("camera", "wall", (far_x + 200.0, HY - 2600.0, top + 900.0), (sx - 2000.0, HY, top + 700.0), 6.0)
    WT = step_top + 100.0
    x, y = r.at(previous, E, 0.6, 100.0, 600.0)
    wall_top = r.block(x - 600.0, x + 600.0, HY - 600.0, HY + 600.0, WT - 2500.0, WT, "ruin", "Wall Top")
    r.jump("giant step 12 -> wall top", previous, wall_top, 100.0, 0.85)
    wx, wy = middle(wall_top)
    r.block(wx - 60.0, wx + 60.0, wy - 60.0, wy + 60.0, WT, WT + 80.0, "gold", "Wing Pedestal")
    r.add("wings", wx, wy, WT + 80.0)
    heights["wall top"] = WT
    # Updrafts up, island by island (the wings needed), to the goal.
    previous, top = wall_top, WT
    x, ly = wx + 600.0, HY
    hops = ((1000.0, 0.0, 0.0, 0.0), (1200.0, 700.0, 2.8, 1.6), (1400.0, -700.0, 2.4, 1.8), (1500.0, 0.0, 2.2, 1.8), (1500.0, 700.0, 2.2, 1.8), (1600.0, -700.0, 2.0, 2.0))
    for i, (distance, side, on, off) in enumerate(hops):
        ly += side
        x += distance
        column = rect(x + 150.0, ly, 300.0)
        bottom, column_top = top - 500.0, top + 1100.0
        r.wind(x + 150.0, ly, (bottom + column_top) / 2.0, column_top - bottom, 300.0, 300.0, 0.0, 90.0, 2200.0, 900.0, on, off)
        r.glide("wing hop {}".format(i + 1), previous, top, column, bottom + 100.0)
        island_top = column_top - 100.0
        isle_x = x + 300.0 + 60.0 + 0.48 * 700.0
        here = r.block(isle_x - 340.0, isle_x + 340.0, ly - 340.0, ly + 340.0, island_top - 300.0, island_top, "ruin", "Floating Rubble")
        r.lift("updraft {} -> rubble".format(i + 1), column, column_top, here, island_top)
        if i == 2:
            # A star coin on a rubble block off this one, a plain jump away.
            cy = ly - 340.0 - 0.6 * r.reach(0.0) - 120.0
            coin_rubble = r.block(isle_x - 120.0, isle_x + 120.0, cy - 120.0, cy + 120.0, island_top - 200.0, island_top, "bronze", "Coin Rubble")
            r.jump("rubble 3 -> coin rubble", here, coin_rubble, 0.0, HARD)
            r.jump("coin rubble -> rubble 3", coin_rubble, here, 0.0, HARD)
            r.add("coin", isle_x, cy, island_top)
        previous, top = here, island_top
        x = isle_x + 340.0
    GT = top - 200.0
    gx, gy = x + 700.0 + 700.0, ly
    goal = r.block(gx - 700.0, gx + 700.0, gy - 700.0, gy + 700.0, GT - 400.0, GT, "paving", "Last Fragment")
    r.glide("last rubble -> last fragment", previous, top, goal, GT)
    r.add("goal", gx, gy, GT)
    r.lamp(gx, gy, GT + 600.0, (255, 120, 80))
    heights["goal"] = GT

    # One catcher under everything else.
    xs = [p[1] for p in r.pieces if p[0] == "block"] + [p[2] for p in r.pieces if p[0] == "block"]
    ys = [p[3] for p in r.pieces if p[0] == "block"] + [p[4] for p in r.pieces if p[0] == "block"]
    X0, X1, Y0, Y1 = min(xs) - 3000.0, max(xs) + 3000.0, min(ys) - 3000.0, max(ys) + 3000.0
    r.add("catcher", X0, X1, Y0, Y1, B - 2500.0)
    r.bounds = (X0, X1, Y0, Y1)
    r.summit_top = GT
    r.heights = heights
    return r


if __name__ == "__main__":
    route = build(2000.0, 500.9, 980.0, 600.0, 300.0)
    for name, g, rise, limit in route.checks:
        print("  {:<46} gap {:>5.0f} rise {:>6.0f} (limit {:>5.0f}){}".format(name, g, rise, limit, "  TIGHT" if g > 0.85 * limit else ""))
    for name, z in route.heights.items():
        print("  {:<18} {:>7.0f}  ({:+.0f} from the start)".format(name, z, z - route.heights["start"]))
    print("bounds {}".format(route.bounds))
    print("pieces {}, jumps {}".format(len(route.pieces), len(route.checks)))
