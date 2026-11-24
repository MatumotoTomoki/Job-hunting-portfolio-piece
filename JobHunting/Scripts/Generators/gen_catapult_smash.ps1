param([string]$OutDir)
# Paste text for setup_catapult_smash.py's blueprints (hidden area 2, 2026-11-22):
#   BP_CatapultSmash_EventGraph.txt
#     Begin Play: StartDelay s later the player's input off, the view on ShowCamera; Started, StartedAt; the target
#       ring shows, a rumble. 2.9 s on (the pillar has landed, see Tick): the catapult destroyed (sounds and all), the
#       wreck shown, the ring hidden, ImpactFx, a boom; Smashed. 2.5 s later the view back to the player, 1 s later input.
#     Tick, once Started: t = now - StartedAt; the ring's Charge = t / 2.5 (clamped); the pillar shows from t >= 2.5
#       and drops from 11000 to 3000 (its middle; 6000 tall, so it ends on the floor) between t 2.5 and 2.9.
#     Then, once Smashed, if Lever (the hidden one) is pulled: the pillar out and Busy for good (the trap off).
#     Touch (Trap), once Smashed, not Busy, the player: Busy; input off, the screen to white; the player put at
#       Respawn, stopped; the white clears; input back; not Busy.
#   BP_ActorRiser_EventGraph.txt
#     Begin Play: StartLocation = Target's location. Tick: not Started - if Lever is valid and Pulled: Started,
#       StartedAt, a rumble at StartLocation. Started - Target at StartLocation + RiseOffset * ease(t / RiseSeconds).
if (-not $OutDir) { throw 'OutDir is required' }
$lightGen = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_heaven_light.ps1') -Encoding UTF8
$cut = ($lightGen | Select-String -Pattern '^# ===== BP_LightBeam' | Select-Object -First 1).LineNumber - 1
. ([ScriptBlock]::Create(($lightGen[1..($cut - 1)] -join "`n")))

$SOUND_BASE = "/Script/CoreUObject.Class'/Script/Engine.SoundBase'"
$MESH_COMP = "/Script/CoreUObject.Class'/Script/Engine.MeshComponent'"
$EMITTER = "/Script/CoreUObject.Class'/Script/Effekseer.EffekseerEmitterComponent'"
$ACTOR_COMP = "/Script/CoreUObject.Class'/Script/Engine.ActorComponent'"
$MOVE_COMP = "/Script/CoreUObject.Class'/Script/Engine.MovementComponent'"
$AREA_SOUNDS = '/Game/ThirdPerson/Blueprints/Gimmicks/Area'
$WHITE = '(R=1.000000,G=1.000000,B=1.000000,A=1.000000)'

