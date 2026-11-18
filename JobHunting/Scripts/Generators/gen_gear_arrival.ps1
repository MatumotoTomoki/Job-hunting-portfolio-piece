param([string]$OutDir)
# Paste text for BP_GearArrival (components and variables from setup_gear_arrival.py): area 1's gear comes up through
# area 2's floor seal.
#   Begin Play (a moment later): only if the game instance's GearArrival is set (BP_GearExit sets it) - clear it,
#     Arriving, ArriveAt = now, the player stood on the gear (down in the shaft), input off, the view on ShowCam, the
#     sounds at SE Volume x Master Volume; OpenDelay later the clunk, the hiss, the steam and the turning sound.
#   Tick, while Arriving (t = now - ArriveAt; ease = FInterpEaseInOut exponent 2):
#     going up:   lid = clamp((t - OpenDelay) / LidSeconds); rise = clamp((t - OpenDelay - 0.6 LidSeconds) / RiseSeconds)
#                 Lift at LandZ - Depth (1 - ease(rise))
#     going down: down = clamp((now - DownAt) / DownSeconds); Lift at LandZ - Depth ease(down)
#                 lid = 1 - clamp((now - DownAt - 0.55 DownSeconds) / LidSeconds)
#     the halves: sink LidSink over the first quarter of lid, then slide LidSlide apart (+Y / -Y) over the rest.
#     The gear turns at SpinSpeed except while it waits at the top.
#     Arrived (rise = 1, once): Landed, the view back on the player (1 s blend), input on, the turning sound stops.
#     Waiting: while the player is in OnGear, OffSince = now; a second after they have left: GoingDown, DownAt = now,
#       the turning sound again.
#     Shut (lid back to 0 while going down): Closed, Arriving off (the graph rests), the clunk, a puff of steam.
if (-not $OutDir) { throw 'OutDir is required' }
$lightGen = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_heaven_light.ps1') -Encoding UTF8
$cut = ($lightGen | Select-String -Pattern '^# ===== BP_LightBeam' | Select-Object -First 1).LineNumber - 1
$helpers = $lightGen[1..($cut - 1)] -join "`n"
. ([ScriptBlock]::Create($helpers))

$EMITTER = "/Script/CoreUObject.Class'/Script/Effekseer.EffekseerEmitterComponent'"
$ACTOR_COMPONENT = "/Script/CoreUObject.Class'/Script/Engine.ActorComponent'"
$AUDIO = "/Script/CoreUObject.Class'/Script/Engine.AudioComponent'"

