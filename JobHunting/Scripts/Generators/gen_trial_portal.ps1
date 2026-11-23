param([string]$OutDir)
# Paste text for BP_TrialPortal (setup_trial_portal.py; hidden area 4's trials, 2026-11-23):
#   Begin Play: with a Wind (the updraft on from this island), that updraft asleep (tick off, hidden) - it wakes
#     with a swell of light when the player is put back here, the trial done. With a Prev, the footing (this actor) and its Flag hidden and not solid; without one, Shown.
#   Tick, not Shown: once Prev is Done - Shown, this footing and its Flag shown and solid, a swell of light.
#   Tick, Started and not Done: once the Shard is gone (taken) - Done; 0.8 s on: input off, the screen to white, the
#     player put on this footing (its flag), stopped; the pillar shows; the white clears, input back; 1.5 s on the
#     pillar goes.
#   Touch, Shown, not Started, the player: Started; input off; the pillar shows, a swell of light; 1.2 s on the screen
#     to white; the player put at Destination, stopped; the pillar goes; the white clears, input back.
if (-not $OutDir) { throw 'OutDir is required' }
$lightGen = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_heaven_light.ps1') -Encoding UTF8
$cut = ($lightGen | Select-String -Pattern '^# ===== BP_LightBeam' | Select-Object -First 1).LineNumber - 1
. ([ScriptBlock]::Create(($lightGen[1..($cut - 1)] -join "`n")))

$SOUND_BASE = "/Script/CoreUObject.Class'/Script/Engine.SoundBase'"
$MOVE_COMP = "/Script/CoreUObject.Class'/Script/Engine.MovementComponent'"
$PORTAL_CLASS = "/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPerson/Blueprints/Gimmicks/Area/BP_TrialPortal.BP_TrialPortal_C'"
$WHITE_COLOR = '(R=1.000000,G=1.000000,B=1.000000,A=1.000000)'

function SelfNode([double]$x, [double]$y) {
  $n = New-Node '/Script/BlueprintGraph.K2Node_Self' @() $x $y
  Add-Pin $n 'self' 'out' 'object' '' $ACTOR
  return $n
}
function OnActor($func, $pin, $value, $targetNode, $targetPin, [double]$x, [double]$y) {
  $n = New-Call $ACTOR $func $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR
  Add-Pin $n $pin 'in' 'bool' '' $null $value
  Connect $targetNode $targetPin $n 'self'
  return $n
}
function OnSelf($func, $pin, $value, [double]$x, [double]$y) { OnActor $func $pin $value (SelfNode ($x - 150) ($y + 200)) 'self' $x $y }
function OnFlag($func, $pin, $value, [double]$x, [double]$y) { OnActor $func $pin $value (New-VarGet 'Flag' $null 'object' '' $ACTOR ($x - 200) ($y + 200)) 'Flag' $x $y }
function Swell([double]$x, [double]$y) {
  $gi = GameInstance $x $y
  $n = New-Call $STATICS 'PlaySound2D' $false ($x + 300) $y
  Add-Pin $n 'Sound' 'in' 'object' '' $SOUND_BASE
  (Get-Pin $n 'Sound') | Add-Member DefaultObject '/Game/ThirdPerson/Blueprints/Gimmicks/Heaven/S_GateLight.S_GateLight'
  Add-Pin $n 'VolumeMultiplier' 'in' 'real' 'float'
  Add-Pin $n 'PitchMultiplier' 'in' 'real' 'float' $null '1.0'
  Add-Pin $n 'StartTime' 'in' 'real' 'float' $null '0.0'
  Connect (Op 'Multiply' 'Multiply_DoubleDouble' (GiGet $gi 'SE Volume' 'real' 'double' ($x + 50) ($y + 250)) 'SE Volume' (GiGet $gi 'Master Volume' 'real' 'double' ($x + 50) ($y + 350)) 'Master Volume' ($x + 250) ($y + 300)) 'ReturnValue' $n 'VolumeMultiplier'
  Connect $gi 'then' $n 'execute'
  return @($gi, $n)
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
  Add-Pin $n 'Color' 'in' 'struct' '' $LINEAR $WHITE_COLOR
  Add-Pin $n 'bShouldFadeAudio' 'in' 'bool' '' $null 'false'
  Add-Pin $n 'bHoldWhenFinished' 'in' 'bool' '' $null $hold
  Connect $camera 'ReturnValue' $n 'self'
  return $n
}
# The player put at `where` (a vector node and its pin) and stopped: returns (move, stop).
function PutPlayer($where, $wherePin, [double]$x, [double]$y) {
  $move = New-Call $ACTOR 'K2_SetActorLocation' $false $x $y
  Add-Pin $move 'self' 'in' 'object' '' $ACTOR
  Add-Pin $move 'NewLocation' 'in' 'struct' '' $VECTOR
  Add-Pin $move 'bSweep' 'in' 'bool' '' $null 'false'
  Add-Pin $move 'SweepHitResult' 'out' 'struct' '' $HIT
  Add-Pin $move 'bTeleport' 'in' 'bool' '' $null 'true'
  Add-Pin $move 'ReturnValue' 'out' 'bool'
  Connect (Player ($x - 200) ($y + 250)) 'ReturnValue' $move 'self'
  Connect $where $wherePin $move 'NewLocation'
  $stop = New-Call $MOVE_COMP 'StopMovementImmediately' $false ($x + 300) $y
  Add-Pin $stop 'self' 'in' 'object' '' $MOVE_COMP
  Connect (Movement ($x + 200) ($y + 250)) 'CharacterMovement' $stop 'self'
  Connect $move 'then' $stop 'execute'
  return @($move, $stop)
}
function LocationOf($node, $pin, [double]$x, [double]$y) {
  $n = New-Call $ACTOR 'K2_GetActorLocation' $true $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR
  Add-Pin $n 'ReturnValue' 'out' 'struct' '' $VECTOR
  Connect $node $pin $n 'self'
  return $n
}

