param([string]$OutDir)
# Generates the Ctrl+V-pasteable graphs for the checkpoint item: BP_CheckpointFlag (drops into the ground when planted,
# BreakFlag tips the top over and removes it), BP_CheckpointItem (pickup), and the character's part: E plants the
# flag, and the fall check sends the player to the flag once before falling back to the PlayerStart.

$helperFile = (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_height_bgm.ps1')
$helpers = Get-Content -LiteralPath $helperFile -Encoding UTF8 | Select-Object -Skip 3 -First 124
. ([ScriptBlock]::Create(($helpers -join "`n")))

$SCENE_CLASS = "/Script/CoreUObject.Class'/Script/Engine.SceneComponent'"
$PRIMITIVE_CLASS = "/Script/CoreUObject.Class'/Script/Engine.PrimitiveComponent'"
$CAPSULE_CLASS = "/Script/CoreUObject.Class'/Script/Engine.CapsuleComponent'"
$MOVEMENT_CLASS = "/Script/CoreUObject.Class'/Script/Engine.CharacterMovementComponent'"
$MONTAGE_CLASS = "/Script/CoreUObject.Class'/Script/Engine.AnimMontage'"
$ROTATOR_STRUCT = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Rotator'"
$TRANSFORM_STRUCT = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Transform'"
$HIT_STRUCT = "/Script/CoreUObject.ScriptStruct'/Script/Engine.HitResult'"
$SPAWN_COLLISION = "/Script/CoreUObject.Enum'/Script/Engine.ESpawnActorCollisionHandlingMethod'"
$FLAG_CLASS = "/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPerson/Item/Checkpoint/BP_CheckpointFlag.BP_CheckpointFlag_C'"
$CHARACTER_CLASS = "/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter1.BP_ThirdPersonCharacter1_C'"
$ZERO = '0.000000,0.000000,0.000000'

$script:objectDefaults = @{}
function Set-ObjectDefault($node, $pinName, $path) { $script:objectDefaults[(Get-Pin $node $pinName).Id] = $path }

function Write-Graph($fileName) {
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
  [IO.File]::WriteAllText((Join-Path $OutDir $fileName), $text, [Text.UTF8Encoding]::new($false))
  "$fileName : $($script:nodes.Count) nodes"
  $script:nodes.Clear()
  $script:objectDefaults.Clear()
}

function New-Move($component, $location, $rotation, $seconds, $easeOutValue, $easeInValue, $x, $y) {
  $node = New-Node '/Script/BlueprintGraph.K2Node_CallFunction' @("FunctionReference=(MemberParent=`"$SYSTEM`",MemberName=`"MoveComponentTo`")") $x $y
  Add-Pin $node 'Move' 'in' 'exec'
  Add-Pin $node 'Stop' 'in' 'exec'
  Add-Pin $node 'Return' 'in' 'exec'
  Add-Pin $node 'then' 'out' 'exec'
  Add-Pin $node 'Component' 'in' 'object' '' $SCENE_CLASS
  Add-Pin $node 'TargetRelativeLocation' 'in' 'struct' '' $VECTOR $location
  Add-Pin $node 'TargetRelativeRotation' 'in' 'struct' '' $ROTATOR_STRUCT $rotation
  Add-Pin $node 'bEaseOut' 'in' 'bool' '' $null $easeOutValue
  Add-Pin $node 'bEaseIn' 'in' 'bool' '' $null $easeInValue
  Add-Pin $node 'OverTime' 'in' 'real' 'float' $null $seconds
  $get = New-VarGet $component $null 'object' '' $SCENE_CLASS ($x - 250) ($y + 200)
  Connect $get $component $node 'Component'
  return $node
}

function New-Wait($seconds, $x, $y) {
  $node = New-Call $SYSTEM 'Delay' $false $x $y
  Add-Pin $node 'Duration' 'in' 'real' 'float' $null $seconds
  return $node
}

function New-BreakCall($flagGet, $x, $y) {
  $node = New-Node '/Script/BlueprintGraph.K2Node_CallFunction' @("FunctionReference=(MemberParent=`"$FLAG_CLASS`",MemberName=`"BreakFlag`")") $x $y
  Add-Exec $node
  Add-Pin $node 'self' 'in' 'object' '' $FLAG_CLASS
  Connect $flagGet 'ActiveFlag' $node 'self'
  return $node
}

# ======================= BP_CheckpointFlag ===================================================
$script:counter = 100
$begin = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$ACTOR`",MemberName=`"ReceiveBeginPlay`")", 'bOverrideFunction=True') 0 0
Add-Pin $begin 'then' 'out' 'exec'
# In time with MM_PlantFlag_Handmade (30 fps): hidden while the player reaches behind, in the hands in front of the
# chest at frame 6, raised with the hop at frame 9, driven into the ground at frame 12. The flag is spawned where the
# player stands, so Base keeps it a little in front (the player faces +X), out of the body.
$FLAG_SPOT = '45.000000,0.000000,0.000000'
function New-Place($location, $x, $yy) {
  $node = New-Call $SCENE_CLASS 'K2_SetRelativeLocation' $false $x $yy
  Add-Pin $node 'self' 'in' 'object' '' $SCENE_CLASS
  Add-Pin $node 'NewLocation' 'in' 'struct' '' $VECTOR $location
  Add-Pin $node 'bSweep' 'in' 'bool' '' $null 'false'
  Add-Pin $node 'SweepHitResult' 'out' 'struct' '' $HIT_STRUCT
  Add-Pin $node 'bTeleport' 'in' 'bool' '' $null 'true'
  $get = New-VarGet 'Base' $null 'object' '' $SCENE_CLASS ($x - 150) ($yy + 200)
  Connect $get 'Base' $node 'self'
  return $node
}
function New-Size($value, $x, $yy) {
  $node = New-Call $SCENE_CLASS 'SetRelativeScale3D' $false $x $yy
  Add-Pin $node 'self' 'in' 'object' '' $SCENE_CLASS
  Add-Pin $node 'NewScale3D' 'in' 'struct' '' $VECTOR $value
  $get = New-VarGet 'Base' $null 'object' '' $SCENE_CLASS ($x - 150) ($yy + 200)
  Connect $get 'Base' $node 'self'
  return $node
}
$held = New-Place '40.000000,0.000000,45.000000' 300 0
$hidden = New-Size '0.000000,0.000000,0.000000' 650 0
$waitReach = New-Wait '0.200000' 1000 0
$shown = New-Size '1.000000,1.000000,1.000000' 1300 0
$raise = New-Move 'Base' '45.000000,0.000000,80.000000' $ZERO '0.100000' 'true' 'false' 1650 0
$drive = New-Move 'Base' $FLAG_SPOT $ZERO '0.100000' 'false' 'true' 2050 0
Connect $begin 'then' $held 'execute'
Connect $held 'then' $hidden 'execute'
Connect $hidden 'then' $waitReach 'execute'
Connect $waitReach 'then' $shown 'execute'
Connect $shown 'then' $raise 'Move'
Connect $raise 'then' $drive 'Move'