function MakeVec($xPin, $yPin, $zPin, [double]$x, [double]$y) {
  # Each pin: a literal string, or @(node, pin).
  $n = New-Call $MATH 'MakeVector' $true $x $y
  foreach ($pair in @(@('X', $xPin), @('Y', $yPin), @('Z', $zPin))) {
    if ($pair[1] -is [string]) { Add-Pin $n $pair[0] 'in' 'real' 'double' $null $pair[1] }
    else { Add-Pin $n $pair[0] 'in' 'real' 'double'; Connect $pair[1][0] $pair[1][1] $n $pair[0] }
  }
  Add-Pin $n 'ReturnValue' 'out' 'struct' '' $VECTOR
  return $n
}
function Place($componentName, $class, $where, [double]$x, [double]$y) {
  $n = New-Call $SCENE 'K2_SetRelativeLocation' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $SCENE
  Add-Pin $n 'NewLocation' 'in' 'struct' '' $VECTOR
  Add-Pin $n 'bSweep' 'in' 'bool' '' $null 'false'
  Add-Pin $n 'SweepHitResult' 'out' 'struct' '' $HIT
  Add-Pin $n 'bTeleport' 'in' 'bool' '' $null 'false'
  Connect (Comp $componentName $class ($x - 200) ($y + 200)) $componentName $n 'self'
  Connect $where 'ReturnValue' $n 'NewLocation'
  return $n
}
function Clamp01($node, $pin, [double]$x, [double]$y) {
  $n = MathCall 'FClamp' @('Value', 'Min', 'Max') 'real' 'double' 'real' 'double' $x $y
  (Get-Pin $n 'Min').Default = '0.0'
  (Get-Pin $n 'Max').Default = '1.0'
  Connect $node $pin $n 'Value'
  return $n
}
function Ease($node, $pin, [double]$x, [double]$y) {
  $n = New-Call $MATH 'FInterpEaseInOut' $true $x $y
  Add-Pin $n 'A' 'in' 'real' 'double' $null '0.0'
  Add-Pin $n 'B' 'in' 'real' 'double' $null '1.0'
  Add-Pin $n 'Alpha' 'in' 'real' 'double'
  Add-Pin $n 'Exponent' 'in' 'real' 'double' $null '2.0'
  Add-Pin $n 'ReturnValue' 'out' 'real' 'double'
  Connect $node $pin $n 'Alpha'
  return $n
}
function Pick($a, $aPin, $b, $bPin, $cond, $condPin, [double]$x, [double]$y) {
  # cond ? a : b on doubles
  $n = New-Call $MATH 'SelectFloat' $true $x $y
  Add-Pin $n 'A' 'in' 'real' 'double'
  Add-Pin $n 'B' 'in' 'real' 'double'
  Add-Pin $n 'bPickA' 'in' 'bool'
  Add-Pin $n 'ReturnValue' 'out' 'real' 'double'
  if ($a) { Connect $a $aPin $n 'A' } else { (Get-Pin $n 'A').Default = $aPin }
  if ($b) { Connect $b $bPin $n 'B' } else { (Get-Pin $n 'B').Default = $bPin }
  Connect $cond $condPin $n 'bPickA'
  return $n
}
function Not($node, $pin, [double]$x, [double]$y) {
  $n = MathCall 'Not_PreBool' @('A') 'bool' '' 'bool' '' $x $y
  Connect $node $pin $n 'A'
  return $n
}
function Start-Emitter($componentName, [double]$x, [double]$y) {
  $n = New-Call $ACTOR_COMPONENT 'Activate' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR_COMPONENT
  Add-Pin $n 'bReset' 'in' 'bool' '' $null 'true'
  Connect (Comp $componentName $EMITTER ($x - 200) ($y + 200)) $componentName $n 'self'
  return $n
}
function Sound($func, $componentName, [double]$x, [double]$y) {
  $n = New-Call $AUDIO $func $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $AUDIO
  if ($func -eq 'Play') { Add-Pin $n 'StartTime' 'in' 'real' 'float' $null '0.0' }
  Connect (Comp $componentName $AUDIO ($x - 200) ($y + 200)) $componentName $n 'self'
  return $n
}
function Hide-Lift($hidden, [double]$x, [double]$y) {
  # Lift and everything on it (gear, rings, glow, axle) hidden in game or shown; the editor still shows them.
  $n = New-Call $SCENE 'SetHiddenInGame' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $SCENE
  Add-Pin $n 'NewHidden' 'in' 'bool' '' $null $hidden
  Add-Pin $n 'bPropagateToChildren' 'in' 'bool' '' $null 'true'
  Connect (Comp 'Lift' $SCENE ($x - 200) ($y + 200)) 'Lift' $n 'self'
  return $n
}
function Block-Hole($type, [double]$x, [double]$y) {
  # LidBlock (the invisible box over the hole) on or off.
  $n = New-Call $PRIMITIVE 'SetCollisionEnabled' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $PRIMITIVE
  Add-Pin $n 'NewType' 'in' 'byte' '' $COLLISION_ENUM $type
  Connect (Comp 'LidBlock' $BOX ($x - 200) ($y + 200)) 'LidBlock' $n 'self'
  return $n
}
function Self-Node([double]$x, [double]$y) {
  $n = New-Node '/Script/BlueprintGraph.K2Node_Self' @() $x $y
  Add-Pin $n 'self' 'out' 'object' '' $ACTOR
  return $n
}

