param([string]$OutDir)
# BP_Sun Event Graph (components and variables from import_sun_model.py and setup_sun_charge.py). Only SunMesh moves
# and turns; the actor and its Area stay put.
#   Begin Play  the face slot gets its own dynamic material (FaceMaterial); SunMesh's spot is remembered (HomeLocation).
#   Tick 1      SunMesh turns its face (+X) toward the player's camera, so the flames in the face's plane ring its edge.
#   Tick 2      the charge, by Phase (PhaseTime counts the seconds in each):
#                 0 waiting   the player enters the Area -> 1
#                 1 aim       Target follows the player; after AimSeconds it is locked in -> 2      face (＃°Д°)
#                 2 charge    SunMesh speeds from where it was to Target over ChargeSeconds -> 3   face (╯‵□′)╯
#                 3 stay      StaySeconds where it stopped -> 4                                      face (´Д｀)
#                 4 rise      eases back to HomeLocation over ReturnSeconds; player still inside -> 1, else 0 (´。＿。｀)
#               No cooldown. Leaving the Area does not cut a run short: it finishes, then waits.
#   Tick 3      during 2 and 3, once per charge, a player within HitRadius is launched along the charge
#               (KnockbackStrength) and up (KnockbackUp).
#   Tick 4      while waiting, every AutoSwitchSeconds FaceIndex moves on by 1-4 (wrapping at 5): a different face.
#   Tick 5      FaceIndex goes to the material.
$helperFile = (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_height_bgm.ps1')
$helpers = Get-Content -LiteralPath $helperFile -Encoding UTF8 | Select-Object -Skip 3 -First 124
. ([ScriptBlock]::Create(($helpers -join "`n")))
$script:counter = 100
$CAMERA_MANAGER = "/Script/CoreUObject.Class'/Script/Engine.PlayerCameraManager'"
$ROTATOR = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Rotator'"
$HIT = "/Script/CoreUObject.ScriptStruct'/Script/Engine.HitResult'"
$PRIMITIVE = "/Script/CoreUObject.Class'/Script/Engine.PrimitiveComponent'"
$SCENE = "/Script/CoreUObject.Class'/Script/Engine.SceneComponent'"
$MESH_COMPONENT = "/Script/CoreUObject.Class'/Script/Engine.StaticMeshComponent'"
$BOX = "/Script/CoreUObject.Class'/Script/Engine.BoxComponent'"
$CHARACTER = "/Script/CoreUObject.Class'/Script/Engine.Character'"
$MATERIAL = "/Script/CoreUObject.Class'/Script/Engine.MaterialInterface'"
$DYNAMIC = "/Script/CoreUObject.Class'/Script/Engine.MaterialInstanceDynamic'"
$FACES = 5
$FACE = @{ Aim = '3'; Charge = '2'; Stay = '1'; Rise = '4' }

# ----- small builders ---------------------------------------------------------------------------------
function RealGet($name, $x, $y) { New-VarGet $name $null 'real' 'double' $null $x $y }
function IntGet($name, $x, $y) { New-VarGet $name $null 'int' '' $null $x $y }
function VecGet($name, $x, $y) { New-VarGet $name $null 'struct' '' $VECTOR $x $y }
function RealSet($name, $x, $y, $value = $null) {
  $n = New-VarSet $name $null 'real' $null $x $y
  (Get-Pin $n $name).Sub = 'double'; (Get-Pin $n 'Output_Get').Sub = 'double'
  if ($null -ne $value) { (Get-Pin $n $name).Default = $value }
  return $n
}
function IntSet($name, $x, $y, $value = $null) {
  $n = New-VarSet $name $null 'int' $null $x $y
  if ($null -ne $value) { (Get-Pin $n $name).Default = $value }
  return $n
}
function BoolSet($name, $value, $x, $y) {
  $n = New-VarSet $name $null 'bool' $null $x $y
  (Get-Pin $n $name).Default = $value
  return $n
}
function VecSet($name, $x, $y) { New-VarSet $name $null 'struct' $VECTOR $x $y }
function Math($operation, $x, $y) {
  $n = New-Operator $operation "${operation}_DoubleDouble" 'real' 'double' 'real' $x $y
  (Get-Pin $n 'ReturnValue').Sub = 'double'
  return $n
}
function CompareOp($operation, $cat, $x, $y) {
  $suffix = if ($cat -eq 'int') { 'IntInt' } else { 'DoubleDouble' }
  $sub = if ($cat -eq 'int') { '' } else { 'double' }
  New-Operator $operation "${operation}_$suffix" $cat $sub 'bool' $x $y
}
# Phase == value, as a bool node.
function PhaseIs($value, $x, $y) {
  $n = CompareOp 'EqualEqual' 'int' $x $y
  Connect (IntGet 'Phase' ($x - 200) $y) 'Phase' $n 'A'
  (Get-Pin $n 'B').Default = $value
  return $n
}
# PhaseTime >= the named setting.
function PhaseOver($setting, $x, $y) {
  $n = CompareOp 'GreaterEqual' 'real' $x $y
  Connect (RealGet 'PhaseTime' ($x - 200) $y) 'PhaseTime' $n 'A'
  Connect (RealGet $setting ($x - 200) ($y + 80)) $setting $n 'B'
  return $n
}
function Sun($x, $y) { New-VarGet 'SunMesh' $null 'object' '' $MESH_COMPONENT $x $y }
function SunAt($x, $y) {
  $n = New-Call $SCENE 'K2_GetComponentLocation' $true $x $y
  Add-Pin $n 'self' 'in' 'object' '' $SCENE
  Add-Pin $n 'ReturnValue' 'out' 'struct' '' $VECTOR
  Connect (Sun ($x - 200) $y) 'SunMesh' $n 'self'
  return $n
}
function Player($x, $y) {
  $n = New-Call $STATICS 'GetPlayerCharacter' $true $x $y
  Add-Pin $n 'PlayerIndex' 'in' 'int' '' $null '0'
  Add-Pin $n 'ReturnValue' 'out' 'object' '' $CHARACTER
  return $n
}
function PlayerAt($x, $y) {
  $n = New-Call $ACTOR 'K2_GetActorLocation' $true $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR
  Add-Pin $n 'ReturnValue' 'out' 'struct' '' $VECTOR
  Connect (Player ($x - 250) $y) 'ReturnValue' $n 'self'
  return $n
}
function Inside($x, $y) {
  $n = New-Call $PRIMITIVE 'IsOverlappingActor' $true $x $y
  Add-Pin $n 'self' 'in' 'object' '' $PRIMITIVE
  Add-Pin $n 'Other' 'in' 'object' '' $ACTOR
  Add-Pin $n 'ReturnValue' 'out' 'bool'
  Connect (New-VarGet 'Area' $null 'object' '' $BOX ($x - 200) $y) 'Area' $n 'self'
  Connect (Player ($x - 250) ($y + 100)) 'ReturnValue' $n 'Other'
  return $n
}
function MoveSun($x, $y) {
  $n = New-Call $SCENE 'K2_SetWorldLocation' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $SCENE
  Add-Pin $n 'NewLocation' 'in' 'struct' '' $VECTOR
  Add-Pin $n 'bSweep' 'in' 'bool' '' $null 'false'
  Add-Pin $n 'SweepHitResult' 'out' 'struct' '' $HIT
  Add-Pin $n 'bTeleport' 'in' 'bool' '' $null 'false'
  Connect (Sun ($x - 200) ($y + 200)) 'SunMesh' $n 'self'
  return $n
}
# PhaseTime / setting, held to 0..1.
function Progress($setting, $x, $y) {
  $ratio = Math 'Divide' $x $y
  Connect (RealGet 'PhaseTime' ($x - 200) $y) 'PhaseTime' $ratio 'A'
  Connect (RealGet $setting ($x - 200) ($y + 80)) $setting $ratio 'B'
  $clamp = New-Call $MATH 'FClamp' $true ($x + 200) $y
  Add-Pin $clamp 'Value' 'in' 'real' 'double'
  Add-Pin $clamp 'Min' 'in' 'real' 'double' $null '0.0'
  Add-Pin $clamp 'Max' 'in' 'real' 'double' $null '1.0'
  Add-Pin $clamp 'ReturnValue' 'out' 'real' 'double'
  Connect $ratio 'ReturnValue' $clamp 'Value'
  return $clamp
}
function Lerp($x, $y) {
  $n = New-Call $MATH 'VLerp' $true $x $y
  Add-Pin $n 'A' 'in' 'struct' '' $VECTOR
  Add-Pin $n 'B' 'in' 'struct' '' $VECTOR
  Add-Pin $n 'Alpha' 'in' 'real' 'float'
  Add-Pin $n 'ReturnValue' 'out' 'struct' '' $VECTOR
  return $n
}
# Execs a chain: each node's 'then' into the next one's 'execute'.
function Chain([object[]]$nodes) { for ($i = 0; $i -lt $nodes.Count - 1; $i++) { Connect $nodes[$i] 'then' $nodes[$i + 1] 'execute' } }
# Phase := value, PhaseTime := 0, FaceIndex := face; returns the three nodes (first, last).
function Enter($phase, $face, $x, $y) {
  $a = IntSet 'Phase' $x $y $phase
  $b = RealSet 'PhaseTime' ($x + 250) $y '0.0'
  $c = IntSet 'FaceIndex' ($x + 500) $y $face
  Chain @($a, $b, $c)
  return @($a, $c)
}

# ===== Begin Play =========================================================================================
$begin = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$ACTOR`",MemberName=`"ReceiveBeginPlay`")", 'bOverrideFunction=True') 0 -600
Add-Pin $begin 'then' 'out' 'exec'
$makeMaterial = New-Call $PRIMITIVE 'CreateDynamicMaterialInstance' $false 300 -600
Add-Pin $makeMaterial 'self' 'in' 'object' '' $PRIMITIVE
Add-Pin $makeMaterial 'ElementIndex' 'in' 'int' '' $null '1'
Add-Pin $makeMaterial 'SourceMaterial' 'in' 'object' '' $MATERIAL
Add-Pin $makeMaterial 'OptionalName' 'in' 'name' '' $null 'None'
Add-Pin $makeMaterial 'ReturnValue' 'out' 'object' '' $DYNAMIC
Connect (Sun 100 -450) 'SunMesh' $makeMaterial 'self'
$keepMaterial = New-VarSet 'FaceMaterial' $null 'object' $DYNAMIC 700 -600
Connect $makeMaterial 'ReturnValue' $keepMaterial 'FaceMaterial'
$keepHome = VecSet 'HomeLocation' 1000 -600
Connect (SunAt 800 -400) 'ReturnValue' $keepHome 'HomeLocation'
Chain @($begin, $makeMaterial, $keepMaterial, $keepHome)

