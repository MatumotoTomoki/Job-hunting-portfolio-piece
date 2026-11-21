param([string]$OutDir)
# Paste text for BP_Wings (components and variables from setup_heaven_wings.py):
#   Begin Play: if the run already has wings (GI HasWings), after 0.2 s they are worn at once.
#   Touched by the player (Grab) while not Owned: worn (Owned, Grab off, snapped onto the player), GI HasWings.
#   Tick while Owned: spread = falling and Jump held (Space or gamepad bottom button); Open eases to spread (Wings
#   scaled out from folded 0.3 / 0.6 to 1); while spread and falling faster than GlideFall, the fall is held to GlideFall.
#   Sounds and effects (2026-11-21): taken - GetSound + GetFx; spreading - FlapSound, GlideSound and GlideFx on;
#   folding - GlideSound fades, GlideFx off (WasSpread remembers the last tick).
if (-not $OutDir) { throw 'OutDir is required' }
# The helpers of gen_heaven_light.ps1 (everything before its first graph).
$lightGen = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_heaven_light.ps1') -Encoding UTF8
$cut = ($lightGen | Select-String -Pattern '^# ===== BP_LightBeam' | Select-Object -First 1).LineNumber - 1
$helpers = $lightGen[1..($cut - 1)] -join "`n"
. ([ScriptBlock]::Create($helpers))

$MOVEMENT = "/Script/CoreUObject.Class'/Script/Engine.MovementComponent'"
$NAV_MOVE = "/Script/CoreUObject.Class'/Script/Engine.NavMovementInterface'"
$KEY = "/Script/CoreUObject.ScriptStruct'/Script/InputCore.Key'"
$ATTACH_ENUM = "/Script/CoreUObject.Enum'/Script/Engine.EAttachmentRule'"

function Wear([double]$x, [double]$y) {
  $owned = SetSelf 'Owned' 'bool' 'true' $x $y
  $off = New-Call $PRIMITIVE 'SetCollisionEnabled' $false ($x + 300) $y
  Add-Pin $off 'self' 'in' 'object' '' $PRIMITIVE
  Add-Pin $off 'NewType' 'in' 'byte' '' $COLLISION_ENUM 'NoCollision'
  Connect (Comp 'Grab' $SPHERE ($x + 100) ($y + 200)) 'Grab' $off 'self'
  $attach = New-Call $ACTOR 'K2_AttachToActor' $false ($x + 600) $y
  Add-Pin $attach 'self' 'in' 'object' '' $ACTOR
  Add-Pin $attach 'ParentActor' 'in' 'object' '' $ACTOR
  Add-Pin $attach 'SocketName' 'in' 'name' '' $null 'None'
  Add-Pin $attach 'LocationRule' 'in' 'byte' '' $ATTACH_ENUM 'SnapToTarget'
  Add-Pin $attach 'RotationRule' 'in' 'byte' '' $ATTACH_ENUM 'SnapToTarget'
  Add-Pin $attach 'ScaleRule' 'in' 'byte' '' $ATTACH_ENUM 'KeepWorld'
  Add-Pin $attach 'bWeldSimulatedBodies' 'in' 'bool' '' $null 'false'
  Add-Pin $attach 'ReturnValue' 'out' 'bool'
  Connect (Player ($x + 400) ($y + 250)) 'ReturnValue' $attach 'ParentActor'
  Chain @($owned, $off, $attach)
  return @($owned, $attach)
}
function KeyDown($keyName, [double]$x, [double]$y) {
  $n = New-Call $CONTROLLER 'IsInputKeyDown' $true $x $y
  Add-Pin $n 'self' 'in' 'object' '' $CONTROLLER
  Add-Pin $n 'Key' 'in' 'struct' '' $KEY $keyName
  Add-Pin $n 'ReturnValue' 'out' 'bool'
  Connect (Controller ($x - 250) $y) 'ReturnValue' $n 'self'
  return $n
}

