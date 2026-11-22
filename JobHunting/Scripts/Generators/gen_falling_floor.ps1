param([string]$OutDir)
# Generates Ctrl+V-pasteable node text: BP_FallingFloor shakes when stepped on, plunges, then comes back.
# Turning the trigger's collision off is what stops it firing again mid-sequence; no state variable needed.
# Sounds and effects (setup_floor_effects.py, 2026-11-22): Begin Play sets their volume (SE x Master); stepped on -
# CrackSound + CrackFx; giving way - FallSound + FallFx; back - ReturnSound and the FootSmoke (scale 3), which this
# graph now holds itself (gen_falling_floor_respawn_fx.ps1 is no longer needed).

# Reuse the node helpers (constants + functions) from the height BGM generator.
$helpers = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_height_bgm.ps1') -Encoding UTF8 |
  Select-Object -Skip 3 -First 124
. ([ScriptBlock]::Create(($helpers -join "`n")))

$SCENE_CLASS = "/Script/CoreUObject.Class'/Script/Engine.SceneComponent'"
$PRIMITIVE_CLASS = "/Script/CoreUObject.Class'/Script/Engine.PrimitiveComponent'"
$MESH_CLASS = "/Script/CoreUObject.Class'/Script/Engine.StaticMeshComponent'"
$BOX_CLASS = "/Script/CoreUObject.Class'/Script/Engine.BoxComponent'"
$ROTATOR_STRUCT = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Rotator'"
$COLLISION_ENUM = "/Script/CoreUObject.Enum'/Script/Engine.ECollisionEnabled'"
$ZERO_VECTOR = '0.000000,0.000000,0.000000'
$ZERO_ROTATION = '0.000000,0.000000,0.000000'

$SHAKE_STEP_SECONDS = '0.080000'
$FALL_DISTANCE = '1500.000000'
$FALL_SECONDS = '0.700000'
$RESPAWN_SECONDS = '3.000000'
# Each shake step: location offset, then rotation as pitch,yaw,roll. 12 steps of 0.08 s is about 1 s.
$SHAKE_STEPS = @(
  @('3,0,0', '0,0,2'), @('-3,0,0', '0,0,-2'), @('0,3,0', '2,0,0'), @('0,-3,0', '-2,0,0'),
  @('3,0,0', '0,0,2'), @('-3,0,0', '0,0,-2'), @('0,3,0', '2,0,0'), @('0,-3,0', '-2,0,0'),
  @('3,0,0', '0,0,2'), @('-3,0,0', '0,0,-2'), @('0,3,0', '2,0,0'), @('0,0,0', '0,0,0')
)

$liftGet = New-VarGet 'Lift' $null 'object' '' $SCENE_CLASS 0 -300
$meshGet = New-VarGet 'FloorMesh' $null 'object' '' $MESH_CLASS 200 -300
$triggerGet = New-VarGet 'Trigger' $null 'object' '' $BOX_CLASS 400 -300

function New-Move($locationValue, $rotationValue, $seconds, $easeOutValue, $easeInValue, $x, $y) {
  $node = New-Node '/Script/BlueprintGraph.K2Node_CallFunction' @("FunctionReference=(MemberParent=`"$SYSTEM`",MemberName=`"MoveComponentTo`")") $x $y
  Add-Pin $node 'Move' 'in' 'exec'
  Add-Pin $node 'Stop' 'in' 'exec'
  Add-Pin $node 'Return' 'in' 'exec'
  Add-Pin $node 'then' 'out' 'exec'
  Add-Pin $node 'Component' 'in' 'object' '' $SCENE_CLASS
  Add-Pin $node 'TargetRelativeLocation' 'in' 'struct' '' $VECTOR $locationValue
  Add-Pin $node 'TargetRelativeRotation' 'in' 'struct' '' $ROTATOR_STRUCT $rotationValue
  Add-Pin $node 'bEaseOut' 'in' 'bool' '' $null $easeOutValue
  Add-Pin $node 'bEaseIn' 'in' 'bool' '' $null $easeInValue
  Add-Pin $node 'OverTime' 'in' 'real' 'float' $null $seconds
  Connect $liftGet 'Lift' $node 'Component'
  return $node
}

function New-SetCollision($targetGet, $targetPin, $mode, $x, $y) {
  $node = New-Call $PRIMITIVE_CLASS 'SetCollisionEnabled' $false $x $y
  Add-Pin $node 'self' 'in' 'object' '' $PRIMITIVE_CLASS
  Add-Pin $node 'NewType' 'in' 'byte' '' $COLLISION_ENUM $mode
  Connect $targetGet $targetPin $node 'self'
  return $node
}