# ===== Tick ===============================================================================================
$tick = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$ACTOR`",MemberName=`"ReceiveTick`")", 'bOverrideFunction=True') 0 0
Add-Pin $tick 'then' 'out' 'exec'
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$steps = New-Node '/Script/BlueprintGraph.K2Node_ExecutionSequence' @() 250 0
Add-Pin $steps 'execute' 'in' 'exec'
foreach ($i in 0..4) { Add-Pin $steps "then_$i" 'out' 'exec' }
Connect $tick 'then' $steps 'execute'

# --- 1. Face the camera ---------------------------------------------------------------------------------------
$cameraManager = New-Call $STATICS 'GetPlayerCameraManager' $true 400 300
Add-Pin $cameraManager 'PlayerIndex' 'in' 'int' '' $null '0'
Add-Pin $cameraManager 'ReturnValue' 'out' 'object' '' $CAMERA_MANAGER
$cameraAt = New-Call $CAMERA_MANAGER 'GetCameraLocation' $true 700 300
Add-Pin $cameraAt 'self' 'in' 'object' '' $CAMERA_MANAGER
Add-Pin $cameraAt 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $cameraManager 'ReturnValue' $cameraAt 'self'
$look = New-Call $MATH 'FindLookAtRotation' $true 1000 200
Add-Pin $look 'Start' 'in' 'struct' '' $VECTOR
Add-Pin $look 'Target' 'in' 'struct' '' $VECTOR
Add-Pin $look 'ReturnValue' 'out' 'struct' '' $ROTATOR
Connect (SunAt 700 150) 'ReturnValue' $look 'Start'
Connect $cameraAt 'ReturnValue' $look 'Target'
$turn = New-Call $SCENE 'K2_SetWorldRotation' $false 1300 0
Add-Pin $turn 'self' 'in' 'object' '' $SCENE
Add-Pin $turn 'NewRotation' 'in' 'struct' '' $ROTATOR
Add-Pin $turn 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $turn 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $turn 'bTeleport' 'in' 'bool' '' $null 'false'
Connect (Sun 1100 350) 'SunMesh' $turn 'self'
Connect $look 'ReturnValue' $turn 'NewRotation'
Connect $steps 'then_0' $turn 'execute'

