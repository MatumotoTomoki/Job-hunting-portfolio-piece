param([string]$OutDir)
# Paste text for the area groundwork (components and variables from setup_area_foundation.py):
#   BP_Lever_EventGraph.txt      touched once: Pulled, the handle swings over; with a ShowCamera the view cuts to it for
#                                ShowSeconds (the player held still) and back.
#   BP_Mechanism_EventGraph.txt  Begin Play remembers where it stands; on Tick, once Lever is Pulled, it eases from
#                                there by MoveOffset and turns Body by Turn, StartDelay to StartDelay + Duration; then Done.
#   BP_AreaExit_EventGraph.txt   stepping in: the item effects saved, ChangingArea, black, NextLevel.
#   BP_AreaStart_EventGraph.txt  Begin Play after an area exit: ChangingArea cleared, the screen clears, effects back.
if (-not $OutDir) { throw 'OutDir is required' }
$cageGen = Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_hell_cage.ps1'
$defs = Get-Content -LiteralPath $cageGen -Encoding UTF8 | Select-Object -Skip 10 -First 172
. ([ScriptBlock]::Create(($defs -join "`n")))

$SCENE = "/Script/CoreUObject.Class'/Script/Engine.SceneComponent'"
$STATIC_MESH = "/Script/CoreUObject.Class'/Script/Engine.StaticMeshComponent'"
$LEVER_CLASS = "/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPerson/Blueprints/Gimmicks/Area/BP_Lever.BP_Lever_C'"
$PULLED_TO = '-40.000000, 0.000000, 0.000000'   # Pitch, Yaw, Roll: setup_area_foundation.py leans it to +40
$PULLED_FROM = '40.000000, 0.000000, 0.000000'  # back where it started
$PIVOT_AT = '0.000000,0.000000,50.000000'
$BLEND = '1.0'

