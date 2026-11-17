param([string]$OutDir)
# Generates Ctrl+V-pasteable node text: play Menu_Cue while the pause menu is open.
# Hooked to the free exec output of "Set IsPaused" at the end of the IA_Pause section.

# Reuse the node helpers (constants + functions) from the height BGM generator.
$helpers = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_height_bgm.ps1') -Encoding UTF8 |
  Select-Object -Skip 3 -First 124
. ([ScriptBlock]::Create(($helpers -join "`n")))

$MENU_CUE = '/Game/Sound/BGM/Menu_Cue.Menu_Cue'

function New-SetPaused($paused, $x, $y) {
  $n = New-Call $AUDIO 'SetPaused' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $AUDIO
  Add-Pin $n 'bPause' 'in' 'bool' '' $null $paused
  return $n
}

# --- Which way did we just toggle? (IsPaused is already flipped by Set IsPaused) --------
$gi = New-Call $STATICS 'GetGameInstance' $true 0 200
Add-Pin $gi 'ReturnValue' 'out' 'object' '' $GAMEINST
$cast = New-Node '/Script/BlueprintGraph.K2Node_DynamicCast' @("TargetType=`"$GI_CLASS`"") 250 0
Add-Exec $cast
Add-Pin $cast 'CastFailed' 'out' 'exec'
Add-Pin $cast 'Object' 'in' 'object' '' $OBJECT
Add-Pin $cast 'AsBP My Game Instance' 'out' 'object' '' $GI_CLASS
Add-Pin $cast 'bSuccess' 'out' 'bool'
$isPaused = New-VarGet 'IsPaused' $null 'bool' '' $null 550 200
$justPaused = New-Branch 750 0

# --- Pausing: pause the game BGM, then let the menu BGM stand in as BgmAudioComponent ---
# Standing in means the pause menu's volume setting (SetBgmVolume) adjusts the menu BGM live.
$bgm = New-VarGet 'BgmAudioComponent' $GI_CLASS 'object' '' $AUDIO 1000 250
$saveGame = New-VarSet 'SavedGameBgm' $null 'object' $AUDIO 1050 0
$saved = New-VarGet 'SavedGameBgm' $null 'object' '' $AUDIO 1300 250
$savedValid = New-IsValid 1500 250
$hasGameBgm = New-Branch 1700 0
$pauseGame = New-SetPaused 'true' 1950 0
$savedVolume = New-VarGet 'VolumeMultiplier' $AUDIO 'real' 'float' $null 1950 250
$create = New-Call $STATICS 'CreateSound2D' $false 2250 0
Add-Pin $create 'Sound' 'in' 'object' '' $SOUND
Add-Pin $create 'VolumeMultiplier' 'in' 'real' 'float' $null '1.0'
Add-Pin $create 'bPersistAcrossLevelTransition' 'in' 'bool' '' $null 'false'
# Thrown away when the menu closes; a fresh one starts from the top next time.
Add-Pin $create 'bAutoDestroy' 'in' 'bool' '' $null 'true'
Add-Pin $create 'ReturnValue' 'out' 'object' '' $AUDIO
$play = New-Call $AUDIO 'Play' $false 2550 0
Add-Pin $play 'self' 'in' 'object' '' $AUDIO
Add-Pin $play 'StartTime' 'in' 'real' 'float' $null '0.0'
$standIn = New-VarSet 'BgmAudioComponent' $GI_CLASS 'object' $AUDIO 2850 0

# --- Unpausing: hand the volume back, stop the menu BGM, resume the game BGM ----------
$savedValid2 = New-IsValid 1000 650
$hasSaved = New-Branch 1200 450
$menu = New-VarGet 'BgmAudioComponent' $GI_CLASS 'object' '' $AUDIO 1200 700
$menuVolume = New-VarGet 'VolumeMultiplier' $AUDIO 'real' 'float' $null 1450 700
$carryVolume = New-Call $AUDIO 'SetVolumeMultiplier' $false 1700 450
Add-Pin $carryVolume 'self' 'in' 'object' '' $AUDIO
Add-Pin $carryVolume 'NewVolumeMultiplier' 'in' 'real' 'float' $null '1.0'
$stopMenu = New-Call $AUDIO 'Stop' $false 2000 450
Add-Pin $stopMenu 'self' 'in' 'object' '' $AUDIO
$restore = New-VarSet 'BgmAudioComponent' $GI_CLASS 'object' $AUDIO 2300 450
$resumeGame = New-SetPaused 'false' 2600 450

Connect $gi 'ReturnValue' $cast 'Object'
Connect $cast 'then' $justPaused 'execute'
Connect $isPaused 'IsPaused' $justPaused 'Condition'
# Pausing
Connect $justPaused 'then' $saveGame 'execute'
Connect $cast 'AsBP My Game Instance' $bgm 'self'
Connect $bgm 'BgmAudioComponent' $saveGame 'SavedGameBgm'
Connect $saveGame 'then' $hasGameBgm 'execute'
Connect $saved 'SavedGameBgm' $savedValid 'Object'
Connect $savedValid 'ReturnValue' $hasGameBgm 'Condition'
Connect $hasGameBgm 'then' $pauseGame 'execute'
Connect $saved 'SavedGameBgm' $pauseGame 'self'
Connect $pauseGame 'then' $create 'execute'
Connect $saved 'SavedGameBgm' $savedVolume 'self'
Connect $savedVolume 'VolumeMultiplier' $create 'VolumeMultiplier'
Connect $create 'then' $play 'execute'
Connect $create 'ReturnValue' $play 'self'
Connect $play 'then' $standIn 'execute'
Connect $cast 'AsBP My Game Instance' $standIn 'self'
Connect $create 'ReturnValue' $standIn 'BgmAudioComponent'
# Unpausing
Connect $justPaused 'else' $hasSaved 'execute'
Connect $saved 'SavedGameBgm' $savedValid2 'Object'
Connect $savedValid2 'ReturnValue' $hasSaved 'Condition'
Connect $cast 'AsBP My Game Instance' $menu 'self'
Connect $hasSaved 'then' $carryVolume 'execute'
Connect $saved 'SavedGameBgm' $carryVolume 'self'
Connect $menu 'BgmAudioComponent' $menuVolume 'self'
Connect $menuVolume 'VolumeMultiplier' $carryVolume 'NewVolumeMultiplier'
Connect $carryVolume 'then' $stopMenu 'execute'
Connect $menu 'BgmAudioComponent' $stopMenu 'self'
Connect $stopMenu 'then' $restore 'execute'
Connect $cast 'AsBP My Game Instance' $restore 'self'
Connect $saved 'SavedGameBgm' $restore 'BgmAudioComponent'
Connect $restore 'then' $resumeGame 'execute'
Connect $saved 'SavedGameBgm' $resumeGame 'self'

$sb = [System.Text.StringBuilder]::new()
foreach ($n in $script:nodes) {
  [void]$sb.AppendLine("Begin Object Class=$($n.Class) Name=`"$($n.Name)`"")
  foreach ($prop in $n.Props) { [void]$sb.AppendLine("   $prop") }
  [void]$sb.AppendLine("   NodePosX=$($n.X)")
  [void]$sb.AppendLine("   NodePosY=$($n.Y)")
  [void]$sb.AppendLine("   NodeGuid=$([guid]::NewGuid().ToString('N').ToUpper())")
  foreach ($p in $n.Pins) {
    $line = Format-Pin $p
    # Object pins take their asset as DefaultObject, which Format-Pin does not write.
    if ($n -eq $create -and $p.Name -eq 'Sound') { $line = $line -replace 'PersistentGuid=', "DefaultObject=`"$MENU_CUE`",PersistentGuid=" }
    [void]$sb.AppendLine($line)
  }
  [void]$sb.AppendLine('End Object')
}
[IO.File]::WriteAllText((Join-Path $OutDir 'PauseBgm_Controller_AfterSetIsPaused.txt'), $sb.ToString(), [Text.UTF8Encoding]::new($false))
"Generated $($script:nodes.Count) nodes"
