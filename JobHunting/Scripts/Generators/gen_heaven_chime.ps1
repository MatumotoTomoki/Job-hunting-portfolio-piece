param([string]$OutDir)
# Paste text for BP_ChimeJewel (components and variables from setup_heaven_chime.py):
#   Tick: beat = floor(game time / BeatSeconds); local = (beat - StartBeat) mod LoopBeats.
#   local < RingBeats: ringing - on the first such tick it chimes (ChimeSound at Pitch, ChimeAttenuation, volume
#   GI SE Volume x Master Volume); Solid shown and colliding, Ghost and Hint hidden.
#   Otherwise: Solid hidden, no collision, Ghost shown, Hint shown only on the beat before it rings (local = LoopBeats - 1).
if (-not $OutDir) { throw 'OutDir is required' }
$lightGen = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_heaven_light.ps1') -Encoding UTF8
$cut = ($lightGen | Select-String -Pattern '^# ===== BP_LightBeam' | Select-Object -First 1).LineNumber - 1
$helpers = $lightGen[1..($cut - 1)] -join "`n"
. ([ScriptBlock]::Create($helpers))

$SOUND_BASE = "/Script/CoreUObject.Class'/Script/Engine.SoundBase'"
$ATTENUATION = "/Script/CoreUObject.Class'/Script/Engine.SoundAttenuation'"
$CONCURRENCY = "/Script/CoreUObject.Class'/Script/Engine.SoundConcurrency'"

function Int($name, [double]$x, [double]$y) { New-VarGet $name $null 'int' '' $null $x $y }
function IntOp($operation, $func, $a, $aPin, $b, $bPin, [double]$x, [double]$y, $outCat = 'int') {
  $n = New-Operator $operation $func 'int' '' $outCat $x $y
  if ($a) { Connect $a $aPin $n 'A' } else { (Get-Pin $n 'A').Default = $aPin }
  if ($b) { Connect $b $bPin $n 'B' } else { (Get-Pin $n 'B').Default = $bPin }
  return $n
}
# Solid or not: returns (first, last).
function Shape($solid, [double]$x, [double]$y, $hint) {
  $c = Collide 'Solid' $(if ($solid) { 'QueryAndPhysics' } else { 'NoCollision' }) $x $y
  $s = Visible 'Solid' $(if ($solid) { 'true' } else { 'false' }) ($x + 300) $y
  $g = Visible 'Ghost' $(if ($solid) { 'false' } else { 'true' }) ($x + 600) $y
  $h = Visible 'Hint' $hint ($x + 900) $y
  Chain @($c, $s, $g, $h)
  return @($c, $h)
}

Reset-Graph 100
$tick = Event 'ReceiveTick' 0 0
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
# Where in the loop are we?
$beatSafe = MathCall 'FMax' @('A', 'B') 'real' 'double' 'real' 'double' 200 700
Connect (Real 'BeatSeconds' 0 700) 'BeatSeconds' $beatSafe 'A'
(Get-Pin $beatSafe 'B').Default = '0.05'
$beats = Op 'Divide' 'Divide_DoubleDouble' (Now 200 550) 'ReturnValue' $beatSafe 'ReturnValue' 400 600
$beat = MathCall 'FFloor' @('A') 'real' 'double' 'int' '' 600 600
Connect $beats 'ReturnValue' $beat 'A'
$loop = MathCall 'Max' @('A', 'B') 'int' '' 'int' '' 400 850
Connect (Int 'LoopBeats' 200 850) 'LoopBeats' $loop 'A'
(Get-Pin $loop 'B').Default = '1'
$fromStart = IntOp 'Subtract' 'Subtract_IntInt' $beat 'ReturnValue' (Int 'StartBeat' 600 750) 'StartBeat' 800 650
$far = IntOp 'Multiply' 'Multiply_IntInt' $loop 'ReturnValue' $null '1000' 800 850
$positive = IntOp 'Add' 'Add_IntInt' $fromStart 'ReturnValue' $far 'ReturnValue' 1000 700
$local = MathCall 'Percent_IntInt' @('A', 'B') 'int' '' 'int' '' 1200 700
Connect $positive 'ReturnValue' $local 'A'
Connect $loop 'ReturnValue' $local 'B'
$ringNow = IntOp 'Less' 'Less_IntInt' $local 'ReturnValue' (Int 'RingBeats' 1200 900) 'RingBeats' 1400 700 'bool'
$last = IntOp 'Subtract' 'Subtract_IntInt' $loop 'ReturnValue' $null '1' 1200 1000
$hintNow = IntOp 'EqualEqual' 'EqualEqual_IntInt' $local 'ReturnValue' $last 'ReturnValue' 1400 950 'bool'

