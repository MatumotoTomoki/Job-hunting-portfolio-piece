param([string]$OutDir)
# Paste text for the machine tower gimmicks (components and variables from setup_area2_gimmicks.py):
#   BP_SpinGear_EventGraph.txt      Tick: Pivot turns SpinSpeed degrees a second about Z.
#   BP_ToggleSwitch_EventGraph.txt  touched (once at a time): the game instance's SwitchRed flips. Tick: the button
#                                   shows red or blue.
#   BP_SwitchBlock_EventGraph.txt   Tick: solid (Solid seen and colliding) while SwitchRed == IsRed, else only the
#                                   see-through Ghost; changed only when it has to.
#   BP_CageTrap_EventGraph.txt      the player walks into Trigger: held still, the cage drops on them from DropHeight,
#                                   black, back at RespawnLocation facing RespawnYaw, the cage gone, the screen clears.
#   BP_Gondola_EventGraph.txt       the player steps into the cabin: it leaves, travels TravelOffset over
#                                   TravelSeconds, waits WaitSeconds, comes back.
if (-not $OutDir) { throw 'OutDir is required' }
$cageGen = Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_hell_cage.ps1'
$defs = Get-Content -LiteralPath $cageGen -Encoding UTF8 | Select-Object -Skip 10 -First 172
. ([ScriptBlock]::Create(($defs -join "`n")))

$SCENE = "/Script/CoreUObject.Class'/Script/Engine.SceneComponent'"
$STATIC_MESH = "/Script/CoreUObject.Class'/Script/Engine.StaticMeshComponent'"
$MOVEMENT = "/Script/CoreUObject.Class'/Script/Engine.MovementComponent'"
$CONTROLLER_BASE = "/Script/CoreUObject.Class'/Script/Engine.Controller'"
$COLLISION_ENUM = "/Script/CoreUObject.Enum'/Script/Engine.ECollisionEnabled'"

function Event($name, [double]$x, [double]$y) {
  $n = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$ACTOR`",MemberName=`"$name`")", 'bOverrideFunction=True') $x $y
  Add-Pin $n 'then' 'out' 'exec'
  return $n
}
function SetSelf($name, $cat, $value, [double]$x, [double]$y) {
  $n = New-VarSet $name $null $cat $null $x $y
  if ($null -ne $value) { (Get-Pin $n $name).Default = $value }
  return $n
}
function Comp($name, $class, [double]$x, [double]$y) { New-VarGet $name $null 'object' '' $class $x $y }
function Real($name, [double]$x, [double]$y) { New-VarGet $name $null 'real' 'double' $null $x $y }
function InputCall($func, [double]$x, [double]$y) {
  $n = New-Call $ACTOR $func $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR
  Add-Pin $n 'PlayerController' 'in' 'object' '' $CONTROLLER
  Connect (Player ($x - 200) ($y + 200)) 'ReturnValue' $n 'self'
  Connect (Controller ($x - 200) ($y + 300)) 'ReturnValue' $n 'PlayerController'
  return $n
}
function PlayerIn($boxName, [double]$x, [double]$y) {
  $n = New-Call $PRIMITIVE 'IsOverlappingActor' $true $x $y
  Add-Pin $n 'self' 'in' 'object' '' $PRIMITIVE
  Add-Pin $n 'Other' 'in' 'object' '' $ACTOR
  Add-Pin $n 'ReturnValue' 'out' 'bool'
  Connect (New-VarGet $boxName $null 'object' '' $BOX ($x - 200) $y) $boxName $n 'self'
  Connect (Player ($x - 250) ($y + 100)) 'ReturnValue' $n 'Other'
  return $n
}
# Touched by the player, once at a time: returns (event, last branch); wire the branch's 'then' on.
function Touched($guard, $boxName, [double]$x, [double]$y) {
  $touch = Event 'ReceiveActorBeginOverlap' $x $y
  Add-Pin $touch 'OtherActor' 'out' 'object' '' $ACTOR
  $once = New-Branch ($x + 300) $y
  Connect (New-VarGet $guard $null 'bool' '' $null ($x + 150) ($y + 200)) $guard $once 'Condition'
  $isPlayer = New-Branch ($x + 550) $y
  Connect (PlayerIn $boxName ($x + 450) ($y + 250)) 'ReturnValue' $isPlayer 'Condition'
  Connect $touch 'then' $once 'execute'
  Connect $once 'else' $isPlayer 'execute'
  return $isPlayer
}
function Visible($component, $componentPin, $value, [double]$x, [double]$y) {
  $n = New-Call $SCENE 'SetVisibility' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $SCENE
  Add-Pin $n 'bNewVisibility' 'in' 'bool' '' $null 'true'
  Add-Pin $n 'bPropagateToChildren' 'in' 'bool' '' $null 'false'
  Connect $component $componentPin $n 'self'
  if ($value -is [string]) { (Get-Pin $n 'bNewVisibility').Default = $value } else { Connect $value[0] $value[1] $n 'bNewVisibility' }
  return $n
}
function Collide($component, $componentPin, $type, [double]$x, [double]$y) {
  $n = New-Call $PRIMITIVE 'SetCollisionEnabled' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $PRIMITIVE
  Add-Pin $n 'NewType' 'in' 'byte' '' $COLLISION_ENUM $type
  Connect $component $componentPin $n 'self'
  return $n
}
function Not($source, $sourcePin, [double]$x, [double]$y) {
  $n = New-Call $MATH 'Not_PreBool' $true $x $y
  Add-Pin $n 'A' 'in' 'bool'
  Add-Pin $n 'ReturnValue' 'out' 'bool'
  Connect $source $sourcePin $n 'A'
  return $n
}
function MoveTo($component, $componentPin, [double]$x, [double]$y) {
  # MoveComponentTo: wire 'Move' in, set or wire TargetRelativeLocation and OverTime.
  $n = New-Call $SYSTEM 'MoveComponentTo' $false $x $y
  $n.Props = @('bWantsEnumToExecExpansion=True') + $n.Props
  $n.Pins.Clear()
  Add-Pin $n 'Move' 'in' 'exec'
  Add-Pin $n 'then' 'out' 'exec'
  Add-Pin $n 'Component' 'in' 'object' '' $SCENE
  Add-Pin $n 'TargetRelativeLocation' 'in' 'struct' '' $VECTOR '0.000000,0.000000,0.000000'
  Add-Pin $n 'TargetRelativeRotation' 'in' 'struct' '' $ROTATOR '0, 0, 0'
  Add-Pin $n 'bEaseOut' 'in' 'bool' '' $null 'true'
  Add-Pin $n 'bEaseIn' 'in' 'bool' '' $null 'true'
  Add-Pin $n 'OverTime' 'in' 'real' 'float' $null '1.0'
  Add-Pin $n 'bForceShortestRotationPath' 'in' 'bool' '' $null 'false'
  Connect $component $componentPin $n 'Component'
  return $n
}