# Sounds and effects (setup_wings_effects.py, 2026-11-21).
$AUDIO_COMP = "/Script/CoreUObject.Class'/Script/Engine.AudioComponent'"
$EMITTER = "/Script/CoreUObject.Class'/Script/Effekseer.EffekseerEmitterComponent'"
$ACTOR_COMP = "/Script/CoreUObject.Class'/Script/Engine.ActorComponent'"
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
  Add-Pin $n 'FadeOutDuration' 'in' 'real' 'float' $null '0.4'
  Add-Pin $n 'FadeVolumeLevel' 'in' 'real' 'float' $null '0.0'
  Connect (New-VarGet $name $null 'object' '' $AUDIO_COMP ($x - 200) ($y + 200)) $name $n 'self'
  return $n
}
function FxPlay($name, [double]$x, [double]$y) {
  $n = New-Call $ACTOR_COMP 'Activate' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR_COMP
  Add-Pin $n 'bReset' 'in' 'bool' '' $null 'true'
  Connect (New-VarGet $name $null 'object' '' $EMITTER ($x - 200) ($y + 200)) $name $n 'self'
  return $n
}
function FxStop($name, [double]$x, [double]$y) {
  $n = New-Call $ACTOR_COMP 'Deactivate' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR_COMP
  Connect (New-VarGet $name $null 'object' '' $EMITTER ($x - 200) ($y + 200)) $name $n 'self'
  return $n
}
# The named sounds at SE Volume x Master Volume. Returns (first, last).
function SoundVolumes([string[]]$names, [double]$x, [double]$y) {
  $cast = GameInstance $x $y
  $vol = Op 'Multiply' 'Multiply_DoubleDouble' (GiGet $cast 'SE Volume' 'real' 'double' ($x + 50) ($y + 250)) 'SE Volume' (GiGet $cast 'Master Volume' 'real' 'double' ($x + 50) ($y + 350)) 'Master Volume' ($x + 250) ($y + 250)
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

Reset-Graph 100
# Begin Play: the sounds' volume; then, wings already won this run.
$begin = Event 'ReceiveBeginPlay' 0 (-600)
$volumes = SoundVolumes @('GetSound', 'FlapSound', 'GlideSound') 300 (-600)
$settle = Delay '0.2' 300 0
$cast = GameInstance 650 0
$hasThem = New-Branch 950 0
Connect (GiGet $cast 'HasWings' 'bool' '' 750 250) 'HasWings' $hasThem 'Condition'
$wear1 = Wear 1250 0
Connect $begin 'then' $volumes[0] 'execute'
Connect $volumes[1] 'then' $settle 'execute'
Connect $settle 'then' $cast 'execute'
Connect $cast 'then' $hasThem 'execute'
Connect $hasThem 'then' $wear1[0] 'execute'

# Picked up.
$touch = Event 'ReceiveActorBeginOverlap' 0 700
Add-Pin $touch 'OtherActor' 'out' 'object' '' $ACTOR
$once = New-Branch 300 700
Connect (Bool 'Owned' 150 900) 'Owned' $once 'Condition'
$isPlayer = New-Branch 550 700
$overlap = New-Call $PRIMITIVE 'IsOverlappingActor' $true 450 950
Add-Pin $overlap 'self' 'in' 'object' '' $PRIMITIVE
Add-Pin $overlap 'Other' 'in' 'object' '' $ACTOR
Add-Pin $overlap 'ReturnValue' 'out' 'bool'
Connect (Comp 'Grab' $SPHERE 250 950) 'Grab' $overlap 'self'
Connect (Player 200 1050) 'ReturnValue' $overlap 'Other'
Connect $overlap 'ReturnValue' $isPlayer 'Condition'
$wear2 = Wear 800 700
$getSound = SoundPlay 'GetSound' 1800 700
$getFx = FxPlay 'GetFx' 2100 700
$cast2 = GameInstance 2500 700
$remember = GiSet $cast2 'HasWings' 'bool' '' 2800 700 'true'
Connect $touch 'then' $once 'execute'
Connect $once 'else' $isPlayer 'execute'
Connect $isPlayer 'then' $wear2[0] 'execute'
Connect $wear2[1] 'then' $getSound 'execute'
Chain @($getSound, $getFx, $cast2)
Connect $cast2 'then' $remember 'execute'

# Gliding.
$tick = Event 'ReceiveTick' 0 1500
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$worn = New-Branch 300 1500
Connect (Bool 'Owned' 150 1700) 'Owned' $worn 'Condition'
Connect $tick 'then' $worn 'execute'
$falling = New-Call $NAV_MOVE 'IsFalling' $true 450 1900
Add-Pin $falling 'self' 'in' 'interface' '' $NAV_MOVE
Add-Pin $falling 'ReturnValue' 'out' 'bool'
Connect (Movement 250 1900) 'CharacterMovement' $falling 'self'
$held = Both (KeyDown 'SpaceBar' 450 2050) 'ReturnValue' (KeyDown 'Gamepad_FaceButton_Bottom' 450 2200) 'ReturnValue' 'BooleanOR' 700 2100
$spread = Both $falling 'ReturnValue' $held 'ReturnValue' 'BooleanAND' 900 1950
$aim = New-Call $MATH 'SelectFloat' $true 1100 1950
Add-Pin $aim 'A' 'in' 'real' 'double' $null '1.0'
Add-Pin $aim 'B' 'in' 'real' 'double' $null '0.0'
Add-Pin $aim 'bPickA' 'in' 'bool'
Add-Pin $aim 'ReturnValue' 'out' 'real' 'double'
Connect $spread 'ReturnValue' $aim 'bPickA'
$ease = New-Call $MATH 'FInterpTo' $true 1300 1850
Add-Pin $ease 'Current' 'in' 'real' 'double'
Add-Pin $ease 'Target' 'in' 'real' 'double'
Add-Pin $ease 'DeltaTime' 'in' 'real' 'double'
Add-Pin $ease 'InterpSpeed' 'in' 'real' 'double' $null '10.0'
Add-Pin $ease 'ReturnValue' 'out' 'real' 'double'
Connect (Real 'Open' 1100 1800) 'Open' $ease 'Current'
Connect $aim 'ReturnValue' $ease 'Target'
Connect $tick 'DeltaSeconds' $ease 'DeltaTime'
$setOpen = SetReal 'Open' 600 1500
Connect $ease 'ReturnValue' $setOpen 'Open'
Connect $worn 'then' $setOpen 'execute'
function Between($from, $to, [double]$x, [double]$y) {
  $n = New-Call $MATH 'Lerp' $true $x $y
  Add-Pin $n 'A' 'in' 'real' 'double' $null $from
  Add-Pin $n 'B' 'in' 'real' 'double' $null $to
  Add-Pin $n 'Alpha' 'in' 'real' 'double'
  Add-Pin $n 'ReturnValue' 'out' 'real' 'double'
  Connect $setOpen 'Output_Get' $n 'Alpha'
  return $n
}
$size = New-Call $MATH 'MakeVector' $true 1100 1600
Add-Pin $size 'X' 'in' 'real' 'double' $null '1.0'
Add-Pin $size 'Y' 'in' 'real' 'double'
Add-Pin $size 'Z' 'in' 'real' 'double'
Add-Pin $size 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect (Between '0.3' '1.0' 900 1650) 'ReturnValue' $size 'Y'
Connect (Between '0.6' '1.0' 900 1750) 'ReturnValue' $size 'Z'
$scale = New-Call $SCENE 'SetRelativeScale3D' $false 1300 1500
Add-Pin $scale 'self' 'in' 'object' '' $SCENE
Add-Pin $scale 'NewScale3D' 'in' 'struct' '' $VECTOR
Connect (Comp 'Wings' $SCENE 1100 1450) 'Wings' $scale 'self'
Connect $size 'ReturnValue' $scale 'NewScale3D'
Connect $setOpen 'then' $scale 'execute'
# Held fall.
$velocity = New-VarGet 'Velocity' $MOVEMENT 'struct' '' $VECTOR 1500 2100
Connect (Movement 1300 2100) 'CharacterMovement' $velocity 'self'
$parts = New-Call $MATH 'BreakVector' $true 1700 2100
Add-Pin $parts 'InVec' 'in' 'struct' '' $VECTOR
Add-Pin $parts 'X' 'out' 'real' 'double'
Add-Pin $parts 'Y' 'out' 'real' 'double'
Add-Pin $parts 'Z' 'out' 'real' 'double'
Connect $velocity 'Velocity' $parts 'InVec'
$limit = Op 'Multiply' 'Multiply_DoubleDouble' (Real 'GlideFall' 1700 2350) 'GlideFall' $null '-1.0' 1900 2350
$sinking = Op 'Less' 'Less_DoubleDouble' $parts 'Z' $limit 'ReturnValue' 2100 2200 'bool'
$glide = New-Branch 1700 1500
Connect (Both $spread 'ReturnValue' $sinking 'ReturnValue' 'BooleanAND' 2300 2000) 'ReturnValue' $glide 'Condition'
# Spread or folded since the last tick: "basa", the wind and the trail start; or the wind fades and the trail stops.
# (WasSpread is read before it is set.)
$changed = New-Branch 1500 2600
$differs = New-Operator 'NotEqual' 'NotEqual_BoolBool' 'bool' '' 'bool' 1300 2800
Connect $spread 'ReturnValue' $differs 'A'
Connect (Bool 'WasSpread' 1100 2900) 'WasSpread' $differs 'B'
Connect $differs 'ReturnValue' $changed 'Condition'
$opening = New-Branch 1750 2600
Connect $spread 'ReturnValue' $opening 'Condition'
$flap = SoundPlay 'FlapSound' 2050 2450
# The wind loop rises after the basa (2026-11-21, bought sounds).
$wind = New-Call $AUDIO_COMP 'FadeIn' $false 2350 2450
Add-Pin $wind 'self' 'in' 'object' '' $AUDIO_COMP
Add-Pin $wind 'FadeInDuration' 'in' 'real' 'float' $null '0.6'
Add-Pin $wind 'FadeVolumeLevel' 'in' 'real' 'float' $null '1.0'
Add-Pin $wind 'StartTime' 'in' 'real' 'float' $null '0.0'
Connect (New-VarGet 'GlideSound' $null 'object' '' $AUDIO_COMP 2150 2650) 'GlideSound' $wind 'self'
$trail = FxPlay 'GlideFx' 2650 2450
$hush = SoundFade 'GlideSound' 2050 2850
$trailOff = FxStop 'GlideFx' 2350 2850
$setWas = SetSelf 'WasSpread' 'bool' $null 3000 2600
Connect $spread 'ReturnValue' $setWas 'WasSpread'
Connect $scale 'then' $changed 'execute'
Connect $changed 'then' $opening 'execute'
Connect $changed 'else' $glide 'execute'
Connect $opening 'then' $flap 'execute'
Chain @($flap, $wind, $trail)
Connect $trail 'then' $setWas 'execute'
Connect $opening 'else' $hush 'execute'
Chain @($hush, $trailOff)
Connect $trailOff 'then' $setWas 'execute'
Connect $setWas 'then' $glide 'execute'
$slowed = New-Call $MATH 'MakeVector' $true 2300 1750
Add-Pin $slowed 'X' 'in' 'real' 'double'
Add-Pin $slowed 'Y' 'in' 'real' 'double'
Add-Pin $slowed 'Z' 'in' 'real' 'double'
Add-Pin $slowed 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $parts 'X' $slowed 'X'
Connect $parts 'Y' $slowed 'Y'
Connect $limit 'ReturnValue' $slowed 'Z'
$hold = New-VarSet 'Velocity' $MOVEMENT 'struct' $VECTOR 2550 1500
Connect (Movement 2350 1650) 'CharacterMovement' $hold 'self'
Connect $slowed 'ReturnValue' $hold 'Velocity'
Connect $glide 'then' $hold 'execute'
Write-Graph 'BP_Wings_EventGraph.txt'