Reset-Graph 100
# ===== Begin Play =====
$begin = Event 'ReceiveBeginPlay' 0 (-1600)
$settle = Delay '0.15' 250 (-1600)
$cast = GameInstance 550 (-1600)
$came = New-Branch 850 (-1600)
Connect (GiGet $cast 'GearArrival' 'bool' '' 700 (-1400)) 'GearArrival' $came 'Condition'
$clear = GiSet $cast 'GearArrival' 'bool' '' 1100 (-1600) 'false'
$arriving = SetSelf 'Arriving' 'bool' 'true' 1400 (-1600)
$arriveAt = SetReal 'ArriveAt' 1650 (-1600)
Connect (Now 1500 (-1400)) 'ReturnValue' $arriveAt 'ArriveAt'
# The player on the gear, down in the shaft: the gear's hub top is 54 above Lift, the capsule's middle 97 above that.
$standZ = Op 'Subtract' 'Subtract_DoubleDouble' (Real 'LandZ' 1700 (-1250)) 'LandZ' (Real 'Depth' 1700 (-1150)) 'Depth' 1900 (-1250)
$standZ2 = Op 'Add' 'Add_DoubleDouble' $standZ 'ReturnValue' $null '151.0' 2100 (-1250)
$up = MakeVec '0.0' '0.0' @($standZ2, 'ReturnValue') 2300 (-1250)
$here = New-Call $ACTOR 'K2_GetActorLocation' $true 2300 (-1050)
Add-Pin $here 'self' 'in' 'object' '' $ACTOR
Add-Pin $here 'ReturnValue' 'out' 'struct' '' $VECTOR
$spot = New-Operator 'Add' 'Add_VectorVector' 'struct' '' 'struct' 2550 (-1150)
foreach ($pin in 'A', 'B', 'ReturnValue') { (Get-Pin $spot $pin).Obj = $VECTOR }
Connect $here 'ReturnValue' $spot 'A'
Connect $up 'ReturnValue' $spot 'B'
$put = New-Call $ACTOR 'K2_SetActorLocation' $false 2750 (-1600)
Add-Pin $put 'self' 'in' 'object' '' $ACTOR
Add-Pin $put 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $put 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $put 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $put 'bTeleport' 'in' 'bool' '' $null 'true'
Add-Pin $put 'ReturnValue' 'out' 'bool'
Connect (Player 2550 (-1400)) 'ReturnValue' $put 'self'
Connect $spot 'ReturnValue' $put 'NewLocation'
$hold = InputCall 'DisableInput' 3050 (-1600)
$show = ViewTarget 3350 (-1600)
(Get-Pin $show 'BlendTime').Default = '0.0'
Connect (Self-Node 3150 (-1350)) 'self' $show 'NewViewTarget'
$seVolume = Op 'Multiply' 'Multiply_DoubleDouble' (GiGet $cast 'SE Volume' 'real' 'double' 3450 (-1200)) 'SE Volume' (GiGet $cast 'Master Volume' 'real' 'double' 3450 (-1100)) 'Master Volume' 3700 (-1150)
$volumes = @()
$sx = 3700
foreach ($name in 'ClunkSound', 'HissSound', 'SpinSound') {
  $v = New-Call $AUDIO 'SetVolumeMultiplier' $false $sx (-1600)
  Add-Pin $v 'self' 'in' 'object' '' $AUDIO
  Add-Pin $v 'NewVolumeMultiplier' 'in' 'real' 'float'
  Connect (Comp $name $AUDIO ($sx - 200) (-1400)) $name $v 'self'
  Connect $seVolume 'ReturnValue' $v 'NewVolumeMultiplier'
  $volumes += $v
  $sx += 300
}
$wait = Delay '1.0' 4650 (-1600)
Connect (Real 'OpenDelay' 4500 (-1400)) 'OpenDelay' $wait 'Duration'
$clunk = Sound 'Play' 'ClunkSound' 4950 (-1600)
$hiss = Sound 'Play' 'HissSound' 5250 (-1600)
$puff = Start-Emitter 'SteamBurst' 5550 (-1600)
$spin = Sound 'Play' 'SpinSound' 5850 (-1600)
# The gear and its axle hang under the floor: hidden in game unless it is bringing the player up (the user, 2026-11-18).
$hideFirst = Hide-Lift 'true' 100 (-1900)
$showGear = Hide-Lift 'false' 1150 (-1900)
# Silence while it plays (the user, 2026-11-18): ArrivalMix (SM_GearArrivalMute, setup_gear_arrival_sound.py) turns
# every sound but the gear's own to 0, pushed at once (before the player is set up, so no BGM slips out) and popped
# when the gear lands and the player takes over (not later: no pausing while the game is silent).
$SOUND_MIX = "/Script/CoreUObject.Class'/Script/Engine.SoundMix'"
function Sound-Mix($func, [double]$x, [double]$y) {
  $n = New-Call $STATICS $func $false $x $y
  Add-Pin $n 'InSoundMixModifier' 'in' 'object' '' $SOUND_MIX
  Connect (New-VarGet 'ArrivalMix' $null 'object' '' $SOUND_MIX ($x - 200) ($y + 200)) 'ArrivalMix' $n 'InSoundMixModifier'
  return $n
}
$hush = Sound-Mix 'PushSoundMixModifier' 1150 (-2200)
# Nothing can be done while it plays (the user, 2026-11-18): the controller's own input is off too, so the pause menu
# can't open (pausing while the mix had the game silent left the BGM dead afterwards). Back on when the gear lands.
function Controller-Input($func, [double]$x, [double]$y) {
  $n = New-Call $ACTOR $func $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR
  Add-Pin $n 'PlayerController' 'in' 'object' '' $CONTROLLER
  Connect (Controller ($x - 200) ($y + 200)) 'ReturnValue' $n 'self'
  Connect (Controller ($x - 200) ($y + 300)) 'ReturnValue' $n 'PlayerController'
  return $n
}
$freeze = Controller-Input 'DisableInput' 1150 (-2500)
# Showing Lift showed OnGear's box outline too: hide that again.
$boxHidden = New-Call $SCENE 'SetHiddenInGame' $false 1400 (-2200)
Add-Pin $boxHidden 'self' 'in' 'object' '' $SCENE
Add-Pin $boxHidden 'NewHidden' 'in' 'bool' '' $null 'true'
Add-Pin $boxHidden 'bPropagateToChildren' 'in' 'bool' '' $null 'false'
Connect (Comp 'OnGear' $BOX 1200 (-2000)) 'OnGear' $boxHidden 'self'
Connect $begin 'then' $hideFirst 'execute'
Connect $hideFirst 'then' $cast 'execute'
Connect $cast 'then' $came 'execute'
Connect $came 'then' $clear 'execute'
$unblock = Block-Hole 'NoCollision' 1650 (-2200)   # the gear has to come up through it
Chain (@($clear, $freeze, $hush, $settle, $showGear, $boxHidden, $unblock, $arriving, $arriveAt, $put, $hold, $show) + @($volumes) + @($wait, $clunk, $hiss, $puff, $spin))

