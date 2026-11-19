param([string]$OutDir)
# Paste text for the sky gimmicks (components and variables from setup_area3_gimmicks.py):
#   BP_VanishCloud_EventGraph.txt  stepped on (once at a time): the cloud sinks 12 cm, StaySeconds later it is gone
#                                  (hidden, no collision), GoneSeconds later it is back where it was.
#   BP_WindZone_EventGraph.txt     Begin Play: with GustOn and GustOff both above 0, from StartDelay on it blows GustOn
#                                  seconds (Active, streaks shown) and rests GustOff seconds, round and round. Tick:
#                                  while Active and the player is in Zone, the player's velocity gains
#                                  forward * Strength * (1 - speed along forward / MaxSpeed, kept 0..1) * dt.
if (-not $OutDir) { throw 'OutDir is required' }
$cageGen = Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_hell_cage.ps1'
$defs = Get-Content -LiteralPath $cageGen -Encoding UTF8 | Select-Object -Skip 10 -First 172
. ([ScriptBlock]::Create(($defs -join "`n")))

$SCENE = "/Script/CoreUObject.Class'/Script/Engine.SceneComponent'"
$STATIC_MESH = "/Script/CoreUObject.Class'/Script/Engine.StaticMeshComponent'"
$COLLISION_ENUM = "/Script/CoreUObject.Enum'/Script/Engine.ECollisionEnabled'"

function Event($name, [double]$x, [double]$y) {
  $n = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$ACTOR`",MemberName=`"$name`")", 'bOverrideFunction=True') $x $y
  Add-Pin $n 'then' 'out' 'exec'
  return $n
}
function SetSelf($name, $cat, $value, [double]$x, [double]$y) {
  $n = New-VarSet $name $null $cat $null $x $y
  if ($null -ne $value) { (Get-Pin $n $name).Default = $value }
  return $n
}
function Comp($name, $class, [double]$x, [double]$y) { New-VarGet $name $null 'object' '' $class $x $y }
function Real($name, [double]$x, [double]$y) { New-VarGet $name $null 'real' 'double' $null $x $y }
function PlayerIn($boxName, [double]$x, [double]$y) {
  $n = New-Call $PRIMITIVE 'IsOverlappingActor' $true $x $y
  Add-Pin $n 'self' 'in' 'object' '' $PRIMITIVE
  Add-Pin $n 'Other' 'in' 'object' '' $ACTOR
  Add-Pin $n 'ReturnValue' 'out' 'bool'
  Connect (New-VarGet $boxName $null 'object' '' $BOX ($x - 200) $y) $boxName $n 'self'
  Connect (Player ($x - 250) ($y + 100)) 'ReturnValue' $n 'Other'
  return $n
}
function Touched($guard, $boxName, [double]$x, [double]$y) {
  $touch = Event 'ReceiveActorBeginOverlap' $x $y
  Add-Pin $touch 'OtherActor' 'out' 'object' '' $ACTOR
  $once = New-Branch ($x + 300) $y
  Connect (New-VarGet $guard $null 'bool' '' $null ($x + 150) ($y + 200)) $guard $once 'Condition'
  $isPlayer = New-Branch ($x + 550) $y
  Connect (PlayerIn $boxName ($x + 450) ($y + 250)) 'ReturnValue' $isPlayer 'Condition'
  Connect $touch 'then' $once 'execute'
  Connect $once 'else' $isPlayer 'execute'
  return $isPlayer
}
function Visible($componentName, $value, [double]$x, [double]$y) {
  $n = New-Call $SCENE 'SetVisibility' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $SCENE
  Add-Pin $n 'bNewVisibility' 'in' 'bool' '' $null $value
  Add-Pin $n 'bPropagateToChildren' 'in' 'bool' '' $null 'false'
  Connect (Comp $componentName $STATIC_MESH ($x - 200) ($y + 200)) $componentName $n 'self'
  return $n
}
function Collide($componentName, $type, [double]$x, [double]$y) {
  $n = New-Call $PRIMITIVE 'SetCollisionEnabled' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $PRIMITIVE
  Add-Pin $n 'NewType' 'in' 'byte' '' $COLLISION_ENUM $type
  Connect (Comp $componentName $STATIC_MESH ($x - 200) ($y + 200)) $componentName $n 'self'
  return $n
}
function MoveTo($componentName, $where, $seconds, [double]$x, [double]$y) {
  $n = New-Call $SYSTEM 'MoveComponentTo' $false $x $y
  $n.Props = @('bWantsEnumToExecExpansion=True') + $n.Props
  $n.Pins.Clear()
  Add-Pin $n 'Move' 'in' 'exec'
  Add-Pin $n 'then' 'out' 'exec'
  Add-Pin $n 'Component' 'in' 'object' '' $SCENE
  Add-Pin $n 'TargetRelativeLocation' 'in' 'struct' '' $VECTOR $where
  Add-Pin $n 'TargetRelativeRotation' 'in' 'struct' '' $ROTATOR '0, 0, 0'
  Add-Pin $n 'bEaseOut' 'in' 'bool' '' $null 'true'
  Add-Pin $n 'bEaseIn' 'in' 'bool' '' $null 'false'
  Add-Pin $n 'OverTime' 'in' 'real' 'float' $null $seconds
  Add-Pin $n 'bForceShortestRotationPath' 'in' 'bool' '' $null 'false'
  Connect (Comp $componentName $STATIC_MESH ($x - 200) ($y + 250)) $componentName $n 'Component'
  return $n
}
function Wait($variable, [double]$x, [double]$y) {
  $n = Delay '0.0' $x $y
  Connect (Real $variable ($x - 150) ($y + 250)) $variable $n 'Duration'
  return $n
}
function MathCall($func, [string[]]$inputs, $inCat, $inSub, $inObj, $outCat, $outSub, $outObj, [double]$x, [double]$y) {
  $n = New-Call $MATH $func $true $x $y
  foreach ($pin in $inputs) { Add-Pin $n $pin 'in' $inCat $inSub $inObj }
  Add-Pin $n 'ReturnValue' 'out' $outCat $outSub $outObj
  return $n
}

