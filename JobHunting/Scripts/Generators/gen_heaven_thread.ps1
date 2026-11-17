param([string]$OutDir)
# Paste text for BP_SpiderThread (components and variables from setup_heaven_thread.py):
#   Begin Play: Thread, Fray and Zone stretched to Length below the top.
#   Tick 0: Swing pitched SwingDegrees * sin(2 pi (t + SwingOffset) / SwingSeconds).
#   Tick 1, not Broken:
#     not Holding: once 0.5 s after the last let-go, if the falling player is in Zone: Holding, HeldFor 0, GrabT = how far
#       below the top the player is (120..Length), JumpWas = Jump held now, LastPoint = the player, movement Flying.
#     Holding: if the player is suddenly far from LastPoint (respawned) - let go. Else HeldFor += dt; up/down input
#       (stick Y + W - S) climbs at ClimbSpeed, no input slides at SlideSpeed; the player is put at top - up * GrabT,
#       still; the thread is red once HeldFor > 60 % of HoldSeconds. Jump pressed (not held from before): let go,
#       launched 450 the camera's way + 520 up + the thread's motion (up to 900). HeldFor >= HoldSeconds > 0: let go,
#       the thread snaps (hidden, Broken) and is back RespawnSeconds later.
if (-not $OutDir) { throw 'OutDir is required' }
$lightGen = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_heaven_light.ps1') -Encoding UTF8
$cut = ($lightGen | Select-String -Pattern '^# ===== BP_LightBeam' | Select-Object -First 1).LineNumber - 1
$helpers = $lightGen[1..($cut - 1)] -join "`n"
. ([ScriptBlock]::Create($helpers))

$MOVEMENT = "/Script/CoreUObject.Class'/Script/Engine.MovementComponent'"
$NAV_MOVE = "/Script/CoreUObject.Class'/Script/Engine.NavMovementInterface'"
$PAWN = "/Script/CoreUObject.Class'/Script/Engine.Pawn'"
$KEY = "/Script/CoreUObject.ScriptStruct'/Script/InputCore.Key'"
$MOVE_ENUM = "/Script/CoreUObject.Enum'/Script/Engine.EMovementMode'"

