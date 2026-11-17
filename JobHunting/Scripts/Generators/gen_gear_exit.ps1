param([string]$OutDir)
# Paste text for BP_GearExit (components and variables from setup_gear_exit.py):
#   Tick, not Started: once the player overlaps Center -> Started, StartedAt = now, the player's input off.
#   Tick, Started: Gear turns SpinSpeed degrees a second; h = RiseHeight * ease(clamp((now - StartedAt) / RiseSeconds));
#   Lift at (0, 0, h); Axle (a 100 cm cylinder about its middle) at h / 2, h tall. Once the rise is done, and not yet
#   Leaving: Leaving, the item effects saved, ChangingArea, black, NextLevel (BP_AreaExit's ending).
if (-not $OutDir) { throw 'OutDir is required' }
$lightGen = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_heaven_light.ps1') -Encoding UTF8
$cut = ($lightGen | Select-String -Pattern '^# ===== BP_LightBeam' | Select-Object -First 1).LineNumber - 1
$helpers = $lightGen[1..($cut - 1)] -join "`n"
. ([ScriptBlock]::Create($helpers))

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

Reset-Graph 100
$tick = Event 'ReceiveTick' 0 0
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$started = New-Branch 300 0
Connect (Bool 'Started' 150 200) 'Started' $started 'Condition'
Connect $tick 'then' $started 'execute'

# ----- not started: waiting for the player on the ring -----
$onRing = New-Branch 600 -600
$inCenter = New-Call $PRIMITIVE 'IsOverlappingActor' $true 450 -350
Add-Pin $inCenter 'self' 'in' 'object' '' $PRIMITIVE
Add-Pin $inCenter 'Other' 'in' 'object' '' $ACTOR
Add-Pin $inCenter 'ReturnValue' 'out' 'bool'
Connect (Comp 'Center' $BOX 250 -350) 'Center' $inCenter 'self'
Connect (Player 250 -250) 'ReturnValue' $inCenter 'Other'
Connect $inCenter 'ReturnValue' $onRing 'Condition'
Connect $started 'else' $onRing 'execute'
$go = SetSelf 'Started' 'bool' 'true' 850 -600
$at = SetReal 'StartedAt' 1100 -600
Connect (Now 950 -400) 'ReturnValue' $at 'StartedAt'
$hold = InputCall 'DisableInput' 1400 -600
# The view moves over to the gear's own Camera.
$view = ViewTarget 1700 -600
$self = New-Node '/Script/BlueprintGraph.K2Node_Self' @() 1550 -300
Add-Pin $self 'self' 'out' 'object' '' $ACTOR
Connect $self 'self' $view 'NewViewTarget'
# Steam bursts out at once; the jets and sparks start as the gear starts to rise, StartDelay later.
$EMITTER = "/Script/CoreUObject.Class'/Script/Effekseer.EffekseerEmitterComponent'"
$ACTOR_COMPONENT = "/Script/CoreUObject.Class'/Script/Engine.ActorComponent'"
function Start-Emitter($componentName, [double]$x, [double]$y) {
  $n = New-Call $ACTOR_COMPONENT 'Activate' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR_COMPONENT
  Add-Pin $n 'bReset' 'in' 'bool' '' $null 'true'
  Connect (Comp $componentName $EMITTER ($x - 200) ($y + 200)) $componentName $n 'self'
  return $n
}
# Sounds (setup_gear_sounds.py): each at SE Volume x Master Volume; the clunk, the hiss and the turning at once,
# the sparks with the rise (SparkSound sits at floor level, so it fades as the gear carries the player away).
$AUDIO = "/Script/CoreUObject.Class'/Script/Engine.AudioComponent'"
$soundCast = GameInstance 2000 (-600)
$seVolume = Op 'Multiply' 'Multiply_DoubleDouble' (GiGet $soundCast 'SE Volume' 'real' 'double' 1950 (-350)) 'SE Volume' (GiGet $soundCast 'Master Volume' 'real' 'double' 1950 (-250)) 'Master Volume' 2200 (-300)
function Sound-Volume($componentName, [double]$x, [double]$y) {
  $n = New-Call $AUDIO 'SetVolumeMultiplier' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $AUDIO
  Add-Pin $n 'NewVolumeMultiplier' 'in' 'real' 'float'
  Connect (Comp $componentName $AUDIO ($x - 200) ($y + 200)) $componentName $n 'self'
  Connect $seVolume 'ReturnValue' $n 'NewVolumeMultiplier'
  return $n
}
function Sound-Play($componentName, [double]$x, [double]$y) {
  $n = New-Call $AUDIO 'Play' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $AUDIO
  Add-Pin $n 'StartTime' 'in' 'real' 'float' $null '0.0'
  Connect (Comp $componentName $AUDIO ($x - 200) ($y + 200)) $componentName $n 'self'
  return $n
}
$volumes = @()
$sx = 2350
foreach ($name in 'ClunkSound', 'HissSound', 'SpinSound', 'SparkSound') { $volumes += Sound-Volume $name $sx (-600); $sx += 300 }
$clunk = Sound-Play 'ClunkSound' 3550 (-600)
$hiss = Sound-Play 'HissSound' 3850 (-600)
$spin = Sound-Play 'SpinSound' 4150 (-600)
$puff = Start-Emitter 'SteamBurst' 4450 (-600)
$ramp = Delay '0.6' 4700 (-600)
Connect (Real 'StartDelay' 4550 (-400)) 'StartDelay' $ramp 'Duration'
$jets = Start-Emitter 'RiseFx' 4950 (-600)
$crackle = Sound-Play 'SparkSound' 5250 (-600)
Connect $onRing 'then' $go 'execute'
Chain @($go, $at, $hold, $view, $soundCast)
Connect $soundCast 'then' $volumes[0] 'execute'
Chain (@($volumes) + @($clunk, $hiss, $spin, $puff, $ramp, $jets, $crackle))