# ===== BP_VanishCloud ======================================================================================
Reset-Graph 100
$stepped = Touched 'Busy' 'Trigger' 0 0
$busy = SetSelf 'Busy' 'bool' 'true' 900 0
$sink = MoveTo 'Cloud' '0.000000,0.000000,-12.000000' '0.15' 1150 0
$stay = Wait 'StaySeconds' 1550 0
$noFloor = Collide 'Cloud' 'NoCollision' 1800 0
$hide = Visible 'Cloud' 'false' 2100 0
$gone = Wait 'GoneSeconds' 2400 0
$back = New-Call $SCENE 'K2_SetRelativeLocation' $false 2650 0
Add-Pin $back 'self' 'in' 'object' '' $SCENE
Add-Pin $back 'NewLocation' 'in' 'struct' '' $VECTOR '0.000000,0.000000,0.000000'
Add-Pin $back 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $back 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $back 'bTeleport' 'in' 'bool' '' $null 'true'
Connect (Comp 'Cloud' $STATIC_MESH 2450 250) 'Cloud' $back 'self'
$floor = Collide 'Cloud' 'QueryAndPhysics' 2950 0
$show = Visible 'Cloud' 'true' 3250 0
$free = SetSelf 'Busy' 'bool' 'false' 3550 0
# The look (setup_vanish_cloud_look.py, 2026-11-19): a poof as it goes, a gathering puff as it comes back; the sounds
# at SE Volume x Master Volume, set at Begin Play.
$CLOUD_EMITTER = "/Script/CoreUObject.Class'/Script/Effekseer.EffekseerEmitterComponent'"
$CLOUD_AUDIO = "/Script/CoreUObject.Class'/Script/Engine.AudioComponent'"
$ACTOR_COMP = "/Script/CoreUObject.Class'/Script/Engine.ActorComponent'"
function Fx-Play($componentName, [double]$x, [double]$y) {
  $n = New-Call $ACTOR_COMP 'Activate' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR_COMP
  Add-Pin $n 'bReset' 'in' 'bool' '' $null 'true'
  Connect (New-VarGet $componentName $null 'object' '' $CLOUD_EMITTER ($x - 200) ($y + 200)) $componentName $n 'self'
  return $n
}
function Sound-Play($componentName, [double]$x, [double]$y) {
  $n = New-Call $CLOUD_AUDIO 'Play' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $CLOUD_AUDIO
  Add-Pin $n 'StartTime' 'in' 'real' 'float' $null '0.0'
  Connect (New-VarGet $componentName $null 'object' '' $CLOUD_AUDIO ($x - 200) ($y + 200)) $componentName $n 'self'
  return $n
}
$poof = Fx-Play 'PoofFx' 2100 (-350)
$poofSound = Sound-Play 'PoofSound' 2350 (-350)
$form = Fx-Play 'FormFx' 2700 (-350)
$formSound = Sound-Play 'FormSound' 2950 (-350)
Connect $stepped 'then' $busy 'execute'
Connect $busy 'then' $sink 'Move'
Connect $sink 'then' $stay 'execute'
Chain @($stay, $noFloor, $hide, $poof, $poofSound, $gone, $back, $form, $formSound, $floor, $show, $free)
# Begin Play: the two sounds' volume.
$start = Event 'ReceiveBeginPlay' 0 (-900)
$giCast = GameInstance 300 (-900)
$seVol = New-Operator 'Multiply' 'Multiply_DoubleDouble' 'real' 'double' 'real' 550 (-650)
(Get-Pin $seVol 'ReturnValue').Sub = 'double'
Connect (GiGet $giCast 'SE Volume' 'real' 'double' 350 (-700)) 'SE Volume' $seVol 'A'
Connect (GiGet $giCast 'Master Volume' 'real' 'double' 350 (-600)) 'Master Volume' $seVol 'B'
$vols = @()
$vx = 700
foreach ($name in 'PoofSound', 'FormSound') {
  $v = New-Call $CLOUD_AUDIO 'SetVolumeMultiplier' $false $vx (-900)
  Add-Pin $v 'self' 'in' 'object' '' $CLOUD_AUDIO
  Add-Pin $v 'NewVolumeMultiplier' 'in' 'real' 'float'
  Connect (New-VarGet $name $null 'object' '' $CLOUD_AUDIO ($vx - 200) (-700)) $name $v 'self'
  Connect $seVol 'ReturnValue' $v 'NewVolumeMultiplier'
  $vols += $v
  $vx += 300
}
Connect $start 'then' $giCast 'execute'
Connect $giCast 'then' $vols[0] 'execute'
Chain $vols
Write-Graph 'BP_VanishCloud_EventGraph.txt'

