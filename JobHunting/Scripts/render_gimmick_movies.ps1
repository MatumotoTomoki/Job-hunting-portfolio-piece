# Renders the gimmick clips made by make_gimmick_movies.py, one game process per clip (Movie Render Queue from the
# command line), into Saved/MovieRenders/Gimmicks/<name>.mp4. Clips already rendered are skipped, so it can be run
# again after a stop. The editor must be closed (each render opens and closes a game window). Run:
#   powershell -File render_gimmick_movies.ps1 [-Only <name part>]
param([string]$Only = '')
$ErrorActionPreference = 'Stop'
$project = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\JobHunting.uproject'))
$out = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\Saved\MovieRenders\Gimmicks'))
$ue = 'C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\Win64\UnrealEditor.exe'
$clips = Get-Content (Join-Path $out 'clips.txt') -Encoding UTF8 | Where-Object { $_.Trim() }
$done = 0; $failed = @()
foreach ($line in $clips) {
  $level, $sequence, $preset, $name = $line.Split('|')
  if ($Only -and $name -notlike "*$Only*") { continue }
  $file = Join-Path $out ($name + '.mp4')
  if (Test-Path $file) { continue }
  if (Get-Process UnrealEditor -ErrorAction SilentlyContinue) { throw 'An Unreal Editor is open: close it first.' }
  $args = @("`"$project`"", $level, '-game', "-LevelSequence=`"$sequence`"", "-MoviePipelineConfig=`"$preset`"",
            '-windowed', '-resx=1280', '-resy=720', '-nosplash', '-unattended', '-log')
  $p = Start-Process $ue -ArgumentList $args -PassThru
  if (-not $p.WaitForExit(600000)) { $p | Stop-Process -Force; $failed += "$name (timed out)"; continue }
  if (Test-Path $file) { $done++; "rendered $name" } else { $failed += $name; "FAILED $name" }
}
"done: $done rendered; failed: $($failed.Count) $($failed -join ', ')"
