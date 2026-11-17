param([string]$OutDir)
# Generates the Ctrl+V-pasteable Event Graph of BP_TimeRewindArea (components and variables from setup_time_rewind.py).
# Begin Play finds the level's sun and works out its night rotation. Every tick:
#   1. the sky turns toward night while the player is inside the Area, back to day outside (NightAlpha, NightBlendSpeed);
#   2. the cooldown runs down;
#   3. inside and off cooldown, the player's spot is remembered and a countdown starts above their head; leaving cancels
#      it; when it reaches 0 the player is put back on that spot with a white flash, and the cooldown starts.

$helperFile = (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_height_bgm.ps1')
$helpers = Get-Content -LiteralPath $helperFile -Encoding UTF8 | Select-Object -Skip 3 -First 124
. ([ScriptBlock]::Create(($helpers -join "`n")))
$script:counter = 100

$CHARACTER = "/Script/CoreUObject.Class'/Script/Engine.Character'"
$MOVEMENT_CLASS = "/Script/CoreUObject.Class'/Script/Engine.CharacterMovementComponent'"
$PRIMITIVE = "/Script/CoreUObject.Class'/Script/Engine.PrimitiveComponent'"
$SCENE = "/Script/CoreUObject.Class'/Script/Engine.SceneComponent'"
$BOX = "/Script/CoreUObject.Class'/Script/Engine.BoxComponent'"
$TEXT_RENDER = "/Script/CoreUObject.Class'/Script/Engine.TextRenderComponent'"
$CAMERA_MANAGER = "/Script/CoreUObject.Class'/Script/Engine.PlayerCameraManager'"
$TEXT_LIBRARY = "/Script/CoreUObject.Class'/Script/Engine.KismetTextLibrary'"
$ROTATOR = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Rotator'"
$HIT = "/Script/CoreUObject.ScriptStruct'/Script/Engine.HitResult'"
$COLOR = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.LinearColor'"
$FLASH_SECONDS = '0.600000'

$script:objectDefaults = @{}

function New-Real($name, $x, $y) { $n = New-VarGet $name $null 'real' 'double' $null $x $y; return $n }
function New-RealSet($name, $x, $y) {
  $n = New-VarSet $name $null 'real' $null $x $y
  (Get-Pin $n $name).Sub = 'double'; (Get-Pin $n 'Output_Get').Sub = 'double'
  return $n
}
function New-BoolSet($name, $value, $x, $y) {
  $n = New-VarSet $name $null 'bool' $null $x $y
  (Get-Pin $n $name).Default = $value
  return $n
}
function New-Math($operation, $outCat, $x, $y) {
  $n = New-Operator $operation "${operation}_DoubleDouble" 'real' 'double' $outCat $x $y
  if ($outCat -eq 'real') { (Get-Pin $n 'ReturnValue').Sub = 'double' }
  return $n
}
function New-Visibility($visible, $x, $y) {
  $n = New-Call $SCENE 'SetVisibility' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $SCENE
  Add-Pin $n 'bNewVisibility' 'in' 'bool' '' $null $visible
  Add-Pin $n 'bPropagateToChildren' 'in' 'bool' '' $null 'false'
  $text = New-VarGet 'CountText' $null 'object' '' $TEXT_RENDER ($x - 50) ($y + 200)
  Connect $text 'CountText' $n 'self'
  return $n
}
function New-Break($x, $y) {
  $n = New-Call $MATH 'BreakVector' $true $x $y
  Add-Pin $n 'InVec' 'in' 'struct' '' $VECTOR
  Add-Pin $n 'X' 'out' 'real' 'double'
  Add-Pin $n 'Y' 'out' 'real' 'double'
  Add-Pin $n 'Z' 'out' 'real' 'double'
  return $n
}
function New-BreakRot($x, $y) {
  $n = New-Call $MATH 'BreakRotator' $true $x $y
  Add-Pin $n 'InRot' 'in' 'struct' '' $ROTATOR
  Add-Pin $n 'Roll' 'out' 'real' 'float'
  Add-Pin $n 'Pitch' 'out' 'real' 'float'
  Add-Pin $n 'Yaw' 'out' 'real' 'float'
  return $n
}
function New-MakeRot($x, $y) {
  $n = New-Call $MATH 'MakeRotator' $true $x $y
  Add-Pin $n 'Roll' 'in' 'real' 'float' $null '0.0'
  Add-Pin $n 'Pitch' 'in' 'real' 'float' $null '0.0'
  Add-Pin $n 'Yaw' 'in' 'real' 'float' $null '0.0'
  Add-Pin $n 'ReturnValue' 'out' 'struct' '' $ROTATOR
  return $n
}

# ===== Begin Play: the sun and its night rotation =====================================================
$begin = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$ACTOR`",MemberName=`"ReceiveBeginPlay`")", 'bOverrideFunction=True') 0 0
Add-Pin $begin 'then' 'out' 'exec'
$hideAtStart = New-Visibility 'false' 250 0
Connect $begin 'then' $hideAtStart 'execute'
$findSun = New-Call $STATICS 'GetActorOfClass' $false 600 0
Add-Pin $findSun 'ActorClass' 'in' 'class' '' $ACTOR
Add-Pin $findSun 'ReturnValue' 'out' 'object' '' $ACTOR
$script:objectDefaults[(Get-Pin $findSun 'ActorClass').Id] = '/Script/Engine.DirectionalLight'
Connect $hideAtStart 'then' $findSun 'execute'
$setSun = New-VarSet 'Sun' $null 'object' $ACTOR 950 0
Connect $findSun 'then' $setSun 'execute'
Connect $findSun 'ReturnValue' $setSun 'Sun'
$sunValid = New-IsValid 1200 200
Connect $setSun 'Output_Get' $sunValid 'Object'
$hasSun = New-Branch 1250 0
Connect $setSun 'then' $hasSun 'execute'
Connect $sunValid 'ReturnValue' $hasSun 'Condition'
$sunRotation = New-Call $ACTOR 'K2_GetActorRotation' $true 1250 300
Add-Pin $sunRotation 'self' 'in' 'object' '' $ACTOR
Add-Pin $sunRotation 'ReturnValue' 'out' 'struct' '' $ROTATOR
Connect $setSun 'Output_Get' $sunRotation 'self'
$setDay = New-VarSet 'DayRotation' $null 'struct' $ROTATOR 1550 0
Connect $hasSun 'then' $setDay 'execute'
Connect $sunRotation 'ReturnValue' $setDay 'DayRotation'
$dayParts = New-BreakRot 1600 250
Connect $setDay 'Output_Get' $dayParts 'InRot'
$nightRot = New-MakeRot 1850 250
Connect $dayParts 'Yaw' $nightRot 'Yaw'
$nightPitch = New-Real 'NightSunPitch' 1600 450
Connect $nightPitch 'NightSunPitch' $nightRot 'Pitch'
$setNight = New-VarSet 'NightRotation' $null 'struct' $ROTATOR 1950 0
Connect $setDay 'then' $setNight 'execute'
Connect $nightRot 'ReturnValue' $setNight 'NightRotation'

