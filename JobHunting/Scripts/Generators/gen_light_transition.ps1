param([string]$OutDir)
# Paste text for area 3 -> 4 (components and variables from setup_light_transition.py):
#   BP_LightGate_EventGraph.txt  Begin Play: the pillar (Shaft) hidden. Tick:
#     not Descended: the player in Approach -> Descended, DescendAt, the pillar shown, the sound, the motes.
#     Descended: the pillar grows down from ShaftHeight to the ground over DescendSeconds (eased).
#       not Ascending: once it is down and the player is in Center -> Ascending, AscendAt, all input off (no pause),
#         Flying, stopped, StartLoc, the rising sound.
#       Ascending: the player floats up RiseHeight over RiseSeconds (eased); from FadeAt of that, once: Leaving, the
#         item effects saved, ChangingArea and LightArrival set, white over 1.2 s, NextLevel.
#   BP_LightArrival_EventGraph.txt  Begin Play: the pillar hidden; a moment later, only if LightArrival: clear it, all
#     input off, the screen clears from white, the pillar shown full, the motes, Flying, the player DescendHeight up.
#     Tick: coming down inside the pillar over DescendSeconds; landed: Walking, the fading sound, the motes stop; the
#     pillar thins and fades over VanishSeconds, then it hides and the controls come back.
if (-not $OutDir) { throw 'OutDir is required' }
$lightGen = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_heaven_light.ps1') -Encoding UTF8
$cut = ($lightGen | Select-String -Pattern '^# ===== BP_LightBeam' | Select-Object -First 1).LineNumber - 1
$helpers = $lightGen[1..($cut - 1)] -join "`n"
. ([ScriptBlock]::Create($helpers))

