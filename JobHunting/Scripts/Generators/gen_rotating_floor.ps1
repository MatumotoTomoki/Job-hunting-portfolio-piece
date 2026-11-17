param([string]$OutDir)
# Generates Ctrl+V-pasteable node text: BP_RotatingFloor turns 90 degrees, waits 3 seconds, repeats.

# Reuse the node helpers (constants + functions) from the height BGM generator.
$helpers = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_height_bgm.ps1') -Encoding UTF8 |
  Select-Object -Skip 3 -First 124
. ([ScriptBlock]::Create(($helpers -join "`n")))

$SCENE_CLASS = "/Script/CoreUObject.Class'/Script/Engine.SceneComponent'"
$ROTATOR_STRUCT = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Rotator'"
$TURN_DEGREES = '90.000000'
$TURN_SECONDS = '1.000000'
$WAIT_SECONDS = '3.000000'

$begin = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$ACTOR`",MemberName=`"ReceiveBeginPlay`")", 'bOverrideFunction=True') 0 0
Add-Pin $begin 'then' 'out' 'exec'

# Target = current rotation + 90 degrees of yaw.
$pivotGet = New-VarGet 'Pivot' $null 'object' '' $SCENE_CLASS 0 300
$current = New-VarGet 'RelativeRotation' $SCENE_CLASS 'struct' '' $ROTATOR_STRUCT 200 300
$breakNode = New-Call $MATH 'BreakRotator' $true 500 300
Add-Pin $breakNode 'InRot' 'in' 'struct' '' $ROTATOR_STRUCT
Add-Pin $breakNode 'Roll' 'out' 'real' 'float'
Add-Pin $breakNode 'Pitch' 'out' 'real' 'float'
Add-Pin $breakNode 'Yaw' 'out' 'real' 'float'
$addYaw = New-Operator 'Add' 'Add_DoubleDouble' 'real' 'double' 'real' 750 400
(Get-Pin $addYaw 'ReturnValue').Sub = 'double'
(Get-Pin $addYaw 'B').Default = $TURN_DEGREES
$makeNode = New-Call $MATH 'MakeRotator' $true 950 300
Add-Pin $makeNode 'Roll' 'in' 'real' 'float' $null '0.0'
Add-Pin $makeNode 'Pitch' 'in' 'real' 'float' $null '0.0'
Add-Pin $makeNode 'Yaw' 'in' 'real' 'float' $null '0.0'
Add-Pin $makeNode 'ReturnValue' 'out' 'struct' '' $ROTATOR_STRUCT

# Shortest path keeps every turn a forward 90 degrees even when the rotation wraps past 180.
$turn = New-Node '/Script/BlueprintGraph.K2Node_CallFunction' @("FunctionReference=(MemberParent=`"$SYSTEM`",MemberName=`"MoveComponentTo`")") 1250 0
Add-Pin $turn 'Move' 'in' 'exec'
Add-Pin $turn 'Stop' 'in' 'exec'
Add-Pin $turn 'Return' 'in' 'exec'
Add-Pin $turn 'then' 'out' 'exec'
Add-Pin $turn 'Component' 'in' 'object' '' $SCENE_CLASS
Add-Pin $turn 'TargetRelativeLocation' 'in' 'struct' '' $VECTOR '0.000000,0.000000,0.000000'
Add-Pin $turn 'TargetRelativeRotation' 'in' 'struct' '' $ROTATOR_STRUCT
Add-Pin $turn 'bEaseOut' 'in' 'bool' '' $null 'true'
Add-Pin $turn 'bEaseIn' 'in' 'bool' '' $null 'true'
Add-Pin $turn 'OverTime' 'in' 'real' 'float' $null $TURN_SECONDS
Add-Pin $turn 'bForceShortestRotationPath' 'in' 'bool' '' $null 'true'

$wait = New-Call $SYSTEM 'Delay' $false 1700 0
Add-Pin $wait 'Duration' 'in' 'real' 'float' $null $WAIT_SECONDS

Connect $begin 'then' $turn 'Move'
Connect $pivotGet 'Pivot' $current 'self'
Connect $current 'RelativeRotation' $breakNode 'InRot'
Connect $breakNode 'Yaw' $addYaw 'A'
Connect $breakNode 'Roll' $makeNode 'Roll'
Connect $breakNode 'Pitch' $makeNode 'Pitch'
Connect $addYaw 'ReturnValue' $makeNode 'Yaw'
Connect $pivotGet 'Pivot' $turn 'Component'
Connect $makeNode 'ReturnValue' $turn 'TargetRelativeRotation'
Connect $turn 'then' $wait 'execute'
# Back to the turn after the wait: this is what repeats forever.
Connect $wait 'then' $turn 'Move'

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
[IO.File]::WriteAllText((Join-Path $OutDir 'BP_RotatingFloor_EventGraph.txt'), $text, [Text.UTF8Encoding]::new($false))
"Generated $($script:nodes.Count) nodes"
