param([string]$OutDir, [switch]$Secret)
# -Secret: BP_SecretGate_EventGraph.txt for the hidden stages' last gate (LV_Secret4, 2026-11-23): the same show, but
#   the ending is ACH_SECRET_CLEAR and, 4 s on, back to LV_Title - no clear screen, no main achievements, no best time.
# Paste text for BP_HeavenGate (setup_heaven_gate.py; area 4's ending, 2026-11-22):
#   Touch (the player walks into Trigger, once): Started, StartedAt = now, ClearTime = the character's ElapsedTime;
#     the player's input off, the view cuts to ShowCamera; OpenSeconds + 0.6 s later back to the player (they walk
#     into the light, see Tick), 1.4 s later the screen fades to white over 1.5 s; then ElapsedTime = ClearTime (the
#     show's seconds don't count), the clear-time achievements (CLEAR; NO_FALL without RunFell; NO_FLAG without
#     RunUsedFlag; PURIST without RunTookItem and RunUsedFlag; TIME when ClearTime < TargetSeconds), and BP_GoalItem's
#     ending: the controller's ShowGameClear, and the best time into HeightSave.
#   Tick, once Started: t = now - StartedAt, e = ease(t / OpenSeconds): the hinges turn -/+ e * OpenAngle, the Veil
#     glows e * MaxGlow, GateLight shines e * MaxLight; from t >= WalkFrom the player is walked on through the gate.
if (-not $OutDir) { throw 'OutDir is required' }
$lightGen = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_heaven_light.ps1') -Encoding UTF8
$cut = ($lightGen | Select-String -Pattern '^# ===== BP_LightBeam' | Select-Object -First 1).LineNumber - 1
. ([ScriptBlock]::Create(($lightGen[1..($cut - 1)] -join "`n")))

$CHAR1 = "/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter1.BP_ThirdPersonCharacter1_C'"
$PC_CLASS = "/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPerson/Blueprints/BP_ThirdPersonPlayerController.BP_ThirdPersonPlayerController_C'"
$SAVE_CLASS = "/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPerson/Blueprints/BP_HeightSave.BP_HeightSave_C'"
$SAVE_BASE = "/Script/CoreUObject.Class'/Script/Engine.SaveGame'"
$MESH_COMP = "/Script/CoreUObject.Class'/Script/Engine.MeshComponent'"
$LIGHT_COMP = "/Script/CoreUObject.Class'/Script/Engine.LightComponent'"
$POINT_LIGHT = "/Script/CoreUObject.Class'/Script/Engine.PointLightComponent'"
$PAWN = "/Script/CoreUObject.Class'/Script/Engine.Pawn'"
$WHITE = '(R=1.000000,G=1.000000,B=1.000000,A=1.000000)'