# --- 2. The charge -------------------------------------------------------------------------------------------
$y = 700
$later = Math 'Add' 400 ($y + 200)
Connect (RealGet 'PhaseTime' 200 ($y + 200)) 'PhaseTime' $later 'A'
Connect $tick 'DeltaSeconds' $later 'B'
$count = RealSet 'PhaseTime' 600 $y
Connect $later 'ReturnValue' $count 'PhaseTime'
Connect $steps 'then_1' $count 'execute'

# 0 waiting: the player came in -> aim.
$is0 = New-Branch 900 $y
Connect (PhaseIs '0' 750 ($y + 200)) 'ReturnValue' $is0 'Condition'
Connect $count 'then' $is0 'execute'
$came = New-Branch 1150 $y
Connect (Inside 1000 ($y + 350)) 'ReturnValue' $came 'Condition'
Connect $is0 'then' $came 'execute'
$aimNow = Enter '1' $FACE.Aim 1400 $y
Connect $came 'then' $aimNow[0] 'execute'

# 1 aim: follow the player; when the time is up, start the charge from where the sun is.
$y = 1300
$is1 = New-Branch 1150 $y
Connect (PhaseIs '1' 1000 ($y + 200)) 'ReturnValue' $is1 'Condition'
Connect $is0 'else' $is1 'execute'
$follow = VecSet 'Target' 1400 $y
Connect (PlayerAt 1250 ($y + 250)) 'ReturnValue' $follow 'Target'
Connect $is1 'then' $follow 'execute'
$aimed = New-Branch 1650 $y
Connect (PhaseOver 'AimSeconds' 1550 ($y + 200)) 'ReturnValue' $aimed 'Condition'
Connect $follow 'then' $aimed 'execute'
$from = VecSet 'ChargeFrom' 1900 $y
Connect (SunAt 1750 ($y + 250)) 'ReturnValue' $from 'ChargeFrom'
Connect $aimed 'then' $from 'execute'
$fresh = BoolSet 'HitDone' 'false' 2150 $y
Connect $from 'then' $fresh 'execute'
$chargeNow = Enter '2' $FACE.Charge 2400 $y
Connect $fresh 'then' $chargeNow[0] 'execute'

