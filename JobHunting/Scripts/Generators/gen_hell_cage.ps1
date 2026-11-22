param([string]$OutDir)
# Paste text for the heaven-or-hell cage pair (variables and assets from setup_hell_cage.py):
#   BP_BirdcageDoor_Blender_EventGraph.txt  the cage graph as exported (bp_export/cage.txt), plus one branch: once the
#       screen is black and the cage has risen, a ToHell cage saves the run's state and opens HellLevel instead of
#       carrying the player to its Destination.
#   BP_CagePair_EventGraph.txt  Begin Play: the run's HellSeed (picked by the first pair to start) decides, by its
#       PairId'th bit, whether CageA or CageB is the hell one. Back from hell (ReturnFromHell, same PairId): the item
#       effects come back and the player stands at the right cage's Destination as the screen clears.
#   BP_HellExit_EventGraph.txt  Begin Play: the item effects come back and the screen clears. Stepping in: the effects
#       are saved, ReturnFromHell is set, the screen goes black and ReturnLevel opens.
$helperFile = (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_height_bgm.ps1')
$helpers = Get-Content -LiteralPath $helperFile -Encoding UTF8 | Select-Object -Skip 3 -First 124
. ([ScriptBlock]::Create(($helpers -join "`n")))

# Const-ref inputs (const FString&) need bIsReference/bIsConst on the pin, or the pasted link is refused.
function Format-Pin($p) {
  $obj = if ($p.Obj) { "`"$($p.Obj)`"" } else { 'None' }
  $ref = if ($p.PSObject.Properties['ConstRef'] -and $p.ConstRef) { 'True' } else { 'False' }
  $s = "PinId=$($p.Id),PinName=`"$($p.Name)`","
  if ($p.Dir -eq 'out') { $s += 'Direction="EGPD_Output",' }
  $s += "PinType.PinCategory=`"$($p.Cat)`",PinType.PinSubCategory=`"$($p.Sub)`",PinType.PinSubCategoryObject=$obj,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=$($p.Container),PinType.bIsReference=$ref,PinType.bIsConst=$ref,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,"
  if ($null -ne $p.Default) { $s += "DefaultValue=`"$($p.Default)`"," }
  if ($p.Links.Count) { $s += 'LinkedTo=(' + (($p.Links | ForEach-Object { "$_," }) -join '') + '),' }
  $s += 'PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,'
  return "   CustomProperties Pin ($s)"
}

$CHARACTER = "/Script/CoreUObject.Class'/Script/Engine.Character'"
$CHAR_MOVE = "/Script/CoreUObject.Class'/Script/Engine.CharacterMovementComponent'"
$CONTROLLER = "/Script/CoreUObject.Class'/Script/Engine.PlayerController'"
$CAMERA_MANAGER = "/Script/CoreUObject.Class'/Script/Engine.PlayerCameraManager'"
$PRIMITIVE = "/Script/CoreUObject.Class'/Script/Engine.PrimitiveComponent'"
$BOX = "/Script/CoreUObject.Class'/Script/Engine.BoxComponent'"
$ROTATOR = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Rotator'"
$HIT = "/Script/CoreUObject.ScriptStruct'/Script/Engine.HitResult'"
$LINEAR = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.LinearColor'"
$STRINGS = "/Script/CoreUObject.Class'/Script/Engine.KismetStringLibrary'"
$CAGE_CLASS = "/Script/Engine.BlueprintGeneratedClass'/Game/Prototype/Birdcage/BP_BirdcageDoor_Blender.BP_BirdcageDoor_Blender_C'"
$GI_OUT = 'AsBP My Game Instance'
$BLACK = '(R=0.000000,G=0.000000,B=0.000000,A=1.000000)'
$STAND = '92.0'          # The player's capsule half height (90) above a Destination on the floor.
$SEED_MAX = '1073741823' # 2^30 - 1: 30 bits, one per PairId 0..29.

function Reset-Graph($start) { $script:nodes = [System.Collections.Generic.List[object]]::new(); $script:counter = $start }
function Chain([object[]]$list) { for ($i = 0; $i -lt $list.Count - 1; $i++) { Connect $list[$i] 'then' $list[$i + 1] 'execute' } }
function Player($x, $y) {
  $n = New-Call $STATICS 'GetPlayerCharacter' $true $x $y
  Add-Pin $n 'PlayerIndex' 'in' 'int' '' $null '0'
  Add-Pin $n 'ReturnValue' 'out' 'object' '' $CHARACTER
  return $n
}
function Controller($x, $y) {
  $n = New-Call $STATICS 'GetPlayerController' $true $x $y
  Add-Pin $n 'PlayerIndex' 'in' 'int' '' $null '0'
  Add-Pin $n 'ReturnValue' 'out' 'object' '' $CONTROLLER
  return $n
}
function Movement($x, $y) {
  $n = New-VarGet 'CharacterMovement' $CHARACTER 'object' '' $CHAR_MOVE $x $y
  Connect (Player ($x - 250) $y) 'ReturnValue' $n 'self'
  return $n
}
# GetGameInstance -> cast to BP_MyGameInstance (an exec node: wire its 'then' on).
function GameInstance($x, $y) {
  $gi = New-Call $STATICS 'GetGameInstance' $true ($x - 250) ($y + 200)
  Add-Pin $gi 'ReturnValue' 'out' 'object' '' $GAMEINST
  $cast = New-Node '/Script/BlueprintGraph.K2Node_DynamicCast' @("TargetType=`"$GI_CLASS`"") $x $y
  Add-Exec $cast
  Add-Pin $cast 'CastFailed' 'out' 'exec'
  Add-Pin $cast 'Object' 'in' 'object' '' $OBJECT
  Add-Pin $cast $GI_OUT 'out' 'object' '' $GI_CLASS
  Add-Pin $cast 'bSuccess' 'out' 'bool'
  Connect $gi 'ReturnValue' $cast 'Object'
  return $cast
}
function GiGet($cast, $name, $cat, $sub, $x, $y) {
  $n = New-VarGet $name $GI_CLASS $cat $sub $null $x $y
  Connect $cast $GI_OUT $n 'self'
  return $n
}
function GiSet($cast, $name, $cat, $sub, $x, $y, $value = $null) {
  $n = New-VarSet $name $GI_CLASS $cat $null $x $y
  (Get-Pin $n $name).Sub = $sub; (Get-Pin $n 'Output_Get').Sub = $sub
  if ($null -ne $value) { (Get-Pin $n $name).Default = $value }
  Connect $cast $GI_OUT $n 'self'
  return $n
}
function Fade($from, $to, $seconds, $hold, $x, $y) {
  $camera = New-Call $STATICS 'GetPlayerCameraManager' $true $x ($y + 250)
  Add-Pin $camera 'PlayerIndex' 'in' 'int' '' $null '0'
  Add-Pin $camera 'ReturnValue' 'out' 'object' '' $CAMERA_MANAGER
  $n = New-Call $CAMERA_MANAGER 'StartCameraFade' $false ($x + 250) $y
  Add-Pin $n 'self' 'in' 'object' '' $CAMERA_MANAGER
  Add-Pin $n 'FromAlpha' 'in' 'real' 'float' $null $from
  Add-Pin $n 'ToAlpha' 'in' 'real' 'float' $null $to
  Add-Pin $n 'Duration' 'in' 'real' 'float' $null $seconds
  Add-Pin $n 'Color' 'in' 'struct' '' $LINEAR $BLACK
  Add-Pin $n 'bShouldFadeAudio' 'in' 'bool' '' $null 'false'
  Add-Pin $n 'bHoldWhenFinished' 'in' 'bool' '' $null $hold
  Connect $camera 'ReturnValue' $n 'self'
  return $n
}
function Delay($seconds, $x, $y) {
  $n = New-Call $SYSTEM 'Delay' $false $x $y
  Add-Pin $n 'Duration' 'in' 'real' 'float' $null $seconds
  return $n
}
# The item effects into the game instance; returns (first, last).
function SaveStats($cast, $x, $y) {
  $speed = GiSet $cast 'SavedWalkSpeed' 'real' 'double' $x $y
  $speedNow = New-VarGet 'MaxWalkSpeed' $CHAR_MOVE 'real' 'float' $null ($x - 50) ($y + 250)
  Connect (Movement ($x - 300) ($y + 250)) 'CharacterMovement' $speedNow 'self'
  Connect $speedNow 'MaxWalkSpeed' $speed 'SavedWalkSpeed'
  $jump = GiSet $cast 'SavedJumpZ' 'real' 'double' ($x + 300) $y
  $jumpNow = New-VarGet 'JumpZVelocity' $CHAR_MOVE 'real' 'float' $null ($x + 250) ($y + 350)
  Connect (Movement ($x) ($y + 350)) 'CharacterMovement' $jumpNow 'self'
  Connect $jumpNow 'JumpZVelocity' $jump 'SavedJumpZ'
  $count = GiSet $cast 'SavedJumpCount' 'int' '' ($x + 600) $y
  $countNow = New-VarGet 'JumpMaxCount' $CHARACTER 'int' '' $null ($x + 550) ($y + 450)
  Connect (Player ($x + 300) ($y + 450)) 'ReturnValue' $countNow 'self'
  Connect $countNow 'JumpMaxCount' $count 'SavedJumpCount'
  $has = GiSet $cast 'HasSavedStats' 'bool' '' ($x + 900) $y 'true'
  Chain @($speed, $jump, $count, $has)
  return @($speed, $has)
}
# The saved item effects back onto the player, if any were saved; returns (first, last) — the last's 'then' and the
# branch's 'else' both lead on, so wire $result[2] (the branch) 'else' as well.
function RestoreStats($cast, $x, $y) {
  $branch = New-Branch $x $y
  Connect (GiGet $cast 'HasSavedStats' 'bool' '' ($x - 200) ($y + 200)) 'HasSavedStats' $branch 'Condition'
  $speed = New-VarSet 'MaxWalkSpeed' $CHAR_MOVE 'real' $null ($x + 300) $y
  (Get-Pin $speed 'MaxWalkSpeed').Sub = 'float'; (Get-Pin $speed 'Output_Get').Sub = 'float'
  Connect (Movement ($x + 50) ($y + 250)) 'CharacterMovement' $speed 'self'
  Connect (GiGet $cast 'SavedWalkSpeed' 'real' 'double' ($x + 100) ($y + 350)) 'SavedWalkSpeed' $speed 'MaxWalkSpeed'
  $jump = New-VarSet 'JumpZVelocity' $CHAR_MOVE 'real' $null ($x + 650) $y
  (Get-Pin $jump 'JumpZVelocity').Sub = 'float'; (Get-Pin $jump 'Output_Get').Sub = 'float'
  Connect (Movement ($x + 400) ($y + 250)) 'CharacterMovement' $jump 'self'
  Connect (GiGet $cast 'SavedJumpZ' 'real' 'double' ($x + 450) ($y + 350)) 'SavedJumpZ' $jump 'JumpZVelocity'
  $count = New-VarSet 'JumpMaxCount' $CHARACTER 'int' $null ($x + 1000) $y
  Connect (Player ($x + 750) ($y + 250)) 'ReturnValue' $count 'self'
  Connect (GiGet $cast 'SavedJumpCount' 'int' '' ($x + 800) ($y + 350)) 'SavedJumpCount' $count 'JumpMaxCount'
  Connect $branch 'then' $speed 'execute'
  Chain @($speed, $jump, $count)
  return @($branch, $count)
}
function OpenLevel($x, $y) {
  $n = New-Call $STATICS 'OpenLevel' $false $x $y
  Add-Pin $n 'LevelName' 'in' 'name' '' $null 'None'
  Add-Pin $n 'bAbsolute' 'in' 'bool' '' $null 'true'
  Add-Pin $n 'Options' 'in' 'string' '' $null ''
  return $n
}
function Write-Graph($file, [string[]]$extraNames = @(), [string]$prefix = '') {
  $sb = [System.Text.StringBuilder]::new()
  if ($prefix) { [void]$sb.Append($prefix) }
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
  if ($text.Contains('@{')) { throw "$file : a node object leaked into a pin" }
  $names = [regex]::Matches($text, '(?m)^Begin Object Class=\S+ Name="(\w+)"') | ForEach-Object { $_.Groups[1].Value }
  if (($names | Sort-Object -Unique).Count -ne $names.Count) { throw "$file : duplicate node names" }
  foreach ($m in [regex]::Matches($text, 'LinkedTo=\(([^)]*)\)')) {
    foreach ($link in ($m.Groups[1].Value -split ',' | Where-Object { $_ })) {
      if ($names -notcontains ($link -split ' ')[0]) { throw "$file : dangling link $link" }
    }
  }
  foreach ($n in $script:nodes) {
    foreach ($p in $n.Pins) {
      if ($p.Cat -eq 'exec' -and $p.Dir -eq 'out' -and $p.Links.Count -gt 1) { throw "$file : exec output with several links: $($n.Name).$($p.Name)" }
      if ($p.Cat -eq 'exec' -and $p.Dir -eq 'in' -and $p.Links.Count -eq 0 -and $n.Class -notmatch 'K2Node_Event') { throw "$file : unreached node $($n.Name)" }
    }
  }
  [IO.File]::WriteAllText((Join-Path (Resolve-Path -LiteralPath $OutDir).Path $file), $text, [Text.UTF8Encoding]::new($false))   # (absolute: .NET resolves relative paths from its own directory, not PowerShell's)
  "$file : $($names.Count) nodes"
}

# ===== 1. The cage: one branch after the cage has risen into the dark ======================================
# (Header lines above are counted by other generators - Skip 10 -First 172 - so notes go here, not there.)
# Sounds and effect spliced in too (setup_cage_effects.py, 2026-11-22): Begin Play sets their volume; the door's
# creak as it swings (DoorSound), the slam as it shuts on the player (LockSound), the haul up (RiseSound), the
# set-down at the destination (LandSound + LandFx).
$export = Get-Content -LiteralPath (Join-Path $OutDir 'bp_export\cage.txt') -Raw -Encoding UTF8
$export = [regex]::Replace($export, ' ExportPath="[^"]*"', '')
$RISE_THEN = 'K2Node_CallFunction_145 DAD13812773841D08F3946BCCC4F8E4C'      # MoveComponentTo (the cage rises) 'then'
$CARRY_EXEC = 'K2Node_CallFunction_149 F6F1C5F26D2D4E56B1A44E2F628BA0C4'     # SetActorLocationAndRotation 'execute'
foreach ($needle in @("LinkedTo=($CARRY_EXEC,)", "LinkedTo=($RISE_THEN,)")) {
  if (([regex]::Matches($export, [regex]::Escape($needle))).Count -ne 1) { throw "cage.txt changed: $needle" }
}
Reset-Graph 900
$toHell = New-Branch 2400 600
Connect (New-VarGet 'ToHell' $null 'bool' '' $null 2250 800) 'ToHell' $toHell 'Condition'
(Get-Pin $toHell 'execute').Links.Add($RISE_THEN)
(Get-Pin $toHell 'else').Links.Add($CARRY_EXEC)
$cast = GameInstance 2700 400
Connect $toHell 'then' $cast 'execute'
$saved = SaveStats $cast 3000 400
$pairId = GiSet $cast 'HellPairId' 'int' '' 4200 400
Connect (New-VarGet 'PairId' $null 'int' '' $null 4000 650) 'PairId' $pairId 'HellPairId'
$fromHell = GiSet $cast 'ReturnFromHell' 'bool' '' 4500 400 'false'
$returnTo = GiSet $cast 'ReturnLevel' 'name' '' 4800 400
# (Not pure: pasted as pure it was pruned for its unwired exec pins and ReturnLevel was left None - 2026-11-22.)
$levelName = New-Call $STATICS 'GetCurrentLevelName' $false 4300 900
Add-Pin $levelName 'bRemovePrefixString' 'in' 'bool' '' $null 'true'
Add-Pin $levelName 'ReturnValue' 'out' 'string'
$asName = New-Call $STRINGS 'Conv_StringToName' $true 4600 900
Add-Pin $asName 'InString' 'in' 'string'
(Get-Pin $asName 'InString') | Add-Member -NotePropertyName ConstRef -NotePropertyValue $true
Add-Pin $asName 'ReturnValue' 'out' 'name'
Connect $levelName 'ReturnValue' $asName 'InString'
Connect $asName 'ReturnValue' $returnTo 'ReturnLevel'
$open = OpenLevel 5100 400
Connect (New-VarGet 'HellLevel' $null 'name' '' $null 4900 650) 'HellLevel' $open 'LevelName'
Connect $cast 'then' $saved[0] 'execute'
Chain @($saved[1], $pairId, $fromHell, $levelName, $returnTo, $open)
$export = $export.Replace("LinkedTo=($CARRY_EXEC,)", "LinkedTo=($($toHell.Name) $((Get-Pin $toHell 'execute').Id),)")
$export = $export.Replace("LinkedTo=($RISE_THEN,)", "LinkedTo=($($toHell.Name) $((Get-Pin $toHell 'else').Id),)")
# --- Sounds and effect (setup_cage_effects.py, 2026-11-22), spliced into the exported graph's exec wires ---
$AUDIO_COMP = "/Script/CoreUObject.Class'/Script/Engine.AudioComponent'"
$ACTOR_COMP = "/Script/CoreUObject.Class'/Script/Engine.ActorComponent'"
$EMITTER = "/Script/CoreUObject.Class'/Script/Effekseer.EffekseerEmitterComponent'"
function SoundPlay($name, [double]$x, [double]$y) {
  $n = New-Call $AUDIO_COMP 'Play' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $AUDIO_COMP
  Add-Pin $n 'StartTime' 'in' 'real' 'float' $null '0.0'
  Connect (New-VarGet $name $null 'object' '' $AUDIO_COMP ($x - 200) ($y + 200)) $name $n 'self'
  return $n
}
function FxPlay($name, [double]$x, [double]$y) {
  $n = New-Call $ACTOR_COMP 'Activate' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR_COMP
  Add-Pin $n 'bReset' 'in' 'bool' '' $null 'true'
  Connect (New-VarGet $name $null 'object' '' $EMITTER ($x - 200) ($y + 200)) $name $n 'self'
  return $n
}
# Puts the chain $nodes (first 'execute' ... last 'then') on the exported node's exec output $pinName: it now runs
# them, then whatever that output ran before (if anything).
function Splice($nodeName, $pinName, [object[]]$nodes) {
  $block = [regex]::Match($script:export, "(?ms)^Begin Object Class=\S+ Name=`"$nodeName`".*?^End Object")
  if (-not $block.Success) { throw "cage.txt changed: no $nodeName" }
  $line = [regex]::Match($block.Value, "CustomProperties Pin \(PinId=(\w+),PinName=`"$pinName`",[^\r\n]*")
  if (-not $line.Success -or $line.Value -notmatch 'Direction="EGPD_Output"') { throw "cage.txt changed: no $nodeName.$pinName" }
  $pinId = $line.Groups[1].Value
  $first = $nodes[0]; $last = $nodes[-1]
  Chain $nodes
  $firstIn = Get-Pin $first 'execute'
  $firstIn.Links.Add("$nodeName $pinId")
  $newLine = $line.Value
  $old = [regex]::Match($line.Value, 'LinkedTo=\(([^)]*)\)')
  if ($old.Success) {
    $targets = @($old.Groups[1].Value -split ',' | Where-Object { $_ })
    if ($targets.Count -ne 1) { throw "$nodeName.$pinName has $($targets.Count) links" }
    (Get-Pin $last 'then').Links.Add($targets[0])
    $newLine = $newLine.Replace($old.Value, "LinkedTo=($($first.Name) $($firstIn.Id),)")
    # The old target now hears from the chain's end instead.
    $script:export = $script:export.Replace("$nodeName $pinId,", "$($last.Name) $((Get-Pin $last 'then').Id),")
  } else {
    $newLine = $newLine.Replace(',PersistentGuid=', ",LinkedTo=($($first.Name) $($firstIn.Id),),PersistentGuid=")
  }
  $script:export = $script:export.Replace($line.Value, $newLine)
}
$script:export = $export
# Begin Play, after Home is noted: the sounds at SE Volume x Master Volume.
$volCast = GameInstance 1200 2600
$vol = New-Operator 'Multiply' 'Multiply_DoubleDouble' 'real' 'double' 'real' 1500 2850
(Get-Pin $vol 'ReturnValue').Sub = 'double'
Connect (GiGet $volCast 'SE Volume' 'real' 'double' 1250 2850) 'SE Volume' $vol 'A'
Connect (GiGet $volCast 'Master Volume' 'real' 'double' 1250 2950) 'Master Volume' $vol 'B'
$volumes = @($volCast); $vx = 1650
foreach ($name in 'DoorSound', 'LockSound', 'RiseSound', 'LandSound') {
  $v = New-Call $AUDIO_COMP 'SetVolumeMultiplier' $false $vx 2600
  Add-Pin $v 'self' 'in' 'object' '' $AUDIO_COMP
  Add-Pin $v 'NewVolumeMultiplier' 'in' 'real' 'float'
  Connect (New-VarGet $name $null 'object' '' $AUDIO_COMP ($vx - 200) 2800) $name $v 'self'
  Connect $vol 'ReturnValue' $v 'NewVolumeMultiplier'
  $volumes += $v; $vx += 300
}
Splice 'K2Node_VariableSet_190' 'then' $volumes
# The door swinging as the player comes and goes, and opening at the destination. (Not as it shuts on the player:
# the LockSound 1 s on is that door, and two clangs a second apart sounded wrong - 2026-11-22.)
Splice 'K2Node_CallFunction_110' 'then' @(SoundPlay 'DoorSound' 1600 3200)
Splice 'K2Node_CallFunction_153' 'then' @(SoundPlay 'DoorSound' 2200 3200)
# Shut (1 s on): the slam and the latch.
Splice 'K2Node_CallFunction_143' 'then' @(SoundPlay 'LockSound' 2500 3200)
# Hauled up into the dark.
Splice 'K2Node_CallFunction_144' 'then' @(SoundPlay 'RiseSound' 2800 3200)
# Set down at the destination: the thud and the dust.
Splice 'K2Node_CallFunction_151' 'then' @((SoundPlay 'LandSound' 3100 3200), (FxPlay 'LandFx' 3400 3200))
$export = $script:export
if (-not $export.EndsWith("`n")) { $export += "`r`n" }
Write-Graph 'BP_BirdcageDoor_Blender_EventGraph.txt' @() $export

# ===== 2. BP_CagePair ======================================================================================
Reset-Graph 100
$begin = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$ACTOR`",MemberName=`"ReceiveBeginPlay`")", 'bOverrideFunction=True') 0 0
Add-Pin $begin 'then' 'out' 'exec'
$cast = GameInstance 300 0
Connect $begin 'then' $cast 'execute'
# The run's seed, once.
$noSeed = New-Branch 600 0
$isZero = New-Operator 'EqualEqual' 'EqualEqual_IntInt' 'int' '' 'bool' 450 200
Connect (GiGet $cast 'HellSeed' 'int' '' 250 200) 'HellSeed' $isZero 'A'
(Get-Pin $isZero 'B').Default = '0'
Connect $isZero 'ReturnValue' $noSeed 'Condition'
Connect $cast 'then' $noSeed 'execute'
$pickSeed = GiSet $cast 'HellSeed' 'int' '' 850 -200
$random = New-Call $MATH 'RandomIntegerInRange' $true 650 -50
Add-Pin $random 'Min' 'in' 'int' '' $null '1'
Add-Pin $random 'Max' 'in' 'int' '' $null $SEED_MAX
Add-Pin $random 'ReturnValue' 'out' 'int'
Connect $random 'ReturnValue' $pickSeed 'HellSeed'
Connect $noSeed 'then' $pickSeed 'execute'
# Bit PairId of the seed: (HellSeed / 2^(PairId % 30)) % 2 == 1 -> CageA is the hell cage.
$wrapped = New-Operator 'Percent' 'Percent_IntInt' 'int' '' 'int' 400 600
Connect (New-VarGet 'PairId' $null 'int' '' $null 200 600) 'PairId' $wrapped 'A'
(Get-Pin $wrapped 'B').Default = '30'
$asReal = New-Call $MATH 'Conv_IntToDouble' $true 600 600
Add-Pin $asReal 'InInt' 'in' 'int'
Add-Pin $asReal 'ReturnValue' 'out' 'real' 'double'
Connect $wrapped 'ReturnValue' $asReal 'InInt'
$power = New-Call $MATH 'MultiplyMultiply_FloatFloat' $true 800 600
Add-Pin $power 'Base' 'in' 'real' 'double' $null '2.0'
Add-Pin $power 'Exp' 'in' 'real' 'double'
Add-Pin $power 'ReturnValue' 'out' 'real' 'double'
Connect $asReal 'ReturnValue' $power 'Exp'
$whole = New-Call $MATH 'FTrunc' $true 1000 600
Add-Pin $whole 'A' 'in' 'real' 'double'
Add-Pin $whole 'ReturnValue' 'out' 'int'
Connect $power 'ReturnValue' $whole 'A'
$shifted = New-Operator 'Divide' 'Divide_IntInt' 'int' '' 'int' 1200 500
Connect (GiGet $cast 'HellSeed' 'int' '' 1000 450) 'HellSeed' $shifted 'A'
Connect $whole 'ReturnValue' $shifted 'B'
$bit = New-Operator 'Percent' 'Percent_IntInt' 'int' '' 'int' 1400 500
Connect $shifted 'ReturnValue' $bit 'A'
(Get-Pin $bit 'B').Default = '2'
$aIsHell = New-Operator 'EqualEqual' 'EqualEqual_IntInt' 'int' '' 'bool' 1600 500
Connect $bit 'ReturnValue' $aIsHell 'A'
(Get-Pin $aIsHell 'B').Default = '1'
$bIsHell = New-Call $MATH 'Not_PreBool' $true 1800 600
Add-Pin $bIsHell 'A' 'in' 'bool'
Add-Pin $bIsHell 'ReturnValue' 'out' 'bool'
Connect $aIsHell 'ReturnValue' $bIsHell 'A'
function Cage($which, $x, $y) { New-VarGet $which $null 'object' '' $CAGE_CLASS $x $y }
function CageSet($which, $name, $cat, $x, $y) {
  $n = New-VarSet $name $CAGE_CLASS $cat $null $x $y
  Connect (Cage $which ($x - 200) ($y + 250)) $which $n 'self'
  return $n
}
$aHell = CageSet 'CageA' 'ToHell' 'bool' 1200 0
Connect $aIsHell 'ReturnValue' $aHell 'ToHell'
$bHell = CageSet 'CageB' 'ToHell' 'bool' 1500 0
Connect $bIsHell 'ReturnValue' $bHell 'ToHell'
$aPair = CageSet 'CageA' 'PairId' 'int' 1800 0
Connect (New-VarGet 'PairId' $null 'int' '' $null 1600 350) 'PairId' $aPair 'PairId'
$bPair = CageSet 'CageB' 'PairId' 'int' 2100 0
Connect (New-VarGet 'PairId' $null 'int' '' $null 1900 350) 'PairId' $bPair 'PairId'
Connect $noSeed 'else' $aHell 'execute'
Connect $pickSeed 'then' $aHell 'execute'
Chain @($aHell, $bHell, $aPair, $bPair)
# Back from this pair's hell?
$back = New-Branch 2400 0
Connect (GiGet $cast 'ReturnFromHell' 'bool' '' 2200 200) 'ReturnFromHell' $back 'Condition'
$mine = New-Branch 2650 0
$samePair = New-Operator 'EqualEqual' 'EqualEqual_IntInt' 'int' '' 'bool' 2500 250
Connect (GiGet $cast 'HellPairId' 'int' '' 2300 300) 'HellPairId' $samePair 'A'
Connect (New-VarGet 'PairId' $null 'int' '' $null 2300 400) 'PairId' $samePair 'B'
Connect $samePair 'ReturnValue' $mine 'Condition'
Connect $bPair 'then' $back 'execute'
Connect $back 'then' $mine 'execute'
$done = GiSet $cast 'ReturnFromHell' 'bool' '' 2900 0 'false'
Connect $mine 'then' $done 'execute'
$clear = Fade '1.0' '0.0' '1.0' 'false' 3150 0
Connect $done 'then' $clear 'execute'
# A moment for the player to be set up before moving them.
$wait = Delay '0.1' 3650 0
Connect $clear 'then' $wait 'execute'
$restore = RestoreStats $cast 3900 0
Connect $wait 'then' $restore[0] 'execute'
# The right cage's Destination: CageB's when CageA is the hell one.
function DestinationOf($which, $what, $type, $x, $y) {
  $dest = New-VarGet 'Destination' $CAGE_CLASS 'object' '' $ACTOR $x $y
  Connect (Cage $which ($x - 200) $y) $which $dest 'self'
  $n = New-Call $ACTOR $what $true ($x + 250) $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR
  Add-Pin $n 'ReturnValue' 'out' 'struct' '' $type
  Connect $dest 'Destination' $n 'self'
  return $n
}
$where = New-Call $MATH 'SelectVector' $true 5000 450
Add-Pin $where 'A' 'in' 'struct' '' $VECTOR
Add-Pin $where 'B' 'in' 'struct' '' $VECTOR
Add-Pin $where 'bPickA' 'in' 'bool'
Add-Pin $where 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect (DestinationOf 'CageB' 'K2_GetActorLocation' $VECTOR 4500 400) 'ReturnValue' $where 'A'
Connect (DestinationOf 'CageA' 'K2_GetActorLocation' $VECTOR 4500 550) 'ReturnValue' $where 'B'
Connect $aIsHell 'ReturnValue' $where 'bPickA'
$up = New-Operator 'Add' 'Add_VectorVector' 'struct' '' 'struct' 5250 450
foreach ($pin in 'A', 'B', 'ReturnValue') { (Get-Pin $up $pin).Obj = $VECTOR }
(Get-Pin $up 'B').Default = "0.000000,0.000000,$STAND"
Connect $where 'ReturnValue' $up 'A'
$facing = New-Call $MATH 'SelectRotator' $true 5000 750
Add-Pin $facing 'A' 'in' 'struct' '' $ROTATOR
Add-Pin $facing 'B' 'in' 'struct' '' $ROTATOR
Add-Pin $facing 'bPickA' 'in' 'bool'
Add-Pin $facing 'ReturnValue' 'out' 'struct' '' $ROTATOR
Connect (DestinationOf 'CageB' 'K2_GetActorRotation' $ROTATOR 4500 750) 'ReturnValue' $facing 'A'
Connect (DestinationOf 'CageA' 'K2_GetActorRotation' $ROTATOR 4500 900) 'ReturnValue' $facing 'B'
Connect $aIsHell 'ReturnValue' $facing 'bPickA'
$place = New-Call $ACTOR 'K2_SetActorLocationAndRotation' $false 5500 0
Add-Pin $place 'self' 'in' 'object' '' $ACTOR
Add-Pin $place 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $place 'NewRotation' 'in' 'struct' '' $ROTATOR
Add-Pin $place 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $place 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $place 'bTeleport' 'in' 'bool' '' $null 'true'
Add-Pin $place 'ReturnValue' 'out' 'bool'
Connect (Player 5250 250) 'ReturnValue' $place 'self'
Connect $up 'ReturnValue' $place 'NewLocation'
Connect $facing 'ReturnValue' $place 'NewRotation'
Connect $restore[0] 'else' $place 'execute'
Connect $restore[1] 'then' $place 'execute'
Write-Graph 'BP_CagePair_EventGraph.txt'

# ===== 3. BP_HellExit ======================================================================================
Reset-Graph 100
$begin = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$ACTOR`",MemberName=`"ReceiveBeginPlay`")", 'bOverrideFunction=True') 0 0
Add-Pin $begin 'then' 'out' 'exec'
$cast = GameInstance 300 0
Connect $begin 'then' $cast 'execute'
$clear = Fade '1.0' '0.0' '1.0' 'false' 550 0
Connect $cast 'then' $clear 'execute'
$wait = Delay '0.1' 1050 0
Connect $clear 'then' $wait 'execute'
$restore = RestoreStats $cast 1300 0
Connect $wait 'then' $restore[0] 'execute'
# Stepping onto the pad (any overlap of this actor; only Area collides).
$touch = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$ACTOR`",MemberName=`"ReceiveActorBeginOverlap`")", 'bOverrideFunction=True') 0 900
Add-Pin $touch 'then' 'out' 'exec'
Add-Pin $touch 'OtherActor' 'out' 'object' '' $ACTOR
$once = New-Branch 300 900
Connect (New-VarGet 'Leaving' $null 'bool' '' $null 150 1100) 'Leaving' $once 'Condition'
Connect $touch 'then' $once 'execute'
$isPlayer = New-Call $PRIMITIVE 'IsOverlappingActor' $true 500 1150
Add-Pin $isPlayer 'self' 'in' 'object' '' $PRIMITIVE
Add-Pin $isPlayer 'Other' 'in' 'object' '' $ACTOR
Add-Pin $isPlayer 'ReturnValue' 'out' 'bool'
Connect (New-VarGet 'Area' $null 'object' '' $BOX 300 1150) 'Area' $isPlayer 'self'
Connect (Player 250 1250) 'ReturnValue' $isPlayer 'Other'
$player = New-Branch 550 900
Connect $isPlayer 'ReturnValue' $player 'Condition'
Connect $once 'else' $player 'execute'
$leaving = New-VarSet 'Leaving' $null 'bool' $null 800 900
(Get-Pin $leaving 'Leaving').Default = 'true'
Connect $player 'then' $leaving 'execute'
$noInput = New-Call $ACTOR 'DisableInput' $false 1050 900
Add-Pin $noInput 'self' 'in' 'object' '' $ACTOR
Add-Pin $noInput 'PlayerController' 'in' 'object' '' $CONTROLLER
Connect (Player 850 1100) 'ReturnValue' $noInput 'self'
Connect (Controller 850 1200) 'ReturnValue' $noInput 'PlayerController'
$cast2 = GameInstance 1550 900
$saved = SaveStats $cast2 1850 900
$back = GiSet $cast2 'ReturnFromHell' 'bool' '' 3050 900 'true'
$dark = Fade '0.0' '1.0' '0.6' 'true' 3300 900
$wait2 = Delay '0.6' 3800 900
$open = OpenLevel 4050 900
Connect (GiGet $cast2 'ReturnLevel' 'name' '' 3850 1100) 'ReturnLevel' $open 'LevelName'
Chain @($leaving, $noInput, $cast2)
Connect $cast2 'then' $saved[0] 'execute'
Chain @($saved[1], $back, $dark, $wait2, $open)
Write-Graph 'BP_HellExit_EventGraph.txt'
