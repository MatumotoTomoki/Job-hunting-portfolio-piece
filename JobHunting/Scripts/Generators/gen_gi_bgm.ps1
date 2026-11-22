param([string]$OutDir)
# BP_MyGameInstance's EventGraph (exported to bp_export\gi_event.txt, 2026-11-22) with one change: Init waits
# 0.2 s and spawned GameBgm_Cue even when an area level had already started its own BGM (BP_AreaBgm) - so GameBgm
# cut in at the start and the controller crossfaded away from it. Now it only spawns when no BGM is playing yet
# (NOT IsValid(BgmAudioComponent)), so it stays the title's BGM. Output: BP_MyGameInstance_EventGraph.txt (whole graph).
if (-not $OutDir) { throw 'OutDir is required' }
$lightGen = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_heaven_light.ps1') -Encoding UTF8
$cut = ($lightGen | Select-String -Pattern '^# ===== BP_LightBeam' | Select-Object -First 1).LineNumber - 1
. ([ScriptBlock]::Create(($lightGen[1..($cut - 1)] -join "`n")))

$export = Get-Content -LiteralPath (Join-Path $OutDir 'bp_export\gi_event.txt') -Raw -Encoding UTF8
$export = [regex]::Replace($export, ' ExportPath="[^"]*"', '')
$DELAY = 'K2Node_CallFunction_2'     # Init's Delay 0.2
$SPAWN = 'K2Node_CallFunction_1'     # SpawnSound2D GameBgm_Cue
$block = [regex]::Match($export, "(?ms)^Begin Object Class=\S+ Name=`"$DELAY`".*?^End Object")
$line = [regex]::Match($block.Value, 'CustomProperties Pin \(PinId=(\w+),PinName="then",[^\r\n]*')
if (-not $line.Success -or $line.Value -notmatch "LinkedTo=\($SPAWN (\w+),\)") { throw 'gi_event.txt changed: Delay.then -> SpawnSound2D not found' }
$spawnExec = $matches[1]
$delayThen = $line.Groups[1].Value

Reset-Graph 900
$bgm = New-VarGet 'BgmAudioComponent' $null 'object' '' "/Script/CoreUObject.Class'/Script/Engine.AudioComponent'" 300 450
$valid = Valid $bgm 'BgmAudioComponent' 500 450
$none = MathCall 'Not_PreBool' @('A') 'bool' '' 'bool' '' 700 450
Connect $valid 'ReturnValue' $none 'A'
$branch = New-Branch 800 250
Connect $none 'ReturnValue' $branch 'Condition'
(Get-Pin $branch 'execute').Links.Add("$DELAY $delayThen")
(Get-Pin $branch 'then').Links.Add("$SPAWN $spawnExec")
$export = $export.Replace($line.Value, $line.Value.Replace("LinkedTo=($SPAWN $spawnExec,)", "LinkedTo=($($branch.Name) $((Get-Pin $branch 'execute').Id),)"))
$export = $export.Replace("LinkedTo=($DELAY $delayThen,)", "LinkedTo=($($branch.Name) $((Get-Pin $branch 'then').Id),)")
Write-Graph 'BP_MyGameInstance_EventGraph.txt' @() ($export.TrimEnd() + "`r`n")
