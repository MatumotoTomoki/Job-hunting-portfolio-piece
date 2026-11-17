param([string]$OutDir)
# Generates Ctrl+V-pasteable node text: FootSmoke at the falling floor when it comes back.
# Hooked by hand to the free exec output of the graph's last node, so any values tuned in the pasted
# graph stay as they are. The emitter stays where it spawned and removes itself after a few seconds.

# Reuse the node helpers (constants + functions) from the height BGM generator.
$helpers = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_height_bgm.ps1') -Encoding UTF8 |
  Select-Object -Skip 3 -First 124
. ([ScriptBlock]::Create(($helpers -join "`n")))
# Stay clear of the node names already in the pasted falling floor graph.
$script:counter = 900

$COMPONENT_CLASS = "/Script/CoreUObject.Class'/Script/Engine.ActorComponent'"
$TRANSFORM_STRUCT = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Transform'"
$ROTATOR_STRUCT = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Rotator'"
$SPAWN_COLLISION = "/Script/CoreUObject.Enum'/Script/Engine.ESpawnActorCollisionHandlingMethod'"
$EMITTER_COMP = "/Script/CoreUObject.Class'/Script/Effekseer.EffekseerEmitterComponent'"
$EFFECT_CLASS = "/Script/CoreUObject.Class'/Script/Effekseer.EffekseerEffect'"
$EMITTER_BP = "/Script/Engine.BlueprintGeneratedClass'/Effekseer/BluePrints/BP_EffekseerEmitter.BP_EffekseerEmitter_C'"
$FOOT_SMOKE = '/Game/FX/Effekseer/FootSmoke.FootSmoke'
$EMITTER_LIFETIME = '5.000000'

$script:objectDefaults = @{}
function Set-ObjectDefault($node, $pinName, $path) { $script:objectDefaults[(Get-Pin $node $pinName).Id] = $path }

$x = 3600; $y = 900
$location = New-Call $null 'K2_GetActorLocation' $true ($x - 550) ($y + 300)
Add-Pin $location 'ReturnValue' 'out' 'struct' '' $VECTOR
$transformNode = New-Call $MATH 'MakeTransform' $true ($x - 300) ($y + 300)
Add-Pin $transformNode 'Location' 'in' 'struct' '' $VECTOR
Add-Pin $transformNode 'Rotation' 'in' 'struct' '' $ROTATOR_STRUCT '0,0,0'
Add-Pin $transformNode 'Scale' 'in' 'struct' '' $VECTOR '1.000000,1.000000,1.000000'
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
Set-ObjectDefault $setEffect 'Effect' $FOOT_SMOKE

$activate = New-Call $COMPONENT_CLASS 'Activate' $false ($x + 800) $y
Add-Pin $activate 'self' 'in' 'object' '' $COMPONENT_CLASS
Add-Pin $activate 'bReset' 'in' 'bool' '' $null 'false'
$life = New-Call $ACTOR 'SetLifeSpan' $false ($x + 1100) $y
Add-Pin $life 'self' 'in' 'object' '' $ACTOR
Add-Pin $life 'InLifespan' 'in' 'real' 'float' $null $EMITTER_LIFETIME

Connect $location 'ReturnValue' $transformNode 'Location'
Connect $transformNode 'ReturnValue' $spawnNode 'SpawnTransform'
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
$text = $sb.ToString()
if ($text.Contains('@{')) { throw 'A node object leaked into a pin or reference (variable name collision)' }
$names = [regex]::Matches($text, '(?m)^Begin Object Class=\S+ Name="(\w+)"') | ForEach-Object { $_.Groups[1].Value }
foreach ($m in [regex]::Matches($text, 'LinkedTo=\(([^)]*)\)')) {
  foreach ($link in ($m.Groups[1].Value -split ',' | Where-Object { $_ })) {
    if ($names -notcontains ($link -split ' ')[0]) { throw "Dangling link: $link" }
  }
}
[IO.File]::WriteAllText((Join-Path $OutDir 'BP_FallingFloor_RespawnEffect.txt'), $text, [Text.UTF8Encoding]::new($false))
"Generated $($script:nodes.Count) nodes"
