param([string]$OutDir)
# Generates the whole Ctrl+V-pasteable Event Graph of BP_BirdcageDoor_Blender: the door opens near the player, and walking
# up to the open door warps the player, cage and all, to Destination. setup_birdcage_warp.py adds the variables and components.

# Reuse the node helpers (constants + functions) from the height BGM generator.
$helperFile = (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_height_bgm.ps1')
$helpers = Get-Content -LiteralPath $helperFile -Encoding UTF8 | Select-Object -Skip 3 -First 124
. ([ScriptBlock]::Create(($helpers -join "`n")))

$SCENE_CLASS = "/Script/CoreUObject.Class'/Script/Engine.SceneComponent'"
$PRIMITIVE_CLASS = "/Script/CoreUObject.Class'/Script/Engine.PrimitiveComponent'"
$SPHERE_CLASS = "/Script/CoreUObject.Class'/Script/Engine.SphereComponent'"
$BOX_CLASS = "/Script/CoreUObject.Class'/Script/Engine.BoxComponent'"
$SKELETAL_CLASS = "/Script/CoreUObject.Class'/Script/Engine.SkeletalMeshComponent'"
$CHARACTER = "/Script/CoreUObject.Class'/Script/Engine.Character'"
$CONTROLLER_CLASS = "/Script/CoreUObject.Class'/Script/Engine.PlayerController'"
$CAMERA_CLASS = "/Script/CoreUObject.Class'/Script/Engine.PlayerCameraManager'"
$MOVEMENT_CLASS = "/Script/CoreUObject.Class'/Script/Engine.CharacterMovementComponent'"
$ROTATOR_STRUCT = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Rotator'"
$COLOR_STRUCT = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.LinearColor'"
$HIT_STRUCT = "/Script/CoreUObject.ScriptStruct'/Script/Engine.HitResult'"
$ATTACH_RULE = "/Script/CoreUObject.Enum'/Script/Engine.EAttachmentRule'"
$DETACH_RULE = "/Script/CoreUObject.Enum'/Script/Engine.EDetachmentRule'"
$MOVEMENT_MODE = "/Script/CoreUObject.Enum'/Script/Engine.EMovementMode'"
$BLACK = '(R=0.000000,G=0.000000,B=0.000000,A=1.000000)'

$DOOR_SECONDS = '1.000000'
# The door counts as open from here on (the animation is 1 second long).
$DOOR_OPEN_POSITION = '0.950000'
$WAIT_SECONDS = '0.100000'
$RISE_HEIGHT = '0.000000,0.000000,300.000000'
$RISE_SECONDS = '2.000000'
$DESCEND_SECONDS = '2.000000'
$FADE_SECONDS = '1.500000'
# How long the cage stays after the player steps out, then one fade: 40 steps of 0.03 s is about 1.2 s.
$LINGER_SECONDS = '1.000000'
$FADE_STEP = '0.025000'
$FADE_STEP_SECONDS = '0.030000'

function New-BoundEvent($component, $signature, $x, $y) {
  $node = New-Node '/Script/BlueprintGraph.K2Node_ComponentBoundEvent' @(
    "DelegatePropertyName=`"OnComponent$signature`"",
    "DelegateOwnerClass=`"$PRIMITIVE_CLASS`"",
    "ComponentPropertyName=`"$component`"",
    "EventReference=(MemberParent=`"/Script/CoreUObject.Package'/Script/Engine'`",MemberName=`"Component${signature}Signature__DelegateSignature`")",
    'bInternalEvent=True',
    "CustomFunctionName=`"BndEvt__BP_BirdcageDoor_Blender_${component}_K2Node_ComponentBoundEvent_0_Component${signature}Signature__DelegateSignature`""
  ) $x $y
  Add-Pin $node 'then' 'out' 'exec'
  return $node
}

function New-PlayerGet($x, $y) {
  $node = New-Call $STATICS 'GetPlayerCharacter' $true $x $y
  Add-Pin $node 'PlayerIndex' 'in' 'int' '' $null '0'
  Add-Pin $node 'ReturnValue' 'out' 'object' '' $CHARACTER
  return $node
}

function New-IsPlayerInside($triggerName, $triggerClass, $x, $y) {
  $playerNode = New-PlayerGet $x ($y + 150)
  $triggerGet = New-VarGet $triggerName $null 'object' '' $triggerClass $x $y
  $inside = New-Call $PRIMITIVE_CLASS 'IsOverlappingActor' $true ($x + 300) $y
  Add-Pin $inside 'self' 'in' 'object' '' $PRIMITIVE_CLASS
  Add-Pin $inside 'Other' 'in' 'object' '' $ACTOR
  Add-Pin $inside 'ReturnValue' 'out' 'bool'
  Connect $triggerGet $triggerName $inside 'self'
  Connect $playerNode 'ReturnValue' $inside 'Other'
  return $inside
}

function New-SetFlag($name, $value, $x, $y) {
  $node = New-VarSet $name $null 'bool' $null $x $y
  (Get-Pin $node $name).Default = $value
  return $node
}

function New-Wait($seconds, $x, $y) {
  $node = New-Call $SYSTEM 'Delay' $false $x $y
  Add-Pin $node 'Duration' 'in' 'real' 'float' $null $seconds
  return $node
}

function New-MoveCage($location, $seconds, $easeOutValue, $easeInValue, $x, $y) {
  $node = New-Node '/Script/BlueprintGraph.K2Node_CallFunction' @("FunctionReference=(MemberParent=`"$SYSTEM`",MemberName=`"MoveComponentTo`")") $x $y
  Add-Pin $node 'Move' 'in' 'exec'
  Add-Pin $node 'Stop' 'in' 'exec'
  Add-Pin $node 'Return' 'in' 'exec'
  Add-Pin $node 'then' 'out' 'exec'
  Add-Pin $node 'Component' 'in' 'object' '' $SCENE_CLASS
  Add-Pin $node 'TargetRelativeLocation' 'in' 'struct' '' $VECTOR $location
  Add-Pin $node 'TargetRelativeRotation' 'in' 'struct' '' $ROTATOR_STRUCT '0.000000,0.000000,0.000000'
  Add-Pin $node 'bEaseOut' 'in' 'bool' '' $null $easeOutValue
  Add-Pin $node 'bEaseIn' 'in' 'bool' '' $null $easeInValue
  Add-Pin $node 'OverTime' 'in' 'real' 'float' $null $seconds
  return $node
}

function New-Fade($from, $to, $hold, $cameraNode, $x, $y) {
  $node = New-Call $CAMERA_CLASS 'StartCameraFade' $false $x $y
  Add-Pin $node 'self' 'in' 'object' '' $CAMERA_CLASS
  Add-Pin $node 'FromAlpha' 'in' 'real' 'float' $null $from
  Add-Pin $node 'ToAlpha' 'in' 'real' 'float' $null $to
  Add-Pin $node 'Duration' 'in' 'real' 'float' $null $FADE_SECONDS
  Add-Pin $node 'Color' 'in' 'struct' '' $COLOR_STRUCT $BLACK
  Add-Pin $node 'bShouldFadeAudio' 'in' 'bool' '' $null 'false'
  Add-Pin $node 'bHoldWhenFinished' 'in' 'bool' '' $null $hold
  Connect $cameraNode 'ReturnValue' $node 'self'
  return $node
}

function New-PlayDoor($rate, $x, $y) {
  $setRate = New-Call $SKELETAL_CLASS 'SetPlayRate' $false $x $y
  Add-Pin $setRate 'self' 'in' 'object' '' $SKELETAL_CLASS
  Add-Pin $setRate 'Rate' 'in' 'real' 'float' $null $rate
  $play = New-Call $SKELETAL_CLASS 'Play' $false ($x + 350) $y
  Add-Pin $play 'self' 'in' 'object' '' $SKELETAL_CLASS
  Add-Pin $play 'bLooping' 'in' 'bool' '' $null 'false'
  Connect $setRate 'then' $play 'execute'
  return @($setRate, $play)
}

# --- Door near the player: left alone while a warp is running ---------------------------
$doorBegin = New-BoundEvent 'Trigger' 'BeginOverlap' 0 0
$doorEnd = New-BoundEvent 'Trigger' 'EndOverlap' 0 200
$warpingGet = New-VarGet 'IsWarping' $null 'bool' '' $null 300 300
$doorBranch = New-Branch 400 100
Connect $doorBegin 'then' $doorBranch 'execute'
Connect $doorEnd 'then' $doorBranch 'execute'
Connect $warpingGet 'IsWarping' $doorBranch 'Condition'
$insideSphere = New-IsPlayerInside 'Trigger' $SPHERE_CLASS 400 400
$rateChoice = New-Call $MATH 'SelectFloat' $true 1000 400
Add-Pin $rateChoice 'A' 'in' 'real' 'double' $null '1.000000'
Add-Pin $rateChoice 'B' 'in' 'real' 'double' $null '-1.000000'
Add-Pin $rateChoice 'bPickA' 'in' 'bool'
Add-Pin $rateChoice 'ReturnValue' 'out' 'real' 'double'
Connect $insideSphere 'ReturnValue' $rateChoice 'bPickA'
$doorPlay = New-PlayDoor '1.0' 1300 100
Connect $doorBranch 'else' $doorPlay[0] 'execute'
Connect $rateChoice 'ReturnValue' $doorPlay[0] 'Rate'
$sphereCage = New-VarGet 'Cage' $null 'object' '' $SKELETAL_CLASS 1150 250
Connect $sphereCage 'Cage' $doorPlay[0] 'self'
Connect $sphereCage 'Cage' $doorPlay[1] 'self'

# --- At the door: wait until it is fully open, as long as the player stays ----------------
$rowY = 800
$enter = New-BoundEvent 'EnterTrigger' 'BeginOverlap' 0 $rowY
$usedGet = New-VarGet 'WarpUsed' $null 'bool' '' $null 300 ($rowY + 200)
$usedBranch = New-Branch 400 $rowY
Connect $enter 'then' $usedBranch 'execute'
Connect $usedGet 'WarpUsed' $usedBranch 'Condition'
$destinationGet = New-VarGet 'Destination' $null 'object' '' $ACTOR 600 ($rowY + 200)
$destinationValid = New-IsValid 800 ($rowY + 200)
Connect $destinationGet 'Destination' $destinationValid 'Object'
$validBranch = New-Branch 800 $rowY
Connect $usedBranch 'else' $validBranch 'execute'
Connect $destinationValid 'ReturnValue' $validBranch 'Condition'

$cageGet = New-VarGet 'Cage' $null 'object' '' $SKELETAL_CLASS 1000 ($rowY + 200)
$position = New-Call $SKELETAL_CLASS 'GetPosition' $true 1200 ($rowY + 200)
Add-Pin $position 'self' 'in' 'object' '' $SKELETAL_CLASS
Add-Pin $position 'ReturnValue' 'out' 'real' 'float'
Connect $cageGet 'Cage' $position 'self'
$isOpen = New-Operator 'GreaterEqual' 'GreaterEqual_DoubleDouble' 'real' 'double' 'bool' 1450 ($rowY + 200)
(Get-Pin $isOpen 'B').Default = $DOOR_OPEN_POSITION
Connect $position 'ReturnValue' $isOpen 'A'
$openBranch = New-Branch 1200 $rowY
Connect $validBranch 'then' $openBranch 'execute'
Connect $isOpen 'ReturnValue' $openBranch 'Condition'

$insideBox = New-IsPlayerInside 'EnterTrigger' $BOX_CLASS 1200 ($rowY + 400)
$stayBranch = New-Branch 1700 ($rowY + 400)
Connect $openBranch 'else' $stayBranch 'execute'
Connect $insideBox 'ReturnValue' $stayBranch 'Condition'
# Back through the WarpUsed check: this loop and a new overlap must not both start a warp.
$retry = New-Wait $WAIT_SECONDS 2000 ($rowY + 400)
Connect $stayBranch 'then' $retry 'execute'
Connect $retry 'then' $usedBranch 'execute'

# --- Warp: the player vanishes and rides along, attached to the cage -----------------------
$rowY = 1600
$player = New-PlayerGet 0 ($rowY + 500)
$controller = New-Call $STATICS 'GetPlayerController' $true 0 ($rowY + 700)
Add-Pin $controller 'PlayerIndex' 'in' 'int' '' $null '0'
Add-Pin $controller 'ReturnValue' 'out' 'object' '' $CONTROLLER_CLASS
$camera = New-Call $STATICS 'GetPlayerCameraManager' $true 0 ($rowY + 900)
Add-Pin $camera 'PlayerIndex' 'in' 'int' '' $null '0'
Add-Pin $camera 'ReturnValue' 'out' 'object' '' $CAMERA_CLASS
$capsuleGet = New-VarGet 'CapsuleComponent' $CHARACTER 'object' '' "/Script/CoreUObject.Class'/Script/Engine.CapsuleComponent'" 300 ($rowY + 500)
Connect $player 'ReturnValue' $capsuleGet 'self'
$movementGet = New-VarGet 'CharacterMovement' $CHARACTER 'object' '' $MOVEMENT_CLASS 300 ($rowY + 700)
Connect $player 'ReturnValue' $movementGet 'self'
$warpCage = New-VarGet 'Cage' $null 'object' '' $SKELETAL_CLASS 300 ($rowY + 900)

function New-SetInput($func, $x, $y) {
  $node = New-Call $ACTOR $func $false $x $y
  Add-Pin $node 'self' 'in' 'object' '' $ACTOR
  Add-Pin $node 'PlayerController' 'in' 'object' '' $CONTROLLER_CLASS
  Connect $player 'ReturnValue' $node 'self'
  Connect $controller 'ReturnValue' $node 'PlayerController'
  return $node
}

# Through the root with children, so the halo on the player's head vanishes as well.
function New-SetShown($value, $x, $y) {
  $node = New-Call $SCENE_CLASS 'SetVisibility' $false $x $y
  Add-Pin $node 'self' 'in' 'object' '' $SCENE_CLASS
  Add-Pin $node 'bNewVisibility' 'in' 'bool' '' $null $value
  Add-Pin $node 'bPropagateToChildren' 'in' 'bool' '' $null 'true'
  Connect $capsuleGet 'CapsuleComponent' $node 'self'
  return $node
}

function New-SetSolid($value, $x, $y) {
  $node = New-Call $ACTOR 'SetActorEnableCollision' $false $x $y
  Add-Pin $node 'self' 'in' 'object' '' $ACTOR
  Add-Pin $node 'bNewActorEnableCollision' 'in' 'bool' '' $null $value
  Connect $player 'ReturnValue' $node 'self'
  return $node
}

$setUsed = New-SetFlag 'WarpUsed' 'true' 700 $rowY
$setWarping = New-SetFlag 'IsWarping' 'true' 1050 $rowY
$stopInput = New-SetInput 'DisableInput' 1400 $rowY
$hidePlayer = New-SetShown 'false' 1750 $rowY
$passThrough = New-SetSolid 'false' 2100 $rowY
$halt = New-Call $MOVEMENT_CLASS 'StopMovementImmediately' $false 2450 $rowY
Add-Pin $halt 'self' 'in' 'object' '' $MOVEMENT_CLASS
Connect $movementGet 'CharacterMovement' $halt 'self'
$noMove = New-Call $MOVEMENT_CLASS 'DisableMovement' $false 2800 $rowY
Add-Pin $noMove 'self' 'in' 'object' '' $MOVEMENT_CLASS
Connect $movementGet 'CharacterMovement' $noMove 'self'
$attach = New-Call $ACTOR 'K2_AttachToComponent' $false 3150 $rowY
Add-Pin $attach 'self' 'in' 'object' '' $ACTOR
Add-Pin $attach 'Parent' 'in' 'object' '' $SCENE_CLASS
Add-Pin $attach 'SocketName' 'in' 'name' '' $null 'None'
Add-Pin $attach 'LocationRule' 'in' 'byte' '' $ATTACH_RULE 'KeepWorld'
Add-Pin $attach 'RotationRule' 'in' 'byte' '' $ATTACH_RULE 'KeepWorld'
Add-Pin $attach 'ScaleRule' 'in' 'byte' '' $ATTACH_RULE 'KeepWorld'
Add-Pin $attach 'bWeldSimulatedBodies' 'in' 'bool' '' $null 'false'
Add-Pin $attach 'ReturnValue' 'out' 'bool'
Connect $player 'ReturnValue' $attach 'self'
Connect $warpCage 'Cage' $attach 'Parent'
Connect $openBranch 'then' $setUsed 'execute'
Connect $setUsed 'then' $setWarping 'execute'
Connect $setWarping 'then' $stopInput 'execute'
Connect $stopInput 'then' $hidePlayer 'execute'
Connect $hidePlayer 'then' $passThrough 'execute'
Connect $passThrough 'then' $halt 'execute'
Connect $halt 'then' $noMove 'execute'
Connect $noMove 'then' $attach 'execute'

# --- Door closes, the cage rises while the screen goes black ------------------------------
$rowY = 2700
$closeDoor = New-PlayDoor '-1.0' 700 $rowY
Connect $attach 'then' $closeDoor[0] 'execute'
Connect $warpCage 'Cage' $closeDoor[0] 'self'
Connect $warpCage 'Cage' $closeDoor[1] 'self'
$closeWait = New-Wait $DOOR_SECONDS 1450 $rowY
Connect $closeDoor[1] 'then' $closeWait 'execute'
$fadeOut = New-Fade '0.0' '1.0' 'true' $camera 1800 $rowY
Connect $closeWait 'then' $fadeOut 'execute'
$rise = New-MoveCage $RISE_HEIGHT $RISE_SECONDS 'false' 'true' 2200 $rowY
Connect $warpCage 'Cage' $rise 'Component'
Connect $fadeOut 'then' $rise 'Move'

# --- In the dark: jump to the destination. The cage stays raised, so it arrives above it ------
$targetLocation = New-Call $ACTOR 'K2_GetActorLocation' $true 2700 ($rowY + 300)
Add-Pin $targetLocation 'self' 'in' 'object' '' $ACTOR
Add-Pin $targetLocation 'ReturnValue' 'out' 'struct' '' $VECTOR
$targetRotation = New-Call $ACTOR 'K2_GetActorRotation' $true 2700 ($rowY + 500)
Add-Pin $targetRotation 'self' 'in' 'object' '' $ACTOR
Add-Pin $targetRotation 'ReturnValue' 'out' 'struct' '' $ROTATOR_STRUCT
$warpDestination = New-VarGet 'Destination' $null 'object' '' $ACTOR 2450 ($rowY + 400)
Connect $warpDestination 'Destination' $targetLocation 'self'
Connect $warpDestination 'Destination' $targetRotation 'self'
$jump = New-Call $null 'K2_SetActorLocationAndRotation' $false 3000 $rowY
Add-Pin $jump 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $jump 'NewRotation' 'in' 'struct' '' $ROTATOR_STRUCT
Add-Pin $jump 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $jump 'SweepHitResult' 'out' 'struct' '' $HIT_STRUCT
Add-Pin $jump 'bTeleport' 'in' 'bool' '' $null 'true'
Add-Pin $jump 'ReturnValue' 'out' 'bool'
Connect $targetLocation 'ReturnValue' $jump 'NewLocation'
Connect $targetRotation 'ReturnValue' $jump 'NewRotation'
Connect $rise 'then' $jump 'execute'

# --- The screen comes back while the cage settles, the door opens, the player steps out ------
$rowY = 3400
$fadeIn = New-Fade '1.0' '0.0' 'false' $camera 700 $rowY
Connect $jump 'then' $fadeIn 'execute'
$descend = New-MoveCage '0.000000,0.000000,0.000000' $DESCEND_SECONDS 'true' 'false' 1100 $rowY
Connect $warpCage 'Cage' $descend 'Component'
Connect $fadeIn 'then' $descend 'Move'
$openDoor = New-PlayDoor '1.0' 1600 $rowY
Connect $descend 'then' $openDoor[0] 'execute'
Connect $warpCage 'Cage' $openDoor[0] 'self'
Connect $warpCage 'Cage' $openDoor[1] 'self'
$openWait = New-Wait $DOOR_SECONDS 2350 $rowY
Connect $openDoor[1] 'then' $openWait 'execute'

$rowY = 4000
$detach = New-Call $ACTOR 'K2_DetachFromActor' $false 700 $rowY
Add-Pin $detach 'self' 'in' 'object' '' $ACTOR
Add-Pin $detach 'LocationRule' 'in' 'byte' '' $DETACH_RULE 'KeepWorld'
Add-Pin $detach 'RotationRule' 'in' 'byte' '' $DETACH_RULE 'KeepWorld'
Add-Pin $detach 'ScaleRule' 'in' 'byte' '' $DETACH_RULE 'KeepWorld'
Connect $player 'ReturnValue' $detach 'self'
Connect $openWait 'then' $detach 'execute'
$exitGet = New-VarGet 'ExitPoint' $null 'object' '' $SCENE_CLASS 800 ($rowY + 300)
$exitLocation = New-Call $SCENE_CLASS 'K2_GetComponentLocation' $true 1000 ($rowY + 300)
Add-Pin $exitLocation 'self' 'in' 'object' '' $SCENE_CLASS
Add-Pin $exitLocation 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $exitGet 'ExitPoint' $exitLocation 'self'
$placePlayer = New-Call $ACTOR 'K2_SetActorLocation' $false 1050 $rowY
Add-Pin $placePlayer 'self' 'in' 'object' '' $ACTOR
Add-Pin $placePlayer 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $placePlayer 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $placePlayer 'SweepHitResult' 'out' 'struct' '' $HIT_STRUCT
Add-Pin $placePlayer 'bTeleport' 'in' 'bool' '' $null 'true'
Add-Pin $placePlayer 'ReturnValue' 'out' 'bool'
Connect $player 'ReturnValue' $placePlayer 'self'
Connect $exitLocation 'ReturnValue' $placePlayer 'NewLocation'
Connect $detach 'then' $placePlayer 'execute'
$showPlayer = New-SetShown 'true' 1450 $rowY
Connect $placePlayer 'then' $showPlayer 'execute'
$solid = New-SetSolid 'true' 1800 $rowY
Connect $showPlayer 'then' $solid 'execute'
$walk = New-Call $MOVEMENT_CLASS 'SetMovementMode' $false 2150 $rowY
Add-Pin $walk 'self' 'in' 'object' '' $MOVEMENT_CLASS
Add-Pin $walk 'NewMovementMode' 'in' 'byte' '' $MOVEMENT_MODE 'MOVE_Walking'
Add-Pin $walk 'NewCustomMode' 'in' 'byte' '' $null '0'
Connect $movementGet 'CharacterMovement' $walk 'self'
Connect $solid 'then' $walk 'execute'
$giveInput = New-SetInput 'EnableInput' 2500 $rowY
Connect $walk 'then' $giveInput 'execute'

# --- The player is out: the cage fades away, goes home with its door shut and fades back in, ready again ---
function New-FadeLoop($startValue, $step, $doneOperation, $doneFunction, $doneValue, $x, $y) {
  $start = New-VarSet 'CageFade' $null 'real' $null $x $y
  (Get-Pin $start 'CageFade').Sub = 'double'
  (Get-Pin $start 'Output_Get').Sub = 'double'
  (Get-Pin $start 'CageFade').Default = $startValue
  $current = New-VarGet 'CageFade' $null 'real' 'double' $null ($x + 300) ($y + 300)
  $change = New-Operator 'Add' 'Add_DoubleDouble' 'real' 'double' 'real' ($x + 500) ($y + 300)
  (Get-Pin $change 'ReturnValue').Sub = 'double'
  (Get-Pin $change 'B').Default = $step
  Connect $current 'CageFade' $change 'A'
  $store = New-VarSet 'CageFade' $null 'real' $null ($x + 350) $y
  (Get-Pin $store 'CageFade').Sub = 'double'
  (Get-Pin $store 'Output_Get').Sub = 'double'
  Connect $change 'ReturnValue' $store 'CageFade'
  $apply = New-Call $SKELETAL_CLASS 'SetScalarParameterValueOnMaterials' $false ($x + 700) $y
  Add-Pin $apply 'self' 'in' 'object' '' $SKELETAL_CLASS
  Add-Pin $apply 'ParameterName' 'in' 'name' '' $null 'Fade'
  Add-Pin $apply 'ParameterValue' 'in' 'real' 'float' $null '1.0'
  Connect $warpCage 'Cage' $apply 'self'
  Connect $store 'Output_Get' $apply 'ParameterValue'
  $finished = New-Operator $doneOperation $doneFunction 'real' 'double' 'bool' ($x + 900) ($y + 300)
  (Get-Pin $finished 'B').Default = $doneValue
  Connect $store 'Output_Get' $finished 'A'
  $doneBranch = New-Branch ($x + 1100) $y
  Connect $finished 'ReturnValue' $doneBranch 'Condition'
  $pause = New-Wait $FADE_STEP_SECONDS ($x + 1400) ($y + 150)
  Connect $start 'then' $store 'execute'
  Connect $store 'then' $apply 'execute'
  Connect $apply 'then' $doneBranch 'execute'
  Connect $doneBranch 'else' $pause 'execute'
  Connect $pause 'then' $store 'execute'
  return @($start, $doneBranch)
}

function New-SetCageSolid($mode, $x, $y) {
  $collisionGet = New-VarGet 'CageCollision' $null 'object' '' "/Script/CoreUObject.Class'/Script/Engine.CapsuleComponent'" ($x - 50) ($y + 200)
  $node = New-Call $PRIMITIVE_CLASS 'SetCollisionEnabled' $false $x $y
  Add-Pin $node 'self' 'in' 'object' '' $PRIMITIVE_CLASS
  Add-Pin $node 'NewType' 'in' 'byte' '' "/Script/CoreUObject.Enum'/Script/Engine.ECollisionEnabled'" $mode
  Connect $collisionGet 'CageCollision' $node 'self'
  return $node
}

$rowY = 4600
$beforeFade = New-Wait $LINGER_SECONDS 700 $rowY
Connect $giveInput 'then' $beforeFade 'execute'
# No invisible wall while the cage fades away and comes back.
$cageGhost = New-SetCageSolid 'NoCollision' 1000 $rowY
Connect $beforeFade 'then' $cageGhost 'execute'
$fadeAway = New-FadeLoop '1.000000' "-$FADE_STEP" 'LessEqual' 'LessEqual_DoubleDouble' '0.000000' 1350 $rowY
Connect $cageGhost 'then' $fadeAway[0] 'execute'

$rowY = 5200
$homeLocationGet = New-VarGet 'HomeLocation' $null 'struct' '' $VECTOR 500 ($rowY + 300)
$homeRotationGet = New-VarGet 'HomeRotation' $null 'struct' '' $ROTATOR_STRUCT 500 ($rowY + 450)
$goHome = New-Call $null 'K2_SetActorLocationAndRotation' $false 700 $rowY
Add-Pin $goHome 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $goHome 'NewRotation' 'in' 'struct' '' $ROTATOR_STRUCT
Add-Pin $goHome 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $goHome 'SweepHitResult' 'out' 'struct' '' $HIT_STRUCT
Add-Pin $goHome 'bTeleport' 'in' 'bool' '' $null 'true'
Add-Pin $goHome 'ReturnValue' 'out' 'bool'
Connect $homeLocationGet 'HomeLocation' $goHome 'NewLocation'
Connect $homeRotationGet 'HomeRotation' $goHome 'NewRotation'
Connect $fadeAway[1] 'then' $goHome 'execute'
# Back to the first frame of the door animation: closed, and already out of sight when it snaps shut.
$shutDoor = New-Call $SKELETAL_CLASS 'SetPosition' $false 1100 $rowY
Add-Pin $shutDoor 'self' 'in' 'object' '' $SKELETAL_CLASS
Add-Pin $shutDoor 'InPos' 'in' 'real' 'float' $null '0.0'
Add-Pin $shutDoor 'bFireNotifies' 'in' 'bool' '' $null 'false'
Connect $warpCage 'Cage' $shutDoor 'self'
Connect $goHome 'then' $shutDoor 'execute'
$fadeBack = New-FadeLoop '0.000000' $FADE_STEP 'GreaterEqual' 'GreaterEqual_DoubleDouble' '1.000000' 1450 $rowY
Connect $shutDoor 'then' $fadeBack[0] 'execute'

$rowY = 5800
$cageSolid = New-SetCageSolid 'QueryAndPhysics' 400 $rowY
Connect $fadeBack[1] 'then' $cageSolid 'execute'
$ready = New-SetFlag 'WarpUsed' 'false' 750 $rowY
Connect $cageSolid 'then' $ready 'execute'
$notWarping = New-SetFlag 'IsWarping' 'false' 1050 $rowY
Connect $ready 'then' $notWarping 'execute'
# Through the normal door logic, in case the player is already waiting beside the cage.
Connect $notWarping 'then' $doorBranch 'execute'

# --- Remember where the cage starts: it comes back here after every warp ---------------------
$rowY = -500
$beginPlay = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$ACTOR`",MemberName=`"ReceiveBeginPlay`")", 'bOverrideFunction=True') 0 $rowY
Add-Pin $beginPlay 'then' 'out' 'exec'
$startLocation = New-Call $null 'K2_GetActorLocation' $true 300 ($rowY + 200)
Add-Pin $startLocation 'ReturnValue' 'out' 'struct' '' $VECTOR
$startRotation = New-Call $null 'K2_GetActorRotation' $true 300 ($rowY + 350)
Add-Pin $startRotation 'ReturnValue' 'out' 'struct' '' $ROTATOR_STRUCT
$saveLocation = New-VarSet 'HomeLocation' $null 'struct' $VECTOR 600 $rowY
$saveRotation = New-VarSet 'HomeRotation' $null 'struct' $ROTATOR_STRUCT 950 $rowY
Connect $beginPlay 'then' $saveLocation 'execute'
Connect $saveLocation 'then' $saveRotation 'execute'
Connect $startLocation 'ReturnValue' $saveLocation 'HomeLocation'
Connect $startRotation 'ReturnValue' $saveRotation 'HomeRotation'

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
if ($text.Contains('@{')) { throw 'A node object leaked into a pin or reference (variable name collision)' }
$names = [regex]::Matches($text, '(?m)^Begin Object Class=\S+ Name="(\w+)"') | ForEach-Object { $_.Groups[1].Value }
foreach ($m in [regex]::Matches($text, 'LinkedTo=\(([^)]*)\)')) {
  foreach ($link in ($m.Groups[1].Value -split ',' | Where-Object { $_ })) {
    if ($names -notcontains ($link -split ' ')[0]) { throw "Dangling link: $link" }
  }
}
# An exec output can hold only one link; pasting two would silently drop one.
foreach ($n in $script:nodes) {
  foreach ($p in $n.Pins) {
    if ($p.Cat -eq 'exec' -and $p.Dir -eq 'out' -and $p.Links.Count -gt 1) { throw "Exec output with several links: $($n.Name).$($p.Name)" }
  }
}
[IO.File]::WriteAllText((Join-Path $OutDir 'BP_BirdcageDoor_Blender_EventGraph.txt'), $text, [Text.UTF8Encoding]::new($false))
"Generated $($script:nodes.Count) nodes"