# ===== BP_WindZone =========================================================================================
Reset-Graph 100
# Gusts.
$begin = Event 'ReceiveBeginPlay' 0 0
$both = MathCall 'BooleanAND' @('A', 'B') 'bool' '' $null 'bool' '' $null 500 250
$onSet = MathCall 'Greater_DoubleDouble' @('A', 'B') 'real' 'double' $null 'bool' '' $null 300 200
Connect (Real 'GustOn' 100 200) 'GustOn' $onSet 'A'
(Get-Pin $onSet 'B').Default = '0.0'
$offSet = MathCall 'Greater_DoubleDouble' @('A', 'B') 'real' 'double' $null 'bool' '' $null 300 350
Connect (Real 'GustOff' 100 350) 'GustOff' $offSet 'A'
(Get-Pin $offSet 'B').Default = '0.0'
Connect $onSet 'ReturnValue' $both 'A'
Connect $offSet 'ReturnValue' $both 'B'
$gusty = New-Branch 300 0
Connect $both 'ReturnValue' $gusty 'Condition'
$first = Wait 'StartDelay' 650 0
$blow = SetSelf 'Active' 'bool' 'true' 900 0
$side1 = Visible 'StreaksSide' 'true' 1200 0
$top1 = Visible 'StreaksTop' 'true' 1500 0
$blowing = Wait 'GustOn' 1800 0
$rest = SetSelf 'Active' 'bool' 'false' 2050 0
$side0 = Visible 'StreaksSide' 'false' 2350 0
$top0 = Visible 'StreaksTop' 'false' 2650 0
$resting = Wait 'GustOff' 2950 0
# The wind's look (WindFx, setup_wind_fx.py, 2026-11-19): on while a gust blows, off while it rests.
$EMITTER = "/Script/CoreUObject.Class'/Script/Effekseer.EffekseerEmitterComponent'"
$ACTOR_COMPONENT = "/Script/CoreUObject.Class'/Script/Engine.ActorComponent'"
function WindFx($func, [double]$x, [double]$y) {
  $n = New-Call $ACTOR_COMPONENT $func $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR_COMPONENT
  if ($func -eq 'Activate') { Add-Pin $n 'bReset' 'in' 'bool' '' $null 'true' }
  Connect (New-VarGet 'WindFx' $null 'object' '' $EMITTER ($x - 200) ($y + 200)) 'WindFx' $n 'self'
  return $n
}
$fxOn = WindFx 'Activate' 1500 (-300)
$fxOff = WindFx 'Deactivate' 2650 (-300)
Connect $begin 'then' $gusty 'execute'
Connect $gusty 'then' $first 'execute'
Chain @($first, $blow, $side1, $top1, $fxOn, $blowing, $rest, $side0, $top0, $fxOff, $resting)
# Round again.
Connect $resting 'then' $blow 'execute'

