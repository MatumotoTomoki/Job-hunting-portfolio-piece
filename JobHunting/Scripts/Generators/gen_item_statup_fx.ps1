param([string]$OutDir, [string]$EffectName = 'StatUp', [string]$OutFile = 'BP_2jump_StatUpEffect.txt')
# Generates Ctrl+V-pasteable node text: an effect at the player's feet when an item is taken, following the player.
# Ends in its own DestroyActor, so hooking it up takes one line and the old DestroyActor gets deleted.

# Reuse the node helpers (constants + functions) from the height BGM generator.
$helpers = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_height_bgm.ps1') -Encoding UTF8 |
  Select-Object -Skip 3 -First 124
. ([ScriptBlock]::Create(($helpers -join "`n")))
# Stay clear of the node names already in the item's graph.
$script:counter = 900

$CHARACTER = "/Script/CoreUObject.Class'/Script/Engine.Character'"
$CAPSULE_CLASS = "/Script/CoreUObject.Class'/Script/Engine.CapsuleComponent'"
$COMPONENT_CLASS = "/Script/CoreUObject.Class'/Script/Engine.ActorComponent'"
$TRANSFORM_STRUCT = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Transform'"
$ROTATOR_STRUCT = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Rotator'"
$SPAWN_COLLISION = "/Script/CoreUObject.Enum'/Script/Engine.ESpawnActorCollisionHandlingMethod'"
$ATTACH_RULE = "/Script/CoreUObject.Enum'/Script/Engine.EAttachmentRule'"
$EMITTER_COMP = "/Script/CoreUObject.Class'/Script/Effekseer.EffekseerEmitterComponent'"
$EFFECT_CLASS = "/Script/CoreUObject.Class'/Script/Effekseer.EffekseerEffect'"
$EMITTER_BP = "/Script/Engine.BlueprintGeneratedClass'/Effekseer/BluePrints/BP_EffekseerEmitter.BP_EffekseerEmitter_C'"
$STAT_UP = "/Game/FX/Effekseer/$EffectName.$EffectName"
# Seconds the spawned emitter lives; must outlast the effect (120 frames, about 2 seconds).
$EMITTER_LIFETIME = '5.000000'

$script:objectDefaults = @{}
function Set-ObjectDefault($node, $pinName, $path) { $script:objectDefaults[(Get-Pin $node $pinName).Id] = $path }

$x = 1400; $y = 0

$playerNode = New-Call $STATICS 'GetPlayerCharacter' $true ($x - 1400) ($y + 500)
Add-Pin $playerNode 'PlayerIndex' 'in' 'int' '' $null '0'
Add-Pin $playerNode 'ReturnValue' 'out' 'object' '' $CHARACTER

# Actor location moved down by the capsule half height, i.e. the point under the character's feet.
$location = New-Call $ACTOR 'K2_GetActorLocation' $true ($x - 1100) ($y + 300)
Add-Pin $location 'self' 'in' 'object' '' $ACTOR
Add-Pin $location 'ReturnValue' 'out' 'struct' '' $VECTOR
$breakNode = New-Call $MATH 'BreakVector' $true ($x - 850) ($y + 300)
Add-Pin $breakNode 'InVec' 'in' 'struct' '' $VECTOR
Add-Pin $breakNode 'X' 'out' 'real' 'double'
Add-Pin $breakNode 'Y' 'out' 'real' 'double'
Add-Pin $breakNode 'Z' 'out' 'real' 'double'
$capsuleGet = New-VarGet 'CapsuleComponent' $CHARACTER 'object' '' $CAPSULE_CLASS ($x - 1100) ($y + 550)
$half = New-Call $CAPSULE_CLASS 'GetScaledCapsuleHalfHeight' $true ($x - 850) ($y + 550)
Add-Pin $half 'self' 'in' 'object' '' $CAPSULE_CLASS
Add-Pin $half 'ReturnValue' 'out' 'real' 'float'
$down = New-Operator 'Subtract' 'Subtract_DoubleDouble' 'real' 'double' 'real' ($x - 600) ($y + 450)
(Get-Pin $down 'ReturnValue').Sub = 'double'
$feet = New-Call $MATH 'MakeVector' $true ($x - 400) ($y + 300)
Add-Pin $feet 'X' 'in' 'real' 'double' $null '0.0'
Add-Pin $feet 'Y' 'in' 'real' 'double' $null '0.0'
Add-Pin $feet 'Z' 'in' 'real' 'double' $null '0.0'
Add-Pin $feet 'ReturnValue' 'out' 'struct' '' $VECTOR
$transformNode = New-Call $MATH 'MakeTransform' $true ($x - 200) ($y + 300)
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