$breakEvent = New-Node '/Script/BlueprintGraph.K2Node_CustomEvent' @('CustomFunctionName="BreakFlag"') 0 600
Add-Pin $breakEvent 'then' 'out' 'exec'
# The top half snaps over sideways; the flag is gone soon after.
$snap = New-Move 'Upper' '0.000000,0.000000,55.000000' '0.000000,0.000000,85.000000' '0.350000' 'false' 'true' 400 600
$linger = New-Wait '0.800000' 800 600
$remove = New-Call $null 'K2_DestroyActor' $false 1150 600
Connect $breakEvent 'then' $snap 'Move'
Connect $snap 'then' $linger 'execute'
Connect $linger 'then' $remove 'execute'
Write-Graph 'BP_CheckpointFlag_EventGraph.txt'

# ======================= BP_CheckpointItem ===================================================
$script:counter = 100
$overlap = New-Node '/Script/BlueprintGraph.K2Node_ComponentBoundEvent' @(
  'DelegatePropertyName="OnComponentBeginOverlap"',
  "DelegateOwnerClass=`"$PRIMITIVE_CLASS`"",
  'ComponentPropertyName="Trigger"',
  "EventReference=(MemberParent=`"/Script/CoreUObject.Package'/Script/Engine'`",MemberName=`"ComponentBeginOverlapSignature__DelegateSignature`")",
  'bInternalEvent=True',
  'CustomFunctionName="BndEvt__BP_CheckpointItem_Trigger_K2Node_ComponentBoundEvent_0_ComponentBeginOverlapSignature__DelegateSignature"'
) 0 0
Add-Pin $overlap 'then' 'out' 'exec'
Add-Pin $overlap 'OtherActor' 'out' 'object' '' $ACTOR
$cast = New-Node '/Script/BlueprintGraph.K2Node_DynamicCast' @("TargetType=`"$CHARACTER_CLASS`"") 300 0
Add-Exec $cast
Add-Pin $cast 'CastFailed' 'out' 'exec'
Add-Pin $cast 'Object' 'in' 'object' '' $OBJECT
Add-Pin $cast 'AsBP Third Person Character 1' 'out' 'object' '' $CHARACTER_CLASS
Add-Pin $cast 'bSuccess' 'out' 'bool'
Connect $overlap 'then' $cast 'execute'
Connect $overlap 'OtherActor' $cast 'Object'
# One at a time: while the player holds one, the pickup stays where it is.
$holding = New-VarGet 'HasFlagItem' $CHARACTER_CLASS 'bool' '' $null 550 250
Connect $cast 'AsBP Third Person Character 1' $holding 'self'
$branch = New-Branch 700 0
Connect $cast 'then' $branch 'execute'
Connect $holding 'HasFlagItem' $branch 'Condition'
$take = New-VarSet 'HasFlagItem' $CHARACTER_CLASS 'bool' $null 1000 0
(Get-Pin $take 'HasFlagItem').Default = 'true'
Connect $cast 'AsBP Third Person Character 1' $take 'self'
Connect $branch 'else' $take 'execute'
$gone = New-Call $null 'K2_DestroyActor' $false 1350 0
Connect $take 'then' $gone 'execute'
Write-Graph 'BP_CheckpointItem_EventGraph.txt'

# ======================= BP_ThirdPersonCharacter1 ============================================
# Above the numbers already in the character graph (up to _954).
$script:counter = 1000
$flagGet = New-VarGet 'ActiveFlag' $null 'object' '' $FLAG_CLASS 400 3700

# --- E: plant the flag where the player stands, if one is held and the player is on the ground ---
$y = 3300
$use = New-Node '/Script/InputBlueprintNodes.K2Node_EnhancedInputAction' @("InputAction=`"/Script/EnhancedInput.InputAction'/Game/Input/Actions/IA_UseItem.IA_UseItem'`"") 0 $y
Add-Pin $use 'Started' 'out' 'exec'
$hasItem = New-VarGet 'HasFlagItem' $null 'bool' '' $null 250 ($y + 200)
$hasBranch = New-Branch 400 $y
Connect $use 'Started' $hasBranch 'execute'
Connect $hasItem 'HasFlagItem' $hasBranch 'Condition'
$movement = New-VarGet 'CharacterMovement' $null 'object' '' $MOVEMENT_CLASS 500 ($y + 200)
$grounded = New-Call $MOVEMENT_CLASS 'IsMovingOnGround' $true 700 ($y + 200)
Add-Pin $grounded 'self' 'in' 'object' '' $MOVEMENT_CLASS
Add-Pin $grounded 'ReturnValue' 'out' 'bool'
Connect $movement 'CharacterMovement' $grounded 'self'
$groundBranch = New-Branch 950 $y
Connect $hasBranch 'then' $groundBranch 'execute'
Connect $grounded 'ReturnValue' $groundBranch 'Condition'
$useUp = New-VarSet 'HasFlagItem' $null 'bool' $null 1250 $y
(Get-Pin $useUp 'HasFlagItem').Default = 'false'
Connect $groundBranch 'then' $useUp 'execute'
# Only one flag stands at a time: a new one breaks the old.
$oldValid = New-IsValid 1500 ($y + 200)
Connect $flagGet 'ActiveFlag' $oldValid 'Object'
$oldBranch = New-Branch 1600 $y
Connect $useUp 'then' $oldBranch 'execute'
Connect $oldValid 'ReturnValue' $oldBranch 'Condition'
$breakOld = New-BreakCall $flagGet 1900 ($y - 150)
Connect $oldBranch 'then' $breakOld 'execute'

$location = New-Call $null 'K2_GetActorLocation' $true 1650 ($y + 450)
Add-Pin $location 'ReturnValue' 'out' 'struct' '' $VECTOR
$breakVector = New-Call $MATH 'BreakVector' $true 1900 ($y + 450)
Add-Pin $breakVector 'InVec' 'in' 'struct' '' $VECTOR
Add-Pin $breakVector 'X' 'out' 'real' 'double'
Add-Pin $breakVector 'Y' 'out' 'real' 'double'
Add-Pin $breakVector 'Z' 'out' 'real' 'double'
$capsuleGet = New-VarGet 'CapsuleComponent' $null 'object' '' $CAPSULE_CLASS 1650 ($y + 650)
$half = New-Call $CAPSULE_CLASS 'GetScaledCapsuleHalfHeight' $true 1900 ($y + 650)
Add-Pin $half 'self' 'in' 'object' '' $CAPSULE_CLASS
Add-Pin $half 'ReturnValue' 'out' 'real' 'float'
$down = New-Operator 'Subtract' 'Subtract_DoubleDouble' 'real' 'double' 'real' 2150 ($y + 550)
(Get-Pin $down 'ReturnValue').Sub = 'double'
$feet = New-Call $MATH 'MakeVector' $true 2350 ($y + 450)
Add-Pin $feet 'X' 'in' 'real' 'double' $null '0.0'
Add-Pin $feet 'Y' 'in' 'real' 'double' $null '0.0'
Add-Pin $feet 'Z' 'in' 'real' 'double' $null '0.0'
Add-Pin $feet 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $location 'ReturnValue' $breakVector 'InVec'
Connect $capsuleGet 'CapsuleComponent' $half 'self'
Connect $breakVector 'Z' $down 'A'
Connect $half 'ReturnValue' $down 'B'
Connect $breakVector 'X' $feet 'X'
Connect $breakVector 'Y' $feet 'Y'
Connect $down 'ReturnValue' $feet 'Z'
$facing = New-Call $null 'K2_GetActorRotation' $true 2350 ($y + 650)
Add-Pin $facing 'ReturnValue' 'out' 'struct' '' $ROTATOR_STRUCT
$place = New-Call $MATH 'MakeTransform' $true 2600 ($y + 450)
Add-Pin $place 'Location' 'in' 'struct' '' $VECTOR
Add-Pin $place 'Rotation' 'in' 'struct' '' $ROTATOR_STRUCT '0,0,0'
Add-Pin $place 'Scale' 'in' 'struct' '' $VECTOR '1.000000,1.000000,1.000000'
Add-Pin $place 'ReturnValue' 'out' 'struct' '' $TRANSFORM_STRUCT
Connect $feet 'ReturnValue' $place 'Location'
Connect $facing 'ReturnValue' $place 'Rotation'
$spawn = New-Node '/Script/BlueprintGraph.K2Node_SpawnActorFromClass' @() 2250 $y
Add-Exec $spawn
Add-Pin $spawn 'Class' 'in' 'class' '' $ACTOR
Add-Pin $spawn 'SpawnTransform' 'in' 'struct' '' $TRANSFORM_STRUCT
Add-Pin $spawn 'CollisionHandlingOverride' 'in' 'byte' '' $SPAWN_COLLISION 'AlwaysSpawn'
Add-Pin $spawn 'ReturnValue' 'out' 'object' '' $FLAG_CLASS
Set-ObjectDefault $spawn 'Class' '/Game/ThirdPerson/Item/Checkpoint/BP_CheckpointFlag.BP_CheckpointFlag_C'
Connect $place 'ReturnValue' $spawn 'SpawnTransform'
Connect $oldBranch 'else' $spawn 'execute'
Connect $breakOld 'then' $spawn 'execute'
$remember = New-VarSet 'ActiveFlag' $null 'object' $FLAG_CLASS 2650 $y
Connect $spawn 'then' $remember 'execute'
Connect $spawn 'ReturnValue' $remember 'ActiveFlag'
$plantAnim = New-Call $null 'PlayAnimMontage' $false 3000 $y
Add-Pin $plantAnim 'AnimMontage' 'in' 'object' '' $MONTAGE_CLASS
Add-Pin $plantAnim 'InPlayRate' 'in' 'real' 'float' $null '1.000000'
Add-Pin $plantAnim 'StartSectionName' 'in' 'name' '' $null 'None'
Add-Pin $plantAnim 'ReturnValue' 'out' 'real' 'float'
Set-ObjectDefault $plantAnim 'AnimMontage' '/Game/ThirdPerson/Blueprints/Plaey/Anim/AM_PlantFlag_Handmade.AM_PlantFlag_Handmade'
Connect $remember 'then' $plantAnim 'execute'

# --- Fall: hooked by hand after the existing Stop Movement Immediately in the -50 m check ---------
$y = 4400
$fallValid = New-IsValid 300 ($y + 200)
Connect $flagGet 'ActiveFlag' $fallValid 'Object'
$fallBranch = New-Branch 500 $y
Connect $fallValid 'ReturnValue' $fallBranch 'Condition'
# With a flag: to its RespawnPoint, then the flag breaks and is forgotten.
$respawnGet = New-VarGet 'RespawnPoint' $FLAG_CLASS 'object' '' $SCENE_CLASS 600 ($y - 250)
Connect $flagGet 'ActiveFlag' $respawnGet 'self'
$respawnWorld = New-Call $SCENE_CLASS 'K2_GetComponentToWorld' $true 850 ($y - 250)
Add-Pin $respawnWorld 'self' 'in' 'object' '' $SCENE_CLASS
Add-Pin $respawnWorld 'ReturnValue' 'out' 'struct' '' $TRANSFORM_STRUCT
Connect $respawnGet 'RespawnPoint' $respawnWorld 'self'

function New-MovePlayer($x, $yy) {
  $node = New-Call $null 'K2_SetActorTransform' $false $x $yy
  Add-Pin $node 'NewTransform' 'in' 'struct' '' $TRANSFORM_STRUCT
  Add-Pin $node 'bSweep' 'in' 'bool' '' $null 'false'
  Add-Pin $node 'SweepHitResult' 'out' 'struct' '' $HIT_STRUCT
  Add-Pin $node 'bTeleport' 'in' 'bool' '' $null 'true'
  Add-Pin $node 'ReturnValue' 'out' 'bool'
  return $node
}
$toFlag = New-MovePlayer 1150 ($y - 100)
Connect $fallBranch 'then' $toFlag 'execute'
Connect $respawnWorld 'ReturnValue' $toFlag 'NewTransform'
$breakUsed = New-BreakCall $flagGet 1500 ($y - 100)
Connect $toFlag 'then' $breakUsed 'execute'
$forget = New-VarSet 'ActiveFlag' $null 'object' $FLAG_CLASS 1850 ($y - 100)
Connect $breakUsed 'then' $forget 'execute'
# Without one: back to the PlayerStart, the same as before.
$findStart = New-Call $STATICS 'GetActorOfClass' $false 850 ($y + 300)
Add-Pin $findStart 'ActorClass' 'in' 'class' '' $ACTOR
Add-Pin $findStart 'ReturnValue' 'out' 'object' '' $ACTOR
Set-ObjectDefault $findStart 'ActorClass' '/Script/Engine.PlayerStart'
Connect $fallBranch 'else' $findStart 'execute'
$startTransform = New-Call $ACTOR 'GetTransform' $true 1150 ($y + 450)
Add-Pin $startTransform 'self' 'in' 'object' '' $ACTOR
Add-Pin $startTransform 'ReturnValue' 'out' 'struct' '' $TRANSFORM_STRUCT
Connect $findStart 'ReturnValue' $startTransform 'self'
$toStart = New-MovePlayer 1450 ($y + 300)
Connect $findStart 'then' $toStart 'execute'
Connect $startTransform 'ReturnValue' $toStart 'NewTransform'
Write-Graph 'Checkpoint_Character.txt'
