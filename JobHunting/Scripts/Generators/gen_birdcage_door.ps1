param([string]$OutDir)
# Generates Ctrl+V-pasteable Event Graphs for the two door-opening birdcages. Both overlap events run one chain, which
# asks whether the player is inside the trigger: that way a change of mind midway just reverses the door from where it is.

# Reuse the node helpers (constants + functions) from the height BGM generator.
$helpers = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_height_bgm.ps1') -Encoding UTF8 |
  Select-Object -Skip 3 -First 124
. ([ScriptBlock]::Create(($helpers -join "`n")))

$SCENE_CLASS = "/Script/CoreUObject.Class'/Script/Engine.SceneComponent'"
$PRIMITIVE_CLASS = "/Script/CoreUObject.Class'/Script/Engine.PrimitiveComponent'"
$SPHERE_CLASS = "/Script/CoreUObject.Class'/Script/Engine.SphereComponent'"
$SKELETAL_CLASS = "/Script/CoreUObject.Class'/Script/Engine.SkeletalMeshComponent'"
$CHARACTER = "/Script/CoreUObject.Class'/Script/Engine.Character'"
$ROTATOR_STRUCT = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Rotator'"
$OPEN_YAW = '90.000000'
$DOOR_SECONDS = '1.000000'

function New-BoundEvent($blueprintName, $signature, $x, $y) {
  $node = New-Node '/Script/BlueprintGraph.K2Node_ComponentBoundEvent' @(
    "DelegatePropertyName=`"OnComponent$signature`"",
    "DelegateOwnerClass=`"$PRIMITIVE_CLASS`"",
    'ComponentPropertyName="Trigger"',
    "EventReference=(MemberParent=`"/Script/CoreUObject.Package'/Script/Engine'`",MemberName=`"Component${signature}Signature__DelegateSignature`")",
    'bInternalEvent=True',
    "CustomFunctionName=`"BndEvt__${blueprintName}_Trigger_K2Node_ComponentBoundEvent_0_Component${signature}Signature__DelegateSignature`""
  ) $x $y
  Add-Pin $node 'then' 'out' 'exec'
  return $node
}

# Pure nodes: picks valueInside while the player is in the trigger, valueOutside once they have left.
function New-PlayerChoice($valueInside, $valueOutside, $x, $y) {
  $playerNode = New-Call $STATICS 'GetPlayerCharacter' $true $x ($y + 150)
  Add-Pin $playerNode 'PlayerIndex' 'in' 'int' '' $null '0'
  Add-Pin $playerNode 'ReturnValue' 'out' 'object' '' $CHARACTER
  $triggerGet = New-VarGet 'Trigger' $null 'object' '' $SPHERE_CLASS $x $y
  $inside = New-Call $PRIMITIVE_CLASS 'IsOverlappingActor' $true ($x + 300) $y
  Add-Pin $inside 'self' 'in' 'object' '' $PRIMITIVE_CLASS
  Add-Pin $inside 'Other' 'in' 'object' '' $ACTOR
  Add-Pin $inside 'ReturnValue' 'out' 'bool'
  $choice = New-Call $MATH 'SelectFloat' $true ($x + 600) $y
  Add-Pin $choice 'A' 'in' 'real' 'double' $null $valueInside
  Add-Pin $choice 'B' 'in' 'real' 'double' $null $valueOutside
  Add-Pin $choice 'bPickA' 'in' 'bool'
  Add-Pin $choice 'ReturnValue' 'out' 'real' 'double'
  Connect $triggerGet 'Trigger' $inside 'self'
  Connect $playerNode 'ReturnValue' $inside 'Other'
  Connect $inside 'ReturnValue' $choice 'bPickA'
  return $choice
}

function Write-Graph($fileName) {
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
  [IO.File]::WriteAllText((Join-Path $OutDir $fileName), $text, [Text.UTF8Encoding]::new($false))
  "$fileName : $($script:nodes.Count) nodes"
  $script:nodes.Clear()
}

# --- UE version: turn the door with one MoveComponentTo, so a new target restarts it from where the door is ---
$begin = New-BoundEvent 'BP_BirdcageDoor_UE' 'BeginOverlap' 0 0
$end = New-BoundEvent 'BP_BirdcageDoor_UE' 'EndOverlap' 0 250
$yawChoice = New-PlayerChoice $OPEN_YAW '0.000000' 0 500
$rotator = New-Call $MATH 'MakeRotator' $true 950 500
Add-Pin $rotator 'Roll' 'in' 'real' 'float' $null '0.0'
Add-Pin $rotator 'Pitch' 'in' 'real' 'float' $null '0.0'
Add-Pin $rotator 'Yaw' 'in' 'real' 'float' $null '0.0'
Add-Pin $rotator 'ReturnValue' 'out' 'struct' '' $ROTATOR_STRUCT
$pivotGet = New-VarGet 'DoorPivot' $null 'object' '' $SCENE_CLASS 950 200
$move = New-Node '/Script/BlueprintGraph.K2Node_CallFunction' @("FunctionReference=(MemberParent=`"$SYSTEM`",MemberName=`"MoveComponentTo`")") 1250 100
Add-Pin $move 'Move' 'in' 'exec'
Add-Pin $move 'Stop' 'in' 'exec'
Add-Pin $move 'Return' 'in' 'exec'
Add-Pin $move 'then' 'out' 'exec'
Add-Pin $move 'Component' 'in' 'object' '' $SCENE_CLASS
Add-Pin $move 'TargetRelativeLocation' 'in' 'struct' '' $VECTOR '0.000000,0.000000,0.000000'
Add-Pin $move 'TargetRelativeRotation' 'in' 'struct' '' $ROTATOR_STRUCT
Add-Pin $move 'bEaseOut' 'in' 'bool' '' $null 'true'
Add-Pin $move 'bEaseIn' 'in' 'bool' '' $null 'true'
Add-Pin $move 'OverTime' 'in' 'real' 'float' $null $DOOR_SECONDS
Add-Pin $move 'bForceShortestRotationPath' 'in' 'bool' '' $null 'true'
Connect $begin 'then' $move 'Move'
Connect $end 'then' $move 'Move'
Connect $yawChoice 'ReturnValue' $rotator 'Yaw'
Connect $rotator 'ReturnValue' $move 'TargetRelativeRotation'
Connect $pivotGet 'DoorPivot' $move 'Component'
Write-Graph 'BP_BirdcageDoor_UE_EventGraph.txt'