# ----- started: turn, rise, stretch the axle -----
$angle = Op 'Multiply' 'Multiply_DoubleDouble' (Real 'SpinSpeed' 400 300) 'SpinSpeed' $tick 'DeltaSeconds' 600 300
$rot = New-Call $MATH 'MakeRotator' $true 800 300
Add-Pin $rot 'Roll' 'in' 'real' 'float' $null '0.0'
Add-Pin $rot 'Pitch' 'in' 'real' 'float' $null '0.0'
Add-Pin $rot 'Yaw' 'in' 'real' 'float'
Add-Pin $rot 'ReturnValue' 'out' 'struct' '' $ROTATOR
Connect $angle 'ReturnValue' $rot 'Yaw'
$turn = New-Call $SCENE 'K2_AddLocalRotation' $false 1000 0
Add-Pin $turn 'self' 'in' 'object' '' $SCENE
Add-Pin $turn 'DeltaRotation' 'in' 'struct' '' $ROTATOR
Add-Pin $turn 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $turn 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $turn 'bTeleport' 'in' 'bool' '' $null 'false'
Connect (Comp 'Gear' $STATIC_MESH 800 150) 'Gear' $turn 'self'
Connect $rot 'ReturnValue' $turn 'DeltaRotation'
Connect $started 'then' $turn 'execute'

