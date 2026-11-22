# Hidden area 2's engine room (area 2's section A), broken open (2026-11-22): the ceiling blown off - so the pillar of
# light can come down on the doomed catapult - and the west, north and south walls broken down to uneven stumps (low:
# 1-4.5 m - taller ones hid the view, the user 2026-11-22);
# two slabs of the ceiling lie on the floor. The east wall (with the door out), the red and blue blocks, the switches
# and the gear arrival stay. Used by build_secret2_stage.py (the collision boxes) and, under Blender, writes the boxes
# for build_tower_blender.py to dress:
#   blender -b --factory-startup --python secret2_engine.py          (writes SourceArt/Models/Tower/secret2_engine_layout.json)
#   blender -b --factory-startup --python build_tower_blender.py -- A --layout secret2_engine_layout.json --prefix SM_SecretTower_
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FLOOR_TOP = 7260.0
REMOVE = ["A2 020 Room Ceiling", "A2 011 Wall", "A2 016 Wall", "A2 017 Wall", "A2 019 Wall",
          "A2 012 Wall", "A2 014 Wall", "A2 015 Wall"]      # (the east wall too, but for the door's sill A2 013)
REMOVE_ART = ["A2 Lamps A"] + ["A2 Gear A{}".format(k) for k in (1, 2, 3, 4, 5, 6, 7, 8)]
DOOMED_AT = (1000.0, 800.0)     # the catapult the light smashes (clear of the blocks, switches and the arrival gear)


def added_boxes():
    # (label, x0, x1, y0, y1, z0, z1): the broken walls and the fallen ceiling slabs.
    boxes = []
    for i, h in enumerate((300.0, 150.0, 250.0, 100.0, 200.0, 350.0)):           # west, y -1500..1500
        boxes.append(("A2 901 Wall", -300.0, 0.0, -1500.0 + 500.0 * i, -1000.0 + 500.0 * i, FLOOR_TOP, FLOOR_TOP + h))
    for i, h in enumerate((300.0, 450.0, 150.0, 350.0, 250.0)):                  # north, x 0..2400
        boxes.append(("A2 902 Wall", 480.0 * i, 480.0 * (i + 1), 1200.0, 1500.0, FLOOR_TOP, FLOOR_TOP + h))
    for i, h in enumerate((350.0, 150.0, 400.0, 200.0)):                         # south, x 0..2000
        boxes.append(("A2 903 Wall", 500.0 * i, 500.0 * (i + 1), -1500.0, -1200.0, FLOOR_TOP, FLOOR_TOP + h))
    boxes.append(("A2 905 Wall", 2400.0, 2700.0, -1500.0, 600.0, FLOOR_TOP, FLOOR_TOP + 740.0))     # east, by the door
    boxes.append(("A2 905 Wall", 2400.0, 2700.0, 1000.0, 1500.0, FLOOR_TOP, FLOOR_TOP + 840.0))
    boxes.append(("A2 904 Fallen Slab", 0.0, 320.0, -1180.0, -900.0, FLOOR_TOP, FLOOR_TOP + 90.0))
    boxes.append(("A2 904 Fallen Slab", 0.0, 260.0, 900.0, 1180.0, FLOOR_TOP, FLOOR_TOP + 70.0))
    return boxes


def rows_for_art(rows):
    # From area 2's own art layout (SourceArt/Models/Tower/area2_layout.json): its section A rows, less the removed
    # ones, plus the new boxes in the same form.
    out = [dict(row) for row in rows if row["folder"].startswith("Area2/A ") and row["label"] not in REMOVE]
    wall = next(row for row in rows if row["label"] == "A2 012 Wall")
    for label, x0, x1, y0, y1, z0, z1 in added_boxes():
        out.append({"label": label, "folder": "Area2/A Engine Room", "class": "StaticMeshActor", "mesh": wall["mesh"],
                    "material": wall["material"], "location": [(x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0],
                    "rotation": [0.0, 0.0, 0.0], "scale": [(x1 - x0) / 100.0, (y1 - y0) / 100.0, (z1 - z0) / 100.0],
                    "min": [x0, y0, z0], "max": [x1, y1, z1], "hidden": False})
    return out


if __name__ == "__main__":
    tower = os.path.join(os.path.dirname(HERE), "SourceArt", "Models", "Tower")
    rows = json.load(open(os.path.join(tower, "area2_layout.json"), encoding="utf-8"))
    out = rows_for_art(rows)
    target = os.path.join(tower, "secret2_engine_layout.json")
    with open(target, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("wrote {} boxes to {}".format(len(out), target))