param([string]$OutDir)
# Generates the Ctrl+V-pasteable ledge grab for BP_ThirdPersonCharacter1. Self-contained: Q (IA_Grab) looks for a wall
# straight ahead and a ledge on top of it; if there is one, the player hangs from it (no movement, hang montage on a
# loop) and watches for the jump key each frame, then climbs onto the ledge. The jump input itself is left alone:
# with movement off, the character cannot jump while hanging.

$helperFile = (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_height_bgm.ps1')
$helpers = Get-Content -LiteralPath $helperFile -Encoding UTF8 | Select-Object -Skip 3 -First 124
. ([ScriptBlock]::Create(($helpers -join "`n")))
# Above the numbers already in the character graph (the checkpoint part went up to _1031).
$script:counter = 1100

$SCENE_CLASS = "/Script/CoreUObject.Class'/Script/Engine.SceneComponent'"
$CAPSULE_CLASS = "/Script/CoreUObject.Class'/Script/Engine.CapsuleComponent'"
$MOVEMENT_CLASS = "/Script/CoreUObject.Class'/Script/Engine.CharacterMovementComponent'"
$MESH_CLASS = "/Script/CoreUObject.Class'/Script/Engine.SkeletalMeshComponent'"
$ANIM_INSTANCE = "/Script/CoreUObject.Class'/Script/Engine.AnimInstance'"
$CONTROLLER_CLASS = "/Script/CoreUObject.Class'/Script/Engine.PlayerController'"
$MONTAGE_CLASS = "/Script/CoreUObject.Class'/Script/Engine.AnimMontage'"
$ROTATOR_STRUCT = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Rotator'"
$HIT_STRUCT = "/Script/CoreUObject.ScriptStruct'/Script/Engine.HitResult'"
$KEY_STRUCT = "/Script/CoreUObject.ScriptStruct'/Script/InputCore.Key'"
$COLOR_STRUCT = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.LinearColor'"
$TRACE_ENUM = "/Script/CoreUObject.Enum'/Script/Engine.ETraceTypeQuery'"
$DEBUG_ENUM = "/Script/CoreUObject.Enum'/Script/Engine.EDrawDebugTrace'"
$MOVEMENT_MODE = "/Script/CoreUObject.Enum'/Script/Engine.EMovementMode'"
$HANG_MONTAGE = '/Game/ThirdPerson/Blueprints/Plaey/Anim/AM_LedgeHang_Handmade.AM_LedgeHang_Handmade'
$CLIMB_MONTAGE = '/Game/ThirdPerson/Blueprints/Plaey/Anim/AM_LedgeClimb_Handmade.AM_LedgeClimb_Handmade'

# cm. The wall must be within WALL_REACH ahead of the capsule's center; the ledge top is searched for from LEDGE_ABOVE
# above the center down to LEDGE_BELOW below it (the feet are 90 below), just past the wall face.
$WALL_REACH = '100.000000'
$LEDGE_ABOVE = '125.000000'
$LEDGE_BELOW = '-90.000000'
$INTO_WALL = '20.000000'
# Hanging: the capsule's center this far out from the wall face (the round body is wider than the capsule), and this far
# above the ledge top, which puts the raised hands (62 cm above the feet, the mesh 89 below the center) at the edge.
$HANG_OUT = '46.000000'
$HANG_UP = '27.000000'
# Climbing: up to standing height (the capsule's half height plus a little) above the ledge, then this far onto it.
$STAND_UP = '92.000000'
$ONTO_LEDGE = '45.000000'

$script:objectDefaults = @{}
function Set-ObjectDefault($node, $pinName, $path) { $script:objectDefaults[(Get-Pin $node $pinName).Id] = $path }

function New-Math($operation, $a, $b, $x, $y) {
  # a (op) b on doubles; a and b are either @(node, pin) or a constant string.
  $node = New-Operator $operation "${operation}_DoubleDouble" 'real' 'double' 'real' $x $y
  (Get-Pin $node 'ReturnValue').Sub = 'double'
  foreach ($pair in @(@('A', $a), @('B', $b))) {
    if ($pair[1] -is [string]) { (Get-Pin $node $pair[0]).Default = $pair[1] } else { Connect $pair[1][0] $pair[1][1] $node $pair[0] }
  }
  return $node
}

function New-Break($x, $y) {
  $node = New-Call $MATH 'BreakVector' $true $x $y
  Add-Pin $node 'InVec' 'in' 'struct' '' $VECTOR
  Add-Pin $node 'X' 'out' 'real' 'double'
  Add-Pin $node 'Y' 'out' 'real' 'double'
  Add-Pin $node 'Z' 'out' 'real' 'double'
  return $node
}

function New-Make($xs, $ys, $zs, $x, $y) {
  $node = New-Call $MATH 'MakeVector' $true $x $y
  foreach ($pair in @(@('X', $xs), @('Y', $ys), @('Z', $zs))) {
    Add-Pin $node $pair[0] 'in' 'real' 'double' $null '0.0'
    if ($pair[1] -is [string]) { (Get-Pin $node $pair[0]).Default = $pair[1] } else { Connect $pair[1][0] $pair[1][1] $node $pair[0] }
  }
  Add-Pin $node 'ReturnValue' 'out' 'struct' '' $VECTOR
  return $node
}

function New-Trace($x, $y) {
  # "Line Trace By Channel" is only the display name; the function itself is LineTraceSingle.
  $node = New-Call $SYSTEM 'LineTraceSingle' $false $x $y
  Add-Pin $node 'Start' 'in' 'struct' '' $VECTOR
  Add-Pin $node 'End' 'in' 'struct' '' $VECTOR
  Add-Pin $node 'TraceChannel' 'in' 'byte' '' $TRACE_ENUM 'TraceTypeQuery1'
  Add-Pin $node 'bTraceComplex' 'in' 'bool' '' $null 'false'
  Add-Pin $node 'ActorsToIgnore' 'in' 'object' '' $ACTOR $null 'Array'
  Add-Pin $node 'DrawDebugType' 'in' 'byte' '' $DEBUG_ENUM 'None'
  Add-Pin $node 'OutHit' 'out' 'struct' '' $HIT_STRUCT
  Add-Pin $node 'bIgnoreSelf' 'in' 'bool' '' $null 'true'
  Add-Pin $node 'ReturnValue' 'out' 'bool'
  return $node
}

function New-HitInfo($trace, $x, $y) {
  $node = New-Call $STATICS 'BreakHitResult' $true $x $y
  Add-Pin $node 'Hit' 'in' 'struct' '' $HIT_STRUCT
  Add-Pin $node 'Distance' 'out' 'real' 'float'
  Add-Pin $node 'Location' 'out' 'struct' '' $VECTOR
  Add-Pin $node 'ImpactNormal' 'out' 'struct' '' $VECTOR
  Connect $trace 'OutHit' $node 'Hit'
  return $node
}

function New-Montage($func, $path, $x, $y) {
  $node = New-Call $null $func $false $x $y
  Add-Pin $node 'AnimMontage' 'in' 'object' '' $MONTAGE_CLASS
  if ($func -eq 'PlayAnimMontage') {
    Add-Pin $node 'InPlayRate' 'in' 'real' 'float' $null '1.000000'
    Add-Pin $node 'StartSectionName' 'in' 'name' '' $null 'None'
    Add-Pin $node 'ReturnValue' 'out' 'real' 'float'
  }
  Set-ObjectDefault $node 'AnimMontage' $path
  return $node
}

function New-Lift($target, $seconds, $easeOut, $easeIn, $x, $y) {
  $node = New-Node '/Script/BlueprintGraph.K2Node_CallFunction' @("FunctionReference=(MemberParent=`"$SYSTEM`",MemberName=`"MoveComponentTo`")") $x $y
  Add-Pin $node 'Move' 'in' 'exec'
  Add-Pin $node 'Stop' 'in' 'exec'
  Add-Pin $node 'Return' 'in' 'exec'
  Add-Pin $node 'then' 'out' 'exec'
  Add-Pin $node 'Component' 'in' 'object' '' $SCENE_CLASS
  Add-Pin $node 'TargetRelativeLocation' 'in' 'struct' '' $VECTOR
  Add-Pin $node 'TargetRelativeRotation' 'in' 'struct' '' $ROTATOR_STRUCT
  Add-Pin $node 'bEaseOut' 'in' 'bool' '' $null $easeOut
  Add-Pin $node 'bEaseIn' 'in' 'bool' '' $null $easeIn
  Add-Pin $node 'OverTime' 'in' 'real' 'float' $null $seconds
  # The capsule is the actor's root, so its "relative" location is the world location.
  $capsule = New-VarGet 'CapsuleComponent' $null 'object' '' $CAPSULE_CLASS ($x - 250) ($y + 200)
  Connect $capsule 'CapsuleComponent' $node 'Component'
  $targetGet = New-VarGet $target $null 'struct' '' $VECTOR ($x - 250) ($y + 330)
  Connect $targetGet $target $node 'TargetRelativeLocation'
  $facing = New-Call $null 'K2_GetActorRotation' $true ($x - 250) ($y + 460)
  Add-Pin $facing 'ReturnValue' 'out' 'struct' '' $ROTATOR_STRUCT
  Connect $facing 'ReturnValue' $node 'TargetRelativeRotation'
  return $node
}

$y0 = 6000
# --- Q: only while not already hanging ---------------------------------------------------
$grab = New-Node '/Script/InputBlueprintNodes.K2Node_EnhancedInputAction' @("InputAction=`"/Script/EnhancedInput.InputAction'/Game/Input/Actions/IA_Grab.IA_Grab'`"") 0 $y0
# Triggered fires every frame while Q is held, so holding it grabs the first ledge that comes within reach.
Add-Pin $grab 'Triggered' 'out' 'exec'
$hangingGet = New-VarGet 'IsHanging' $null 'bool' '' $null 150 ($y0 + 200)
$notHanging = New-Branch 300 $y0
Connect $grab 'Triggered' $notHanging 'execute'
Connect $hangingGet 'IsHanging' $notHanging 'Condition'

# --- Is there a wall straight ahead? ------------------------------------------------------
$here = New-Call $null 'K2_GetActorLocation' $true 300 ($y0 + 400)
Add-Pin $here 'ReturnValue' 'out' 'struct' '' $VECTOR
$herePart = New-Break 550 ($y0 + 400)
Connect $here 'ReturnValue' $herePart 'InVec'
$ahead = New-Call $null 'GetActorForwardVector' $true 300 ($y0 + 600)
Add-Pin $ahead 'ReturnValue' 'out' 'struct' '' $VECTOR
$aheadPart = New-Break 550 ($y0 + 600)
Connect $ahead 'ReturnValue' $aheadPart 'InVec'
$reachX = New-Math 'Add' @($herePart, 'X') @((New-Math 'Multiply' @($aheadPart, 'X') $WALL_REACH 800 ($y0 + 650)), 'ReturnValue') 1000 ($y0 + 450)
$reachY = New-Math 'Add' @($herePart, 'Y') @((New-Math 'Multiply' @($aheadPart, 'Y') $WALL_REACH 800 ($y0 + 800)), 'ReturnValue') 1000 ($y0 + 600)
$wallEnd = New-Make @($reachX, 'ReturnValue') @($reachY, 'ReturnValue') @($herePart, 'Z') 1200 ($y0 + 450)
$wallTrace = New-Trace 650 $y0
Connect $notHanging 'else' $wallTrace 'execute'
Connect $here 'ReturnValue' $wallTrace 'Start'
Connect $wallEnd 'ReturnValue' $wallTrace 'End'
$wallFound = New-Branch 1100 $y0
Connect $wallTrace 'then' $wallFound 'execute'
Connect $wallTrace 'ReturnValue' $wallFound 'Condition'
$wall = New-HitInfo $wallTrace 1300 ($y0 + 200)
$wallPoint = New-Break 1550 ($y0 + 200)
Connect $wall 'Location' $wallPoint 'InVec'
$wallNormal = New-Break 1550 ($y0 + 400)
Connect $wall 'ImpactNormal' $wallNormal 'InVec'

# --- A ledge on top of it: look down just past the face -----------------------------------
$probeX = New-Math 'Subtract' @($wallPoint, 'X') @((New-Math 'Multiply' @($wallNormal, 'X') $INTO_WALL 1750 ($y0 + 450)), 'ReturnValue') 1950 ($y0 + 200)
$probeY = New-Math 'Subtract' @($wallPoint, 'Y') @((New-Math 'Multiply' @($wallNormal, 'Y') $INTO_WALL 1750 ($y0 + 600)), 'ReturnValue') 1950 ($y0 + 350)
$topZ = New-Math 'Add' @($herePart, 'Z') $LEDGE_ABOVE 1950 ($y0 + 500)
$bottomZ = New-Math 'Add' @($herePart, 'Z') $LEDGE_BELOW 1950 ($y0 + 650)
$ledgeStart = New-Make @($probeX, 'ReturnValue') @($probeY, 'ReturnValue') @($topZ, 'ReturnValue') 2150 ($y0 + 300)
$ledgeEnd = New-Make @($probeX, 'ReturnValue') @($probeY, 'ReturnValue') @($bottomZ, 'ReturnValue') 2150 ($y0 + 500)
$ledgeTrace = New-Trace 1650 $y0
Connect $wallFound 'then' $ledgeTrace 'execute'
Connect $ledgeStart 'ReturnValue' $ledgeTrace 'Start'
Connect $ledgeEnd 'ReturnValue' $ledgeTrace 'End'
$ledgeFound = New-Branch 2100 $y0
Connect $ledgeTrace 'then' $ledgeFound 'execute'
Connect $ledgeTrace 'ReturnValue' $ledgeFound 'Condition'
$ledge = New-HitInfo $ledgeTrace 2350 ($y0 + 300)
# A hit right at the start means the wall goes on above the search: no ledge within reach.
$outside = New-Operator 'Greater' 'Greater_DoubleDouble' 'real' 'double' 'bool' 2550 ($y0 + 250)
(Get-Pin $outside 'B').Default = '1.000000'
Connect $ledge 'Distance' $outside 'A'
$ledgeReal = New-Branch 2450 $y0
Connect $ledgeFound 'then' $ledgeReal 'execute'
Connect $outside 'ReturnValue' $ledgeReal 'Condition'
$ledgePoint = New-Break 2550 ($y0 + 450)
Connect $ledge 'Location' $ledgePoint 'InVec'

# --- Where to hang, where the climb goes, which way to face -------------------------------
$y1 = $y0 + 1000
$outX = New-Math 'Add' @($wallPoint, 'X') @((New-Math 'Multiply' @($wallNormal, 'X') $HANG_OUT 300 ($y1 + 300)), 'ReturnValue') 550 ($y1 + 300)
$outY = New-Math 'Add' @($wallPoint, 'Y') @((New-Math 'Multiply' @($wallNormal, 'Y') $HANG_OUT 300 ($y1 + 450)), 'ReturnValue') 550 ($y1 + 450)
$onX = New-Math 'Subtract' @($wallPoint, 'X') @((New-Math 'Multiply' @($wallNormal, 'X') $ONTO_LEDGE 300 ($y1 + 600)), 'ReturnValue') 550 ($y1 + 600)
$onY = New-Math 'Subtract' @($wallPoint, 'Y') @((New-Math 'Multiply' @($wallNormal, 'Y') $ONTO_LEDGE 300 ($y1 + 750)), 'ReturnValue') 550 ($y1 + 750)
$hangZ = New-Math 'Add' @($ledgePoint, 'Z') $HANG_UP 550 ($y1 + 900)
$standZ = New-Math 'Add' @($ledgePoint, 'Z') $STAND_UP 550 ($y1 + 1050)
$hangSpot = New-Make @($outX, 'ReturnValue') @($outY, 'ReturnValue') @($hangZ, 'ReturnValue') 800 ($y1 + 300)
$liftSpot = New-Make @($outX, 'ReturnValue') @($outY, 'ReturnValue') @($standZ, 'ReturnValue') 800 ($y1 + 500)
$onSpot = New-Make @($onX, 'ReturnValue') @($onY, 'ReturnValue') @($standZ, 'ReturnValue') 800 ($y1 + 700)
$intoX = New-Math 'Multiply' @($wallNormal, 'X') '-1.000000' 550 ($y1 + 1200)
$intoY = New-Math 'Multiply' @($wallNormal, 'Y') '-1.000000' 550 ($y1 + 1350)
$intoWall = New-Make @($intoX, 'ReturnValue') @($intoY, 'ReturnValue') '0.0' 800 ($y1 + 1200)
$faceWall = New-Call $MATH 'MakeRotFromX' $true 1000 ($y1 + 1200)
Add-Pin $faceWall 'X' 'in' 'struct' '' $VECTOR
Add-Pin $faceWall 'ReturnValue' 'out' 'struct' '' $ROTATOR_STRUCT
Connect $intoWall 'ReturnValue' $faceWall 'X'

$saveLift = New-VarSet 'ClimbLift' $null 'struct' $VECTOR 1000 $y1
Connect $ledgeReal 'then' $saveLift 'execute'
Connect $liftSpot 'ReturnValue' $saveLift 'ClimbLift'
$saveOn = New-VarSet 'ClimbTarget' $null 'struct' $VECTOR 1350 $y1
Connect $saveLift 'then' $saveOn 'execute'
Connect $onSpot 'ReturnValue' $saveOn 'ClimbTarget'

# --- Hang: no movement (so no gravity and no jumping), facing the wall, the hang pose on a loop ---
$movement = New-VarGet 'CharacterMovement' $null 'object' '' $MOVEMENT_CLASS 1600 ($y1 + 300)
$halt = New-Call $MOVEMENT_CLASS 'StopMovementImmediately' $false 1700 $y1
Add-Pin $halt 'self' 'in' 'object' '' $MOVEMENT_CLASS
Connect $movement 'CharacterMovement' $halt 'self'
Connect $saveOn 'then' $halt 'execute'
$noMove = New-Call $MOVEMENT_CLASS 'DisableMovement' $false 2050 $y1
Add-Pin $noMove 'self' 'in' 'object' '' $MOVEMENT_CLASS
Connect $movement 'CharacterMovement' $noMove 'self'
Connect $halt 'then' $noMove 'execute'
$place = New-Call $null 'K2_SetActorLocationAndRotation' $false 2400 $y1
Add-Pin $place 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $place 'NewRotation' 'in' 'struct' '' $ROTATOR_STRUCT
Add-Pin $place 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $place 'SweepHitResult' 'out' 'struct' '' $HIT_STRUCT
Add-Pin $place 'bTeleport' 'in' 'bool' '' $null 'true'
Add-Pin $place 'ReturnValue' 'out' 'bool'
Connect $hangSpot 'ReturnValue' $place 'NewLocation'
Connect $faceWall 'ReturnValue' $place 'NewRotation'
Connect $noMove 'then' $place 'execute'
$setHanging = New-VarSet 'IsHanging' $null 'bool' $null 2750 $y1
(Get-Pin $setHanging 'IsHanging').Default = 'true'
Connect $place 'then' $setHanging 'execute'
$playHang = New-Montage 'PlayAnimMontage' $HANG_MONTAGE 3100 $y1
Connect $setHanging 'then' $playHang 'execute'
$meshGet = New-VarGet 'Mesh' $null 'object' '' $MESH_CLASS 3150 ($y1 + 300)
$animInstance = New-Call $MESH_CLASS 'GetAnimInstance' $true 3350 ($y1 + 300)
Add-Pin $animInstance 'self' 'in' 'object' '' $MESH_CLASS
Add-Pin $animInstance 'ReturnValue' 'out' 'object' '' $ANIM_INSTANCE
Connect $meshGet 'Mesh' $animInstance 'self'
# The montage's one section, "Default", follows itself: it repeats until stopped.
$loop = New-Call $ANIM_INSTANCE 'Montage_SetNextSection' $false 3500 $y1
Add-Pin $loop 'self' 'in' 'object' '' $ANIM_INSTANCE
Add-Pin $loop 'SectionNameToChange' 'in' 'name' '' $null 'Default'
Add-Pin $loop 'NextSection' 'in' 'name' '' $null 'Default'
Add-Pin $loop 'Montage' 'in' 'object' '' $MONTAGE_CLASS
Set-ObjectDefault $loop 'Montage' $HANG_MONTAGE
Connect $animInstance 'ReturnValue' $loop 'self'
Connect $playHang 'then' $loop 'execute'

# --- While hanging: watch IA_Jump every frame ---------------------------------------------
# Raw key checks (WasInputKeyJustPressed) never see presses under Enhanced Input, so read the jump action's current
# value instead: it covers every key mapped to jump. First wait for it to be released (it may still be held from the
# jump that reached the ledge), then for a fresh press.
$y2 = $y1 + 1600
$jumpHeld = New-Node '/Script/InputBlueprintNodes.K2Node_GetInputActionValue' @("InputAction=`"/Script/EnhancedInput.InputAction'/Game/Input/Actions/IA_Jump.IA_Jump'`"") 300 ($y2 + 250)
Add-Pin $jumpHeld 'ActionValue' 'out' 'bool'
$waitRelease = New-Call $SYSTEM 'Delay' $false 300 $y2
Add-Pin $waitRelease 'Duration' 'in' 'real' 'float' $null '0.0'
Connect $loop 'then' $waitRelease 'execute'
$stillHeld = New-Branch 600 $y2
Connect $waitRelease 'then' $stillHeld 'execute'
Connect $jumpHeld 'ActionValue' $stillHeld 'Condition'
Connect $stillHeld 'then' $waitRelease 'execute'
$waitPress = New-Call $SYSTEM 'Delay' $false 850 $y2
Add-Pin $waitPress 'Duration' 'in' 'real' 'float' $null '0.0'
Connect $stillHeld 'else' $waitPress 'execute'
$climbNow = New-Branch 1100 $y2
Connect $waitPress 'then' $climbNow 'execute'
Connect $jumpHeld 'ActionValue' $climbNow 'Condition'
Connect $climbNow 'else' $waitPress 'execute'

# --- Climb: up, then onto the ledge, then walking again -----------------------------------
$cx = 500
$stopHang = New-Montage 'StopAnimMontage' $HANG_MONTAGE (1000 + $cx) $y2
Connect $climbNow 'then' $stopHang 'execute'
$playClimb = New-Montage 'PlayAnimMontage' $CLIMB_MONTAGE (1350 + $cx) $y2
Connect $stopHang 'then' $playClimb 'execute'
$up = New-Lift 'ClimbLift' '0.250000' 'true' 'false' (1950 + $cx) $y2
Connect $playClimb 'then' $up 'Move'
$over = New-Lift 'ClimbTarget' '0.200000' 'true' 'true' (2550 + $cx) $y2
Connect $up 'then' $over 'Move'
$walk = New-Call $MOVEMENT_CLASS 'SetMovementMode' $false (2900 + $cx) $y2
Add-Pin $walk 'self' 'in' 'object' '' $MOVEMENT_CLASS
Add-Pin $walk 'NewMovementMode' 'in' 'byte' '' $MOVEMENT_MODE 'MOVE_Walking'
Add-Pin $walk 'NewCustomMode' 'in' 'byte' '' $null '0'
$walkMovement = New-VarGet 'CharacterMovement' $null 'object' '' $MOVEMENT_CLASS (2850 + $cx) ($y2 + 200)
Connect $walkMovement 'CharacterMovement' $walk 'self'
Connect $over 'then' $walk 'execute'
# The jump press that started the climb must not turn into a jump once walking again.
$noJump = New-Call $null 'StopJumping' $false (3250 + $cx) $y2
Connect $walk 'then' $noJump 'execute'
$done = New-VarSet 'IsHanging' $null 'bool' $null (3550 + $cx) $y2
(Get-Pin $done 'IsHanging').Default = 'false'
Connect $noJump 'then' $done 'execute'

$sb = [System.Text.StringBuilder]::new()
foreach ($n in $script:nodes) {
  [void]$sb.AppendLine("Begin Object Class=$($n.Class) Name=`"$($n.Name)`"")
  foreach ($prop in $n.Props) { [void]$sb.AppendLine("   $prop") }
  [void]$sb.AppendLine("   NodePosX=$($n.X)")
  [void]$sb.AppendLine("   NodePosY=$($n.Y)")
  [void]$sb.AppendLine("   NodeGuid=$([guid]::NewGuid().ToString('N').ToUpper())")
  foreach ($p in $n.Pins) {
    $line = Format-Pin $p
    if ($script:objectDefaults.ContainsKey($p.Id)) { $line = $line -replace 'PersistentGuid=', "DefaultObject=`"$($script:objectDefaults[$p.Id])`",PersistentGuid=" }
    # BreakHitResult takes its Hit as a const reference; a by-value pin loses its link when the node is rebuilt.
    if ($p.Name -eq 'Hit' -and $p.Dir -eq 'in') { $line = $line -replace 'bIsReference=False,PinType.bIsConst=False', 'bIsReference=True,PinType.bIsConst=True' }
    [void]$sb.AppendLine($line)
  }
  [void]$sb.AppendLine('End Object')
}
$text = $sb.ToString()
if ($text.Contains('@{')) { throw 'A node object leaked into a pin or reference (variable name collision)' }
$names = [regex]::Matches($text, '(?m)^Begin Object Class=\S+ Name="(\w+)"') | ForEach-Object { $_.Groups[1].Value }
foreach ($m in [regex]::Matches($text, 'LinkedTo=\(([^)]*)\)')) {
  foreach ($link in ($m.Groups[1].Value -split ',' | Where-Object { $_ })) {
    if ($names -notcontains ($link -split ' ')[0]) { throw "Dangling link: $link" }
  }
}
foreach ($n in $script:nodes) {
  foreach ($p in $n.Pins) {
    if ($p.Cat -eq 'exec' -and $p.Dir -eq 'out' -and $p.Links.Count -gt 1) { throw "Exec output with several links: $($n.Name).$($p.Name)" }
  }
}
[IO.File]::WriteAllText((Join-Path $OutDir 'LedgeGrab_Character.txt'), $text, [Text.UTF8Encoding]::new($false))
"Generated $($script:nodes.Count) nodes"