# ===== BP_SpinGear =========================================================================================
Reset-Graph 100
$tick = Event 'ReceiveTick' 0 0
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$angle = New-Operator 'Multiply' 'Multiply_DoubleDouble' 'real' 'double' 'real' 300 250
(Get-Pin $angle 'ReturnValue').Sub = 'double'
Connect (Real 'SpinSpeed' 100 250) 'SpinSpeed' $angle 'A'
Connect $tick 'DeltaSeconds' $angle 'B'
$rot = New-Call $MATH 'MakeRotator' $true 500 250
Add-Pin $rot 'Roll' 'in' 'real' 'float' $null '0.0'
Add-Pin $rot 'Pitch' 'in' 'real' 'float' $null '0.0'
Add-Pin $rot 'Yaw' 'in' 'real' 'float'
Add-Pin $rot 'ReturnValue' 'out' 'struct' '' $ROTATOR
Connect $angle 'ReturnValue' $rot 'Yaw'
$turn = New-Call $SCENE 'K2_AddLocalRotation' $false 750 0
Add-Pin $turn 'self' 'in' 'object' '' $SCENE
Add-Pin $turn 'DeltaRotation' 'in' 'struct' '' $ROTATOR
Add-Pin $turn 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $turn 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $turn 'bTeleport' 'in' 'bool' '' $null 'false'
Connect (Comp 'Pivot' $SCENE 550 150) 'Pivot' $turn 'self'
Connect $rot 'ReturnValue' $turn 'DeltaRotation'
Connect $tick 'then' $turn 'execute'
Write-Graph 'BP_SpinGear_EventGraph.txt'