# alpha = clamp((now - StartedAt) / RiseSeconds, 0, 1); h = RiseHeight * ease(alpha).
$since = Op 'Subtract' 'Subtract_DoubleDouble' (Now 400 700) 'ReturnValue' (Real 'StartedAt' 400 800) 'StartedAt' 600 700
$late = Op 'Subtract' 'Subtract_DoubleDouble' $since 'ReturnValue' (Real 'StartDelay' 600 950) 'StartDelay' 750 600
$part = Op 'Divide' 'Divide_DoubleDouble' $late 'ReturnValue' (Real 'RiseSeconds' 600 850) 'RiseSeconds' 900 700
$alpha = MathCall 'FClamp' @('Value', 'Min', 'Max') 'real' 'double' 'real' 'double' 1000 700
(Get-Pin $alpha 'Min').Default = '0.0'
(Get-Pin $alpha 'Max').Default = '1.0'
Connect $part 'ReturnValue' $alpha 'Value'
$eased = New-Call $MATH 'FInterpEaseInOut' $true 1200 700
Add-Pin $eased 'A' 'in' 'real' 'double' $null '0.0'
Add-Pin $eased 'B' 'in' 'real' 'double' $null '1.0'
Add-Pin $eased 'Alpha' 'in' 'real' 'double'
Add-Pin $eased 'Exponent' 'in' 'real' 'double' $null '2.0'
Add-Pin $eased 'ReturnValue' 'out' 'real' 'double'
Connect $alpha 'ReturnValue' $eased 'Alpha'
$h = Op 'Multiply' 'Multiply_DoubleDouble' $eased 'ReturnValue' (Real 'RiseHeight' 1200 900) 'RiseHeight' 1450 700

$liftAt = MakeVec '0.0' '0.0' @($h, 'ReturnValue') 1450 300
$rise = Place 'Lift' $SCENE $liftAt 1650 0
$half = Op 'Multiply' 'Multiply_DoubleDouble' $h 'ReturnValue' $null '0.5' 1700 700
$axleAt = MakeVec '0.0' '0.0' @($half, 'ReturnValue') 1900 300
$axleMove = Place 'Axle' $STATIC_MESH $axleAt 2100 0
$tall = Op 'Multiply' 'Multiply_DoubleDouble' $h 'ReturnValue' $null '0.01' 1700 850
$tallAtLeast = MathCall 'FMax' @('A', 'B') 'real' 'double' 'real' 'double' 1900 850
Connect $tall 'ReturnValue' $tallAtLeast 'A'
(Get-Pin $tallAtLeast 'B').Default = '0.01'
$size = MakeVec '0.9' '0.9' @($tallAtLeast, 'ReturnValue') 2150 750
$stretch = New-Call $SCENE 'SetRelativeScale3D' $false 2400 0
Add-Pin $stretch 'self' 'in' 'object' '' $SCENE
Add-Pin $stretch 'NewScale3D' 'in' 'struct' '' $VECTOR
Connect (Comp 'Axle' $STATIC_MESH 2200 200) 'Axle' $stretch 'self'
Connect $size 'ReturnValue' $stretch 'NewScale3D'
Chain @($turn, $rise, $axleMove, $stretch)