# 2 charge: speeding up (alpha squared) from ChargeFrom to Target.
$y = 1900
$is2 = New-Branch 1400 $y
Connect (PhaseIs '2' 1250 ($y + 200)) 'ReturnValue' $is2 'Condition'
Connect $is1 'else' $is2 'execute'
$chargeAlpha = Progress 'ChargeSeconds' 1300 ($y + 450)
$speedUp = Math 'Multiply' 1750 ($y + 450)
Connect $chargeAlpha 'ReturnValue' $speedUp 'A'
Connect $chargeAlpha 'ReturnValue' $speedUp 'B'
$chargePath = Lerp 1950 ($y + 300)
Connect (VecGet 'ChargeFrom' 1750 ($y + 300)) 'ChargeFrom' $chargePath 'A'
Connect (VecGet 'Target' 1750 ($y + 370)) 'Target' $chargePath 'B'
Connect $speedUp 'ReturnValue' $chargePath 'Alpha'
$charge = MoveSun 2200 $y
Connect $chargePath 'ReturnValue' $charge 'NewLocation'
Connect $is2 'then' $charge 'execute'
$arrived = New-Branch 2550 $y
Connect (PhaseOver 'ChargeSeconds' 2400 ($y + 200)) 'ReturnValue' $arrived 'Condition'
Connect $charge 'then' $arrived 'execute'
$stayNow = Enter '3' $FACE.Stay 2800 $y
Connect $arrived 'then' $stayNow[0] 'execute'