function New-SetVisible($value, $x, $y) {
  $node = New-Call $SCENE_CLASS 'SetVisibility' $false $x $y
  Add-Pin $node 'self' 'in' 'object' '' $SCENE_CLASS
  Add-Pin $node 'bNewVisibility' 'in' 'bool' '' $null $value
  Add-Pin $node 'bPropagateToChildren' 'in' 'bool' '' $null 'false'
  Connect $meshGet 'FloorMesh' $node 'self'
  return $node
}

# Sounds and effects (setup_floor_effects.py, 2026-11-22).
$EMITTER_COMP = "/Script/CoreUObject.Class'/Script/Effekseer.EffekseerEmitterComponent'"
$COMPONENT_CLASS = "/Script/CoreUObject.Class'/Script/Engine.ActorComponent'"
$GI_OUT = 'AsBP My Game Instance'
# (Typed coordinates: untyped, a negative y arrives as text and -250 + 200 becomes -250200.)
function SoundPlay($name, [double]$x, [double]$y) {
  $n = New-Call $AUDIO 'Play' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $AUDIO
  Add-Pin $n 'StartTime' 'in' 'real' 'float' $null '0.0'
  Connect (New-VarGet $name $null 'object' '' $AUDIO ($x - 200) ($y + 200)) $name $n 'self'
  return $n
}
function FxPlay($name, [double]$x, [double]$y) {
  $n = New-Call $COMPONENT_CLASS 'Activate' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $COMPONENT_CLASS
  Add-Pin $n 'bReset' 'in' 'bool' '' $null 'true'
  Connect (New-VarGet $name $null 'object' '' $EMITTER_COMP ($x - 200) ($y + 200)) $name $n 'self'
  return $n
}

# Begin Play: the sounds at SE Volume x Master Volume.
$begin = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$ACTOR`",MemberName=`"ReceiveBeginPlay`")", 'bOverrideFunction=True') 0 -800
Add-Pin $begin 'then' 'out' 'exec'
$gi = New-Call $STATICS 'GetGameInstance' $true 50 -600
Add-Pin $gi 'ReturnValue' 'out' 'object' '' $GAMEINST
$cast = New-Node '/Script/BlueprintGraph.K2Node_DynamicCast' @("TargetType=`"$GI_CLASS`"") 300 -800
Add-Exec $cast
Add-Pin $cast 'CastFailed' 'out' 'exec'
Add-Pin $cast 'Object' 'in' 'object' '' $OBJECT
Add-Pin $cast $GI_OUT 'out' 'object' '' $GI_CLASS
Add-Pin $cast 'bSuccess' 'out' 'bool'
Connect $gi 'ReturnValue' $cast 'Object'
Connect $begin 'then' $cast 'execute'
$seVol = New-VarGet 'SE Volume' $GI_CLASS 'real' 'double' $null 350 -550
Connect $cast $GI_OUT $seVol 'self'
$masterVol = New-VarGet 'Master Volume' $GI_CLASS 'real' 'double' $null 350 -450
Connect $cast $GI_OUT $masterVol 'self'
$vol = New-Operator 'Multiply' 'Multiply_DoubleDouble' 'real' 'double' 'real' 600 -550
(Get-Pin $vol 'ReturnValue').Sub = 'double'
Connect $seVol 'SE Volume' $vol 'A'
Connect $masterVol 'Master Volume' $vol 'B'
$prev = $cast; $vx = 750
foreach ($name in 'CrackSound', 'FallSound', 'ReturnSound') {
  $v = New-Call $AUDIO 'SetVolumeMultiplier' $false $vx -800
  Add-Pin $v 'self' 'in' 'object' '' $AUDIO
  Add-Pin $v 'NewVolumeMultiplier' 'in' 'real' 'float'
  Connect (New-VarGet $name $null 'object' '' $AUDIO ($vx - 200) -600) $name $v 'self'
  Connect $vol 'ReturnValue' $v 'NewVolumeMultiplier'
  Connect $prev 'then' $v 'execute'
  $prev = $v; $vx += 300
}

# Bound events need a function name; this form matches what the editor generates.
$overlap = New-Node '/Script/BlueprintGraph.K2Node_ComponentBoundEvent' @(
  'DelegatePropertyName="OnComponentBeginOverlap"',
  "DelegateOwnerClass=`"$PRIMITIVE_CLASS`"",
  'ComponentPropertyName="Trigger"',
  "EventReference=(MemberParent=`"/Script/CoreUObject.Package'/Script/Engine'`",MemberName=`"ComponentBeginOverlapSignature__DelegateSignature`")",
  'bInternalEvent=True',
  'CustomFunctionName="BndEvt__BP_FallingFloor_Trigger_K2Node_ComponentBoundEvent_0_ComponentBeginOverlapSignature__DelegateSignature"'
) 0 0
Add-Pin $overlap 'then' 'out' 'exec'

