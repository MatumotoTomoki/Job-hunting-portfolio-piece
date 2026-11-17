param([string]$OutDir)
# Generates Ctrl+V-pasteable node text: BP_FallingFloor shakes when stepped on, plunges, then comes back.
# Turning the trigger's collision off is what stops it firing again mid-sequence; no state variable needed.

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
$previous = $disarm; $previousPin = 'then'
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
$plunge = New-Move "0.000000,0.000000,-$FALL_DISTANCE" $ZERO_ROTATION $FALL_SECONDS 'false' 'true' 350 $rowY
Connect $passThrough 'then' $plunge 'Move'
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
[IO.File]::WriteAllText((Join-Path $OutDir 'BP_FallingFloor_EventGraph.txt'), $text, [Text.UTF8Encoding]::new($false))
"Generated $($script:nodes.Count) nodes"