# 3 stay: then rise back from wherever it stopped.
$y = 2600
$is3 = New-Branch 1650 $y
Connect (PhaseIs '3' 1500 ($y + 200)) 'ReturnValue' $is3 'Condition'
Connect $is2 'else' $is3 'execute'
$stayed = New-Branch 1900 $y
Connect (PhaseOver 'StaySeconds' 1750 ($y + 200)) 'ReturnValue' $stayed 'Condition'
Connect $is3 'then' $stayed 'execute'
$riseFrom = VecSet 'ChargeFrom' 2150 $y
Connect (SunAt 2000 ($y + 250)) 'ReturnValue' $riseFrom 'ChargeFrom'
Connect $stayed 'then' $riseFrom 'execute'
$riseNow = Enter '4' $FACE.Rise 2400 $y
Connect $riseFrom 'then' $riseNow[0] 'execute'

# 4 rise: ease in and out back home; then again if the player is still inside, else wait.
$y = 3200
$is4 = New-Branch 1900 $y
Connect (PhaseIs '4' 1750 ($y + 200)) 'ReturnValue' $is4 'Condition'
Connect $is3 'else' $is4 'execute'
$riseAlpha = Progress 'ReturnSeconds' 1800 ($y + 450)
$ease = New-Call $MATH 'FInterpEaseInOut' $true 2250 ($y + 450)
Add-Pin $ease 'A' 'in' 'real' 'double' $null '0.0'
Add-Pin $ease 'B' 'in' 'real' 'double' $null '1.0'
Add-Pin $ease 'Alpha' 'in' 'real' 'double'
Add-Pin $ease 'Exponent' 'in' 'real' 'double' $null '2.0'
Add-Pin $ease 'ReturnValue' 'out' 'real' 'double'
Connect $riseAlpha 'ReturnValue' $ease 'Alpha'
$risePath = Lerp 2500 ($y + 300)
Connect (VecGet 'ChargeFrom' 2300 ($y + 300)) 'ChargeFrom' $risePath 'A'
Connect (VecGet 'HomeLocation' 2300 ($y + 370)) 'HomeLocation' $risePath 'B'
Connect $ease 'ReturnValue' $risePath 'Alpha'
$rise = MoveSun 2750 $y
Connect $risePath 'ReturnValue' $rise 'NewLocation'
Connect $is4 'then' $rise 'execute'
$backHome = New-Branch 3100 $y
Connect (PhaseOver 'ReturnSeconds' 2950 ($y + 200)) 'ReturnValue' $backHome 'Condition'
Connect $rise 'then' $backHome 'execute'
$still = New-Branch 3350 $y
Connect (Inside 3200 ($y + 350)) 'ReturnValue' $still 'Condition'
Connect $backHome 'then' $still 'execute'
$again = Enter '1' $FACE.Aim 3600 $y
Connect $still 'then' $again[0] 'execute'
$rest = IntSet 'Phase' 3600 ($y + 200) '0'
Connect $still 'else' $rest 'execute'
$restClock = RealSet 'FaceTime' 3850 ($y + 200) '0.0'
Connect $rest 'then' $restClock 'execute'

