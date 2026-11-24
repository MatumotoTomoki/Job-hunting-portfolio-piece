# Hidden stage 1's lower town (area 1's section A), broken up (the user, 2026-11-22: "the start should be more
# collapsed"). Pure Python: used by build_secret_stage.py (to move, take out and add the collision boxes in LV_Secret)
# and, run under Blender, it writes the broken town's boxes for build_ruins_blender.py to dress as art:
#   blender -b --factory-startup --python secret_town.py           (writes SourceArt/Models/Ruins/secret_town_layout.json)
#   blender -b --factory-startup --python build_ruins_blender.py -- A --layout secret_town_layout.json --prefix SM_SecretRuins_
# The town (x -4000..1500, y -2000..2000) splits into chunks, each moved whole:
#   S1  the start (x < -2900, south of y 1300)       stays
#   N   the north strip (crates up to the star coin)  stays
#   H   the hall (x -2600..-1300)                     raised 1 m across a 3 m crack from the start
#   E1  the east town (x -1300..100)                  slid down 6 m
#   E2  the far east (x > 100)                        slid down 14 m
# The one-piece ground and the two long base walls are taken out and come back split per chunk; a few stones of the
# walls' tops have fallen (taken out). Jumps: start -> hall's floor across the crack (checked below).
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

CHUNK_OFFSET = {"S1": (0.0, 0.0, 0.0), "N": (0.0, 0.0, 0.0), "H": (0.0, 0.0, 100.0),
                "E1": (0.0, -150.0, -600.0), "E2": (150.0, 200.0, -1400.0)}
HALL_OFFSET = CHUNK_OFFSET["H"]
CRACK_X0, CRACK_X1 = -2900.0, -2600.0
HALL_X1 = -1300.0
EAST_SPLIT = 100.0
NORTH_Y = 1300.0
REMOVE = ["A1 009 Town Ground", "A1 020 Wall", "A1 021 Wall",           # (back below, split)
          "A1 012 Wall", "A1 026 Wall", "A1 031 Wall", "A1 034 Wall"]    # fallen stones
FLOOR_DEPTH = 4000.0


def chunk_of(label, x, y):
    # Which chunk a box of the town belongs to, by its label (the hall's own pieces) or its middle.
    number = label.split(" ")[1] if label.startswith("A1 ") else ""
    if number.isdigit() and 42 <= int(number) <= 66:
        return "H"
    if y > NORTH_Y and x < HALL_X1:
        return "N"
    if x < CRACK_X1 - 50.0:
        return "S1"
    if x < HALL_X1:
        return "H"
    return "E1" if x < EAST_SPLIT else "E2"


def added_boxes():
    # (label, chunk, x0, x1, y0, y1, z0, z1) in area 1's own coordinates (the chunk's offset still to come).
    boxes = []
    ground = (("S1", -4000.0, CRACK_X0, -2000.0, NORTH_Y), ("N", -4000.0, HALL_X1, NORTH_Y, 2000.0),
              ("H", CRACK_X1, HALL_X1, -2000.0, NORTH_Y), ("E1", HALL_X1, EAST_SPLIT, -2000.0, 2000.0),
              ("E2", EAST_SPLIT, 1500.0, -2000.0, 2000.0))
    for i, (chunk, x0, x1, y0, y1) in enumerate(ground):
        boxes.append(("S Town Ground {}".format(i + 1), chunk, x0, x1, y0, y1, -FLOOR_DEPTH, 0.0))
    # The base walls along the north (y 1800..2000, 0..600) and south (y -2000..-1800, 0..700) edges, cut per chunk.
    cuts = ((-3800.0, CRACK_X0, "S1"), (CRACK_X1, HALL_X1, "H"), (HALL_X1, EAST_SPLIT, "E1"), (EAST_SPLIT, 1500.0, "E2"))
    for x0, x1, chunk in cuts:
        boxes.append(("S Town Wall South", chunk, x0, x1, -2000.0, -1800.0, 0.0, 700.0))
        north_chunk = "N" if chunk in ("S1", "H") else chunk
        boxes.append(("S Town Wall North", north_chunk, x0, x1, 1800.0, 2000.0, 0.0, 600.0))
    return boxes


def collapsed_rows(rows):
    # The town's static boxes after the collapse, as build_ruins_blender.py reads them (area 1's dump rows in).
    out = []
    for row in rows:
        if not row["folder"].startswith("Area1/A ") or row["class"] != "StaticMeshActor" or row["label"] in REMOVE:
            continue
        if row["max"][0] - row["min"][0] > 100000.0:
            continue
        x, y = (row["min"][0] + row["max"][0]) / 2.0, (row["min"][1] + row["max"][1]) / 2.0
        dx, dy, dz = CHUNK_OFFSET[chunk_of(row["label"], x, y)]
        out.append({"label": row["label"], "folder": "Area1/A Lower Town", "class": "StaticMeshActor", "hidden": False,
                    "min": [row["min"][0] + dx, row["min"][1] + dy, row["min"][2] + dz],
                    "max": [row["max"][0] + dx, row["max"][1] + dy, row["max"][2] + dz]})
    for label, chunk, x0, x1, y0, y1, z0, z1 in added_boxes():
        dx, dy, dz = CHUNK_OFFSET[chunk]
        out.append({"label": "A1 900 " + label.replace("S Town ", ""), "folder": "Area1/A Lower Town",
                    "class": "StaticMeshActor", "hidden": False,
                    "min": [x0 + dx, y0 + dy, z0 + dz], "max": [x1 + dx, y1 + dy, z1 + dz]})
    return out


def check(route_class):
    # start floor -> the hall's floor across the crack (the hall's door: its west wall is open at y -200..200)
    from area3_layout import rect
    r = route_class(0.0, 500.9, 980.0, 600.0, 300.0)
    s1 = ("rect", -4000.0, CRACK_X0, -2000.0, NORTH_Y)
    hall_floor = ("rect", CRACK_X1, HALL_X1, -2000.0, NORTH_Y)
    r.jump("start floor -> hall floor (crack)", s1, hall_floor, HALL_OFFSET[2], 0.9)
    return r


if __name__ == "__main__":
    from area4_layout import Route
    r = check(Route)
    for name, g, rise, limit in r.checks:
        print("  {:<40} gap {:>5.0f} rise {:>5.0f} (limit {:>5.0f})".format(name, g, rise, limit))
    dump = os.path.join(os.path.dirname(HERE), "Saved", "level_dump_LV_Area1_Ruins.json")
    rows = json.load(open(dump, encoding="utf-8"))
    out = collapsed_rows(rows)
    target = os.path.join(os.path.dirname(HERE), "SourceArt", "Models", "Ruins", "secret_town_layout.json")
    with open(target, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("wrote {} boxes to {}".format(len(out), target))