# --- Blender version: play Door_Open forward to open, backward to close, from wherever it is now ---
$begin = New-BoundEvent 'BP_BirdcageDoor_Blender' 'BeginOverlap' 0 0
$end = New-BoundEvent 'BP_BirdcageDoor_Blender' 'EndOverlap' 0 250
$rateChoice = New-PlayerChoice '1.000000' '-1.000000' 0 500
$cageGet = New-VarGet 'Cage' $null 'object' '' $SKELETAL_CLASS 700 200
$setRate = New-Call $SKELETAL_CLASS 'SetPlayRate' $false 1000 100
Add-Pin $setRate 'self' 'in' 'object' '' $SKELETAL_CLASS
Add-Pin $setRate 'Rate' 'in' 'real' 'float' $null '1.0'
$play = New-Call $SKELETAL_CLASS 'Play' $false 1400 100
Add-Pin $play 'self' 'in' 'object' '' $SKELETAL_CLASS
Add-Pin $play 'bLooping' 'in' 'bool' '' $null 'false'
Connect $begin 'then' $setRate 'execute'
Connect $end 'then' $setRate 'execute'
Connect $rateChoice 'ReturnValue' $setRate 'Rate'
Connect $cageGet 'Cage' $setRate 'self'
Connect $setRate 'then' $play 'execute'
Connect $cageGet 'Cage' $play 'self'
Write-Graph 'BP_BirdcageDoor_Blender_EventGraph.txt'