function Event($name, $x, $y) {
  $n = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$ACTOR`",MemberName=`"$name`")", 'bOverrideFunction=True') $x $y
  Add-Pin $n 'then' 'out' 'exec'
  return $n
}
function SetSelf($name, $cat, $value, $x, $y) {
  $n = New-VarSet $name $null $cat $null $x $y
  if ($null -ne $value) { (Get-Pin $n $name).Default = $value }
  return $n
}
function InputCall($func, $x, $y) {
  $n = New-Call $ACTOR $func $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR
  Add-Pin $n 'PlayerController' 'in' 'object' '' $CONTROLLER
  Connect (Player ($x - 200) ($y + 200)) 'ReturnValue' $n 'self'
  Connect (Controller ($x - 200) ($y + 300)) 'ReturnValue' $n 'PlayerController'
  return $n
}
function PlayerIn($boxName, $x, $y) {
  $n = New-Call $PRIMITIVE 'IsOverlappingActor' $true $x $y
  Add-Pin $n 'self' 'in' 'object' '' $PRIMITIVE
  Add-Pin $n 'Other' 'in' 'object' '' $ACTOR
  Add-Pin $n 'ReturnValue' 'out' 'bool'
  Connect (New-VarGet $boxName $null 'object' '' $BOX ($x - 200) $y) $boxName $n 'self'
  Connect (Player ($x - 250) ($y + 100)) 'ReturnValue' $n 'Other'
  return $n
}
function ViewTarget($x, $y) {
  $n = New-Call $CONTROLLER 'SetViewTargetWithBlend' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $CONTROLLER
  Add-Pin $n 'NewViewTarget' 'in' 'object' '' $ACTOR
  Add-Pin $n 'BlendTime' 'in' 'real' 'float' $null $BLEND
  Connect (Controller ($x - 250) ($y + 200)) 'ReturnValue' $n 'self'
  return $n
}
function Real($name, $x, $y) { New-VarGet $name $null 'real' 'double' $null $x $y }
function Vec($name, $x, $y) { New-VarGet $name $null 'struct' '' $VECTOR $x $y }
# As gen_hell_cage's, plus DefaultObject (a class pin's chosen class: the camera shakes).
function Format-Pin($p) {
  $obj = if ($p.Obj) { "`"$($p.Obj)`"" } else { 'None' }
  $ref = if ($p.PSObject.Properties['ConstRef'] -and $p.ConstRef) { 'True' } else { 'False' }
  $s = "PinId=$($p.Id),PinName=`"$($p.Name)`","
  if ($p.Dir -eq 'out') { $s += 'Direction="EGPD_Output",' }
  $s += "PinType.PinCategory=`"$($p.Cat)`",PinType.PinSubCategory=`"$($p.Sub)`",PinType.PinSubCategoryObject=$obj,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=$($p.Container),PinType.bIsReference=$ref,PinType.bIsConst=$ref,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,"
  if ($null -ne $p.Default) { $s += "DefaultValue=`"$($p.Default)`"," }
  if ($p.PSObject.Properties['DefaultObject']) { $s += "DefaultObject=`"$($p.DefaultObject)`"," }
  if ($p.Links.Count) { $s += 'LinkedTo=(' + (($p.Links | ForEach-Object { "$_," }) -join '') + '),' }
  $s += 'PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,'
  return "   CustomProperties Pin ($s)"
}
# Sounds and effects (setup_lever_sounds.py, 2026-11-20).
$AUDIO_COMP = "/Script/CoreUObject.Class'/Script/Engine.AudioComponent'"
$EMITTER = "/Script/CoreUObject.Class'/Script/Effekseer.EffekseerEmitterComponent'"
$ACTOR_COMP = "/Script/CoreUObject.Class'/Script/Engine.ActorComponent'"
function SoundPlay($name, $x, $y) {
  $n = New-Call $AUDIO_COMP 'Play' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $AUDIO_COMP
  Add-Pin $n 'StartTime' 'in' 'real' 'float' $null '0.0'
  Connect (New-VarGet $name $null 'object' '' $AUDIO_COMP ($x - 200) ($y + 200)) $name $n 'self'
  return $n
}
function FxPlay($name, $x, $y) {
  $n = New-Call $ACTOR_COMP 'Activate' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR_COMP
  Add-Pin $n 'bReset' 'in' 'bool' '' $null 'true'
  Connect (New-VarGet $name $null 'object' '' $EMITTER ($x - 200) ($y + 200)) $name $n 'self'
  return $n
}
# Begin Play part: the named sounds at SE Volume x Master Volume. Returns (first, last).
function SoundVolumes([string[]]$names, $x, $y) {
  $cast = GameInstance $x $y
  $vol = New-Operator 'Multiply' 'Multiply_DoubleDouble' 'real' 'double' 'real' ($x + 250) ($y + 250)
  (Get-Pin $vol 'ReturnValue').Sub = 'double'
  Connect (GiGet $cast 'SE Volume' 'real' 'double' ($x + 50) ($y + 250)) 'SE Volume' $vol 'A'
  Connect (GiGet $cast 'Master Volume' 'real' 'double' ($x + 50) ($y + 350)) 'Master Volume' $vol 'B'
  $prev = $cast; $vx = $x + 350
  foreach ($name in $names) {
    $v = New-Call $AUDIO_COMP 'SetVolumeMultiplier' $false $vx $y
    Add-Pin $v 'self' 'in' 'object' '' $AUDIO_COMP
    Add-Pin $v 'NewVolumeMultiplier' 'in' 'real' 'float'
    Connect (New-VarGet $name $null 'object' '' $AUDIO_COMP ($vx - 200) ($y + 200)) $name $v 'self'
    Connect $vol 'ReturnValue' $v 'NewVolumeMultiplier'
    Connect $prev 'then' $v 'execute'
    $prev = $v; $vx += 300
  }
  return @($cast, $prev)
}

# ===== BP_Lever ============================================================================================
# Touched while not Pulled: Pulled, PulledAt = now, the handle swings over. Then, side by side:
#   0: with a ShowCamera, the view cuts to it for ShowSeconds, the player held still, and back.
#   1: with a ResetAfter, after that long the handle swings back and Pulled clears: it can be pulled again.
Reset-Graph 100
function Now($x, $y) {
  $n = New-Call $SYSTEM 'GetGameTimeInSeconds' $true $x $y
  Add-Pin $n 'ReturnValue' 'out' 'real' 'double'
  return $n
}
function Swing($rotation, $x, $y) {
  $n = New-Call $SYSTEM 'MoveComponentTo' $false $x $y
  $n.Props = @('bWantsEnumToExecExpansion=True') + $n.Props
  $n.Pins.Clear()
  Add-Pin $n 'Move' 'in' 'exec'
  Add-Pin $n 'then' 'out' 'exec'
  Add-Pin $n 'Component' 'in' 'object' '' $SCENE
  Add-Pin $n 'TargetRelativeLocation' 'in' 'struct' '' $VECTOR $PIVOT_AT
  Add-Pin $n 'TargetRelativeRotation' 'in' 'struct' '' $ROTATOR $rotation
  Add-Pin $n 'bEaseOut' 'in' 'bool' '' $null 'true'
  Add-Pin $n 'bEaseIn' 'in' 'bool' '' $null 'true'
  Add-Pin $n 'OverTime' 'in' 'real' 'float' $null '0.4'
  Add-Pin $n 'bForceShortestRotationPath' 'in' 'bool' '' $null 'false'
  Connect (New-VarGet 'Pivot' $null 'object' '' $SCENE ($x - 200) ($y + 250)) 'Pivot' $n 'Component'
  return $n
}
$touch = Event 'ReceiveActorBeginOverlap' 0 0
Add-Pin $touch 'OtherActor' 'out' 'object' '' $ACTOR
$once = New-Branch 300 0
Connect (New-VarGet 'Pulled' $null 'bool' '' $null 150 200) 'Pulled' $once 'Condition'
$isPlayer = New-Branch 550 0
Connect (PlayerIn 'Trigger' 450 250) 'ReturnValue' $isPlayer 'Condition'
$pulled = SetSelf 'Pulled' 'bool' 'true' 800 0
$stamp = New-VarSet 'PulledAt' $null 'real' $null 1050 0
(Get-Pin $stamp 'PulledAt').Sub = 'double'; (Get-Pin $stamp 'Output_Get').Sub = 'double'
Connect (Now 900 250) 'ReturnValue' $stamp 'PulledAt'
$swing = Swing $PULLED_TO 1350 0
$both = New-Node '/Script/BlueprintGraph.K2Node_ExecutionSequence' @() 1750 0
Add-Pin $both 'execute' 'in' 'exec'
Add-Pin $both 'then_0' 'out' 'exec'
Add-Pin $both 'then_1' 'out' 'exec'
Connect $touch 'then' $once 'execute'
Connect $once 'else' $isPlayer 'execute'
Connect $isPlayer 'then' $pulled 'execute'
Connect $pulled 'then' $stamp 'execute'
# "kacha... ga-kon" and the sparks as it lands (they wait 0.37 s themselves).
$pullSound = SoundPlay 'PullSound' 1050 (-400)
$pullFx = FxPlay 'PullFx' 1350 (-400)
Connect $stamp 'then' $pullSound 'execute'
Connect $pullSound 'then' $pullFx 'execute'
Connect $pullFx 'then' $swing 'Move'
Connect $swing 'then' $both 'execute'
# 0: the show.
$hasCamera = New-Branch 2050 0
$valid = New-IsValid 1900 250
Connect (New-VarGet 'ShowCamera' $null 'object' '' $ACTOR 1700 300) 'ShowCamera' $valid 'Object'
Connect $valid 'ReturnValue' $hasCamera 'Condition'
$hold = InputCall 'DisableInput' 2350 0
$toCamera = ViewTarget 2650 0
Connect (New-VarGet 'ShowCamera' $null 'object' '' $ACTOR 2450 350) 'ShowCamera' $toCamera 'NewViewTarget'
$watch = Delay '0.0' 3000 0
Connect (Real 'ShowSeconds' 2850 250) 'ShowSeconds' $watch 'Duration'
$toPlayer = ViewTarget 3300 0
Connect (Player 3100 350) 'ReturnValue' $toPlayer 'NewViewTarget'
$back = Delay $BLEND 3650 0
$free = InputCall 'EnableInput' 3950 0
Connect $both 'then_0' $hasCamera 'execute'
Connect $hasCamera 'then' $hold 'execute'
# Silence while the show plays (setup_mech_show_mute.py, 2026-11-20): ShowMix turns every sound but the machine's to 0
# as the view cuts away and is popped as it comes back. The controller's input is off too, so the pause menu can't
# open while the game is silent (that left the BGM dead after the gear arrival).
$SOUND_MIX = "/Script/CoreUObject.Class'/Script/Engine.SoundMix'"
function Sound-Mix($func, [double]$x, [double]$y) {
  $n = New-Call $STATICS $func $false $x $y
  Add-Pin $n 'InSoundMixModifier' 'in' 'object' '' $SOUND_MIX
  Connect (New-VarGet 'ShowMix' $null 'object' '' $SOUND_MIX ($x - 200) ($y + 200)) 'ShowMix' $n 'InSoundMixModifier'
  return $n
}
function Controller-Input($func, [double]$x, [double]$y) {
  $n = New-Call $ACTOR $func $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR
  Add-Pin $n 'PlayerController' 'in' 'object' '' $CONTROLLER
  Connect (Controller ($x - 200) ($y + 200)) 'ReturnValue' $n 'self'
  Connect (Controller ($x - 200) ($y + 300)) 'ReturnValue' $n 'PlayerController'
  return $n
}
$freeze = Controller-Input 'DisableInput' 2350 (-350)
$hush = Sound-Mix 'PushSoundMixModifier' 2650 (-350)
$sound = Sound-Mix 'PopSoundMixModifier' 3300 (-350)
$unfreeze = Controller-Input 'EnableInput' 4250 0
Chain @($hold, $freeze, $hush, $toCamera, $watch, $toPlayer, $sound, $back, $free, $unfreeze)
# 1: springing back.
$resets = New-Branch 2050 700
$positive = New-Operator 'Greater' 'Greater_DoubleDouble' 'real' 'double' 'bool' 1900 900
Connect (Real 'ResetAfter' 1700 900) 'ResetAfter' $positive 'A'
(Get-Pin $positive 'B').Default = '0.0'
Connect $positive 'ReturnValue' $resets 'Condition'
$wait = Delay '0.0' 2350 700
Connect (Real 'ResetAfter' 2200 950) 'ResetAfter' $wait 'Duration'
$swingBack = Swing $PULLED_FROM 2700 700
$free2 = SetSelf 'Pulled' 'bool' 'false' 3100 700
Connect $both 'then_1' $resets 'execute'
Connect $resets 'then' $wait 'execute'
$returnSound = SoundPlay 'ReturnSound' 2500 450
Connect $wait 'then' $returnSound 'execute'
Connect $returnSound 'then' $swingBack 'Move'
Connect $swingBack 'then' $free2 'execute'
# Begin Play: the sounds' volume.
$leverBegin = Event 'ReceiveBeginPlay' 0 (-900)
$leverVol = SoundVolumes @('PullSound', 'ReturnSound') 300 (-900)
Connect $leverBegin 'then' $leverVol[0] 'execute'
Write-Graph 'BP_Lever_EventGraph.txt'

# ===== BP_Mechanism ========================================================================================
# Begin Play: StartLocation where it stands, EndLocation MoveOffset away. Every Tick, once its Lever has been pulled
# (PulledAt > 0), t = seconds since then:
#   out  = 0..1 over StartDelay .. StartDelay + Duration
#   back = 0..1 over that + ReturnAfter .. + ReturnSeconds, only when Returns
#   eased (out - back) places it between StartLocation and EndLocation and turns Body by that much of Turn.
# A lever pulled again starts it over.
Reset-Graph 100
$begin = Event 'ReceiveBeginPlay' 0 0
$here = New-VarSet 'StartLocation' $null 'struct' $VECTOR 300 0
$where = New-Call $ACTOR 'K2_GetActorLocation' $true 100 200
Add-Pin $where 'self' 'in' 'object' '' $ACTOR
Add-Pin $where 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $where 'ReturnValue' $here 'StartLocation'
$there = New-VarSet 'EndLocation' $null 'struct' $VECTOR 650 0
$sum = New-Operator 'Add' 'Add_VectorVector' 'struct' '' 'struct' 500 200
foreach ($pin in 'A', 'B', 'ReturnValue') { (Get-Pin $sum $pin).Obj = $VECTOR }
Connect (Vec 'StartLocation' 300 200) 'StartLocation' $sum 'A'
Connect (Vec 'MoveOffset' 300 300) 'MoveOffset' $sum 'B'
Connect $sum 'ReturnValue' $there 'EndLocation'
Connect $begin 'then' $here 'execute'
Connect $here 'then' $there 'execute'

function Add2($a, $aPin, $b, $bPin, $x, $y) {
  $n = New-Operator 'Add' 'Add_DoubleDouble' 'real' 'double' 'real' $x $y
  (Get-Pin $n 'ReturnValue').Sub = 'double'
  Connect $a $aPin $n 'A'
  Connect $b $bPin $n 'B'
  return $n
}
function Range01($value, $valuePin, $from, $fromPin, $to, $toPin, $x, $y) {
  $n = New-Call $MATH 'MapRangeClamped' $true $x $y
  Add-Pin $n 'Value' 'in' 'real' 'double'
  Add-Pin $n 'InRangeA' 'in' 'real' 'double'
  Add-Pin $n 'InRangeB' 'in' 'real' 'double'
  Add-Pin $n 'OutRangeA' 'in' 'real' 'double' $null '0.0'
  Add-Pin $n 'OutRangeB' 'in' 'real' 'double' $null '1.0'
  Add-Pin $n 'ReturnValue' 'out' 'real' 'double'
  Connect $value $valuePin $n 'Value'
  Connect $from $fromPin $n 'InRangeA'
  Connect $to $toPin $n 'InRangeB'
  return $n
}
function LeverGet($name, $x, $y) {
  $n = New-VarGet $name $LEVER_CLASS 'real' 'double' $null $x $y
  Connect (New-VarGet 'Lever' $null 'object' '' $LEVER_CLASS ($x - 200) ($y + 50)) 'Lever' $n 'self'
  return $n
}

$tick = Event 'ReceiveTick' 0 600
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$hasLever = New-Branch 300 600
$leverValid = New-IsValid 150 850
Connect (New-VarGet 'Lever' $null 'object' '' $LEVER_CLASS -50 850) 'Lever' $leverValid 'Object'
Connect $leverValid 'ReturnValue' $hasLever 'Condition'
$wasPulled = New-Branch 600 600
$ever = New-Operator 'Greater' 'Greater_DoubleDouble' 'real' 'double' 'bool' 450 850
Connect (LeverGet 'PulledAt' 250 950) 'PulledAt' $ever 'A'
(Get-Pin $ever 'B').Default = '0.0'
Connect $ever 'ReturnValue' $wasPulled 'Condition'
# t: seconds since the pull.
$since = New-Operator 'Subtract' 'Subtract_DoubleDouble' 'real' 'double' 'real' 900 1100
(Get-Pin $since 'ReturnValue').Sub = 'double'
Connect (Now 700 1100) 'ReturnValue' $since 'A'
Connect (LeverGet 'PulledAt' 700 1200) 'PulledAt' $since 'B'
$startDelay = Real 'StartDelay' 700 1350
$outEnd = Add2 $startDelay 'StartDelay' (Real 'Duration' 700 1450) 'Duration' 900 1400
$out = Range01 $since 'ReturnValue' $startDelay 'StartDelay' $outEnd 'ReturnValue' 1150 1100
$backStart = Add2 $outEnd 'ReturnValue' (Real 'ReturnAfter' 900 1550) 'ReturnAfter' 1100 1500
$backEnd = Add2 $backStart 'ReturnValue' (Real 'ReturnSeconds' 1100 1650) 'ReturnSeconds' 1300 1600
$back = Range01 $since 'ReturnValue' $backStart 'ReturnValue' $backEnd 'ReturnValue' 1550 1400
$backUsed = New-Call $MATH 'SelectFloat' $true 1800 1400
Add-Pin $backUsed 'A' 'in' 'real' 'double'
Add-Pin $backUsed 'B' 'in' 'real' 'double' $null '0.0'
Add-Pin $backUsed 'bPickA' 'in' 'bool'
Add-Pin $backUsed 'ReturnValue' 'out' 'real' 'double'
Connect $back 'ReturnValue' $backUsed 'A'
Connect (New-VarGet 'Returns' $null 'bool' '' $null 1600 1600) 'Returns' $backUsed 'bPickA'
$alpha = New-Operator 'Subtract' 'Subtract_DoubleDouble' 'real' 'double' 'real' 2050 1200
(Get-Pin $alpha 'ReturnValue').Sub = 'double'
Connect $out 'ReturnValue' $alpha 'A'
Connect $backUsed 'ReturnValue' $alpha 'B'
$eased = New-Call $MATH 'FInterpEaseInOut' $true 2250 1100
Add-Pin $eased 'A' 'in' 'real' 'double' $null '0.0'
Add-Pin $eased 'B' 'in' 'real' 'double' $null '1.0'
Add-Pin $eased 'Alpha' 'in' 'real' 'double'
Add-Pin $eased 'Exponent' 'in' 'real' 'double' $null '2.0'
Add-Pin $eased 'ReturnValue' 'out' 'real' 'double'
Connect $alpha 'ReturnValue' $eased 'Alpha'
$lerp = New-Call $MATH 'VLerp' $true 2500 900
Add-Pin $lerp 'A' 'in' 'struct' '' $VECTOR
Add-Pin $lerp 'B' 'in' 'struct' '' $VECTOR
Add-Pin $lerp 'Alpha' 'in' 'real' 'float'
Add-Pin $lerp 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect (Vec 'StartLocation' 2300 850) 'StartLocation' $lerp 'A'
Connect (Vec 'EndLocation' 2300 950) 'EndLocation' $lerp 'B'
Connect $eased 'ReturnValue' $lerp 'Alpha'
$move = New-Call $ACTOR 'K2_SetActorLocation' $false 2800 600
Add-Pin $move 'self' 'in' 'object' '' $ACTOR
Add-Pin $move 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $move 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $move 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $move 'bTeleport' 'in' 'bool' '' $null 'false'
Add-Pin $move 'ReturnValue' 'out' 'bool'
Connect $lerp 'ReturnValue' $move 'NewLocation'
$angle = New-Call $MATH 'RLerp' $true 2800 1100
Add-Pin $angle 'A' 'in' 'struct' '' $ROTATOR '0, 0, 0'
Add-Pin $angle 'B' 'in' 'struct' '' $ROTATOR
Add-Pin $angle 'Alpha' 'in' 'real' 'float'
Add-Pin $angle 'bShortestPath' 'in' 'bool' '' $null 'false'
Add-Pin $angle 'ReturnValue' 'out' 'struct' '' $ROTATOR
Connect (New-VarGet 'Turn' $null 'struct' '' $ROTATOR 2600 1250) 'Turn' $angle 'B'
Connect $eased 'ReturnValue' $angle 'Alpha'
$turn = New-Call $SCENE 'K2_SetRelativeRotation' $false 3200 600
Add-Pin $turn 'self' 'in' 'object' '' $SCENE
Add-Pin $turn 'NewRotation' 'in' 'struct' '' $ROTATOR
Add-Pin $turn 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $turn 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $turn 'bTeleport' 'in' 'bool' '' $null 'false'
Connect (New-VarGet 'Body' $null 'object' '' $STATIC_MESH 3000 850) 'Body' $turn 'self'
Connect $angle 'ReturnValue' $turn 'NewRotation'
Connect $tick 'then' $hasLever 'execute'
Connect $hasLever 'then' $wasPulled 'execute'
Connect $wasPulled 'then' $move 'execute'
Connect $move 'then' $turn 'execute'
# The rumble while it moves: moving = the eased alpha changed since the last tick; it fades in as it starts moving
# and out as it stops (WasMoving remembers which).
$delta = New-Operator 'Subtract' 'Subtract_DoubleDouble' 'real' 'double' 'real' 3400 1100
(Get-Pin $delta 'ReturnValue').Sub = 'double'
Connect $eased 'ReturnValue' $delta 'A'
Connect (Real 'LastAlpha' 3200 1200) 'LastAlpha' $delta 'B'
$size = New-Call $MATH 'Abs' $true 3600 1100
Add-Pin $size 'A' 'in' 'real' 'double'
Add-Pin $size 'ReturnValue' 'out' 'real' 'double'
Connect $delta 'ReturnValue' $size 'A'
$movingNow = New-Operator 'Greater' 'Greater_DoubleDouble' 'real' 'double' 'bool' 3800 1100
Connect $size 'ReturnValue' $movingNow 'A'
(Get-Pin $movingNow 'B').Default = '0.00001'
# (LastAlpha is set at the very end: the branch reads it through the pure nodes when it runs, so setting it first
# made every tick look still.)
$keepAlpha = New-VarSet 'LastAlpha' $null 'real' $null 5700 600
(Get-Pin $keepAlpha 'LastAlpha').Sub = 'double'; (Get-Pin $keepAlpha 'Output_Get').Sub = 'double'
Connect $eased 'ReturnValue' $keepAlpha 'LastAlpha'
$isMoving = New-Branch 3800 600
Connect $movingNow 'ReturnValue' $isMoving 'Condition'
Connect $turn 'then' $isMoving 'execute'
$wasMoving = New-Branch 4100 400
Connect (New-VarGet 'WasMoving' $null 'bool' '' $null 3950 300) 'WasMoving' $wasMoving 'Condition'
$wasMoving2 = New-Branch 4100 800
Connect (New-VarGet 'WasMoving' $null 'bool' '' $null 3950 1000) 'WasMoving' $wasMoving2 'Condition'
Connect $isMoving 'then' $wasMoving 'execute'
Connect $isMoving 'else' $wasMoving2 'execute'
$fadeIn = New-Call $AUDIO_COMP 'FadeIn' $false 4400 400
Add-Pin $fadeIn 'self' 'in' 'object' '' $AUDIO_COMP
Add-Pin $fadeIn 'FadeInDuration' 'in' 'real' 'float' $null '0.3'
Add-Pin $fadeIn 'FadeVolumeLevel' 'in' 'real' 'float' $null '1.0'
Add-Pin $fadeIn 'StartTime' 'in' 'real' 'float' $null '0.0'
Connect (New-VarGet 'MoveSound' $null 'object' '' $AUDIO_COMP 4200 550) 'MoveSound' $fadeIn 'self'
$startMoving = SetSelf 'WasMoving' 'bool' 'true' 4750 400
Connect $wasMoving 'else' $fadeIn 'execute'
Connect $fadeIn 'then' $startMoving 'execute'
$fadeOut = New-Call $AUDIO_COMP 'FadeOut' $false 4400 800
Add-Pin $fadeOut 'self' 'in' 'object' '' $AUDIO_COMP
Add-Pin $fadeOut 'FadeOutDuration' 'in' 'real' 'float' $null '0.6'
Add-Pin $fadeOut 'FadeVolumeLevel' 'in' 'real' 'float' $null '0.0'
Connect (New-VarGet 'MoveSound' $null 'object' '' $AUDIO_COMP 4200 950) 'MoveSound' $fadeOut 'self'
$stopMoving = SetSelf 'WasMoving' 'bool' 'false' 4750 800
Connect $wasMoving2 'then' $fadeOut 'execute'
# "ga-kon" as it comes to rest.
$stopSound = SoundPlay 'StopSound' 5050 800
Connect $fadeOut 'then' $stopSound 'execute'
# Weight (setup_mech_weight.py, 2026-11-20): dust while it moves, a dust burst and a knock of the camera as it stops,
# and while it moves a small rumble shake - at most one every 0.45 s from all parts together (GI MechShakeAt; a gap
# over 1 s means the clock started again in a new level, so it may shake).
$SHAKE_BASE = "/Script/CoreUObject.Class'/Script/Engine.CameraShakeBase'"
function Shake($name, $inner, $outer, [double]$x, [double]$y) {
  $n = New-Call $STATICS 'PlayWorldCameraShake' $false $x $y
  Add-Pin $n 'Shake' 'in' 'class' '' $SHAKE_BASE
  (Get-Pin $n 'Shake') | Add-Member -NotePropertyName DefaultObject -NotePropertyValue "/Game/ThirdPerson/Blueprints/Gimmicks/Area/$name.${name}_C"
  Add-Pin $n 'Epicenter' 'in' 'struct' '' $VECTOR
  Add-Pin $n 'InnerRadius' 'in' 'real' 'float' $null $inner
  Add-Pin $n 'OuterRadius' 'in' 'real' 'float' $null $outer
  Add-Pin $n 'Falloff' 'in' 'real' 'float' $null '1.0'
  Add-Pin $n 'bOrientShakeTowardsEpicenter' 'in' 'bool' '' $null 'false'
  $at = New-Call $ACTOR 'K2_GetActorLocation' $true ($x - 200) ($y + 250)
  Add-Pin $at 'self' 'in' 'object' '' $ACTOR
  Add-Pin $at 'ReturnValue' 'out' 'struct' '' $VECTOR
  Connect $at 'ReturnValue' $n 'Epicenter'
  return $n
}
function FxStop($name, [double]$x, [double]$y) {
  $n = New-Call $ACTOR_COMP 'Deactivate' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR_COMP
  Connect (New-VarGet $name $null 'object' '' $EMITTER ($x - 200) ($y + 200)) $name $n 'self'
  return $n
}
# Starting: the dust begins.
$dustOn = FxPlay 'MoveFx' 5050 400
Connect $startMoving 'then' $dustOn 'execute'
Connect $dustOn 'then' $keepAlpha 'execute'
# Stopping: dust off, the thud's dust and shake.
$dustOff = FxStop 'MoveFx' 5650 800
$thudFx = FxPlay 'StopFx' 5950 800
$thudShake = Shake 'CS_MechThud' '1500.0' '5000.0' 6250 800
$stopMoving.X = 6650
Connect $stopSound 'then' $dustOff 'execute'
Connect $dustOff 'then' $thudFx 'execute'
Connect $thudFx 'then' $thudShake 'execute'
Connect $thudShake 'then' $stopMoving 'execute'
Connect $stopMoving 'then' $keepAlpha 'execute'
# Still moving: the shared rumble shake.
$shakeCast = GameInstance 4500 (-200)
Connect $wasMoving 'then' $shakeCast 'execute'
$gap = New-Operator 'Subtract' 'Subtract_DoubleDouble' 'real' 'double' 'real' 4700 (-450)
(Get-Pin $gap 'ReturnValue').Sub = 'double'
Connect (GiGet $shakeCast 'MechShakeAt' 'real' 'double' 4500 (-500)) 'MechShakeAt' $gap 'A'
Connect (Now 4500 (-400)) 'ReturnValue' $gap 'B'
$waiting = New-Call $MATH 'InRange_FloatFloat' $true 4900 (-450)
Add-Pin $waiting 'Value' 'in' 'real' 'double'
Add-Pin $waiting 'Min' 'in' 'real' 'double' $null '0.0'
Add-Pin $waiting 'Max' 'in' 'real' 'double' $null '1.0'
Add-Pin $waiting 'InclusiveMin' 'in' 'bool' '' $null 'false'
Add-Pin $waiting 'InclusiveMax' 'in' 'bool' '' $null 'true'
Add-Pin $waiting 'ReturnValue' 'out' 'bool'
Connect $gap 'ReturnValue' $waiting 'Value'
$mayShake = New-Branch 4800 (-200)
Connect $waiting 'ReturnValue' $mayShake 'Condition'
Connect $shakeCast 'then' $mayShake 'execute'
Connect $shakeCast 'CastFailed' $keepAlpha 'execute'
$rumbleShake = Shake 'CS_MechRumble' '2000.0' '6000.0' 5100 (-200)
$nextShake = GiSet $shakeCast 'MechShakeAt' 'real' 'double' 5450 (-200)
$later = New-Operator 'Add' 'Add_DoubleDouble' 'real' 'double' 'real' 5300 (-400)
(Get-Pin $later 'ReturnValue').Sub = 'double'
Connect (Now 5100 (-450)) 'ReturnValue' $later 'A'
(Get-Pin $later 'B').Default = '0.45'
Connect $later 'ReturnValue' $nextShake 'MechShakeAt'
Connect $mayShake 'else' $rumbleShake 'execute'
Connect $rumbleShake 'then' $nextShake 'execute'
Connect $nextShake 'then' $keepAlpha 'execute'
Connect $mayShake 'then' $keepAlpha 'execute'
# Not moving and was not: nothing but remembering.
Connect $wasMoving2 'else' $keepAlpha 'execute'
# Begin Play: the sounds' volume.
$mechVol = SoundVolumes @('MoveSound', 'StopSound') 950 0
Connect $there 'then' $mechVol[0] 'execute'
Write-Graph 'BP_Mechanism_EventGraph.txt'

# ===== BP_AreaExit =========================================================================================
Reset-Graph 100
$touch = Event 'ReceiveActorBeginOverlap' 0 0
Add-Pin $touch 'OtherActor' 'out' 'object' '' $ACTOR
$once = New-Branch 300 0
Connect (New-VarGet 'Leaving' $null 'bool' '' $null 150 200) 'Leaving' $once 'Condition'
$isPlayer = New-Branch 550 0
Connect (PlayerIn 'Area' 450 250) 'ReturnValue' $isPlayer 'Condition'
$leaving = SetSelf 'Leaving' 'bool' 'true' 800 0
$noInput = InputCall 'DisableInput' 1050 0
$cast = GameInstance 1550 0
$saved = SaveStats $cast 1850 0
$moving = GiSet $cast 'ChangingArea' 'bool' '' 3050 0 'true'
$dark = Fade '0.0' '1.0' '0.6' 'true' 3300 0
$wait = Delay '0.6' 3800 0
$open = OpenLevel 4050 0
Connect (New-VarGet 'NextLevel' $null 'name' '' $null 3850 200) 'NextLevel' $open 'LevelName'
Connect $touch 'then' $once 'execute'
Connect $once 'else' $isPlayer 'execute'
Connect $isPlayer 'then' $leaving 'execute'
Chain @($leaving, $noInput, $cast)
Connect $cast 'then' $saved[0] 'execute'
Chain @($saved[1], $moving, $dark, $wait, $open)
Write-Graph 'BP_AreaExit_EventGraph.txt'

# ===== BP_AreaStart ========================================================================================
# Begin Play: this is the area being played (AreaLevel, and AreaCoinTotal from AreaCoins, for the star coin counter);
# then, arriving through an area exit, the screen clears and the item effects come back.
Reset-Graph 100
function LevelName([double]$x, [double]$y) {
  $n = New-Call $STATICS 'GetCurrentLevelName' $false $x $y
  Add-Pin $n 'bRemovePrefixString' 'in' 'bool' '' $null 'true'
  Add-Pin $n 'ReturnValue' 'out' 'string'
  return $n
}
$begin = Event 'ReceiveBeginPlay' 0 0
$level = LevelName 250 0
$cast = GameInstance 650 0
$here = GiSet $cast 'AreaLevel' 'name' '' 900 0
$asName = New-Call $STRINGS 'Conv_StringToName' $true 650 300
Add-Pin $asName 'InString' 'in' 'string'
(Get-Pin $asName 'InString') | Add-Member -NotePropertyName ConstRef -NotePropertyValue $true
Add-Pin $asName 'ReturnValue' 'out' 'name'
Connect $level 'ReturnValue' $asName 'InString'
Connect $asName 'ReturnValue' $here 'AreaLevel'
$total = GiSet $cast 'AreaCoinTotal' 'int' '' 1200 0
Connect (New-VarGet 'AreaCoins' $null 'int' '' $null 1000 300) 'AreaCoins' $total 'AreaCoinTotal'
$arriving = New-Branch 1500 0
Connect (GiGet $cast 'ChangingArea' 'bool' '' 1350 200) 'ChangingArea' $arriving 'Condition'
$arrived = GiSet $cast 'ChangingArea' 'bool' '' 1750 0 'false'
$clear = Fade '1.0' '0.0' '1.0' 'false' 2000 0
# A moment for the player to be set up first.
$wait = Delay '0.1' 2500 0
$restore = RestoreStats $cast 2750 0
Connect $begin 'then' $level 'execute'
Chain @($level, $cast)
Connect $cast 'then' $here 'execute'
Chain @($here, $total, $arriving)
Connect $arriving 'then' $arrived 'execute'
Chain @($arrived, $clear, $wait)
Connect $wait 'then' $restore[0] 'execute'
Write-Graph 'BP_AreaStart_EventGraph.txt'