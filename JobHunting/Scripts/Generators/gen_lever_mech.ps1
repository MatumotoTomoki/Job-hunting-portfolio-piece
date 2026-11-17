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
Connect $stamp 'then' $swing 'Move'
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
Chain @($hold, $toCamera, $watch, $toPlayer, $back, $free)
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
Connect $wait 'then' $swingBack 'Move'
Connect $swingBack 'then' $free2 'execute'
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
Write-Graph 'BP_Mechanism_EventGraph.txt'

