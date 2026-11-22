param([string]$OutDir)
# Paste text for the hell stage's hazards (components and variables from build_hell_stage.py):
#   BP_HellLava_EventGraph.txt  the player sinking into KillZone is sent back to RespawnLocation.
#   BP_FlameJet_EventGraph.txt  the eruption loop (StartDelay, then Fire flares for WarnSeconds, the Column stands and
#       Burning is on for BurnSeconds, then OffSeconds of nothing), and on Tick: Burning and the player in HitBox ->
#       sent back. Sounds and effects (setup_flame_effects.py, 2026-11-22): Begin Play sets their volume (SE x Master);
#       flaring - WarnSound; the column out - EruptSound, RoarSound (looping), EruptFx; gone - RoarSound fades, SmokeFx;
#       the player caught - HurtSound.
# Sent back: once at a time (Busy), input off, the screen goes black, the player stops and stands at RespawnLocation
# facing +X, the screen clears, input back on.
if (-not $OutDir) { throw 'OutDir is required' }
# The helper and graph-building functions of gen_hell_cage.ps1 (everything before its first graph).
$cageGen = Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_hell_cage.ps1'
$defs = Get-Content -LiteralPath $cageGen -Encoding UTF8 | Select-Object -Skip 10 -First 172
. ([ScriptBlock]::Create(($defs -join "`n")))

$MOVEMENT = "/Script/CoreUObject.Class'/Script/Engine.MovementComponent'"
$CONTROLLER_BASE = "/Script/CoreUObject.Class'/Script/Engine.Controller'"
$SCENE = "/Script/CoreUObject.Class'/Script/Engine.SceneComponent'"
$ACTOR_COMPONENT = "/Script/CoreUObject.Class'/Script/Engine.ActorComponent'"
$STATIC_MESH = "/Script/CoreUObject.Class'/Script/Engine.StaticMeshComponent'"
$EMITTER = "/Script/CoreUObject.Class'/Script/Effekseer.EffekseerEmitterComponent'"
$LAUNCH = '0.000000,0.000000,1200.000000'   # straight up: JumpZ 500 lifts 1.3 m, this about 7 m
$FLY_SECONDS = '0.6'                         # seen flying up before the screen goes black