# ===== Tick ===========================================================================================
$y0 = 800
$tick = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$ACTOR`",MemberName=`"ReceiveTick`")", 'bOverrideFunction=True') 0 $y0
Add-Pin $tick 'then' 'out' 'exec'
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$steps = New-Node '/Script/BlueprintGraph.K2Node_ExecutionSequence' @() 250 $y0
Add-Pin $steps 'execute' 'in' 'exec'
Add-Pin $steps 'then_0' 'out' 'exec'
Add-Pin $steps 'then_1' 'out' 'exec'
Add-Pin $steps 'then_2' 'out' 'exec'
Connect $tick 'then' $steps 'execute'

# Shared: the player, and whether they are inside the Area.
$player = New-Call $STATICS 'GetPlayerCharacter' $true 0 ($y0 + 250)
Add-Pin $player 'PlayerIndex' 'in' 'int' '' $null '0'
Add-Pin $player 'ReturnValue' 'out' 'object' '' $CHARACTER
$areaGet = New-VarGet 'Area' $null 'object' '' $BOX 0 ($y0 + 400)
$inside = New-Call $PRIMITIVE 'IsOverlappingActor' $true 250 ($y0 + 300)
Add-Pin $inside 'self' 'in' 'object' '' $PRIMITIVE
Add-Pin $inside 'Other' 'in' 'object' '' $ACTOR
Add-Pin $inside 'ReturnValue' 'out' 'bool'
Connect $areaGet 'Area' $inside 'self'
Connect $player 'ReturnValue' $inside 'Other'

