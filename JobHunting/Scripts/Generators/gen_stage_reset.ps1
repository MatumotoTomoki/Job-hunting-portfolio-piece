param([string]$OutDir)
# Pause menu リセット (2026-11-25; variables from setup_stage_reset.py). Writes:
#   GI_StageReset.txt         for BP_MyGameInstance's EventGraph, two custom events:
#     SnapshotStage  in a stage (LV_Area*, LV_Secret*) other than SnapshotLevel: SnapshotLevel = it, and the run's
#                    TakenCoinIds, TakenItems, RaisedFlags, the achievements (loaded first), the carried item effects
#                    (HasSavedStats, SavedWalkSpeed/JumpZ/JumpCount) and RunFell/RunUsedFlag/RunTookItem copied to Stage*.
#                    (A hell return or a reset reopens the same level: no new snapshot.)
#     ResetStage     all of that put back (TakenInArea 0), the achievements saved to their slot, ChangingArea on (so
#                    BP_AreaStart fades in and gives the carried item effects back), the game unpaused, SnapshotLevel opened.
#   AreaStart_Snapshot.txt    for BP_AreaStart's Begin Play (after the ACH_ENTER_S hook, before the ChangingArea Branch):
#                    Cast To BP_MyGameInstance -> SnapshotStage.
if (-not $OutDir) { throw 'OutDir is required' }
$GenDir = if ($PSScriptRoot) { $PSScriptRoot } else { $GenDir }
$achLines = Get-Content -LiteralPath (Join-Path $GenDir 'gen_achievements.ps1') -Encoding UTF8
$from = ($achLines | Select-String -Pattern '^\$cageGen = ' | Select-Object -First 1).LineNumber - 1
$to = ($achLines | Select-String -Pattern '^# ===== LoadAchievements' | Select-Object -First 1).LineNumber - 2
. ([ScriptBlock]::Create(($achLines[$from..$to] -join "`n")))