# ===== Tick =====
$tick = Event 'ReceiveTick' 0 0
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$active = New-Branch 250 0
Connect (Bool 'Arriving' 100 200) 'Arriving' $active 'Condition'
Connect $tick 'then' $active 'execute'

# --- the numbers (pure) ---
$since = Op 'Subtract' 'Subtract_DoubleDouble' (Now 200 600) 'ReturnValue' (Real 'ArriveAt' 200 700) 'ArriveAt' 400 600
$openDelay = Real 'OpenDelay' 400 800
$lidSeconds = Real 'LidSeconds' 400 900
$t1 = Op 'Subtract' 'Subtract_DoubleDouble' $since 'ReturnValue' $openDelay 'OpenDelay' 600 600
$lidOpen = Clamp01 (Op 'Divide' 'Divide_DoubleDouble' $t1 'ReturnValue' $lidSeconds 'LidSeconds' 800 600) 'ReturnValue' 1000 600
$lead = Op 'Multiply' 'Multiply_DoubleDouble' $lidSeconds 'LidSeconds' $null '0.6' 600 800
$t2 = Op 'Subtract' 'Subtract_DoubleDouble' $t1 'ReturnValue' $lead 'ReturnValue' 800 800
$rise = Clamp01 (Op 'Divide' 'Divide_DoubleDouble' $t2 'ReturnValue' (Real 'RiseSeconds' 800 950) 'RiseSeconds' 1000 800) 'ReturnValue' 1200 800
$depth = Real 'Depth' 1200 1000
$landZ = Real 'LandZ' 1200 1100
$riseLeft = Op 'Subtract' 'Subtract_DoubleDouble' $null '1.0' (Ease $rise 'ReturnValue' 1400 800) 'ReturnValue' 1650 800
$upDrop = Op 'Multiply' 'Multiply_DoubleDouble' $depth 'Depth' $riseLeft 'ReturnValue' 1850 850
$upH = Op 'Subtract' 'Subtract_DoubleDouble' $landZ 'LandZ' $upDrop 'ReturnValue' 2050 850
$downSince = Op 'Subtract' 'Subtract_DoubleDouble' (Now 200 1300) 'ReturnValue' (Real 'DownAt' 200 1400) 'DownAt' 400 1300
$downSeconds = Real 'DownSeconds' 400 1500
$down = Clamp01 (Op 'Divide' 'Divide_DoubleDouble' $downSince 'ReturnValue' $downSeconds 'DownSeconds' 600 1300) 'ReturnValue' 800 1300
$downDrop = Op 'Multiply' 'Multiply_DoubleDouble' $depth 'Depth' (Ease $down 'ReturnValue' 1000 1300) 'ReturnValue' 1850 1250
$downH = Op 'Subtract' 'Subtract_DoubleDouble' $landZ 'LandZ' $downDrop 'ReturnValue' 2050 1250
$closeLead = Op 'Multiply' 'Multiply_DoubleDouble' $downSeconds 'DownSeconds' $null '0.55' 600 1500
$t3 = Op 'Subtract' 'Subtract_DoubleDouble' $downSince 'ReturnValue' $closeLead 'ReturnValue' 800 1500
$closing = Clamp01 (Op 'Divide' 'Divide_DoubleDouble' $t3 'ReturnValue' $lidSeconds 'LidSeconds' 1000 1500) 'ReturnValue' 1200 1500
$lidClose = Op 'Subtract' 'Subtract_DoubleDouble' $null '1.0' $closing 'ReturnValue' 1400 1500
$goingDown = Bool 'GoingDown' 2050 1400
$h = Pick $downH 'ReturnValue' $upH 'ReturnValue' $goingDown 'GoingDown' 2300 1000
$lid = Pick $lidClose 'ReturnValue' $lidOpen 'ReturnValue' $goingDown 'GoingDown' 2300 1450
# the halves: sink over the first quarter, slide over the rest
$sinkPart = Clamp01 (Op 'Multiply' 'Multiply_DoubleDouble' $lid 'ReturnValue' $null '4.0' 2550 1450) 'ReturnValue' 2750 1450
$sinkZ = Op 'Multiply' 'Multiply_DoubleDouble' $sinkPart 'ReturnValue' (Real 'LidSink' 2750 1600) 'LidSink' 2950 1450
$sinkNeg = Op 'Multiply' 'Multiply_DoubleDouble' $sinkZ 'ReturnValue' $null '-1.0' 3150 1450
$slidePart = Clamp01 (Op 'Divide' 'Divide_DoubleDouble' (Op 'Subtract' 'Subtract_DoubleDouble' $lid 'ReturnValue' $null '0.25' 2550 1700) 'ReturnValue' $null '0.75' 2750 1700) 'ReturnValue' 2950 1700
$slideY = Op 'Multiply' 'Multiply_DoubleDouble' (Ease $slidePart 'ReturnValue' 3150 1700) 'ReturnValue' (Real 'LidSlide' 3150 1850) 'LidSlide' 3400 1700
$slideNeg = Op 'Multiply' 'Multiply_DoubleDouble' $slideY 'ReturnValue' $null '-1.0' 3600 1750