$ring = New-Branch 300 0
Connect $ringNow 'ReturnValue' $ring 'Condition'
Connect $tick 'then' $ring 'execute'
# Ringing.
$was = New-Branch 600 -400
Connect (Bool 'Ringing' 450 -250) 'Ringing' $was 'Condition'
Connect $ring 'then' $was 'execute'
$start = SetSelf 'Ringing' 'bool' 'true' 900 -600
Connect $was 'else' $start 'execute'
$cast = GameInstance 1200 -600
Connect $start 'then' $cast 'execute'
$play = New-Call $STATICS 'PlaySoundAtLocation' $false 1600 -600
Add-Pin $play 'Sound' 'in' 'object' '' $SOUND_BASE
Add-Pin $play 'Location' 'in' 'struct' '' $VECTOR
Add-Pin $play 'Rotation' 'in' 'struct' '' $ROTATOR '0, 0, 0'
Add-Pin $play 'VolumeMultiplier' 'in' 'real' 'float' $null '1.0'
Add-Pin $play 'PitchMultiplier' 'in' 'real' 'float' $null '1.0'
Add-Pin $play 'StartTime' 'in' 'real' 'float' $null '0.0'
Add-Pin $play 'AttenuationSettings' 'in' 'object' '' $ATTENUATION
Add-Pin $play 'ConcurrencySettings' 'in' 'object' '' $CONCURRENCY
Add-Pin $play 'OwningActor' 'in' 'object' '' $ACTOR
Connect (New-VarGet 'ChimeSound' $null 'object' '' $SOUND_BASE 1350 -350) 'ChimeSound' $play 'Sound'
$here = New-Call $ACTOR 'K2_GetActorLocation' $true 1350 -250
Add-Pin $here 'self' 'in' 'object' '' $ACTOR
Add-Pin $here 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $here 'ReturnValue' $play 'Location'
$volume = Op 'Multiply' 'Multiply_DoubleDouble' (GiGet $cast 'SE Volume' 'real' 'double' 1150 -150) 'SE Volume' (GiGet $cast 'Master Volume' 'real' 'double' 1150 -50) 'Master Volume' 1400 -120
Connect $volume 'ReturnValue' $play 'VolumeMultiplier'
Connect (Real 'Pitch' 1400 0) 'Pitch' $play 'PitchMultiplier'
Connect (New-VarGet 'ChimeAttenuation' $null 'object' '' $ATTENUATION 1400 100) 'ChimeAttenuation' $play 'AttenuationSettings'
Connect $cast 'then' $play 'execute'
$solid = Shape $true 2000 -400 'false'
Connect $was 'then' $solid[0] 'execute'
Connect $play 'then' $solid[0] 'execute'
Connect $cast 'CastFailed' $solid[0] 'execute'
# Resting.
$stop = SetSelf 'Ringing' 'bool' 'false' 600 300
Connect $ring 'else' $stop 'execute'
$ghost = Shape $false 1700 300 @($hintNow, 'ReturnValue')
Connect $stop 'then' $ghost[0] 'execute'
Write-Graph 'BP_ChimeJewel_EventGraph.txt'