function CustomEvent($name, [double]$x, [double]$y) {
  $n = New-Node '/Script/BlueprintGraph.K2Node_CustomEvent' @("CustomFunctionName=`"$name`"") $x $y
  Add-Pin $n 'then' 'out' 'exec'
  return $n
}
function SelfCall($name, [double]$x, [double]$y) {
  $n = New-Node '/Script/BlueprintGraph.K2Node_CallFunction' @("FunctionReference=(MemberName=`"$name`",bSelfContext=True)") $x $y
  Add-Exec $n
  return $n
}
# to = from (both members of the game instance): returns the Set node.
function CopyVar($from, $to, $cat, [double]$x, [double]$y, $sub = '', $container = 'None') {
  $get = SelfGet $from $cat ($x - 200) ($y + 200) $container
  $set = SelfSet $to $cat $x $y $container
  if ($sub) { foreach ($pin in $to, 'Output_Get') { (Get-Pin $set $pin).Sub = $sub }; (Get-Pin $get $from).Sub = $sub }
  Connect $get $from $set $to
  return $set
}
function StartsWith($node, $pin, $prefix, [double]$x, [double]$y) {
  $n = New-Call $STRINGS 'StartsWith' $true $x $y
  Add-Pin $n 'SourceString' 'in' 'string'
  Add-Pin $n 'InPrefix' 'in' 'string' '' $null $prefix
  Add-Pin $n 'SearchCase' 'in' 'byte' '' "/Script/CoreUObject.Enum'/Script/CoreUObject.ESearchCase'" 'IgnoreCase'
  Add-Pin $n 'ReturnValue' 'out' 'bool'
  ConstRef $n @('SourceString', 'InPrefix')
  Connect $node $pin $n 'SourceString'
  return $n
}
function BoolOp($func, $a, $aPin, $b, $bPin, [double]$x, [double]$y) {
  $n = New-Call $MATH $func $true $x $y
  Add-Pin $n 'A' 'in' 'bool'
  Add-Pin $n 'B' 'in' 'bool'
  Add-Pin $n 'ReturnValue' 'out' 'bool'
  Connect $a $aPin $n 'A'
  Connect $b $bPin $n 'B'
  return $n
}
# The achievements slot written from UnlockedAchievements and FreeAchievementCount: returns (first, last).
function SaveNow([double]$x, [double]$y) {
  $create = New-Call $STATICS 'CreateSaveGameObject' $false $x $y
  Add-Pin $create 'SaveGameClass' 'in' 'class' '' $SAVEGAME
  (Get-Pin $create 'SaveGameClass') | Add-Member -NotePropertyName DefaultObject -NotePropertyValue $SAVE_PATH
  Add-Pin $create 'ReturnValue' 'out' 'object' '' $SAVEGAME
  $cast = SaveCast ($x + 350) $y
  Connect $create 'then' $cast 'execute'
  Connect $create 'ReturnValue' $cast 'Object'
  $putUnlocked = New-VarSet 'Unlocked' $SAVE_CLASS 'name' $null ($x + 700) $y
  foreach ($pin in 'Unlocked', 'Output_Get') { (Get-Pin $putUnlocked $pin).Container = 'Array' }
  Connect $cast $SAVE_OUT $putUnlocked 'self'
  Connect (SelfGet 'UnlockedAchievements' 'name' ($x + 500) ($y + 250) 'Array') 'UnlockedAchievements' $putUnlocked 'Unlocked'
  Connect $cast 'then' $putUnlocked 'execute'
  $putCount = New-VarSet 'FreeCount' $SAVE_CLASS 'int' $null ($x + 1050) $y
  Connect $cast $SAVE_OUT $putCount 'self'
  Connect (SelfGet 'FreeAchievementCount' 'int' ($x + 850) ($y + 300)) 'FreeAchievementCount' $putCount 'FreeCount'
  Connect $putUnlocked 'then' $putCount 'execute'
  $write = New-Call $STATICS 'SaveGameToSlot' $false ($x + 1400) $y
  Add-Pin $write 'SaveGameObject' 'in' 'object' '' $SAVEGAME
  Add-Pin $write 'SlotName' 'in' 'string' '' $null $SLOT
  Add-Pin $write 'UserIndex' 'in' 'int' '' $null '0'
  Add-Pin $write 'ReturnValue' 'out' 'bool'
  ConstRef $write 'SlotName'
  Connect $cast $SAVE_OUT $write 'SaveGameObject'
  Connect $putCount 'then' $write 'execute'
  return @($create, $write)
}
# The pairs copied (game instance variable, stage copy, category, sub, container).
$PAIRS = @(
  @('TakenCoinIds', 'StageCoinIds', 'string', '', 'None'),
  @('TakenItems', 'StageItems', 'name', '', 'Array'),
  @('RaisedFlags', 'StageFlags', 'name', '', 'Array'),
  @('UnlockedAchievements', 'StageAchievements', 'name', '', 'Array'),
  @('FreeAchievementCount', 'StageFreeCount', 'int', '', 'None'),
  @('HasSavedStats', 'StageHasStats', 'bool', '', 'None'),
  @('SavedWalkSpeed', 'StageWalkSpeed', 'real', 'double', 'None'),
  @('SavedJumpZ', 'StageJumpZ', 'real', 'double', 'None'),
  @('SavedJumpCount', 'StageJumpCount', 'int', '', 'None'),
  @('RunFell', 'StageRunFell', 'bool', '', 'None'),
  @('RunUsedFlag', 'StageRunUsedFlag', 'bool', '', 'None'),
  @('RunTookItem', 'StageRunTookItem', 'bool', '', 'None'))

