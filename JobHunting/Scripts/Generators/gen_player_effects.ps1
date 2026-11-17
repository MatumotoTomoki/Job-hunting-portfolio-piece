param([string]$OutDir)
# Generates Ctrl+V-pasteable node text: Effekseer effects for jump, double jump and landing.
# The jump chain is hooked to the free exec output of the OnJumped PlaySound2D by hand: that section
# shares data links with the Tick logic, so re-emitting it would mean replacing most of the graph.
# Effects go through a spawned BP_EffekseerEmitter: only an emitter draws its effect. Calling Play on
# the system component runs the effect without anything drawing it.

# Reuse the node helpers (constants + functions) from the height BGM generator.
$helpers = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_height_bgm.ps1') -Encoding UTF8 |
  Select-Object -Skip 3 -First 124
. ([ScriptBlock]::Create(($helpers -join "`n")))
# Stay clear of the node names already in the exported character graph.
$script:counter = 900

# PowerShell variables are case-insensitive: locals below must not reuse these names.
$CHARACTER = "/Script/CoreUObject.Class'/Script/Engine.Character'"
$CAPSULE_CLASS = "/Script/CoreUObject.Class'/Script/Engine.CapsuleComponent'"
$COMPONENT_CLASS = "/Script/CoreUObject.Class'/Script/Engine.ActorComponent'"
$HIT_STRUCT = "/Script/CoreUObject.ScriptStruct'/Script/Engine.HitResult'"
$TRANSFORM_STRUCT = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Transform'"
$ROTATOR_STRUCT = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Rotator'"
$SPAWN_COLLISION = "/Script/CoreUObject.Enum'/Script/Engine.ESpawnActorCollisionHandlingMethod'"
$EMITTER_COMP = "/Script/CoreUObject.Class'/Script/Effekseer.EffekseerEmitterComponent'"
$EFFECT_CLASS = "/Script/CoreUObject.Class'/Script/Effekseer.EffekseerEffect'"
$EMITTER_BP = "/Script/Engine.BlueprintGeneratedClass'/Effekseer/BluePrints/BP_EffekseerEmitter.BP_EffekseerEmitter_C'"
$PUFF = '/Game/FX/Effekseer/NS_JumpPuff.NS_JumpPuff'
$FEATHER = '/Game/FX/Effekseer/NS_DoubleJumpFeather.NS_DoubleJumpFeather'
$NORMAL_SCALE = '1.000000,1.000000,1.000000'
$LAND_SCALE = '1.300000,1.300000,1.300000'
# Seconds each spawned emitter lives; must outlast the longest effect.
$EMITTER_LIFETIME = '5.000000'

# Object pins take their asset as DefaultObject, which Format-Pin does not write.
$script:objectDefaults = @{}
function Set-ObjectDefault($node, $pinName, $path) { $script:objectDefaults[(Get-Pin $node $pinName).Id] = $path }

# Actor location moved down by the capsule half height, i.e. the point under the character's feet.
function New-FeetLocation($x, $y) {
  $location = New-Call $null 'K2_GetActorLocation' $true $x $y
  Add-Pin $location 'ReturnValue' 'out' 'struct' '' $VECTOR
  $break = New-Call $MATH 'BreakVector' $true ($x + 250) $y
  Add-Pin $break 'InVec' 'in' 'struct' '' $VECTOR
  Add-Pin $break 'X' 'out' 'real' 'double'
  Add-Pin $break 'Y' 'out' 'real' 'double'
  Add-Pin $break 'Z' 'out' 'real' 'double'
  $capsuleGet = New-VarGet 'CapsuleComponent' $null 'object' '' $CAPSULE_CLASS $x ($y + 200)
  $half = New-Call $CAPSULE_CLASS 'GetScaledCapsuleHalfHeight' $true ($x + 250) ($y + 200)
  Add-Pin $half 'self' 'in' 'object' '' $CAPSULE_CLASS
  Add-Pin $half 'ReturnValue' 'out' 'real' 'float'
  $down = New-Operator 'Subtract' 'Subtract_DoubleDouble' 'real' 'double' 'real' ($x + 500) ($y + 100)
  (Get-Pin $down 'ReturnValue').Sub = 'double'
  $feet = New-Call $MATH 'MakeVector' $true ($x + 700) $y
  Add-Pin $feet 'X' 'in' 'real' 'double' $null '0.0'
  Add-Pin $feet 'Y' 'in' 'real' 'double' $null '0.0'
  Add-Pin $feet 'Z' 'in' 'real' 'double' $null '0.0'
  Add-Pin $feet 'ReturnValue' 'out' 'struct' '' $VECTOR
  Connect $location 'ReturnValue' $break 'InVec'
  Connect $capsuleGet 'CapsuleComponent' $half 'self'
  Connect $break 'Z' $down 'A'
  Connect $half 'ReturnValue' $down 'B'
  Connect $break 'X' $feet 'X'
  Connect $break 'Y' $feet 'Y'
  Connect $down 'ReturnValue' $feet 'Z'
  return $feet
}