function Event($name, $x, $y) {
  $n = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$ACTOR`",MemberName=`"$name`")", 'bOverrideFunction=True') $x $y
  Add-Pin $n 'then' 'out' 'exec'
  return $n
}
function SetSelf($name, $value, $x, $y) {
  $n = New-VarSet $name $null 'bool' $null $x $y
  (Get-Pin $n $name).Default = $value
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
# The player overlapping one of this actor's boxes.
# (Not "$box": PowerShell names ignore case, so it would hide $BOX.)
function PlayerIn($boxName, $x, $y) {
  $n = New-Call $PRIMITIVE 'IsOverlappingActor' $true $x $y
  Add-Pin $n 'self' 'in' 'object' '' $PRIMITIVE
  Add-Pin $n 'Other' 'in' 'object' '' $ACTOR
  Add-Pin $n 'ReturnValue' 'out' 'bool'
  Connect (New-VarGet $boxName $null 'object' '' $BOX ($x - 200) $y) $boxName $n 'self'
  Connect (Player ($x - 250) ($y + 100)) 'ReturnValue' $n 'Other'
  return $n
}
# Sends the player back to RespawnLocation; returns the entry branch (wire into 'execute'). With $hurtSound (an
# AudioComponent's name), that is played once as the player is caught (BP_FlameJet, 2026-11-22).
function SendBack($x, $y, $hurtSound = $null) {
  $busy = New-Branch $x $y
  Connect (New-VarGet 'Busy' $null 'bool' '' $null ($x - 150) ($y + 200)) 'Busy' $busy 'Condition'
  $lock = SetSelf 'Busy' 'true' ($x + 250) $y
  $noInput = InputCall 'DisableInput' ($x + 500) $y
  $steps = @($lock)
  if ($hurtSound) { $steps += SoundPlay $hurtSound ($x + 250) ($y + 450) }
  # Too hot: the player shoots straight up (any run or fall cancelled), and is seen flying before the screen goes black.
  $hop = New-Call $CHARACTER 'LaunchCharacter' $false ($x + 750) ($y - 400)
  Add-Pin $hop 'self' 'in' 'object' '' $CHARACTER
  Add-Pin $hop 'LaunchVelocity' 'in' 'struct' '' $VECTOR $LAUNCH
  Add-Pin $hop 'bXYOverride' 'in' 'bool' '' $null 'true'
  Add-Pin $hop 'bZOverride' 'in' 'bool' '' $null 'true'
  Connect (Player ($x + 550) ($y - 200)) 'ReturnValue' $hop 'self'
  $fly = Delay $FLY_SECONDS ($x + 1050) ($y - 400)
  $dark = Fade '0.0' '1.0' '0.3' 'true' ($x + 750) $y
  $wait = Delay '0.35' ($x + 1250) $y
  $stop = New-Call $MOVEMENT 'StopMovementImmediately' $false ($x + 1500) $y
  Add-Pin $stop 'self' 'in' 'object' '' $MOVEMENT
  Connect (Movement ($x + 1300) ($y + 250)) 'CharacterMovement' $stop 'self'
  $place = New-Call $ACTOR 'K2_SetActorLocationAndRotation' $false ($x + 1800) $y
  Add-Pin $place 'self' 'in' 'object' '' $ACTOR
  Add-Pin $place 'NewLocation' 'in' 'struct' '' $VECTOR
  Add-Pin $place 'NewRotation' 'in' 'struct' '' $ROTATOR '0, 0, 0'
  Add-Pin $place 'bSweep' 'in' 'bool' '' $null 'false'
  Add-Pin $place 'SweepHitResult' 'out' 'struct' '' $HIT
  Add-Pin $place 'bTeleport' 'in' 'bool' '' $null 'true'
  Add-Pin $place 'ReturnValue' 'out' 'bool'
  Connect (Player ($x + 1550) ($y + 350)) 'ReturnValue' $place 'self'
  Connect (New-VarGet 'RespawnLocation' $null 'struct' '' $VECTOR ($x + 1550) ($y + 450)) 'RespawnLocation' $place 'NewLocation'
  $face = New-Call $CONTROLLER_BASE 'SetControlRotation' $false ($x + 2150) $y
  Add-Pin $face 'self' 'in' 'object' '' $CONTROLLER_BASE
  Add-Pin $face 'NewRotation' 'in' 'struct' '' $ROTATOR
  (Get-Pin $face 'NewRotation') | Add-Member -NotePropertyName ConstRef -NotePropertyValue $true
  Connect (Controller ($x + 1950) ($y + 250)) 'ReturnValue' $face 'self'
  # A by-ref input must be wired: a Make Rotator of (0, 0, 0), facing +X.
  $forward = New-Call $MATH 'MakeRotator' $true ($x + 1950) ($y + 400)
  Add-Pin $forward 'Roll' 'in' 'real' 'float' $null '0.0'
  Add-Pin $forward 'Pitch' 'in' 'real' 'float' $null '0.0'
  Add-Pin $forward 'Yaw' 'in' 'real' 'float' $null '0.0'
  Add-Pin $forward 'ReturnValue' 'out' 'struct' '' $ROTATOR
  Connect $forward 'ReturnValue' $face 'NewRotation'
  $clear = Fade '1.0' '0.0' '0.4' 'false' ($x + 2400) $y
  $input = InputCall 'EnableInput' ($x + 2900) $y
  $unlock = SetSelf 'Busy' 'false' ($x + 3150) $y
  Connect $busy 'else' $lock 'execute'
  Chain ($steps + @($noInput, $hop, $fly, $dark, $wait, $stop, $place, $face, $clear, $input, $unlock))
  return $busy
}
# Sounds and effects (setup_flame_effects.py, 2026-11-22). Positive coordinates only here: these helpers take them
# untyped, and a negative y arrives as text (-250 + 200 becomes -250200).
$AUDIO_COMP = "/Script/CoreUObject.Class'/Script/Engine.AudioComponent'"
function SoundPlay($name, [double]$x, [double]$y) {
  $n = New-Call $AUDIO_COMP 'Play' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $AUDIO_COMP
  Add-Pin $n 'StartTime' 'in' 'real' 'float' $null '0.0'
  Connect (New-VarGet $name $null 'object' '' $AUDIO_COMP ($x - 200) ($y + 200)) $name $n 'self'
  return $n
}
function SoundFade($name, [double]$x, [double]$y) {
  $n = New-Call $AUDIO_COMP 'FadeOut' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $AUDIO_COMP
  Add-Pin $n 'FadeOutDuration' 'in' 'real' 'float' $null '0.25'
  Add-Pin $n 'FadeVolumeLevel' 'in' 'real' 'float' $null '0.0'
  Connect (New-VarGet $name $null 'object' '' $AUDIO_COMP ($x - 200) ($y + 200)) $name $n 'self'
  return $n
}
function FxPlay($name, [double]$x, [double]$y) {
  $n = New-Call $ACTOR_COMPONENT 'Activate' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR_COMPONENT
  Add-Pin $n 'bReset' 'in' 'bool' '' $null 'true'
  Connect (New-VarGet $name $null 'object' '' $EMITTER ($x - 200) ($y + 200)) $name $n 'self'
  return $n
}

# ===== BP_HellLava =========================================================================================
Reset-Graph 100
$touch = Event 'ReceiveActorBeginOverlap' 0 0
Add-Pin $touch 'OtherActor' 'out' 'object' '' $ACTOR
$isPlayer = New-Branch 450 0
Connect (PlayerIn 'KillZone' 300 200) 'ReturnValue' $isPlayer 'Condition'
Connect $touch 'then' $isPlayer 'execute'
Connect $isPlayer 'then' (SendBack 750 0) 'execute'
Write-Graph 'BP_HellLava_EventGraph.txt'

# ===== BP_FlameJet =========================================================================================
Reset-Graph 100
function Comp($name, $obj, $x, $y) { New-VarGet $name $null 'object' '' $obj $x $y }
function Seconds($name, $x, $y) {
  $n = Delay '0.0' $x $y
  Connect (New-VarGet $name $null 'real' 'double' $null ($x - 200) ($y + 200)) $name $n 'Duration'
  return $n
}
# The Jet emitter (the FlameJet effect, import_flame_jet.py) on or off: Activate with a reset, or Deactivate.
function Jet($on, $x, $y) {
  $n = New-Call $ACTOR_COMPONENT $(if ($on) { 'Activate' } else { 'Deactivate' }) $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR_COMPONENT
  if ($on) { Add-Pin $n 'bReset' 'in' 'bool' '' $null 'true' }
  Connect (Comp 'Jet' $EMITTER ($x - 200) ($y + 200)) 'Jet' $n 'self'
  return $n
}
$begin = Event 'ReceiveBeginPlay' 0 0
# Begin Play: the sounds at SE Volume x Master Volume first (2026-11-22).
$cast = GameInstance 300 1600
$vol = New-Operator 'Multiply' 'Multiply_DoubleDouble' 'real' 'double' 'real' 600 1850
(Get-Pin $vol 'ReturnValue').Sub = 'double'
Connect (GiGet $cast 'SE Volume' 'real' 'double' 350 1850) 'SE Volume' $vol 'A'
Connect (GiGet $cast 'Master Volume' 'real' 'double' 350 1950) 'Master Volume' $vol 'B'
$prev = $cast; $vx = 750
foreach ($name in 'WarnSound', 'EruptSound', 'RoarSound', 'HurtSound') {
  $v = New-Call $AUDIO_COMP 'SetVolumeMultiplier' $false $vx 1600
  Add-Pin $v 'self' 'in' 'object' '' $AUDIO_COMP
  Add-Pin $v 'NewVolumeMultiplier' 'in' 'real' 'float'
  Connect (New-VarGet $name $null 'object' '' $AUDIO_COMP ($vx - 200) 1800) $name $v 'self'
  Connect $vol 'ReturnValue' $v 'NewVolumeMultiplier'
  Connect $prev 'then' $v 'execute'
  $prev = $v; $vx += 300
}
$first = Seconds 'StartDelay' 300 0
Connect $begin 'then' $cast 'execute'
Connect $prev 'then' $first 'execute'
Connect $cast 'CastFailed' $first 'execute'
$flare = New-Call $ACTOR_COMPONENT 'Activate' $false 600 0
Add-Pin $flare 'self' 'in' 'object' '' $ACTOR_COMPONENT
Add-Pin $flare 'bReset' 'in' 'bool' '' $null 'true'
Connect (Comp 'Fire' $EMITTER 400 200) 'Fire' $flare 'self'
$warnSound = SoundPlay 'WarnSound' 900 300
$warn = Seconds 'WarnSeconds' 900 0
$show = Jet $true 1200 0
$eruptSound = SoundPlay 'EruptSound' 1200 300
$roar = SoundPlay 'RoarSound' 1500 300
$eruptFx = FxPlay 'EruptFx' 1800 300
$burning = SetSelf 'Burning' 'true' 1500 0
$burn = Seconds 'BurnSeconds' 1800 0
$hide = Jet $false 2100 0
$hush = SoundFade 'RoarSound' 2100 300
$smokeFx = FxPlay 'SmokeFx' 2400 300
$cool = SetSelf 'Burning' 'false' 2400 0
$out = New-Call $ACTOR_COMPONENT 'Deactivate' $false 2700 0
Add-Pin $out 'self' 'in' 'object' '' $ACTOR_COMPONENT
Connect (Comp 'Fire' $EMITTER 2500 200) 'Fire' $out 'self'
$off = Seconds 'OffSeconds' 3000 0
Connect $first 'then' $flare 'execute'
Chain @($flare, $warnSound, $warn, $show, $eruptSound, $roar, $eruptFx, $burning, $burn, $hide, $hush, $smokeFx, $cool, $out, $off)
Connect $off 'then' $flare 'execute'
# Every frame: burning and the player in the fire.
$tick = Event 'ReceiveTick' 0 700
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$hot = New-Branch 300 700
Connect (New-VarGet 'Burning' $null 'bool' '' $null 150 900) 'Burning' $hot 'Condition'
Connect $tick 'then' $hot 'execute'
$caught = New-Branch 600 700
Connect (PlayerIn 'HitBox' 450 950) 'ReturnValue' $caught 'Condition'
Connect $hot 'then' $caught 'execute'
Connect $caught 'then' (SendBack 900 700 'HurtSound') 'execute'
Write-Graph 'BP_FlameJet_EventGraph.txt'