function Times($a, $aPin, $b, $bPin, [double]$x, [double]$y) { Op 'Multiply' 'Multiply_DoubleDouble' $a $aPin $b $bPin $x $y }
function SelfNode([double]$x, [double]$y) {
  $n = New-Node '/Script/BlueprintGraph.K2Node_Self' @() $x $y
  Add-Pin $n 'self' 'out' 'object' '' $ACTOR
  return $n
}
function Volume($cast, [double]$x, [double]$y) {
  Op 'Multiply' 'Multiply_DoubleDouble' (GiGet $cast 'SE Volume' 'real' 'double' $x $y) 'SE Volume' (GiGet $cast 'Master Volume' 'real' 'double' $x ($y + 100)) 'Master Volume' ($x + 250) ($y + 50)
}
function Play2D($asset, $volume, [double]$x, [double]$y) {
  $n = New-Call $STATICS 'PlaySound2D' $false $x $y
  Add-Pin $n 'Sound' 'in' 'object' '' $SOUND_BASE
  (Get-Pin $n 'Sound') | Add-Member DefaultObject "$AREA_SOUNDS/$asset.$asset"
  Add-Pin $n 'VolumeMultiplier' 'in' 'real' 'float'
  Add-Pin $n 'PitchMultiplier' 'in' 'real' 'float' $null '1.0'
  Add-Pin $n 'StartTime' 'in' 'real' 'float' $null '0.0'
  Connect $volume 'ReturnValue' $n 'VolumeMultiplier'
  return $n
}
# S_MechRumble loops (3 s): spawned as a component so it can be faded out (played with PlaySound2D it never stopped,
# the user 2026-11-22).
function Spawn2D($asset, $volume, [double]$x, [double]$y) {
  $n = New-Call $STATICS 'SpawnSound2D' $false $x $y
  Add-Pin $n 'Sound' 'in' 'object' '' $SOUND_BASE
  (Get-Pin $n 'Sound') | Add-Member DefaultObject "$AREA_SOUNDS/$asset.$asset"
  Add-Pin $n 'VolumeMultiplier' 'in' 'real' 'float'
  Add-Pin $n 'PitchMultiplier' 'in' 'real' 'float' $null '1.0'
  Add-Pin $n 'StartTime' 'in' 'real' 'float' $null '0.0'
  Add-Pin $n 'bPersistAcrossLevelTransition' 'in' 'bool' '' $null 'false'
  Add-Pin $n 'bAutoDestroy' 'in' 'bool' '' $null 'true'
  Add-Pin $n 'ReturnValue' 'out' 'object' '' "/Script/CoreUObject.Class'/Script/Engine.AudioComponent'"
  Connect $volume 'ReturnValue' $n 'VolumeMultiplier'
  return $n
}
function FadeOutSound($spawned, $seconds, [double]$x, [double]$y) {
  $n = New-Call "/Script/CoreUObject.Class'/Script/Engine.AudioComponent'" 'FadeOut' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' "/Script/CoreUObject.Class'/Script/Engine.AudioComponent'"
  Add-Pin $n 'FadeOutDuration' 'in' 'real' 'float' $null $seconds
  Add-Pin $n 'FadeVolumeLevel' 'in' 'real' 'float' $null '0.0'
  Connect $spawned 'ReturnValue' $n 'self'
  return $n
}
function ActorCall($func, $pin, $value, $targetNode, $targetPin, [double]$x, [double]$y) {
  $n = New-Call $ACTOR $func $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR
  Add-Pin $n $pin 'in' 'bool' '' $null $value
  Connect $targetNode $targetPin $n 'self'
  return $n
}
function Ranged($value, $valuePin, $inA, $inB, [double]$x, [double]$y) {
  $n = New-Call $MATH 'MapRangeClamped' $true $x $y
  Add-Pin $n 'Value' 'in' 'real' 'double'
  Add-Pin $n 'InRangeA' 'in' 'real' 'double' $null $inA
  Add-Pin $n 'InRangeB' 'in' 'real' 'double'
  Add-Pin $n 'OutRangeA' 'in' 'real' 'double' $null '0.0'
  Add-Pin $n 'OutRangeB' 'in' 'real' 'double' $null '1.0'
  Add-Pin $n 'ReturnValue' 'out' 'real' 'double'
  Connect $value $valuePin $n 'Value'
  if ($inB -is [string]) { (Get-Pin $n 'InRangeB').Default = $inB } else { Connect $inB[0] $inB[1] $n 'InRangeB' }
  return $n
}
function Fade($from, $to, $seconds, $hold, [double]$x, [double]$y) {
  $camera = New-Call $STATICS 'GetPlayerCameraManager' $true $x ($y + 250)
  Add-Pin $camera 'PlayerIndex' 'in' 'int' '' $null '0'
  Add-Pin $camera 'ReturnValue' 'out' 'object' '' $CAMERA_MANAGER
  $n = New-Call $CAMERA_MANAGER 'StartCameraFade' $false ($x + 250) $y
  Add-Pin $n 'self' 'in' 'object' '' $CAMERA_MANAGER
  Add-Pin $n 'FromAlpha' 'in' 'real' 'float' $null $from
  Add-Pin $n 'ToAlpha' 'in' 'real' 'float' $null $to
  Add-Pin $n 'Duration' 'in' 'real' 'float' $null $seconds
  Add-Pin $n 'Color' 'in' 'struct' '' $LINEAR $WHITE
  Add-Pin $n 'bShouldFadeAudio' 'in' 'bool' '' $null 'false'
  Add-Pin $n 'bHoldWhenFinished' 'in' 'bool' '' $null $hold
  Connect $camera 'ReturnValue' $n 'self'
  return $n
}