# --- moving it all ---
$liftAt = MakeVec '0.0' '0.0' @($h, 'ReturnValue') 2550 1000
$moveLift = Place 'Lift' $SCENE $liftAt 600 0
$plusAt = MakeVec '0.0' @($slideY, 'ReturnValue') @($sinkNeg, 'ReturnValue') 3800 1500
$movePlus = Place 'LidPlus' $STATIC_MESH $plusAt 900 0
$minusAt = MakeVec '0.0' @($slideNeg, 'ReturnValue') @($sinkNeg, 'ReturnValue') 3800 1700
$moveMinus = Place 'LidMinus' $STATIC_MESH $minusAt 1200 0
# the gear turns except while it waits at the top (Landed and not GoingDown)
$waiting = Both (Bool 'Landed' 1300 400) 'Landed' (Not $goingDown 'GoingDown' 1300 500) 'ReturnValue' 'BooleanAND' 1500 450
$turning = Pick $null '0.0' $null '1.0' $waiting 'ReturnValue' 1700 450
$angle = Op 'Multiply' 'Multiply_DoubleDouble' (Op 'Multiply' 'Multiply_DoubleDouble' (Real 'SpinSpeed' 1500 300) 'SpinSpeed' $tick 'DeltaSeconds' 1700 300) 'ReturnValue' $turning 'ReturnValue' 1900 350
$rot = New-Call $MATH 'MakeRotator' $true 2050 300
Add-Pin $rot 'Roll' 'in' 'real' 'float' $null '0.0'
Add-Pin $rot 'Pitch' 'in' 'real' 'float' $null '0.0'
Add-Pin $rot 'Yaw' 'in' 'real' 'float'
Add-Pin $rot 'ReturnValue' 'out' 'struct' '' $ROTATOR
Connect $angle 'ReturnValue' $rot 'Yaw'
$turn = New-Call $SCENE 'K2_AddLocalRotation' $false 1500 0
Add-Pin $turn 'self' 'in' 'object' '' $SCENE
Add-Pin $turn 'DeltaRotation' 'in' 'struct' '' $ROTATOR
Add-Pin $turn 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $turn 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $turn 'bTeleport' 'in' 'bool' '' $null 'false'
Connect (Comp 'Gear' $STATIC_MESH 1300 200) 'Gear' $turn 'self'
Connect $rot 'ReturnValue' $turn 'DeltaRotation'
Connect $active 'then' $moveLift 'execute'
Chain @($moveLift, $movePlus, $moveMinus, $turn)