function OnWind($func, $pin, $value, [double]$x, [double]$y) { OnActor $func $pin $value (New-VarGet 'Wind' $null 'object' '' $ACTOR ($x - 200) ($y + 200)) 'Wind' $x $y }
function WindThere([double]$x, [double]$y) {
  $n = New-Branch $x $y
  Connect (Valid (New-VarGet 'Wind' $null 'object' '' $ACTOR ($x - 250) ($y + 250)) 'Wind' ($x - 100) ($y + 250)) 'ReturnValue' $n 'Condition'
  return $n
}

Reset-Graph 100
# ----- Begin Play -----
$begin = Event 'ReceiveBeginPlay' 0 (-700)
# the updraft on from this island sleeps (no push, not shown) until this trial is done
$windAt = WindThere 300 (-700)
$windStill = OnWind 'SetActorTickEnabled' 'bEnabled' 'false' 600 (-700)
$windHide = OnWind 'SetActorHiddenInGame' 'bNewHidden' 'true' 900 (-700)
Connect $begin 'then' $windAt 'execute'
Connect $windAt 'then' $windStill 'execute'
Chain @($windStill, $windHide)
$hasPrev = New-Branch 300 0
Connect (Valid (New-VarGet 'Prev' $null 'object' '' $PORTAL_CLASS 50 250) 'Prev' 200 250) 'ReturnValue' $hasPrev 'Condition'
Connect $windAt 'else' $hasPrev 'execute'
Connect $windHide 'then' $hasPrev 'execute'
$hideSelf = OnSelf 'SetActorHiddenInGame' 'bNewHidden' 'true' 600 0
$solidSelf = OnSelf 'SetActorEnableCollision' 'bNewActorEnableCollision' 'false' 900 0
$hideFlag = OnFlag 'SetActorHiddenInGame' 'bNewHidden' 'true' 1200 0
$solidFlag = OnFlag 'SetActorEnableCollision' 'bNewActorEnableCollision' 'false' 1500 0
Connect $hasPrev 'then' $hideSelf 'execute'
Chain @($hideSelf, $solidSelf, $hideFlag, $solidFlag)
$shownNow = SetSelf 'Shown' 'bool' 'true' 600 400
Connect $hasPrev 'else' $shownNow 'execute'