# ===== BP_CatapultSmash =====
Reset-Graph 100
$begin = Event 'ReceiveBeginPlay' 0 0
$wait = Delay '4.0' 250 0
Connect (Real 'StartDelay' 100 200) 'StartDelay' $wait 'Duration'
$noInput = InputCall 'DisableInput' 500 0
$toShow = ViewTarget 800 0
Connect (SelfNode 600 300) 'self' $toShow 'NewViewTarget'
$started = SetSelf 'Started' 'bool' 'true' 1100 0
$startedAt = SetReal 'StartedAt' 1350 0
Connect (Now 1200 200) 'ReturnValue' $startedAt 'StartedAt'
$ring = Visible 'Marker' 'true' 1600 0
$gi = GameInstance 1900 0
$rumble = Spawn2D 'S_MechRumble' (Volume $gi 1900 300) 2200 0
$rumbleOff = FadeOutSound $rumble '0.3' 3150 -250
$waitHit = Delay '2.9' 2500 0
# The catapult destroyed, not just hidden: hidden, its own sounds (the steam) went on (the user, 2026-11-22).
$gone = New-Call $ACTOR 'K2_DestroyActor' $false 2900 0
Add-Pin $gone 'self' 'in' 'object' '' $ACTOR
Connect (New-VarGet 'Catapult' $null 'object' '' $ACTOR 2700 300) 'Catapult' $gone 'self'
$wrecks = @()
for ($i = 1; $i -le 4; $i++) { $wrecks += Visible "Wreck$i" 'true' (3100 + 300 * $i) 0 }
$ringOff = Visible 'Marker' 'false' 4600 0
$blast = New-Call $ACTOR_COMP 'Activate' $false 4900 0
Add-Pin $blast 'self' 'in' 'object' '' $ACTOR_COMP
Add-Pin $blast 'bReset' 'in' 'bool' '' $null 'true'
Connect (New-VarGet 'ImpactFx' $null 'object' '' $EMITTER 4750 250) 'ImpactFx' $blast 'self'
$boom = Play2D 'S_CatapultBoom' (Volume $gi 5000 300) 5200 0
$smashed = SetSelf 'Smashed' 'bool' 'true' 5500 0
$waitLook = Delay '2.5' 5800 0
$back = ViewTarget 6100 0
Connect (Player 5900 300) 'ReturnValue' $back 'NewViewTarget'
$waitInput = Delay '1.0' 6400 0
$input = InputCall 'EnableInput' 6700 0
# First let the gear arrival (Arrival, if any) finish: while it is Arriving and not yet Landed, look again 0.3 s
# later; once landed, a second's pause (2026-11-22: the two shows clashed).
$ARRIVAL_CLASS = "/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPerson/Blueprints/Gimmicks/Area/BP_GearArrival.BP_GearArrival_C'"
$hasArrival = New-Branch 450 -400
Connect (Valid (New-VarGet 'Arrival' $null 'object' '' $ARRIVAL_CLASS 250 -200) 'Arrival' 350 -200) 'ReturnValue' $hasArrival 'Condition'
$rising = New-Branch 750 -400
$arriving = New-VarGet 'Arriving' $ARRIVAL_CLASS 'bool' '' $null 550 -200
Connect (New-VarGet 'Arrival' $null 'object' '' $ARRIVAL_CLASS 400 -100) 'Arrival' $arriving 'self'
$landed = New-VarGet 'Landed' $ARRIVAL_CLASS 'bool' '' $null 550 -50
Connect (New-VarGet 'Arrival' $null 'object' '' $ARRIVAL_CLASS 400 50) 'Arrival' $landed 'self'
$notLanded = MathCall 'Not_PreBool' @('A') 'bool' '' 'bool' '' 700 -50
Connect $landed 'Landed' $notLanded 'A'
Connect (Both $arriving 'Arriving' $notLanded 'ReturnValue' 'BooleanAND' 850 -150) 'ReturnValue' $rising 'Condition'
$again = Delay '0.3' 1000 -550
$settle = Delay '1.0' 1000 -300
Connect $begin 'then' $wait 'execute'
Connect $wait 'then' $hasArrival 'execute'
Connect $hasArrival 'then' $rising 'execute'
Connect $hasArrival 'else' $noInput 'execute'
Connect $rising 'then' $again 'execute'
Connect $again 'then' $hasArrival 'execute'
Connect $rising 'else' $settle 'execute'
Connect $settle 'then' $noInput 'execute'
Chain @($noInput, $toShow, $started, $startedAt, $ring, $gi)
Connect $gi 'then' $rumble 'execute'
# The pillar put where it ends, shown, right at the blast too (not only by Tick).
$pillarDown = New-Call $SCENE 'K2_SetRelativeLocation' $false 3150 -500
Add-Pin $pillarDown 'self' 'in' 'object' '' $SCENE
Add-Pin $pillarDown 'NewLocation' 'in' 'struct' '' $VECTOR '0, 0, 3000'
Add-Pin $pillarDown 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $pillarDown 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $pillarDown 'bTeleport' 'in' 'bool' '' $null 'true'
Connect (Comp 'Pillar' $STATIC_MESH 3000 -350) 'Pillar' $pillarDown 'self'
$pillarOn = Visible 'Pillar' 'true' 3450 -500
Chain (@($rumble, $waitHit, $gone, $pillarDown, $pillarOn, $rumbleOff) + $wrecks + @($ringOff, $blast, $boom, $smashed, $waitLook, $back, $waitInput, $input))