# --- 1. Night: NightAlpha moves toward 1 inside, 0 outside; the sun turns with it -----------------------
$y1 = $y0 - 400
$goal = New-Call $MATH 'SelectFloat' $true 550 ($y1 + 250)
Add-Pin $goal 'A' 'in' 'real' 'double' $null '1.0'
Add-Pin $goal 'B' 'in' 'real' 'double' $null '0.0'
Add-Pin $goal 'bPickA' 'in' 'bool'
Add-Pin $goal 'ReturnValue' 'out' 'real' 'double'
Connect $inside 'ReturnValue' $goal 'bPickA'
$blend = New-Call $MATH 'FInterpTo_Constant' $true 800 ($y1 + 200)
Add-Pin $blend 'Current' 'in' 'real' 'double'
Add-Pin $blend 'Target' 'in' 'real' 'double'
Add-Pin $blend 'DeltaTime' 'in' 'real' 'double'
Add-Pin $blend 'InterpSpeed' 'in' 'real' 'double'
Add-Pin $blend 'ReturnValue' 'out' 'real' 'double'
Connect (New-Real 'NightAlpha' 550 ($y1 + 150)) 'NightAlpha' $blend 'Current'
Connect $goal 'ReturnValue' $blend 'Target'
Connect $tick 'DeltaSeconds' $blend 'DeltaTime'
Connect (New-Real 'NightBlendSpeed' 550 ($y1 + 400)) 'NightBlendSpeed' $blend 'InterpSpeed'
$setAlpha = New-RealSet 'NightAlpha' 1050 $y1
Connect $steps 'then_0' $setAlpha 'execute'
Connect $blend 'ReturnValue' $setAlpha 'NightAlpha'
$sunGet = New-VarGet 'Sun' $null 'object' '' $ACTOR 1300 ($y1 + 250)
$sunOk = New-IsValid 1450 ($y1 + 250)
Connect $sunGet 'Sun' $sunOk 'Object'
$hasSunNow = New-Branch 1400 $y1
Connect $setAlpha 'then' $hasSunNow 'execute'
Connect $sunOk 'ReturnValue' $hasSunNow 'Condition'
$skyTurn = New-Call $MATH 'RLerp' $true 1700 ($y1 + 250)
Add-Pin $skyTurn 'A' 'in' 'struct' '' $ROTATOR
Add-Pin $skyTurn 'B' 'in' 'struct' '' $ROTATOR
Add-Pin $skyTurn 'Alpha' 'in' 'real' 'float'
Add-Pin $skyTurn 'bShortestPath' 'in' 'bool' '' $null 'true'
Add-Pin $skyTurn 'ReturnValue' 'out' 'struct' '' $ROTATOR
Connect (New-VarGet 'DayRotation' $null 'struct' '' $ROTATOR 1450 ($y1 + 400)) 'DayRotation' $skyTurn 'A'
Connect (New-VarGet 'NightRotation' $null 'struct' '' $ROTATOR 1450 ($y1 + 500)) 'NightRotation' $skyTurn 'B'
Connect $setAlpha 'Output_Get' $skyTurn 'Alpha'
$turnSun = New-Call $ACTOR 'K2_SetActorRotation' $false 1750 $y1
Add-Pin $turnSun 'self' 'in' 'object' '' $ACTOR
Add-Pin $turnSun 'NewRotation' 'in' 'struct' '' $ROTATOR
Add-Pin $turnSun 'bTeleportPhysics' 'in' 'bool' '' $null 'false'
Add-Pin $turnSun 'ReturnValue' 'out' 'bool'
Connect $sunGet 'Sun' $turnSun 'self'
Connect $skyTurn 'ReturnValue' $turnSun 'NewRotation'
Connect $hasSunNow 'then' $turnSun 'execute'