# ===== BP_ToggleSwitch =====================================================================================
Reset-Graph 100
# (Not $hit: names ignore case, and $HIT is the HitResult type.)
$pressed = Touched 'Busy' 'Trigger' 0 0
$busy = SetSelf 'Busy' 'bool' 'true' 900 0
$cast = GameInstance 1200 0
$flip = GiSet $cast 'SwitchRed' 'bool' '' 1500 0
Connect (Not (GiGet $cast 'SwitchRed' 'bool' '' 1250 250) 'SwitchRed' 1450 250) 'ReturnValue' $flip 'SwitchRed'
$rest = Delay '0.4' 1800 0
$free = SetSelf 'Busy' 'bool' 'false' 2050 0
Connect $pressed 'then' $busy 'execute'
Chain @($busy, $cast)
Connect $cast 'then' $flip 'execute'
Chain @($flip, $rest, $free)
# The button shows what is on.
$tick = Event 'ReceiveTick' 0 700
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$cast2 = GameInstance 300 700
$isRed = GiGet $cast2 'SwitchRed' 'bool' '' 300 950
$showRed = Visible (Comp 'ButtonRed' $STATIC_MESH 450 1050) 'ButtonRed' @($isRed, 'SwitchRed') 600 700
$showBlue = Visible (Comp 'ButtonBlue' $STATIC_MESH 750 1050) 'ButtonBlue' @((Not $isRed 'SwitchRed' 700 1150), 'ReturnValue') 900 700
Connect $tick 'then' $cast2 'execute'
Connect $cast2 'then' $showRed 'execute'
Chain @($showRed, $showBlue)
Write-Graph 'BP_ToggleSwitch_EventGraph.txt'

# ===== BP_SwitchBlock ======================================================================================
Reset-Graph 100
$tick = Event 'ReceiveTick' 0 0
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$cast = GameInstance 300 0
$wanted = New-Operator 'EqualEqual' 'EqualEqual_BoolBool' 'bool' '' 'bool' 500 250
Connect (GiGet $cast 'SwitchRed' 'bool' '' 300 250) 'SwitchRed' $wanted 'A'
Connect (New-VarGet 'IsRed' $null 'bool' '' $null 300 350) 'IsRed' $wanted 'B'
$same = New-Operator 'EqualEqual' 'EqualEqual_BoolBool' 'bool' '' 'bool' 700 300
Connect $wanted 'ReturnValue' $same 'A'
Connect (New-VarGet 'Shown' $null 'bool' '' $null 500 400) 'Shown' $same 'B'
$unchanged = New-Call $MATH 'BooleanAND' $true 900 300
Add-Pin $unchanged 'A' 'in' 'bool'
Add-Pin $unchanged 'B' 'in' 'bool'
Add-Pin $unchanged 'ReturnValue' 'out' 'bool'
Connect (New-VarGet 'Ready' $null 'bool' '' $null 700 450) 'Ready' $unchanged 'A'
Connect $same 'ReturnValue' $unchanged 'B'
$skip = New-Branch 1000 0
Connect $unchanged 'ReturnValue' $skip 'Condition'
$which = New-Branch 1250 0
Connect $wanted 'ReturnValue' $which 'Condition'
Connect $tick 'then' $cast 'execute'
Connect $cast 'then' $skip 'execute'
Connect $skip 'else' $which 'execute'
foreach ($on in $true, $false) {
  $y = if ($on) { -300 } else { 400 }
  $collide = Collide (Comp 'Solid' $STATIC_MESH 1400 ($y + 200)) 'Solid' $(if ($on) { 'QueryAndPhysics' } else { 'NoCollision' }) 1550 $y
  $seen = Visible (Comp 'Solid' $STATIC_MESH 1700 ($y + 200)) 'Solid' $(if ($on) { 'true' } else { 'false' }) 1850 $y
  $ghostSeen = Visible (Comp 'Ghost' $STATIC_MESH 2000 ($y + 200)) 'Ghost' $(if ($on) { 'false' } else { 'true' }) 2150 $y
  $shown = SetSelf 'Shown' 'bool' $(if ($on) { 'true' } else { 'false' }) 2450 $y
  $ready = SetSelf 'Ready' 'bool' 'true' 2700 $y
  Connect $which $(if ($on) { 'then' } else { 'else' }) $collide 'execute'
  Chain @($collide, $seen, $ghostSeen, $shown, $ready)
}
Write-Graph 'BP_SwitchBlock_EventGraph.txt'

