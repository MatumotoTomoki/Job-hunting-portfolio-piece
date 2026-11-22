# Hidden area 3 (LV_Secret3) as area 3 itself, collapsed (the user, 2026-11-22): area 3's own goal kept (the lever,
# the cloud stair round the column, the light gate - now on to LV_Secret4) and the way there made longer and stranger
# with stretches of gimmicks between the torn-apart sections and new gimmicks over the old ones. build_secret3_stage.py
# copies LV_Area3_Sky and moves each section whole by route.section_offsets (worked out here). Checked jump by jump:
#   blender -b --factory-startup --python secret3_collapse.py
#   A Cloud Harbor   (start: hidden area 2's catapult drops the player here; a crosswind over its vanishing clouds)
#   1 Melody Garden  north: a melody stair of jewels, an island, two rising islands     -> B Crosswind Beams (a flame jet)
#   2 Gear Works     east: gears, pistons by turns, red and blue blocks and a switch    -> C Updraft Gorge (a flame jet)
#   3 Hell Rift      east: flame jets on burnt slabs, then the cages (heaven goes on)   -> D Island Chain (the sun loose)
#   4 Fallen Garden  east: two gravity zones walked on the ceiling                      -> E+F Storm Stair, Cloud Stair
#   Three light shards hidden off the way (west of the garden island, south of the works, north of the first garden
#   landing): the light gate stays shut until all three are taken (BP_ShardLock, setup_shard_lock.py).
#                                                                                          (flame jets on the stair)
# Timed chains always leave time to cross (pistons alternate, see secret-stages notes). Pieces from area 3's dump
# (Saved/level_dump_LV_Area3_Sky.json, 2026-11-22).
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from area3_layout import rect, circle, middle, gap
from area4_layout import Route, ceiling_run, HARD, MID, PENTA, E, N, W, S

GROUPS = {"F": "E"}                                            # the cloud stair (F) rises off E's last island
A_END = ("A", 6426.0, 7026.0, -172.0, 412.0, 15660.0)          # A3 015 Island
B_START = ("B", 6666.0, 6786.0, 658.0, 1308.0, 15760.0)        # A3 016 Marble
B_END = ("B", 6376.0, 7076.0, 5197.0, 5879.0, 16260.0)         # A3 028 Island (flag 1)
C_START = ("C", 7102.0, 7402.0, 5388.0, 5688.0, 16260.0)       # A3 033 Updraft's column, jumped into at B's height
C_END = ("C", 10012.0, 10232.0, 5328.0, 5548.0, 18360.0)       # A3 039 Marble
D_START = ("D", 10372.0, 10708.0, 5270.0, 5606.0, 18360.0)     # A3 043 Moving Island, down
D_END = ("D", 10894.0, 11594.0, 11147.0, 11829.0, 19810.0)     # A3 055 Island (flag 2)
E_START = ("E", 11880.0, 12100.0, 11378.0, 11598.0, 19910.0)   # A3 057 Marble


