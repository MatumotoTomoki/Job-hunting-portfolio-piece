# Hidden area 4 (LV_Secret4) as area 4 itself, collapsed - the last hidden stage (the user, 2026-11-23): area 4's own
# way kept (threads, jewel forest, upside down, dark tower, Iwato, wings, updrafts) and made longer with stretches of
# gimmicks between its sections; its goal kept but crumbling: the gate's island and the island before it are gone,
# the way up to the gate is a stair of crumbling stones (art without them: build_heaven_art_blender.py --skip), and the
# gate is BP_SecretGate (the hidden stages' end: ACH_SECRET_CLEAR, then the title). build_secret4_stage.py copies
# LV_Area4_Heaven and moves each section whole by route.section_offsets (worked out here). Checked jump by jump:
#   blender -b --factory-startup --python secret4_collapse.py
# Area 4's sections interlock, so a stretch ends on a copy of the piece it set out from, and the next section is moved
# so that copy stands where that piece stood for it (every jump into the next section stays as it was):
#   1 Spider Threads  -> 1 Sun Court       wide slabs and blocks up, the sun loose      -> (a copy of the forest floor)
#      (the jewel forest itself is left as it was: a crosswind on its timed jewels was not crossable)
#   2 Jewel Forest    -> 2 Wind Tunnel     beams and dust clouds in a crosswind, jewels -> (a copy of the upside-down floor)
#   3 Upside Down     -> 3 Light Maze      lit stones as a wave, a swept row, a rare one -> the tower's landing
#      (a copy of that landing catches the player out of the last gravity zone)
#   4 Dark Tower + 5 Iwato -> 4 Falling Sky  with the wings: updrafts, rubble, crumbling stones -> (a copy of the corridor's end)
#   6 Heaven's Gate: kept whole; trials on its first four islands (each onward updraft asleep until its trial is done).
# Positions are the level's own (Saved/level_dump_LV_Area4_Heaven.json, 2026-11-22: sections 2-6 stand 23 cm west and
# 17 cm north of area4_layout.py's numbers).
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from area3_layout import rect, circle, middle, gap
from area4_layout import Route, HARD, MID, PENTA, E, N, W, S
import secret_collapse

GROUPS = {"5": "4"}                                            # the Iwato stands on the tower's roof
FOREST = ("1", 310.0, 1500.0, -300.0, 300.0, 26810.0)          # A4 028 Forest Floor
UD_FLOOR = ("2", 1799.0, 2599.0, -17415.0, -16615.0, 30630.0)  # A4 072 Upside Down Floor
LANDING4 = ("4", 27052.0, 27952.0, -17415.0, -16615.0, 32830.0)   # A4 146 Landing (the tower's)
CORRIDOR_END = ("4", 33052.0, 33452.0, -17365.0, -16665.0, 36930.0)  # the Iwato corridor's east end (A4 220)
GATE = (49712.0, -17015.0, 42730.0)                            # the gate's middle, on its island's top
# Section 6 is kept whole (the user, 11-23: "この形を崩さずに" - its islands and updrafts as they are). The four
# trial footings lie on its first four islands; each island's onward updraft sleeps until that trial is done.
REMOVE = []
TRIAL_ISLANDS = [(35147.5, -17014.7, 37930.0),    # A4 230 Island (tops, from the level dump)
                 (37379.5, -16414.7, 38930.0),    # A4 232 Island
                 (39811.5, -17014.7, 39930.0),    # A4 234 Island
                 (42443.5, -17014.7, 40930.0)]    # A4 238 Island
TRIAL_WINDS = ["A4 231 Updraft", "A4 233 Updraft", "A4 237 Updraft", "A4 239 Updraft"]
TRIAL_SPACING = 9000.0      # the small areas lie this far apart, south of the footings