# SpawnActor(BP_EffekseerEmitter) at the feet + its emitter component. It stays where it spawned, so
# the effect does not follow the character.
function New-EmitterSpawn($scaleValue, $x, $y) {
  $spawnNode = New-Node '/Script/BlueprintGraph.K2Node_SpawnActorFromClass' @() $x $y
  Add-Exec $spawnNode
  Add-Pin $spawnNode 'Class' 'in' 'class' '' $ACTOR
  Add-Pin $spawnNode 'SpawnTransform' 'in' 'struct' '' $TRANSFORM_STRUCT
  Add-Pin $spawnNode 'CollisionHandlingOverride' 'in' 'byte' '' $SPAWN_COLLISION 'AlwaysSpawn'
  Add-Pin $spawnNode 'ReturnValue' 'out' 'object' '' $EMITTER_BP
  Set-ObjectDefault $spawnNode 'Class' '/Effekseer/BluePrints/BP_EffekseerEmitter.BP_EffekseerEmitter_C'
  $feetNode = New-FeetLocation ($x - 1100) ($y + 300)
  $transformNode = New-Call $MATH 'MakeTransform' $true ($x - 200) ($y + 300)
  Add-Pin $transformNode 'Location' 'in' 'struct' '' $VECTOR
  Add-Pin $transformNode 'Rotation' 'in' 'struct' '' $ROTATOR_STRUCT '0,0,0'
  Add-Pin $transformNode 'Scale' 'in' 'struct' '' $VECTOR $scaleValue
  Add-Pin $transformNode 'ReturnValue' 'out' 'struct' '' $TRANSFORM_STRUCT
  $emitterGet = New-Call $ACTOR 'GetComponentByClass' $true ($x + 350) ($y + 300)
  Add-Pin $emitterGet 'self' 'in' 'object' '' $ACTOR
  Add-Pin $emitterGet 'ComponentClass' 'in' 'class' '' $COMPONENT_CLASS
  Add-Pin $emitterGet 'ReturnValue' 'out' 'object' '' $EMITTER_COMP
  Set-ObjectDefault $emitterGet 'ComponentClass' '/Script/Effekseer.EffekseerEmitterComponent'
  Connect $feetNode 'ReturnValue' $transformNode 'Location'
  Connect $transformNode 'ReturnValue' $spawnNode 'SpawnTransform'
  Connect $spawnNode 'ReturnValue' $emitterGet 'self'
  return @($spawnNode, $emitterGet)
}

function New-SetEffect($effectPath, $emitterGet, $x, $y) {
  $setNode = New-VarSet 'Effect' $EMITTER_COMP 'object' $EFFECT_CLASS $x $y
  Set-ObjectDefault $setNode 'Effect' $effectPath
  Connect $emitterGet 'ReturnValue' $setNode 'self'
  return $setNode
}

