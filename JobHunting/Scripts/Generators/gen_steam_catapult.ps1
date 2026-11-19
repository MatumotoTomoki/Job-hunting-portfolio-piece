param([string]$OutDir)
# Paste text for area 2 -> 3 (components and variables from setup_steam_catapult.py):
#   BP_SteamCatapult_EventGraph.txt  Tick, not Started: once the player is in PadTrigger -> Started, StartedAt; the
#       controller's and the pawn's input off (no pause), the player stood on the ring's middle, stopped; the sounds
#       at SE Volume x Master Volume; the clunk, the charge sound, the vents' steam.
#     Tick, Started (t = now - StartedAt): the piston (pad) sinks CompressDepth over ChargeSeconds (eased), then kicks
#       up to PadKick above where it began in 0.12 s. At t >= ChargeSeconds, once: Launched, LaunchCharacter straight up
#       at LaunchSpeed, the boom, the blast, the vents and the charge sound stop. At t >= ChargeSeconds + FadeAfter,
#       once: Leaving, the item effects saved, ChangingArea and CatapultArrival set, white over 0.8 s, NextLevel.
#   BP_SkyLanding_EventGraph.txt  Begin Play (a moment later), only if CatapultArrival: clear it; input off; the
#       screen clears from white over 1.5 s; GravityScale -> FallGravity (the old one kept); the player DropHeight
#       above this actor, stopped; Falling, FallAt. Tick while Falling, 0.3 s on and the player on the ground: Falling
#       off, gravity back, a cloud puff at their feet, the landing sound, input back.
if (-not $OutDir) { throw 'OutDir is required' }
$lightGen = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_heaven_light.ps1') -Encoding UTF8
$cut = ($lightGen | Select-String -Pattern '^# ===== BP_LightBeam' | Select-Object -First 1).LineNumber - 1
$helpers = $lightGen[1..($cut - 1)] -join "`n"
. ([ScriptBlock]::Create($helpers))

$EMITTER = "/Script/CoreUObject.Class'/Script/Effekseer.EffekseerEmitterComponent'"
$ACTOR_COMPONENT = "/Script/CoreUObject.Class'/Script/Engine.ActorComponent'"
$AUDIO = "/Script/CoreUObject.Class'/Script/Engine.AudioComponent'"
$MOVEMENT_BASE = "/Script/CoreUObject.Class'/Script/Engine.MovementComponent'"
$WHITE = '(R=1.000000,G=1.000000,B=1.000000,A=1.000000)'

