param([string]$OutDir)
# BP_Sun Event Graph (components and variables from import_sun_model.py and setup_sun_charge.py). Only SunMesh moves
# and turns; the actor and its Area stay put.
#   Begin Play  the face and body slots get their own dynamic materials (FaceMaterial, BodyMaterial); SunMesh's spot is
#               remembered (HomeLocation); the Platform starts with no collision.
#   Tick 0      SunMesh turns its face (+X) toward the player's camera, so the flames in the face's plane ring its edge.
#   Tick 1      the charge, by Phase (PhaseTime counts the seconds in each, AngerPace^Anger times faster):
#                 0 waiting   the player enters the Area -> 1
#                 1 aim       Target follows the player's feet (LandDrop below the capsule centre, so the ball lands on
#                             the ground); after AimSeconds it is locked in -> 2                     face (＃°Д°)
#                 2 charge    SunMesh speeds from where it was to Target over ChargeSeconds -> 3   face (╯‵□′)╯
#                 3 stay      the Platform on top becomes solid, so the player can ride; StaySeconds -> 4  face (´Д｀)
#                             A charge that never hit the player makes it angrier (Anger + 1, up to MaxAnger).
#                 4 rise      eases back to HomeLocation over ReturnSeconds, carrying a rider; at the top the Platform
#                             goes soft and a rider within RideRadius is thrown up (RideLaunch). Player still inside
#                             -> 1, else 0 and calm again                                            face (´。＿。｀)
#               No cooldown. Leaving the Area does not cut a run short: it finishes, then waits.
#               At full anger a charge is a grab charge (GrabCharge) GrabChance of the time; it glows GrabGlowBoost
#               brighter. If it hits, instead of the knockback (setup_sun_grab.py made the parts, at their own pace):
#                 5 lift      the player is caught, laid on their back on the sun's head flailing (FlailAnim), and the
#                             sun eases home over LiftSeconds                                         face ω
#                 6 drop      the black TrapCage falls beside the sun (CageOffsetX/Y) over DropSeconds; its door opens
#                 7 door      DoorSeconds for the door
#                 8 throw     the player flies into the cage on an arc over ThrowSeconds, vanishes; the door shuts
#                                                                                                     face (╯‵□′)╯
#                 9 shut      CloseSeconds; then TrapFire burns                                      face (＃°Д°)
#                 10 burn     the cage fades away over BurnSeconds; the screen goes black over FadeSeconds
#                 11 dark     the player is back at RespawnPoint, as before; the screen clears; the sun waits, calm
#   Tick 2      the Platform follows the top of the ball (it does not turn with SunMesh).
#   Tick 3      during 2 and 3, once per charge, a player within HitRadius is launched along the charge
#               (KnockbackStrength) and up (KnockbackUp); a hit calms it (Anger 0).
#   Tick 4      while waiting, every AutoSwitchSeconds FaceIndex moves on by 1-4 (wrapping at 5): a different face.
#   Tick 5      FaceIndex goes to the material; at MaxAnger the face stays (╯‵□′)╯.
#   Tick 6      the body goes from orange to blue and glows brighter with Anger / MaxAnger.
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
$LINEAR = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.LinearColor'"
$COLLISION = "/Script/CoreUObject.Enum'/Script/Engine.ECollisionEnabled'"
$FACES = 5
$FACE = @{ Aim = '3'; Charge = '2'; Stay = '1'; Rise = '4'; Furious = '2.0' }
$PLATFORM_ABOVE = '42.0'   # Platform centre above the ball's: its top (8 cm thick half) on the 50 cm ball's top.
$CALM = '(R=1.000000,G=0.420000,B=0.100000,A=1.000000)'
$ANGRY = '(R=0.050000,G=0.250000,B=1.000000,A=1.000000)'   # blue: hotter as it gets angrier
$CALM_GLOW = '3.0'
$ANGRY_GLOW = '6.0'
# The grab (phases 5-11).
$HIT_RESULT = $HIT   # $hit (the hit branch) overwrites $HIT later: PowerShell names ignore case.
$SKELETAL = "/Script/CoreUObject.Class'/Script/Engine.SkeletalMeshComponent'"
$CAPSULE = "/Script/CoreUObject.Class'/Script/Engine.CapsuleComponent'"
$CHAR_MOVE = "/Script/CoreUObject.Class'/Script/Engine.CharacterMovementComponent'"
$MOVE_COMP = "/Script/CoreUObject.Class'/Script/Engine.MovementComponent'"
$ACTOR_COMP = "/Script/CoreUObject.Class'/Script/Engine.ActorComponent'"
$CONTROLLER = "/Script/CoreUObject.Class'/Script/Engine.PlayerController'"
$TRANSFORM = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Transform'"
$ANIM_ASSET = "/Script/CoreUObject.Class'/Script/Engine.AnimationAsset'"
$MOVE_MODE = "/Script/CoreUObject.Enum'/Script/Engine.EMovementMode'"
$ANIM_MODE = "/Script/CoreUObject.Enum'/Script/Engine.EAnimationMode'"
$STRINGS = "/Script/CoreUObject.Class'/Script/Engine.KismetStringLibrary'"
$EFFEKSEER = "/Script/CoreUObject.Class'/Script/Effekseer.EffekseerEmitterComponent'"
$GRAB_FACE = @{ Carry = '0'; Throw = '2'; Shut = '3' }
$MESH_YAW = '270.0'          # The player mesh's own yaw in BP_ThirdPersonCharacter1 (it faces the capsule's +X).
$PELVIS = '-90.0'            # Feet to pelvis, negated: lying down turns about the pelvis, not the feet.
$INTO_CAGE = '100.0'         # Thrown at this height above the cage's floor (the cage is shown at twice its size).
$BLACK = '(R=0.000000,G=0.000000,B=0.000000,A=1.000000)'

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
function Platform($x, $y) { New-VarGet 'Platform' $null 'object' '' $BOX $x $y }
function PlatformAt($x, $y) {
  $n = New-Call $SCENE 'K2_GetComponentLocation' $true $x $y
  Add-Pin $n 'self' 'in' 'object' '' $SCENE
  Add-Pin $n 'ReturnValue' 'out' 'struct' '' $VECTOR
  Connect (Platform ($x - 200) $y) 'Platform' $n 'self'
  return $n
}
# Platform collision on (QueryAndPhysics) or off (NoCollision).
function PlatformSolid($type, [double]$x, [double]$y) {
  $n = New-Call $PRIMITIVE 'SetCollisionEnabled' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $PRIMITIVE
  Add-Pin $n 'NewType' 'in' 'byte' '' $COLLISION $type
  Connect (Platform ($x - 200) ($y + 200)) 'Platform' $n 'self'
  return $n
}
function IntToReal($x, $y) {
  $n = New-Call $MATH 'Conv_IntToDouble' $true $x $y
  Add-Pin $n 'InInt' 'in' 'int'
  Add-Pin $n 'ReturnValue' 'out' 'real' 'double'
  return $n
}
function BreakVec($x, $y) {
  $n = New-Call $MATH 'BreakVector' $true $x $y
  Add-Pin $n 'InVec' 'in' 'struct' '' $VECTOR
  Add-Pin $n 'X' 'out' 'real' 'double'
  Add-Pin $n 'Y' 'out' 'real' 'double'
  Add-Pin $n 'Z' 'out' 'real' 'double'
  return $n
}
function MakeVec($x, $y) {
  $n = New-Call $MATH 'MakeVector' $true $x $y
  Add-Pin $n 'X' 'in' 'real' 'double' $null '0.0'
  Add-Pin $n 'Y' 'in' 'real' 'double' $null '0.0'
  Add-Pin $n 'Z' 'in' 'real' 'double' $null '0.0'
  Add-Pin $n 'ReturnValue' 'out' 'struct' '' $VECTOR
  return $n
}
# vector with LandDrop / PLATFORM_ABOVE etc. added to Z: returns (break, make, add) so Z's addend can be wired.
function ShiftZ($x, $y) {
  $parts = BreakVec $x $y
  $z = Math 'Add' ($x + 200) ($y + 150)
  Connect $parts 'Z' $z 'A'
  $made = MakeVec ($x + 400) $y
  Connect $parts 'X' $made 'X'
  Connect $parts 'Y' $made 'Y'
  Connect $z 'ReturnValue' $made 'Z'
  return @($parts, $made, $z)
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

# ----- the grab's builders -------------------------------------------------------------------------------
function TrapCage($x, $y) { New-VarGet 'TrapCage' $null 'object' '' $SKELETAL $x $y }
function TrapFire($x, $y) { New-VarGet 'TrapFire' $null 'object' '' $EFFEKSEER $x $y }
# A component of the player character (Mesh, CapsuleComponent, CharacterMovement).
function PlayerPart($name, $type, [double]$x, [double]$y) {
  $n = New-VarGet $name $CHARACTER 'object' '' $type $x $y
  Connect (Player ($x - 250) $y) 'ReturnValue' $n 'self'
  return $n
}
function Controller([double]$x, [double]$y) {
  $n = New-Call $STATICS 'GetPlayerController' $true $x $y
  Add-Pin $n 'PlayerIndex' 'in' 'int' '' $null '0'
  Add-Pin $n 'ReturnValue' 'out' 'object' '' $CONTROLLER
  return $n
}
function VectorOut($node) { $node }
# K2_SetActorLocation on the player, teleporting; the caller wires NewLocation.
function PutPlayer([double]$x, [double]$y) {
  $n = New-Call $ACTOR 'K2_SetActorLocation' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR
  Add-Pin $n 'NewLocation' 'in' 'struct' '' $VECTOR
  Add-Pin $n 'bSweep' 'in' 'bool' '' $null 'false'
  Add-Pin $n 'SweepHitResult' 'out' 'struct' '' $HIT_RESULT
  Add-Pin $n 'bTeleport' 'in' 'bool' '' $null 'true'
  Connect (Player ($x - 250) ($y + 250)) 'ReturnValue' $n 'self'
  return $n
}
# The player lying on the sun's head: HoldHeight above the ball's centre.
function HoldPlayer([double]$x, [double]$y) {
  $n = PutPlayer $x $y
  $spot = ShiftZ ($x - 650) ($y + 300)
  Connect (SunAt ($x - 850) ($y + 300)) 'ReturnValue' $spot[0] 'InVec'
  Connect (RealGet 'HoldHeight' ($x - 450) ($y + 500)) 'HoldHeight' $spot[2] 'B'
  Connect $spot[1] 'ReturnValue' $n 'NewLocation'
  return $n
}
function SetVisible($target, $targetPin, $visible, [double]$x, [double]$y) {
  $n = New-Call $SCENE 'SetVisibility' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $SCENE
  Add-Pin $n 'bNewVisibility' 'in' 'bool' '' $null $visible
  Add-Pin $n 'bPropagateToChildren' 'in' 'bool' '' $null 'true'
  Connect $target $targetPin $n 'self'
  return $n
}
# The cage door: 1 opens, -1 closes (its animation played forward or back). Returns (first, last).
function Door($rate, [double]$x, [double]$y) {
  $r = New-Call $SKELETAL 'SetPlayRate' $false $x $y
  Add-Pin $r 'self' 'in' 'object' '' $SKELETAL
  Add-Pin $r 'Rate' 'in' 'real' 'float' $null $rate
  $p = New-Call $SKELETAL 'Play' $false ($x + 250) $y
  Add-Pin $p 'self' 'in' 'object' '' $SKELETAL
  Add-Pin $p 'bLooping' 'in' 'bool' '' $null 'false'
  $cage = TrapCage ($x - 150) ($y + 200)
  Connect $cage 'TrapCage' $r 'self'
  Connect $cage 'TrapCage' $p 'self'
  Chain @($r, $p)
  return @($r, $p)
}
# The black materials' Fade (1 shown, 0 gone); the caller wires the value unless it is fixed.
function CageFade($value, [double]$x, [double]$y) {
  # Declared on UMeshComponent; with PrimitiveComponent as its parent the pasted node is dropped silently.
  $meshComp = "/Script/CoreUObject.Class'/Script/Engine.MeshComponent'"
  $n = New-Call $meshComp 'SetScalarParameterValueOnMaterials' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $meshComp
  Add-Pin $n 'ParameterName' 'in' 'name' '' $null 'Fade'
  Add-Pin $n 'ParameterValue' 'in' 'real' 'float' $null $value
  Connect (TrapCage ($x - 200) ($y + 200)) 'TrapCage' $n 'self'
  return $n
}
function CameraFade($from, $to, $hold, [double]$x, [double]$y) {
  $manager = New-Call $STATICS 'GetPlayerCameraManager' $true ($x - 300) ($y + 200)
  Add-Pin $manager 'PlayerIndex' 'in' 'int' '' $null '0'
  Add-Pin $manager 'ReturnValue' 'out' 'object' '' $CAMERA_MANAGER
  $n = New-Call $CAMERA_MANAGER 'StartCameraFade' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $CAMERA_MANAGER
  Add-Pin $n 'FromAlpha' 'in' 'real' 'float' $null $from
  Add-Pin $n 'ToAlpha' 'in' 'real' 'float' $null $to
  Add-Pin $n 'Duration' 'in' 'real' 'float'
  Add-Pin $n 'Color' 'in' 'struct' '' $LINEAR $BLACK
  Add-Pin $n 'bShouldFadeAudio' 'in' 'bool' '' $null 'false'
  Add-Pin $n 'bHoldWhenFinished' 'in' 'bool' '' $null $hold
  Connect $manager 'ReturnValue' $n 'self'
  Connect (RealGet 'FadeSeconds' ($x - 300) ($y + 300)) 'FadeSeconds' $n 'Duration'
  return $n
}
function EaseOf($setting, [double]$x, [double]$y) {
  $alpha = Progress $setting $x $y
  $e = New-Call $MATH 'FInterpEaseInOut' $true ($x + 450) $y
  Add-Pin $e 'A' 'in' 'real' 'double' $null '0.0'
  Add-Pin $e 'B' 'in' 'real' 'double' $null '1.0'
  Add-Pin $e 'Alpha' 'in' 'real' 'double'
  Add-Pin $e 'Exponent' 'in' 'real' 'double' $null '2.0'
  Add-Pin $e 'ReturnValue' 'out' 'real' 'double'
  Connect $alpha 'ReturnValue' $e 'Alpha'
  return $e
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
$makeBody = New-Call $PRIMITIVE 'CreateDynamicMaterialInstance' $false 1300 -600
Add-Pin $makeBody 'self' 'in' 'object' '' $PRIMITIVE
Add-Pin $makeBody 'ElementIndex' 'in' 'int' '' $null '0'
Add-Pin $makeBody 'SourceMaterial' 'in' 'object' '' $MATERIAL
Add-Pin $makeBody 'OptionalName' 'in' 'name' '' $null 'None'
Add-Pin $makeBody 'ReturnValue' 'out' 'object' '' $DYNAMIC
Connect (Sun 1100 -450) 'SunMesh' $makeBody 'self'
$keepBody = New-VarSet 'BodyMaterial' $null 'object' $DYNAMIC 1700 -600
Connect $makeBody 'ReturnValue' $keepBody 'BodyMaterial'
$soft = PlatformSolid 'NoCollision' 2000 -600
Chain @($begin, $makeMaterial, $keepMaterial, $keepHome, $makeBody, $keepBody, $soft)

# ===== Tick ===============================================================================================
$tick = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$ACTOR`",MemberName=`"ReceiveTick`")", 'bOverrideFunction=True') 0 0
Add-Pin $tick 'then' 'out' 'exec'
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$steps = New-Node '/Script/BlueprintGraph.K2Node_ExecutionSequence' @() 250 0
Add-Pin $steps 'execute' 'in' 'exec'
foreach ($i in 0..6) { Add-Pin $steps "then_$i" 'out' 'exec' }
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
# PhaseTime += DeltaSeconds * AngerPace ^ Anger: every phase runs faster the angrier it is.
$pace = New-Call $MATH 'MultiplyMultiply_FloatFloat' $true 0 ($y + 400)
Add-Pin $pace 'Base' 'in' 'real' 'double'
Add-Pin $pace 'Exp' 'in' 'real' 'double'
Add-Pin $pace 'ReturnValue' 'out' 'real' 'double'
Connect (RealGet 'AngerPace' -200 ($y + 400)) 'AngerPace' $pace 'Base'
$angerReal = IntToReal -200 ($y + 500)
Connect (IntGet 'Anger' -400 ($y + 500)) 'Anger' $angerReal 'InInt'
Connect $angerReal 'ReturnValue' $pace 'Exp'
$step = Math 'Multiply' 200 ($y + 350)
Connect $tick 'DeltaSeconds' $step 'A'
# The grab (phases 5 and up) keeps its own time, however angry the sun is.
$grabbing = CompareOp 'GreaterEqual' 'int' -200 ($y + 650)
Connect (IntGet 'Phase' -400 ($y + 650)) 'Phase' $grabbing 'A'
(Get-Pin $grabbing 'B').Default = '5'
$paceNow = New-Call $MATH 'SelectFloat' $true 0 ($y + 600)
Add-Pin $paceNow 'A' 'in' 'real' 'double' $null '1.0'
Add-Pin $paceNow 'B' 'in' 'real' 'double'
Add-Pin $paceNow 'bPickA' 'in' 'bool'
Add-Pin $paceNow 'ReturnValue' 'out' 'real' 'double'
Connect $pace 'ReturnValue' $paceNow 'B'
Connect $grabbing 'ReturnValue' $paceNow 'bPickA'
Connect $paceNow 'ReturnValue' $step 'B'
$later = Math 'Add' 400 ($y + 200)
Connect (RealGet 'PhaseTime' 200 ($y + 200)) 'PhaseTime' $later 'A'
Connect $step 'ReturnValue' $later 'B'
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
$feet = ShiftZ 850 ($y + 250)
Connect (PlayerAt 650 ($y + 250)) 'ReturnValue' $feet[0] 'InVec'
$drop = Math 'Multiply' 850 ($y + 500)
Connect (RealGet 'LandDrop' 650 ($y + 500)) 'LandDrop' $drop 'A'
(Get-Pin $drop 'B').Default = '-1.0'
Connect $drop 'ReturnValue' $feet[2] 'B'
Connect $feet[1] 'ReturnValue' $follow 'Target'
Connect $is1 'then' $follow 'execute'
$aimed = New-Branch 1650 $y
Connect (PhaseOver 'AimSeconds' 1550 ($y + 200)) 'ReturnValue' $aimed 'Condition'
Connect $follow 'then' $aimed 'execute'
$from = VecSet 'ChargeFrom' 1900 $y
Connect (SunAt 1750 ($y + 250)) 'ReturnValue' $from 'ChargeFrom'
Connect $aimed 'then' $from 'execute'
$fresh = BoolSet 'HitDone' 'false' 2150 $y
Connect $from 'then' $fresh 'execute'
$chargeNow = Enter '2' $FACE.Charge 2900 $y
# At full anger, GrabChance of the charges grab instead of knocking back (GrabCharge; the body flashes as a warning).
$furyCharge = New-Branch 2400 $y
$furyFull = CompareOp 'GreaterEqual' 'int' 2250 ($y + 200)
Connect (IntGet 'Anger' 2050 ($y + 200)) 'Anger' $furyFull 'A'
Connect (IntGet 'MaxAnger' 2050 ($y + 280)) 'MaxAnger' $furyFull 'B'
Connect $furyFull 'ReturnValue' $furyCharge 'Condition'
Connect $fresh 'then' $furyCharge 'execute'
$roll = New-Call $MATH 'RandomBoolWithWeight' $true 2450 ($y + 350)
Add-Pin $roll 'Weight' 'in' 'real' 'float'
Add-Pin $roll 'ReturnValue' 'out' 'bool'
Connect (RealGet 'GrabChance' 2250 ($y + 400)) 'GrabChance' $roll 'Weight'
$decide = New-VarSet 'GrabCharge' $null 'bool' $null 2650 ($y - 100)
Connect $roll 'ReturnValue' $decide 'GrabCharge'
Connect $furyCharge 'then' $decide 'execute'
$noGrab = BoolSet 'GrabCharge' 'false' 2650 ($y + 150)
Connect $furyCharge 'else' $noGrab 'execute'
Connect $decide 'then' $chargeNow[0] 'execute'
Connect $noGrab 'then' $chargeNow[0] 'execute'

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
$solid = PlatformSolid 'QueryAndPhysics' 3550 $y
Connect $stayNow[1] 'then' $solid 'execute'

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
# Missed (no hit this charge) -> one step angrier, up to MaxAnger.
$hitThis = New-Branch 2400 $y
Connect (New-VarGet 'HitDone' $null 'bool' '' $null 2250 ($y + 200)) 'HitDone' $hitThis 'Condition'
$grabMissed = BoolSet 'GrabCharge' 'false' 2150 ($y - 200)
Connect $riseFrom 'then' $grabMissed 'execute'
Connect $grabMissed 'then' $hitThis 'execute'
$canRage = New-Branch 2650 ($y + 150)
$belowMax = CompareOp 'Less' 'int' 2500 ($y + 350)
Connect (IntGet 'Anger' 2300 ($y + 350)) 'Anger' $belowMax 'A'
Connect (IntGet 'MaxAnger' 2300 ($y + 430)) 'MaxAnger' $belowMax 'B'
Connect $belowMax 'ReturnValue' $canRage 'Condition'
Connect $hitThis 'else' $canRage 'execute'
$angrier = New-Operator 'Add' 'Add_IntInt' 'int' '' 'int' 2900 ($y + 350)
Connect (IntGet 'Anger' 2700 ($y + 450)) 'Anger' $angrier 'A'
(Get-Pin $angrier 'B').Default = '1'
$rage = IntSet 'Anger' 3100 ($y + 150)
Connect $angrier 'ReturnValue' $rage 'Anger'
Connect $canRage 'then' $rage 'execute'
$riseNow = Enter '4' $FACE.Rise 3400 $y
Connect $hitThis 'then' $riseNow[0] 'execute'
Connect $canRage 'else' $riseNow[0] 'execute'
Connect $rage 'then' $riseNow[0] 'execute'

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
# At the top: the Platform goes soft and whoever rode up is thrown into the air.
$soften = PlatformSolid 'NoCollision' 3350 $y
Connect $backHome 'then' $soften 'execute'
$rideGap = New-Call $MATH 'Vector_Distance' $true 3450 ($y + 450)
Add-Pin $rideGap 'V1' 'in' 'struct' '' $VECTOR
Add-Pin $rideGap 'V2' 'in' 'struct' '' $VECTOR
Add-Pin $rideGap 'ReturnValue' 'out' 'real' 'double'
Connect (PlatformAt 3250 ($y + 450)) 'ReturnValue' $rideGap 'V1'
Connect (PlayerAt 3250 ($y + 550)) 'ReturnValue' $rideGap 'V2'
$onTop = CompareOp 'Less' 'real' 3700 ($y + 450)
Connect $rideGap 'ReturnValue' $onTop 'A'
Connect (RealGet 'RideRadius' 3500 ($y + 650)) 'RideRadius' $onTop 'B'
$rider = New-Branch 3700 $y
Connect $onTop 'ReturnValue' $rider 'Condition'
Connect $soften 'then' $rider 'execute'
$throwUp = MakeVec 3950 ($y + 450)
Connect (RealGet 'RideLaunch' 3750 ($y + 650)) 'RideLaunch' $throwUp 'Z'
$fling = New-Call $CHARACTER 'LaunchCharacter' $false 4000 $y
Add-Pin $fling 'self' 'in' 'object' '' $CHARACTER
Add-Pin $fling 'LaunchVelocity' 'in' 'struct' '' $VECTOR
Add-Pin $fling 'bXYOverride' 'in' 'bool' '' $null 'false'
Add-Pin $fling 'bZOverride' 'in' 'bool' '' $null 'true'
Connect (Player 3800 ($y + 200)) 'ReturnValue' $fling 'self'
Connect $throwUp 'ReturnValue' $fling 'LaunchVelocity'
Connect $rider 'then' $fling 'execute'
$still = New-Branch 4350 $y
Connect (Inside 4200 ($y + 350)) 'ReturnValue' $still 'Condition'
Connect $fling 'then' $still 'execute'
Connect $rider 'else' $still 'execute'
$again = Enter '1' $FACE.Aim 4600 $y
Connect $still 'then' $again[0] 'execute'
$rest = IntSet 'Phase' 4600 ($y + 200) '0'
Connect $still 'else' $rest 'execute'
$restClock = RealSet 'FaceTime' 4850 ($y + 200) '0.0'
Connect $rest 'then' $restClock 'execute'
$calmDown = IntSet 'Anger' 5100 ($y + 200) '0'
Connect $restClock 'then' $calmDown 'execute'

# ===== The grab, phases 5-11 (entered from the hit, Tick 3) ===================================================
# 5 lift: the sun eases home over LiftSeconds with the player lying on its head.
$y = 8000
$is5 = New-Branch 2150 $y
Connect (PhaseIs '5' 2000 ($y + 200)) 'ReturnValue' $is5 'Condition'
Connect $is4 'else' $is5 'execute'
$liftPath = Lerp 2800 ($y + 300)
Connect (VecGet 'ChargeFrom' 2600 ($y + 300)) 'ChargeFrom' $liftPath 'A'
Connect (VecGet 'HomeLocation' 2600 ($y + 370)) 'HomeLocation' $liftPath 'B'
Connect (EaseOf 'LiftSeconds' 2100 ($y + 500)) 'ReturnValue' $liftPath 'Alpha'
$lift = MoveSun 3100 $y
Connect $liftPath 'ReturnValue' $lift 'NewLocation'
Connect $is5 'then' $lift 'execute'
$hold5 = HoldPlayer 4100 $y
Connect $lift 'then' $hold5 'execute'
$lifted = New-Branch 4400 $y
Connect (PhaseOver 'LiftSeconds' 4250 ($y + 200)) 'ReturnValue' $lifted 'Condition'
Connect $hold5 'then' $lifted 'execute'
$dropNow = Enter '6' $GRAB_FACE.Carry 4650 $y
Connect $lifted 'then' $dropNow[0] 'execute'
$showCage = SetVisible (TrapCage 5300 ($y + 200)) 'TrapCage' 'true' 5450 $y
Connect $dropNow[1] 'then' $showCage 'execute'

# 6 drop: the black cage falls from CageTop to CageGround (speeding up) over DropSeconds, then its door opens.
$y = 8800
$is6 = New-Branch 2400 $y
Connect (PhaseIs '6' 2250 ($y + 200)) 'ReturnValue' $is6 'Condition'
Connect $is5 'else' $is6 'execute'
$fallAlpha = Progress 'DropSeconds' 2400 ($y + 450)
$fallFaster = Math 'Multiply' 2850 ($y + 450)
Connect $fallAlpha 'ReturnValue' $fallFaster 'A'
Connect $fallAlpha 'ReturnValue' $fallFaster 'B'
$fallPath = Lerp 3050 ($y + 300)
Connect (VecGet 'CageTop' 2850 ($y + 300)) 'CageTop' $fallPath 'A'
Connect (VecGet 'CageGround' 2850 ($y + 370)) 'CageGround' $fallPath 'B'
Connect $fallFaster 'ReturnValue' $fallPath 'Alpha'
$fall = New-Call $SCENE 'K2_SetWorldLocation' $false 3300 $y
Add-Pin $fall 'self' 'in' 'object' '' $SCENE
Add-Pin $fall 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $fall 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $fall 'SweepHitResult' 'out' 'struct' '' $HIT_RESULT
Add-Pin $fall 'bTeleport' 'in' 'bool' '' $null 'true'
Connect (TrapCage 3100 ($y + 200)) 'TrapCage' $fall 'self'
Connect $fallPath 'ReturnValue' $fall 'NewLocation'
Connect $is6 'then' $fall 'execute'
$hold6 = HoldPlayer 4300 $y
Connect $fall 'then' $hold6 'execute'
$landed = New-Branch 4600 $y
Connect (PhaseOver 'DropSeconds' 4450 ($y + 200)) 'ReturnValue' $landed 'Condition'
Connect $hold6 'then' $landed 'execute'
$openNow = Enter '7' $GRAB_FACE.Carry 4850 $y
Connect $landed 'then' $openNow[0] 'execute'
$open = Door '1.0' 5650 $y
Connect $openNow[1] 'then' $open[0] 'execute'

# 7 door: wait DoorSeconds for it to open; then the throw starts from where the player lies.  face (╯‵□′)╯
$y = 9500
$is7 = New-Branch 2650 $y
Connect (PhaseIs '7' 2500 ($y + 200)) 'ReturnValue' $is7 'Condition'
Connect $is6 'else' $is7 'execute'
$hold7 = HoldPlayer 3700 $y
Connect $is7 'then' $hold7 'execute'
$opened = New-Branch 4000 $y
Connect (PhaseOver 'DoorSeconds' 3850 ($y + 200)) 'ReturnValue' $opened 'Condition'
Connect $hold7 'then' $opened 'execute'
$throwFrom = VecSet 'ThrowFrom' 4250 $y
Connect (PlayerAt 4100 ($y + 250)) 'ReturnValue' $throwFrom 'ThrowFrom'
Connect $opened 'then' $throwFrom 'execute'
$throwNow = Enter '8' $GRAB_FACE.Throw 4500 $y
Connect $throwFrom 'then' $throwNow[0] 'execute'

# 8 throw: an arc (ThrowArc high at its middle) from ThrowFrom into the cage over ThrowSeconds; inside, the player is
# hidden and the door shuts.  face (＃°Д°)
$y = 10200
$is8 = New-Branch 2900 $y
Connect (PhaseIs '8' 2750 ($y + 200)) 'ReturnValue' $is8 'Condition'
Connect $is7 'else' $is8 'execute'
$throwAlpha = Progress 'ThrowSeconds' 2700 ($y + 500)
$intoCage = ShiftZ 2900 ($y + 300)
Connect (VecGet 'CageGround' 2700 ($y + 300)) 'CageGround' $intoCage[0] 'InVec'
(Get-Pin $intoCage[2] 'B').Default = $INTO_CAGE
$throwLine = Lerp 3400 ($y + 300)
Connect (VecGet 'ThrowFrom' 3200 ($y + 250)) 'ThrowFrom' $throwLine 'A'
Connect $intoCage[1] 'ReturnValue' $throwLine 'B'
Connect $throwAlpha 'ReturnValue' $throwLine 'Alpha'
$rest01 = Math 'Subtract' 3150 ($y + 600)
(Get-Pin $rest01 'A').Default = '1.0'
Connect $throwAlpha 'ReturnValue' $rest01 'B'
$bell = Math 'Multiply' 3350 ($y + 600)
Connect $throwAlpha 'ReturnValue' $bell 'A'
Connect $rest01 'ReturnValue' $bell 'B'
$bellHigh = Math 'Multiply' 3550 ($y + 600)
Connect $bell 'ReturnValue' $bellHigh 'A'
Connect (RealGet 'ThrowArc' 3350 ($y + 700)) 'ThrowArc' $bellHigh 'B'
$arcHeight = Math 'Multiply' 3750 ($y + 600)
Connect $bellHigh 'ReturnValue' $arcHeight 'A'
(Get-Pin $arcHeight 'B').Default = '4.0'
$arc = ShiftZ 3650 ($y + 300)
Connect $throwLine 'ReturnValue' $arc[0] 'InVec'
Connect $arcHeight 'ReturnValue' $arc[2] 'B'
$fly = PutPlayer 4250 $y
Connect $arc[1] 'ReturnValue' $fly 'NewLocation'
Connect $is8 'then' $fly 'execute'
$inside = New-Branch 4550 $y
Connect (PhaseOver 'ThrowSeconds' 4400 ($y + 200)) 'ReturnValue' $inside 'Condition'
Connect $fly 'then' $inside 'execute'
$vanish = SetVisible (PlayerPart 'CapsuleComponent' $CAPSULE 4650 ($y + 250)) 'CapsuleComponent' 'false' 4800 $y
Connect $inside 'then' $vanish 'execute'
$shut = Door '-1.0' 5150 $y
Connect $vanish 'then' $shut[0] 'execute'
$shutNow = Enter '9' $GRAB_FACE.Shut 5650 $y
Connect $shut[1] 'then' $shutNow[0] 'execute'

# 9 shut: wait CloseSeconds for the door; then the cage catches fire.
$y = 10900
$is9 = New-Branch 3150 $y
Connect (PhaseIs '9' 3000 ($y + 200)) 'ReturnValue' $is9 'Condition'
Connect $is8 'else' $is9 'execute'
$closed = New-Branch 3400 $y
Connect (PhaseOver 'CloseSeconds' 3250 ($y + 200)) 'ReturnValue' $closed 'Condition'
Connect $is9 'then' $closed 'execute'
$ignite = New-Call $ACTOR_COMP 'Activate' $false 3650 $y
Add-Pin $ignite 'self' 'in' 'object' '' $ACTOR_COMP
Add-Pin $ignite 'bReset' 'in' 'bool' '' $null 'true'
Connect (TrapFire 3450 ($y + 200)) 'TrapFire' $ignite 'self'
Connect $closed 'then' $ignite 'execute'
$burnNow = Enter '10' $GRAB_FACE.Shut 3950 $y
Connect $ignite 'then' $burnNow[0] 'execute'

# 10 burn: the cage fades away (dithered, like the birdcage warp) over BurnSeconds while it burns; then the screen
# goes black over FadeSeconds.
$y = 11500
$is10 = New-Branch 3400 $y
Connect (PhaseIs '10' 3250 ($y + 200)) 'ReturnValue' $is10 'Condition'
Connect $is9 'else' $is10 'execute'
$burnAlpha = Progress 'BurnSeconds' 3300 ($y + 400)
$left = Math 'Subtract' 3750 ($y + 400)
(Get-Pin $left 'A').Default = '1.0'
Connect $burnAlpha 'ReturnValue' $left 'B'
$fadeCage = CageFade $null 4000 $y
Connect $left 'ReturnValue' $fadeCage 'ParameterValue'
Connect $is10 'then' $fadeCage 'execute'
$burnt = New-Branch 4300 $y
Connect (PhaseOver 'BurnSeconds' 4150 ($y + 200)) 'ReturnValue' $burnt 'Condition'
Connect $fadeCage 'then' $burnt 'execute'
$blackOut = CameraFade '0.0' '1.0' 'true' 4600 $y
Connect $burnt 'then' $blackOut 'execute'
$darkNow = Enter '11' $GRAB_FACE.Shut 4900 $y
Connect $blackOut 'then' $darkNow[0] 'execute'

# 11 dark: after FadeSeconds the player is back at RespawnPoint (the level's PlayerStart), as before the grab, and the
# sun waits again, calm.
$y = 12200
$is11 = New-Branch 3650 $y
Connect (PhaseIs '11' 3500 ($y + 200)) 'ReturnValue' $is11 'Condition'
Connect $is10 'else' $is11 'execute'
$dark = New-Branch 3900 $y
Connect (PhaseOver 'FadeSeconds' 3750 ($y + 200)) 'ReturnValue' $dark 'Condition'
Connect $is11 'then' $dark 'execute'
$respawn = New-VarGet 'RespawnPoint' $null 'object' '' $ACTOR 3900 ($y + 300)
$hasRespawn = New-IsValid 4100 ($y + 300)
Connect $respawn 'RespawnPoint' $hasRespawn 'Object'
$canReturn = New-Branch 4150 $y
Connect $hasRespawn 'ReturnValue' $canReturn 'Condition'
Connect $dark 'then' $canReturn 'execute'
$respawnAt = New-Call $ACTOR 'K2_GetActorLocation' $true 4250 ($y + 450)
Add-Pin $respawnAt 'self' 'in' 'object' '' $ACTOR
Add-Pin $respawnAt 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $respawn 'RespawnPoint' $respawnAt 'self'
$toStart = PutPlayer 4500 $y
Connect $respawnAt 'ReturnValue' $toStart 'NewLocation'
Connect $canReturn 'then' $toStart 'execute'
$reappear = SetVisible (PlayerPart 'CapsuleComponent' $CAPSULE 4700 ($y + 250)) 'CapsuleComponent' 'true' 4850 $y
Connect $toStart 'then' $reappear 'execute'
# No RespawnPoint set on this sun: the game mode's player start (where the level began).
$GAME_MODE = "/Script/CoreUObject.Class'/Script/Engine.GameModeBase'"
$CONTROLLER_BASE = "/Script/CoreUObject.Class'/Script/Engine.Controller'"
$gameMode = New-Call $STATICS 'GetGameMode' $true 4150 ($y + 650)
Add-Pin $gameMode 'ReturnValue' 'out' 'object' '' $GAME_MODE
$findStart = New-Call $GAME_MODE 'K2_FindPlayerStart' $false 4400 ($y + 550)
Add-Pin $findStart 'self' 'in' 'object' '' $GAME_MODE
Add-Pin $findStart 'Player' 'in' 'object' '' $CONTROLLER_BASE
Add-Pin $findStart 'IncomingName' 'in' 'string' '' $null ''
Add-Pin $findStart 'ReturnValue' 'out' 'object' '' $ACTOR
Connect $gameMode 'ReturnValue' $findStart 'self'
Connect (Controller 4150 ($y + 750)) 'ReturnValue' $findStart 'Player'
Connect $canReturn 'else' $findStart 'execute'
$startAt = New-Call $ACTOR 'K2_GetActorLocation' $true 4700 ($y + 750)
Add-Pin $startAt 'self' 'in' 'object' '' $ACTOR
Add-Pin $startAt 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $findStart 'ReturnValue' $startAt 'self'
$toFoundStart = PutPlayer 4800 ($y + 550)
Connect $startAt 'ReturnValue' $toFoundStart 'NewLocation'
Connect $findStart 'then' $toFoundStart 'execute'
Connect $toFoundStart 'then' $reappear 'execute'
$meshBack = New-Call $SCENE 'K2_SetRelativeTransform' $false 5150 $y
Add-Pin $meshBack 'self' 'in' 'object' '' $SCENE
Add-Pin $meshBack 'NewTransform' 'in' 'struct' '' $TRANSFORM
Add-Pin $meshBack 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $meshBack 'SweepHitResult' 'out' 'struct' '' $HIT_RESULT
Add-Pin $meshBack 'bTeleport' 'in' 'bool' '' $null 'true'
Connect (PlayerPart 'Mesh' $SKELETAL 5000 ($y + 250)) 'Mesh' $meshBack 'self'
Connect (New-VarGet 'MeshRest' $null 'struct' '' $TRANSFORM 4950 ($y + 350)) 'MeshRest' $meshBack 'NewTransform'
$animBack = New-Call $SKELETAL 'SetAnimationMode' $false 5450 $y
Add-Pin $animBack 'self' 'in' 'object' '' $SKELETAL
Add-Pin $animBack 'InAnimationMode' 'in' 'byte' '' $ANIM_MODE 'AnimationBlueprint'
Add-Pin $animBack 'bForceInitAnimScriptInstance' 'in' 'bool' '' $null 'true'
Connect (PlayerPart 'Mesh' $SKELETAL 5300 ($y + 250)) 'Mesh' $animBack 'self'
$walkBack = New-Call $CHAR_MOVE 'SetMovementMode' $false 5750 $y
Add-Pin $walkBack 'self' 'in' 'object' '' $CHAR_MOVE
Add-Pin $walkBack 'NewMovementMode' 'in' 'byte' '' $MOVE_MODE 'MOVE_Falling'
Add-Pin $walkBack 'NewCustomMode' 'in' 'byte' '' $null '0'
Connect (PlayerPart 'CharacterMovement' $CHAR_MOVE 5600 ($y + 250)) 'CharacterMovement' $walkBack 'self'
$inputBack = New-Call $ACTOR 'EnableInput' $false 6050 $y
Add-Pin $inputBack 'self' 'in' 'object' '' $ACTOR
Add-Pin $inputBack 'PlayerController' 'in' 'object' '' $CONTROLLER
Connect (Player 5850 ($y + 250)) 'ReturnValue' $inputBack 'self'
Connect (Controller 5850 ($y + 350)) 'ReturnValue' $inputBack 'PlayerController'
$putOut = New-Call $ACTOR_COMP 'Deactivate' $false 6350 $y
Add-Pin $putOut 'self' 'in' 'object' '' $ACTOR_COMP
Connect (TrapFire 6200 ($y + 200)) 'TrapFire' $putOut 'self'
$hideCage = SetVisible (TrapCage 6500 ($y + 200)) 'TrapCage' 'false' 6650 $y
$lightUp = CameraFade '1.0' '0.0' 'false' 6950 $y
$waitNow = Enter '0' '0' 7250 $y
$faceClock = RealSet 'FaceTime' 8000 $y '0.0'
$calmAgain = IntSet 'Anger' 8250 $y '0'
$grabDone = BoolSet 'GrabCharge' 'false' 8500 $y
Chain @($reappear, $meshBack, $animBack, $walkBack, $inputBack, $putOut, $hideCage, $lightUp, $waitNow[0])
Chain @($waitNow[1], $faceClock, $calmAgain, $grabDone)

# --- 3. Hitting the player -----------------------------------------------------------------------------------
$y = 4000
$fromCharge = New-Branch 600 $y
$atLeast2 = CompareOp 'GreaterEqual' 'int' 450 ($y + 200)
Connect (IntGet 'Phase' 250 ($y + 200)) 'Phase' $atLeast2 'A'
(Get-Pin $atLeast2 'B').Default = '2'
Connect $atLeast2 'ReturnValue' $fromCharge 'Condition'
Connect $steps 'then_3' $fromCharge 'execute'
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
$isGrab = New-Branch 1850 ($y - 300)
Connect (New-VarGet 'GrabCharge' $null 'bool' '' $null 1700 ($y - 150)) 'GrabCharge' $isGrab 'Condition'
Connect $hit 'then' $isGrab 'execute'
Connect $isGrab 'else' $launch 'execute'
$once = BoolSet 'HitDone' 'true' 2300 $y
Connect $launch 'then' $once 'execute'
$calmed = IntSet 'Anger' 2550 $y '0'
Connect $once 'then' $calmed 'execute'

# A grab charge that hits: the player is caught and laid on the sun's back, flailing (FlailAnim, looping), and the
# black cage waits hidden above its spot beside the sun (CageOffset from the actor, on the ground), door to the sun.
$y = 13000
$caught = Enter '5' $GRAB_FACE.Carry 2100 $y
Connect $isGrab 'then' $caught[0] 'execute'
$caughtOnce = BoolSet 'HitDone' 'true' 2850 $y
$liftFrom = VecSet 'ChargeFrom' 3100 $y
Connect (SunAt 2950 ($y + 250)) 'ReturnValue' $liftFrom 'ChargeFrom'
$noRide = PlatformSolid 'NoCollision' 3400 $y
$noInput = New-Call $ACTOR 'DisableInput' $false 3700 $y
Add-Pin $noInput 'self' 'in' 'object' '' $ACTOR
Add-Pin $noInput 'PlayerController' 'in' 'object' '' $CONTROLLER
Connect (Player 3500 ($y + 250)) 'ReturnValue' $noInput 'self'
Connect (Controller 3500 ($y + 350)) 'ReturnValue' $noInput 'PlayerController'
$halt = New-Call $MOVE_COMP 'StopMovementImmediately' $false 4000 $y
Add-Pin $halt 'self' 'in' 'object' '' $MOVE_COMP
Connect (PlayerPart 'CharacterMovement' $CHAR_MOVE 3850 ($y + 250)) 'CharacterMovement' $halt 'self'
$freeze = New-Call $CHAR_MOVE 'DisableMovement' $false 4300 $y
Add-Pin $freeze 'self' 'in' 'object' '' $CHAR_MOVE
Connect (PlayerPart 'CharacterMovement' $CHAR_MOVE 4150 ($y + 350)) 'CharacterMovement' $freeze 'self'
$meshNow = New-Call $SCENE 'GetRelativeTransform' $true 4450 ($y + 250)
Add-Pin $meshNow 'self' 'in' 'object' '' $SCENE
Add-Pin $meshNow 'ReturnValue' 'out' 'struct' '' $TRANSFORM
Connect (PlayerPart 'Mesh' $SKELETAL 4300 ($y + 250)) 'Mesh' $meshNow 'self'
$keepMesh = New-VarSet 'MeshRest' $null 'struct' $TRANSFORM 4650 $y
Connect $meshNow 'ReturnValue' $keepMesh 'MeshRest'
# On its back: turned LieRoll about its length, and moved so it turns about the pelvis.
$lieTurn = New-Call $MATH 'MakeRotator' $true 4750 ($y + 400)
Add-Pin $lieTurn 'Roll' 'in' 'real' 'float'
Add-Pin $lieTurn 'Pitch' 'in' 'real' 'float' $null '0.0'
Add-Pin $lieTurn 'Yaw' 'in' 'real' 'float' $null $MESH_YAW
Add-Pin $lieTurn 'ReturnValue' 'out' 'struct' '' $ROTATOR
Connect (RealGet 'LieRoll' 4550 ($y + 450)) 'LieRoll' $lieTurn 'Roll'
$lieShift = New-Call $MATH 'GreaterGreater_VectorRotator' $true 5000 ($y + 300)
Add-Pin $lieShift 'A' 'in' 'struct' '' $VECTOR "0.000000,0.000000,$PELVIS"
Add-Pin $lieShift 'B' 'in' 'struct' '' $ROTATOR
Add-Pin $lieShift 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $lieTurn 'ReturnValue' $lieShift 'B'
$lie = New-Call $SCENE 'K2_SetRelativeLocationAndRotation' $false 5250 $y
Add-Pin $lie 'self' 'in' 'object' '' $SCENE
Add-Pin $lie 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $lie 'NewRotation' 'in' 'struct' '' $ROTATOR
Add-Pin $lie 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $lie 'SweepHitResult' 'out' 'struct' '' $HIT_RESULT
Add-Pin $lie 'bTeleport' 'in' 'bool' '' $null 'true'
Connect (PlayerPart 'Mesh' $SKELETAL 5100 ($y + 200)) 'Mesh' $lie 'self'
Connect $lieShift 'ReturnValue' $lie 'NewLocation'
Connect $lieTurn 'ReturnValue' $lie 'NewRotation'
$flail = New-Call $SKELETAL 'PlayAnimation' $false 5550 $y
Add-Pin $flail 'self' 'in' 'object' '' $SKELETAL
Add-Pin $flail 'NewAnimToPlay' 'in' 'object' '' $ANIM_ASSET
Add-Pin $flail 'bLooping' 'in' 'bool' '' $null 'true'
Connect (PlayerPart 'Mesh' $SKELETAL 5400 ($y + 200)) 'Mesh' $flail 'self'
Connect (New-VarGet 'FlailAnim' $null 'object' '' $ANIM_ASSET 5400 ($y + 300)) 'FlailAnim' $flail 'NewAnimToPlay'
# The cage's spot: CageOffset (X, Y) from the actor, on its ground; it starts DropHeight above.
$actorAt = New-Call $ACTOR 'K2_GetActorLocation' $true 5450 ($y + 500)
Add-Pin $actorAt 'self' 'in' 'object' '' $ACTOR
Add-Pin $actorAt 'ReturnValue' 'out' 'struct' '' $VECTOR
$actorParts = BreakVec 5700 ($y + 500)
Connect $actorAt 'ReturnValue' $actorParts 'InVec'
$spotX = Math 'Add' 5900 ($y + 450)
Connect $actorParts 'X' $spotX 'A'
Connect (RealGet 'CageOffsetX' 5700 ($y + 650)) 'CageOffsetX' $spotX 'B'
$spotY = Math 'Add' 5900 ($y + 600)
Connect $actorParts 'Y' $spotY 'A'
Connect (RealGet 'CageOffsetY' 5700 ($y + 750)) 'CageOffsetY' $spotY 'B'
$spot = MakeVec 6100 ($y + 500)
Connect $spotX 'ReturnValue' $spot 'X'
Connect $spotY 'ReturnValue' $spot 'Y'
Connect $actorParts 'Z' $spot 'Z'
$keepGround = VecSet 'CageGround' 5850 $y
Connect $spot 'ReturnValue' $keepGround 'CageGround'
$above = ShiftZ 6100 ($y + 250)
Connect $keepGround 'Output_Get' $above[0] 'InVec'
Connect (RealGet 'DropHeight' 6100 ($y + 400)) 'DropHeight' $above[2] 'B'
$keepTop = VecSet 'CageTop' 6650 $y
Connect $above[1] 'ReturnValue' $keepTop 'CageTop'
# Door (the cage's +Y) toward the sun: yaw = the way to the sun - 90.
$toSun = New-Call $MATH 'FindLookAtRotation' $true 6650 ($y + 450)
Add-Pin $toSun 'Start' 'in' 'struct' '' $VECTOR
Add-Pin $toSun 'Target' 'in' 'struct' '' $VECTOR
Add-Pin $toSun 'ReturnValue' 'out' 'struct' '' $ROTATOR
Connect $keepGround 'Output_Get' $toSun 'Start'
Connect (VecGet 'HomeLocation' 6450 ($y + 550)) 'HomeLocation' $toSun 'Target'
$toSunParts = New-Call $MATH 'BreakRotator' $true 6900 ($y + 450)
Add-Pin $toSunParts 'InRot' 'in' 'struct' '' $ROTATOR
Add-Pin $toSunParts 'Roll' 'out' 'real' 'float'
Add-Pin $toSunParts 'Pitch' 'out' 'real' 'float'
Add-Pin $toSunParts 'Yaw' 'out' 'real' 'float'
Connect $toSun 'ReturnValue' $toSunParts 'InRot'
$doorYaw = Math 'Add' 7100 ($y + 450)
Connect $toSunParts 'Yaw' $doorYaw 'A'
(Get-Pin $doorYaw 'B').Default = '-90.0'
$doorTurn = New-Call $MATH 'MakeRotator' $true 7300 ($y + 450)
Add-Pin $doorTurn 'Roll' 'in' 'real' 'float' $null '0.0'
Add-Pin $doorTurn 'Pitch' 'in' 'real' 'float' $null '0.0'
Add-Pin $doorTurn 'Yaw' 'in' 'real' 'float'
Add-Pin $doorTurn 'ReturnValue' 'out' 'struct' '' $ROTATOR
Connect $doorYaw 'ReturnValue' $doorTurn 'Yaw'
$placeCage = New-Call $SCENE 'K2_SetWorldLocationAndRotation' $false 6950 $y
Add-Pin $placeCage 'self' 'in' 'object' '' $SCENE
Add-Pin $placeCage 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $placeCage 'NewRotation' 'in' 'struct' '' $ROTATOR
Add-Pin $placeCage 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $placeCage 'SweepHitResult' 'out' 'struct' '' $HIT_RESULT
Add-Pin $placeCage 'bTeleport' 'in' 'bool' '' $null 'true'
Connect (TrapCage 6800 ($y + 250)) 'TrapCage' $placeCage 'self'
Connect $keepTop 'Output_Get' $placeCage 'NewLocation'
Connect $doorTurn 'ReturnValue' $placeCage 'NewRotation'
# Door shut at the start of its animation, the cage solid (Fade 1).
$doorShut = New-Call $SKELETAL 'SetPosition' $false 7250 $y
Add-Pin $doorShut 'self' 'in' 'object' '' $SKELETAL
Add-Pin $doorShut 'InPos' 'in' 'real' 'float' $null '0.0'
Add-Pin $doorShut 'bFireNotifies' 'in' 'bool' '' $null 'false'
Connect (TrapCage 7100 ($y + 200)) 'TrapCage' $doorShut 'self'
$solidCage = CageFade '1.0' 7550 $y
Chain @($caught[1], $caughtOnce, $liftFrom, $noRide, $noInput, $halt, $freeze, $keepMesh, $lie, $flail, $keepGround, $keepTop, $placeCage, $doorShut, $solidCage)

# --- Platform follows the top of the ball (separate from SunMesh, so it stays level) --------------------------------
$y = 7000
$platformSpot = ShiftZ 500 ($y + 200)
Connect (SunAt 300 ($y + 200)) 'ReturnValue' $platformSpot[0] 'InVec'
(Get-Pin $platformSpot[2] 'B').Default = $PLATFORM_ABOVE
$carry = New-Call $SCENE 'K2_SetWorldLocation' $false 1100 $y
Add-Pin $carry 'self' 'in' 'object' '' $SCENE
Add-Pin $carry 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $carry 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $carry 'SweepHitResult' 'out' 'struct' '' "/Script/CoreUObject.ScriptStruct'/Script/Engine.HitResult'"  # $HIT is the hit branch by now
Add-Pin $carry 'bTeleport' 'in' 'bool' '' $null 'false'
Connect (Platform 900 ($y + 400)) 'Platform' $carry 'self'
Connect $platformSpot[1] 'ReturnValue' $carry 'NewLocation'
Connect $steps 'then_2' $carry 'execute'

# --- 4. Switch faces on a timer while waiting --------------------------------------------------------------------
$y = 5200
$waiting = New-Branch 600 $y
Connect (PhaseIs '0' 450 ($y + 200)) 'ReturnValue' $waiting 'Condition'
Connect $steps 'then_4' $waiting 'execute'
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
Connect $steps 'then_5' $ready 'execute'
Connect $hasMaterial 'ReturnValue' $ready 'Condition'
# At full anger (MaxAnger above 0 and reached) the face stays furious, whatever the phase.
$full = New-Branch 1100 $y
$atMax = CompareOp 'GreaterEqual' 'int' 950 ($y + 200)
Connect (IntGet 'Anger' 750 ($y + 200)) 'Anger' $atMax 'A'
Connect (IntGet 'MaxAnger' 750 ($y + 280)) 'MaxAnger' $atMax 'B'
Connect $atMax 'ReturnValue' $full 'Condition'
Connect $ready 'then' $full 'execute'
$someAnger = New-Branch 1350 $y
$any = CompareOp 'Greater' 'int' 1200 ($y + 200)
Connect (IntGet 'Anger' 1000 ($y + 300)) 'Anger' $any 'A'
(Get-Pin $any 'B').Default = '0'
Connect $any 'ReturnValue' $someAnger 'Condition'
# Not during the grab (phases 5 and up), which picks its own faces.
$notGrab = New-Branch 1225 ($y - 250)
$beforeGrab = CompareOp 'Less' 'int' 1075 ($y - 100)
Connect (IntGet 'Phase' 875 ($y - 100)) 'Phase' $beforeGrab 'A'
(Get-Pin $beforeGrab 'B').Default = '5'
Connect $beforeGrab 'ReturnValue' $notGrab 'Condition'
Connect $full 'then' $notGrab 'execute'
Connect $notGrab 'then' $someAnger 'execute'
$furious = New-Call $DYNAMIC 'SetScalarParameterValue' $false 1650 ($y - 150)
Add-Pin $furious 'self' 'in' 'object' '' $DYNAMIC
Add-Pin $furious 'ParameterName' 'in' 'name' '' $null 'FaceIndex'
Add-Pin $furious 'Value' 'in' 'real' 'float' $null $FACE.Furious
Connect $someAnger 'then' $furious 'execute'
Connect (New-VarGet 'FaceMaterial' $null 'object' '' $DYNAMIC 1450 ($y - 50)) 'FaceMaterial' $furious 'self'
$asNumber = IntToReal 1400 ($y + 350)
Connect (IntGet 'FaceIndex' 1200 ($y + 400)) 'FaceIndex' $asNumber 'InInt'
$show = New-Call $DYNAMIC 'SetScalarParameterValue' $false 1650 ($y + 150)
Add-Pin $show 'self' 'in' 'object' '' $DYNAMIC
Add-Pin $show 'ParameterName' 'in' 'name' '' $null 'FaceIndex'
Add-Pin $show 'Value' 'in' 'real' 'float'
Connect $full 'else' $show 'execute'
Connect $notGrab 'else' $show 'execute'
Connect $someAnger 'else' $show 'execute'
Connect $material 'FaceMaterial' $show 'self'
Connect $asNumber 'ReturnValue' $show 'Value'

# --- 6. Body colour and glow by anger ----------------------------------------------------------------------------
$y = 6400
$body = New-VarGet 'BodyMaterial' $null 'object' '' $DYNAMIC 350 ($y + 200)
$hasBody = New-IsValid 600 ($y + 200)
Connect $body 'BodyMaterial' $hasBody 'Object'
$bodyReady = New-Branch 850 $y
Connect $steps 'then_6' $bodyReady 'execute'
Connect $hasBody 'ReturnValue' $bodyReady 'Condition'
$angerNow = IntToReal 700 ($y + 400)
Connect (IntGet 'Anger' 500 ($y + 400)) 'Anger' $angerNow 'InInt'
$angerMax = IntToReal 700 ($y + 500)
Connect (IntGet 'MaxAnger' 500 ($y + 500)) 'MaxAnger' $angerMax 'InInt'
$share = New-Call $MATH 'SafeDivide' $true 950 ($y + 400)
Add-Pin $share 'A' 'in' 'real' 'double'
Add-Pin $share 'B' 'in' 'real' 'double'
Add-Pin $share 'ReturnValue' 'out' 'real' 'double'
Connect $angerNow 'ReturnValue' $share 'A'
Connect $angerMax 'ReturnValue' $share 'B'
$tint = New-Call $MATH 'LinearColorLerp' $true 1200 ($y + 300)
Add-Pin $tint 'A' 'in' 'struct' '' $LINEAR $CALM
Add-Pin $tint 'B' 'in' 'struct' '' $LINEAR $ANGRY
Add-Pin $tint 'Alpha' 'in' 'real' 'float'
Add-Pin $tint 'ReturnValue' 'out' 'struct' '' $LINEAR
Connect $share 'ReturnValue' $tint 'Alpha'
$paint = New-Call $DYNAMIC 'SetVectorParameterValue' $false 1500 $y
Add-Pin $paint 'self' 'in' 'object' '' $DYNAMIC
Add-Pin $paint 'ParameterName' 'in' 'name' '' $null 'Color'
Add-Pin $paint 'Value' 'in' 'struct' '' $LINEAR
Connect $bodyReady 'then' $paint 'execute'
Connect $body 'BodyMaterial' $paint 'self'
Connect $tint 'ReturnValue' $paint 'Value'
$glowLevel = New-Call $MATH 'Lerp' $true 1500 ($y + 450)
Add-Pin $glowLevel 'A' 'in' 'real' 'double' $null $CALM_GLOW
Add-Pin $glowLevel 'B' 'in' 'real' 'double' $null $ANGRY_GLOW
Add-Pin $glowLevel 'Alpha' 'in' 'real' 'double'
Add-Pin $glowLevel 'ReturnValue' 'out' 'real' 'double'
Connect $share 'ReturnValue' $glowLevel 'Alpha'
$shine = New-Call $DYNAMIC 'SetScalarParameterValue' $false 1850 $y
Add-Pin $shine 'self' 'in' 'object' '' $DYNAMIC
Add-Pin $shine 'ParameterName' 'in' 'name' '' $null 'Glow'
Add-Pin $shine 'Value' 'in' 'real' 'float'
Connect $paint 'then' $shine 'execute'
Connect $body 'BodyMaterial' $shine 'self'
# A grab charge flashes GrabGlowBoost times brighter: the warning.
$warn = New-Call $MATH 'SelectFloat' $true 1500 ($y + 650)
Add-Pin $warn 'A' 'in' 'real' 'double'
Add-Pin $warn 'B' 'in' 'real' 'double' $null '1.0'
Add-Pin $warn 'bPickA' 'in' 'bool'
Add-Pin $warn 'ReturnValue' 'out' 'real' 'double'
Connect (RealGet 'GrabGlowBoost' 1300 ($y + 650)) 'GrabGlowBoost' $warn 'A'
Connect (New-VarGet 'GrabCharge' $null 'bool' '' $null 1300 ($y + 750)) 'GrabCharge' $warn 'bPickA'
$glowWarned = Math 'Multiply' 1700 ($y + 500)
Connect $glowLevel 'ReturnValue' $glowWarned 'A'
Connect $warn 'ReturnValue' $glowWarned 'B'
Connect $glowWarned 'ReturnValue' $shine 'Value'
# The flames fade the same way: SunFire (orange) out, SunFireBlue (the same fire in blue) in, through AllColor's alpha.
$EMITTER = "/Script/CoreUObject.Class'/Script/Effekseer.EffekseerEmitterComponent'"
$FCOLOR = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Color'"
$last = $shine
$fx = 2150
foreach ($fire in @(@('SunFire', '(R=1.000000,G=1.000000,B=1.000000,A=1.000000)', '(R=1.000000,G=1.000000,B=1.000000,A=0.000000)'),
                    @('SunFireBlue', '(R=1.000000,G=1.000000,B=1.000000,A=0.000000)', '(R=1.000000,G=1.000000,B=1.000000,A=1.000000)'))) {
  $fade = New-Call $MATH 'LinearColorLerp' $true ($fx - 100) ($y + 300)
  Add-Pin $fade 'A' 'in' 'struct' '' $LINEAR $fire[1]
  Add-Pin $fade 'B' 'in' 'struct' '' $LINEAR $fire[2]
  Add-Pin $fade 'Alpha' 'in' 'real' 'float'
  Add-Pin $fade 'ReturnValue' 'out' 'struct' '' $LINEAR
  Connect $share 'ReturnValue' $fade 'Alpha'
  $asColor = New-Call $MATH 'Conv_LinearColorToColor' $true ($fx + 100) ($y + 300)
  Add-Pin $asColor 'InLinearColor' 'in' 'struct' '' $LINEAR
  Add-Pin $asColor 'InUseSRGB' 'in' 'bool' '' $null 'false'
  Add-Pin $asColor 'ReturnValue' 'out' 'struct' '' $FCOLOR
  Connect $fade 'ReturnValue' $asColor 'InLinearColor'
  $tintFire = New-VarSet 'AllColor' $EMITTER 'struct' $FCOLOR ($fx + 300) $y
  Connect $asColor 'ReturnValue' $tintFire 'AllColor'
  Connect (New-VarGet $fire[0] $null 'object' '' $EMITTER ($fx + 100) ($y + 200)) $fire[0] $tintFire 'self'
  Connect $last 'then' $tintFire 'execute'
  $last = $tintFire
  $fx += 600
}
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