# --- 3. Hitting the player -----------------------------------------------------------------------------------
$y = 4000
$fromCharge = New-Branch 600 $y
$atLeast2 = CompareOp 'GreaterEqual' 'int' 450 ($y + 200)
Connect (IntGet 'Phase' 250 ($y + 200)) 'Phase' $atLeast2 'A'
(Get-Pin $atLeast2 'B').Default = '2'
Connect $atLeast2 'ReturnValue' $fromCharge 'Condition'
Connect $steps 'then_2' $fromCharge 'execute'
$toStay = New-Branch 850 $y
$atMost3 = CompareOp 'LessEqual' 'int' 700 ($y + 200)
Connect (IntGet 'Phase' 500 ($y + 300)) 'Phase' $atMost3 'A'
(Get-Pin $atMost3 'B').Default = '3'
Connect $atMost3 'ReturnValue' $toStay 'Condition'
Connect $fromCharge 'then' $toStay 'execute'
$already = New-Branch 1100 $y
Connect (New-VarGet 'HitDone' $null 'bool' '' $null 950 ($y + 200)) 'HitDone' $already 'Condition'
Connect $toStay 'then' $already 'execute'
$distance = New-Call $MATH 'Vector_Distance' $true 1250 ($y + 250)
Add-Pin $distance 'V1' 'in' 'struct' '' $VECTOR
Add-Pin $distance 'V2' 'in' 'struct' '' $VECTOR
Add-Pin $distance 'ReturnValue' 'out' 'real' 'double'
Connect (SunAt 1050 ($y + 300)) 'ReturnValue' $distance 'V1'
Connect (PlayerAt 1050 ($y + 400)) 'ReturnValue' $distance 'V2'
$close = CompareOp 'Less' 'real' 1500 ($y + 250)
Connect $distance 'ReturnValue' $close 'A'
Connect (RealGet 'HitRadius' 1300 ($y + 450)) 'HitRadius' $close 'B'
$hit = New-Branch 1700 $y
Connect $close 'ReturnValue' $hit 'Condition'
Connect $already 'else' $hit 'execute'
# Along the charge, level: (Target - ChargeFrom) seen from above, made unit length, times KnockbackStrength; plus up.
$way = New-Call $MATH 'GetDirectionUnitVector' $true 1500 ($y + 600)
Add-Pin $way 'From' 'in' 'struct' '' $VECTOR
Add-Pin $way 'To' 'in' 'struct' '' $VECTOR
Add-Pin $way 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect (VecGet 'ChargeFrom' 1300 ($y + 600)) 'ChargeFrom' $way 'From'
Connect (VecGet 'Target' 1300 ($y + 680)) 'Target' $way 'To'
$wayParts = New-Call $MATH 'BreakVector' $true 1750 ($y + 600)
Add-Pin $wayParts 'InVec' 'in' 'struct' '' $VECTOR
Add-Pin $wayParts 'X' 'out' 'real' 'double'
Add-Pin $wayParts 'Y' 'out' 'real' 'double'
Add-Pin $wayParts 'Z' 'out' 'real' 'double'
Connect $way 'ReturnValue' $wayParts 'InVec'
$flat = New-Call $MATH 'MakeVector' $true 1950 ($y + 600)
Add-Pin $flat 'X' 'in' 'real' 'double'
Add-Pin $flat 'Y' 'in' 'real' 'double'
Add-Pin $flat 'Z' 'in' 'real' 'double' $null '0.0'
Add-Pin $flat 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $wayParts 'X' $flat 'X'
Connect $wayParts 'Y' $flat 'Y'
$unit = New-Call $MATH 'Normal' $true 2150 ($y + 600)
Add-Pin $unit 'A' 'in' 'struct' '' $VECTOR
Add-Pin $unit 'Tolerance' 'in' 'real' 'float' $null '0.000100'
Add-Pin $unit 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $flat 'ReturnValue' $unit 'A'
$unitParts = New-Call $MATH 'BreakVector' $true 2350 ($y + 600)
Add-Pin $unitParts 'InVec' 'in' 'struct' '' $VECTOR
Add-Pin $unitParts 'X' 'out' 'real' 'double'
Add-Pin $unitParts 'Y' 'out' 'real' 'double'
Add-Pin $unitParts 'Z' 'out' 'real' 'double'
Connect $unit 'ReturnValue' $unitParts 'InVec'
$pushX = Math 'Multiply' 2550 ($y + 550)
$pushY = Math 'Multiply' 2550 ($y + 700)
Connect $unitParts 'X' $pushX 'A'
Connect $unitParts 'Y' $pushY 'A'
Connect (RealGet 'KnockbackStrength' 2350 ($y + 800)) 'KnockbackStrength' $pushX 'B'
Connect (RealGet 'KnockbackStrength' 2350 ($y + 880)) 'KnockbackStrength' $pushY 'B'
$push = New-Call $MATH 'MakeVector' $true 2750 ($y + 600)
Add-Pin $push 'X' 'in' 'real' 'double'
Add-Pin $push 'Y' 'in' 'real' 'double'
Add-Pin $push 'Z' 'in' 'real' 'double'
Add-Pin $push 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $pushX 'ReturnValue' $push 'X'
Connect $pushY 'ReturnValue' $push 'Y'
Connect (RealGet 'KnockbackUp' 2550 ($y + 850)) 'KnockbackUp' $push 'Z'
$launch = New-Call $CHARACTER 'LaunchCharacter' $false 2000 $y
Add-Pin $launch 'self' 'in' 'object' '' $CHARACTER
Add-Pin $launch 'LaunchVelocity' 'in' 'struct' '' $VECTOR
Add-Pin $launch 'bXYOverride' 'in' 'bool' '' $null 'true'
Add-Pin $launch 'bZOverride' 'in' 'bool' '' $null 'true'
Connect (Player 1800 ($y + 150)) 'ReturnValue' $launch 'self'
Connect $push 'ReturnValue' $launch 'LaunchVelocity'
Connect $hit 'then' $launch 'execute'
$once = BoolSet 'HitDone' 'true' 2300 $y
Connect $launch 'then' $once 'execute'

