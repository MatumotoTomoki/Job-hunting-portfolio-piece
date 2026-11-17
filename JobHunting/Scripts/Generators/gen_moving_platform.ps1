param([string]$OutDir)
# Generates the Ctrl+V-pasteable Event Graph of BP_MovingPlatform: wait, move out by MoveOffset, wait, move back, repeat.

# Reuse the node helpers (constants + functions) from the height BGM generator.
$helperFile = (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_height_bgm.ps1')
$helpers = Get-Content -LiteralPath $helperFile -Encoding UTF8 | Select-Object -Skip 3 -First 124
. ([ScriptBlock]::Create(($helpers -join "`n")))

$SCENE_CLASS = "/Script/CoreUObject.Class'/Script/Engine.SceneComponent'"
$ROTATOR_STRUCT = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Rotator'"

function New-Wait($x, $y) {
  $node = New-Call $SYSTEM 'Delay' $false $x $y
  Add-Pin $node 'Duration' 'in' 'real' 'float' $null '1.0'
  $wait = New-VarGet 'WaitSeconds' $null 'real' 'double' $null ($x - 50) ($y + 200)
  Connect $wait 'WaitSeconds' $node 'Duration'
  return $node
}

# Eases in and out, so the player is not jerked off at the ends.
function New-Slide($x, $y) {
  $node = New-Node '/Script/BlueprintGraph.K2Node_CallFunction' @("FunctionReference=(MemberParent=`"$SYSTEM`",MemberName=`"MoveComponentTo`")") $x $y
  Add-Pin $node 'Move' 'in' 'exec'
  Add-Pin $node 'Stop' 'in' 'exec'
  Add-Pin $node 'Return' 'in' 'exec'
  Add-Pin $node 'then' 'out' 'exec'
  Add-Pin $node 'Component' 'in' 'object' '' $SCENE_CLASS
  Add-Pin $node 'TargetRelativeLocation' 'in' 'struct' '' $VECTOR '0.000000,0.000000,0.000000'
  Add-Pin $node 'TargetRelativeRotation' 'in' 'struct' '' $ROTATOR_STRUCT '0.000000,0.000000,0.000000'
  Add-Pin $node 'bEaseOut' 'in' 'bool' '' $null 'true'
  Add-Pin $node 'bEaseIn' 'in' 'bool' '' $null 'true'
  Add-Pin $node 'OverTime' 'in' 'real' 'float' $null '1.0'
  $lift = New-VarGet 'Lift' $null 'object' '' $SCENE_CLASS ($x - 250) ($y + 200)
  $seconds = New-VarGet 'MoveSeconds' $null 'real' 'double' $null ($x - 250) ($y + 400)
  Connect $lift 'Lift' $node 'Component'
  Connect $seconds 'MoveSeconds' $node 'OverTime'
  return $node
}

$begin = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$ACTOR`",MemberName=`"ReceiveBeginPlay`")", 'bOverrideFunction=True') 0 0
Add-Pin $begin 'then' 'out' 'exec'
$waitStart = New-Wait 300 0
$out = New-Slide 700 0
$offset = New-VarGet 'MoveOffset' $null 'struct' '' $VECTOR 450 600
Connect $offset 'MoveOffset' $out 'TargetRelativeLocation'
$waitEnd = New-Wait 1150 0
# Back home: the Lift's start, zero.
$back = New-Slide 1550 0

Connect $begin 'then' $waitStart 'execute'
Connect $waitStart 'then' $out 'Move'
Connect $out 'then' $waitEnd 'execute'
Connect $waitEnd 'then' $back 'Move'
Connect $back 'then' $waitStart 'execute'

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
foreach ($n in $script:nodes) {
  foreach ($p in $n.Pins) {
    if ($p.Cat -eq 'exec' -and $p.Dir -eq 'out' -and $p.Links.Count -gt 1) { throw "Exec output with several links: $($n.Name).$($p.Name)" }
  }
}
[IO.File]::WriteAllText((Join-Path $OutDir 'BP_MovingPlatform_EventGraph.txt'), $text, [Text.UTF8Encoding]::new($false))
"Generated $($script:nodes.Count) nodes"
