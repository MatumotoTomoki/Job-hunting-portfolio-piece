param([string]$OutDir)
# Debug commands for the achievements (the user, 2026-11-24: "type a command while playing and every achievement is
# taken"). Paste text for BP_MyGameInstance's EventGraph: three custom events, called from the console (~) in play
# (PIE or a development build; the console is not in shipping builds):
#   ke * DebugAllAchievements             every achievement taken (no corner notices), saved
#   ke * DebugResetAchievements           every achievement gone, the save deleted
#   ke * DebugLockAchievement ACH_COIN_S2 that one taken off again (to earn it once more), saved
#   (ke * UnlockAchievement ACH_COIN_S2   the game's own function: takes one, with its notice)
# Each prints what it did. Writes GI_DebugAchievements.txt.
if (-not $OutDir) { throw 'OutDir is required' }
$GenDir = if ($PSScriptRoot) { $PSScriptRoot } else { $GenDir }
# gen_achievements' helpers (from its first helper to the first graph), without running its graphs.
$achLines = Get-Content -LiteralPath (Join-Path $GenDir 'gen_achievements.ps1') -Encoding UTF8
$from = ($achLines | Select-String -Pattern '^\$cageGen = ' | Select-Object -First 1).LineNumber - 1
$to = ($achLines | Select-String -Pattern '^# ===== LoadAchievements' | Select-Object -First 1).LineNumber - 2
. ([ScriptBlock]::Create(($achLines[$from..$to] -join "`n")))