function KeyDown($keyName, [double]$x, [double]$y) {
  $n = New-Call $CONTROLLER 'IsInputKeyDown' $true $x $y
  Add-Pin $n 'self' 'in' 'object' '' $CONTROLLER
  Add-Pin $n 'Key' 'in' 'struct' '' $KEY $keyName
  Add-Pin $n 'ReturnValue' 'out' 'bool'
  Connect (Controller ($x - 250) $y) 'ReturnValue' $n 'self'
  return $n
}
function JumpHeld([double]$x, [double]$y) {
  Both (KeyDown 'SpaceBar' $x $y) 'ReturnValue' (KeyDown 'Gamepad_FaceButton_Bottom' $x ($y + 120)) 'ReturnValue' 'BooleanOR' ($x + 250) ($y + 50)
}
function MoveMode($mode, [double]$x, [double]$y) {
  $n = New-Call $CHAR_MOVE 'SetMovementMode' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $CHAR_MOVE
  Add-Pin $n 'NewMovementMode' 'in' 'byte' '' $MOVE_ENUM $mode
  Add-Pin $n 'NewCustomMode' 'in' 'byte' '' $null '0'
  Connect (Movement ($x - 200) ($y + 220)) 'CharacterMovement' $n 'self'
  return $n
}
function Still([double]$x, [double]$y) {
  $n = New-VarSet 'Velocity' $MOVEMENT 'struct' $VECTOR $x $y
  (Get-Pin $n 'Velocity').Default = '0.000000,0.000000,0.000000'
  Connect (Movement ($x - 200) ($y + 220)) 'CharacterMovement' $n 'self'
  return $n
}
function MakeVec($xv, $yv, $zv, [double]$x, [double]$y) {
  $n = New-Call $MATH 'MakeVector' $true $x $y
  foreach ($axis in @(@('X', $xv), @('Y', $yv), @('Z', $zv))) {
    Add-Pin $n $axis[0] 'in' 'real' 'double'
    if ($axis[1] -is [string]) { (Get-Pin $n $axis[0]).Default = $axis[1] } else { Connect $axis[1][0] $axis[1][1] $n $axis[0] }
  }
  Add-Pin $n 'ReturnValue' 'out' 'struct' '' $VECTOR
  return $n
}
function VecTimes($v, $vPin, $f, $fPin, [double]$x, [double]$y) {
  $n = New-Call $MATH 'Multiply_VectorFloat' $true $x $y
  Add-Pin $n 'A' 'in' 'struct' '' $VECTOR
  Add-Pin $n 'B' 'in' 'real' 'double'
  Add-Pin $n 'ReturnValue' 'out' 'struct' '' $VECTOR
  Connect $v $vPin $n 'A'
  if ($f) { Connect $f $fPin $n 'B' } else { (Get-Pin $n 'B').Default = $fPin }
  return $n
}
function VecOp($operation, $func, $a, $aPin, $b, $bPin, [double]$x, [double]$y) {
  $n = New-Operator $operation $func 'struct' '' 'struct' $x $y
  foreach ($pin in 'A', 'B', 'ReturnValue') { (Get-Pin $n $pin).Obj = $VECTOR }
  Connect $a $aPin $n 'A'
  Connect $b $bPin $n 'B'
  return $n
}
function RelLocation($component, $class, $where, [double]$x, [double]$y) {
  $n = New-Call $SCENE 'K2_SetRelativeLocation' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $SCENE
  Add-Pin $n 'NewLocation' 'in' 'struct' '' $VECTOR
  Add-Pin $n 'bSweep' 'in' 'bool' '' $null 'false'
  Add-Pin $n 'SweepHitResult' 'out' 'struct' '' $HIT
  Add-Pin $n 'bTeleport' 'in' 'bool' '' $null 'true'
  Connect (Comp $component $class ($x - 200) ($y + 200)) $component $n 'self'
  Connect $where 'ReturnValue' $n 'NewLocation'
  return $n
}
function RelScale($component, $size, [double]$x, [double]$y) {
  $n = New-Call $SCENE 'SetRelativeScale3D' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $SCENE
  Add-Pin $n 'NewScale3D' 'in' 'struct' '' $VECTOR
  Connect (Comp $component $STATIC_MESH ($x - 200) ($y + 200)) $component $n 'self'
  Connect $size 'ReturnValue' $n 'NewScale3D'
  return $n
}
function Clamp($value, $valuePin, $min, $minPin, $max, $maxPin, [double]$x, [double]$y) {
  $n = New-Call $MATH 'FClamp' $true $x $y
  Add-Pin $n 'Value' 'in' 'real' 'double'
  Add-Pin $n 'Min' 'in' 'real' 'double'
  Add-Pin $n 'Max' 'in' 'real' 'double'
  Add-Pin $n 'ReturnValue' 'out' 'real' 'double'
  foreach ($p in @(@('Value', $value, $valuePin), @('Min', $min, $minPin), @('Max', $max, $maxPin))) {
    if ($p[1]) { Connect $p[1] $p[2] $n $p[0] } else { (Get-Pin $n $p[0]).Default = $p[2] }
  }
  return $n
}
function Not($node, $pin, [double]$x, [double]$y) {
  $n = MathCall 'Not_PreBool' @('A') 'bool' '' 'bool' '' $x $y
  Connect $node $pin $n 'A'
  return $n
}

Reset-Graph 100
# ----- Begin Play: stretch to Length -----
$begin = Event 'ReceiveBeginPlay' 0 0
$scaleZ = Op 'Divide' 'Divide_DoubleDouble' (Real 'Length' 0 250) 'Length' $null '100.0' 200 250
$size = MakeVec '0.04' '0.04' @($scaleZ, 'ReturnValue') 400 250
$below = Op 'Multiply' 'Multiply_DoubleDouble' (Real 'Length' 0 400) 'Length' $null '-0.5' 200 400
$pos = MakeVec '0.0' '0.0' @($below, 'ReturnValue') 400 400
$halfLen = Op 'Multiply' 'Multiply_DoubleDouble' (Real 'Length' 0 550) 'Length' $null '0.5' 200 550
$extent = MakeVec '45.0' '45.0' @($halfLen, 'ReturnValue') 400 550
$s1 = RelScale 'Thread' $size 700 0
$l1 = RelLocation 'Thread' $STATIC_MESH $pos 1000 0
$s2 = RelScale 'Fray' $size 1300 0
$l2 = RelLocation 'Fray' $STATIC_MESH $pos 1600 0
$zoneSize = New-Call $BOX 'SetBoxExtent' $false 1900 0
Add-Pin $zoneSize 'self' 'in' 'object' '' $BOX
Add-Pin $zoneSize 'InBoxExtent' 'in' 'struct' '' $VECTOR
Add-Pin $zoneSize 'bUpdateOverlaps' 'in' 'bool' '' $null 'true'
Connect (Comp 'Zone' $BOX 1700 200) 'Zone' $zoneSize 'self'
Connect $extent 'ReturnValue' $zoneSize 'InBoxExtent'
$l3 = RelLocation 'Zone' $BOX $pos 2200 0
Connect $begin 'then' $s1 'execute'
Chain @($s1, $l1, $s2, $l2, $zoneSize, $l3)