function MakeVec($xPin, $yPin, $zPin, [double]$x, [double]$y) {
  $n = New-Call $MATH 'MakeVector' $true $x $y
  foreach ($pair in @(@('X', $xPin), @('Y', $yPin), @('Z', $zPin))) {
    if ($pair[1] -is [string]) { Add-Pin $n $pair[0] 'in' 'real' 'double' $null $pair[1] }
    else { Add-Pin $n $pair[0] 'in' 'real' 'double'; Connect $pair[1][0] $pair[1][1] $n $pair[0] }
  }
  Add-Pin $n 'ReturnValue' 'out' 'struct' '' $VECTOR
  return $n
}
function AddVec($a, $aPin, $b, $bPin, [double]$x, [double]$y) {
  $n = New-Operator 'Add' 'Add_VectorVector' 'struct' '' 'struct' $x $y
  foreach ($pin in 'A', 'B', 'ReturnValue') { (Get-Pin $n $pin).Obj = $VECTOR }
  Connect $a $aPin $n 'A'
  Connect $b $bPin $n 'B'
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
function Emit($func, $componentName, [double]$x, [double]$y) {
  $n = New-Call $ACTOR_COMPONENT $func $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR_COMPONENT
  if ($func -eq 'Activate') { Add-Pin $n 'bReset' 'in' 'bool' '' $null 'true' }
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
function Volume($componentName, $volume, [double]$x, [double]$y) {
  $n = New-Call $AUDIO 'SetVolumeMultiplier' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $AUDIO
  Add-Pin $n 'NewVolumeMultiplier' 'in' 'real' 'float'
  Connect (Comp $componentName $AUDIO ($x - 200) ($y + 200)) $componentName $n 'self'
  Connect $volume 'ReturnValue' $n 'NewVolumeMultiplier'
  return $n
}
function SeVolume($cast, [double]$x, [double]$y) {
  Op 'Multiply' 'Multiply_DoubleDouble' (GiGet $cast 'SE Volume' 'real' 'double' $x $y) 'SE Volume' (GiGet $cast 'Master Volume' 'real' 'double' $x ($y + 100)) 'Master Volume' ($x + 250) ($y + 50)
}
function Controller-Input($func, [double]$x, [double]$y) {
  $n = New-Call $ACTOR $func $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR
  Add-Pin $n 'PlayerController' 'in' 'object' '' $CONTROLLER
  Connect (Controller ($x - 200) ($y + 200)) 'ReturnValue' $n 'self'
  Connect (Controller ($x - 200) ($y + 300)) 'ReturnValue' $n 'PlayerController'
  return $n
}
function Put-Player($where, [double]$x, [double]$y) {
  $n = New-Call $ACTOR 'K2_SetActorLocation' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR
  Add-Pin $n 'NewLocation' 'in' 'struct' '' $VECTOR
  Add-Pin $n 'bSweep' 'in' 'bool' '' $null 'false'
  Add-Pin $n 'SweepHitResult' 'out' 'struct' '' $HIT
  Add-Pin $n 'bTeleport' 'in' 'bool' '' $null 'true'
  Add-Pin $n 'ReturnValue' 'out' 'bool'
  Connect (Player ($x - 200) ($y + 200)) 'ReturnValue' $n 'self'
  Connect $where 'ReturnValue' $n 'NewLocation'
  return $n
}
function Halt([double]$x, [double]$y) {
  $n = New-Call $MOVEMENT_BASE 'StopMovementImmediately' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $MOVEMENT_BASE
  Connect (Movement ($x - 100) ($y + 200)) 'CharacterMovement' $n 'self'
  return $n
}
function White-Fade($from, $to, $seconds, $hold, [double]$x, [double]$y) {
  $n = Fade $from $to $seconds $hold $x $y
  (Get-Pin $n 'Color').Default = $WHITE
  return $n
}

# ===== BP_SteamCatapult ====================================================================================
Reset-Graph 100
$tick = Event 'ReceiveTick' 0 0
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$started = New-Branch 250 0
Connect (Bool 'Started' 100 200) 'Started' $started 'Condition'
Connect $tick 'then' $started 'execute'

# --- waiting for the player on the ring ---
$onPad = New-Call $PRIMITIVE 'IsOverlappingActor' $true 400 (-400)
Add-Pin $onPad 'self' 'in' 'object' '' $PRIMITIVE
Add-Pin $onPad 'Other' 'in' 'object' '' $ACTOR
Add-Pin $onPad 'ReturnValue' 'out' 'bool'
Connect (Comp 'PadTrigger' $BOX 200 (-400)) 'PadTrigger' $onPad 'self'
Connect (Player 200 (-300)) 'ReturnValue' $onPad 'Other'
$stepped = New-Branch 600 (-700)
Connect $onPad 'ReturnValue' $stepped 'Condition'
Connect $started 'else' $stepped 'execute'
$go = SetSelf 'Started' 'bool' 'true' 850 (-700)
$at = SetReal 'StartedAt' 1100 (-700)
Connect (Now 1000 (-500)) 'ReturnValue' $at 'StartedAt'
$freeze = Controller-Input 'DisableInput' 1400 (-700)
$hold = InputCall 'DisableInput' 1700 (-700)
# stood on the ring's middle
$ringAt = New-Call $SCENE 'K2_GetComponentLocation' $true 1800 (-400)
Add-Pin $ringAt 'self' 'in' 'object' '' $SCENE
Add-Pin $ringAt 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect (Comp 'Ring' $STATIC_MESH 1600 (-400)) 'Ring' $ringAt 'self'
$stand = AddVec $ringAt 'ReturnValue' (MakeVec '0.0' '0.0' '98.0' 1800 (-250)) 'ReturnValue' 2050 (-350)
$snap = Put-Player $stand 2200 (-700)
$still = Halt 2500 (-700)
$cast = GameInstance 2800 (-700)
$vol = SeVolume $cast 2750 (-450)
$v1 = Volume 'ClunkSound' $vol 3100 (-700)
$v2 = Volume 'ChargeSound' $vol 3400 (-700)
$v3 = Volume 'BoomSound' $vol 3700 (-700)
$clunk = Sound 'Play' 'ClunkSound' 4000 (-700)
$charge = Sound 'Play' 'ChargeSound' 4300 (-700)
$vents = Emit 'Activate' 'ChargeFx' 4600 (-700)
Connect $stepped 'then' $go 'execute'
Chain @($go, $at, $freeze, $hold, $snap, $still, $cast)
Connect $cast 'then' $v1 'execute'
Chain @($v1, $v2, $v3, $clunk, $charge, $vents)

# --- started: the piston ---
$since = Op 'Subtract' 'Subtract_DoubleDouble' (Now 200 600) 'ReturnValue' (Real 'StartedAt' 200 700) 'StartedAt' 400 600
$chargeSeconds = Real 'ChargeSeconds' 400 800
$squeeze = Ease (Clamp01 (Op 'Divide' 'Divide_DoubleDouble' $since 'ReturnValue' $chargeSeconds 'ChargeSeconds' 600 600) 'ReturnValue' 800 600) 'ReturnValue' 1000 600
$afterCharge = Op 'Subtract' 'Subtract_DoubleDouble' $since 'ReturnValue' $chargeSeconds 'ChargeSeconds' 600 850
$kick = Clamp01 (Op 'Divide' 'Divide_DoubleDouble' $afterCharge 'ReturnValue' $null '0.12' 800 850) 'ReturnValue' 1000 850
$depth = Real 'CompressDepth' 1000 1000
$down = Op 'Multiply' 'Multiply_DoubleDouble' $depth 'CompressDepth' $squeeze 'ReturnValue' 1250 650
$reach = Op 'Add' 'Add_DoubleDouble' $depth 'CompressDepth' (Real 'PadKick' 1000 1100) 'PadKick' 1250 1000
$up = Op 'Multiply' 'Multiply_DoubleDouble' $reach 'ReturnValue' $kick 'ReturnValue' 1450 900
$z1 = Op 'Subtract' 'Subtract_DoubleDouble' $null '50.0' $down 'ReturnValue' 1450 650
$z2 = Op 'Add' 'Add_DoubleDouble' $z1 'ReturnValue' $up 'ReturnValue' 1650 750
$pistonAt = MakeVec '0.0' '0.0' @($z2, 'ReturnValue') 1850 600
$move = New-Call $SCENE 'K2_SetRelativeLocation' $false 600 0
Add-Pin $move 'self' 'in' 'object' '' $SCENE
Add-Pin $move 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $move 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $move 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $move 'bTeleport' 'in' 'bool' '' $null 'false'
Connect (Comp 'Piston' $SCENE 400 200) 'Piston' $move 'self'
Connect $pistonAt 'ReturnValue' $move 'NewLocation'
Connect $started 'then' $move 'execute'

# --- leaving (checked first: it comes FadeAfter after the launch) ---
$fadeTime = Op 'Add' 'Add_DoubleDouble' $chargeSeconds 'ChargeSeconds' (Real 'FadeAfter' 600 1300) 'FadeAfter' 800 1250
$fadeNow = New-Branch 900 0
Connect (Op 'GreaterEqual' 'GreaterEqual_DoubleDouble' $since 'ReturnValue' $fadeTime 'ReturnValue' 1000 1250 'bool') 'ReturnValue' $fadeNow 'Condition'
Connect $move 'then' $fadeNow 'execute'
$once = New-Branch 1150 (-200)
Connect (Bool 'Leaving' 1000 (-100)) 'Leaving' $once 'Condition'
Connect $fadeNow 'then' $once 'execute'
$leaving = SetSelf 'Leaving' 'bool' 'true' 1400 (-200)
$cast2 = GameInstance 1700 (-200)
$saved = SaveStats $cast2 2000 (-200)
$moving = GiSet $cast2 'ChangingArea' 'bool' '' 3200 (-200) 'true'
$flag = GiSet $cast2 'CatapultArrival' 'bool' '' 3450 (-200) 'true'
$toWhite = White-Fade '0.0' '1.0' '0.8' 'true' 3700 (-200)
$wait = Delay '0.9' 4200 (-200)
$open = OpenLevel 4450 (-200)
Connect (New-VarGet 'NextLevel' $null 'name' '' $null 4250 0) 'NextLevel' $open 'LevelName'
Connect $once 'else' $leaving 'execute'
Chain @($leaving, $cast2)
Connect $cast2 'then' $saved[0] 'execute'
Chain @($saved[1], $moving, $flag, $toWhite, $wait, $open)

# --- the launch ---
$launchNow = New-Branch 1150 300
Connect (Op 'GreaterEqual' 'GreaterEqual_DoubleDouble' $since 'ReturnValue' $chargeSeconds 'ChargeSeconds' 1000 450 'bool') 'ReturnValue' $launchNow 'Condition'
Connect $fadeNow 'else' $launchNow 'execute'
$fired = New-Branch 1400 300
Connect (Bool 'Launched' 1250 450) 'Launched' $fired 'Condition'
Connect $launchNow 'then' $fired 'execute'
$launched = SetSelf 'Launched' 'bool' 'true' 1650 300
$fling = New-Call $CHARACTER 'LaunchCharacter' $false 1950 300
Add-Pin $fling 'self' 'in' 'object' '' $CHARACTER
Add-Pin $fling 'LaunchVelocity' 'in' 'struct' '' $VECTOR
Add-Pin $fling 'bXYOverride' 'in' 'bool' '' $null 'true'
Add-Pin $fling 'bZOverride' 'in' 'bool' '' $null 'true'
Connect (Player 1750 500) 'ReturnValue' $fling 'self'
Connect (MakeVec '0.0' '0.0' @((Real 'LaunchSpeed' 1600 650), 'LaunchSpeed') 1800 600) 'ReturnValue' $fling 'LaunchVelocity'
$boom = Sound 'Play' 'BoomSound' 2250 300
$blast = Emit 'Activate' 'BlastFx' 2550 300
$ventsOff = Emit 'Deactivate' 'ChargeFx' 2850 300
$chargeOff = Sound 'Stop' 'ChargeSound' 3150 300
Connect $fired 'else' $launched 'execute'
Chain @($launched, $fling, $boom, $blast, $ventsOff, $chargeOff)
Write-Graph 'BP_SteamCatapult_EventGraph.txt'

# ===== BP_SkyLanding =======================================================================================
Reset-Graph 100
$begin = Event 'ReceiveBeginPlay' 0 0
$settle = Delay '0.05' 250 0
$cast = GameInstance 550 0
$came = New-Branch 850 0
Connect (GiGet $cast 'CatapultArrival' 'bool' '' 700 200) 'CatapultArrival' $came 'Condition'
$clear = GiSet $cast 'CatapultArrival' 'bool' '' 1100 0 'false'
$freeze = Controller-Input 'DisableInput' 1400 0
$hold = InputCall 'DisableInput' 1700 0
$clearWhite = White-Fade '1.0' '0.0' '1.5' 'false' 2000 0
$gravityNow = New-VarGet 'GravityScale' $CHAR_MOVE 'real' 'float' $null 2300 300
Connect (Movement 2100 300) 'CharacterMovement' $gravityNow 'self'
$keepGravity = SetReal 'OldGravity' 2500 0
Connect $gravityNow 'GravityScale' $keepGravity 'OldGravity'
$light = New-VarSet 'GravityScale' $CHAR_MOVE 'real' $null 2800 0
(Get-Pin $light 'GravityScale').Sub = 'float'; (Get-Pin $light 'Output_Get').Sub = 'float'
Connect (Movement 2600 300) 'CharacterMovement' $light 'self'
Connect (Real 'FallGravity' 2600 400) 'FallGravity' $light 'GravityScale'
$here = New-Call $ACTOR 'K2_GetActorLocation' $true 2900 450
Add-Pin $here 'self' 'in' 'object' '' $ACTOR
Add-Pin $here 'ReturnValue' 'out' 'struct' '' $VECTOR
$high = Op 'Add' 'Add_DoubleDouble' (Real 'DropHeight' 2900 650) 'DropHeight' $null '92.0' 3100 650
$above = AddVec $here 'ReturnValue' (MakeVec '0.0' '0.0' @($high, 'ReturnValue') 3100 550) 'ReturnValue' 3300 500
$drop = Put-Player $above 3100 0
$still = Halt 3400 0
$falling = SetSelf 'Falling' 'bool' 'true' 3700 0
$fallAt = SetReal 'FallAt' 3950 0
Connect (Now 3850 200) 'ReturnValue' $fallAt 'FallAt'
Connect $begin 'then' $settle 'execute'
Connect $settle 'then' $cast 'execute'
Connect $cast 'then' $came 'execute'
Connect $came 'then' $clear 'execute'
Chain @($clear, $freeze, $hold, $clearWhite, $keepGravity, $light, $drop, $still, $falling, $fallAt)

$tick = Event 'ReceiveTick' 0 900
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$active = New-Branch 250 900
Connect (Bool 'Falling' 100 1100) 'Falling' $active 'Condition'
Connect $tick 'then' $active 'execute'
$ground = New-Call "/Script/CoreUObject.Class'/Script/Engine.CharacterMovementComponent'" 'IsMovingOnGround' $true 400 1300
Add-Pin $ground 'self' 'in' 'object' '' $CHAR_MOVE
Add-Pin $ground 'ReturnValue' 'out' 'bool'
Connect (Movement 200 1300) 'CharacterMovement' $ground 'self'
$waited = Op 'Greater' 'Greater_DoubleDouble' (Op 'Subtract' 'Subtract_DoubleDouble' (Now 200 1450) 'ReturnValue' (Real 'FallAt' 200 1550) 'FallAt' 400 1450) 'ReturnValue' $null '0.3' 600 1450 'bool'
$landedNow = Both $ground 'ReturnValue' $waited 'ReturnValue' 'BooleanAND' 750 1350
$landed = New-Branch 500 900
Connect $landedNow 'ReturnValue' $landed 'Condition'
Connect $active 'then' $landed 'execute'
$stop = SetSelf 'Falling' 'bool' 'false' 800 900
$back = New-VarSet 'GravityScale' $CHAR_MOVE 'real' $null 1100 900
(Get-Pin $back 'GravityScale').Sub = 'float'; (Get-Pin $back 'Output_Get').Sub = 'float'
Connect (Movement 900 1150) 'CharacterMovement' $back 'self'
Connect (Real 'OldGravity' 900 1250) 'OldGravity' $back 'GravityScale'
# the puff at the player's feet
$feetAt = New-Call $ACTOR 'K2_GetActorLocation' $true 1200 1300
Add-Pin $feetAt 'self' 'in' 'object' '' $ACTOR
Add-Pin $feetAt 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect (Player 1000 1400) 'ReturnValue' $feetAt 'self'
$feet = AddVec $feetAt 'ReturnValue' (MakeVec '0.0' '0.0' '-90.0' 1200 1500) 'ReturnValue' 1450 1350
$placeFx = New-Call $SCENE 'K2_SetWorldLocation' $false 1400 900
Add-Pin $placeFx 'self' 'in' 'object' '' $SCENE
Add-Pin $placeFx 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $placeFx 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $placeFx 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $placeFx 'bTeleport' 'in' 'bool' '' $null 'true'
Connect (Comp 'LandFx' $EMITTER 1250 1150) 'LandFx' $placeFx 'self'
Connect $feet 'ReturnValue' $placeFx 'NewLocation'
$puff = Emit 'Activate' 'LandFx' 1700 900
$cast3 = GameInstance 2000 900
$vol = SeVolume $cast3 1950 1150
$loud = Volume 'LandSound' $vol 2300 900
$thump = Sound 'Play' 'LandSound' 2600 900
$free = InputCall 'EnableInput' 2900 900
$unfreeze = Controller-Input 'EnableInput' 3200 900
Connect $landed 'then' $stop 'execute'
Chain @($stop, $back, $placeFx, $puff, $cast3)
Connect $cast3 'then' $loud 'execute'
Chain @($loud, $thump, $free, $unfreeze)
Write-Graph 'BP_SkyLanding_EventGraph.txt'