function CustomEvent($name, [double]$x, [double]$y) {
  $n = New-Node '/Script/BlueprintGraph.K2Node_CustomEvent' @("CustomFunctionName=`"$name`"") $x $y
  Add-Pin $n 'then' 'out' 'exec'
  return $n
}
function BoolAnd2($a, $aPin, $b, $bPin, [double]$x, [double]$y) {
  $n = New-Call $MATH 'BooleanAND' $true $x $y
  Add-Pin $n 'A' 'in' 'bool'
  Add-Pin $n 'B' 'in' 'bool'
  Add-Pin $n 'ReturnValue' 'out' 'bool'
  Connect $a $aPin $n 'A'
  Connect $b $bPin $n 'B'
  return $n
}
function Text([string]$s, [double]$x, [double]$y) {
  # a literal string for Print: an empty Concat with the text as A
  return (Concat $null $s $null '' $x $y)
}
# The slot written from UnlockedAchievements and FreeAchievementCount; returns (first, last).
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

Reset-Graph 100
# ----- ke * DebugAllAchievements -----
$all = CustomEvent 'DebugAllAchievements' 0 0
$loadA = New-Node '/Script/BlueprintGraph.K2Node_CallFunction' @('FunctionReference=(MemberName="LoadAchievements",bSelfContext=True)') 250 0
Add-Exec $loadA
$setAll = SelfSet 'UnlockedAchievements' 'name' 550 0 'Array'
Connect (SelfGet 'AchievementIds' 'name' 350 200 'Array') 'AchievementIds' $setAll 'UnlockedAchievements'
$length = ArrayCall 'Array_Length' $true 700 250
Add-Pin $length 'TargetArray' 'in' 'name' '' $null $null 'Array'
Add-Pin $length 'ReturnValue' 'out' 'int'
Connect (SelfGet 'FreeAchievements' 'name' 500 300 'Array') 'FreeAchievements' $length 'TargetArray'
$setFree = SelfSet 'FreeAchievementCount' 'int' 900 0
Connect $length 'ReturnValue' $setFree 'FreeAchievementCount'
$saveA = SaveNow 1250 0
$printA = Print (Text '【デバッグ】全実績を解除しました' 2700 200) 'ReturnValue' 2950 0
Connect $all 'then' $loadA 'execute'
Chain @($loadA, $setAll, $setFree, $saveA[0])
Connect $saveA[1] 'then' $printA 'execute'

# ----- ke * DebugResetAchievements -----
$reset = CustomEvent 'DebugResetAchievements' 0 800
$loadR = New-Node '/Script/BlueprintGraph.K2Node_CallFunction' @('FunctionReference=(MemberName="LoadAchievements",bSelfContext=True)') 250 800
Add-Exec $loadR
$clear = ArrayCall 'Array_Clear' $false 550 800
Add-Pin $clear 'TargetArray' 'in' 'name' '' $null $null 'Array'
Connect (SelfGet 'UnlockedAchievements' 'name' 350 1000 'Array') 'UnlockedAchievements' $clear 'TargetArray'
$zero = SelfSet 'FreeAchievementCount' 'int' 850 800 'None' '0'
$delete = Slot 'DeleteGameInSlot' $false 1150 800
Add-Pin $delete 'ReturnValue' 'out' 'bool'
$printR = Print (Text '【デバッグ】全実績をリセットしました' 1400 1000) 'ReturnValue' 1650 800
Connect $reset 'then' $loadR 'execute'
Chain @($loadR, $clear, $zero, $delete, $printR)

# ----- ke * DebugLockAchievement <ID> -----
$lock = CustomEvent 'DebugLockAchievement' 0 1500
Add-Pin $lock 'ID' 'out' 'name'
$lock.Props += 'CustomProperties UserDefinedPin (PinName="ID",PinType=(PinCategory="name"),DesiredPinDirection=EGPD_Output)'
$loadL = New-Node '/Script/BlueprintGraph.K2Node_CallFunction' @('FunctionReference=(MemberName="LoadAchievements",bSelfContext=True)') 250 1500
Add-Exec $loadL
$setLast = SelfSet 'LastAchievement' 'name' 550 1500
Connect $lock 'ID' $setLast 'LastAchievement'
$remove = ArrayCall 'Array_RemoveItem' $false 850 1500
Add-Pin $remove 'TargetArray' 'in' 'name' '' $null $null 'Array'
Add-Pin $remove 'Item' 'in' 'name'
Add-Pin $remove 'ReturnValue' 'out' 'bool'
Connect (SelfGet 'UnlockedAchievements' 'name' 650 1700 'Array') 'UnlockedAchievements' $remove 'TargetArray'
Connect (SelfGet 'LastAchievement' 'name' 650 1800) 'LastAchievement' $remove 'Item'
$wasFree = New-Branch 1200 1500
$freeOne = Contains (SelfGet 'FreeAchievements' 'name' 900 1850 'Array') 'FreeAchievements' (SelfGet 'LastAchievement' 'name' 900 1950) 'LastAchievement' 1100 1850
Connect (BoolAnd2 $remove 'ReturnValue' $freeOne 'ReturnValue' 1150 1750) 'ReturnValue' $wasFree 'Condition'
$countDown = SelfSet 'FreeAchievementCount' 'int' 1550 1350
$minusOne = New-Operator 'Subtract' 'Subtract_IntInt' 'int' '' 'int' 1400 1250
Connect (SelfGet 'FreeAchievementCount' 'int' 1200 1250) 'FreeAchievementCount' $minusOne 'A'
(Get-Pin $minusOne 'B').Default = '1'
Connect $minusOne 'ReturnValue' $countDown 'FreeAchievementCount'
$saveL = SaveNow 1900 1500
$idText = New-Call $STRINGS 'Conv_NameToString' $true 3300 1750
Add-Pin $idText 'InName' 'in' 'name'
Add-Pin $idText 'ReturnValue' 'out' 'string'
Connect (SelfGet 'LastAchievement' 'name' 3100 1750) 'LastAchievement' $idText 'InName'
$printL = Print (Concat $null '【デバッグ】実績を取り消しました: ' $idText 'ReturnValue' 3500 1700) 'ReturnValue' 3750 1500
Connect $lock 'then' $loadL 'execute'
Chain @($loadL, $setLast, $remove, $wasFree)
Connect $wasFree 'then' $countDown 'execute'
Connect $wasFree 'else' $saveL[0] 'execute'
Connect $countDown 'then' $saveL[0] 'execute'
Connect $saveL[1] 'then' $printL 'execute'

Write-Graph 'GI_DebugAchievements.txt'

# ----- the J key (the user, 2026-11-24): BP_ThirdPersonCharacter's EventGraph, J pressed -> DebugAllAchievements.
# Not in a packaged shipping game (Is Packaged For Distribution), so it cannot be pressed by players.
Reset-Graph 100
$key = New-Node '/Script/BlueprintGraph.K2Node_InputKey' @('InputKey=J') 0 0
Add-Pin $key 'Pressed' 'out' 'exec'
Add-Pin $key 'Released' 'out' 'exec'
Add-Pin $key 'Key' 'out' 'struct' '' "/Script/CoreUObject.ScriptStruct'/Script/InputCore.Key'"
$shipping = New-Call $SYSTEM 'IsPackagedForDistribution' $true 100 250
Add-Pin $shipping 'ReturnValue' 'out' 'bool'
$devOnly = New-Branch 300 0
Connect $shipping 'ReturnValue' $devOnly 'Condition'
Connect $key 'Pressed' $devOnly 'execute'
$castJ = GameInstance 650 0
Connect $devOnly 'else' $castJ 'execute'
$callAll = New-Call $GI_CLASS 'DebugAllAchievements' $false 950 0
Add-Pin $callAll 'self' 'in' 'object' '' $GI_CLASS
Connect $castJ $GI_OUT $callAll 'self'
Connect $castJ 'then' $callAll 'execute'
Write-Graph 'Character_DebugAchievementsJ.txt'