# KeepWorld keeps the feet position as the offset, and the emitter then moves with the player.
$attach = New-Call $ACTOR 'K2_AttachToActor' $false ($x + 400) $y
Add-Pin $attach 'self' 'in' 'object' '' $ACTOR
Add-Pin $attach 'ParentActor' 'in' 'object' '' $ACTOR
Add-Pin $attach 'SocketName' 'in' 'name' '' $null 'None'
Add-Pin $attach 'LocationRule' 'in' 'byte' '' $ATTACH_RULE 'KeepWorld'
Add-Pin $attach 'RotationRule' 'in' 'byte' '' $ATTACH_RULE 'KeepWorld'
Add-Pin $attach 'ScaleRule' 'in' 'byte' '' $ATTACH_RULE 'KeepWorld'
Add-Pin $attach 'bWeldSimulatedBodies' 'in' 'bool' '' $null 'false'
Add-Pin $attach 'ReturnValue' 'out' 'bool'

$emitterGet = New-Call $ACTOR 'GetComponentByClass' $true ($x + 750) ($y + 300)
Add-Pin $emitterGet 'self' 'in' 'object' '' $ACTOR
Add-Pin $emitterGet 'ComponentClass' 'in' 'class' '' $COMPONENT_CLASS
Add-Pin $emitterGet 'ReturnValue' 'out' 'object' '' $EMITTER_COMP
Set-ObjectDefault $emitterGet 'ComponentClass' '/Script/Effekseer.EffekseerEmitterComponent'

$setEffect = New-VarSet 'Effect' $EMITTER_COMP 'object' $EFFECT_CLASS ($x + 800) $y
Set-ObjectDefault $setEffect 'Effect' $STAT_UP

$activate = New-Call $COMPONENT_CLASS 'Activate' $false ($x + 1200) $y
Add-Pin $activate 'self' 'in' 'object' '' $COMPONENT_CLASS
Add-Pin $activate 'bReset' 'in' 'bool' '' $null 'false'
$life = New-Call $ACTOR 'SetLifeSpan' $false ($x + 1500) $y
Add-Pin $life 'self' 'in' 'object' '' $ACTOR
Add-Pin $life 'InLifespan' 'in' 'real' 'float' $null $EMITTER_LIFETIME
# The item removes itself last: this graph runs on it.
$destroyNode = New-Call $null 'K2_DestroyActor' $false ($x + 1800) $y

Connect $playerNode 'ReturnValue' $location 'self'
Connect $playerNode 'ReturnValue' $capsuleGet 'self'
Connect $location 'ReturnValue' $breakNode 'InVec'
Connect $capsuleGet 'CapsuleComponent' $half 'self'
Connect $breakNode 'Z' $down 'A'
Connect $half 'ReturnValue' $down 'B'
Connect $breakNode 'X' $feet 'X'
Connect $breakNode 'Y' $feet 'Y'
Connect $down 'ReturnValue' $feet 'Z'
Connect $feet 'ReturnValue' $transformNode 'Location'
Connect $transformNode 'ReturnValue' $spawnNode 'SpawnTransform'
Connect $spawnNode 'then' $attach 'execute'
Connect $spawnNode 'ReturnValue' $attach 'self'
Connect $playerNode 'ReturnValue' $attach 'ParentActor'
Connect $attach 'then' $setEffect 'execute'
Connect $spawnNode 'ReturnValue' $emitterGet 'self'
Connect $emitterGet 'ReturnValue' $setEffect 'self'
Connect $setEffect 'then' $activate 'execute'
Connect $emitterGet 'ReturnValue' $activate 'self'
Connect $activate 'then' $life 'execute'
Connect $spawnNode 'ReturnValue' $life 'self'
Connect $life 'then' $destroyNode 'execute'

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
[IO.File]::WriteAllText((Join-Path $OutDir $OutFile), $text, [Text.UTF8Encoding]::new($false))
"Generated $($script:nodes.Count) nodes"
