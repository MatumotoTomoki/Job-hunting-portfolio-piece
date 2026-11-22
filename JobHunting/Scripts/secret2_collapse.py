# Hidden area 2 (LV_Secret2) as area 2 itself, collapsed (the user, 2026-11-22): area 2's own goal kept (the roof's
# lever, the drawer steps, the catapult on the spire - now to LV_Secret3, sunk in the spire until a hidden lever
# raises it) and the way there made longer and stranger with stretches of gimmicks between the torn-apart sections
# and new gimmicks over the old ones. build_secret2_stage.py copies LV_Area2_Tower and moves each section whole by
# route.section_offsets (worked out here); the engine room is broken open (secret2_engine.py). Checked jump by jump:
#   blender -b --factory-startup --python secret2_collapse.py
#   A Engine Room  (start; from it, as the player arrives, the catapult on the goal is seen smashed by a pillar of light)
#   1 Crane Lines  three threads off a broken crane, beams and dust clouds in a crosswind      -> B+C Gear Shaft, Gondolas
#                                                                                                 (flame jets on the balcony)
#   2 Clock Ruin   the hall upside down (two gravity zones), melody gears, the clock floor (flag, time rewind) - HIDDEN:
#                  ledges down off its south side to the lever chamber, an updraft back up - fading steps
#                                                                                              -> D Beams (a crosswind)
#   3 Sun Spire    wide steps with the sun loose among them, light platforms by turns         -> E Heaven or Hell
#   the cages carry on to F+G (Clock Room, Roof: the sun on the roof), area 2's own end.
# The pieces the stretches start from and end on are area 2's (Saved/level_dump_LV_Area2_Tower.json, 2026-11-22).
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from area3_layout import rect, circle, middle, gap
from area4_layout import Route, ceiling_run, THREAD_HANG, HARD, MID, PENTA, E, N, W, S
import secret2_engine

MOVE_WITH = {"A2 107 Cage Destination": "F"}       # in E's folder, but it is where the cage puts the player (in F)
GROUPS = {"C": "B", "G": "F"}                      # sections moved together (C hangs off B; G stands on F's roof)
DOOR_A = ("A", 2400.0, 2700.0, 600.0, 1000.0, 7960.0)          # the engine room's east door sill (A2 013 Wall's top)
BRACKET_B = ("B", 2700.0, 3000.0, 650.0, 950.0, 7960.0)        # A2 039 Door Bracket
GONDOLA_END = ("B", 3150.0, 3450.0, 6350.0, 6650.0, 10360.0)   # A2 076 Gondola (C, moved with B) at its run's far end
BALCONY_D = ("D", 2800.0, 4400.0, 6700.0, 7600.0, 10360.0)     # A2 078 Second Tower Balcony
BEAM_END = ("D", 7150.0, 8000.0, 7100.0, 7200.0, 10360.0)      # A2 092 Beam
CAGE_E = ("E", 8400.0, 9600.0, 6600.0, 7700.0, 10360.0)        # A2 102 Cage Platform (walled but for its west side)
CATAPULT = ("F", 14600.0, 6500.0, 14960.0)                     # A2 182 Steam Catapult (G, moved with F)
SINK = 700.0                                                   # how far it waits down in the spire


