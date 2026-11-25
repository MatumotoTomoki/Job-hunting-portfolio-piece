param([string]$OutDir)
# Paste text for the checkpoint flag as it works since 2026-11-19 (the user: the flags stand in the level from the
# start, broken; touched, a flag stands up and from then on every fall comes back to it): BP_CheckpointFlag_EventGraph.txt
# (components and variables from setup_checkpoint_flags.py).
#   Begin Play: the top half (Upper) lies tipped over (BreakFlag's pose: roll 85 at the 55 cm joint).
#   Touched by the player (Touch box), the first time only: Raised, the player's ActiveFlag = this flag, the top half
#     swings up straight in 0.35 s (eased). The character's fall check then sends the player to this flag's
#     RespawnPoint on every fall (its "break and forget" nodes removed by hand, see setup_checkpoint_flags.py).
#   While the player is in Touch the flag listens to E (IA_UseItem); walking away stops it.
#   E by a raised flag not yet Broken: Broken, it tips over again for good (Raised stays, so it never stands up
#     again); if it was the player's ActiveFlag, that is cleared (falls go back to the area's start).
#   BreakFlag (kept: the character's old plant-a-flag graph still calls it): the top snaps over, the flag is removed.
#   Achievements (2026-11-21): raising adds the flag to GI RaisedFlags (ACH_FLAGS once FlagTotal are up); breaking it
#     with E is ACH_BREAK_FLAG. Only flags in LV_Area* levels go on RaisedFlags (11-25: the hidden stages' don't count).
if (-not $OutDir) { throw 'OutDir is required' }
$lightGen = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_heaven_light.ps1') -Encoding UTF8
$cut = ($lightGen | Select-String -Pattern '^# ===== BP_LightBeam' | Select-Object -First 1).LineNumber - 1
$helpers = $lightGen[1..($cut - 1)] -join "`n"
. ([ScriptBlock]::Create($helpers))

$CHARACTER_BP = "/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter1.BP_ThirdPersonCharacter1_C'"
$FLAG_BP = "/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPerson/Item/Checkpoint/BP_CheckpointFlag.BP_CheckpointFlag_C'"
$JOINT = '0.000000,0.000000,55.000000'
$BROKEN = '0.000000,0.000000,85.000000'    # Pitch, Yaw, Roll: tipped over sideways
$UPRIGHT = '0.000000,0.000000,0.000000'

function MoveTo($componentName, $where, $rotation, $seconds, [double]$x, [double]$y) {
  $n = New-Call $SYSTEM 'MoveComponentTo' $false $x $y
  $n.Props = @('bWantsEnumToExecExpansion=True') + $n.Props
  $n.Pins.Clear()
  Add-Pin $n 'Move' 'in' 'exec'
  Add-Pin $n 'then' 'out' 'exec'
  Add-Pin $n 'Component' 'in' 'object' '' $SCENE
  Add-Pin $n 'TargetRelativeLocation' 'in' 'struct' '' $VECTOR $where
  Add-Pin $n 'TargetRelativeRotation' 'in' 'struct' '' $ROTATOR $rotation
  Add-Pin $n 'bEaseOut' 'in' 'bool' '' $null 'true'
  Add-Pin $n 'bEaseIn' 'in' 'bool' '' $null 'false'
  Add-Pin $n 'OverTime' 'in' 'real' 'float' $null $seconds
  Add-Pin $n 'bForceShortestRotationPath' 'in' 'bool' '' $null 'true'
  Connect (Comp $componentName $SCENE ($x - 200) ($y + 250)) $componentName $n 'Component'
  return $n
}

Reset-Graph 100
# ----- Begin Play: broken -----
$begin = Event 'ReceiveBeginPlay' 0 0
$lie = New-Call $SCENE 'K2_SetRelativeLocationAndRotation' $false 300 0
Add-Pin $lie 'self' 'in' 'object' '' $SCENE
Add-Pin $lie 'NewLocation' 'in' 'struct' '' $VECTOR $JOINT
Add-Pin $lie 'NewRotation' 'in' 'struct' '' $ROTATOR $BROKEN
Add-Pin $lie 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $lie 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $lie 'bTeleport' 'in' 'bool' '' $null 'true'
Connect (Comp 'Upper' $SCENE 100 200) 'Upper' $lie 'self'
Connect $begin 'then' $lie 'execute'