# ----- Tick -----
$tick = Event 'ReceiveTick' 0 900
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$seq = New-Node '/Script/BlueprintGraph.K2Node_ExecutionSequence' @() 250 900
Add-Pin $seq 'execute' 'in' 'exec'
Add-Pin $seq 'then_0' 'out' 'exec'
Add-Pin $seq 'then_1' 'out' 'exec'
Connect $tick 'then' $seq 'execute'

# 0: the swing.
$tSwing = Op 'Add' 'Add_DoubleDouble' (Now 300 1150) 'ReturnValue' (Real 'SwingOffset' 300 1250) 'SwingOffset' 500 1150
$period = MathCall 'FMax' @('A', 'B') 'real' 'double' 'real' 'double' 500 1300
Connect (Real 'SwingSeconds' 300 1350) 'SwingSeconds' $period 'A'
(Get-Pin $period 'B').Default = '0.1'
$omega = Op 'Divide' 'Divide_DoubleDouble' $null '6.2831853' $period 'ReturnValue' 700 1300
$phase = Op 'Multiply' 'Multiply_DoubleDouble' $omega 'ReturnValue' $tSwing 'ReturnValue' 900 1200
$sine = MathCall 'Sin' @('A') 'real' 'double' 'real' 'double' 1100 1200
Connect $phase 'ReturnValue' $sine 'A'
$angle = Op 'Multiply' 'Multiply_DoubleDouble' (Real 'SwingDegrees' 1100 1350) 'SwingDegrees' $sine 'ReturnValue' 1300 1200
$tilt = New-Call $MATH 'MakeRotator' $true 1500 1200
Add-Pin $tilt 'Roll' 'in' 'real' 'float' $null '0.0'
Add-Pin $tilt 'Pitch' 'in' 'real' 'float'
Add-Pin $tilt 'Yaw' 'in' 'real' 'float' $null '0.0'
Add-Pin $tilt 'ReturnValue' 'out' 'struct' '' $ROTATOR
Connect $angle 'ReturnValue' $tilt 'Pitch'
$turn = New-Call $SCENE 'K2_SetRelativeRotation' $false 1700 950
Add-Pin $turn 'self' 'in' 'object' '' $SCENE
Add-Pin $turn 'NewRotation' 'in' 'struct' '' $ROTATOR
Add-Pin $turn 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $turn 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $turn 'bTeleport' 'in' 'bool' '' $null 'false'
Connect (Comp 'Swing' $SCENE 1500 1050) 'Swing' $turn 'self'
Connect $tilt 'ReturnValue' $turn 'NewRotation'
Connect $seq 'then_0' $turn 'execute'

# 1: holding on.
$broken = New-Branch 400 1700
Connect (Bool 'Broken' 250 1900) 'Broken' $broken 'Condition'
Connect $seq 'then_1' $broken 'execute'
$holding = New-Branch 700 1700
Connect (Bool 'Holding' 550 1900) 'Holding' $holding 'Condition'
Connect $broken 'else' $holding 'execute'