# --- 2. Cooldown runs down to 0 ------------------------------------------------------------------------
$y2 = $y0 + 650
$less = New-Math 'Subtract' 'real' 550 ($y2 + 150)
Connect (New-Real 'Cooldown' 350 ($y2 + 150)) 'Cooldown' $less 'A'
Connect $tick 'DeltaSeconds' $less 'B'
$floor = New-Call $MATH 'FMax' $true 750 ($y2 + 150)
Add-Pin $floor 'A' 'in' 'real' 'double'
Add-Pin $floor 'B' 'in' 'real' 'double' $null '0.0'
Add-Pin $floor 'ReturnValue' 'out' 'real' 'double'
Connect $less 'ReturnValue' $floor 'A'
$setCooldown = New-RealSet 'Cooldown' 1000 $y2
Connect $steps 'then_1' $setCooldown 'execute'
Connect $floor 'ReturnValue' $setCooldown 'Cooldown'

# --- 3. The countdown ----------------------------------------------------------------------------------
$y3 = $y0 + 1100
$countingGet = New-VarGet 'Counting' $null 'bool' '' $null 400 ($y3 + 200)
$isCounting = New-Branch 550 $y3
Connect $steps 'then_2' $isCounting 'execute'
Connect $countingGet 'Counting' $isCounting 'Condition'

# Not counting: inside and off cooldown starts one from where the player stands.
$y4 = $y3 + 1300
$ready = New-Math 'LessEqual' 'bool' 550 ($y4 + 300)
Connect (New-Real 'Cooldown' 350 ($y4 + 300)) 'Cooldown' $ready 'A'
(Get-Pin $ready 'B').Default = '0.0'
$both = New-Node '/Script/BlueprintGraph.K2Node_CommutativeAssociativeBinaryOperator' @('bDefaultsToPureFunc=True', "FunctionReference=(MemberParent=`"$MATH`",MemberName=`"BooleanAND`")") 750 ($y4 + 250)
Add-Pin $both 'A' 'in' 'bool'
Add-Pin $both 'B' 'in' 'bool'
Add-Pin $both 'ReturnValue' 'out' 'bool'
Connect $inside 'ReturnValue' $both 'A'
Connect $ready 'ReturnValue' $both 'B'
$canStart = New-Branch 850 $y4
Connect $isCounting 'else' $canStart 'execute'
Connect $both 'ReturnValue' $canStart 'Condition'
$playerSpot = New-Call $ACTOR 'K2_GetActorLocation' $true 1000 ($y4 + 300)
Add-Pin $playerSpot 'self' 'in' 'object' '' $ACTOR
Add-Pin $playerSpot 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $player 'ReturnValue' $playerSpot 'self'
$remember = New-VarSet 'RewindPoint' $null 'struct' $VECTOR 1200 $y4
Connect $canStart 'then' $remember 'execute'
Connect $playerSpot 'ReturnValue' $remember 'RewindPoint'
$startTime = New-RealSet 'CountTime' 1550 $y4
Connect $remember 'then' $startTime 'execute'
Connect (New-Real 'CountSeconds' 1400 ($y4 + 250)) 'CountSeconds' $startTime 'CountTime'
$startCount = New-BoolSet 'Counting' 'true' 1900 $y4
Connect $startTime 'then' $startCount 'execute'
$showText = New-Visibility 'true' 2250 $y4
Connect $startCount 'then' $showText 'execute'

# Counting, but the player left: cancel.
$stillInside = New-Branch 850 $y3
Connect $isCounting 'then' $stillInside 'execute'
Connect $inside 'ReturnValue' $stillInside 'Condition'
$y5 = $y3 + 600
$cancel = New-BoolSet 'Counting' 'false' 1200 $y5
Connect $stillInside 'else' $cancel 'execute'
$hideOnCancel = New-Visibility 'false' 1550 $y5
Connect $cancel 'then' $hideOnCancel 'execute'