# ===== BP_CageTrap =========================================================================================
Reset-Graph 100
$caught = Touched 'Busy' 'Trigger' 0 0
$busy = SetSelf 'Busy' 'bool' 'true' 900 0
$hold = InputCall 'DisableInput' 1150 0
$stop = New-Call $MOVEMENT 'StopMovementImmediately' $false 1450 0
Add-Pin $stop 'self' 'in' 'object' '' $MOVEMENT
Connect (Movement 1250 250) 'CharacterMovement' $stop 'self'
# Where the cage lands: the player's feet (92 cm under the capsule's middle), relative to this actor.
$feet = New-Operator 'Subtract' 'Subtract_VectorVector' 'struct' '' 'struct' 1700 500
foreach ($pin in 'A', 'B', 'ReturnValue') { (Get-Pin $feet $pin).Obj = $VECTOR }
$playerAt = New-Call $ACTOR 'K2_GetActorLocation' $true 1450 450
Add-Pin $playerAt 'self' 'in' 'object' '' $ACTOR
Add-Pin $playerAt 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect (Player 1250 450) 'ReturnValue' $playerAt 'self'
$selfAt = New-Call $ACTOR 'K2_GetActorLocation' $true 1450 600
Add-Pin $selfAt 'self' 'in' 'object' '' $ACTOR
Add-Pin $selfAt 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $playerAt 'ReturnValue' $feet 'A'
Connect $selfAt 'ReturnValue' $feet 'B'
$land = New-Operator 'Subtract' 'Subtract_VectorVector' 'struct' '' 'struct' 1900 500
foreach ($pin in 'A', 'B', 'ReturnValue') { (Get-Pin $land $pin).Obj = $VECTOR }
Connect $feet 'ReturnValue' $land 'A'
(Get-Pin $land 'B').Default = '0.000000,0.000000,92.000000'
$up = New-Call $MATH 'MakeVector' $true 1900 700
Add-Pin $up 'X' 'in' 'real' 'double' $null '0.0'
Add-Pin $up 'Y' 'in' 'real' 'double' $null '0.0'
Add-Pin $up 'Z' 'in' 'real' 'double'
Add-Pin $up 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect (Real 'DropHeight' 1700 750) 'DropHeight' $up 'Z'
$above = New-Operator 'Add' 'Add_VectorVector' 'struct' '' 'struct' 2100 600
foreach ($pin in 'A', 'B', 'ReturnValue') { (Get-Pin $above $pin).Obj = $VECTOR }
Connect $land 'ReturnValue' $above 'A'
Connect $up 'ReturnValue' $above 'B'
$lift = New-Call $SCENE 'K2_SetRelativeLocation' $false 1750 0
Add-Pin $lift 'self' 'in' 'object' '' $SCENE
Add-Pin $lift 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $lift 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $lift 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $lift 'bTeleport' 'in' 'bool' '' $null 'true'
Connect (Comp 'Cage' $STATIC_MESH 1550 200) 'Cage' $lift 'self'
Connect $above 'ReturnValue' $lift 'NewLocation'
$appear = Visible (Comp 'Cage' $STATIC_MESH 1950 250) 'Cage' 'true' 2100 0
$drop = MoveTo (Comp 'Cage' $STATIC_MESH 2250 250) 'Cage' 2400 0
(Get-Pin $drop 'bEaseOut').Default = 'false'
(Get-Pin $drop 'OverTime').Default = '0.45'
Connect $land 'ReturnValue' $drop 'TargetRelativeLocation'
$look = Delay '0.7' 2800 0
$dark = Fade '0.0' '1.0' '0.5' 'true' 3050 0
$wait = Delay '0.6' 3550 0
$place = New-Call $ACTOR 'K2_SetActorLocationAndRotation' $false 3800 0
Add-Pin $place 'self' 'in' 'object' '' $ACTOR
Add-Pin $place 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $place 'NewRotation' 'in' 'struct' '' $ROTATOR '0, 0, 0'
Add-Pin $place 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $place 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $place 'bTeleport' 'in' 'bool' '' $null 'true'
Add-Pin $place 'ReturnValue' 'out' 'bool'
Connect (Player 3600 300) 'ReturnValue' $place 'self'
Connect (New-VarGet 'RespawnLocation' $null 'struct' '' $VECTOR 3600 400) 'RespawnLocation' $place 'NewLocation'
$face = New-Call $CONTROLLER_BASE 'SetControlRotation' $false 4150 0
Add-Pin $face 'self' 'in' 'object' '' $CONTROLLER_BASE
Add-Pin $face 'NewRotation' 'in' 'struct' '' $ROTATOR
(Get-Pin $face 'NewRotation') | Add-Member -NotePropertyName ConstRef -NotePropertyValue $true
Connect (Controller 3950 250) 'ReturnValue' $face 'self'
$facing = New-Call $MATH 'MakeRotator' $true 3950 400
Add-Pin $facing 'Roll' 'in' 'real' 'float' $null '0.0'
Add-Pin $facing 'Pitch' 'in' 'real' 'float' $null '0.0'
Add-Pin $facing 'Yaw' 'in' 'real' 'float'
Add-Pin $facing 'ReturnValue' 'out' 'struct' '' $ROTATOR
Connect (Real 'RespawnYaw' 3750 500) 'RespawnYaw' $facing 'Yaw'
Connect $facing 'ReturnValue' $face 'NewRotation'
$gone = Visible (Comp 'Cage' $STATIC_MESH 4300 250) 'Cage' 'false' 4450 0
$clear = Fade '1.0' '0.0' '0.6' 'false' 4700 0
$free = InputCall 'EnableInput' 5200 0
$unlock = SetSelf 'Busy' 'bool' 'false' 5450 0
Connect $caught 'then' $busy 'execute'
Chain @($busy, $hold, $stop, $lift, $appear)
Connect $appear 'then' $drop 'Move'
Connect $drop 'then' $look 'execute'
Chain @($look, $dark, $wait, $place, $face, $gone, $clear, $free, $unlock)
Write-Graph 'BP_CageTrap_EventGraph.txt'