# --- Step on: stop the trigger firing again, then shake ------------------------------
$disarm = New-SetCollision $triggerGet 'Trigger' 'NoCollision' 350 0
Connect $overlap 'then' $disarm 'execute'
$crackSound = SoundPlay 'CrackSound' 350 -250
$crackFx = FxPlay 'CrackFx' 650 -250
Connect $disarm 'then' $crackSound 'execute'
Connect $crackSound 'then' $crackFx 'execute'
$previous = $crackFx; $previousPin = 'then'
$column = 0; $row = 0
foreach ($step in $SHAKE_STEPS) {
  $move = New-Move $step[0] $step[1] $SHAKE_STEP_SECONDS 'false' 'false' (700 + $column * 400) (0 + $row * 450)
  Connect $previous $previousPin $move 'Move'
  $previous = $move; $previousPin = 'then'
  $column++
  if ($column -eq 6) { $column = 0; $row++ }
}

# --- Plunge: no collision, so the player drops freely and lower platforms are passed through ---
$rowY = 900
$passThrough = New-SetCollision $meshGet 'FloorMesh' 'NoCollision' 0 $rowY
Connect $previous $previousPin $passThrough 'execute'
$fallSound = SoundPlay 'FallSound' 0 ($rowY + 400)
$fallFx = FxPlay 'FallFx' 300 ($rowY + 400)
Connect $passThrough 'then' $fallSound 'execute'
Connect $fallSound 'then' $fallFx 'execute'
$plunge = New-Move "0.000000,0.000000,-$FALL_DISTANCE" $ZERO_ROTATION $FALL_SECONDS 'false' 'true' 350 $rowY
Connect $fallFx 'then' $plunge 'Move'
$hide = New-SetVisible 'false' 800 $rowY
Connect $plunge 'then' $hide 'execute'

# --- Come back: move home while hidden, wait, then show it and arm it again ------------
$home_ = New-Call $SCENE_CLASS 'K2_SetRelativeLocation' $false 1150 $rowY
Add-Pin $home_ 'self' 'in' 'object' '' $SCENE_CLASS
Add-Pin $home_ 'NewLocation' 'in' 'struct' '' $VECTOR $ZERO_VECTOR
Add-Pin $home_ 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $home_ 'bTeleport' 'in' 'bool' '' $null 'true'
Connect $liftGet 'Lift' $home_ 'self'
Connect $hide 'then' $home_ 'execute'
$wait = New-Call $SYSTEM 'Delay' $false 1550 $rowY
Add-Pin $wait 'Duration' 'in' 'real' 'float' $null $RESPAWN_SECONDS
Connect $home_ 'then' $wait 'execute'
$show = New-SetVisible 'true' 1900 $rowY
Connect $wait 'then' $show 'execute'
$solid = New-SetCollision $meshGet 'FloorMesh' 'QueryAndPhysics' 2250 $rowY
Connect $show 'then' $solid 'execute'
$arm = New-SetCollision $triggerGet 'Trigger' 'QueryOnly' 2600 $rowY
Connect $solid 'then' $arm 'execute'
$returnSound = SoundPlay 'ReturnSound' 2950 $rowY
Connect $arm 'then' $returnSound 'execute'