# --- 4. Switch faces on a timer while waiting --------------------------------------------------------------------
$y = 5200
$waiting = New-Branch 600 $y
Connect (PhaseIs '0' 450 ($y + 200)) 'ReturnValue' $waiting 'Condition'
Connect $steps 'then_3' $waiting 'execute'
$autoOn = CompareOp 'Greater' 'real' 750 ($y + 200)
(Get-Pin $autoOn 'B').Default = '0.0'
Connect (RealGet 'AutoSwitchSeconds' 600 ($y + 300)) 'AutoSwitchSeconds' $autoOn 'A'
$isAuto = New-Branch 900 $y
Connect $waiting 'then' $isAuto 'execute'
Connect $autoOn 'ReturnValue' $isAuto 'Condition'
$faceLater = Math 'Add' 1000 ($y + 200)
Connect (RealGet 'FaceTime' 800 ($y + 400)) 'FaceTime' $faceLater 'A'
Connect $tick 'DeltaSeconds' $faceLater 'B'
$faceCount = RealSet 'FaceTime' 1200 $y
Connect $isAuto 'then' $faceCount 'execute'
Connect $faceLater 'ReturnValue' $faceCount 'FaceTime'
$due = CompareOp 'GreaterEqual' 'real' 1450 ($y + 200)
Connect $faceCount 'Output_Get' $due 'A'
Connect (RealGet 'AutoSwitchSeconds' 1250 ($y + 300)) 'AutoSwitchSeconds' $due 'B'
$isDue = New-Branch 1650 $y
Connect $faceCount 'then' $isDue 'execute'
Connect $due 'ReturnValue' $isDue 'Condition'
$restart = RealSet 'FaceTime' 1900 $y '0.0'
Connect $isDue 'then' $restart 'execute'
# Step on by 1 to FACES-1, so it never lands on the same face, then wrap back into 0..FACES-1.
$step = New-Call $MATH 'RandomIntegerInRange' $true 2000 ($y + 300)
Add-Pin $step 'Min' 'in' 'int' '' $null '1'
Add-Pin $step 'Max' 'in' 'int' '' $null ([string]($FACES - 1))
Add-Pin $step 'ReturnValue' 'out' 'int'
$sum = New-Operator 'Add' 'Add_IntInt' 'int' '' 'int' 2250 ($y + 200)
Connect (IntGet 'FaceIndex' 2050 ($y + 200)) 'FaceIndex' $sum 'A'
Connect $step 'ReturnValue' $sum 'B'
$moved = IntSet 'FaceIndex' 2450 $y
Connect $restart 'then' $moved 'execute'
Connect $sum 'ReturnValue' $moved 'FaceIndex'
$over = CompareOp 'GreaterEqual' 'int' 2700 ($y + 350)
(Get-Pin $over 'B').Default = [string]$FACES
Connect $moved 'Output_Get' $over 'A'
$back = New-Operator 'Subtract' 'Subtract_IntInt' 'int' '' 'int' 2700 ($y + 200)
(Get-Pin $back 'B').Default = [string]$FACES
Connect $moved 'Output_Get' $back 'A'
$wrap = New-Call $MATH 'SelectInt' $true 2950 ($y + 200)
Add-Pin $wrap 'A' 'in' 'int'
Add-Pin $wrap 'B' 'in' 'int'
Add-Pin $wrap 'bPickA' 'in' 'bool'
Add-Pin $wrap 'ReturnValue' 'out' 'int'
Connect $back 'ReturnValue' $wrap 'A'
Connect $moved 'Output_Get' $wrap 'B'
Connect $over 'ReturnValue' $wrap 'bPickA'
$wrapped = IntSet 'FaceIndex' 3200 $y
Connect $moved 'then' $wrapped 'execute'
Connect $wrap 'ReturnValue' $wrapped 'FaceIndex'