# ===== BP_Gondola ==========================================================================================
Reset-Graph 100
$aboard = Touched 'Moving' 'Trigger' 0 0
$moving = SetSelf 'Moving' 'bool' 'true' 900 0
$settle = Delay '0.6' 1150 0
$go = MoveTo (Comp 'Cabin' $SCENE 1300 250) 'Cabin' 1450 0
Connect (New-VarGet 'TravelOffset' $null 'struct' '' $VECTOR 1250 400) 'TravelOffset' $go 'TargetRelativeLocation'
Connect (Real 'TravelSeconds' 1250 500) 'TravelSeconds' $go 'OverTime'
$stay = Delay '0.0' 1850 0
Connect (Real 'WaitSeconds' 1700 250) 'WaitSeconds' $stay 'Duration'
$back = MoveTo (Comp 'Cabin' $SCENE 2000 250) 'Cabin' 2150 0
Connect (Real 'TravelSeconds' 2000 400) 'TravelSeconds' $back 'OverTime'
$done = SetSelf 'Moving' 'bool' 'false' 2550 0
Connect $aboard 'then' $moving 'execute'
Chain @($moving, $settle)
Connect $settle 'then' $go 'Move'
Connect $go 'then' $stay 'execute'
Connect $stay 'then' $back 'Move'
Connect $back 'then' $done 'execute'
Write-Graph 'BP_Gondola_EventGraph.txt'

# ===== BP_FallCatcher ======================================================================================
# The player in the Net: moved straight down to below the character's -50 m fall check, which respawns them.
Reset-Graph 100
$touch = Event 'ReceiveActorBeginOverlap' 0 0
Add-Pin $touch 'OtherActor' 'out' 'object' '' $ACTOR
$isPlayer = New-Branch 300 0
Connect (PlayerIn 'Net' 200 250) 'ReturnValue' $isPlayer 'Condition'
$at = New-Call $ACTOR 'K2_GetActorLocation' $true 300 450
Add-Pin $at 'self' 'in' 'object' '' $ACTOR
Add-Pin $at 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect (Player 100 450) 'ReturnValue' $at 'self'
$parts = New-Call $MATH 'BreakVector' $true 550 450
Add-Pin $parts 'InVec' 'in' 'struct' '' $VECTOR
Add-Pin $parts 'X' 'out' 'real' 'double'
Add-Pin $parts 'Y' 'out' 'real' 'double'
Add-Pin $parts 'Z' 'out' 'real' 'double'
Connect $at 'ReturnValue' $parts 'InVec'
$below = New-Call $MATH 'MakeVector' $true 800 450
Add-Pin $below 'X' 'in' 'real' 'double'
Add-Pin $below 'Y' 'in' 'real' 'double'
Add-Pin $below 'Z' 'in' 'real' 'double' $null '-5100.0'
Add-Pin $below 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $parts 'X' $below 'X'
Connect $parts 'Y' $below 'Y'
$drop = New-Call $ACTOR 'K2_SetActorLocation' $false 600 0
Add-Pin $drop 'self' 'in' 'object' '' $ACTOR
Add-Pin $drop 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $drop 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $drop 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $drop 'bTeleport' 'in' 'bool' '' $null 'true'
Add-Pin $drop 'ReturnValue' 'out' 'bool'
Connect (Player 400 250) 'ReturnValue' $drop 'self'
Connect $below 'ReturnValue' $drop 'NewLocation'
Connect $touch 'then' $isPlayer 'execute'
Connect $isPlayer 'then' $drop 'execute'
Write-Graph 'BP_FallCatcher_EventGraph.txt'
