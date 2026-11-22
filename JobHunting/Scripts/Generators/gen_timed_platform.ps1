param([string]$OutDir)
# Generates the Ctrl+V-pasteable Event Graph of BP_TimedPlatform: after StartDelay, repeat forever: stay VisibleSeconds,
# fade out over FadeSeconds and stop carrying the player, stay gone HiddenSeconds, fade back in and carry again.
# Sounds and effects (setup_timed_effects.py, 2026-11-22): Begin Play sets their volume (SE x Master). Both mark the
# moment the player's footing changes (the user): gone after fading out - VanishSound + VanishFx; solid again after
# fading in - AppearSound + AppearFx.

# Reuse the node helpers (constants + functions) from the height BGM generator.
$helperFile = (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_height_bgm.ps1')
$helpers = Get-Content -LiteralPath $helperFile -Encoding UTF8 | Select-Object -Skip 3 -First 124
. ([ScriptBlock]::Create(($helpers -join "`n")))

$SCENE_CLASS = "/Script/CoreUObject.Class'/Script/Engine.SceneComponent'"
$PRIMITIVE_CLASS = "/Script/CoreUObject.Class'/Script/Engine.PrimitiveComponent'"
$MESH_CLASS = "/Script/CoreUObject.Class'/Script/Engine.StaticMeshComponent'"
$COLLISION_ENUM = "/Script/CoreUObject.Enum'/Script/Engine.ECollisionEnabled'"

function New-Wait($variable, $x, $y) {
  $node = New-Call $SYSTEM 'Delay' $false $x $y
  Add-Pin $node 'Duration' 'in' 'real' 'float' $null '0.0'
  if ($variable) {
    $get = New-VarGet $variable $null 'real' 'double' $null ($x - 50) ($y + 200)
    Connect $get $variable $node 'Duration'
  }
  return $node
}

function New-MeshGet($x, $y) { return New-VarGet 'FloorMesh' $null 'object' '' $MESH_CLASS $x $y }

function New-SetSolid($mode, $x, $y) {
  $node = New-Call $PRIMITIVE_CLASS 'SetCollisionEnabled' $false $x $y
  Add-Pin $node 'self' 'in' 'object' '' $PRIMITIVE_CLASS
  Add-Pin $node 'NewType' 'in' 'byte' '' $COLLISION_ENUM $mode
  $mesh = New-MeshGet ($x - 50) ($y + 200)
  Connect $mesh 'FloorMesh' $node 'self'
  return $node
}

# Belt and braces with the dithered fade: fully hidden while gone, no shadow left behind.
function New-SetShown($value, $x, $y) {
  $node = New-Call $SCENE_CLASS 'SetVisibility' $false $x $y
  Add-Pin $node 'self' 'in' 'object' '' $SCENE_CLASS
  Add-Pin $node 'bNewVisibility' 'in' 'bool' '' $null $value
  Add-Pin $node 'bPropagateToChildren' 'in' 'bool' '' $null 'false'
  $mesh = New-MeshGet ($x - 50) ($y + 200)
  Connect $mesh 'FloorMesh' $node 'self'
  return $node
}

# Fade steps by this frame's time over FadeSeconds, once a frame, until it reaches the end value.
function New-FadeLoop($startValue, $direction, $doneOperation, $doneFunction, $doneValue, $x, $y) {
  $start = New-VarSet 'Fade' $null 'real' $null $x $y
  (Get-Pin $start 'Fade').Sub = 'double'
  (Get-Pin $start 'Output_Get').Sub = 'double'
  (Get-Pin $start 'Fade').Default = $startValue
  $frame = New-Call $STATICS 'GetWorldDeltaSeconds' $true ($x + 100) ($y + 450)
  Add-Pin $frame 'ReturnValue' 'out' 'real' 'double'
  $seconds = New-VarGet 'FadeSeconds' $null 'real' 'double' $null ($x + 100) ($y + 600)
  $step = New-Operator 'Divide' 'Divide_DoubleDouble' 'real' 'double' 'real' ($x + 350) ($y + 450)
  (Get-Pin $step 'ReturnValue').Sub = 'double'
  Connect $frame 'ReturnValue' $step 'A'
  Connect $seconds 'FadeSeconds' $step 'B'
  $current = New-VarGet 'Fade' $null 'real' 'double' $null ($x + 350) ($y + 300)
  $change = New-Operator $direction "${direction}_DoubleDouble" 'real' 'double' 'real' ($x + 600) ($y + 350)
  (Get-Pin $change 'ReturnValue').Sub = 'double'
  Connect $current 'Fade' $change 'A'
  Connect $step 'ReturnValue' $change 'B'
  $store = New-VarSet 'Fade' $null 'real' $null ($x + 350) $y
  (Get-Pin $store 'Fade').Sub = 'double'
  (Get-Pin $store 'Output_Get').Sub = 'double'
  Connect $change 'ReturnValue' $store 'Fade'
  $apply = New-Call "/Script/CoreUObject.Class'/Script/Engine.MeshComponent'" 'SetScalarParameterValueOnMaterials' $false ($x + 700) $y
  Add-Pin $apply 'self' 'in' 'object' '' "/Script/CoreUObject.Class'/Script/Engine.MeshComponent'"
  Add-Pin $apply 'ParameterName' 'in' 'name' '' $null 'Fade'
  Add-Pin $apply 'ParameterValue' 'in' 'real' 'float' $null '1.0'
  $mesh = New-MeshGet ($x + 600) ($y + 200)
  Connect $mesh 'FloorMesh' $apply 'self'
  Connect $store 'Output_Get' $apply 'ParameterValue'
  $finished = New-Operator $doneOperation $doneFunction 'real' 'double' 'bool' ($x + 950) ($y + 300)
  (Get-Pin $finished 'B').Default = $doneValue
  Connect $store 'Output_Get' $finished 'A'
  $doneBranch = New-Branch ($x + 1100) $y
  Connect $finished 'ReturnValue' $doneBranch 'Condition'
  # A zero Delay finishes on the next frame.
  $nextFrame = New-Wait $null ($x + 1400) ($y + 200)
  Connect $start 'then' $store 'execute'
  Connect $store 'then' $apply 'execute'
  Connect $apply 'then' $doneBranch 'execute'
  Connect $doneBranch 'else' $nextFrame 'execute'
  Connect $nextFrame 'then' $store 'execute'
  return @($start, $doneBranch)
}

# Sounds and effects (setup_timed_effects.py, 2026-11-22). (Typed coordinates: untyped, a negative y arrives as
# text and -250 + 200 becomes -250200.)
$EMITTER_COMP = "/Script/CoreUObject.Class'/Script/Effekseer.EffekseerEmitterComponent'"
$COMPONENT_CLASS = "/Script/CoreUObject.Class'/Script/Engine.ActorComponent'"
$GI_OUT = 'AsBP My Game Instance'
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

$begin = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$ACTOR`",MemberName=`"ReceiveBeginPlay`")", 'bOverrideFunction=True') 0 0
Add-Pin $begin 'then' 'out' 'exec'
# Begin Play: the sounds at SE Volume x Master Volume, then on as before.
$gi = New-Call $STATICS 'GetGameInstance' $true 50 -500
Add-Pin $gi 'ReturnValue' 'out' 'object' '' $GAMEINST
$cast = New-Node '/Script/BlueprintGraph.K2Node_DynamicCast' @("TargetType=`"$GI_CLASS`"") 300 -700
Add-Exec $cast
Add-Pin $cast 'CastFailed' 'out' 'exec'
Add-Pin $cast 'Object' 'in' 'object' '' $OBJECT
Add-Pin $cast $GI_OUT 'out' 'object' '' $GI_CLASS
Add-Pin $cast 'bSuccess' 'out' 'bool'
Connect $gi 'ReturnValue' $cast 'Object'
Connect $begin 'then' $cast 'execute'
$seVol = New-VarGet 'SE Volume' $GI_CLASS 'real' 'double' $null 350 -450
Connect $cast $GI_OUT $seVol 'self'
$masterVol = New-VarGet 'Master Volume' $GI_CLASS 'real' 'double' $null 350 -350
Connect $cast $GI_OUT $masterVol 'self'
$vol = New-Operator 'Multiply' 'Multiply_DoubleDouble' 'real' 'double' 'real' 600 -450
(Get-Pin $vol 'ReturnValue').Sub = 'double'
Connect $seVol 'SE Volume' $vol 'A'
Connect $masterVol 'Master Volume' $vol 'B'
$prev = $cast; $vx = 750
foreach ($name in 'VanishSound', 'AppearSound') {
  $v = New-Call $AUDIO 'SetVolumeMultiplier' $false $vx -700
  Add-Pin $v 'self' 'in' 'object' '' $AUDIO
  Add-Pin $v 'NewVolumeMultiplier' 'in' 'real' 'float'
  Connect (New-VarGet $name $null 'object' '' $AUDIO ($vx - 200) -500) $name $v 'self'
  Connect $vol 'ReturnValue' $v 'NewVolumeMultiplier'
  Connect $prev 'then' $v 'execute'
  $prev = $v; $vx += 300
}
$startDelay = New-Wait 'StartDelay' 300 0
Connect $prev 'then' $startDelay 'execute'
Connect $cast 'CastFailed' $startDelay 'execute'

# --- Visible, then fade out and drop the player ----------------------------------------
$visible = New-Wait 'VisibleSeconds' 700 0
Connect $startDelay 'then' $visible 'execute'
$fadeOut = New-FadeLoop '1.000000' 'Subtract' 'LessEqual' 'LessEqual_DoubleDouble' '0.000000' 1100 0
Connect $visible 'then' $fadeOut[0] 'execute'
$rowY = 900
$passThrough = New-SetSolid 'NoCollision' 300 $rowY
Connect $fadeOut[1] 'then' $passThrough 'execute'
# Gone: the cue that it can no longer be stood on (the user, 2026-11-22).
$vanishSound = SoundPlay 'VanishSound' 650 ($rowY - 350)
$vanishFx = FxPlay 'VanishFx' 950 ($rowY - 350)
Connect $passThrough 'then' $vanishSound 'execute'
Connect $vanishSound 'then' $vanishFx 'execute'
$hide = New-SetShown 'false' 650 $rowY
Connect $vanishFx 'then' $hide 'execute'

# --- Gone, then fade back in and carry the player again ---------------------------------
$hidden = New-Wait 'HiddenSeconds' 1050 $rowY
Connect $hide 'then' $hidden 'execute'
$show = New-SetShown 'true' 1400 $rowY
Connect $hidden 'then' $show 'execute'
$fadeIn = New-FadeLoop '0.000000' 'Add' 'GreaterEqual' 'GreaterEqual_DoubleDouble' '1.000000' 1800 $rowY
Connect $show 'then' $fadeIn[0] 'execute'
$rowY = 1800
$solid = New-SetSolid 'QueryAndPhysics' 300 $rowY
Connect $fadeIn[1] 'then' $solid 'execute'
# Solid again: the cue that it can be stood on (the user, 2026-11-22).
$appearSound = SoundPlay 'AppearSound' 650 $rowY
$appearFx = FxPlay 'AppearFx' 950 $rowY
Connect $solid 'then' $appearSound 'execute'
Connect $appearSound 'then' $appearFx 'execute'
Connect $appearFx 'then' $visible 'execute'

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
[IO.File]::WriteAllText((Join-Path $OutDir 'BP_TimedPlatform_EventGraph.txt'), $text, [Text.UTF8Encoding]::new($false))
"Generated $($script:nodes.Count) nodes"