# ----- touched: stands up, becomes the checkpoint -----
$touch = Event 'ReceiveActorBeginOverlap' 0 500
Add-Pin $touch 'OtherActor' 'out' 'object' '' $ACTOR
$once = New-Branch 300 500
Connect (Bool 'Raised' 150 700) 'Raised' $once 'Condition'
$inside = New-Call $PRIMITIVE 'IsOverlappingActor' $true 400 750
Add-Pin $inside 'self' 'in' 'object' '' $PRIMITIVE
Add-Pin $inside 'Other' 'in' 'object' '' $ACTOR
Add-Pin $inside 'ReturnValue' 'out' 'bool'
Connect (Comp 'Touch' $BOX 200 750) 'Touch' $inside 'self'
Connect (Player 200 850) 'ReturnValue' $inside 'Other'
$isPlayer = New-Branch 600 500
Connect $inside 'ReturnValue' $isPlayer 'Condition'
$raised = SetSelf 'Raised' 'bool' 'true' 850 500
$cast = New-Node '/Script/BlueprintGraph.K2Node_DynamicCast' @("TargetType=`"$CHARACTER_BP`"") 1100 500
Add-Exec $cast
Add-Pin $cast 'CastFailed' 'out' 'exec'
Add-Pin $cast 'Object' 'in' 'object' '' $OBJECT
Add-Pin $cast 'AsBP Third Person Character 1' 'out' 'object' '' $CHARACTER_BP
Add-Pin $cast 'bSuccess' 'out' 'bool'
Connect (Player 900 700) 'ReturnValue' $cast 'Object'
$remember = New-VarSet 'ActiveFlag' $CHARACTER_BP 'object' $FLAG_BP 1450 500
Connect $cast 'AsBP Third Person Character 1' $remember 'self'
$self = New-Node '/Script/BlueprintGraph.K2Node_Self' @() 1250 750
Add-Pin $self 'self' 'out' 'object' '' $ACTOR
Connect $self 'self' $remember 'ActiveFlag'
$standUp = MoveTo 'Upper' $JOINT $UPRIGHT '0.35' 1800 500
# The player near the flag: it listens to E (IA_UseItem) while they are in Touch (2026-11-19).
function Flag-Input($func, [double]$x, [double]$y) {
  $n = New-Call $ACTOR $func $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR
  Add-Pin $n 'PlayerController' 'in' 'object' '' $CONTROLLER
  Connect (Controller ($x - 200) ($y + 250)) 'ReturnValue' $n 'PlayerController'
  return $n
}
$listen = Flag-Input 'EnableInput' 300 300
Connect $touch 'then' $isPlayer 'execute'
Connect $isPlayer 'then' $listen 'execute'
Connect $listen 'then' $once 'execute'
Connect $once 'else' $raised 'execute'
Connect $cast 'then' $remember 'execute'
# Achievements (2026-11-21, ACH_FLAGS): "<level>.<this flag>" goes on GI RaisedFlags once; all FlagTotal of them raised
# -> ACH_FLAGS. Either way on to the cast.
$gi = GameInstance 1100 (-300)
Connect $raised 'then' $gi 'execute'
$levelName = New-Call $STATICS 'GetCurrentLevelName' $false 1400 (-300)
Add-Pin $levelName 'bRemovePrefixString' 'in' 'bool' '' $null 'true'
Add-Pin $levelName 'ReturnValue' 'out' 'string'
Connect $gi 'then' $levelName 'execute'
$selfName = New-Call $SYSTEM 'GetObjectName' $true 1400 (-50)
Add-Pin $selfName 'Object' 'in' 'object' '' $OBJECT
Add-Pin $selfName 'ReturnValue' 'out' 'string'
$selfForName = New-Node '/Script/BlueprintGraph.K2Node_Self' @() 1250 (-50)
Add-Pin $selfForName 'self' 'out' 'object' '' $ACTOR
Connect $selfForName 'self' $selfName 'Object'
function Joined($a, $aPin, $b, $bPin, $bText, [double]$x, [double]$y) {
  $n = New-Call $STRINGS 'Concat_StrStr' $true $x $y
  Add-Pin $n 'A' 'in' 'string'
  Add-Pin $n 'B' 'in' 'string' '' $null $bText
  Add-Pin $n 'ReturnValue' 'out' 'string'
  Connect $a $aPin $n 'A'
  if ($b) { Connect $b $bPin $n 'B' }
  return $n
}
$withDot = Joined $levelName 'ReturnValue' $null $null '.' 1650 (-150)
$flagId = Joined $withDot 'ReturnValue' $selfName 'ReturnValue' $null 1850 (-100)
$flagName = New-Call $STRINGS 'Conv_StringToName' $true 2050 (-100)
Add-Pin $flagName 'InString' 'in' 'string'
Add-Pin $flagName 'ReturnValue' 'out' 'name'
Connect $flagId 'ReturnValue' $flagName 'InString'
$addFlag = New-Call $ARRAYLIB 'Array_AddUnique' $false 2250 (-300) '/Script/BlueprintGraph.K2Node_CallArrayFunction'
Add-Pin $addFlag 'TargetArray' 'in' 'name' '' $null $null 'Array'
Add-Pin $addFlag 'NewItem' 'in' 'name'
Add-Pin $addFlag 'ReturnValue' 'out' 'int'
$flagsGet = New-VarGet 'RaisedFlags' $GI_CLASS 'name' '' $null 2050 (-200) 'Array'
Connect $gi $GI_OUT $flagsGet 'self'
Connect $flagsGet 'RaisedFlags' $addFlag 'TargetArray'
Connect $flagName 'ReturnValue' $addFlag 'NewItem'
# Only the four areas' flags count (the user, 2026-11-25: the hidden stages' flags are left out of ACH_FLAGS).
$isArea = New-Call $STRINGS 'StartsWith' $true 1650 (-450)
Add-Pin $isArea 'SourceString' 'in' 'string'
Add-Pin $isArea 'InPrefix' 'in' 'string' '' $null 'LV_Area'
Add-Pin $isArea 'SearchCase' 'in' 'byte' '' "/Script/CoreUObject.Enum'/Script/CoreUObject.ESearchCase'" 'IgnoreCase'
Add-Pin $isArea 'ReturnValue' 'out' 'bool'
foreach ($pin in 'SourceString', 'InPrefix') { (Get-Pin $isArea $pin) | Add-Member -NotePropertyName ConstRef -NotePropertyValue $true -Force }
Connect $levelName 'ReturnValue' $isArea 'SourceString'
$counts = New-Branch 1900 (-300)
Connect $isArea 'ReturnValue' $counts 'Condition'
Connect $levelName 'then' $counts 'execute'
Connect $counts 'then' $addFlag 'execute'
$flagsGet2 = New-VarGet 'RaisedFlags' $GI_CLASS 'name' '' $null 2300 (-50) 'Array'
Connect $gi $GI_OUT $flagsGet2 'self'
$howMany = New-Call $ARRAYLIB 'Array_Length' $true 2500 (-50) '/Script/BlueprintGraph.K2Node_CallArrayFunction'
Add-Pin $howMany 'TargetArray' 'in' 'name' '' $null $null 'Array'
Add-Pin $howMany 'ReturnValue' 'out' 'int'
Connect $flagsGet2 'RaisedFlags' $howMany 'TargetArray'
$allUp = New-Operator 'GreaterEqual' 'GreaterEqual_IntInt' 'int' '' 'bool' 2700 (-50)
Connect $howMany 'ReturnValue' $allUp 'A'
Connect (GiGet $gi 'FlagTotal' 'int' '' 2500 50) 'FlagTotal' $allUp 'B'
$everyFlag = New-Branch 2600 (-300)
Connect $allUp 'ReturnValue' $everyFlag 'Condition'
Connect $addFlag 'then' $everyFlag 'execute'
function Achieve($giCast, $id, [double]$x, [double]$y) {
  $n = New-Call $GI_CLASS 'UnlockAchievement' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $GI_CLASS
  Add-Pin $n 'ID' 'in' 'name' '' $null $id
  Connect $giCast $GI_OUT $n 'self'
  return $n
}
$flagsDone = Achieve $gi 'ACH_FLAGS' 2900 (-300)
Connect $everyFlag 'then' $flagsDone 'execute'
Connect $flagsDone 'then' $cast 'execute'
Connect $everyFlag 'else' $cast 'execute'
Connect $counts 'else' $cast 'execute'
Connect $remember 'then' $standUp 'Move'

# ----- the player walks away: stop listening to E -----
$leave = Event 'ReceiveActorEndOverlap' 0 1700
Add-Pin $leave 'OtherActor' 'out' 'object' '' $ACTOR
$stillIn = New-Call $PRIMITIVE 'IsOverlappingActor' $true 250 1900
Add-Pin $stillIn 'self' 'in' 'object' '' $PRIMITIVE
Add-Pin $stillIn 'Other' 'in' 'object' '' $ACTOR
Add-Pin $stillIn 'ReturnValue' 'out' 'bool'
Connect (Comp 'Touch' $BOX 50 1900) 'Touch' $stillIn 'self'
Connect (Player 50 2000) 'ReturnValue' $stillIn 'Other'
$gone = New-Branch 450 1700
Connect $stillIn 'ReturnValue' $gone 'Condition'
$deaf = Flag-Input 'DisableInput' 750 1700
Connect $leave 'then' $gone 'execute'
Connect $gone 'else' $deaf 'execute'

# ----- E by a standing flag: it breaks again, for good (2026-11-19) -----
# Only a raised flag not yet broken, with the player at it. If it was the player's checkpoint, that is forgotten
# (a fall goes back to the area's start). Raised stays true, so touching it never raises it again.
$e = New-Node '/Script/InputBlueprintNodes.K2Node_EnhancedInputAction' @("InputAction=`"/Script/EnhancedInput.InputAction'/Game/Input/Actions/IA_UseItem.IA_UseItem'`"") 0 2300
Add-Pin $e 'Started' 'out' 'exec'
$notBroken = MathCall 'Not_PreBool' @('A') 'bool' '' 'bool' '' 200 2650
Connect (Bool 'Broken' 50 2650) 'Broken' $notBroken 'A'
$standing = Both (Bool 'Raised' 200 2550) 'Raised' $notBroken 'ReturnValue' 'BooleanAND' 400 2550
$canBreak = New-Branch 300 2300
Connect $standing 'ReturnValue' $canBreak 'Condition'
$atFlag = New-Call $PRIMITIVE 'IsOverlappingActor' $true 450 2750
Add-Pin $atFlag 'self' 'in' 'object' '' $PRIMITIVE
Add-Pin $atFlag 'Other' 'in' 'object' '' $ACTOR
Add-Pin $atFlag 'ReturnValue' 'out' 'bool'
Connect (Comp 'Touch' $BOX 250 2750) 'Touch' $atFlag 'self'
Connect (Player 250 2850) 'ReturnValue' $atFlag 'Other'
$near = New-Branch 600 2300
Connect $atFlag 'ReturnValue' $near 'Condition'
$markBroken = SetSelf 'Broken' 'bool' 'true' 850 2300
$cast2 = New-Node '/Script/BlueprintGraph.K2Node_DynamicCast' @("TargetType=`"$CHARACTER_BP`"") 1100 2300
Add-Exec $cast2
Add-Pin $cast2 'CastFailed' 'out' 'exec'
Add-Pin $cast2 'Object' 'in' 'object' '' $OBJECT
Add-Pin $cast2 'AsBP Third Person Character 1' 'out' 'object' '' $CHARACTER_BP
Add-Pin $cast2 'bSuccess' 'out' 'bool'
Connect (Player 900 2500) 'ReturnValue' $cast2 'Object'
$current = New-VarGet 'ActiveFlag' $CHARACTER_BP 'object' '' $FLAG_BP 1300 2550
Connect $cast2 'AsBP Third Person Character 1' $current 'self'
$isMine = MathCall 'EqualEqual_ObjectObject' @('A', 'B') 'object' '' 'bool' '' 1550 2550
(Get-Pin $isMine 'A').Obj = $OBJECT; (Get-Pin $isMine 'B').Obj = $OBJECT
Connect $current 'ActiveFlag' $isMine 'A'
$self2 = New-Node '/Script/BlueprintGraph.K2Node_Self' @() 1350 2700
Add-Pin $self2 'self' 'out' 'object' '' $ACTOR
Connect $self2 'self' $isMine 'B'
$mine = New-Branch 1400 2300
Connect $isMine 'ReturnValue' $mine 'Condition'
$forget = New-VarSet 'ActiveFlag' $CHARACTER_BP 'object' $FLAG_BP 1700 2200
Connect $cast2 'AsBP Third Person Character 1' $forget 'self'
$fallOver = MoveTo 'Upper' $JOINT $BROKEN '0.35' 2050 2300
Connect $e 'Started' $canBreak 'execute'
Connect $canBreak 'then' $near 'execute'
Connect $near 'then' $markBroken 'execute'
# Achievements (2026-11-21): breaking one's own flag is ACH_BREAK_FLAG.
$gi2 = GameInstance 850 2000
$selfBreak = Achieve $gi2 'ACH_BREAK_FLAG' 1100 2000
Connect $markBroken 'then' $gi2 'execute'
Connect $gi2 'then' $selfBreak 'execute'
Connect $selfBreak 'then' $cast2 'execute'
Connect $cast2 'then' $mine 'execute'
Connect $mine 'then' $forget 'execute'
Connect $forget 'then' $fallOver 'Move'
Connect $mine 'else' $fallOver 'Move'
Connect $cast2 'CastFailed' $fallOver 'Move'


# ----- BreakFlag (kept for the character's old plant-a-flag graph) -----
$breakEvent = New-Node '/Script/BlueprintGraph.K2Node_CustomEvent' @('CustomFunctionName="BreakFlag"') 0 1200
Add-Pin $breakEvent 'then' 'out' 'exec'
$snap = MoveTo 'Upper' $JOINT $BROKEN '0.35' 400 1200
$linger = Delay '0.8' 800 1200
$remove = New-Call $ACTOR 'K2_DestroyActor' $false 1100 1200
Add-Pin $remove 'self' 'in' 'object' '' $ACTOR
Connect $breakEvent 'then' $snap 'Move'
Connect $snap 'then' $linger 'execute'
Connect $linger 'then' $remove 'execute'
Write-Graph 'BP_CheckpointFlag_EventGraph.txt'