# --- 5. Show FaceIndex ----------------------------------------------------------------------------------------------
$y = 5800
$material = New-VarGet 'FaceMaterial' $null 'object' '' $DYNAMIC 350 ($y + 200)
$hasMaterial = New-IsValid 600 ($y + 200)
Connect $material 'FaceMaterial' $hasMaterial 'Object'
$ready = New-Branch 850 $y
Connect $steps 'then_4' $ready 'execute'
Connect $hasMaterial 'ReturnValue' $ready 'Condition'
$asNumber = New-Call $MATH 'Conv_IntToDouble' $true 900 ($y + 300)
Add-Pin $asNumber 'InInt' 'in' 'int'
Add-Pin $asNumber 'ReturnValue' 'out' 'real' 'double'
Connect (IntGet 'FaceIndex' 700 ($y + 350)) 'FaceIndex' $asNumber 'InInt'
$show = New-Call $DYNAMIC 'SetScalarParameterValue' $false 1150 $y
Add-Pin $show 'self' 'in' 'object' '' $DYNAMIC
Add-Pin $show 'ParameterName' 'in' 'name' '' $null 'FaceIndex'
Add-Pin $show 'Value' 'in' 'real' 'float'
Connect $ready 'then' $show 'execute'
Connect $material 'FaceMaterial' $show 'self'
Connect $asNumber 'ReturnValue' $show 'Value'

# ===== Write ===========================================================================================================
$sb = [System.Text.StringBuilder]::new()
foreach ($n in $script:nodes) {
  [void]$sb.AppendLine("Begin Object Class=$($n.Class) Name=`"$($n.Name)`"")
  foreach ($prop in $n.Props) { [void]$sb.AppendLine("   $prop") }
  [void]$sb.AppendLine("   NodePosX=$($n.X)")
  [void]$sb.AppendLine("   NodePosY=$($n.Y)")
  [void]$sb.AppendLine("   NodeGuid=$([guid]::NewGuid().ToString('N').ToUpper())")
  foreach ($p in $n.Pins) { [void]$sb.AppendLine((Format-Pin $p)) }
  [void]$sb.AppendLine('End Object')
}
$text = $sb.ToString()
if ($text.Contains('@{')) { throw 'A node object leaked into a pin' }
$names = [regex]::Matches($text, '(?m)^Begin Object Class=\S+ Name="(\w+)"') | ForEach-Object { $_.Groups[1].Value }
foreach ($m in [regex]::Matches($text, 'LinkedTo=\(([^)]*)\)')) {
  foreach ($link in ($m.Groups[1].Value -split ',' | Where-Object { $_ })) {
    if ($names -notcontains ($link -split ' ')[0]) { throw "Dangling link: $link" }
  }
}
foreach ($n in $script:nodes) {
  foreach ($p in $n.Pins) {
    if ($p.Cat -eq 'exec' -and $p.Dir -eq 'out' -and $p.Links.Count -gt 1) { throw "Exec output with several links: $($n.Name).$($p.Name)" }
    if ($p.Cat -eq 'exec' -and $p.Dir -eq 'in' -and $p.Links.Count -eq 0 -and $n.Class -notmatch 'K2Node_Event') { throw "Unreached node: $($n.Name)" }
  }
}
[IO.File]::WriteAllText((Join-Path $OutDir 'BP_Sun_EventGraph.txt'), $text, [Text.UTF8Encoding]::new($false))
"Generated $($script:nodes.Count) nodes"