# Counting inside: one frame less.
$minus = New-Math 'Subtract' 'real' 1000 ($y3 + 250)
Connect (New-Real 'CountTime' 850 ($y3 + 250)) 'CountTime' $minus 'A'
Connect $tick 'DeltaSeconds' $minus 'B'
$tickDown = New-RealSet 'CountTime' 1200 $y3
Connect $stillInside 'then' $tickDown 'execute'
Connect $minus 'ReturnValue' $tickDown 'CountTime'
$timeUp = New-Math 'LessEqual' 'bool' 1450 ($y3 + 250)
Connect $tickDown 'Output_Get' $timeUp 'A'
(Get-Pin $timeUp 'B').Default = '0.0'
$done = New-Branch 1550 $y3
Connect $tickDown 'then' $done 'execute'
Connect $timeUp 'ReturnValue' $done 'Condition'

# Still counting: show the whole seconds left above the player's head, facing the camera.
$y6 = $y3 + 300
$seconds = New-Call $MATH 'FCeil' $true 1800 ($y6 + 300)
Add-Pin $seconds 'A' 'in' 'real' 'double'
Add-Pin $seconds 'ReturnValue' 'out' 'int'
Connect $tickDown 'Output_Get' $seconds 'A'
$asText = New-Call $TEXT_LIBRARY 'Conv_IntToText' $true 2000 ($y6 + 300)
Add-Pin $asText 'Value' 'in' 'int'
Add-Pin $asText 'ReturnValue' 'out' 'text'
Connect $seconds 'ReturnValue' $asText 'Value'
$write = New-Call $TEXT_RENDER 'K2_SetText' $false 2300 $y6
Add-Pin $write 'self' 'in' 'object' '' $TEXT_RENDER
Add-Pin $write 'Value' 'in' 'text'
Connect (New-VarGet 'CountText' $null 'object' '' $TEXT_RENDER 2200 ($y6 + 200)) 'CountText' $write 'self'
Connect $asText 'ReturnValue' $write 'Value'
Connect $done 'else' $write 'execute'
$head = New-Break 2300 ($y6 + 450)
Connect $playerSpot 'ReturnValue' $head 'InVec'
$headZ = New-Math 'Add' 'real' 2500 ($y6 + 550)
Connect $head 'Z' $headZ 'A'
Connect (New-Real 'TextHeight' 2300 ($y6 + 650)) 'TextHeight' $headZ 'B'
$above = New-Call $MATH 'MakeVector' $true 2700 ($y6 + 450)
Add-Pin $above 'X' 'in' 'real' 'double' $null '0.0'
Add-Pin $above 'Y' 'in' 'real' 'double' $null '0.0'
Add-Pin $above 'Z' 'in' 'real' 'double' $null '0.0'
Add-Pin $above 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $head 'X' $above 'X'
Connect $head 'Y' $above 'Y'
Connect $headZ 'ReturnValue' $above 'Z'
$cameraManager = New-Call $STATICS 'GetPlayerCameraManager' $true 2300 ($y6 + 750)
Add-Pin $cameraManager 'PlayerIndex' 'in' 'int' '' $null '0'
Add-Pin $cameraManager 'ReturnValue' 'out' 'object' '' $CAMERA_MANAGER
$view = New-Call $CAMERA_MANAGER 'GetCameraRotation' $true 2550 ($y6 + 750)
Add-Pin $view 'self' 'in' 'object' '' $CAMERA_MANAGER
Add-Pin $view 'ReturnValue' 'out' 'struct' '' $ROTATOR
Connect $cameraManager 'ReturnValue' $view 'self'
$viewParts = New-BreakRot 2750 ($y6 + 750)
Connect $view 'ReturnValue' $viewParts 'InRot'
# Text reads from its front (+X), so it points back at the camera.
$turnAround = New-Math 'Add' 'real' 2950 ($y6 + 800)
Connect $viewParts 'Yaw' $turnAround 'A'
(Get-Pin $turnAround 'B').Default = '180.0'
$facing = New-MakeRot 3150 ($y6 + 750)
Connect $turnAround 'ReturnValue' $facing 'Yaw'
$place = New-Call $SCENE 'K2_SetWorldLocationAndRotation' $false 3350 $y6
Add-Pin $place 'self' 'in' 'object' '' $SCENE
Add-Pin $place 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $place 'NewRotation' 'in' 'struct' '' $ROTATOR
Add-Pin $place 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $place 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $place 'bTeleport' 'in' 'bool' '' $null 'true'
Connect (New-VarGet 'CountText' $null 'object' '' $TEXT_RENDER 3250 ($y6 + 300)) 'CountText' $place 'self'
Connect $above 'ReturnValue' $place 'NewLocation'
Connect $facing 'ReturnValue' $place 'NewRotation'
Connect $write 'then' $place 'execute'