$EMITTER = "/Script/CoreUObject.Class'/Script/Effekseer.EffekseerEmitterComponent'"
$ACTOR_COMPONENT = "/Script/CoreUObject.Class'/Script/Engine.ActorComponent'"
$AUDIO = "/Script/CoreUObject.Class'/Script/Engine.AudioComponent'"
$MESH_COMPONENT = "/Script/CoreUObject.Class'/Script/Engine.MeshComponent'"
$MOVEMENT_BASE = "/Script/CoreUObject.Class'/Script/Engine.MovementComponent'"
$MODE_ENUM = "/Script/CoreUObject.Enum'/Script/Engine.EMovementMode'"
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
# t = clamp((now - <since>) / <seconds>)
function Progress($since, $seconds, [double]$x, [double]$y) {
  $elapsed = Op 'Subtract' 'Subtract_DoubleDouble' (Now $x $y) 'ReturnValue' (Real $since $x ($y + 100)) $since ($x + 200) $y
  $part = Op 'Divide' 'Divide_DoubleDouble' $elapsed 'ReturnValue' (Real $seconds ($x + 200) ($y + 150)) $seconds ($x + 400) $y
  return Clamp01 $part 'ReturnValue' ($x + 600) $y
}
function Emit($func, [double]$x, [double]$y) {
  $n = New-Call $ACTOR_COMPONENT $func $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR_COMPONENT
  if ($func -eq 'Activate') { Add-Pin $n 'bReset' 'in' 'bool' '' $null 'true' }
  Connect (Comp 'MotesFx' $EMITTER ($x - 200) ($y + 200)) 'MotesFx' $n 'self'
  return $n
}
function PlaySound($componentName, $cast, [double]$x, [double]$y) {
  # volume = SE Volume x Master Volume, then play: returns (first, last)
  $vol = Op 'Multiply' 'Multiply_DoubleDouble' (GiGet $cast 'SE Volume' 'real' 'double' ($x - 250) ($y + 250)) 'SE Volume' (GiGet $cast 'Master Volume' 'real' 'double' ($x - 250) ($y + 350)) 'Master Volume' $x ($y + 300)
  $v = New-Call $AUDIO 'SetVolumeMultiplier' $false $x $y
  Add-Pin $v 'self' 'in' 'object' '' $AUDIO
  Add-Pin $v 'NewVolumeMultiplier' 'in' 'real' 'float'
  Connect (Comp $componentName $AUDIO ($x - 200) ($y + 200)) $componentName $v 'self'
  Connect $vol 'ReturnValue' $v 'NewVolumeMultiplier'
  $p = New-Call $AUDIO 'Play' $false ($x + 300) $y
  Add-Pin $p 'self' 'in' 'object' '' $AUDIO
  Add-Pin $p 'StartTime' 'in' 'real' 'float' $null '0.0'
  Connect (Comp $componentName $AUDIO ($x + 100) ($y + 200)) $componentName $p 'self'
  Connect $v 'then' $p 'execute'
  return @($v, $p)
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
function Mode($mode, [double]$x, [double]$y) {
  $n = New-Call $CHAR_MOVE 'SetMovementMode' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $CHAR_MOVE
  Add-Pin $n 'NewMovementMode' 'in' 'byte' '' $MODE_ENUM $mode
  Add-Pin $n 'NewCustomMode' 'in' 'byte' '' $null '0'
  Connect (Movement ($x - 100) ($y + 200)) 'CharacterMovement' $n 'self'
  return $n
}
function White-Fade($from, $to, $seconds, $hold, [double]$x, [double]$y) {
  $n = Fade $from $to $seconds $hold $x $y
  (Get-Pin $n 'Color').Default = $WHITE
  return $n
}
function Hide-Shaft($hidden, [double]$x, [double]$y) {
  $n = New-Call $SCENE 'SetHiddenInGame' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $SCENE
  Add-Pin $n 'NewHidden' 'in' 'bool' '' $null $hidden
  Add-Pin $n 'bPropagateToChildren' 'in' 'bool' '' $null 'false'
  Connect (Comp 'Shaft' $STATIC_MESH ($x - 200) ($y + 200)) 'Shaft' $n 'self'
  return $n
}
# The pillar: centre at z, width w (scale), height h cm (two nodes: place, size); returns (place, size).
function Shape-Shaft($z, $w, $h, [double]$x, [double]$y) {
  $at = MakeVec '0.0' '0.0' $z ($x - 200) ($y + 350)
  $place = New-Call $SCENE 'K2_SetRelativeLocation' $false $x $y
  Add-Pin $place 'self' 'in' 'object' '' $SCENE
  Add-Pin $place 'NewLocation' 'in' 'struct' '' $VECTOR
  Add-Pin $place 'bSweep' 'in' 'bool' '' $null 'false'
  Add-Pin $place 'SweepHitResult' 'out' 'struct' '' $HIT
  Add-Pin $place 'bTeleport' 'in' 'bool' '' $null 'true'
  Connect (Comp 'Shaft' $STATIC_MESH ($x - 200) ($y + 200)) 'Shaft' $place 'self'
  Connect $at 'ReturnValue' $place 'NewLocation'
  $tall = Op 'Multiply' 'Multiply_DoubleDouble' $h[0] $h[1] $null '0.01' ($x + 50) ($y + 500)
  $atLeast = MathCall 'FMax' @('A', 'B') 'real' 'double' 'real' 'double' ($x + 250) ($y + 500)
  Connect $tall 'ReturnValue' $atLeast 'A'
  (Get-Pin $atLeast 'B').Default = '0.01'
  $size = MakeVec $w $w @($atLeast, 'ReturnValue') ($x + 300) ($y + 350)
  $scale = New-Call $SCENE 'SetRelativeScale3D' $false ($x + 300) $y
  Add-Pin $scale 'self' 'in' 'object' '' $SCENE
  Add-Pin $scale 'NewScale3D' 'in' 'struct' '' $VECTOR
  Connect (Comp 'Shaft' $STATIC_MESH ($x + 100) ($y + 200)) 'Shaft' $scale 'self'
  Connect $size 'ReturnValue' $scale 'NewScale3D'
  Connect $place 'then' $scale 'execute'
  return @($place, $scale)
}
function PlayerIn($boxName, [double]$x, [double]$y) {
  $n = New-Call $PRIMITIVE 'IsOverlappingActor' $true $x $y
  Add-Pin $n 'self' 'in' 'object' '' $PRIMITIVE
  Add-Pin $n 'Other' 'in' 'object' '' $ACTOR
  Add-Pin $n 'ReturnValue' 'out' 'bool'
  Connect (Comp $boxName $BOX ($x - 200) $y) $boxName $n 'self'
  Connect (Player ($x - 200) ($y + 100)) 'ReturnValue' $n 'Other'
  return $n
}

# ===== BP_LightGate ========================================================================================
Reset-Graph 100
$begin = Event 'ReceiveBeginPlay' 0 (-1200)
Connect $begin 'then' (Hide-Shaft 'true' 300 (-1200)) 'execute'

$tick = Event 'ReceiveTick' 0 0
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$down = New-Branch 250 0
Connect (Bool 'Descended' 100 200) 'Descended' $down 'Condition'
Connect $tick 'then' $down 'execute'
# --- waiting for the player to come near ---
$near = New-Branch 500 (-700)
Connect (PlayerIn 'Approach' 400 (-500)) 'ReturnValue' $near 'Condition'
Connect $down 'else' $near 'execute'
$markDown = SetSelf 'Descended' 'bool' 'true' 750 (-700)
$downAt = SetReal 'DescendAt' 1000 (-700)
Connect (Now 900 (-500)) 'ReturnValue' $downAt 'DescendAt'
$show = Hide-Shaft 'false' 1300 (-700)
$cast = GameInstance 1600 (-700)
$chime = PlaySound 'DescendSound' $cast 1900 (-700)
$motesOn = Emit 'Activate' 2550 (-700)
Connect $near 'then' $markDown 'execute'
Chain @($markDown, $downAt, $show, $cast)
Connect $cast 'then' $chime[0] 'execute'
Connect $chime[1] 'then' $motesOn 'execute'
# --- the pillar coming down ---
$d = Progress 'DescendAt' 'DescendSeconds' 200 700
$grown = Ease $d 'ReturnValue' 1000 700
$h = Op 'Multiply' 'Multiply_DoubleDouble' (Real 'ShaftHeight' 1000 850) 'ShaftHeight' $grown 'ReturnValue' 1250 700
$halfH = Op 'Multiply' 'Multiply_DoubleDouble' $h 'ReturnValue' $null '0.5' 1450 800
$centreZ = Op 'Subtract' 'Subtract_DoubleDouble' (Real 'ShaftHeight' 1450 950) 'ShaftHeight' $halfH 'ReturnValue' 1650 850
$width = Real 'ShaftWidth' 1650 1000
$shape = Shape-Shaft @($centreZ, 'ReturnValue') @($width, 'ShaftWidth') @($h, 'ReturnValue') 600 0
Connect $down 'then' $shape[0] 'execute'
$rising = New-Branch 1300 0
Connect (Bool 'Ascending' 1150 200) 'Ascending' $rising 'Condition'
Connect $shape[1] 'then' $rising 'execute'
# --- stepping into the light ---
$ready = Both (Op 'GreaterEqual' 'GreaterEqual_DoubleDouble' $d 'ReturnValue' $null '1.0' 1500 (-250) 'bool') 'ReturnValue' (PlayerIn 'Center' 1500 (-150)) 'ReturnValue' 'BooleanAND' 1700 (-200)
$inLight = New-Branch 1550 (-400)
Connect $ready 'ReturnValue' $inLight 'Condition'
Connect $rising 'else' $inLight 'execute'
$markUp = SetSelf 'Ascending' 'bool' 'true' 1800 (-400)
$upAt = SetReal 'AscendAt' 2050 (-400)
Connect (Now 1950 (-250)) 'ReturnValue' $upAt 'AscendAt'
$freeze = Controller-Input 'DisableInput' 2350 (-400)
$hold = InputCall 'DisableInput' 2650 (-400)
$fly = Mode 'MOVE_Flying' 2950 (-400)
$still = Halt 3250 (-400)
$where = New-Call $ACTOR 'K2_GetActorLocation' $true 3350 (-200)
Add-Pin $where 'self' 'in' 'object' '' $ACTOR
Add-Pin $where 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect (Player 3150 (-150)) 'ReturnValue' $where 'self'
$keep = New-VarSet 'StartLoc' $null 'struct' $VECTOR 3550 (-400)
Connect $where 'ReturnValue' $keep 'StartLoc'
$cast2 = GameInstance 3850 (-400)
$swell = PlaySound 'AscendSound' $cast2 4150 (-400)
Connect $inLight 'then' $markUp 'execute'
Chain @($markUp, $upAt, $freeze, $hold, $fly, $still, $keep, $cast2)
Connect $cast2 'then' $swell[0] 'execute'
# --- rising ---
$r = Progress 'AscendAt' 'RiseSeconds' 1300 1200
$lift = Op 'Multiply' 'Multiply_DoubleDouble' (Real 'RiseHeight' 2100 1350) 'RiseHeight' (Ease $r 'ReturnValue' 2100 1200) 'ReturnValue' 2350 1250
$risen = AddVec (New-VarGet 'StartLoc' $null 'struct' '' $VECTOR 2350 1050) 'StartLoc' (MakeVec '0.0' '0.0' @($lift, 'ReturnValue') 2550 1250) 'ReturnValue' 2750 1150
$float = Put-Player $risen 1600 300
Connect $rising 'then' $float 'execute'
$fadeNow = New-Branch 1900 300
Connect (Op 'GreaterEqual' 'GreaterEqual_DoubleDouble' $r 'ReturnValue' (Real 'FadeAt' 1700 500) 'FadeAt' 1800 450 'bool') 'ReturnValue' $fadeNow 'Condition'
Connect $float 'then' $fadeNow 'execute'
$once = New-Branch 2150 300
Connect (Bool 'Leaving' 2000 500) 'Leaving' $once 'Condition'
Connect $fadeNow 'then' $once 'execute'
$leaving = SetSelf 'Leaving' 'bool' 'true' 2400 300
$cast3 = GameInstance 2700 300
$saved = SaveStats $cast3 3000 300
$moving = GiSet $cast3 'ChangingArea' 'bool' '' 4200 300 'true'
$flag = GiSet $cast3 'LightArrival' 'bool' '' 4450 300 'true'
$toWhite = White-Fade '0.0' '1.0' '1.2' 'true' 4700 300
$wait = Delay '1.3' 5200 300
$open = OpenLevel 5450 300
Connect (New-VarGet 'NextLevel' $null 'name' '' $null 5250 500) 'NextLevel' $open 'LevelName'
Connect $once 'else' $leaving 'execute'
Chain @($leaving, $cast3)
Connect $cast3 'then' $saved[0] 'execute'
Chain @($saved[1], $moving, $flag, $toWhite, $wait, $open)
Write-Graph 'BP_LightGate_EventGraph.txt'

# ===== BP_LightArrival =====================================================================================
Reset-Graph 100
$begin = Event 'ReceiveBeginPlay' 0 (-1200)
$hideFirst = Hide-Shaft 'true' 300 (-1200)
$settle = Delay '0.05' 550 (-1200)
$cast = GameInstance 850 (-1200)
$came = New-Branch 1150 (-1200)
Connect (GiGet $cast 'LightArrival' 'bool' '' 1000 (-1000)) 'LightArrival' $came 'Condition'
$clear = GiSet $cast 'LightArrival' 'bool' '' 1400 (-1200) 'false'
$freeze = Controller-Input 'DisableInput' 1700 (-1200)
$hold = InputCall 'DisableInput' 2000 (-1200)
$fromWhite = White-Fade '1.0' '0.0' '1.8' 'false' 2300 (-1200)
$show = Hide-Shaft 'false' 2800 (-1200)
$fullZ = Op 'Multiply' 'Multiply_DoubleDouble' (Real 'ShaftHeight' 2900 (-800)) 'ShaftHeight' $null '0.5' 3100 (-800)
$full = Shape-Shaft @($fullZ, 'ReturnValue') @((Real 'ShaftWidth' 3100 (-650)), 'ShaftWidth') @((Real 'ShaftHeight' 3100 (-550)), 'ShaftHeight') 3300 (-1200)
$motesOn = Emit 'Activate' 3950 (-1200)
$fly = Mode 'MOVE_Flying' 4250 (-1200)
$still = Halt 4550 (-1200)
$here = New-Call $ACTOR 'K2_GetActorLocation' $true 4650 (-950)
Add-Pin $here 'self' 'in' 'object' '' $ACTOR
Add-Pin $here 'ReturnValue' 'out' 'struct' '' $VECTOR
$highZ = Op 'Add' 'Add_DoubleDouble' (Real 'DescendHeight' 4650 (-800)) 'DescendHeight' $null '92.0' 4850 (-800)
$high = AddVec $here 'ReturnValue' (MakeVec '0.0' '0.0' @($highZ, 'ReturnValue') 5050 (-800)) 'ReturnValue' 5250 (-900)
$up = Put-Player $high 4850 (-1200)
$arriving = SetSelf 'Arriving' 'bool' 'true' 5150 (-1200)
$at = SetReal 'ArriveAt' 5400 (-1200)
Connect (Now 5300 (-1000)) 'ReturnValue' $at 'ArriveAt'
Connect $begin 'then' $hideFirst 'execute'
Chain @($hideFirst, $settle, $cast)
Connect $cast 'then' $came 'execute'
Connect $came 'then' $clear 'execute'
Chain @($clear, $freeze, $hold, $fromWhite, $show, $full[0])
Connect $full[1] 'then' $motesOn 'execute'
Chain @($motesOn, $fly, $still, $up, $arriving, $at)

$tick = Event 'ReceiveTick' 0 0
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$active = New-Branch 250 0
Connect (Bool 'Arriving' 100 200) 'Arriving' $active 'Condition'
Connect $tick 'then' $active 'execute'
$landedYet = New-Branch 500 0
Connect (Bool 'Landed' 350 200) 'Landed' $landedYet 'Condition'
Connect $active 'then' $landedYet 'execute'
# --- coming down ---
$a = Progress 'ArriveAt' 'DescendSeconds' 200 (-600)
$left = Op 'Subtract' 'Subtract_DoubleDouble' $null '1.0' (Ease $a 'ReturnValue' 1000 (-600)) 'ReturnValue' 1200 (-600)
$above = Op 'Multiply' 'Multiply_DoubleDouble' (Real 'DescendHeight' 1200 (-450)) 'DescendHeight' $left 'ReturnValue' 1400 (-550)
$aboveFeet = Op 'Add' 'Add_DoubleDouble' $above 'ReturnValue' $null '92.0' 1600 (-550)
$selfAt = New-Call $ACTOR 'K2_GetActorLocation' $true 1600 (-750)
Add-Pin $selfAt 'self' 'in' 'object' '' $ACTOR
Add-Pin $selfAt 'ReturnValue' 'out' 'struct' '' $VECTOR
$spot = AddVec $selfAt 'ReturnValue' (MakeVec '0.0' '0.0' @($aboveFeet, 'ReturnValue') 1800 (-550)) 'ReturnValue' 2000 (-650)
$sink = Put-Player $spot 800 (-300)
Connect $landedYet 'else' $sink 'execute'
$touched = New-Branch 1100 (-300)
Connect (Op 'GreaterEqual' 'GreaterEqual_DoubleDouble' $a 'ReturnValue' $null '1.0' 950 (-150) 'bool') 'ReturnValue' $touched 'Condition'
Connect $sink 'then' $touched 'execute'
$markLanded = SetSelf 'Landed' 'bool' 'true' 1350 (-300)
$landAt = SetReal 'LandAt' 1600 (-300)
Connect (Now 1500 (-150)) 'ReturnValue' $landAt 'LandAt'
$walk = Mode 'MOVE_Walking' 1900 (-300)
$cast2 = GameInstance 2200 (-300)
$sad = PlaySound 'FadeSound' $cast2 2500 (-300)
$motesOff = Emit 'Deactivate' 3150 (-300)
Connect $touched 'then' $markLanded 'execute'
Chain @($markLanded, $landAt, $walk, $cast2)
Connect $cast2 'then' $sad[0] 'execute'
Connect $sad[1] 'then' $motesOff 'execute'
# --- the light dying away ---
$doneYet = New-Branch 800 300
Connect (Bool 'Done' 650 500) 'Done' $doneYet 'Condition'
Connect $landedYet 'then' $doneYet 'execute'
$v = Progress 'LandAt' 'VanishSeconds' 200 700
$fading = Ease $v 'ReturnValue' 1000 700
$thin = Op 'Multiply' 'Multiply_DoubleDouble' (Real 'ShaftWidth' 1000 850) 'ShaftWidth' (Op 'Subtract' 'Subtract_DoubleDouble' $null '1.0' $fading 'ReturnValue' 1200 750) 'ReturnValue' 1400 800
$thinW = Op 'Add' 'Add_DoubleDouble' $thin 'ReturnValue' $null '0.02' 1600 800
$keepZ = Op 'Multiply' 'Multiply_DoubleDouble' (Real 'ShaftHeight' 1600 950) 'ShaftHeight' $null '0.5' 1800 950
$narrow = Shape-Shaft @($keepZ, 'ReturnValue') @($thinW, 'ReturnValue') @((Real 'ShaftHeight' 1800 1100), 'ShaftHeight') 1100 300
Connect $doneYet 'else' $narrow[0] 'execute'
$dim = New-Call $MESH_COMPONENT 'SetScalarParameterValueOnMaterials' $false 1750 300
Add-Pin $dim 'self' 'in' 'object' '' $MESH_COMPONENT
Add-Pin $dim 'ParameterName' 'in' 'name' '' $null 'Opacity'
Add-Pin $dim 'ParameterValue' 'in' 'real' 'float'
Connect (Comp 'Shaft' $STATIC_MESH 1550 500) 'Shaft' $dim 'self'
Connect (Op 'Subtract' 'Subtract_DoubleDouble' $null '1.0' $v 'ReturnValue' 1550 650) 'ReturnValue' $dim 'ParameterValue'
Connect $narrow[1] 'then' $dim 'execute'
$gone = New-Branch 2050 300
Connect (Op 'GreaterEqual' 'GreaterEqual_DoubleDouble' $v 'ReturnValue' $null '1.0' 1900 500 'bool') 'ReturnValue' $gone 'Condition'
Connect $dim 'then' $gone 'execute'
$markDone = SetSelf 'Done' 'bool' 'true' 2300 300
$rest = SetSelf 'Arriving' 'bool' 'false' 2550 300
$hideShaft = Hide-Shaft 'true' 2800 300
$free = InputCall 'EnableInput' 3100 300
$unfreeze = Controller-Input 'EnableInput' 3400 300
Connect $gone 'then' $markDone 'execute'
Chain @($markDone, $rest, $hideShaft, $free, $unfreeze)
Write-Graph 'BP_LightArrival_EventGraph.txt'