# Activate -> SetLifeSpan: starts the effect, then removes the emitter once it has finished.
function New-StartEmitter($spawnNode, $emitterGet, $x, $y) {
  $activate = New-Call $COMPONENT_CLASS 'Activate' $false $x $y
  Add-Pin $activate 'self' 'in' 'object' '' $COMPONENT_CLASS
  Add-Pin $activate 'bReset' 'in' 'bool' '' $null 'false'
  $life = New-Call $ACTOR 'SetLifeSpan' $false ($x + 300) $y
  Add-Pin $life 'self' 'in' 'object' '' $ACTOR
  Add-Pin $life 'InLifespan' 'in' 'real' 'float' $null $EMITTER_LIFETIME
  Connect $emitterGet 'ReturnValue' $activate 'self'
  Connect $activate 'then' $life 'execute'
  Connect $spawnNode 'ReturnValue' $life 'self'
  return $activate
}

# --- Jump: the free exec of the OnJumped PlaySound2D connects to $jumpSpawn by hand ------
$jumpX = 4500; $jumpY = 1088
$jumpParts = New-EmitterSpawn $NORMAL_SCALE $jumpX $jumpY
$jumpSpawn = $jumpParts[0]; $jumpEmitter = $jumpParts[1]
# JumpCurrentCount is already counted up when OnJumped fires: 1 = first jump, 2 = double jump.
$jumpCount = New-VarGet 'JumpCurrentCount' $null 'int' '' $null ($jumpX + 150) ($jumpY + 500)
$isDouble = New-Operator 'GreaterEqual' 'GreaterEqual_IntInt' 'int' '' 'bool' ($jumpX + 400) ($jumpY + 500)
(Get-Pin $isDouble 'B').Default = '2'
$choose = New-Branch ($jumpX + 650) $jumpY
$setFeather = New-SetEffect $FEATHER $jumpEmitter ($jumpX + 950) ($jumpY - 100)
$setPuff = New-SetEffect $PUFF $jumpEmitter ($jumpX + 950) ($jumpY + 150)
$jumpActivate = New-StartEmitter $jumpSpawn $jumpEmitter ($jumpX + 1350) $jumpY
Connect $jumpSpawn 'then' $choose 'execute'
Connect $jumpCount 'JumpCurrentCount' $isDouble 'A'
Connect $isDouble 'ReturnValue' $choose 'Condition'
Connect $choose 'then' $setFeather 'execute'
Connect $choose 'else' $setPuff 'execute'
Connect $setFeather 'then' $jumpActivate 'execute'
Connect $setPuff 'then' $jumpActivate 'execute'

# --- Landing: same effect as the jump, a little larger ---------------------------------
$landX = 3200; $landY = 2000
$landed = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$CHARACTER`",MemberName=`"OnLanded`")", 'bOverrideFunction=True') ($landX - 300) $landY
Add-Pin $landed 'then' 'out' 'exec'
Add-Pin $landed 'Hit' 'out' 'struct' '' $HIT_STRUCT
$landParts = New-EmitterSpawn $LAND_SCALE $landX $landY
$landSpawn = $landParts[0]; $landEmitter = $landParts[1]
$setLand = New-SetEffect $PUFF $landEmitter ($landX + 400) $landY
$landActivate = New-StartEmitter $landSpawn $landEmitter ($landX + 800) $landY
Connect $landed 'then' $landSpawn 'execute'
Connect $landSpawn 'then' $setLand 'execute'
Connect $setLand 'then' $landActivate 'execute'

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
# Every link must land on a node in this paste; nothing can link to the existing graph.
$names = [regex]::Matches($text, '(?m)^Begin Object Class=\S+ Name="(\w+)"') | ForEach-Object { $_.Groups[1].Value }
foreach ($m in [regex]::Matches($text, 'LinkedTo=\(([^)]*)\)')) {
  foreach ($link in ($m.Groups[1].Value -split ',' | Where-Object { $_ })) {
    if ($names -notcontains ($link -split ' ')[0]) { throw "Dangling link: $link" }
  }
}
[IO.File]::WriteAllText((Join-Path $OutDir 'PlayerEffects_Character.txt'), $text, [Text.UTF8Encoding]::new($false))
"Generated $($script:nodes.Count) nodes; start of jump chain: $($jumpSpawn.Name)"
