param([string]$OutDir, [string]$ControllerExport)
# Generates one Ctrl+V-pasteable replacement for the pause menu up/down and left/right input sections,
# copied from the exported controller graph, with Pose_movement_Cue played when the input actually
# moves the cursor or a volume. The check runs inline at the start of each section, before the
# existing nodes change anything. (A custom event with parameters crashed the editor on paste.)

# Reuse the node helpers (constants + functions) from the height BGM generator.
$helpers = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_height_bgm.ps1') -Encoding UTF8 |
  Select-Object -Skip 3 -First 124
. ([ScriptBlock]::Create(($helpers -join "`n")))
# Export-reuse helpers (Read-Blocks, Get-Section, Set-ExportPin, ...) from the pause menu generator.
$exportHelpers = (Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_pause_menu.ps1') -Encoding UTF8)[174..225]
. ([ScriptBlock]::Create(($exportHelpers -join "`n")))
# Stay clear of the node names already in the exported controller graph.
$script:counter = 900

$MOVE_CUE = '/Game/Sound/SE/Pose_movement_Cue.Pose_movement_Cue'
$PAUSE_WIDGET = "/Script/UMG.WidgetBlueprintGeneratedClass'/Game/UI/pa-zu.pa-zu_C'"
# Last menu row index (BGM / SE / Quit) and the top of both volume scales, as in the input handlers.
$LAST_ROW = '2'
$MAX_VOLUME = '10'

$blocks = Read-Blocks $ControllerExport

# Branch that passes only when Clamp(value + step, 0, max) differs from value.
function New-WouldChange($step, $valueNode, $valuePin, $max, $x, $y) {
  $sum = New-Operator 'Add' 'Add_IntInt' 'int' '' 'int' $x ($y + 250)
  $clamp = New-Call $MATH 'Clamp' $true ($x + 200) ($y + 250)
  Add-Pin $clamp 'Value' 'in' 'int' '' $null '0'
  Add-Pin $clamp 'Min' 'in' 'int' '' $null '0'
  Add-Pin $clamp 'Max' 'in' 'int' '' $null $max
  Add-Pin $clamp 'ReturnValue' 'out' 'int'
  $differs = New-Operator 'NotEqual' 'NotEqual_IntInt' 'int' '' 'bool' ($x + 400) ($y + 250)
  $branch = New-Branch ($x + 600) $y
  Connect $valueNode $valuePin $sum 'A'
  Connect $step 'ReturnValue' $sum 'B'
  Connect $sum 'ReturnValue' $clamp 'Value'
  Connect $clamp 'ReturnValue' $differs 'A'
  Connect $valueNode $valuePin $differs 'B'
  Connect $differs 'ReturnValue' $branch 'Condition'
  return $branch
}

# Started -> (paused? would it move?) -> [play the sound] -> the section's original first node.
function Add-MoveSound($eventName, [bool]$vertical) {
  $event = $blocks[$eventName]
  $startedId = Get-ExportPinId $event 'Started'
  $valueId = Get-ExportPinId $event 'ActionValue'
  if ($event -notmatch "PinName=`"Started`"[^\n]*?LinkedTo=\((\w+) (\w+),\)") { throw "$eventName Started is not linked to one node" }
  $firstName = $Matches[1]; $firstPinId = $Matches[2]
  $ox = [int]([regex]::Match($event, 'NodePosX=(-?\d+)').Groups[1].Value) + 300
  $oy = [int]([regex]::Match($event, 'NodePosY=(-?\d+)').Groups[1].Value) - 1500

  # Menu input actions may fire outside the pause menu too; stay silent then.
  $isPaused = New-VarGet 'IsPaused' $null 'bool' '' $null $ox ($oy + 200)
  $inMenu = New-Branch ($ox + 200) $oy
  $gi = New-Call $STATICS 'GetGameInstance' $true ($ox + 200) ($oy + 300)
  Add-Pin $gi 'ReturnValue' 'out' 'object' '' $GAMEINST
  $cast = New-Node '/Script/BlueprintGraph.K2Node_DynamicCast' @("TargetType=`"$GI_CLASS`"") ($ox + 450) $oy
  Add-Exec $cast
  Add-Pin $cast 'CastFailed' 'out' 'exec'
  Add-Pin $cast 'Object' 'in' 'object' '' $OBJECT
  Add-Pin $cast 'AsBP My Game Instance' 'out' 'object' '' $GI_CLASS
  Add-Pin $cast 'bSuccess' 'out' 'bool'
  $step = New-Call $MATH 'Round' $true ($ox + 450) ($oy + 450)
  Add-Pin $step 'A' 'in' 'real' 'double' $null '0.0'
  Add-Pin $step 'ReturnValue' 'out' 'int'
  $row = New-VarGet 'SelectedIndex' $null 'int' '' $null ($ox + 450) ($oy + 600)
  $seLevel = New-VarGet 'SeVolumeLevel' $GI_CLASS 'int' '' $null ($ox + 700) ($oy + 800)
  Connect $isPaused 'IsPaused' $inMenu 'Condition'
  Connect $inMenu 'then' $cast 'execute'
  Connect $gi 'ReturnValue' $cast 'Object'
  Connect $cast 'AsBP My Game Instance' $seLevel 'self'
  $skips = @((Get-Pin $inMenu 'else'), (Get-Pin $cast 'CastFailed'))

  if ($vertical) {
    # Up/down: does the cursor row move?
    $moves = @(New-WouldChange $step $row 'SelectedIndex' $LAST_ROW ($ox + 700) $oy)
    Connect $cast 'then' $moves[0] 'execute'
    $px = $ox + 1500
  } else {
    # Left/right: does the volume on the selected row move? (The Quit row has no value.)
    $onBgmRow = New-Operator 'EqualEqual' 'EqualEqual_IntInt' 'int' '' 'bool' ($ox + 700) ($oy + 450)
    (Get-Pin $onBgmRow 'B').Default = '0'
    $bgmRow = New-Branch ($ox + 900) $oy
    $widget = New-VarGet 'PauseMenuWidget' $null 'object' '' $PAUSE_WIDGET ($ox + 900) ($oy + 600)
    $bgmLevel = New-VarGet 'VolumeLevel' $PAUSE_WIDGET 'int' '' $null ($ox + 1150) ($oy + 600)
    $bgmMoves = New-WouldChange $step $bgmLevel 'VolumeLevel' $MAX_VOLUME ($ox + 1150) $oy
    $onSeRow = New-Operator 'EqualEqual' 'EqualEqual_IntInt' 'int' '' 'bool' ($ox + 900) ($oy + 1000)
    (Get-Pin $onSeRow 'B').Default = '1'
    $seRow = New-Branch ($ox + 1100) ($oy + 850)
    $seMoves = New-WouldChange $step $seLevel 'SeVolumeLevel' $MAX_VOLUME ($ox + 1350) ($oy + 850)
    Connect $cast 'then' $bgmRow 'execute'
    Connect $row 'SelectedIndex' $onBgmRow 'A'
    Connect $onBgmRow 'ReturnValue' $bgmRow 'Condition'
    Connect $widget 'PauseMenuWidget' $bgmLevel 'self'
    Connect $bgmRow 'then' $bgmMoves 'execute'
    Connect $bgmRow 'else' $seRow 'execute'
    Connect $row 'SelectedIndex' $onSeRow 'A'
    Connect $onSeRow 'ReturnValue' $seRow 'Condition'
    Connect $seRow 'then' $seMoves 'execute'
    $skips += Get-Pin $seRow 'else'
    $moves = @($bgmMoves, $seMoves)
    $px = $ox + 2000
  }

  # Same volume as the pause menu's SE row: SeVolumeLevel (0-10) / 10.
  $toFloat = New-Call $MATH 'Conv_IntToDouble' $true $px ($oy + 300)
  Add-Pin $toFloat 'InInt' 'in' 'int' '' $null '0'
  Add-Pin $toFloat 'ReturnValue' 'out' 'real' 'double'
  $volume = New-Call $MATH 'SafeDivide' $true ($px + 250) ($oy + 300)
  Add-Pin $volume 'A' 'in' 'real' 'double' $null '0.0'
  Add-Pin $volume 'B' 'in' 'real' 'double' $null '10.0'
  Add-Pin $volume 'ReturnValue' 'out' 'real' 'double'
  $play = New-Call $STATICS 'PlaySound2D' $false ($px + 500) $oy
  Add-Pin $play 'Sound' 'in' 'object' '' $SOUND
  Add-Pin $play 'VolumeMultiplier' 'in' 'real' 'float' $null '1.0'
  $script:playNodes += $play
  Connect $seLevel 'SeVolumeLevel' $toFloat 'InInt'
  Connect $toFloat 'ReturnValue' $volume 'A'
  Connect $volume 'ReturnValue' $play 'VolumeMultiplier'
  foreach ($m in $moves) {
    Connect $m 'then' $play 'execute'
    $skips += Get-Pin $m 'else'
  }
  $skips += Get-Pin $play 'then'

  # Splice: Started -> the check; every way out of the check -> the original first node.
  $inMenuIn = Get-Pin $inMenu 'execute'
  $inMenuIn.Links.Add("$eventName $startedId")
  $blocks[$eventName] = Set-ExportPin $event 'Started' @("$($inMenu.Name) $($inMenuIn.Id)") $false
  (Get-Pin $step 'A').Links.Add("$eventName $valueId")
  $blocks[$eventName] = Set-ExportPin $blocks[$eventName] 'ActionValue' @("$($step.Name) $((Get-Pin $step 'A').Id)") $true
  foreach ($exit in $skips) { $exit.Links.Add("$firstName $firstPinId") }
  $owners = foreach ($exit in $skips) { $script:nodes | Where-Object { $_.Pins.Contains($exit) } | Select-Object -First 1 }
  $links = for ($i = 0; $i -lt $skips.Count; $i++) { "$($owners[$i].Name) $($skips[$i].Id)," }
  $blocks[$firstName] = $blocks[$firstName].Replace("$eventName $startedId,", ($links -join ''))
}

$script:playNodes = @()
Add-MoveSound 'K2Node_EnhancedInputAction_1' $true
Add-MoveSound 'K2Node_EnhancedInputAction_2' $false
$sectionNames = (Get-Section $blocks 'K2Node_EnhancedInputAction_1') + (Get-Section $blocks 'K2Node_EnhancedInputAction_2') |
  Where-Object { $blocks.Contains($_) }

$sb = [System.Text.StringBuilder]::new()
foreach ($name in $sectionNames) { [void]$sb.AppendLine($blocks[$name]) }
foreach ($n in $script:nodes) {
  [void]$sb.AppendLine("Begin Object Class=$($n.Class) Name=`"$($n.Name)`"")
  foreach ($prop in $n.Props) { [void]$sb.AppendLine("   $prop") }
  [void]$sb.AppendLine("   NodePosX=$($n.X)")
  [void]$sb.AppendLine("   NodePosY=$($n.Y)")
  [void]$sb.AppendLine("   NodeGuid=$([guid]::NewGuid().ToString('N').ToUpper())")
  foreach ($p in $n.Pins) {
    $line = Format-Pin $p
    # Object pins take their asset as DefaultObject, which Format-Pin does not write.
    if ($script:playNodes -contains $n -and $p.Name -eq 'Sound') { $line = $line -replace 'PersistentGuid=', "DefaultObject=`"$MOVE_CUE`",PersistentGuid=" }
    [void]$sb.AppendLine($line)
  }
  [void]$sb.AppendLine('End Object')
}
Assert-LinksResolve $sb.ToString()
[IO.File]::WriteAllText((Join-Path $OutDir 'PauseMenu_5_Controller_MenuInput_MoveSound.txt'), $sb.ToString(), [Text.UTF8Encoding]::new($false))
"Generated $($sectionNames.Count) copied + $($script:nodes.Count) new nodes"