# ----- the camera: swing round, from low to high, draw back; a clunk at the start -----
$pitch = Op 'Multiply' 'Multiply_DoubleDouble' $eased 'ReturnValue' $null '-40.0' 2500 1100
$pitchAt = Op 'Add' 'Add_DoubleDouble' $pitch 'ReturnValue' $null '15.0' 2700 1100
$yaw = Op 'Multiply' 'Multiply_DoubleDouble' $eased 'ReturnValue' (Real 'OrbitDegrees' 2300 1300) 'OrbitDegrees' 2500 1250
$yawAt = Op 'Add' 'Add_DoubleDouble' $yaw 'ReturnValue' $null '180.0' 2700 1250
$swingRot = New-Call $MATH 'MakeRotator' $true 2900 1100
Add-Pin $swingRot 'Roll' 'in' 'real' 'float' $null '0.0'
Add-Pin $swingRot 'Pitch' 'in' 'real' 'float'
Add-Pin $swingRot 'Yaw' 'in' 'real' 'float'
Add-Pin $swingRot 'ReturnValue' 'out' 'struct' '' $ROTATOR
Connect $pitchAt 'ReturnValue' $swingRot 'Pitch'
Connect $yawAt 'ReturnValue' $swingRot 'Yaw'
$swing = New-Call $SCENE 'K2_SetRelativeRotation' $false 2650 0
Add-Pin $swing 'self' 'in' 'object' '' $SCENE
Add-Pin $swing 'NewRotation' 'in' 'struct' '' $ROTATOR
Add-Pin $swing 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $swing 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $swing 'bTeleport' 'in' 'bool' '' $null 'false'
Connect (Comp 'CamPivot' $SCENE 2450 200) 'CamPivot' $swing 'self'
Connect $swingRot 'ReturnValue' $swing 'NewRotation'
$ARM = "/Script/CoreUObject.Class'/Script/Engine.SpringArmComponent'"
$CAMERA = "/Script/CoreUObject.Class'/Script/Engine.CameraComponent'"
$reach = Op 'Multiply' 'Multiply_DoubleDouble' $eased 'ReturnValue' $null '500.0' 3000 1400
$reachAt = Op 'Add' 'Add_DoubleDouble' $reach 'ReturnValue' $null '600.0' 3200 1400
$length = New-VarSet 'TargetArmLength' $ARM 'real' $null 3000 0
(Get-Pin $length 'TargetArmLength').Sub = 'float'; (Get-Pin $length 'Output_Get').Sub = 'float'
Connect (Comp 'CamArm' $ARM 2800 250) 'CamArm' $length 'self'
Connect $reachAt 'ReturnValue' $length 'TargetArmLength'
# shake = ShakeSize * max(0, 1 - since / 0.8) * sin(since * 45), sideways and a little up.
$fadeOut = Op 'Divide' 'Divide_DoubleDouble' $since 'ReturnValue' $null '0.8' 3300 1600
$left = Op 'Subtract' 'Subtract_DoubleDouble' $null '1.0' $fadeOut 'ReturnValue' 3500 1600
$kept = MathCall 'FMax' @('A', 'B') 'real' 'double' 'real' 'double' 3700 1600
Connect $left 'ReturnValue' $kept 'A'
(Get-Pin $kept 'B').Default = '0.0'
$fast = Op 'Multiply' 'Multiply_DoubleDouble' $since 'ReturnValue' $null '45.0' 3300 1800
$wave = MathCall 'Sin' @('A') 'real' 'double' 'real' 'double' 3500 1800
Connect $fast 'ReturnValue' $wave 'A'
$amount = Op 'Multiply' 'Multiply_DoubleDouble' $kept 'ReturnValue' (Real 'ShakeSize' 3700 1800) 'ShakeSize' 3900 1650
$shake = Op 'Multiply' 'Multiply_DoubleDouble' $amount 'ReturnValue' $wave 'ReturnValue' 4100 1650
$shakeUp = Op 'Multiply' 'Multiply_DoubleDouble' $shake 'ReturnValue' $null '0.7' 4300 1750
$shakeAt = MakeVec '0.0' @($shake, 'ReturnValue') @($shakeUp, 'ReturnValue') 4500 1600
$jolt = Place 'Camera' $CAMERA $shakeAt 3300 0
Chain @($stretch, $swing, $length, $jolt)

# ----- at the top: BP_AreaExit's ending -----
$top = New-Branch 2700 0
$done = Op 'GreaterEqual' 'GreaterEqual_DoubleDouble' $alpha 'ReturnValue' $null '0.85' 2500 450 'bool'   # black from 85 % up, before the very top
Connect $done 'ReturnValue' $top 'Condition'
$once = New-Branch 2950 0
Connect (Bool 'Leaving' 2800 200) 'Leaving' $once 'Condition'
$leaving = SetSelf 'Leaving' 'bool' 'true' 3200 0
$cast = GameInstance 3500 0
$saved = SaveStats $cast 3800 0
$moving = GiSet $cast 'ChangingArea' 'bool' '' 5000 0 'true'
$dark = Fade '0.0' '1.0' '0.6' 'true' 5250 0
$wait = Delay '0.6' 5750 0
$open = OpenLevel 6000 0
Connect (New-VarGet 'NextLevel' $null 'name' '' $null 5800 200) 'NextLevel' $open 'LevelName'
Connect $jolt 'then' $top 'execute'
Connect $top 'then' $once 'execute'
Connect $once 'else' $leaving 'execute'
Chain @($leaving, $cast)
Connect $cast 'then' $saved[0] 'execute'
Chain @($saved[1], $moving, $dark, $wait, $open)
Write-Graph 'BP_GearExit_EventGraph.txt'