# Tick: the ring charging, the pillar dropping.
$tick = Event 'ReceiveTick' 0 1000
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$going = New-Branch 250 1000
Connect (Bool 'Started' 100 1200) 'Started' $going 'Condition'
Connect $tick 'then' $going 'execute'
$t = Op 'Subtract' 'Subtract_DoubleDouble' (Now 200 1400) 'ReturnValue' (Real 'StartedAt' 200 1500) 'StartedAt' 400 1400
$charge = New-Call $MESH_COMP 'SetScalarParameterValueOnMaterials' $false 700 1000
Add-Pin $charge 'self' 'in' 'object' '' $MESH_COMP
Add-Pin $charge 'ParameterName' 'in' 'name' '' $null 'Charge'
(Get-Pin $charge 'ParameterName') | Add-Member -NotePropertyName ConstRef -NotePropertyValue $true
Add-Pin $charge 'ParameterValue' 'in' 'real' 'float'
Connect (Comp 'Marker' $STATIC_MESH 550 1200) 'Marker' $charge 'self'
Connect (Ranged $t 'ReturnValue' '0.0' '2.5' 600 1400) 'ReturnValue' $charge 'ParameterValue'
$falling = Op 'GreaterEqual' 'GreaterEqual_DoubleDouble' $t 'ReturnValue' $null '2.5' 900 1500 'bool'
$pillarShow = Visible 'Pillar' @($falling, 'ReturnValue') 1050 1000
$drop = Ranged $t 'ReturnValue' '2.5' '2.9' 1100 1500
$z = New-Call $MATH 'Lerp' $true 1350 1500
Add-Pin $z 'A' 'in' 'real' 'double' $null '11000.0'
Add-Pin $z 'B' 'in' 'real' 'double' $null '3000.0'
Add-Pin $z 'Alpha' 'in' 'real' 'double'
Add-Pin $z 'ReturnValue' 'out' 'real' 'double'
Connect $drop 'ReturnValue' $z 'Alpha'
$at = New-Call $MATH 'MakeVector' $true 1550 1500
Add-Pin $at 'X' 'in' 'real' 'double' $null '0.0'
Add-Pin $at 'Y' 'in' 'real' 'double' $null '0.0'
Add-Pin $at 'Z' 'in' 'real' 'double'
Add-Pin $at 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $z 'ReturnValue' $at 'Z'
$place = New-Call $SCENE 'K2_SetRelativeLocation' $false 1400 1000
Add-Pin $place 'self' 'in' 'object' '' $SCENE
Add-Pin $place 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $place 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $place 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $place 'bTeleport' 'in' 'bool' '' $null 'false'
Connect (Comp 'Pillar' $STATIC_MESH 1250 1200) 'Pillar' $place 'self'
Connect $at 'ReturnValue' $place 'NewLocation'
Connect $going 'then' $charge 'execute'
Chain @($charge, $pillarShow, $place)
# Disarmed by the hidden lever (Lever pulled, once smashed): the pillar out, the trap off for good (Busy).
$LEVER_BP = "/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPerson/Blueprints/Gimmicks/Area/BP_Lever.BP_Lever_C'"
$smashedYet = New-Branch 1700 1000
Connect (Bool 'Smashed' 1550 1200) 'Smashed' $smashedYet 'Condition'
Connect $place 'then' $smashedYet 'execute'
$hasLever = New-Branch 1950 1000
Connect (Valid (New-VarGet 'Lever' $null 'object' '' $LEVER_BP 1750 1300) 'Lever' 1850 1300) 'ReturnValue' $hasLever 'Condition'
Connect $smashedYet 'then' $hasLever 'execute'
$isPulled = New-Branch 2200 1000
$pulledGet = New-VarGet 'Pulled' $LEVER_BP 'bool' '' $null 2050 1300
Connect (New-VarGet 'Lever' $null 'object' '' $LEVER_BP 1900 1400) 'Lever' $pulledGet 'self'
Connect $pulledGet 'Pulled' $isPulled 'Condition'
Connect $hasLever 'then' $isPulled 'execute'
$pillarOut = Visible 'Pillar' 'false' 2450 1000
$trapOff = SetSelf 'Busy' 'bool' 'true' 2750 1000
Connect $isPulled 'then' $pillarOut 'execute'
Connect $pillarOut 'then' $trapOff 'execute'