# The push.
$tick = Event 'ReceiveTick' 0 800
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$on = New-Branch 300 800
Connect (New-VarGet 'Active' $null 'bool' '' $null 150 1000) 'Active' $on 'Condition'
$inside = New-Branch 550 800
Connect (PlayerIn 'Zone' 450 1050) 'ReturnValue' $inside 'Condition'
$forward = New-Call $null 'GetActorForwardVector' $true 300 1300
Add-Pin $forward 'ReturnValue' 'out' 'struct' '' $VECTOR
$velocity = New-Call $ACTOR 'GetVelocity' $true 300 1450
Add-Pin $velocity 'self' 'in' 'object' '' $ACTOR
Add-Pin $velocity 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect (Player 100 1450) 'ReturnValue' $velocity 'self'
$along = MathCall 'Dot_VectorVector' @('A', 'B') 'struct' '' $VECTOR 'real' 'double' $null 550 1400
Connect $velocity 'ReturnValue' $along 'A'
Connect $forward 'ReturnValue' $along 'B'
$part = MathCall 'Divide_DoubleDouble' @('A', 'B') 'real' 'double' $null 'real' 'double' $null 750 1400
Connect $along 'ReturnValue' $part 'A'
Connect (Real 'MaxSpeed' 600 1550) 'MaxSpeed' $part 'B'
$left = MathCall 'Subtract_DoubleDouble' @('A', 'B') 'real' 'double' $null 'real' 'double' $null 950 1400
(Get-Pin $left 'A').Default = '1.0'
Connect $part 'ReturnValue' $left 'B'
$room = New-Call $MATH 'FClamp' $true 1150 1400
Add-Pin $room 'Value' 'in' 'real' 'double'
Add-Pin $room 'Min' 'in' 'real' 'double' $null '0.0'
Add-Pin $room 'Max' 'in' 'real' 'double' $null '1.0'
Add-Pin $room 'ReturnValue' 'out' 'real' 'double'
Connect $left 'ReturnValue' $room 'Value'
$push = MathCall 'Multiply_DoubleDouble' @('A', 'B') 'real' 'double' $null 'real' 'double' $null 1350 1300
Connect (Real 'Strength' 1200 1250) 'Strength' $push 'A'
Connect $room 'ReturnValue' $push 'B'
$step = MathCall 'Multiply_DoubleDouble' @('A', 'B') 'real' 'double' $null 'real' 'double' $null 1550 1300
Connect $push 'ReturnValue' $step 'A'
Connect $tick 'DeltaSeconds' $step 'B'
$impulse = New-Call $MATH 'Multiply_VectorFloat' $true 1750 1250
Add-Pin $impulse 'A' 'in' 'struct' '' $VECTOR
Add-Pin $impulse 'B' 'in' 'real' 'double'
Add-Pin $impulse 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $forward 'ReturnValue' $impulse 'A'
Connect $step 'ReturnValue' $impulse 'B'
$add = New-Call $CHAR_MOVE 'AddImpulse' $false 1950 800
Add-Pin $add 'self' 'in' 'object' '' $CHAR_MOVE
Add-Pin $add 'Impulse' 'in' 'struct' '' $VECTOR
Add-Pin $add 'bVelocityChange' 'in' 'bool' '' $null 'true'
Connect (Movement 1750 1050) 'CharacterMovement' $add 'self'
Connect $impulse 'ReturnValue' $add 'Impulse'
Connect $tick 'then' $on 'execute'
Connect $on 'then' $inside 'execute'
Connect $inside 'then' $add 'execute'
Write-Graph 'BP_WindZone_EventGraph.txt'