# ----- Tick -----
$tick = Event 'ReceiveTick' 0 900
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$isShown = New-Branch 250 900
Connect (Bool 'Shown' 100 1100) 'Shown' $isShown 'Condition'
Connect $tick 'then' $isShown 'execute'
# not shown yet: wait for Prev
$prevThere = New-Branch 550 1300
Connect (Valid (New-VarGet 'Prev' $null 'object' '' $PORTAL_CLASS 300 1500) 'Prev' 450 1500) 'ReturnValue' $prevThere 'Condition'
Connect $isShown 'else' $prevThere 'execute'
$prevDone = New-Branch 800 1300
$doneGet = New-VarGet 'Done' $PORTAL_CLASS 'bool' '' $null 650 1550
Connect (New-VarGet 'Prev' $null 'object' '' $PORTAL_CLASS 500 1650) 'Prev' $doneGet 'self'
Connect $doneGet 'Done' $prevDone 'Condition'
Connect $prevThere 'then' $prevDone 'execute'
$appear = SetSelf 'Shown' 'bool' 'true' 1050 1300
$showSelf = OnSelf 'SetActorHiddenInGame' 'bNewHidden' 'false' 1300 1300
$firmSelf = OnSelf 'SetActorEnableCollision' 'bNewActorEnableCollision' 'true' 1600 1300
$showFlag = OnFlag 'SetActorHiddenInGame' 'bNewHidden' 'false' 1900 1300
$firmFlag = OnFlag 'SetActorEnableCollision' 'bNewActorEnableCollision' 'true' 2200 1300
$appearSound = Swell 2500 1300
Connect $prevDone 'then' $appear 'execute'
Chain @($appear, $showSelf, $firmSelf, $showFlag, $firmFlag, $appearSound[0])
# shown: on a trip, wait for the shard
$onTrip = New-Branch 550 900
$notDone = MathCall 'Not_PreBool' @('A') 'bool' '' 'bool' '' 350 1100
Connect (Bool 'Done' 250 1150) 'Done' $notDone 'A'
Connect (Both (Bool 'Started' 300 1000) 'Started' $notDone 'ReturnValue' 'BooleanAND' 450 1050) 'ReturnValue' $onTrip 'Condition'
Connect $isShown 'then' $onTrip 'execute'
$taken = New-Branch 800 900
$gone = MathCall 'Not_PreBool' @('A') 'bool' '' 'bool' '' 700 1100
Connect (Valid (New-VarGet 'Shard' $null 'object' '' $SHARD_CLASS 500 1200) 'Shard' 600 1150) 'ReturnValue' $gone 'A'
Connect $gone 'ReturnValue' $taken 'Condition'
Connect $onTrip 'then' $taken 'execute'
$finished = SetSelf 'Done' 'bool' 'true' 1050 900
$linger = Delay '0.8' 1300 900
$lockBack = InputCall 'DisableInput' 1550 900
$whiteBack = Fade '0.0' '1.0' '0.5' 'true' 1800 900
$waitBack = Delay '0.6' 2300 900
$backTo = New-Operator 'Add' 'Add_VectorVector' 'struct' '' 'struct' 2700 1150
foreach ($pin in 'A', 'B', 'ReturnValue') { (Get-Pin $backTo $pin).Obj = $VECTOR }
Connect (LocationOf (SelfNode 2350 1150) 'self' 2500 1150) 'ReturnValue' $backTo 'A'
(Get-Pin $backTo 'B').Default = '0, 0, 120'
$putBack = PutPlayer $backTo 'ReturnValue' 2600 900
$pillarBack = Visible 'Pillar' 'true' 3200 900
$clearBack = Fade '1.0' '0.0' '0.8' 'false' 3500 900
$freeBack = InputCall 'EnableInput' 4000 900
$waitPillar = Delay '1.5' 4300 900
$pillarGone = Visible 'Pillar' 'false' 4600 900
Connect $taken 'then' $finished 'execute'
Chain @($finished, $linger, $lockBack, $whiteBack, $waitBack, $putBack[0])
Chain @($pillarBack, $clearBack, $freeBack, $waitPillar, $pillarGone)
# back on the island: its updraft wakes, with a swell of light
$windBack = WindThere 2950 1700
$windGo = OnWind 'SetActorTickEnabled' 'bEnabled' 'true' 3200 1700
$windShow = OnWind 'SetActorHiddenInGame' 'bNewHidden' 'false' 3500 1700
$windSound = Swell 3800 1700
Connect $putBack[1] 'then' $windBack 'execute'
Connect $windBack 'then' $windGo 'execute'
Chain @($windGo, $windShow, $windSound[0])
Connect $windBack 'else' $pillarBack 'execute'
Connect $windSound[1] 'then' $pillarBack 'execute'

# ----- Touch -----
$touch = Event 'ReceiveActorBeginOverlap' 0 2200
Add-Pin $touch 'OtherActor' 'out' 'object' '' $ACTOR
$same = New-Call $MATH 'EqualEqual_ObjectObject' $true 150 2450
Add-Pin $same 'A' 'in' 'object' '' $OBJECT
Add-Pin $same 'B' 'in' 'object' '' $OBJECT
Add-Pin $same 'ReturnValue' 'out' 'bool'
Connect $touch 'OtherActor' $same 'A'
Connect (Player 0 2550) 'ReturnValue' $same 'B'
$notStarted = MathCall 'Not_PreBool' @('A') 'bool' '' 'bool' '' 150 2650
Connect (Bool 'Started' 0 2700) 'Started' $notStarted 'A'
$ready = Both (Bool 'Shown' 250 2350) 'Shown' $notStarted 'ReturnValue' 'BooleanAND' 350 2400
$go = New-Branch 550 2200
Connect (Both $ready 'ReturnValue' $same 'ReturnValue' 'BooleanAND' 450 2500) 'ReturnValue' $go 'Condition'
Connect $touch 'then' $go 'execute'
$start = SetSelf 'Started' 'bool' 'true' 800 2200
$lock = InputCall 'DisableInput' 1050 2200
$pillarOn = Visible 'Pillar' 'true' 1300 2200
$goSound = Swell 1550 2200
$waitGo = Delay '1.2' 2150 2200
$whiteGo = Fade '0.0' '1.0' '0.4' 'true' 2400 2200
$waitWhite = Delay '0.5' 2900 2200
$there = LocationOf (New-VarGet 'Destination' $null 'object' '' $ACTOR 2950 2450) 'Destination' 3100 2450
$putThere = PutPlayer $there 'ReturnValue' 3200 2200
$pillarOff = Visible 'Pillar' 'false' 3800 2200
$clearGo = Fade '1.0' '0.0' '0.8' 'false' 4100 2200
$freeGo = InputCall 'EnableInput' 4600 2200
Connect $go 'then' $start 'execute'
Chain @($start, $lock, $pillarOn, $goSound[0])
Chain @($goSound[1], $waitGo, $whiteGo, $waitWhite, $putThere[0])
Chain @($putThere[1], $pillarOff, $clearGo, $freeGo)
Write-Graph 'BP_TrialPortal_EventGraph.txt'