def build(base, jump_z, gravity, walk, plat):
    r = Route(base, jump_z, gravity, walk, plat)
    heights = {"start": 14960.0}
    off = {"A": (0.0, 0.0, 0.0)}
    r.section_offsets = off

    def moved(piece):
        section, x0, x1, y0, y1, top = piece
        dx, dy, dz = off[section]
        return ("rect", x0 + dx, x1 + dx, y0 + dy, y1 + dy), top + dz

    def place(piece, after, after_top, direction=E, rise=0.0, ratio=0.6):
        section, x0, x1, y0, y1, top = piece
        g = ratio * r.reach(rise)
        ax, ay = middle(after)
        if direction == E:
            off[section] = (after[2] + g - x0, ay - (y0 + y1) / 2.0, after_top + rise - top)
        else:
            off[section] = (ax - (x0 + x1) / 2.0, after[4] + g - y0, after_top + rise - top)
        return moved(piece)

    r.add("spot", "start", -300.0, 0.0, 14960.0)
    # A: a crosswind over the vanishing clouds (west, gusting)
    r.add("section", "A Cloud Harbor")
    r.wind(2150.0, 60.0, 15300.0, 2600.0, 1400.0, 900.0, 90.0, 0.0, 500.0, 350.0, 1.8, 2.4, 0.0)

    # =====================================================================================================
    # 1 Melody Garden (north)
    # =====================================================================================================
    r.add("section", "1 Melody Garden")
    previous, top = moved(A_END)
    JR = 110.0
    for i in range(6):
        top += 80.0
        x, y = r.at(previous, N, 0.45, 80.0, JR, side=(90.0 if i % 2 else -90.0))
        here = r.jewel(x, y, top, JR, i, 2, 6, 0.9, PENTA[i])
        r.jump("melody stair {}".format(i + 1), previous, here, 80.0, 0.55)
        previous = here
        if i == 3:
            sx = x + 2.0 * JR + 0.45 * r.reach(0.0)
            side_jewel = r.jewel(sx, y, top, JR, 9, 2, 12, 0.9, 2.0)
            r.jump("melody stair 4 -> coin jewel", here, side_jewel, 0.0, 0.5)
            r.jump("coin jewel -> melody stair 4", side_jewel, here, 0.0, 0.5)
            r.add("coin", sx, y, top)
    top += 80.0
    x, y = r.at(previous, N, 0.7, 80.0, 0.48 * 800.0)
    rest = r.island(x, y, top, 800.0)
    r.jump("melody stair -> garden island", previous, rest, 80.0, MID)
    r.add("spot", "garden", x, y, top)
    # Light shard 1 (the gate needs all three, 2026-11-23): west off the garden island over three vanishing clouds.
    previous_s = rest
    for i in range(3):
        sx, sy = r.at(previous_s, W, 0.55, 0.0, 0.4 * 400.0)
        here = r.vanish(sx, sy, top, 400.0, 0.7, 2.2)
        r.jump("to shard 1: cloud {}".format(i + 1), previous_s, here, 0.0, HARD)
        r.jump("back: cloud {}".format(i + 1), here, previous_s, 0.0, HARD)
        previous_s = here
    sx, sy = r.at(previous_s, W, 0.6, 0.0, 0.48 * 500.0)
    shard_isle = r.island(sx, sy, top, 500.0)
    r.jump("cloud -> shard 1 island", previous_s, shard_isle, 0.0, HARD)
    r.jump("shard 1 island -> cloud", shard_isle, previous_s, 0.0, HARD)
    r.add("shard", "shard1", sx, sy, top)
    r.lamp(sx, sy, top + 500.0, (190, 230, 255))
    x, y = r.at(rest, N, 0.6, 0.0, 0.48 * 350.0)
    ride, arrive = r.mover(x, y, top, (0.0, 1100.0, 250.0), 4.0, 1.5)
    r.jump("garden island -> rising island 1", rest, ride, 0.0, MID)
    top += 250.0
    x, y = r.at(arrive, N, 0.6, 0.0, 0.48 * 350.0)
    far, near = r.mover(x, y + 1100.0, top + 250.0, (0.0, -1100.0, -250.0), 4.0, 1.5)
    r.jump("rising island 1 -> 2 (they meet)", arrive, near, 0.0, MID)
    top += 250.0
    previous = far
    for i in range(4):
        x, y = r.at(previous, N, 0.55, 0.0, 0.4 * 450.0, side=(150.0 if i % 2 else -150.0))
        here = r.vanish(x, y, top, 450.0, 0.7, 2.2)
        r.jump("garden cloud {}".format(i + 1), previous, here, 0.0, HARD)
        previous = here
    top += 100.0
    x, y = r.at(previous, N, 0.6, 100.0, 300.0)
    landing = r.block(x - 300.0, x + 300.0, y - 300.0, y + 300.0, top - 250.0, top, "marble", "Garden Ledge")
    r.jump("garden cloud -> garden ledge", previous, landing, 100.0, MID)
    beam, bt = place(B_START, landing, top, N)
    r.jump("garden ledge -> the beams", landing, beam, 0.0, HARD)
    dx, dy, dz = off["B"]
    r.add("spot", "beams", (landing[1] + landing[2]) / 2.0, middle(landing)[1], top)
    r.add("flame", 6726.0 + dx, 2783.0 + dy, 15960.0 + dz, 0.0, 0.0, 0.8, 1.2, 2.2, "beams")
    heights["beams"] = bt

    # =====================================================================================================
    # 2 Gear Works (east)
    # =====================================================================================================
    r.add("section", "2 Gear Works")
    previous, top = moved(B_END)
    LY = middle(previous)[1]
    x, y = r.at(previous, E, 0.6, 0.0, 250.0)
    gate = r.block(x - 250.0, x + 250.0, LY - 250.0, LY + 250.0, top - 300.0, top, "darkstone", "Works Gate")
    r.jump("flag island -> works gate", previous, gate, 0.0, HARD)
    r.add("switch", x, LY + 150.0, top)       # puts the blocks back to red after a fall
    previous = gate
    piston_count = 0
    plan = ("gear", "piston", "gear", "red", "red", "switch", "blue", "blue", "gear", "piston", "gear", "piston", "gear")
    for i, kind in enumerate(plan):
        if kind == "gear":
            x, y = r.at(previous, E, 0.6, 0.0, 0.92 * 220.0)
            r.add("gear", x, y, top, 220.0, 40.0 if i % 2 else -40.0)
            here = circle(x, y, 0.92 * 220.0)
            r.jump("works {} gear".format(i + 1), previous, here, 0.0, HARD)
        elif kind == "piston":
            x, y = r.at(previous, E, 0.6, 0.0, 200.0)
            if piston_count % 2:
                here_up, here = r.moving(x, y, top + 450.0, (0.0, 0.0, -450.0), 2.5, 1.5, 400.0)
            else:
                here, here_up = r.moving(x, y, top, (0.0, 0.0, 450.0), 2.5, 1.5, 400.0)
            piston_count += 1
            r.jump("works {} piston".format(i + 1), previous, here, 0.0, MID)
            top += 450.0
            here = here_up
        elif kind in ("red", "blue"):
            top += 100.0
            x, y = r.at(previous, E, 0.65, 100.0, 120.0)
            r.add("sblock", x, y, top, 240.0, kind == "red")
            here = rect(x, y, 240.0)
            r.jump("works {} {}".format(i + 1, kind), previous, here, 100.0, HARD)
        else:
            x, y = r.at(previous, E, 0.65, 0.0, 120.0)
            here = r.block(x - 120.0, x + 120.0, y - 120.0, y + 120.0, top - 400.0, top, "darkstone", "Switch Pedestal")
            r.add("switch", x, y, top)
            r.jump("works {} switch pedestal".format(i + 1), previous, here, 0.0, HARD)
            cx, cy = x, y + 120.0 + 0.6 * r.reach(0.0) + 90.0
            perch = r.block(cx - 90.0, cx + 90.0, cy - 90.0, cy + 90.0, top - 150.0, top, "bronze", "Coin Perch")
            r.jump("switch pedestal -> coin perch", here, perch, 0.0, HARD)
            r.jump("coin perch -> switch pedestal", perch, here, 0.0, HARD)
            r.add("coin", cx, cy, top)
        previous = here
    x, y = r.at(previous, E, 0.6, 0.0, 300.0)
    works_end = r.block(x - 300.0, x + 300.0, y - 300.0, y + 300.0, top - 300.0, top, "darkstone", "Works End")
    r.jump("works -> works end", previous, works_end, 0.0, HARD)
    # Light shard 2: south off the works' end over two turning gears.
    previous_s = works_end
    for i in range(2):
        sx, sy = r.at(previous_s, S, 0.6, 0.0, 0.92 * 200.0)
        r.add("gear", sx, sy, top, 200.0, 45.0 if i % 2 == 0 else -45.0)
        here = circle(sx, sy, 0.92 * 200.0)
        r.jump("to shard 2: gear {}".format(i + 1), previous_s, here, 0.0, HARD)
        r.jump("back: gear {}".format(i + 1), here, previous_s, 0.0, HARD)
        previous_s = here
    sx, sy = r.at(previous_s, S, 0.6, 0.0, 200.0)
    pedestal = r.block(sx - 200.0, sx + 200.0, sy - 200.0, sy + 200.0, top - 300.0, top, "gold", "Shard Pedestal")
    r.jump("gear -> shard 2 pedestal", previous_s, pedestal, 0.0, HARD)
    r.jump("shard 2 pedestal -> gear", pedestal, previous_s, 0.0, HARD)
    r.add("shard", "shard2", sx, sy, top)
    r.lamp(sx, sy, top + 500.0, (190, 230, 255))
    column, ct = place(C_START, works_end, top)
    r.jump("works end -> the updraft", works_end, column, 0.0, HARD)
    dx, dy, dz = off["C"]
    r.add("spot", "gorge", middle(works_end)[0], middle(works_end)[1], top)
    r.add("flame", 7744.0 + dx, 5538.0 + dy, 17110.0 + dz, 0.0, 0.5, 0.8, 1.2, 2.2, "gorge")
    heights["gorge"] = ct

    # =====================================================================================================
    # 3 Hell Rift (east)
    # =====================================================================================================
    r.add("section", "3 Hell Rift")
    marble, top = moved(C_END)
    x, y = r.at(marble, E, 0.6, 0.0, 400.0)
    edge = r.block(x - 400.0, x + 400.0, y - 400.0, y + 400.0, top - 300.0, top, "darkstone", "Rift Edge")
    r.jump("marble -> rift edge", marble, edge, 0.0, HARD)
    HY = y
    r.add("spot", "rift", x, y, top)
    r.add("sign", x, y + 300.0, top + 380.0, 180.0, "Hell burns below")
    previous = edge
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
    WALL = 900.0
    r.block(x + 700.0, x + 800.0, HY - 600.0, HY + 600.0, top, top + WALL, "darkstone", "Rift Wall")
    r.block(x - 700.0, x + 700.0, HY + 500.0, HY + 600.0, top, top + WALL, "darkstone", "Rift Wall")
    r.block(x - 700.0, x + 700.0, HY - 600.0, HY - 500.0, top, top + WALL, "darkstone", "Rift Wall")
    far_x = x + 700.0 + 2000.0
    FAR = top + 600.0
    far = r.block(far_x, far_x + 1200.0, HY - 600.0, HY + 600.0, FAR - 400.0, FAR, "marble", "Far Ledge")
    if gap(choice, far) < 1.2 * r.reach(FAR - top):
        raise RuntimeError("The far ledge can be jumped to from the cage platform")
    r.add("cages", x + 200.0, HY, top, (far_x + 300.0, HY, FAR + 100.0), 8)
    r.add("flag", far_x + 300.0, HY - 300.0, FAR)
    r.add("spot", "far ledge", far_x + 300.0, HY - 300.0, FAR)
    chain, dt = place(D_START, far, FAR)
    r.jump("far ledge -> the moving island", far, chain, 0.0, MID)
    dx, dy, dz = off["D"]
    r.add("spot", "chain", 11244.0 + dx, 5438.0 + dy, 19210.0 + dz)
    r.add("sun", 11244.0 + dx, 8200.0 + dy, 19400.0 + dz, "chain", (2000.0, 2000.0, 2000.0), 2800.0)
    heights["island chain"] = dt

    # =====================================================================================================
    # 4 Fallen Garden (east, upside down)
    # =====================================================================================================
    r.add("section", "4 Fallen Garden")
    island, top = moved(D_END)
    LY = middle(island)[1]
    start = r.block(island[2], island[2] + 900.0, LY - 450.0, LY + 450.0, top - 300.0, top, "marble", "Garden Fragment")
    r.walk_on("flag island -> garden fragment", island, start)
    r.add("sign", island[2] + 300.0, LY + 500.0, top + 380.0, 180.0, "The garden hangs upside down")
    RISE = 900.0
    x_start = start[2]
    zones = (
        (("gap", -100.0, 400.0, 0.85), ("fade", -100.0, 0.0, 0.8), ("gear", 0.0, 240.0, 40.0, 0.75), ("gap", 0.0, 500.0, 0.85)),
        (("gap", -100.0, 300.0, 0.88), ("gear", -100.0, 220.0, -50.0, 0.75), ("fade", 0.0, 0.6, 0.85),
         ("gap", 100.0, 300.0, 0.88), ("gap", 0.0, 600.0, 0.85)),
    )
    ltop = top
    for z, items in enumerate(zones):
        cu = ltop + RISE
        last, last_u, end = ceiling_run(r, LY, x_start - 300.0, cu, items, "garden ceiling {}".format(z + 1))
        if z == 1:
            coin_x = end - 300.0
            cy0 = LY + 250.0 + 0.8 * r.reach(80.0)
            coin_ceiling = r.under(coin_x - 100.0, coin_x + 100.0, cy0, cy0 + 200.0, last_u + 80.0, look="gold", name="Coin Ceiling")
            r.flipped("garden ceiling 2 -> coin ceiling", last, last_u, coin_ceiling, last_u + 80.0, HARD)
            r.flipped("coin ceiling -> garden ceiling 2", coin_ceiling, last_u + 80.0, last, last_u, HARD)
            r.add("coin", coin_x, cy0 + 100.0, last_u + 80.0 - 330.0)
        z_end = end + 200.0
        r.under(end, z_end + 400.0, LY - 250.0, LY + 250.0, last_u, look="stone", name="Ceiling")
        r.gzone(x_start + 60.0, z_end, LY - 600.0, LY + (1100.0 if z == 1 else 600.0), ltop - 400.0, cu + 900.0)
        r.add("catcher", x_start + 60.0, z_end, LY - 600.0, LY + (1100.0 if z == 1 else 600.0), cu + 450.0)
        ltop = min(cu, last_u) - 350.0
        landing = r.block(z_end + 60.0, z_end + 960.0, LY - 600.0, LY + 600.0, ltop - 200.0, ltop, "marble", "Landing")
        if z == 0:
            r.add("flag", z_end + 500.0, LY, ltop)
            r.add("spot", "garden ceiling", z_end + 500.0, LY, ltop)
            # Light shard 3: north off this landing, up four marble steps to a high perch.
            previous_s, stop = landing, ltop
            for i in range(4):
                stop += 100.0
                sx, sy = r.at(previous_s, N, 0.6, 100.0, 150.0, side=(120.0 if i % 2 else -120.0))
                here = r.block(sx - 150.0, sx + 150.0, sy - 150.0, sy + 150.0, stop - 1200.0, stop, "marble", "Shard Step")
                r.jump("to shard 3: step {}".format(i + 1), previous_s, here, 100.0, HARD)
                r.jump("back: step {}".format(i + 1), here, previous_s, -100.0, HARD)
                previous_s = here
            stop += 100.0
            sx, sy = r.at(previous_s, N, 0.6, 100.0, 200.0)
            perch = r.block(sx - 200.0, sx + 200.0, sy - 200.0, sy + 200.0, stop - 300.0, stop, "gold", "Shard Perch")
            r.jump("step -> shard 3 perch", previous_s, perch, 100.0, HARD)
            r.add("shard", "shard3", sx, sy, stop)
            r.lamp(sx, sy, stop + 500.0, (190, 230, 255))
        x_start = z_end + 960.0
    stair, st = place(E_START, landing, ltop)
    r.jump("landing -> the storm stair", landing, stair, 0.0, HARD)
    off["F"] = off["E"]
    dx, dy, dz = off["E"]
    r.add("spot", "stair", 11990.0 + dx, 11488.0 + dy, 19910.0 + dz)
    r.add("flame", 13030.0 + dx, 11488.0 + dy, 20110.0 + dz, 0.0, 0.0, 0.8, 1.2, 2.2, "stair")
    r.add("flame", 14590.0 + dx, 11488.0 + dy, 20410.0 + dz, 0.0, 1.1, 0.8, 1.2, 2.2, "stair")
    heights["storm stair"] = st
    heights["light gate (goal)"] = 22610.0 + dz

    xs = [p[1] for p in r.pieces if p[0] == "block"] + [p[2] for p in r.pieces if p[0] == "block"] + [-700.0, 20538.0 + dx]
    ys = [p[3] for p in r.pieces if p[0] == "block"] + [p[4] for p in r.pieces if p[0] == "block"] + [-700.0, 13436.0 + dy]
    X0, X1, Y0, Y1 = min(xs) - 3000.0, max(xs) + 3000.0, min(ys) - 3000.0, max(ys) + 3000.0
    r.add("catcher", X0, X1, Y0, Y1, 12500.0)
    r.bounds = (X0, X1, Y0, Y1)
    r.summit_top = 22610.0 + dz
    r.heights = heights
    return r


if __name__ == "__main__":
    route = build(14960.0, 500.9, 980.0, 600.0, 300.0)
    for name, g, rise, limit in route.checks:
        if "->" in name:
            print("  {:<46} gap {:>5.0f} rise {:>6.0f} (limit {:>5.0f})".format(name, g, rise, limit))
    for name, z in route.heights.items():
        print("  {:<18} {:>7.0f}".format(name, z))
    for k, v in sorted(route.section_offsets.items()):
        print("  offset {} = ({:.0f}, {:.0f}, {:.0f})".format(k, *v))
    print("pieces {}, jumps {}".format(len(route.pieces), len(route.checks)))
