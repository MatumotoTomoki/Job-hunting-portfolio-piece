# Paste-graph generators

These PowerShell scripts write the Blueprint paste files, `Scripts/BP_*_EventGraph.txt` and the like. You open a file, select all, copy, and paste it into the Blueprint graph with Ctrl+V. Each generator's header names the Blueprint it targets and the setup script that creates that Blueprint's components and variables.

Run one with the Scripts folder as the output:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File gen_gear_exit.ps1 -OutDir ..
```

## Shared helpers

The generators share code. Each one reads part of another file and dot-sources it, so keep them all in this folder.

| File | What it gives | How callers read it |
|---|---|---|
| `gen_height_bgm.ps1` | The node and pin builders: New-Node, New-Call, Add-Pin, Connect, New-VarGet/Set, New-Operator | Lines 4–127 |
| `gen_hell_cage.ps1` | Player, Controller, GameInstance cast, Fade, Delay, SaveStats, OpenLevel, Write-Graph | Lines 11–182 |
| `gen_heaven_light.ps1` | Typed versions of the above, plus Op, MathCall, Visible, Collide | Everything above `# ===== BP_LightBeam` |

Because callers read some of these files by line number, adding or removing a line above those ranges breaks every generator that uses them.

The helpers find each other through `$GenDir`, the folder the running script sits in. `$PSScriptRoot` is empty inside a dot-sourced block, so the scripts use `$GenDir` instead.

## Notes

- `gen_hell_cage.ps1` reads `bp_export/cage.txt` from the output folder.
- `gen_menu_move_se.ps1` currently stops with "Pin Started not found". It did the same before the move, and its output file is already in Scripts.
- Several generators write the same file, such as `BP_Sun_EventGraph.txt` from the sun face, ride and grab steps. Run the latest one last.