# --- Back: FootSmoke at the floor (once hooked by hand from gen_falling_floor_respawn_fx.ps1; the user set its
# scale to 3). A spawned emitter actor that removes itself after a few seconds. ---
$TRANSFORM_STRUCT = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Transform'"
$SPAWN_COLLISION = "/Script/CoreUObject.Enum'/Script/Engine.ESpawnActorCollisionHandlingMethod'"
$EFFECT_CLASS = "/Script/CoreUObject.Class'/Script/Effekseer.EffekseerEffect'"
$EMITTER_BP = "/Script/Engine.BlueprintGeneratedClass'/Effekseer/BluePrints/BP_EffekseerEmitter.BP_EffekseerEmitter_C'"
$script:objectDefaults = @{}
function Set-ObjectDefault($node, $pinName, $path) { $script:objectDefaults[(Get-Pin $node $pinName).Id] = $path }
$x = 3600; $y = $rowY
$location = New-Call $null 'K2_GetActorLocation' $true ($x - 550) ($y + 300)
Add-Pin $location 'ReturnValue' 'out' 'struct' '' $VECTOR
$transformNode = New-Call $MATH 'MakeTransform' $true ($x - 300) ($y + 300)
Add-Pin $transformNode 'Location' 'in' 'struct' '' $VECTOR
Add-Pin $transformNode 'Rotation' 'in' 'struct' '' $ROTATOR_STRUCT '0,0,0'
Add-Pin $transformNode 'Scale' 'in' 'struct' '' $VECTOR '3.000000,3.000000,3.000000'
Add-Pin $transformNode 'ReturnValue' 'out' 'struct' '' $TRANSFORM_STRUCT
$spawnNode = New-Node '/Script/BlueprintGraph.K2Node_SpawnActorFromClass' @() $x $y
Add-Exec $spawnNode
Add-Pin $spawnNode 'Class' 'in' 'class' '' $ACTOR
Add-Pin $spawnNode 'SpawnTransform' 'in' 'struct' '' $TRANSFORM_STRUCT
Add-Pin $spawnNode 'CollisionHandlingOverride' 'in' 'byte' '' $SPAWN_COLLISION 'AlwaysSpawn'
Add-Pin $spawnNode 'ReturnValue' 'out' 'object' '' $EMITTER_BP
Set-ObjectDefault $spawnNode 'Class' '/Effekseer/BluePrints/BP_EffekseerEmitter.BP_EffekseerEmitter_C'
$emitterGet = New-Call $ACTOR 'GetComponentByClass' $true ($x + 350) ($y + 300)
Add-Pin $emitterGet 'self' 'in' 'object' '' $ACTOR
Add-Pin $emitterGet 'ComponentClass' 'in' 'class' '' $COMPONENT_CLASS
Add-Pin $emitterGet 'ReturnValue' 'out' 'object' '' $EMITTER_COMP
Set-ObjectDefault $emitterGet 'ComponentClass' '/Script/Effekseer.EffekseerEmitterComponent'
$setEffect = New-VarSet 'Effect' $EMITTER_COMP 'object' $EFFECT_CLASS ($x + 400) $y
Set-ObjectDefault $setEffect 'Effect' '/Game/FX/Effekseer/FootSmoke.FootSmoke'
$activate = New-Call $COMPONENT_CLASS 'Activate' $false ($x + 800) $y
Add-Pin $activate 'self' 'in' 'object' '' $COMPONENT_CLASS
Add-Pin $activate 'bReset' 'in' 'bool' '' $null 'false'
$life = New-Call $ACTOR 'SetLifeSpan' $false ($x + 1100) $y
Add-Pin $life 'self' 'in' 'object' '' $ACTOR
Add-Pin $life 'InLifespan' 'in' 'real' 'float' $null '5.000000'
Connect $location 'ReturnValue' $transformNode 'Location'
Connect $transformNode 'ReturnValue' $spawnNode 'SpawnTransform'
Connect $returnSound 'then' $spawnNode 'execute'
Connect $spawnNode 'then' $setEffect 'execute'
Connect $spawnNode 'ReturnValue' $emitterGet 'self'
Connect $emitterGet 'ReturnValue' $setEffect 'self'
Connect $setEffect 'then' $activate 'execute'
Connect $emitterGet 'ReturnValue' $activate 'self'
Connect $activate 'then' $life 'execute'
Connect $spawnNode 'ReturnValue' $life 'self'

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
foreach ($n in $script:nodes) {
  foreach ($p in $n.Pins) {
    if ($p.Cat -eq 'exec' -and $p.Dir -eq 'out' -and $p.Links.Count -gt 1) { throw "exec output with several links: $($n.Name).$($p.Name)" }
  }
}
$text = $sb.ToString()
if ($text.Contains('@{')) { throw 'A node object leaked into a pin or reference (variable name collision)' }
$names = [regex]::Matches($text, '(?m)^Begin Object Class=\S+ Name="(\w+)"') | ForEach-Object { $_.Groups[1].Value }
foreach ($m in [regex]::Matches($text, 'LinkedTo=\(([^)]*)\)')) {
  foreach ($link in ($m.Groups[1].Value -split ',' | Where-Object { $_ })) {
    if ($names -notcontains ($link -split ' ')[0]) { throw "Dangling link: $link" }
  }
}
[IO.File]::WriteAllText((Join-Path $OutDir 'BP_FallingFloor_EventGraph.txt'), $text, [Text.UTF8Encoding]::new($false))
"Generated $($script:nodes.Count) nodes"
