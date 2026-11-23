# Hidden area 4's goal (the user, 2026-11-23: "隠し全クリア演出"): Heaven's Gate as at area 4's end - the doors open, the
# light, the walk in, the white - but the end of the hidden stages: ACH_SECRET_CLEAR, then back to the title (no game
# clear screen, no best time, none of area 4's clear achievements).
#   Gimmicks/Heaven/BP_SecretGate   a copy of BP_HeavenGate (same doors, veil, light, trigger, camera, variables).
#   Its graph: Scripts/BP_SecretGate_EventGraph.txt (Generators/gen_heaven_gate.ps1 -Secret). In BP_SecretGate's
#   EventGraph select everything (Ctrl+A), delete it, then paste the text (Ctrl+V), compile and save.
# BP_HeavenGate itself is not changed. build_secret4_stage.py puts BP_SecretGate where area 4's gate stood. Safe to run
# again (an existing BP_SecretGate is kept). From the Output Log (Python), or as a commandlet:
#   exec(open(r'C:\Git\Job-hunting-portfolio-piece\JobHunting\Scripts\setup_secret_gate.py', encoding='utf-8').read())
import os

import unreal

DIR = "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven"
SOURCE = DIR + "/BP_HeavenGate"
PATH = DIR + "/BP_SecretGate"
library = unreal.EditorAssetLibrary
lines = []

if library.does_asset_exist(PATH):
    lines.append(PATH + " already there: kept")
else:
    if not library.does_asset_exist(SOURCE):
        raise RuntimeError("Missing " + SOURCE + " (run setup_heaven_gate.py first)")
    if not library.duplicate_asset(SOURCE, PATH):
        raise RuntimeError("Could not copy {} to {}".format(SOURCE, PATH))
    library.save_asset(PATH, False)
    lines.append("{} copied from {}: paste BP_SecretGate_EventGraph.txt over its EventGraph".format(PATH, SOURCE))

with open(os.path.join(unreal.Paths.project_saved_dir(), "secret_gate.txt"), "w", encoding="utf-8") as out:
    out.write("\n".join(lines) + "\n")
unreal.log("\n".join(lines))
