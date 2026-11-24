# Hidden area 2's (LV_Secret2) route as plain data, checked jump by jump; build_secret2_stage.py places it.
#   blender -b --factory-startup --python secret2_layout.py
# "Area 2, collapsed" (the user, 2026-11-22): the machine tower burst apart, its pieces hanging in the red dusk. Area 2
# itself (LV_Area2_Tower and its blueprints) is not touched. As long as hidden stage 1; gimmicks from every area.
#   0 Arrival          the gear from hidden stage 1 comes up through the start platform (BP_GearArrival). On the same
#                      platform stands a steam catapult - the way out, it seems - until, on arrival, the sun's
#                      target ring shows on it and a pillar of light smashes it. The pillar stays: it looks like the
#                      goal, but walking in sends the player back to the start (BP_CatapultSmash).
#   1 Engine Wreck     north: red and blue blocks and a switch (a switch on the start platform resets them)
#   2 Gear Shaft       up: turning gears and pistons, a star coin on a gear off the way
#   3 Gondola Line     east: three gondolas between crumbling stops (flag 1)
#   4 Broken Beams     east: narrow beams in a gusting crosswind, dust clouds; a star coin
#   5 Upside Down      the engine hall hanging upside down: two gravity zones (flag 2 between)
#   6 Clock Ruin       melody gears, a time rewind floor (flag 3), fading steps. HIDDEN: off the clock floor's
#                      far side, out of sight, ledges drop to the lever chamber; pulling the lever shows the new
#                      catapult rising on the roof; an updraft carries the player back up
#   7 Sun Spire        the sun loose among wide platforms (it charges; caught, back to flag 3); light platforms
#   8 Roof             up to the roof: the catapult pit under a hatch (both opened by the lever) - the catapult to hidden area 3
# Pieces: as secret_layout.py plus
#   ("seal", x, y, top)            BP_GearArrival over a 528 cm square hole (the blocks round it are in the layout)
#   ("doomed", x, y, top, spot)    the catapult smashed on arrival (BP_SteamCatapult + BP_CatapultSmash; back to spot)
#   ("exit_catapult", x, y, top, sink, lever)   BP_SteamCatapult to LV_Secret3, sunk `sink` under the roof in a pit,
#                                  raised by BP_ActorRiser when the lever is pulled
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from area3_layout import rect, circle, middle, gap, beyond
from area4_layout import Route, ceiling_run, THREAD_HANG, HARD, MID, EASY, PENTA, E, N, W, S

HOLE = 264.0


def holed(r, x0, x1, y0, y1, top, thick, cx, cy, look, name):
    # A floor with a square hole (half HOLE) round (cx, cy); returns its footing (the whole floor counts).
    r.block(x0, x1, cy + HOLE, y1, top - thick, top, look, name)
    r.block(x0, x1, y0, cy - HOLE, top - thick, top, look, name)
    r.block(x0, cx - HOLE, cy - HOLE, cy + HOLE, top - thick, top, look, name)
    r.block(cx + HOLE, x1, cy - HOLE, cy + HOLE, top - thick, top, look, name)
    return ("rect", x0, x1, y0, y1)