function Times($a, $aPin, $b, $bPin, [double]$x, [double]$y) { Op 'Multiply' 'Multiply_DoubleDouble' $a $aPin $b $bPin $x $y }
function CastTo($class, $outName, [double]$x, [double]$y) {
  $n = New-Node '/Script/BlueprintGraph.K2Node_DynamicCast' @("TargetType=`"$class`"") $x $y
  Add-Exec $n
  Add-Pin $n 'CastFailed' 'out' 'exec'
  Add-Pin $n 'Object' 'in' 'object' '' $OBJECT
  Add-Pin $n $outName 'out' 'object' '' $class
  Add-Pin $n 'bSuccess' 'out' 'bool'
  return $n
}
function Unlock($cast, $id, [double]$x, [double]$y) {
  $n = New-Call $GI_CLASS 'UnlockAchievement' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $GI_CLASS
  Add-Pin $n 'ID' 'in' 'name' '' $null $id
  Connect $cast $GI_OUT $n 'self'
  return $n
}
function NotBool($node, $pin, [double]$x, [double]$y) {
  $n = MathCall 'Not_PreBool' @('A') 'bool' '' 'bool' '' $x $y
  Connect $node $pin $n 'A'
  return $n
}
# Branch on $condition: True runs Unlock $id; both ways go on to whatever is wired to the returned pair's ends.
function MaybeUnlock($cast, $condition, $conditionPin, $id, [double]$x, [double]$y) {
  $b = New-Branch $x $y
  Connect $condition $conditionPin $b 'Condition'
  $u = Unlock $cast $id ($x + 250) ($y - 150)
  Connect $b 'then' $u 'execute'
  return @($b, $u)
}

Reset-Graph 100
# ===== Touch =====
$touch = Event 'ReceiveActorBeginOverlap' 0 0
Add-Pin $touch 'OtherActor' 'out' 'object' '' $ACTOR
$once = New-Branch 250 0
Connect (Bool 'Started' 100 200) 'Started' $once 'Condition'
$isPlayer = New-Branch 500 0
$same = New-Call $MATH 'EqualEqual_ObjectObject' $true 350 250
Add-Pin $same 'A' 'in' 'object' '' $OBJECT
Add-Pin $same 'B' 'in' 'object' '' $OBJECT
Add-Pin $same 'ReturnValue' 'out' 'bool'
Connect $touch 'OtherActor' $same 'A'
Connect (Player 150 350) 'ReturnValue' $same 'B'
Connect $same 'ReturnValue' $isPlayer 'Condition'
Connect $touch 'then' $once 'execute'
Connect $once 'else' $isPlayer 'execute'
$started = SetSelf 'Started' 'bool' 'true' 750 0
$startedAt = SetReal 'StartedAt' 1000 0
Connect (Now 850 200) 'ReturnValue' $startedAt 'StartedAt'
$char = CastTo $CHAR1 'AsBP Third Person Character 1' 1250 0
Connect (Player 1050 250) 'ReturnValue' $char 'Object'
$clearTime = SetReal 'ClearTime' 1550 0
$elapsed = New-VarGet 'ElapsedTime' $CHAR1 'real' 'double' $null 1350 250
Connect $char 'AsBP Third Person Character 1' $elapsed 'self'
Connect $elapsed 'ElapsedTime' $clearTime 'ClearTime'
$noInput = InputCall 'DisableInput' 1800 0
$toGate = ViewTarget 2100 0
$self = New-Node '/Script/BlueprintGraph.K2Node_Self' @() 1900 300
Add-Pin $self 'self' 'out' 'object' '' $ACTOR
Connect $self 'self' $toGate 'NewViewTarget'
$waitOpen = Delay '3.6' 2400 0
Connect (Op 'Add' 'Add_DoubleDouble' (Real 'OpenSeconds' 2200 250) 'OpenSeconds' $null '0.6' 2350 250) 'ReturnValue' $waitOpen 'Duration'
$toPlayer = ViewTarget 2700 0
Connect (Player 2500 300) 'ReturnValue' $toPlayer 'NewViewTarget'
$waitWalk = Delay '1.4' 3000 0
$camera = New-Call $STATICS 'GetPlayerCameraManager' $true 3050 250
Add-Pin $camera 'PlayerIndex' 'in' 'int' '' $null '0'
Add-Pin $camera 'ReturnValue' 'out' 'object' '' $CAMERA_MANAGER
$whiteOut = New-Call $CAMERA_MANAGER 'StartCameraFade' $false 3300 0
Add-Pin $whiteOut 'self' 'in' 'object' '' $CAMERA_MANAGER
Add-Pin $whiteOut 'FromAlpha' 'in' 'real' 'float' $null '0.0'
Add-Pin $whiteOut 'ToAlpha' 'in' 'real' 'float' $null '1.0'
Add-Pin $whiteOut 'Duration' 'in' 'real' 'float' $null '1.5'
Add-Pin $whiteOut 'Color' 'in' 'struct' '' $LINEAR $WHITE
Add-Pin $whiteOut 'bShouldFadeAudio' 'in' 'bool' '' $null 'false'
Add-Pin $whiteOut 'bHoldWhenFinished' 'in' 'bool' '' $null 'true'
Connect $camera 'ReturnValue' $whiteOut 'self'
$waitWhite = Delay '1.7' 3600 0
# The show's seconds don't count.
$putBack = New-VarSet 'ElapsedTime' $CHAR1 'real' $null 3900 0
(Get-Pin $putBack 'ElapsedTime').Sub = 'double'; (Get-Pin $putBack 'Output_Get').Sub = 'double'
Connect $char 'AsBP Third Person Character 1' $putBack 'self'
Connect (Real 'ClearTime' 3700 250) 'ClearTime' $putBack 'ElapsedTime'
# As the view cuts to the gate: the doors' sound and the light's (setup_gate_sounds.py), 2D, SE Volume x Master Volume.
$SOUND_BASE = "/Script/CoreUObject.Class'/Script/Engine.SoundBase'"
$soundGi = GameInstance 2350 -600
$soundVol = Op 'Multiply' 'Multiply_DoubleDouble' (GiGet $soundGi 'SE Volume' 'real' 'double' 2400 -350) 'SE Volume' (GiGet $soundGi 'Master Volume' 'real' 'double' 2400 -250) 'Master Volume' 2650 -300
function Play2D($asset, [double]$x, [double]$y) {
  $n = New-Call $STATICS 'PlaySound2D' $false $x $y
  Add-Pin $n 'Sound' 'in' 'object' '' $SOUND_BASE
  (Get-Pin $n 'Sound') | Add-Member DefaultObject "/Game/ThirdPerson/Blueprints/Gimmicks/Heaven/$asset.$asset"
  Add-Pin $n 'VolumeMultiplier' 'in' 'real' 'float'
  Add-Pin $n 'PitchMultiplier' 'in' 'real' 'float' $null '1.0'
  Add-Pin $n 'StartTime' 'in' 'real' 'float' $null '0.0'
  Connect $soundVol 'ReturnValue' $n 'VolumeMultiplier'
  return $n
}
$doorSound = Play2D 'S_GateOpen' 2650 -600
$lightSound = Play2D 'S_GateLight' 2950 -600
Connect $soundGi 'then' $doorSound 'execute'
Connect $doorSound 'then' $lightSound 'execute'
Connect $soundGi 'CastFailed' $waitOpen 'execute'
Connect $lightSound 'then' $waitOpen 'execute'
Connect $isPlayer 'then' $started 'execute'
Chain @($started, $startedAt, $char)
Connect $char 'then' $clearTime 'execute'
Chain @($clearTime, $noInput, $toGate, $soundGi)
Chain @($waitOpen, $toPlayer, $waitWalk, $whiteOut, $waitWhite, $putBack)

if ($Secret) {
  # ----- the hidden stages' end: their own achievement, then back to the title -----
  $gi = GameInstance 4200 0
  Connect $putBack 'then' $gi 'execute'
  $clear = Unlock $gi 'ACH_SECRET_CLEAR' 4500 0
  Connect $gi 'then' $clear 'execute'
  $rest = Delay '4.0' 4800 0
  Connect $clear 'then' $rest 'execute'
  $title = OpenLevel 5100 0
  (Get-Pin $title 'LevelName').Default = 'LV_Title'
  Connect $rest 'then' $title 'execute'
} else {# ----- the clear-time achievements -----
$gi = GameInstance 4200 0
Connect $putBack 'then' $gi 'execute'
$clear = Unlock $gi 'ACH_CLEAR' 4500 0
Connect $gi 'then' $clear 'execute'
$noFall = MaybeUnlock $gi (NotBool (GiGet $gi 'RunFell' 'bool' '' 4600 250) 'RunFell' 4800 250) 'ReturnValue' 'ACH_NO_FALL' 5000 0
Connect $clear 'then' $noFall[0] 'execute'
$noFlag = MaybeUnlock $gi (NotBool (GiGet $gi 'RunUsedFlag' 'bool' '' 5400 250) 'RunUsedFlag' 5600 250) 'ReturnValue' 'ACH_NO_FLAG' 5800 0
Connect $noFall[0] 'else' $noFlag[0] 'execute'
Connect $noFall[1] 'then' $noFlag[0] 'execute'
$clean = Both (NotBool (GiGet $gi 'RunTookItem' 'bool' '' 6200 250) 'RunTookItem' 6400 250) 'ReturnValue' `
  (NotBool (GiGet $gi 'RunUsedFlag' 'bool' '' 6200 400) 'RunUsedFlag' 6400 400) 'ReturnValue' 'BooleanAND' 6550 300
$purist = MaybeUnlock $gi $clean 'ReturnValue' 'ACH_PURIST' 6600 0
Connect $noFlag[0] 'else' $purist[0] 'execute'
Connect $noFlag[1] 'then' $purist[0] 'execute'
$fast = Op 'Less' 'Less_DoubleDouble' (Real 'ClearTime' 7200 250) 'ClearTime' (Real 'TargetSeconds' 7200 350) 'TargetSeconds' 7400 250 'bool'
$time = MaybeUnlock $gi $fast 'ReturnValue' 'ACH_TIME' 7400 0

Connect $purist[0] 'else' $time[0] 'execute'
Connect $purist[1] 'then' $time[0] 'execute'

# ----- BP_GoalItem's ending: ShowGameClear, then the best time -----
$pc = CastTo $PC_CLASS 'AsBP Third Person Player Controller' 8000 0
Connect (Controller 7800 250) 'ReturnValue' $pc 'Object'
Connect $time[0] 'else' $pc 'execute'
Connect $time[1] 'then' $pc 'execute'
$show = New-Call $PC_CLASS 'ShowGameClear' $false 8300 0
Add-Pin $show 'self' 'in' 'object' '' $PC_CLASS
Connect $pc 'AsBP Third Person Player Controller' $show 'self'
Connect $pc 'then' $show 'execute'
$load = New-Call $STATICS 'LoadGameFromSlot' $false 8550 0
Add-Pin $load 'SlotName' 'in' 'string' '' $null 'HeightSave'
(Get-Pin $load 'SlotName') | Add-Member -NotePropertyName ConstRef -NotePropertyValue $true
Add-Pin $load 'UserIndex' 'in' 'int' '' $null '0'
Add-Pin $load 'ReturnValue' 'out' 'object' '' $SAVE_BASE
Connect $show 'then' $load 'execute'
$save = CastTo $SAVE_CLASS 'AsBP Height Save' 8850 0
Connect $load 'ReturnValue' $save 'Object'
Connect $load 'then' $save 'execute'
$best = New-VarGet 'SavedBestTime' $SAVE_CLASS 'real' 'double' $null 8900 300
Connect $save 'AsBP Height Save' $best 'self'
$faster = Op 'Less' 'Less_DoubleDouble' (Real 'ClearTime' 8900 450) 'ClearTime' $best 'SavedBestTime' 9100 300 'bool'
$none = Op 'LessEqual' 'LessEqual_DoubleDouble' $best 'SavedBestTime' $null '0.0' 9100 450 'bool'
$record = New-Branch 9350 0
Connect (Both $faster 'ReturnValue' $none 'ReturnValue' 'BooleanOR' 9250 350) 'ReturnValue' $record 'Condition'
Connect $save 'then' $record 'execute'
$setBest = New-VarSet 'SavedBestTime' $SAVE_CLASS 'real' $null 9600 0
(Get-Pin $setBest 'SavedBestTime').Sub = 'double'; (Get-Pin $setBest 'Output_Get').Sub = 'double'
Connect $save 'AsBP Height Save' $setBest 'self'
Connect (Real 'ClearTime' 9400 300) 'ClearTime' $setBest 'SavedBestTime'
Connect $record 'then' $setBest 'execute'
$write = New-Call $STATICS 'SaveGameToSlot' $false 9900 0
Add-Pin $write 'SaveGameObject' 'in' 'object' '' $SAVE_BASE
Add-Pin $write 'SlotName' 'in' 'string' '' $null 'HeightSave'
(Get-Pin $write 'SlotName') | Add-Member -NotePropertyName ConstRef -NotePropertyValue $true
Add-Pin $write 'UserIndex' 'in' 'int' '' $null '0'
Add-Pin $write 'ReturnValue' 'out' 'bool'
Connect $save 'AsBP Height Save' $write 'SaveGameObject'
Connect $setBest 'then' $write 'execute'

}

# ===== Tick =====
$tick = Event 'ReceiveTick' 0 1200
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$going = New-Branch 250 1200
Connect (Bool 'Started' 100 1400) 'Started' $going 'Condition'
Connect $tick 'then' $going 'execute'
$t = Op 'Subtract' 'Subtract_DoubleDouble' (Now 200 1600) 'ReturnValue' (Real 'StartedAt' 200 1700) 'StartedAt' 400 1600
$alpha = New-Call $MATH 'MapRangeClamped' $true 600 1600
Add-Pin $alpha 'Value' 'in' 'real' 'double'
Add-Pin $alpha 'InRangeA' 'in' 'real' 'double' $null '0.0'
Add-Pin $alpha 'InRangeB' 'in' 'real' 'double'
Add-Pin $alpha 'OutRangeA' 'in' 'real' 'double' $null '0.0'
Add-Pin $alpha 'OutRangeB' 'in' 'real' 'double' $null '1.0'
Add-Pin $alpha 'ReturnValue' 'out' 'real' 'double'
Connect $t 'ReturnValue' $alpha 'Value'
Connect (Real 'OpenSeconds' 400 1800) 'OpenSeconds' $alpha 'InRangeB'
# e = 0.5 - 0.5 cos(pi a): slow start, slow stop.
$cos = MathCall 'Cos' @('A') 'real' 'double' 'real' 'double' 1000 1600
Connect (Op 'Multiply' 'Multiply_DoubleDouble' $alpha 'ReturnValue' $null '3.14159265' 850 1600) 'ReturnValue' $cos 'A'
$ease = Op 'Subtract' 'Subtract_DoubleDouble' $null '0.5' (Op 'Multiply' 'Multiply_DoubleDouble' $cos 'ReturnValue' $null '0.5' 1150 1600) 'ReturnValue' 1300 1600
$angle = Times $ease 'ReturnValue' (Real 'OpenAngle' 1300 1750) 'OpenAngle' 1500 1650
$minus = Op 'Multiply' 'Multiply_DoubleDouble' $angle 'ReturnValue' $null '-1.0' 1700 1750
function Turn($hinge, $node, $pin, [double]$x, [double]$y) {
  $rot = New-Call $MATH 'MakeRotator' $true ($x - 200) ($y + 250)
  Add-Pin $rot 'Roll' 'in' 'real' 'float' $null '0.0'
  Add-Pin $rot 'Pitch' 'in' 'real' 'float' $null '0.0'
  Add-Pin $rot 'Yaw' 'in' 'real' 'float'
  Add-Pin $rot 'ReturnValue' 'out' 'struct' '' $ROTATOR
  Connect $node $pin $rot 'Yaw'
  $n = New-Call $SCENE 'K2_SetRelativeRotation' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $SCENE
  Add-Pin $n 'NewRotation' 'in' 'struct' '' $ROTATOR
  Add-Pin $n 'bSweep' 'in' 'bool' '' $null 'false'
  Add-Pin $n 'SweepHitResult' 'out' 'struct' '' $HIT
  Add-Pin $n 'bTeleport' 'in' 'bool' '' $null 'false'
  Connect (Comp $hinge $SCENE ($x - 200) ($y + 150)) $hinge $n 'self'
  Connect $rot 'ReturnValue' $n 'NewRotation'
  return $n
}
$turnL = Turn 'HingeL' $minus 'ReturnValue' 2000 1200
$turnR = Turn 'HingeR' $angle 'ReturnValue' 2300 1200
$glow = New-Call $MESH_COMP 'SetScalarParameterValueOnMaterials' $false 2600 1200
Add-Pin $glow 'self' 'in' 'object' '' $MESH_COMP
Add-Pin $glow 'ParameterName' 'in' 'name' '' $null 'Glow'
(Get-Pin $glow 'ParameterName') | Add-Member -NotePropertyName ConstRef -NotePropertyValue $true
Add-Pin $glow 'ParameterValue' 'in' 'real' 'float'
Connect (Comp 'Veil' $STATIC_MESH 2400 1400) 'Veil' $glow 'self'
Connect (Times $ease 'ReturnValue' (Real 'MaxGlow' 2300 1600) 'MaxGlow' 2450 1550) 'ReturnValue' $glow 'ParameterValue'
$shine = New-Call $LIGHT_COMP 'SetIntensity' $false 2900 1200
Add-Pin $shine 'self' 'in' 'object' '' $LIGHT_COMP
Add-Pin $shine 'NewIntensity' 'in' 'real' 'float'
Connect (Comp 'GateLight' $POINT_LIGHT 2700 1400) 'GateLight' $shine 'self'
Connect (Times $ease 'ReturnValue' (Real 'MaxLight' 2600 1650) 'MaxLight' 2750 1600) 'ReturnValue' $shine 'NewIntensity'
$walking = New-Branch 3200 1200
Connect (Op 'GreaterEqual' 'GreaterEqual_DoubleDouble' $t 'ReturnValue' (Real 'WalkFrom' 2950 1700) 'WalkFrom' 3100 1600 'bool') 'ReturnValue' $walking 'Condition'
$walk = New-Call $PAWN 'AddMovementInput' $false 3500 1200
Add-Pin $walk 'self' 'in' 'object' '' $PAWN
Add-Pin $walk 'WorldDirection' 'in' 'struct' '' $VECTOR
Add-Pin $walk 'ScaleValue' 'in' 'real' 'float' $null '1.0'
Add-Pin $walk 'bForce' 'in' 'bool' '' $null 'true'
Connect (Player 3300 1450) 'ReturnValue' $walk 'self'
$forward = New-Call $ACTOR 'GetActorForwardVector' $true 3300 1550
Add-Pin $forward 'self' 'in' 'object' '' $ACTOR
Add-Pin $forward 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $forward 'ReturnValue' $walk 'WorldDirection'
Connect $going 'then' $turnL 'execute'
Chain @($turnL, $turnR, $glow, $shine, $walking)
Connect $walking 'then' $walk 'execute'
Write-Graph $(if ($Secret) { 'BP_SecretGate_EventGraph.txt' } else { 'BP_HeavenGate_EventGraph.txt' })