# Touch: the false goal.
$touch = Event 'ReceiveActorBeginOverlap' 0 2000
Add-Pin $touch 'OtherActor' 'out' 'object' '' $ACTOR
$same = New-Call $MATH 'EqualEqual_ObjectObject' $true 150 2250
Add-Pin $same 'A' 'in' 'object' '' $OBJECT
Add-Pin $same 'B' 'in' 'object' '' $OBJECT
Add-Pin $same 'ReturnValue' 'out' 'bool'
Connect $touch 'OtherActor' $same 'A'
Connect (Player 0 2350) 'ReturnValue' $same 'B'
$notBusy = MathCall 'Not_PreBool' @('A') 'bool' '' 'bool' '' 150 2450
Connect (Bool 'Busy' 0 2500) 'Busy' $notBusy 'A'
$ready = Both (Bool 'Smashed' 250 2150) 'Smashed' $notBusy 'ReturnValue' 'BooleanAND' 350 2200
$go = New-Branch 550 2000
Connect (Both $ready 'ReturnValue' $same 'ReturnValue' 'BooleanAND' 450 2300) 'ReturnValue' $go 'Condition'
Connect $touch 'then' $go 'execute'
$busy = SetSelf 'Busy' 'bool' 'true' 800 2000
$lock = InputCall 'DisableInput' 1050 2000
$whiteOut = Fade '0.0' '1.0' '0.5' 'true' 1300 2000
$waitWhite = Delay '0.6' 1850 2000
$move = New-Call $ACTOR 'K2_SetActorLocation' $false 2100 2000
Add-Pin $move 'self' 'in' 'object' '' $ACTOR
Add-Pin $move 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $move 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $move 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $move 'bTeleport' 'in' 'bool' '' $null 'true'
Add-Pin $move 'ReturnValue' 'out' 'bool'
Connect (Player 1900 2250) 'ReturnValue' $move 'self'
$spotAt = New-Call $ACTOR 'K2_GetActorLocation' $true 1900 2400
Add-Pin $spotAt 'self' 'in' 'object' '' $ACTOR
Add-Pin $spotAt 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect (New-VarGet 'Respawn' $null 'object' '' $ACTOR 1700 2400) 'Respawn' $spotAt 'self'
Connect $spotAt 'ReturnValue' $move 'NewLocation'
$stop = New-Call $MOVE_COMP 'StopMovementImmediately' $false 2400 2000
Add-Pin $stop 'self' 'in' 'object' '' $MOVE_COMP
Connect (Movement 2300 2250) 'CharacterMovement' $stop 'self'
$clear = Fade '1.0' '0.0' '0.8' 'false' 2650 2000
$unlock = InputCall 'EnableInput' 3200 2000
$free = SetSelf 'Busy' 'bool' 'false' 3500 2000
Connect $go 'then' $busy 'execute'
Chain @($busy, $lock, $whiteOut, $waitWhite, $move, $stop, $clear, $unlock, $free)
Write-Graph 'BP_CatapultSmash_EventGraph.txt'