def continue_from(r, previous, top, LY, heights):
    # Sections 4-8 (beams, upside down, the clock with the hidden lever, the sun spire, the roof with the catapult pit),
    # from the footing previous at 	op, heading east along y = LY. Also used by secret2_collapse.py (2026-11-22).
    # =====================================================================================================
    # 4 Broken Beams (east): narrow beams, a gusting crosswind (blowing south), dust clouds
    # =====================================================================================================
    r.add("section", "4 Broken Beams")
    first_x = previous[2]
    for i in range(16):
        rise = 100.0 if i % 3 == 2 else 0.0
        top += rise
        if i % 3 == 1:
            x, y = r.at(previous, E, 0.55, rise, 0.4 * 400.0)
            here = r.vanish(x, y, top, 400.0, 0.8, 2.0)
        else:
            length = 700.0
            x, y = r.at(previous, E, 0.6, rise, length / 2.0)
            here = r.block(x - length / 2.0, x + length / 2.0, y - 60.0, y + 60.0, top - 80.0, top, "iron", "Broken Beam")
        r.jump("beam {}".format(i + 1), previous, here, rise, HARD)
        previous = here
        if i == 5:
            cx, cy = middle(here)
            cy += 60.0 + 0.6 * r.reach(0.0) + 90.0
            perch = r.block(cx - 90.0, cx + 90.0, cy - 90.0, cy + 90.0, top - 150.0, top, "bronze", "Coin Perch")
            r.jump("beam 6 -> coin perch (upwind)", here, perch, 0.0, HARD)
            r.jump("coin perch -> beam 6", perch, here, 0.0, HARD)
            r.add("coin", cx, cy, top)
    last_x = previous[2]
    r.wind((first_x + last_x) / 2.0, LY, top - 100.0, last_x - first_x + 400.0, 1400.0, 900.0, -90.0, 0.0, 600.0, 400.0, 2.0, 2.2, 0.0)
    # Threads hanging from a broken crane: catch, climb, leap to the next beam.
    for k in range(3):
        tx = previous[2] + 0.55 * r.reach(0.0)
        bottom = top + 60.0
        anchor = bottom + 1100.0 + 200.0 * k
        r.thread(tx, LY, anchor, anchor - bottom, 15.0 * k, 3.5, 0.0, 0.0, 90.0)
        r.catch("crane thread {}".format(k + 1), previous, top, tx, LY, bottom)
        top = anchor - THREAD_HANG - 200.0
        here = r.block(tx + 380.0, tx + 1080.0, LY - 60.0, LY + 60.0, top - 80.0, top, "iron", "Crane Arm")
        r.leap("crane thread {} -> arm".format(k + 1), tx, LY, anchor, here, top)
        previous = here
    top += 100.0
    x, y = r.at(previous, E, 0.6, 100.0, 450.0)
    hall_floor = r.block(x - 450.0, x + 450.0, LY - 450.0, LY + 450.0, top - 300.0, top, "iron", "Hall Floor")
    r.jump("beam -> hall floor", previous, hall_floor, 100.0, HARD)
    heights["hall floor"] = top

    # =====================================================================================================
    # 5 Upside Down (east)
    # =====================================================================================================
    r.add("section", "5 Upside Down")
    RISE = 900.0
    x_start = hall_floor[2]
    zones = (
        (("gap", -100.0, 400.0, 0.85), ("red", -100.0, 0.85), ("switch", 0.0, 0.7), ("blue", 100.0, 0.85),
         ("gear", 0.0, 240.0, 40.0, 0.75), ("gap", 0.0, 500.0, 0.85)),
        (("fade", -100.0, 0.0, 0.85), ("gap", -100.0, 300.0, 0.88), ("gear", 0.0, 220.0, -50.0, 0.75),
         ("fade", 0.0, 1.0, 0.85), ("gap", 100.0, 300.0, 0.88), ("gear", 0.0, 200.0, 60.0, 0.75), ("gap", 0.0, 600.0, 0.85)),
        (("gap", -100.0, 300.0, 0.88), ("fade", -100.0, 0.5, 0.85), ("gear", 0.0, 220.0, 55.0, 0.75),
         ("gap", 100.0, 250.0, 0.88), ("fade", 0.0, 1.3, 0.85), ("gap", 0.0, 600.0, 0.85)),
    )
    ltop = top
    for z, items in enumerate(zones):
        cu = ltop + RISE
        last, last_u, end = ceiling_run(r, LY, x_start - 300.0, cu, items, "hall ceiling {}".format(z + 1))
        z_end = end + 200.0
        r.under(end, z_end + 400.0, LY - 250.0, LY + 250.0, last_u, look="iron", name="Ceiling")
        r.gzone(x_start + 60.0, z_end, LY - 600.0, LY + 600.0, ltop - 400.0, cu + 900.0)
        r.add("catcher", x_start + 60.0, z_end, LY - 600.0, LY + 600.0, cu + 450.0)
        ltop = min(cu, last_u) - 350.0
        landing = r.block(z_end + 60.0, z_end + 960.0, LY - 600.0, LY + 600.0, ltop - 200.0, ltop, "iron", "Landing")
        if z == 0:
            r.add("flag", z_end + 500.0, LY, ltop)
            r.add("spot", "hall", z_end + 500.0, LY, ltop)
            r.add("switch", z_end + 500.0, LY + 450.0, ltop)
        x_start = z_end + 960.0
        heights["hall landing {}".format(z + 1)] = ltop
    top = ltop
    previous = landing

    # =====================================================================================================
    # 6 Clock Ruin (east): melody gears, the clock floor, fading steps; the hidden way to the lever
    # =====================================================================================================
    r.add("section", "6 Clock Ruin")
    JR = 110.0
    for i in range(6):
        top += 80.0
        x, y = r.at(previous, E, 0.45, 80.0, JR, side=(90.0 if i % 2 else -90.0))
        here = r.jewel(x, y, top, JR, i, 2, 6, 0.8, PENTA[i])
        r.jump("melody gear {}".format(i + 1), previous, here, 80.0, 0.55)
        previous = here
    top += 80.0
    x, y = r.at(previous, E, 0.65, 80.0, 700.0)
    clock = r.block(x - 700.0, x + 700.0, LY - 700.0, LY + 700.0, top - 400.0, top, "bronze", "Clock Floor")
    r.jump("melody gear -> clock floor", previous, clock, 80.0, MID)
    CX, CT = x, top
    r.add("flag", CX - 300.0, LY + 300.0, CT)
    r.add("spot", "clock", CX - 300.0, LY + 300.0, CT)
    r.add("rewind", CX + 200.0, LY - 300.0, CT)
    r.lamp(CX, LY, CT + 700.0, (255, 160, 90))
    heights["clock floor"] = CT
    # HIDDEN: from the clock floor's south edge, ledges drop down out of sight, west, to the lever chamber.
    previous_h, htop = clock, CT
    hy = clock[3]
    for i in range(6):
        drop = -250.0 if i < 3 else 0.0
        htop += drop
        x, y = r.at(previous_h, (S, S, W, W, S, S)[i], 0.6, drop, 130.0)
        here = r.block(x - 130.0, x + 130.0, y - 130.0, y + 130.0, htop - 200.0, htop, "rock", "Hidden Ledge")
        r.jump("hidden ledge {}".format(i + 1), previous_h, here, drop, HARD)
        previous_h = here
    x, y = r.at(previous_h, S, 0.6, 0.0, 400.0)
    chamber = r.block(x - 400.0, x + 400.0, y - 400.0, y + 400.0, htop - 300.0, htop, "bronze", "Lever Chamber")
    r.jump("hidden ledge -> lever chamber", previous_h, chamber, 0.0, HARD)
    r.block(x - 400.0, x + 400.0, y - 400.0, y + 400.0, htop + 700.0, htop + 800.0, "rock", "Chamber Roof")
    r.add("lever", "catapult", x, y, htop, 90.0, 0.0)
    r.lamp(x, y, htop + 500.0, (255, 190, 120))
    # Back up: an updraft beside the chamber to a ledge level with the clock floor, then onto it.
    col = ("rect", chamber[2] + 60.0, chamber[2] + 360.0, y - 150.0, y + 150.0)
    col_bottom, col_top = htop - 300.0, CT + 300.0
    r.wind((col[1] + col[2]) / 2.0, y, (col_bottom + col_top) / 2.0, col_top - col_bottom, 300.0, 300.0, 0.0, 90.0, 2200.0, 900.0)
    r.jump("lever chamber -> updraft", chamber, col, 0.0, HARD)
    back = r.block(col[2] + 40.0, col[2] + 340.0, y - 150.0, y + 150.0, CT + 100.0, CT + 200.0, "rock", "Hidden Ledge")
    r.lift("updraft -> ledge", col, col_top, back, CT + 200.0)
    # Ledges back north (level) until the clock floor is in reach.
    previous_h, n = back, 0
    while gap(previous_h, clock) > 0.8 * r.reach(-200.0):
        n += 1
        direction = N if middle(previous_h)[1] < clock[3] - 200.0 else E
        x, y2 = r.at(previous_h, direction, 0.65, 0.0, 150.0)
        here = r.block(x - 150.0, x + 150.0, y2 - 150.0, y2 + 150.0, CT + 100.0, CT + 200.0, "rock", "Hidden Ledge")
        r.jump("way back {}".format(n), previous_h, here, 0.0, HARD)
        previous_h = here
    r.jump("way back -> clock floor", previous_h, clock, -200.0, HARD)
    # On: fading steps east.
    previous = clock
    for i in range(12):
        rise = 100.0 if i % 2 == 0 else 0.0
        top += rise
        x, y = r.at(previous, E, 0.65, rise, 150.0)
        here = r.timed(x, y, top, 1.5 * (i % 2))
        r.jump("fading step {}".format(i + 1), previous, here, rise, HARD)
        previous = here

    # =====================================================================================================
    # 7 Sun Spire (east): wide platforms with the sun loose among them, then light platforms
    # =====================================================================================================
    r.add("section", "7 Sun Spire")
    top += 100.0
    x, y = r.at(previous, E, 0.65, 100.0, 500.0)
    spire0 = r.block(x - 500.0, x + 500.0, LY - 500.0, LY + 500.0, top - 300.0, top, "darkstone", "Spire Floor")
    r.jump("fading step -> spire floor", previous, spire0, 100.0, HARD)
    r.add("spot", "spire", x, LY, top)
    SX0, ST = x, top
    previous = spire0
    for i in range(12):
        rise = 100.0
        top += rise
        x, y = r.at(previous, E if i % 2 == 0 else (N if i % 4 == 1 else S), 0.65, rise, 250.0)
        here = r.block(x - 250.0, x + 250.0, y - 250.0, y + 250.0, top - 200.0, top, "darkstone", "Spire Step")
        r.jump("spire step {}".format(i + 1), previous, here, rise, HARD)
        previous = here
    r.add("sun", (SX0 + middle(previous)[0]) / 2.0, LY, ST, "spire", (2200.0, 2200.0, 2200.0), 3000.0)
    # Light platforms in turns, east.
    for i in range(12):
        top += 100.0
        x, y = r.at(previous, E, 0.55, 100.0, 130.0, side=(150.0 if i % 2 else -150.0))
        beam = "spire{}".format(i + 1)
        r.beam(beam, x, y, top - 300.0, top + 700.0, 400.0, 2.8, 2.0, 0.0 if i % 2 == 0 else 2.4)
        here = r.lplat(beam, x, y, top, 260.0)
        r.jump("spire light {}".format(i + 1), previous, here, 100.0, 0.8)
        previous = here
        if i == 5:
            rx, ry = x, y + 130.0 + 0.55 * r.reach(0.0) + 110.0
            r.beam("rare", rx, ry, top - 300.0, top + 700.0, 300.0, 1.6, 5.0, 0.0)
            rare = r.lplat("rare", rx, ry, top, 220.0)
            r.jump("spire light 6 -> rare light", here, rare, 0.0, 0.7)
            r.add("coin", rx, ry, top)
    top += 100.0
    x, y = r.at(previous, E, 0.6, 100.0, 500.0)
    spire_top = r.block(x - 500.0, x + 500.0, LY - 500.0, LY + 500.0, top - 300.0, top, "darkstone", "Spire Top")
    r.jump("spire light -> spire top", previous, spire_top, 100.0, 0.85)
    r.add("flag", x, LY - 250.0, top)
    r.add("spot", "spire top", x, LY - 250.0, top)
    heights["spire top"] = top
    previous = spire_top

    # =====================================================================================================
    # 8 Roof: crumbling and fading steps, two ledge grabs, the roof with the catapult pit
    # =====================================================================================================
    r.add("section", "8 Roof")
    for i, kind in enumerate(("falling", "block", "timed", "block", "falling", "block", "timed", "block", "falling", "block", "timed", "block")):
        rise = 100.0 if kind == "block" else 0.0
        top += rise
        x, y = r.at(previous, N, 0.65, rise, 150.0, side=(150.0 if i % 2 else -150.0))
        if kind == "falling":
            here = r.falling(x, y, top)
        elif kind == "timed":
            here = r.timed(x, y, top, 0.0 if i % 4 == 2 else 1.5)
        else:
            here = r.block(x - 150.0, x + 150.0, y - 150.0, y + 150.0, top - 200.0, top, "iron", "Roof Debris")
        r.jump("roof debris {}".format(i + 1), previous, here, rise, HARD)
        previous = here
        if i == 3:
            cx, cy = r.at(here, E, 0.7, 100.0, 90.0)
            perch = r.block(cx - 90.0, cx + 90.0, cy - 90.0, cy + 90.0, top - 150.0, top + 100.0, "bronze", "Coin Perch")
            r.jump("roof debris 4 -> coin perch", here, perch, 100.0, HARD)
            r.jump("coin perch -> roof debris 4", perch, here, -100.0, HARD)
            r.add("coin", cx, cy, top + 100.0)
    x, y = r.at(previous, N, 0.6, 0.0, 400.0)
    ledge = r.block(x - 400.0, x + 400.0, y - 300.0, y + 300.0, top - 400.0, top, "iron", "Roof Ledge")
    r.jump("roof debris -> roof ledge", previous, ledge, 0.0, HARD)
    previous = ledge
    for i in range(2):
        here_top = top + 220.0
        y1 = previous[4]
        here = r.block(previous[1], previous[2], y1, y1 + 400.0, here_top - 600.0, here_top, "iron", "Roof Step")
        r.grab("roof step {}".format(i + 1), previous, here, 220.0)
        previous, top = here, here_top
    px, py = middle(previous)
    RX0, RX1, RY0, RY1 = px - 1000.0, px + 1000.0, previous[4], previous[4] + 2000.0
    PX, PY = px, RY0 + 1200.0
    roof = holed(r, RX0, RX1, RY0, RY1, top + 100.0, 300.0, PX, PY, "iron", "Roof")
    r.jump("roof step -> roof", previous, roof, 100.0, 0.85)
    top += 100.0
    # The pit under the hole, and the catapult sunk in it until the lever is pulled.
    r.block(PX - HOLE, PX + HOLE, PY - HOLE, PY + HOLE, top - 1100.0, top - 1000.0, "iron", "Pit Floor")
    r.add("exit_catapult", PX, PY, top, 700.0, "catapult")
    # A hatch over the hole (the user, 11-22: without it the player just dropped in onto the sunk catapult); the lever
    # slides it aside before the catapult comes up.
    r.add("mech", "catapult", PX, PY, top + 20.0, (2.0 * HOLE + 60.0, 2.0 * HOLE + 60.0, 60.0), (2.0 * HOLE + 200.0, 0.0, 0.0), 0.3, 1.5, None, "iron", "Pit Hatch")
    r.add("camera", "catapult", (PX - 1800.0, PY - 1800.0, top + 900.0), (PX, PY, top + 200.0), 6.0)
    r.add("sign", PX, RY1 - 100.0, top + 380.0, -90.0, "The way on is shut")
    heights["roof"] = top

    return top