# --- what happens next ---
$downward = New-Branch 1800 0
Connect $goingDown 'GoingDown' $downward 'Condition'
Connect $turn 'then' $downward 'execute'
# going up / waiting
$landed = New-Branch 2100 (-400)
Connect (Bool 'Landed' 1950 (-250)) 'Landed' $landed 'Condition'
Connect $downward 'else' $landed 'execute'
$arrived = New-Branch 2400 (-700)
Connect (Op 'GreaterEqual' 'GreaterEqual_DoubleDouble' $rise 'ReturnValue' $null '1.0' 2250 (-550) 'bool') 'ReturnValue' $arrived 'Condition'
Connect $landed 'else' $arrived 'execute'
$setLanded = SetSelf 'Landed' 'bool' 'true' 2650 (-700)
$offFirst = SetReal 'OffSince' 2900 (-700)
Connect (Now 2800 (-550)) 'ReturnValue' $offFirst 'OffSince'
$back = ViewTarget 3200 (-700)
Connect (Player 3000 (-500)) 'ReturnValue' $back 'NewViewTarget'
$free = InputCall 'EnableInput' 3500 (-700)
$quiet = Sound 'Stop' 'SpinSound' 3800 (-700)
$unfreeze = Controller-Input 'EnableInput' 4100 (-700)
$sound = Sound-Mix 'PopSoundMixModifier' 4400 (-700)   # the game's sounds come back over 2 s as the player takes over
Connect $arrived 'then' $setLanded 'execute'
Chain @($setLanded, $offFirst, $back, $free, $quiet, $unfreeze, $sound)
# waiting for the player to step off
$onGear = New-Call $PRIMITIVE 'IsOverlappingActor' $true 2300 (-150)
Add-Pin $onGear 'self' 'in' 'object' '' $PRIMITIVE
Add-Pin $onGear 'Other' 'in' 'object' '' $ACTOR
Add-Pin $onGear 'ReturnValue' 'out' 'bool'
Connect (Comp 'OnGear' $BOX 2100 (-150)) 'OnGear' $onGear 'self'
Connect (Player 2100 (-50)) 'ReturnValue' $onGear 'Other'
$still = New-Branch 2450 (-400)
Connect $onGear 'ReturnValue' $still 'Condition'
Connect $landed 'then' $still 'execute'
$keep = SetReal 'OffSince' 2750 (-400)
Connect (Now 2600 (-250)) 'ReturnValue' $keep 'OffSince'
Connect $still 'then' $keep 'execute'
$gone = New-Branch 2750 (-150)
$away = Op 'Subtract' 'Subtract_DoubleDouble' (Now 2450 50) 'ReturnValue' (Real 'OffSince' 2450 150) 'OffSince' 2600 50
Connect (Op 'Greater' 'Greater_DoubleDouble' $away 'ReturnValue' $null '1.0' 2650 (-50) 'bool') 'ReturnValue' $gone 'Condition'
Connect $still 'else' $gone 'execute'
$startDown = SetSelf 'GoingDown' 'bool' 'true' 3000 (-150)
$downAt = SetReal 'DownAt' 3250 (-150)
Connect (Now 3100 0) 'ReturnValue' $downAt 'DownAt'
$spinAgain = Sound 'Play' 'SpinSound' 3550 (-150)
Connect $gone 'then' $startDown 'execute'
Chain @($startDown, $downAt, $spinAgain)
# going down: the seal shut
$shut = New-Branch 2100 300
Connect (Op 'LessEqual' 'LessEqual_DoubleDouble' $lidClose 'ReturnValue' $null '0.0' 1950 450 'bool') 'ReturnValue' $shut 'Condition'
Connect $downward 'then' $shut 'execute'
$closed = SetSelf 'Closed' 'bool' 'true' 2400 300
$rest = SetSelf 'Arriving' 'bool' 'false' 2650 300
$stop = Sound 'Stop' 'SpinSound' 2900 300
$thud = Sound 'Play' 'ClunkSound' 3200 300
$lastPuff = Start-Emitter 'SteamBurst' 3500 300
# Done: the gear and axle gone (hidden, and the gear no longer collides).
$hideAgain = Hide-Lift 'true' 3800 300
$noBlock = Collide 'Gear' 'NoCollision' 4100 300
Connect $shut 'then' $closed 'execute'
$reblock = Block-Hole 'QueryAndPhysics' 4400 300   # the shut seal is solid again
Chain @($closed, $rest, $stop, $thud, $lastPuff, $hideAgain, $noBlock, $reblock)
Write-Graph 'BP_GearArrival_EventGraph.txt'