# Shared values.
$playerAt = New-Call $ACTOR 'K2_GetActorLocation' $true 600 2300
Add-Pin $playerAt 'self' 'in' 'object' '' $ACTOR
Add-Pin $playerAt 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect (Player 400 2300) 'ReturnValue' $playerAt 'self'
$top = New-Call $SCENE 'K2_GetComponentLocation' $true 600 2450
Add-Pin $top 'self' 'in' 'object' '' $SCENE
Add-Pin $top 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect (Comp 'Swing' $SCENE 400 2450) 'Swing' $top 'self'
$upward = New-Call $SCENE 'GetUpVector' $true 600 2600
Add-Pin $upward 'self' 'in' 'object' '' $SCENE
Add-Pin $upward 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect (Comp 'Swing' $SCENE 400 2600) 'Swing' $upward 'self'
$jumpNow = JumpHeld 400 2750

# ----- not holding: catch hold? -----
$freeAt = Op 'Add' 'Add_DoubleDouble' (Real 'ReleasedAt' 800 2900) 'ReleasedAt' $null '0.5' 1000 2900
$rested = Op 'Greater' 'Greater_DoubleDouble' (Now 1000 3050) 'ReturnValue' $freeAt 'ReturnValue' 1200 2950 'bool'
$inZone = New-Call $PRIMITIVE 'IsOverlappingActor' $true 1000 3150
Add-Pin $inZone 'self' 'in' 'object' '' $PRIMITIVE
Add-Pin $inZone 'Other' 'in' 'object' '' $ACTOR
Add-Pin $inZone 'ReturnValue' 'out' 'bool'
Connect (Comp 'Zone' $BOX 800 3150) 'Zone' $inZone 'self'
Connect (Player 800 3250) 'ReturnValue' $inZone 'Other'
$falling = New-Call $NAV_MOVE 'IsFalling' $true 1000 3350
Add-Pin $falling 'self' 'in' 'interface' '' $NAV_MOVE
Add-Pin $falling 'ReturnValue' 'out' 'bool'
Connect (Movement 800 3350) 'CharacterMovement' $falling 'self'
$ok1 = Both $rested 'ReturnValue' $inZone 'ReturnValue' 'BooleanAND' 1400 3050
$canGrab = Both $ok1 'ReturnValue' $falling 'ReturnValue' 'BooleanAND' 1600 3150
$grab = New-Branch 1000 2600
Connect $canGrab 'ReturnValue' $grab 'Condition'
Connect $holding 'else' $grab 'execute'
$hold1 = SetSelf 'Holding' 'bool' 'true' 1900 2600
$held0 = SetReal 'HeldFor' 2200 2600
(Get-Pin $held0 'HeldFor').Default = '0.0'
$topZ = New-Call $MATH 'BreakVector' $true 2000 2850
Add-Pin $topZ 'InVec' 'in' 'struct' '' $VECTOR
Add-Pin $topZ 'X' 'out' 'real' 'double'; Add-Pin $topZ 'Y' 'out' 'real' 'double'; Add-Pin $topZ 'Z' 'out' 'real' 'double'
Connect $top 'ReturnValue' $topZ 'InVec'
$playerZ = New-Call $MATH 'BreakVector' $true 2000 3000
Add-Pin $playerZ 'InVec' 'in' 'struct' '' $VECTOR
Add-Pin $playerZ 'X' 'out' 'real' 'double'; Add-Pin $playerZ 'Y' 'out' 'real' 'double'; Add-Pin $playerZ 'Z' 'out' 'real' 'double'
Connect $playerAt 'ReturnValue' $playerZ 'InVec'
$depth = Op 'Subtract' 'Subtract_DoubleDouble' $topZ 'Z' $playerZ 'Z' 2200 2900
$depthC = Clamp $depth 'ReturnValue' $null '120.0' (Real 'Length' 2200 3050) 'Length' 2400 2900
$setT = SetReal 'GrabT' 2500 2600
Connect $depthC 'ReturnValue' $setT 'GrabT'
$was = SetSelf 'JumpWas' 'bool' $null 2800 2600
Connect $jumpNow 'ReturnValue' $was 'JumpWas'
$mark = New-VarSet 'LastPoint' $null 'struct' $VECTOR 3100 2600
Connect $playerAt 'ReturnValue' $mark 'LastPoint'
$fly = MoveMode 'MOVE_Flying' 3400 2600
$stop1 = Still 3700 2600
Connect $grab 'then' $hold1 'execute'
Chain @($hold1, $held0, $setT, $was, $mark, $fly, $stop1)