def build(base, jump_z, gravity, walk, plat):
    r = Route(base, jump_z, gravity, walk, plat)
    B = base
    heights = {"start": B}

    # =====================================================================================================
    # 0 Arrival
    # =====================================================================================================
    r.add("section", "0 Arrival")
    GX, GY = -800.0, 0.0
    start = holed(r, -1500.0, 1500.0, -1000.0, 1000.0, B, 300.0, GX, GY, "iron", "Arrival Deck")
    r.add("seal", GX, GY, B)
    r.add("start", GX, GY, B, 0.0)
    r.add("spot", "start", GX - 450.0, GY, B)
    r.add("doomed", 800.0, 0.0, B, "start")
    r.add("switch", -1200.0, 700.0, B)
    previous, top = start, B

    # =====================================================================================================
    # 1 Engine Wreck (north): red steps, a switch on a pedestal, blue steps
    # =====================================================================================================
    r.add("section", "1 Engine Wreck")
    x_line = -800.0
    for i, colour in enumerate(("red", "red", "red", "red", "switch", "blue", "blue", "blue", "blue", "blue")):
        rise = 100.0 if colour != "switch" else 0.0
        top += rise
        x, y = r.at(previous, N, 0.65, rise, 120.0, side=(150.0 if i % 2 else -150.0) if i else (x_line - middle(previous)[0]))
        if colour == "switch":
            here = r.block(x - 120.0, x + 120.0, y - 120.0, y + 120.0, top - 400.0, top, "iron", "Switch Pedestal")
            r.add("switch", x, y, top)
        else:
            r.add("sblock", x, y, top, 240.0, colour == "red")
            here = rect(x, y, 240.0)
        r.jump("engine block {}".format(i + 1), previous, here, rise, HARD)
        previous = here
    top += 100.0
    x, y = r.at(previous, N, 0.65, 100.0, 400.0)
    ew_end = r.block(x - 400.0, x + 400.0, y - 400.0, y + 400.0, top - 300.0, top, "iron", "Engine Floor")
    r.jump("engine block -> engine floor", previous, ew_end, 100.0, HARD)
    previous = ew_end

    # =====================================================================================================
    # 2 Gear Shaft (north and up): gears and pistons by turns
    # =====================================================================================================
    r.add("section", "2 Gear Shaft")
    for i in range(16):
        if i % 2 == 0:
            x, y = r.at(previous, N, 0.6, 0.0, 0.92 * 230.0, side=(200.0 if i % 4 else -200.0))
            r.add("gear", x, y, top, 230.0, 35.0 if i % 4 else -35.0)
            here = circle(x, y, 0.92 * 230.0)
            r.jump("shaft gear {}".format(i // 2 + 1), previous, here, 0.0, HARD)
            previous = here
            if i == 4:
                cx, cy = x + 0.92 * 230.0 + 0.6 * r.reach(0.0) + 0.92 * 160.0, y
                r.add("gear", cx, cy, top, 160.0, 70.0)
                coin_gear = circle(cx, cy, 0.92 * 160.0)
                r.jump("shaft gear 3 -> coin gear", here, coin_gear, 0.0, HARD)
                r.jump("coin gear -> shaft gear 3", coin_gear, here, 0.0, HARD)
                r.add("coin", cx, cy, top)
        else:
            x, y = r.at(previous, N, 0.6, 0.0, 200.0)
            piston, piston_up = r.moving(x, y, top, (0.0, 0.0, 400.0), 2.5, 1.5, 400.0)
            r.jump("shaft piston {}".format(i // 2 + 1), previous, piston, 0.0, MID)
            top += 400.0
            previous = piston_up
    top += 100.0
    x, y = r.at(previous, N, 0.65, 100.0, 500.0)
    shaft_top = r.block(x - 500.0, x + 500.0, y - 500.0, y + 500.0, top - 300.0, top, "iron", "Shaft Head")
    r.jump("shaft -> shaft head", previous, shaft_top, 100.0, MID)
    heights["shaft head"] = top
    previous = shaft_top

    # =====================================================================================================
    # 3 Gondola Line (east)
    # =====================================================================================================
    r.add("section", "3 Gondola Line")
    LY = middle(previous)[1]
    for i, (dx, dz) in enumerate(((1800.0, 300.0), (2000.0, 300.0), (1600.0, 200.0), (1800.0, 400.0))):
        x = previous[2] + 0.5 * r.reach(0.0) + 150.0
        g, g_end = r.gondola(x, LY, top, (dx, 0.0, dz), 6.0 + i * 0.5)
        r.jump("gondola {}".format(i + 1), previous, g, 0.0, MID)
        top += dz
        x, y = r.at(g_end, E, 0.6, 0.0, 150.0)
        stop = r.falling(x, y, top) if i < 3 else r.block(x - 600.0, x + 600.0, y - 500.0, y + 500.0, top - 300.0, top, "iron", "Gondola Station")
        r.jump("gondola {} -> stop".format(i + 1), g_end, stop, 0.0, MID)
        previous = stop
    sx, sy = middle(previous)
    r.add("flag", sx, sy - 250.0, top)
    r.add("spot", "station", sx, sy - 250.0, top)
    heights["gondola station"] = top

    top = continue_from(r, previous, top, LY, heights)

    xs = [p[1] for p in r.pieces if p[0] == "block"] + [p[2] for p in r.pieces if p[0] == "block"]
    ys = [p[3] for p in r.pieces if p[0] == "block"] + [p[4] for p in r.pieces if p[0] == "block"]
    X0, X1, Y0, Y1 = min(xs) - 3000.0, max(xs) + 3000.0, min(ys) - 3000.0, max(ys) + 3000.0
    r.add("catcher", X0, X1, Y0, Y1, B - 2500.0)
    r.bounds = (X0, X1, Y0, Y1)
    r.summit_top = top
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