Reset-Graph 100
# ===== SnapshotStage =====
$snap = CustomEvent 'SnapshotStage' 0 0
$level = New-Call $STATICS 'GetCurrentLevelName' $false 250 0
Add-Pin $level 'bRemovePrefixString' 'in' 'bool' '' $null 'true'
Add-Pin $level 'ReturnValue' 'out' 'string'
Connect $snap 'then' $level 'execute'
$levelName = New-Call $STRINGS 'Conv_StringToName' $true 450 300
Add-Pin $levelName 'InString' 'in' 'string'
Add-Pin $levelName 'ReturnValue' 'out' 'name'
ConstRef $levelName @('InString')
Connect $level 'ReturnValue' $levelName 'InString'
$isStage = BoolOp 'BooleanOR' (StartsWith $level 'ReturnValue' 'LV_Area' 450 450) 'ReturnValue' (StartsWith $level 'ReturnValue' 'LV_Secret' 450 600) 'ReturnValue' 700 500
$differs = New-Call $MATH 'NotEqual_NameName' $true 700 300
Add-Pin $differs 'A' 'in' 'name'
Add-Pin $differs 'B' 'in' 'name'
Add-Pin $differs 'ReturnValue' 'out' 'bool'
Connect $levelName 'ReturnValue' $differs 'A'
Connect (SelfGet 'SnapshotLevel' 'name' 500 200) 'SnapshotLevel' $differs 'B'
$fresh = New-Branch 950 0
Connect (BoolOp 'BooleanAND' $isStage 'ReturnValue' $differs 'ReturnValue' 900 400) 'ReturnValue' $fresh 'Condition'
Connect $level 'then' $fresh 'execute'
$setLevel = SelfSet 'SnapshotLevel' 'name' 1250 0
Connect $levelName 'ReturnValue' $setLevel 'SnapshotLevel'
$loadA = SelfCall 'LoadAchievements' 1550 0
$chain = @($setLevel, $loadA)
$x = 1900
foreach ($p in $PAIRS) { $chain += CopyVar $p[0] $p[1] $p[2] $x 0 $p[3] $p[4]; $x += 300 }
Connect $fresh 'then' $setLevel 'execute'
Chain $chain

# ===== ResetStage =====
$reset = CustomEvent 'ResetStage' 0 900
$known = New-Branch 300 900
$hasLevel = New-Call $MATH 'NotEqual_NameName' $true 150 1100
Add-Pin $hasLevel 'A' 'in' 'name'
Add-Pin $hasLevel 'B' 'in' 'name' '' $null 'None'
Add-Pin $hasLevel 'ReturnValue' 'out' 'bool'
Connect (SelfGet 'SnapshotLevel' 'name' 0 1100) 'SnapshotLevel' $hasLevel 'A'
Connect $hasLevel 'ReturnValue' $known 'Condition'
Connect $reset 'then' $known 'execute'
$chain = @()
$x = 600
foreach ($p in $PAIRS) { $chain += CopyVar $p[1] $p[0] $p[2] $x 900 $p[3] $p[4]; $x += 300 }
$zeroCoins = SelfSet 'TakenInArea' 'int' $x 900 'None' '0'; $x += 300
$loaded = SelfSet 'AchievementsLoaded' 'bool' $x 900 'None' 'true'; $x += 300
$chain += @($zeroCoins, $loaded)
$save = SaveNow $x 900; $x += 1800
$arriving = SelfSet 'ChangingArea' 'bool' $x 900 'None' 'true'; $x += 300
$notHell = SelfSet 'ReturnFromHell' 'bool' $x 900 'None' 'false'; $x += 300
$unpause = New-Call $STATICS 'SetGamePaused' $false $x 900; $x += 300
Add-Pin $unpause 'bPaused' 'in' 'bool' '' $null 'false'
Add-Pin $unpause 'ReturnValue' 'out' 'bool'
$open = New-Call $STATICS 'OpenLevel' $false $x 900
Add-Pin $open 'LevelName' 'in' 'name'
Add-Pin $open 'bAbsolute' 'in' 'bool' '' $null 'true'
Add-Pin $open 'Options' 'in' 'string' '' $null ''
Connect (SelfGet 'SnapshotLevel' 'name' ($x - 200) 1100) 'SnapshotLevel' $open 'LevelName'
Connect $known 'then' $chain[0] 'execute'
Chain $chain
Connect $chain[-1] 'then' $save[0] 'execute'
Connect $save[1] 'then' $arriving 'execute'
Chain @($arriving, $notHell, $unpause, $open)
Write-Graph 'GI_StageReset.txt'

# ===== BP_AreaStart: the snapshot =====
Reset-Graph 900
$cast = GameInstance 250 0
$call = New-Call $GI_CLASS 'SnapshotStage' $false 600 0
Add-Pin $call 'self' 'in' 'object' '' $GI_CLASS
Connect $cast $GI_OUT $call 'self'
Connect $cast 'then' $call 'execute'
Write-Body 'AreaStart_Snapshot.txt' $cast