def build(base, jump_z, gravity, walk, plat):
    r = Route(base, jump_z, gravity, walk, plat)
    heights = {"start": 7260.0}
    off = {"A": (0.0, 0.0, 0.0)}
    r.section_offsets = off

    def moved(piece):
        section, x0, x1, y0, y1, top = piece
        dx, dy, dz = off[section]
        return ("rect", x0 + dx, x1 + dx, y0 + dy, y1 + dy), top + dz

    def place(piece, after, after_top, direction=E, rise=0.0, ratio=0.6):
        # Put piece's section just past `after` along direction (E: its west edge east of after's; N: its south edge
        # north of after's), lined up on after's middle, its top `rise` above after_top.
        section, x0, x1, y0, y1, top = piece
        g = ratio * r.reach(rise)
        (ax, ay) = middle(after)
        if direction == E:
            off[section] = (after[2] + g - x0, ay - (y0 + y1) / 2.0, after_top + rise - top)
        else:
            off[section] = (ax - (x0 + x1) / 2.0, after[4] + g - y0, after_top + rise - top)
        return moved(piece)

    r.add("spot", "start", 300.0, 0.0, 7260.0)
    r.add("section", "Engine Room")
    # (the doomed catapult stands at the goal now - see the end)

    # =====================================================================================================
    # 1 Crane Lines (the engine room's door -> the gear shaft)
    # =====================================================================================================
    r.add("section", "1 Crane Lines")
    previous, top = moved(DOOR_A)
    LY = middle(previous)[1]
    ledge = r.block(previous[2], previous[2] + 500.0, LY - 250.0, LY + 250.0, top - 300.0, top, "iron", "Door Ledge")
    r.walk_on("engine door -> door ledge", previous, ledge)
    previous = ledge
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
    first_x = previous[2]
    for i in range(9):
        rise = 100.0 if i % 3 == 2 else 0.0
        top += rise
        if i % 3 == 1:
            x, y = r.at(previous, E, 0.55, rise, 0.4 * 400.0)
            here = r.vanish(x, y, top, 400.0, 0.8, 2.0)
        else:
            x, y = r.at(previous, E, 0.6, rise, 350.0)
            here = r.block(x - 350.0, x + 350.0, y - 60.0, y + 60.0, top - 80.0, top, "iron", "Broken Beam")
        r.jump("beam {}".format(i + 1), previous, here, rise, HARD)
        previous = here
        if i == 3:
            cx, cy = middle(here)
            cy += 60.0 + 0.6 * r.reach(0.0) + 90.0
            perch = r.block(cx - 90.0, cx + 90.0, cy - 90.0, cy + 90.0, top - 150.0, top, "bronze", "Coin Perch")
            r.jump("beam 4 -> coin perch (upwind)", here, perch, 0.0, HARD)
            r.jump("coin perch -> beam 4", perch, here, 0.0, HARD)
            r.add("coin", cx, cy, top)
    r.wind((first_x + previous[2]) / 2.0, LY, top - 100.0, previous[2] - first_x + 400.0, 1400.0, 900.0, -90.0, 0.0, 600.0, 400.0, 2.0, 2.2, 0.0)
    x, y = r.at(previous, E, 0.6, 0.0, 300.0)
    landing = r.block(x - 300.0, x + 300.0, LY - 300.0, LY + 300.0, top - 300.0, top, "iron", "Crane Base")
    r.jump("beam -> crane base", previous, landing, 0.0, HARD)
    bracket, bt = place(BRACKET_B, landing, top)
    r.jump("crane base -> the gear shaft", landing, bracket, 0.0, HARD)
    off["C"] = off["B"]
    dx, dy, dz = off["B"]
    r.add("spot", "shaft", 2850.0 + dx, 800.0 + dy, 7960.0 + dz)
    r.add("flame", 3600.0 + dx, 900.0 + dy, 9660.0 + dz, 0.0, 0.0, 0.8, 1.4, 1.8, "shaft")
    heights["gear shaft"] = bt

    # =====================================================================================================
    # 2 Clock Ruin (the gondola's far end -> the second tower), with the hidden lever
    # =====================================================================================================
    r.add("section", "2 Clock Ruin")
    gondola, top = moved(GONDOLA_END)
    LY = middle(gondola)[1]
    x0 = gondola[2] + 0.5 * r.reach(0.0)
    start = r.block(x0, x0 + 900.0, LY - 450.0, LY + 450.0, top - 300.0, top, "iron", "Hall Fragment")
    r.jump("gondola -> hall fragment", gondola, start, 0.0, HARD)
    r.add("sign", x0 + 300.0, LY + 500.0, top + 380.0, 180.0, "The hall hangs upside down")
    RISE = 900.0
    x_start = start[2]
    zones = (
        (("gap", -100.0, 400.0, 0.85), ("red", -100.0, 0.85), ("switch", 0.0, 0.7), ("blue", 100.0, 0.85),
         ("gear", 0.0, 240.0, 40.0, 0.75), ("gap", 0.0, 500.0, 0.85)),
        (("fade", -100.0, 0.0, 0.85), ("gap", -100.0, 300.0, 0.88), ("gear", 0.0, 220.0, -50.0, 0.75),
         ("fade", 0.0, 1.0, 0.85), ("gap", 100.0, 300.0, 0.88), ("gap", 0.0, 600.0, 0.85)),
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
    top, previous = ltop, landing
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
    # HIDDEN: off the clock floor's south edge, out of sight, ledges down to the lever chamber; an updraft back up.
    previous_h, htop = clock, CT
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
    col = ("rect", chamber[2] + 60.0, chamber[2] + 360.0, y - 150.0, y + 150.0)
    col_bottom, col_top = htop - 300.0, CT + 300.0
    r.wind((col[1] + col[2]) / 2.0, y, (col_bottom + col_top) / 2.0, col_top - col_bottom, 300.0, 300.0, 0.0, 90.0, 2200.0, 900.0)
    r.jump("lever chamber -> updraft", chamber, col, 0.0, HARD)
    back = r.block(col[2] + 40.0, col[2] + 340.0, y - 150.0, y + 150.0, CT + 100.0, CT + 200.0, "rock", "Hidden Ledge")
    r.lift("updraft -> ledge", col, col_top, back, CT + 200.0)
    previous_h, n = back, 0
    while gap(previous_h, clock) > 0.8 * r.reach(-200.0):
        n += 1
        direction = N if middle(previous_h)[1] < clock[3] - 200.0 else E
        x, y2 = r.at(previous_h, direction, 0.65, 0.0, 150.0)
        here = r.block(x - 150.0, x + 150.0, y2 - 150.0, y2 + 150.0, CT + 100.0, CT + 200.0, "rock", "Hidden Ledge")
        r.jump("way back {}".format(n), previous_h, here, 0.0, HARD)
        previous_h = here
    r.jump("way back -> clock floor", previous_h, clock, -200.0, HARD)
    previous = clock
    for i in range(8):
        rise = 100.0 if i % 2 == 0 else 0.0
        top += rise
        x, y = r.at(previous, E, 0.65, rise, 150.0)
        here = r.timed(x, y, top, 0.5 * i)     # a wave (0.5 s apart): neighbours share 1.3 s (by turns left 0.3 s)
        r.jump("fading step {}".format(i + 1), previous, here, rise, HARD)
        previous = here
    top += 100.0
    x, y = r.at(previous, E, 0.6, 100.0, 300.0)
    clock_end = r.block(x - 300.0, x + 300.0, y - 300.0, y + 300.0, top - 300.0, top, "iron", "Clock Ledge")
    r.jump("fading step -> clock ledge", previous, clock_end, 100.0, HARD)
    balcony, dt = place(BALCONY_D, clock_end, top, N)
    r.jump("clock ledge -> the second tower", clock_end, balcony, 0.0, HARD)
    dx, dy, dz = off["D"]
    r.wind(6300.0 + dx, 7150.0 + dy, 10560.0 + dz, 3400.0, 1200.0, 700.0, -90.0, 0.0, 500.0, 350.0, 2.0, 2.5, 0.0)
    heights["second tower"] = dt

    # =====================================================================================================
    # 3 Sun Spire (the last beam -> the cage platform)
    # =====================================================================================================
    r.add("section", "3 Sun Spire")
    beam, top = moved(BEAM_END)
    LY = middle(beam)[1]
    top += 100.0
    x, y = r.at(beam, E, 0.65, 100.0, 500.0)
    spire0 = r.block(x - 500.0, x + 500.0, LY - 500.0, LY + 500.0, top - 300.0, top, "darkstone", "Spire Floor")
    r.jump("beam -> spire floor", beam, spire0, 100.0, HARD)
    r.add("spot", "spire", x, LY, top)
    SX0, ST = x, top
    previous = spire0
    for i in range(8):
        top += 100.0
        x, y = r.at(previous, E if i % 2 == 0 else (N if i % 4 == 1 else S), 0.65, 100.0, 250.0)
        here = r.block(x - 250.0, x + 250.0, y - 250.0, y + 250.0, top - 200.0, top, "darkstone", "Spire Step")
        r.jump("spire step {}".format(i + 1), previous, here, 100.0, HARD)
        previous = here
    r.add("sun", (SX0 + middle(previous)[0]) / 2.0, LY, ST, "spire", (2200.0, 2200.0, 2200.0), 3000.0)
    for i in range(8):
        top += 100.0
        x, y = r.at(previous, E, 0.55, 100.0, 130.0, side=(150.0 if i % 2 else -150.0))
        name = "spire{}".format(i + 1)
        r.beam(name, x, y, top - 300.0, top + 700.0, 400.0, 3.0, 2.4, 0.9 * i)    # a wave up (see secret_collapse.py)
        here = r.lplat(name, x, y, top, 260.0)
        r.jump("spire light {}".format(i + 1), previous, here, 100.0, 0.8)
        previous = here
        if i == 5:
            rx, ry = x, y + 130.0 + 0.55 * r.reach(0.0) + 110.0
            r.beam("rare", rx, ry, top - 300.0, top + 700.0, 300.0, 1.6, 5.0, 0.0)
            rare = r.lplat("rare", rx, ry, top, 220.0)
            r.jump("spire light 6 -> rare light", here, rare, 0.0, 0.7)
            r.add("coin", rx, ry, top)
    top += 100.0
    x, y = r.at(previous, E, 0.6, 100.0, 300.0)
    spire_top = r.block(x - 300.0, x + 300.0, LY - 300.0, LY + 300.0, top - 300.0, top, "darkstone", "Spire Top")
    r.jump("spire light -> spire top", previous, spire_top, 100.0, 0.85)
    r.add("flag", x, LY, top)
    r.add("spot", "spire top", x, LY, top)
    cage, ct = place(CAGE_E, spire_top, top)
    r.jump("spire top -> the cage platform", spire_top, cage, 0.0, HARD)
    heights["cage platform"] = ct

    # The cages carry on to F+G, which stand well away, higher: area 2's own way up to the roof and its end.
    ex, ey, ez = off["E"]
    off["F"] = (ex + 4000.0, ey, ez + 700.0)
    off["G"] = off["F"]
    dx, dy, dz = off["F"]
    r.add("spot", "roof", 10400.0 + dx, 5700.0 + dy, 13660.0 + dz)
    r.add("sun", 11000.0 + dx, 6500.0 + dy, 13660.0 + dz, "roof", (1800.0, 1800.0, 1800.0), 2500.0)
    _, cx, cy, cz = CATAPULT
    # The goal, as it first seems: a catapult on the spire top, smashed by the pillar of light as the player arrives
    # (the user, 2026-11-22: "put this catapult at the goal"); the pillar stays there as a trap back to the start until
    # the hidden lever puts it out and brings the real catapult up out of the spire.
    r.add("doomed", cx + dx, cy + dy, cz + dz, "start", "catapult")
    r.add("exit_catapult", cx + dx, cy + dy, cz + dz, SINK, "catapult")
    r.add("camera", "catapult", (cx + dx - 1800.0, cy + dy - 1800.0, cz + dz + 900.0), (cx + dx, cy + dy, cz + dz + 200.0), 6.0)
    heights["spire (goal)"] = cz + dz

    xs = [p[1] for p in r.pieces if p[0] == "block"] + [p[2] for p in r.pieces if p[0] == "block"] + [-300.0, 15600.0 + dx]
    ys = [p[3] for p in r.pieces if p[0] == "block"] + [p[4] for p in r.pieces if p[0] == "block"] + [-1500.0, 8000.0 + dy]
    X0, X1, Y0, Y1 = min(xs) - 3000.0, max(xs) + 3000.0, min(ys) - 3000.0, max(ys) + 3000.0
    r.add("catcher", X0, X1, Y0, Y1, 4000.0)
    r.bounds = (X0, X1, Y0, Y1)
    r.summit_top = cz + dz
    r.heights = heights
    return r


if __name__ == "__main__":
    route = build(7260.0, 500.9, 980.0, 600.0, 300.0)
    for name, g, rise, limit in route.checks:
        if "->" in name:
            print("  {:<46} gap {:>5.0f} rise {:>6.0f} (limit {:>5.0f})".format(name, g, rise, limit))
    for name, z in route.heights.items():
        print("  {:<18} {:>7.0f}".format(name, z))
    for k, v in sorted(route.section_offsets.items()):
        print("  offset {} = ({:.0f}, {:.0f}, {:.0f})".format(k, *v))
    print("pieces {}, jumps {}".format(len(route.pieces), len(route.checks)))