# ----- holding -----
$distance = New-Call $MATH 'Vector_Distance' $true 1000 1500
Add-Pin $distance 'V1' 'in' 'struct' '' $VECTOR
Add-Pin $distance 'V2' 'in' 'struct' '' $VECTOR
Add-Pin $distance 'ReturnValue' 'out' 'real' 'double'
Connect $playerAt 'ReturnValue' $distance 'V1'
Connect (Vec 'LastPoint' 800 1550) 'LastPoint' $distance 'V2'
$moved = New-Branch 1000 1200
Connect (Op 'Greater' 'Greater_DoubleDouble' $distance 'ReturnValue' $null '400.0' 1200 1450 'bool') 'ReturnValue' $moved 'Condition'
Connect $holding 'then' $moved 'execute'
# Respawned elsewhere: just let go.
$lost = SetSelf 'Holding' 'bool' 'false' 1300 1000
$lostMode = MoveMode 'MOVE_Falling' 1600 1000
Connect $moved 'then' $lost 'execute'
Connect $lost 'then' $lostMode 'execute'
# Climbing.
$heldMore = SetReal 'HeldFor' 1400 1200
Connect (Op 'Add' 'Add_DoubleDouble' (Real 'HeldFor' 1200 1650) 'HeldFor' $tick 'DeltaSeconds' 1400 1650) 'ReturnValue' $heldMore 'HeldFor'
Connect $moved 'else' $heldMore 'execute'
$stick = New-Call $CONTROLLER 'GetInputAnalogKeyState' $true 1500 1800
Add-Pin $stick 'self' 'in' 'object' '' $CONTROLLER
Add-Pin $stick 'Key' 'in' 'struct' '' $KEY 'Gamepad_LeftY'
Add-Pin $stick 'ReturnValue' 'out' 'real' 'float'
Connect (Controller 1300 1800) 'ReturnValue' $stick 'self'
$wKey = MathCall 'Conv_BoolToDouble' @('InBool') 'bool' '' 'real' 'double' 1500 1950
Connect (KeyDown 'W' 1300 1950) 'ReturnValue' $wKey 'InBool'
$sKey = MathCall 'Conv_BoolToDouble' @('InBool') 'bool' '' 'real' 'double' 1500 2100
Connect (KeyDown 'S' 1300 2100) 'ReturnValue' $sKey 'InBool'
$upDown = Op 'Add' 'Add_DoubleDouble' $stick 'ReturnValue' $wKey 'ReturnValue' 1700 1850
$net = Op 'Subtract' 'Subtract_DoubleDouble' $upDown 'ReturnValue' $sKey 'ReturnValue' 1900 1900
$axis = Clamp $net 'ReturnValue' $null '-1.0' $null '1.0' 2100 1900
$size2 = MathCall 'Abs' @('A') 'real' 'double' 'real' 'double' 2300 2000
Connect $axis 'ReturnValue' $size2 'A'
$active = Op 'Greater' 'Greater_DoubleDouble' $size2 'ReturnValue' $null '0.2' 2500 2000 'bool'
$climb = Op 'Multiply' 'Multiply_DoubleDouble' $axis 'ReturnValue' (Real 'ClimbSpeed' 2100 2050) 'ClimbSpeed' 2300 1850
$climbDown = Op 'Multiply' 'Multiply_DoubleDouble' $climb 'ReturnValue' $null '-1.0' 2500 1850
$rate = New-Call $MATH 'SelectFloat' $true 2700 1850
Add-Pin $rate 'A' 'in' 'real' 'double'
Add-Pin $rate 'B' 'in' 'real' 'double'
Add-Pin $rate 'bPickA' 'in' 'bool'
Add-Pin $rate 'ReturnValue' 'out' 'real' 'double'
Connect $climbDown 'ReturnValue' $rate 'A'
Connect (Real 'SlideSpeed' 2500 2150) 'SlideSpeed' $rate 'B'
Connect $active 'ReturnValue' $rate 'bPickA'
$stepT = Op 'Multiply' 'Multiply_DoubleDouble' $rate 'ReturnValue' $tick 'DeltaSeconds' 2900 1850
$nextT = Op 'Add' 'Add_DoubleDouble' (Real 'GrabT' 2900 1750) 'GrabT' $stepT 'ReturnValue' 3100 1800
$nextTC = Clamp $nextT 'ReturnValue' $null '120.0' (Real 'Length' 3100 1950) 'Length' 3300 1800
$setT2 = SetReal 'GrabT' 1700 1200
Connect $nextTC 'ReturnValue' $setT2 'GrabT'
Connect $heldMore 'then' $setT2 'execute'
# Where the player hangs, and how fast that point moves.
$negT = Op 'Multiply' 'Multiply_DoubleDouble' $setT2 'Output_Get' $null '-1.0' 1900 1400
$along = VecTimes $upward 'ReturnValue' $negT 'ReturnValue' 2100 1400
$point = VecOp 'Add' 'Add_VectorVector' $top 'ReturnValue' $along 'ReturnValue' 2300 1400
$moveBy = VecOp 'Subtract' 'Subtract_VectorVector' $point 'ReturnValue' (Vec 'LastPoint' 2300 1550) 'LastPoint' 2500 1450
$dtSafe = MathCall 'FMax' @('A', 'B') 'real' 'double' 'real' 'double' 2500 1600
Connect $tick 'DeltaSeconds' $dtSafe 'A'
(Get-Pin $dtSafe 'B').Default = '0.001'
$perSecond = Op 'Divide' 'Divide_DoubleDouble' $null '1.0' $dtSafe 'ReturnValue' 2700 1600
$velocity = VecTimes $moveBy 'ReturnValue' $perSecond 'ReturnValue' 2900 1450
$swingVel = New-Call $MATH 'ClampVectorSize' $true 3100 1450
Add-Pin $swingVel 'A' 'in' 'struct' '' $VECTOR
Add-Pin $swingVel 'Min' 'in' 'real' 'double' $null '0.0'
Add-Pin $swingVel 'Max' 'in' 'real' 'double' $null '900.0'
Add-Pin $swingVel 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $velocity 'ReturnValue' $swingVel 'A'
$mark2 = New-VarSet 'LastPoint' $null 'struct' $VECTOR 2000 1200
Connect $point 'ReturnValue' $mark2 'LastPoint'
$place = New-Call $ACTOR 'K2_SetActorLocation' $false 2300 1200
Add-Pin $place 'self' 'in' 'object' '' $ACTOR
Add-Pin $place 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $place 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $place 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $place 'bTeleport' 'in' 'bool' '' $null 'true'
Add-Pin $place 'ReturnValue' 'out' 'bool'
Connect (Player 2100 1100) 'ReturnValue' $place 'self'
Connect $point 'ReturnValue' $place 'NewLocation'
$stop2 = Still 2600 1200
# Fraying.
$limited = Op 'Greater' 'Greater_DoubleDouble' (Real 'HoldSeconds' 2700 2300) 'HoldSeconds' $null '0.0' 2900 2300 'bool'
$warnAt = Op 'Multiply' 'Multiply_DoubleDouble' (Real 'HoldSeconds' 2700 2450) 'HoldSeconds' $null '0.6' 2900 2450
$late = Op 'Greater' 'Greater_DoubleDouble' $heldMore 'Output_Get' $warnAt 'ReturnValue' 3100 2400 'bool'
$fraying = Both $limited 'ReturnValue' $late 'ReturnValue' 'BooleanAND' 3300 2350
$red = Visible 'Fray' @($fraying, 'ReturnValue') 2900 1200
$white = Visible 'Thread' @((Not $fraying 'ReturnValue' 3400 2200), 'ReturnValue') 3200 1200
# Jump: pressed now, not held from before.
$fresh = Both $jumpNow 'ReturnValue' (Not (Bool 'JumpWas' 3300 1600) 'JumpWas' 3450 1600) 'ReturnValue' 'BooleanAND' 3600 1550
$wasNow = SetSelf 'JumpWas' 'bool' $null 3500 1200
Connect $jumpNow 'ReturnValue' $wasNow 'JumpWas'
$leap = New-Branch 3800 1200
Connect $fresh 'ReturnValue' $leap 'Condition'
Connect $setT2 'then' $mark2 'execute'
# (Decide on the jump before JumpWas takes this frame's state, or a press never counts.)
Chain @($mark2, $place, $stop2, $red, $white, $leap)
# Let go with a leap.
$let = SetSelf 'Holding' 'bool' 'false' 4100 1000
$when = SetReal 'ReleasedAt' 4400 1000
Connect (Now 4250 1200) 'ReturnValue' $when 'ReleasedAt'
$fall = MoveMode 'MOVE_Falling' 4700 1000
$facing = New-Call $PAWN 'GetControlRotation' $true 4500 1350
Add-Pin $facing 'self' 'in' 'object' '' $PAWN
Add-Pin $facing 'ReturnValue' 'out' 'struct' '' $ROTATOR
Connect (Player 4300 1350) 'ReturnValue' $facing 'self'
$parts = New-Call $MATH 'BreakRotator' $true 4700 1350
Add-Pin $parts 'InRot' 'in' 'struct' '' $ROTATOR
Add-Pin $parts 'Roll' 'out' 'real' 'float'; Add-Pin $parts 'Pitch' 'out' 'real' 'float'; Add-Pin $parts 'Yaw' 'out' 'real' 'float'
Connect $facing 'ReturnValue' $parts 'InRot'
$flat = New-Call $MATH 'MakeRotator' $true 4900 1350
Add-Pin $flat 'Roll' 'in' 'real' 'float' $null '0.0'
Add-Pin $flat 'Pitch' 'in' 'real' 'float' $null '0.0'
Add-Pin $flat 'Yaw' 'in' 'real' 'float'
Add-Pin $flat 'ReturnValue' 'out' 'struct' '' $ROTATOR
Connect $parts 'Yaw' $flat 'Yaw'
$ahead = New-Call $MATH 'GetForwardVector' $true 5100 1350
Add-Pin $ahead 'InRot' 'in' 'struct' '' $ROTATOR
Add-Pin $ahead 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $flat 'ReturnValue' $ahead 'InRot'
$push = VecTimes $ahead 'ReturnValue' $null '450.0' 5300 1350
$lift = MakeVec '0.0' '0.0' '520.0' 5300 1500
$push2 = VecOp 'Add' 'Add_VectorVector' $push 'ReturnValue' $lift 'ReturnValue' 5500 1400
$launchVel = VecOp 'Add' 'Add_VectorVector' $push2 'ReturnValue' $swingVel 'ReturnValue' 5700 1400
$launch = New-Call $CHARACTER 'LaunchCharacter' $false 5000 1000
Add-Pin $launch 'self' 'in' 'object' '' $CHARACTER
Add-Pin $launch 'LaunchVelocity' 'in' 'struct' '' $VECTOR
Add-Pin $launch 'bXYOverride' 'in' 'bool' '' $null 'true'
Add-Pin $launch 'bZOverride' 'in' 'bool' '' $null 'true'
Connect (Player 4800 1200) 'ReturnValue' $launch 'self'
Connect $launchVel 'ReturnValue' $launch 'LaunchVelocity'
Connect $leap 'then' $let 'execute'
Chain @($let, $when, $fall, $launch)
# Held too long: it snaps.
$snap = New-Branch 4100 1700
$tooLong = Op 'GreaterEqual' 'GreaterEqual_DoubleDouble' $heldMore 'Output_Get' (Real 'HoldSeconds' 3800 1950) 'HoldSeconds' 4000 1900 'bool'
Connect (Both $limited 'ReturnValue' $tooLong 'ReturnValue' 'BooleanAND' 4100 1950) 'ReturnValue' $snap 'Condition'
Connect $leap 'else' $wasNow 'execute'
Connect $wasNow 'then' $snap 'execute'
$let2 = SetSelf 'Holding' 'bool' 'false' 4400 1700
$when2 = SetReal 'ReleasedAt' 4700 1700
Connect (Now 4550 1900) 'ReturnValue' $when2 'ReleasedAt'
$fall2 = MoveMode 'MOVE_Falling' 5000 1700
$gone = SetSelf 'Broken' 'bool' 'true' 5300 1700
$hideW = Visible 'Thread' 'false' 5600 1700
$hideR = Visible 'Fray' 'false' 5900 1700
$wait = Delay '4.0' 6200 1700
Connect (Real 'RespawnSeconds' 6050 1950) 'RespawnSeconds' $wait 'Duration'
$back = SetSelf 'Broken' 'bool' 'false' 6500 1700
$showW = Visible 'Thread' 'true' 6800 1700
Connect $snap 'then' $let2 'execute'
Chain @($let2, $when2, $fall2, $gone, $hideW, $hideR, $wait, $back, $showW)
Write-Graph 'BP_SpiderThread_EventGraph.txt'