# Time up: back to the remembered spot, stopped, with a white flash; then the cooldown.
$back = New-Call $ACTOR 'K2_SetActorLocation' $false 1900 $y3
Add-Pin $back 'self' 'in' 'object' '' $ACTOR
Add-Pin $back 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $back 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $back 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $back 'bTeleport' 'in' 'bool' '' $null 'true'
Add-Pin $back 'ReturnValue' 'out' 'bool'
Connect $player 'ReturnValue' $back 'self'
Connect (New-VarGet 'RewindPoint' $null 'struct' '' $VECTOR 1750 ($y3 + 200)) 'RewindPoint' $back 'NewLocation'
Connect $done 'then' $back 'execute'
$movement = New-VarGet 'CharacterMovement' $CHARACTER 'object' '' $MOVEMENT_CLASS 2150 ($y3 + 200)
Connect $player 'ReturnValue' $movement 'self'
$halt = New-Call $MOVEMENT_CLASS 'StopMovementImmediately' $false 2300 $y3
Add-Pin $halt 'self' 'in' 'object' '' $MOVEMENT_CLASS
Connect $movement 'CharacterMovement' $halt 'self'
Connect $back 'then' $halt 'execute'
$flash = New-Call $CAMERA_MANAGER 'StartCameraFade' $false 2650 $y3
Add-Pin $flash 'self' 'in' 'object' '' $CAMERA_MANAGER
Add-Pin $flash 'FromAlpha' 'in' 'real' 'float' $null '1.000000'
Add-Pin $flash 'ToAlpha' 'in' 'real' 'float' $null '0.000000'
Add-Pin $flash 'Duration' 'in' 'real' 'float' $null $FLASH_SECONDS
Add-Pin $flash 'Color' 'in' 'struct' '' $COLOR '(R=1.000000,G=1.000000,B=1.000000,A=1.000000)'
Add-Pin $flash 'bShouldFadeAudio' 'in' 'bool' '' $null 'false'
Add-Pin $flash 'bHoldWhenFinished' 'in' 'bool' '' $null 'false'
Connect $cameraManager 'ReturnValue' $flash 'self'
Connect $halt 'then' $flash 'execute'
$stop = New-BoolSet 'Counting' 'false' 3000 $y3
Connect $flash 'then' $stop 'execute'
$rest = New-RealSet 'Cooldown' 3350 $y3
Connect (New-Real 'CooldownSeconds' 3200 ($y3 + 200)) 'CooldownSeconds' $rest 'Cooldown'
Connect $stop 'then' $rest 'execute'
$hideAfter = New-Visibility 'false' 3700 $y3
Connect $rest 'then' $hideAfter 'execute'

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
foreach ($n in $script:nodes) {
  foreach ($p in $n.Pins) {
    if ($p.Cat -eq 'exec' -and $p.Dir -eq 'out' -and $p.Links.Count -gt 1) { throw "Exec output with several links: $($n.Name).$($p.Name)" }
  }
}
[IO.File]::WriteAllText((Join-Path $OutDir 'BP_TimeRewindArea_EventGraph.txt'), $text, [Text.UTF8Encoding]::new($false))
"Generated $($script:nodes.Count) nodes"