# ===== BP_ActorRiser =====
Reset-Graph 100
$begin = Event 'ReceiveBeginPlay' 0 0
$remember = New-VarSet 'StartLocation' $null 'struct' $VECTOR 300 0
$where = New-Call $ACTOR 'K2_GetActorLocation' $true 100 200
Add-Pin $where 'self' 'in' 'object' '' $ACTOR
Add-Pin $where 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect (New-VarGet 'Target' $null 'object' '' $ACTOR -100 200) 'Target' $where 'self'
Connect $where 'ReturnValue' $remember 'StartLocation'
Connect $begin 'then' $remember 'execute'

$tick = Event 'ReceiveTick' 0 600
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$going = New-Branch 250 600
Connect (Bool 'Started' 100 800) 'Started' $going 'Condition'
Connect $tick 'then' $going 'execute'
# Not yet: is the lever there, and pulled? (two branches: a pure AND would read Pulled off a missing lever)
$hasLever = New-Branch 500 900
Connect (Valid (New-VarGet 'Lever' $null 'object' '' $LEVER_CLASS 250 1100) 'Lever' 400 1100) 'ReturnValue' $hasLever 'Condition'
Connect $going 'else' $hasLever 'execute'
$pulled = New-Branch 750 900
$isPulled = New-VarGet 'Pulled' $LEVER_CLASS 'bool' '' $null 600 1100
Connect (New-VarGet 'Lever' $null 'object' '' $LEVER_CLASS 450 1200) 'Lever' $isPulled 'self'
Connect $isPulled 'Pulled' $pulled 'Condition'
Connect $hasLever 'then' $pulled 'execute'
$start = SetSelf 'Started' 'bool' 'true' 1000 900
$stamp = SetReal 'StartedAt' 1250 900
Connect (Now 1100 1100) 'ReturnValue' $stamp 'StartedAt'
$gi = GameInstance 1550 900
$rumble = New-Call $STATICS 'SpawnSoundAtLocation' $false 1850 900
Add-Pin $rumble 'Sound' 'in' 'object' '' $SOUND_BASE
(Get-Pin $rumble 'Sound') | Add-Member DefaultObject "$AREA_SOUNDS/S_MechRumble.S_MechRumble"
Add-Pin $rumble 'Location' 'in' 'struct' '' $VECTOR
Add-Pin $rumble 'Rotation' 'in' 'struct' '' $ROTATOR '0, 0, 0'
Add-Pin $rumble 'VolumeMultiplier' 'in' 'real' 'float'
Add-Pin $rumble 'PitchMultiplier' 'in' 'real' 'float' $null '0.8'
Add-Pin $rumble 'StartTime' 'in' 'real' 'float' $null '0.0'
Add-Pin $rumble 'ReturnValue' 'out' 'object' '' "/Script/CoreUObject.Class'/Script/Engine.AudioComponent'"
Connect (Vec 'StartLocation' 1650 1200) 'StartLocation' $rumble 'Location'
Connect (Volume $gi 1550 1250) 'ReturnValue' $rumble 'VolumeMultiplier'
Connect $pulled 'then' $start 'execute'
Chain @($start, $stamp, $gi)
Connect $gi 'then' $rumble 'execute'
# The rumble (a loop) fades out as the rise ends.
$riseWait = Delay '4.0' 2150 900
Connect (Real 'RiseSeconds' 2000 1100) 'RiseSeconds' $riseWait 'Duration'
$riseQuiet = FadeOutSound $rumble '0.5' 2400 900
Connect $rumble 'then' $riseWait 'execute'
Connect $riseWait 'then' $riseQuiet 'execute'
# Started: rise.
$t = Op 'Subtract' 'Subtract_DoubleDouble' (Now 400 300) 'ReturnValue' (Real 'StartedAt' 400 400) 'StartedAt' 600 300
$a = Ranged $t 'ReturnValue' '0.0' @((Real 'RiseSeconds' 600 450), 'RiseSeconds') 800 300
$cos = MathCall 'Cos' @('A') 'real' 'double' 'real' 'double' 1200 300
Connect (Op 'Multiply' 'Multiply_DoubleDouble' $a 'ReturnValue' $null '3.14159265' 1000 300) 'ReturnValue' $cos 'A'
$ease = Op 'Subtract' 'Subtract_DoubleDouble' $null '0.5' (Op 'Multiply' 'Multiply_DoubleDouble' $cos 'ReturnValue' $null '0.5' 1350 300) 'ReturnValue' 1500 300
$offset = New-Call $MATH 'Multiply_VectorFloat' $true 1700 250
Add-Pin $offset 'A' 'in' 'struct' '' $VECTOR
Add-Pin $offset 'B' 'in' 'real' 'double'
Add-Pin $offset 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect (Vec 'RiseOffset' 1500 200) 'RiseOffset' $offset 'A'
Connect $ease 'ReturnValue' $offset 'B'
$sum = New-Operator 'Add' 'Add_VectorVector' 'struct' '' 'struct' 1900 200
foreach ($pin in 'A', 'B', 'ReturnValue') { (Get-Pin $sum $pin).Obj = $VECTOR }
Connect (Vec 'StartLocation' 1700 100) 'StartLocation' $sum 'A'
Connect $offset 'ReturnValue' $sum 'B'
$lift = New-Call $ACTOR 'K2_SetActorLocation' $false 2100 0
Add-Pin $lift 'self' 'in' 'object' '' $ACTOR
Add-Pin $lift 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $lift 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $lift 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $lift 'bTeleport' 'in' 'bool' '' $null 'false'
Add-Pin $lift 'ReturnValue' 'out' 'bool'
Connect (New-VarGet 'Target' $null 'object' '' $ACTOR 1900 -100) 'Target' $lift 'self'
Connect $sum 'ReturnValue' $lift 'NewLocation'
Connect $going 'then' $lift 'execute'
Write-Graph 'BP_ActorRiser_EventGraph.txt'