def build(base, jump_z, gravity, walk, plat):
    r = Route(base, jump_z, gravity, walk, plat)
    heights = {"start": 22610.0}
    off = {"1": (0.0, 0.0, 0.0)}
    r.section_offsets = off

    def moved(piece, section=None):
        name, x0, x1, y0, y1, top = piece
        dx, dy, dz = off[section or name]
        return ("rect", x0 + dx, x1 + dx, y0 + dy, y1 + dy), top + dz

    def copy_at(piece, x0, y_mid, top, look, label):
        # A copy of piece's footing put with its west edge at x0, its middle at y_mid, its top at top; returns the
        # copy and the offset that puts piece's own section there.
        _, px0, px1, py0, py1, ptop = piece
        w, d = px1 - px0, py1 - py0
        here = r.block(x0, x0 + w, y_mid - d / 2.0, y_mid + d / 2.0, top - 300.0, top, look, label)
        return here, (x0 - px0, y_mid - (py0 + py1) / 2.0, top - ptop)

    r.add("spot", "start", -3000.0, 0.0, 22610.0)

    # =====================================================================================================
    # 1 Sun Court (the forest floor -> a copy of it, before the jewel forest)
    # =====================================================================================================
    r.add("section", "1 Sun Court")
    previous, top = moved(FOREST)
    LY = middle(previous)[1]
    x, y = r.at(previous, E, 0.6, 0.0, 500.0)
    court = r.block(x - 500.0, x + 500.0, LY - 500.0, LY + 500.0, top - 300.0, top, "marble", "Sun Court")
    r.jump("forest floor -> sun court", previous, court, 0.0, HARD)
    r.add("spot", "sun court", x, LY, top)
    SX0, ST = x, top
    previous = court
    for i in range(10):
        top += 100.0
        x, y = r.at(previous, E if i % 2 == 0 else (N if i % 4 == 1 else S), 0.65, 100.0, 250.0)
        here = r.block(x - 250.0, x + 250.0, y - 250.0, y + 250.0, top - 200.0, top, "marble", "Court Step")
        r.jump("court step {}".format(i + 1), previous, here, 100.0, HARD)
        previous = here
        if i == 5:
            cx, cy = r.at(here, N, 0.7, 100.0, 90.0)
            perch = r.block(cx - 90.0, cx + 90.0, cy - 90.0, cy + 90.0, top - 150.0, top + 100.0, "gold", "Coin Perch")
            r.jump("court step 6 -> coin perch", here, perch, 100.0, HARD)
            r.jump("coin perch -> court step 6", perch, here, -100.0, HARD)
            r.add("coin", cx, cy, top + 100.0)
    r.add("sun", (SX0 + middle(previous)[0]) / 2.0, LY, ST, "sun court", (2200.0, 2200.0, 2200.0), 3000.0)
    x0 = previous[2] + 0.6 * r.reach(0.0)
    forest_copy, off["2"] = copy_at(FOREST, x0, middle(previous)[1], top, "gold", "Forest Floor (copy)")
    r.jump("court step -> forest floor copy", previous, forest_copy, 0.0, HARD)
    dx, dy, dz = off["2"]
    r.add("spot", "jewel", 1055.0 + dx, -8276.0 + dy, 27970.0 + dz)
    # (a crosswind over the jewel forest was tried and taken out: not crossable on the timed jewels - the user, 11-23)
    heights["jewel forest"] = top

    # =====================================================================================================
    # 2 Wind Tunnel (the upside-down floor -> a copy of it, before the gravity zones)
    # =====================================================================================================
    r.add("section", "2 Wind Tunnel")
    previous, top = moved(UD_FLOOR)
    LY = middle(previous)[1]
    first_x = previous[2]
    for i in range(12):
        rise = 100.0 if i % 3 == 2 else 0.0
        top += rise
        if i % 3 == 1:
            x, y = r.at(previous, E, 0.55, rise, 0.4 * 400.0)
            here = r.vanish(x, y, top, 400.0, 0.8, 2.0)
        elif i % 4 == 3:
            x, y = r.at(previous, E, 0.45, rise, 110.0)
            here = r.jewel(x, y, top, 110.0, i % 6, 3, 6, 0.8, PENTA[i % 6])
        else:
            x, y = r.at(previous, E, 0.6, rise, 350.0)
            here = r.block(x - 350.0, x + 350.0, y - 110.0, y + 110.0, top - 80.0, top, "marble", "Wind Beam")
        r.jump("wind tunnel {}".format(i + 1), previous, here, rise, HARD if i % 4 != 3 else 0.55)
        previous = here
    r.wind((first_x + previous[2]) / 2.0, LY, top - 100.0, previous[2] - first_x + 400.0, 1400.0, 900.0, 90.0, 0.0, 400.0, 300.0, 1.6, 2.6, 0.0)
    x, y = r.at(previous, E, 0.6, 0.0, 300.0)
    rest = r.block(x - 300.0, x + 300.0, LY - 300.0, LY + 300.0, top - 300.0, top, "marble", "Tunnel End")
    r.jump("wind tunnel -> tunnel end", previous, rest, 0.0, HARD)
    r.add("flag", x, LY, top)
    r.add("spot", "tunnel", x, LY, top)
    x0 = rest[2] + 0.6 * r.reach(0.0)
    floor_copy, off["3"] = copy_at(UD_FLOOR, x0, LY, top, "marble", "Upside Down Floor (copy)")
    r.jump("tunnel end -> upside down floor copy", rest, floor_copy, 0.0, HARD)
    dx, dy, dz = off["3"]
    r.add("flame", 7383.0 + dx, -16015.0 + dy, 31180.0 + dz, 0.0, 0.0, 0.8, 1.2, 2.2, "flip copy")
    r.add("spot", "flip copy", 7383.0 + dx, -17015.0 + dy, 31180.0 + dz)
    heights["upside down"] = top

    # =====================================================================================================
    # 3 Light Maze (a copy of the tower's landing, out of the last zone -> the tower's own landing)
    # =====================================================================================================
    r.add("section", "3 Light Maze")
    _, lx0, lx1, ly0, ly1, ltop = LANDING4
    landing_copy = r.block(lx0 + dx, lx1 + dx, ly0 + dy, ly1 + dy, ltop + dz - 200.0, ltop + dz, "marble", "Landing (copy)")
    top = ltop + dz
    LY = (ly0 + ly1) / 2.0 + dy
    r.add("spot", "maze", (lx0 + lx1) / 2.0 + dx, LY, top)
    previous = landing_copy
    for i in range(10):
        x, y = previous[2] + 380.0 + 300.0 * i if i == 0 else middle(previous)[0] + 300.0, LY + (-250.0 if i % 2 == 0 else 250.0)
        if i == 0:
            x = landing_copy[2] + 250.0 + 130.0
        top += 100.0
        beam = "maze{}".format(i + 1)
        r.beam(beam, x, y, top - 300.0, top + 700.0, 400.0, 3.0, 2.4, 0.9 * i)
        here = r.lplat(beam, x, y, top, 260.0)
        r.jump("lit stone {}".format(i + 1), previous, here, 100.0, 0.8)
        previous = here
        if i == 6:
            rx, ry = x, y - 130.0 - 0.55 * r.reach(0.0) - 110.0
            r.beam("rare", rx, ry, top - 300.0, top + 700.0, 300.0, 1.6, 5.0, 0.0)
            rare = r.lplat("rare", rx, ry, top, 220.0)
            r.jump("lit stone 7 -> rare light", here, rare, 0.0, 0.7)
            r.add("coin", rx, ry, top)
    cx, cy = middle(previous)
    row_y = cy
    r.beam("sweep", cx + 600.0, row_y, top - 300.0, top + 1200.0, 450.0, 0.0, 0.0, 0.0, (1200.0, 0.0, 0.0), 4.0)
    prev = previous
    for i in range(4):
        here = r.lplat("sweep", cx + 600.0 + 400.0 * i, row_y, top, 260.0)
        r.jump("swept stone {}".format(i + 1), prev, here, 0.0, 0.8)
        prev = here
    x, y = r.at(prev, E, 0.6, 0.0, 300.0)
    maze_end = r.block(x - 300.0, x + 300.0, row_y - 300.0, row_y + 300.0, top - 300.0, top, "marble", "Maze End")
    r.jump("swept stone -> maze end", prev, maze_end, 0.0, HARD)
    landing4, l4top = None, top
    _, px0, px1, py0, py1, ptop = LANDING4
    g = 0.6 * r.reach(0.0)
    off["4"] = (maze_end[2] + g - px0, middle(maze_end)[1] - (py0 + py1) / 2.0, top - ptop)
    off["5"] = off["4"]
    landing4, l4top = moved(LANDING4)
    r.jump("maze end -> the tower's landing", maze_end, landing4, 0.0, HARD)
    dx, dy, dz = off["4"]
    r.add("spot", "tower floor", 28400.0 + dx, -17015.0 + dy, 32830.0 + dz)
    r.add("flame", 29200.0 + dx, -16015.0 + dy, 32830.0 + dz, 0.0, 0.0, 0.8, 1.2, 2.2, "tower floor")
    r.add("flame", 30400.0 + dx, -18015.0 + dy, 32830.0 + dz, 0.0, 1.0, 0.8, 1.2, 2.2, "tower floor")
    heights["dark tower"] = l4top

    # =====================================================================================================
    # 4 Falling Sky (the corridor's end, wings on -> a copy of it, before the gate's updrafts)
    # =====================================================================================================
    r.add("section", "4 Falling Sky")
    previous, top = moved(CORRIDOR_END)
    LY = middle(previous)[1]
    x = previous[2]
    for i, (distance, side) in enumerate(((1100.0, 0.0), (1300.0, 600.0), (1300.0, -600.0))):
        LY_i = LY + side
        x += distance
        column = rect(x + 150.0, LY_i, 300.0)
        bottom, column_top = top - 500.0, top + 900.0
        r.wind(x + 150.0, LY_i, (bottom + column_top) / 2.0, column_top - bottom, 300.0, 300.0, 0.0, 90.0, 2200.0, 900.0,
               0.0 if i == 0 else 2.6, 0.0 if i == 0 else 1.6)
        r.glide("falling sky hop {}".format(i + 1), previous, top, column, bottom + 100.0)
        island_top = column_top - 100.0
        isle_x = x + 300.0 + 60.0 + 300.0
        here = r.block(isle_x - 300.0, isle_x + 300.0, LY_i - 300.0, LY_i + 300.0, island_top - 300.0, island_top, "stone", "Falling Rubble")
        r.lift("falling sky updraft {} -> rubble".format(i + 1), column, column_top, here, island_top)
        previous, top = here, island_top
        x = isle_x + 300.0
    r.add("flag", middle(previous)[0], middle(previous)[1], top)
    r.add("spot", "falling sky", middle(previous)[0], middle(previous)[1], top)
    for i in range(5):
        sx, sy = r.at(previous, E, 0.65, 0.0, 150.0)
        here = r.falling(sx, sy, top)
        r.jump("crumbling sky {}".format(i + 1), previous, here, 0.0, HARD)
        previous = here
    _, px0, px1, py0, py1, ptop = CORRIDOR_END
    x0 = previous[2] + 0.6 * r.reach(0.0)
    corridor_copy = r.block(x0, x0 + (px1 - px0), middle(previous)[1] - (py1 - py0) / 2.0, middle(previous)[1] + (py1 - py0) / 2.0,
                            top - 300.0, top, "marble", "Corridor End (copy)")
    r.jump("crumbling sky -> corridor end copy", previous, corridor_copy, 0.0, HARD)
    heights["the trials"] = top

    # =====================================================================================================
    # 6 The Trials (the user, 2026-11-23): four gold footings (BP_TrialPortal), each but the first hidden until the
    # one before is done. On a footing a pillar of light carries the player to a small area (ruins, tower, sky,
    # heaven); its light shard carries them back, and the next footing appears. After the fourth, the crumbling stair.
    # =====================================================================================================
    r.add("section", "6 Trials")
    _, px0, px1, py0, py1, ptop = CORRIDOR_END
    off["6"] = (corridor_copy[1] - px0, middle(corridor_copy)[1] - (py0 + py1) / 2.0, top - ptop)
    dx, dy, dz = off["6"]
    footings = []
    for k, (ix, iy, itop) in enumerate(TRIAL_ISLANDS):
        r.add("portal", k + 1, ix + dx, iy + dy, itop + dz)
        footings.append((ix + dx, iy + dy, itop + dz))
    gtop = GATE[2] + dz
    heights["the gate (goal)"] = gtop

    # ----- the small areas, each south of its footing; a flag where the player lands, the shard at the far end -----
    def trial_start(k, x, y, t, look, label):
        r.add("section", "6 Trial {} {}".format(k, label))
        start = r.block(x - 400.0, x + 400.0, y - 400.0, y + 400.0, t - 400.0, t, look, "Trial Start")
        r.add("spot", "trial{}".format(k), x, y, t)
        r.add("flag", x, y, t)
        return start

    def trial_end(k, p, t, look):
        x, y = r.at(p, E, 0.6, 0.0, 400.0)
        end = r.block(x - 400.0, x + 400.0, y - 400.0, y + 400.0, t - 400.0, t, look, "Trial End")
        r.jump("trial {} -> its end".format(k), p, end, 0.0, HARD)
        r.add("shard", "trial{}".format(k), x, y, t)
        return t

    def step_block(name, p, t, rise, look, half=150.0):
        x, y = r.at(p, E, 0.6, rise, half)
        here = r.block(x - half, x + half, y - half, y + half, t + rise - 400.0, t + rise, look, "Trial Step")
        r.jump(name, p, here, rise, HARD)
        return here, t + rise, x, y

    def piston(name, p, t, h):
        x, y = r.at(p, E, 0.6, 0.0, 200.0)
        low, high = r.moving(x, y, t, (0.0, 0.0, h), 2.5, 1.5, 400.0)
        r.jump(name, p, low, 0.0, HARD)
        return high, t + h

    def falling_run(name, p, t, count):
        for i in range(count):
            x, y = r.at(p, E, 0.65, 0.0, r.plat / 2.0)
            here = r.falling(x, y, t)
            r.jump("{} {}".format(name, i + 1), p, here, 0.0, HARD)
            p = here
        return p

    def trial_ruins(k, x, y, t):
        # Area 1: broken steps, two pistons, a wave of fading steps, crumbling floors.
        p = trial_start(k, x, y, t, "paving", "Ruins")
        for i in range(3):
            p, t, _, _ = step_block("ruins step {}".format(i + 1), p, t, 100.0, "ruin")
        p, t = piston("ruins piston 1", p, t, 400.0)
        p, t, cx, cy = step_block("ruins piston 1 -> ledge", p, t, 0.0, "plaster", 200.0)
        r.add("coin", cx, cy, t)
        p, t = piston("ruins piston 2", p, t, 400.0)
        p, t, _, _ = step_block("ruins piston 2 -> ledge", p, t, 0.0, "tile", 200.0)
        for i in range(4):
            sx, sy = r.at(p, E, 0.6, 0.0, r.plat / 2.0)
            here = r.timed(sx, sy, t, 0.5 * i)
            r.jump("ruins fading step {}".format(i + 1), p, here, 0.0, HARD)
            p = here
        p = falling_run("ruins crumbling floor", p, t, 3)
        trial_end(k, p, t, "paving")

    def trial_tower(k, x, y, t):
        # Area 2: spinning gears, a sliding platform, a piston, crumbling floors.
        p = trial_start(k, x, y, t, "iron", "Tower")
        for i in range(3):
            t += 100.0
            gx_, gy_ = r.at(p, E, 0.55, 100.0, 250.0)
            r.add("gear", gx_, gy_, t, 250.0, 45.0 if i % 2 == 0 else -45.0)
            here = circle(gx_, gy_, 250.0)
            r.jump("tower gear {}".format(i + 1), p, here, 100.0, 0.8)
            p = here
        p, t, _, _ = step_block("tower gear -> ledge", p, t, 0.0, "bronze", 200.0)
        sx, sy = r.at(p, E, 0.6, 0.0, r.plat / 2.0)
        low, high = r.moving(sx, sy, t, (900.0, 0.0, 0.0), 3.0, 1.5)
        r.jump("tower -> sliding platform", p, low, 0.0, HARD)
        p, t, _, _ = step_block("sliding platform -> ledge", high, t, 0.0, "iron", 200.0)
        p, t = piston("tower piston", p, t, 400.0)
        p, t, cx, cy = step_block("tower piston -> ledge", p, t, 0.0, "bronze", 200.0)
        r.add("coin", cx, cy, t)
        p = falling_run("tower crumbling floor", p, t, 2)
        trial_end(k, p, t, "iron")

    def trial_sky(k, x, y, t):
        # Area 3: clouds, vanishing clouds, a moving island, an updraft.
        r.add("section", "6 Trial {} Sky".format(k))
        p = r.cloud(x, y, t, 1000.0)
        r.add("spot", "trial{}".format(k), x, y, t)
        r.add("flag", x, y, t)
        for i in range(2):
            t += 100.0
            cx, cy = r.at(p, E, 0.6, 100.0, 180.0)
            here = r.cloud(cx, cy, t, 450.0)
            r.jump("sky cloud {}".format(i + 1), p, here, 100.0, HARD)
            p = here
        for i in range(3):
            cx, cy = r.at(p, E, 0.55, 0.0, 160.0)
            here = r.vanish(cx, cy, t, 400.0, 0.8, 2.0)
            r.jump("sky vanishing cloud {}".format(i + 1), p, here, 0.0, HARD)
            p = here
        mx, my = r.at(p, E, 0.55, 0.0, 168.0)
        a, b = r.mover(mx, my, t, (800.0, 0.0, 0.0), 3.0, 1.5)
        r.jump("sky -> moving island", p, a, 0.0, HARD)
        cx, cy = r.at(b, E, 0.55, 0.0, 180.0)
        p = r.cloud(cx, cy, t, 450.0)
        r.jump("moving island -> cloud", b, p, 0.0, HARD)
        ux, uy = r.at(p, E, 0.5, 0.0, 150.0)
        column = rect(ux, uy, 300.0)
        bottom, column_top = t - 400.0, t + 900.0
        r.wind(ux, uy, (bottom + column_top) / 2.0, column_top - bottom, 300.0, 300.0, 0.0, 90.0, 2200.0, 900.0)
        r.jump("sky cloud -> updraft", p, column, 0.0, HARD)
        t = column_top - 100.0
        p = r.cloud(ux + 150.0 + 60.0 + 240.0, uy, t, 600.0)
        r.lift("sky updraft -> cloud", column, column_top, p, t)
        r.add("coin", ux + 150.0 + 60.0 + 240.0, uy, t)
        for i in range(2):
            cx, cy = r.at(p, E, 0.55, 0.0, 160.0)
            here = r.vanish(cx, cy, t, 400.0, 0.8, 2.0)
            r.jump("sky last vanishing cloud {}".format(i + 1), p, here, 0.0, HARD)
            p = here
        trial_end(k, p, t, "marble")

    def trial_heaven(k, x, y, t):
        # Area 4: a melody of chime jewels, a wave of light platforms, crumbling floors.
        p = trial_start(k, x, y, t, "marble", "Heaven")
        for i in range(5):
            jx, jy = r.at(p, E, 0.5, 0.0, 110.0)
            here = r.jewel(jx, jy, t, 110.0, i, 3, 6, 0.8, PENTA[i])
            r.jump("heaven jewel {}".format(i + 1), p, here, 0.0, 0.55)
            p = here
        p, t, _, _ = step_block("heaven jewel -> ledge", p, t, 0.0, "marble", 200.0)
        for i in range(4):
            t += 100.0
            lx_, ly_ = r.at(p, E, 0.55, 100.0, 130.0)
            name = "trial{} light {}".format(k, i + 1)
            r.beam(name, lx_, ly_, t - 300.0, t + 700.0, 400.0, 3.0, 2.4, 0.9 * i)
            here = r.lplat(name, lx_, ly_, t, 260.0)
            r.jump("heaven lit stone {}".format(i + 1), p, here, 100.0, 0.8)
            p = here
        p, t, cx, cy = step_block("heaven lit stone -> ledge", p, t, 0.0, "gold", 200.0)
        r.add("coin", cx, cy, t)
        p = falling_run("heaven crumbling floor", p, t, 2)
        trial_end(k, p, t, "gold")

    for k, (fx, fy, ftop) in enumerate(footings):
        (trial_ruins, trial_tower, trial_sky, trial_heaven)[k](k + 1, fx - 600.0, fy - TRIAL_SPACING * (k + 1), ftop)

    xs = [p[1] for p in r.pieces if p[0] == "block"] + [p[2] for p in r.pieces if p[0] == "block"] + [-3500.0, GATE[0] + dx + 1000.0]
    ys = [p[3] for p in r.pieces if p[0] == "block"] + [p[4] for p in r.pieces if p[0] == "block"] + [-20000.0, 1000.0]
    X0, X1, Y0, Y1 = min(xs) - 4000.0, max(xs) + 4000.0, min(ys) - 4000.0, max(ys) + 4000.0
    r.add("catcher", X0, X1, Y0, Y1, 19000.0)
    r.bounds = (X0, X1, Y0, Y1)
    r.summit_top = gtop
    r.heights = heights
    return r


if __name__ == "__main__":
    route = build(22610.0, 500.9, 980.0, 600.0, 300.0)
    for name, g, rise, limit in route.checks:
        if "->" in name or "crumbling" in name:
            print("  {:<46} gap {:>5.0f} rise {:>6.0f} (limit {:>5.0f})".format(name, g, rise, limit))
    for name, z in route.heights.items():
        print("  {:<24} {:>7.0f}".format(name, z))
    for k, v in sorted(route.section_offsets.items()):
        print("  offset {} = ({:.0f}, {:.0f}, {:.0f})".format(k, *v))
    print("pieces {}, jumps {}".format(len(route.pieces), len(route.checks)))
