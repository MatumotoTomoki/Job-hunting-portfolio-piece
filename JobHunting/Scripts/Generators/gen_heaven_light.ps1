param([string]$OutDir)
# Paste text for area 4's light gimmicks (components and variables from setup_heaven_light.py):
#   BP_LightBeam_EventGraph.txt     Begin Play: StartLocation. Tick: t = now - StartDelay; Lit = OffSeconds <= 0, or
#                                   t >= 0 and (t mod (On + Off)) < OnSeconds; the shaft shows while Lit. With
#                                   MoveSeconds > 0 it stands at StartLocation + MoveOffset * (0.5 - 0.5 cos(pi t / MoveSeconds)).
#   BP_LightPlatform_EventGraph.txt Tick, with a Beam: solid (Solid shown and colliding, Ghost hidden) while the Beam is
#                                   Lit and overlapping Probe, else the other way round.
#   BP_LightShard_EventGraph.txt    BP_StarCoin's graph without the coin counting: spins, taken by the player (Grab) it
#                                   spins up, rises, shrinks and is destroyed; its id goes on the run's TakenCoinIds,
#                                   so it stays gone after a trip to hell. Taken: IdleFx off, GetFx, GetSound played
#                                   at its place (2026-11-21).
#   BP_Iwato_EventGraph.txt         Begin Play: Sun, Sky = the level's directional and sky light. Tick: Counter shows how
#                                   many of Shard1..3 are gone; once all three are, Opened: the Lever is pulled (Pulled,
#                                   PulledAt = now) and, more than 1.5 s into the level, the view cuts to ShowCamera for
#                                   ShowSeconds. Every tick LightAlpha eases to Opened (1) or not (0) over BlendSeconds and
#                                   sets the sun's rotation and brightness and the sky light's intensity between Dark* and Bright*.
if (-not $OutDir) { throw 'OutDir is required' }
$cageGen = Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_hell_cage.ps1'
# Its helpers: from 'param' + header to the first graph (by marker, not a line count - its header grows).
$cageLines = Get-Content -LiteralPath $cageGen -Encoding UTF8
$cageStart = ($cageLines | Select-String -Pattern '^\$helperFile' | Select-Object -First 1).LineNumber - 1
$cageEnd = ($cageLines | Select-String -Pattern '^# ===== 1\.' | Select-Object -First 1).LineNumber - 2
$defs = $cageLines[$cageStart..$cageEnd]
. ([ScriptBlock]::Create(($defs -join "`n")))
# gen_hell_cage's helpers again with typed coordinates: untyped, a negative y arrives as text and -600 + 200
# becomes -600200 (the GetGameInstance node of BP_ChimeJewel landed 600 000 units up).
function Player([double]$x, [double]$y) {
  $n = New-Call $STATICS 'GetPlayerCharacter' $true $x $y
  Add-Pin $n 'PlayerIndex' 'in' 'int' '' $null '0'
  Add-Pin $n 'ReturnValue' 'out' 'object' '' $CHARACTER
  return $n
}
function Controller([double]$x, [double]$y) {
  $n = New-Call $STATICS 'GetPlayerController' $true $x $y
  Add-Pin $n 'PlayerIndex' 'in' 'int' '' $null '0'
  Add-Pin $n 'ReturnValue' 'out' 'object' '' $CONTROLLER
  return $n
}
function Movement([double]$x, [double]$y) {
  $n = New-VarGet 'CharacterMovement' $CHARACTER 'object' '' $CHAR_MOVE $x $y
  Connect (Player ($x - 250) $y) 'ReturnValue' $n 'self'
  return $n
}
function GameInstance([double]$x, [double]$y) {
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
function Delay($seconds, [double]$x, [double]$y) {
  $n = New-Call $SYSTEM 'Delay' $false $x $y
  Add-Pin $n 'Duration' 'in' 'real' 'float' $null $seconds
  return $n
}
# As gen_hell_cage's, plus DefaultObject (a class pin's chosen class).
function Format-Pin($p) {
  $obj = if ($p.Obj) { "`"$($p.Obj)`"" } else { 'None' }
  $ref = if ($p.PSObject.Properties['ConstRef'] -and $p.ConstRef) { 'True' } else { 'False' }
  $s = "PinId=$($p.Id),PinName=`"$($p.Name)`","
  if ($p.Dir -eq 'out') { $s += 'Direction="EGPD_Output",' }
  $s += "PinType.PinCategory=`"$($p.Cat)`",PinType.PinSubCategory=`"$($p.Sub)`",PinType.PinSubCategoryObject=$obj,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=$($p.Container),PinType.bIsReference=$ref,PinType.bIsConst=$ref,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,"
  if ($null -ne $p.Default) { $s += "DefaultValue=`"$($p.Default)`"," }
  if ($p.PSObject.Properties['DefaultObject']) { $s += "DefaultObject=`"$($p.DefaultObject)`"," }
  if ($p.Links.Count) { $s += 'LinkedTo=(' + (($p.Links | ForEach-Object { "$_," }) -join '') + '),' }
  $s += 'PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,'
  return "   CustomProperties Pin ($s)"
}

$SCENE = "/Script/CoreUObject.Class'/Script/Engine.SceneComponent'"
$STATIC_MESH = "/Script/CoreUObject.Class'/Script/Engine.StaticMeshComponent'"
$SPHERE = "/Script/CoreUObject.Class'/Script/Engine.SphereComponent'"
$TEXT_RENDER = "/Script/CoreUObject.Class'/Script/Engine.TextRenderComponent'"
$LIGHT = "/Script/CoreUObject.Class'/Script/Engine.Light'"
$DIR_LIGHT = "/Script/CoreUObject.Class'/Script/Engine.DirectionalLight'"
$SKY_LIGHT = "/Script/CoreUObject.Class'/Script/Engine.SkyLight'"
$SKY_COMP = "/Script/CoreUObject.Class'/Script/Engine.SkyLightComponent'"
$TEXTLIB = "/Script/CoreUObject.Class'/Script/Engine.KismetTextLibrary'"
$COLLISION_ENUM = "/Script/CoreUObject.Enum'/Script/Engine.ECollisionEnabled'"
$HEAVEN = '/Game/ThirdPerson/Blueprints/Gimmicks/Heaven'
$BEAM_CLASS = "/Script/Engine.BlueprintGeneratedClass'$HEAVEN/BP_LightBeam.BP_LightBeam_C'"
$SHARD_CLASS = "/Script/Engine.BlueprintGeneratedClass'$HEAVEN/BP_LightShard.BP_LightShard_C'"
$LEVER_CLASS = "/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPerson/Blueprints/Gimmicks/Area/BP_Lever.BP_Lever_C'"
$BLEND = '1.0'

function Event($name, [double]$x, [double]$y) {
  $n = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$ACTOR`",MemberName=`"$name`")", 'bOverrideFunction=True') $x $y
  Add-Pin $n 'then' 'out' 'exec'
  return $n
}
function SetSelf($name, $cat, $value, [double]$x, [double]$y) {
  $n = New-VarSet $name $null $cat $null $x $y
  if ($null -ne $value) { (Get-Pin $n $name).Default = $value }
  return $n
}
function SetReal($name, [double]$x, [double]$y) {
  $n = New-VarSet $name $null 'real' $null $x $y
  (Get-Pin $n $name).Sub = 'double'; (Get-Pin $n 'Output_Get').Sub = 'double'
  return $n
}
function Comp($name, $class, [double]$x, [double]$y) { New-VarGet $name $null 'object' '' $class $x $y }
function Real($name, [double]$x, [double]$y) { New-VarGet $name $null 'real' 'double' $null $x $y }
function Bool($name, [double]$x, [double]$y) { New-VarGet $name $null 'bool' '' $null $x $y }
function Vec($name, [double]$x, [double]$y) { New-VarGet $name $null 'struct' '' $VECTOR $x $y }
function Rot($name, [double]$x, [double]$y) { New-VarGet $name $null 'struct' '' $ROTATOR $x $y }
function Now([double]$x, [double]$y) {
  $n = New-Call $SYSTEM 'GetGameTimeInSeconds' $true $x $y
  Add-Pin $n 'ReturnValue' 'out' 'real' 'double'
  return $n
}
# A (op) B on doubles; a $null node takes the pin argument as a literal instead.
function Op($operation, $func, $a, $aPin, $b, $bPin, [double]$x, [double]$y, $outCat = 'real') {
  $n = New-Operator $operation $func 'real' 'double' $outCat $x $y
  if ($outCat -eq 'real') { (Get-Pin $n 'ReturnValue').Sub = 'double' }
  if ($a) { Connect $a $aPin $n 'A' } else { (Get-Pin $n 'A').Default = $aPin }
  if ($b) { Connect $b $bPin $n 'B' } else { (Get-Pin $n 'B').Default = $bPin }
  return $n
}
# A plain math call with the given input pins (all one type) and one output.
function MathCall($func, [string[]]$inputs, $inCat, $inSub, $outCat, $outSub, [double]$x, [double]$y) {
  $n = New-Call $MATH $func $true $x $y
  foreach ($pin in $inputs) { Add-Pin $n $pin 'in' $inCat $inSub }
  Add-Pin $n 'ReturnValue' 'out' $outCat $outSub
  return $n
}
function Both($a, $aPin, $b, $bPin, $func, [double]$x, [double]$y) {
  $n = MathCall $func @('A', 'B') 'bool' '' 'bool' '' $x $y
  Connect $a $aPin $n 'A'
  Connect $b $bPin $n 'B'
  return $n
}
function Visible($componentName, $value, [double]$x, [double]$y) {
  $n = New-Call $SCENE 'SetVisibility' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $SCENE
  Add-Pin $n 'bNewVisibility' 'in' 'bool' '' $null 'true'
  Add-Pin $n 'bPropagateToChildren' 'in' 'bool' '' $null 'false'
  Connect (Comp $componentName $STATIC_MESH ($x - 200) ($y + 200)) $componentName $n 'self'
  if ($value -is [string]) { (Get-Pin $n 'bNewVisibility').Default = $value } else { Connect $value[0] $value[1] $n 'bNewVisibility' }
  return $n
}
function Collide($componentName, $type, [double]$x, [double]$y) {
  $n = New-Call $PRIMITIVE 'SetCollisionEnabled' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $PRIMITIVE
  Add-Pin $n 'NewType' 'in' 'byte' '' $COLLISION_ENUM $type
  Connect (Comp $componentName $STATIC_MESH ($x - 200) ($y + 200)) $componentName $n 'self'
  return $n
}
function Valid($node, $pin, [double]$x, [double]$y) {
  $n = New-IsValid $x $y
  Connect $node $pin $n 'Object'
  return $n
}
function InputCall($func, [double]$x, [double]$y) {
  $n = New-Call $ACTOR $func $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR
  Add-Pin $n 'PlayerController' 'in' 'object' '' $CONTROLLER
  Connect (Player ($x - 200) ($y + 200)) 'ReturnValue' $n 'self'
  Connect (Controller ($x - 200) ($y + 300)) 'ReturnValue' $n 'PlayerController'
  return $n
}
function ViewTarget([double]$x, [double]$y) {
  $n = New-Call $CONTROLLER 'SetViewTargetWithBlend' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $CONTROLLER
  Add-Pin $n 'NewViewTarget' 'in' 'object' '' $ACTOR
  Add-Pin $n 'BlendTime' 'in' 'real' 'float' $null $BLEND
  Connect (Controller ($x - 250) ($y + 200)) 'ReturnValue' $n 'self'
  return $n
}
function Lerp($a, $b, $alpha, [double]$x, [double]$y) {
  $n = New-Call $MATH 'Lerp' $true $x $y
  Add-Pin $n 'A' 'in' 'real' 'double'
  Add-Pin $n 'B' 'in' 'real' 'double'
  Add-Pin $n 'Alpha' 'in' 'real' 'double'
  Add-Pin $n 'ReturnValue' 'out' 'real' 'double'
  Connect $a $a.Pins[0].Name $n 'A'
  Connect $b $b.Pins[0].Name $n 'B'
  Connect $alpha[0] $alpha[1] $n 'Alpha'
  return $n
}

# ===== BP_LightBeam ========================================================================================
Reset-Graph 100
$begin = Event 'ReceiveBeginPlay' 0 0
$remember = New-VarSet 'StartLocation' $null 'struct' $VECTOR 300 0
$here = New-Call $ACTOR 'K2_GetActorLocation' $true 100 200
Add-Pin $here 'self' 'in' 'object' '' $ACTOR
Add-Pin $here 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $here 'ReturnValue' $remember 'StartLocation'
Connect $begin 'then' $remember 'execute'

$tick = Event 'ReceiveTick' 0 600
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$t = Op 'Subtract' 'Subtract_DoubleDouble' (Now 0 900) 'ReturnValue' (Real 'StartDelay' 0 1000) 'StartDelay' 200 900
$tPos = MathCall 'FMax' @('A', 'B') 'real' 'double' 'real' 'double' 400 900
Connect $t 'ReturnValue' $tPos 'A'
(Get-Pin $tPos 'B').Default = '0.0'
# Shining?
$period = Op 'Add' 'Add_DoubleDouble' (Real 'OnSeconds' 200 1150) 'OnSeconds' (Real 'OffSeconds' 200 1250) 'OffSeconds' 400 1150
$periodSafe = MathCall 'FMax' @('A', 'B') 'real' 'double' 'real' 'double' 600 1150
Connect $period 'ReturnValue' $periodSafe 'A'
(Get-Pin $periodSafe 'B').Default = '0.01'
$phase = MathCall 'Percent_FloatFloat' @('A', 'B') 'real' 'double' 'real' 'double' 800 1000
Connect $tPos 'ReturnValue' $phase 'A'
Connect $periodSafe 'ReturnValue' $phase 'B'
$inOn = Op 'Less' 'Less_DoubleDouble' $phase 'ReturnValue' (Real 'OnSeconds' 800 1200) 'OnSeconds' 1000 1000 'bool'
$started = Op 'GreaterEqual' 'GreaterEqual_DoubleDouble' $t 'ReturnValue' $null '0.0' 1000 850 'bool'
$blinkOn = Both $started 'ReturnValue' $inOn 'ReturnValue' 'BooleanAND' 1200 900
$steady = Op 'LessEqual' 'LessEqual_DoubleDouble' (Real 'OffSeconds' 1000 1350) 'OffSeconds' $null '0.0' 1200 1300 'bool'
$litNow = Both $steady 'ReturnValue' $blinkOn 'ReturnValue' 'BooleanOR' 1400 1000
$setLit = SetSelf 'Lit' 'bool' $null 1600 600
Connect $litNow 'ReturnValue' $setLit 'Lit'
$show = Visible 'Shaft' @($setLit, 'Output_Get') 1900 600
# Swaying?
$sways = New-Branch 2200 600
Connect (Op 'Greater' 'Greater_DoubleDouble' (Real 'MoveSeconds' 1900 900) 'MoveSeconds' $null '0.0' 2050 900 'bool') 'ReturnValue' $sways 'Condition'
$angle = Op 'Multiply' 'Multiply_DoubleDouble' $tPos 'ReturnValue' $null '3.14159265' 1600 1500
$angle2 = Op 'Divide' 'Divide_DoubleDouble' $angle 'ReturnValue' (Real 'MoveSeconds' 1600 1650) 'MoveSeconds' 1800 1500
$cos = MathCall 'Cos' @('A') 'real' 'double' 'real' 'double' 2000 1500
Connect $angle2 'ReturnValue' $cos 'A'
$half = Op 'Multiply' 'Multiply_DoubleDouble' $cos 'ReturnValue' $null '-0.5' 2200 1500
$a = Op 'Add' 'Add_DoubleDouble' $half 'ReturnValue' $null '0.5' 2400 1500
$offset = New-Call $MATH 'Multiply_VectorFloat' $true 2600 1350
Add-Pin $offset 'A' 'in' 'struct' '' $VECTOR
Add-Pin $offset 'B' 'in' 'real' 'double'
Add-Pin $offset 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect (Vec 'MoveOffset' 2400 1350) 'MoveOffset' $offset 'A'
Connect $a 'ReturnValue' $offset 'B'
$where = New-Operator 'Add' 'Add_VectorVector' 'struct' '' 'struct' 2800 1250
foreach ($pin in 'A', 'B', 'ReturnValue') { (Get-Pin $where $pin).Obj = $VECTOR }
Connect (Vec 'StartLocation' 2600 1200) 'StartLocation' $where 'A'
Connect $offset 'ReturnValue' $where 'B'
$move = New-Call $ACTOR 'K2_SetActorLocation' $false 2500 600
Add-Pin $move 'self' 'in' 'object' '' $ACTOR
Add-Pin $move 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $move 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $move 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $move 'bTeleport' 'in' 'bool' '' $null 'false'
Add-Pin $move 'ReturnValue' 'out' 'bool'
Connect $where 'ReturnValue' $move 'NewLocation'
Connect $tick 'then' $setLit 'execute'
Connect $setLit 'then' $show 'execute'
Connect $show 'then' $sways 'execute'
Connect $sways 'then' $move 'execute'
Write-Graph 'BP_LightBeam_EventGraph.txt'

# ===== BP_LightPlatform ====================================================================================
Reset-Graph 100
$tick = Event 'ReceiveTick' 0 0
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$hasBeam = New-Branch 300 0
Connect (Valid (Comp 'Beam' $BEAM_CLASS 0 200) 'Beam' 150 200) 'ReturnValue' $hasBeam 'Condition'
$lit = New-VarGet 'Lit' $BEAM_CLASS 'bool' '' $null 450 300
Connect (Comp 'Beam' $BEAM_CLASS 250 350) 'Beam' $lit 'self'
$touching = New-Call $PRIMITIVE 'IsOverlappingActor' $true 450 450
Add-Pin $touching 'self' 'in' 'object' '' $PRIMITIVE
Add-Pin $touching 'Other' 'in' 'object' '' $ACTOR
Add-Pin $touching 'ReturnValue' 'out' 'bool'
Connect (Comp 'Probe' $BOX 250 500) 'Probe' $touching 'self'
Connect (Comp 'Beam' $BEAM_CLASS 250 600) 'Beam' $touching 'Other'
$on = New-Branch 800 0
Connect (Both $lit 'Lit' $touching 'ReturnValue' 'BooleanAND' 650 300) 'ReturnValue' $on 'Condition'
$solidOn = Collide 'Solid' 'QueryAndPhysics' 1100 -200
$solidShow = Visible 'Solid' 'true' 1400 -200
$ghostHide = Visible 'Ghost' 'false' 1700 -200
$solidOff = Collide 'Solid' 'NoCollision' 1100 300
$solidHide = Visible 'Solid' 'false' 1400 300
$ghostShow = Visible 'Ghost' 'true' 1700 300
Connect $tick 'then' $hasBeam 'execute'
Connect $hasBeam 'then' $on 'execute'
Connect $on 'then' $solidOn 'execute'
Chain @($solidOn, $solidShow, $ghostHide)
Connect $on 'else' $solidOff 'execute'
Chain @($solidOff, $solidHide, $ghostShow)
Write-Graph 'BP_LightPlatform_EventGraph.txt'

# ===== BP_LightShard: BP_StarCoin's graph (gen_star_coin.ps1) without StarCoins / TakenInArea ===============
$COLLECT = '0.9'
$EXTRA_SPIN = '2400.0'
$LIFT = '120.0'
function Concat($a, $aPin, $b, $bPin, [double]$x, [double]$y) {
  $n = New-Call $STRINGS 'Concat_StrStr' $true $x $y
  Add-Pin $n 'A' 'in' 'string'
  Add-Pin $n 'B' 'in' 'string'
  Add-Pin $n 'ReturnValue' 'out' 'string'
  foreach ($pin in 'A', 'B') { (Get-Pin $n $pin) | Add-Member -NotePropertyName ConstRef -NotePropertyValue $true }
  if ($a) { Connect $a $aPin $n 'A' } else { (Get-Pin $n 'A').Default = $aPin }
  if ($b) { Connect $b $bPin $n 'B' } else { (Get-Pin $n 'B').Default = $bPin }
  return $n
}
function LevelName([double]$x, [double]$y) {
  $n = New-Call $STATICS 'GetCurrentLevelName' $false $x $y
  Add-Pin $n 'bRemovePrefixString' 'in' 'bool' '' $null 'true'
  Add-Pin $n 'ReturnValue' 'out' 'string'
  return $n
}
function Pivot([double]$x, [double]$y) { New-VarGet 'Pivot' $null 'object' '' $SCENE $x $y }
function Times($a, $aPin, $b, $bPin, [double]$x, [double]$y) {
  $n = New-Operator 'Multiply' 'Multiply_DoubleDouble' 'real' 'double' 'real' $x $y
  (Get-Pin $n 'ReturnValue').Sub = 'double'
  Connect $a $aPin $n 'A'
  Connect $b $bPin $n 'B'
  return $n
}
function Spin($degrees, $degreesPin, [double]$x, [double]$y) {
  $rot = New-Call $MATH 'MakeRotator' $true ($x - 250) ($y + 250)
  Add-Pin $rot 'Roll' 'in' 'real' 'float' $null '0.0'
  Add-Pin $rot 'Pitch' 'in' 'real' 'float' $null '0.0'
  Add-Pin $rot 'Yaw' 'in' 'real' 'float'
  Add-Pin $rot 'ReturnValue' 'out' 'struct' '' $ROTATOR
  Connect $degrees $degreesPin $rot 'Yaw'
  $n = New-Call $SCENE 'K2_AddLocalRotation' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $SCENE
  Add-Pin $n 'DeltaRotation' 'in' 'struct' '' $ROTATOR
  Add-Pin $n 'bSweep' 'in' 'bool' '' $null 'false'
  Add-Pin $n 'SweepHitResult' 'out' 'struct' '' $HIT
  Add-Pin $n 'bTeleport' 'in' 'bool' '' $null 'false'
  Connect (Pivot ($x - 200) ($y + 150)) 'Pivot' $n 'self'
  Connect $rot 'ReturnValue' $n 'DeltaRotation'
  return $n
}

Reset-Graph 100
$tick = Event 'ReceiveTick' 0 0
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$taken = New-Branch 300 0
Connect (Bool 'Collected' 150 200) 'Collected' $taken 'Condition'
Connect $tick 'then' $taken 'execute'
$restSpin = Spin (Times (Real 'SpinSpeed' 400 650) 'SpinSpeed' $tick 'DeltaSeconds' 600 650) 'ReturnValue' 900 450
Connect $taken 'else' $restSpin 'execute'
$count = SetReal 'CollectedFor' 650 -300
$plus = Op 'Add' 'Add_DoubleDouble' (Real 'CollectedFor' 300 -100) 'CollectedFor' $tick 'DeltaSeconds' 500 -100
Connect $plus 'ReturnValue' $count 'CollectedFor'
Connect $taken 'then' $count 'execute'
$tt = New-Call $MATH 'MapRangeClamped' $true 900 -100
Add-Pin $tt 'Value' 'in' 'real' 'double'
Add-Pin $tt 'InRangeA' 'in' 'real' 'double' $null '0.0'
Add-Pin $tt 'InRangeB' 'in' 'real' 'double' $null $COLLECT
Add-Pin $tt 'OutRangeA' 'in' 'real' 'double' $null '0.0'
Add-Pin $tt 'OutRangeB' 'in' 'real' 'double' $null '1.0'
Add-Pin $tt 'ReturnValue' 'out' 'real' 'double'
Connect $count 'Output_Get' $tt 'Value'
$boost = Op 'Multiply' 'Multiply_DoubleDouble' $tt 'ReturnValue' $null $EXTRA_SPIN 1150 -150
$rate = Op 'Add' 'Add_DoubleDouble' (Real 'SpinSpeed' 1150 -50) 'SpinSpeed' $boost 'ReturnValue' 1350 -150
$fastSpin = Spin (Times $rate 'ReturnValue' $tick 'DeltaSeconds' 1550 -150) 'ReturnValue' 1950 -300
Connect $count 'then' $fastSpin 'execute'
$square = Op 'Multiply' 'Multiply_DoubleDouble' $tt 'ReturnValue' $tt 'ReturnValue' 2100 0
$left = Op 'Subtract' 'Subtract_DoubleDouble' $null '1.0' $square 'ReturnValue' 2300 0
$asVector = New-Call $MATH 'Conv_DoubleToVector' $true 2500 0
Add-Pin $asVector 'InDouble' 'in' 'real' 'double'
Add-Pin $asVector 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $left 'ReturnValue' $asVector 'InDouble'
$shrink = New-Call $SCENE 'SetRelativeScale3D' $false 2750 -300
Add-Pin $shrink 'self' 'in' 'object' '' $SCENE
Add-Pin $shrink 'NewScale3D' 'in' 'struct' '' $VECTOR
Connect (Pivot 2550 -150) 'Pivot' $shrink 'self'
Connect $asVector 'ReturnValue' $shrink 'NewScale3D'
$up = Op 'Multiply' 'Multiply_DoubleDouble' $tt 'ReturnValue' $null $LIFT 2900 100
$lifted = New-Call $MATH 'MakeVector' $true 3100 100
Add-Pin $lifted 'X' 'in' 'real' 'double' $null '0.0'
Add-Pin $lifted 'Y' 'in' 'real' 'double' $null '0.0'
Add-Pin $lifted 'Z' 'in' 'real' 'double'
Add-Pin $lifted 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $up 'ReturnValue' $lifted 'Z'
$rise = New-Call $SCENE 'K2_SetRelativeLocation' $false 3100 -300
Add-Pin $rise 'self' 'in' 'object' '' $SCENE
Add-Pin $rise 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $rise 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $rise 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $rise 'bTeleport' 'in' 'bool' '' $null 'false'
Connect (Pivot 2900 -150) 'Pivot' $rise 'self'
Connect $lifted 'ReturnValue' $rise 'NewLocation'
$over = New-Branch 3450 -300
Connect (Op 'GreaterEqual' 'GreaterEqual_DoubleDouble' $tt 'ReturnValue' $null '1.0' 3300 -100 'bool') 'ReturnValue' $over 'Condition'
$destroy = New-Call $ACTOR 'K2_DestroyActor' $false 3700 -300
Add-Pin $destroy 'self' 'in' 'object' '' $ACTOR
Chain @($fastSpin, $shrink, $rise, $over)
Connect $over 'then' $destroy 'execute'
# Touched.
$touch = Event 'ReceiveActorBeginOverlap' 0 1000
Add-Pin $touch 'OtherActor' 'out' 'object' '' $ACTOR
$once = New-Branch 300 1000
Connect (Bool 'Collected' 150 1200) 'Collected' $once 'Condition'
$isPlayer = New-Branch 550 1000
$overlap = New-Call $PRIMITIVE 'IsOverlappingActor' $true 450 1250
Add-Pin $overlap 'self' 'in' 'object' '' $PRIMITIVE
Add-Pin $overlap 'Other' 'in' 'object' '' $ACTOR
Add-Pin $overlap 'ReturnValue' 'out' 'bool'
Connect (Comp 'Grab' $SPHERE 250 1250) 'Grab' $overlap 'self'
Connect (Player 200 1350) 'ReturnValue' $overlap 'Other'
Connect $overlap 'ReturnValue' $isPlayer 'Condition'
$got = SetSelf 'Collected' 'bool' 'true' 800 1000
# The waiting glints stop, the pick-up burst, then "kiran" played at its place (outliving the shard; 2026-11-21,
# setup_shard_effects.py).
$EMITTER = "/Script/CoreUObject.Class'/Script/Effekseer.EffekseerEmitterComponent'"
$ACTOR_COMP = "/Script/CoreUObject.Class'/Script/Engine.ActorComponent'"
$SOUND_BASE = "/Script/CoreUObject.Class'/Script/Engine.SoundBase'"
$idleOff = New-Call $ACTOR_COMP 'Deactivate' $false 1050 1000
Add-Pin $idleOff 'self' 'in' 'object' '' $ACTOR_COMP
Connect (New-VarGet 'IdleFx' $null 'object' '' $EMITTER 850 1200) 'IdleFx' $idleOff 'self'
$burst = New-Call $ACTOR_COMP 'Activate' $false 1300 1000
Add-Pin $burst 'self' 'in' 'object' '' $ACTOR_COMP
Add-Pin $burst 'bReset' 'in' 'bool' '' $null 'true'
Connect (New-VarGet 'GetFx' $null 'object' '' $EMITTER 1100 1200) 'GetFx' $burst 'self'
$cast = GameInstance 1800 1000
$keep = GiSet $cast 'TakenCoinIds' 'string' '' 2100 1000
Connect (Concat (GiGet $cast 'TakenCoinIds' 'string' '' 1850 1250) 'TakenCoinIds' (New-VarGet 'CoinId' $null 'string' '' $null 1850 1350) 'CoinId' 2050 1250) 'ReturnValue' $keep 'TakenCoinIds'
$ring = New-Call $STATICS 'PlaySoundAtLocation' $false 2450 1000
Add-Pin $ring 'Sound' 'in' 'object' '' $SOUND_BASE
Add-Pin $ring 'Location' 'in' 'struct' '' $VECTOR
Add-Pin $ring 'Rotation' 'in' 'struct' '' $ROTATOR '0, 0, 0'
Add-Pin $ring 'VolumeMultiplier' 'in' 'real' 'float'
Add-Pin $ring 'PitchMultiplier' 'in' 'real' 'float' $null '1.0'
Add-Pin $ring 'StartTime' 'in' 'real' 'float' $null '0.0'
Connect (New-VarGet 'GetSound' $null 'object' '' $SOUND_BASE 2250 1450) 'GetSound' $ring 'Sound'
$shardAt = New-Call $ACTOR 'K2_GetActorLocation' $true 2250 1550
Add-Pin $shardAt 'self' 'in' 'object' '' $ACTOR
Add-Pin $shardAt 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $shardAt 'ReturnValue' $ring 'Location'
$vol = Op 'Multiply' 'Multiply_DoubleDouble' (GiGet $cast 'SE Volume' 'real' 'double' 2050 1650) 'SE Volume' (GiGet $cast 'Master Volume' 'real' 'double' 2050 1750) 'Master Volume' 2250 1700
Connect $vol 'ReturnValue' $ring 'VolumeMultiplier'
Connect $touch 'then' $once 'execute'
Connect $once 'else' $isPlayer 'execute'
Connect $isPlayer 'then' $got 'execute'
Chain @($got, $idleOff, $burst, $cast)
Connect $cast 'then' $keep 'execute'
Connect $keep 'then' $ring 'execute'
# Begin Play: CoinId = "|<level>.<this shard's name>|"; gone already if it is on the run's list.
$begin = Event 'ReceiveBeginPlay' 0 1800
$level2 = LevelName 300 1800
$self = New-Node '/Script/BlueprintGraph.K2Node_Self' @() 100 2150
Add-Pin $self 'self' 'out' 'object' '' $ACTOR
$objectName = New-Call $SYSTEM 'GetObjectName' $true 300 2150
Add-Pin $objectName 'Object' 'in' 'object' '' $OBJECT
Add-Pin $objectName 'ReturnValue' 'out' 'string'
Connect $self 'self' $objectName 'Object'
$dot = Concat $level2 'ReturnValue' $null '.' 600 2000
$named = Concat $dot 'ReturnValue' $objectName 'ReturnValue' 800 2050
$barred = Concat $null '|' $named 'ReturnValue' 1000 2050
$id = Concat $barred 'ReturnValue' $null '|' 1200 2050
$setId = New-VarSet 'CoinId' $null 'string' $null 650 1800
Connect $id 'ReturnValue' $setId 'CoinId'
$cast2 = GameInstance 1150 1800
$gone = New-Branch 1450 1800
$has = New-Call $STRINGS 'Contains' $true 1300 2150
Add-Pin $has 'SearchIn' 'in' 'string'
Add-Pin $has 'Substring' 'in' 'string'
Add-Pin $has 'bUseCase' 'in' 'bool' '' $null 'true'
Add-Pin $has 'bSearchFromEnd' 'in' 'bool' '' $null 'false'
Add-Pin $has 'ReturnValue' 'out' 'bool'
foreach ($pin in 'SearchIn', 'Substring') { (Get-Pin $has $pin) | Add-Member -NotePropertyName ConstRef -NotePropertyValue $true }
Connect (GiGet $cast2 'TakenCoinIds' 'string' '' 1100 2250) 'TakenCoinIds' $has 'SearchIn'
Connect (New-VarGet 'CoinId' $null 'string' '' $null 1100 2350) 'CoinId' $has 'Substring'
Connect $has 'ReturnValue' $gone 'Condition'
$remove = New-Call $ACTOR 'K2_DestroyActor' $false 1700 1800
Add-Pin $remove 'self' 'in' 'object' '' $ACTOR
Connect $begin 'then' $level2 'execute'
Chain @($level2, $setId, $cast2)
Connect $cast2 'then' $gone 'execute'
Connect $gone 'then' $remove 'execute'
Write-Graph 'BP_LightShard_EventGraph.txt'

# ===== BP_Iwato ============================================================================================
Reset-Graph 100
function FindActor($class, [double]$x, [double]$y) {
  $n = New-Call $STATICS 'GetActorOfClass' $false $x $y
  $cls = $class -replace "^/Script/CoreUObject.Class'(.*)'$", '$1'
  Add-Pin $n 'ActorClass' 'in' 'class' '' $ACTOR
  $p = Get-Pin $n 'ActorClass'
  $p | Add-Member -NotePropertyName DefaultObject -NotePropertyValue $cls
  Add-Pin $n 'ReturnValue' 'out' 'object' '' $class
  return $n
}
$begin = Event 'ReceiveBeginPlay' 0 0
$findSun = FindActor $DIR_LIGHT 300 0
$setSun = New-VarSet 'Sun' $null 'object' $DIR_LIGHT 650 0
Connect $findSun 'ReturnValue' $setSun 'Sun'
$findSky = FindActor $SKY_LIGHT 950 0
$setSky = New-VarSet 'Sky' $null 'object' $SKY_LIGHT 1300 0
Connect $findSky 'ReturnValue' $setSky 'Sky'
Connect $begin 'then' $findSun 'execute'
Chain @($findSun, $setSun, $findSky, $setSky)

$tick = Event 'ReceiveTick' 0 600
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$seq = New-Node '/Script/BlueprintGraph.K2Node_ExecutionSequence' @() 250 600
Add-Pin $seq 'execute' 'in' 'exec'
Add-Pin $seq 'then_0' 'out' 'exec'
Add-Pin $seq 'then_1' 'out' 'exec'
Connect $tick 'then' $seq 'execute'
# 0: the count, and opening.
$goneInts = @()
$i = 0
foreach ($name in 'Shard1', 'Shard2', 'Shard3') {
  $valid = Valid (New-VarGet $name $null 'object' '' $SHARD_CLASS 0 (900 + 120 * $i)) $name 200 (900 + 120 * $i)
  $not = MathCall 'Not_PreBool' @('A') 'bool' '' 'bool' '' 380 (900 + 120 * $i)
  Connect $valid 'ReturnValue' $not 'A'
  $asInt = New-Call $MATH 'Conv_BoolToInt' $true 560 (900 + 120 * $i)
  Add-Pin $asInt 'InBool' 'in' 'bool'
  Add-Pin $asInt 'ReturnValue' 'out' 'int'
  Connect $not 'ReturnValue' $asInt 'InBool'
  $goneInts += $asInt
  $i++
}
$sum12 = New-Operator 'Add' 'Add_IntInt' 'int' '' 'int' 760 950
Connect $goneInts[0] 'ReturnValue' $sum12 'A'
Connect $goneInts[1] 'ReturnValue' $sum12 'B'
$sum = New-Operator 'Add' 'Add_IntInt' 'int' '' 'int' 940 1050
Connect $sum12 'ReturnValue' $sum 'A'
Connect $goneInts[2] 'ReturnValue' $sum 'B'
$asString = New-Call $STRINGS 'Conv_IntToString' $true 1100 1050
Add-Pin $asString 'InInt' 'in' 'int'
Add-Pin $asString 'ReturnValue' 'out' 'string'
Connect $sum 'ReturnValue' $asString 'InInt'
$label = Concat $asString 'ReturnValue' $null ' / 3' 1280 1050
$asText = New-Call $TEXTLIB 'Conv_StringToText' $true 1460 1050
Add-Pin $asText 'InString' 'in' 'string'
Add-Pin $asText 'ReturnValue' 'out' 'text'
(Get-Pin $asText 'InString') | Add-Member -NotePropertyName ConstRef -NotePropertyValue $true
Connect $label 'ReturnValue' $asText 'InString'
$write = New-Call $TEXT_RENDER 'K2_SetText' $false 1650 600
Add-Pin $write 'self' 'in' 'object' '' $TEXT_RENDER
Add-Pin $write 'Value' 'in' 'text'
(Get-Pin $write 'Value') | Add-Member -NotePropertyName ConstRef -NotePropertyValue $true
Connect (Comp 'Counter' $TEXT_RENDER 1450 800) 'Counter' $write 'self'
Connect $asText 'ReturnValue' $write 'Value'
Connect $seq 'then_0' $write 'execute'
$already = New-Branch 1950 600
Connect (Bool 'Opened' 1800 800) 'Opened' $already 'Condition'
Connect $write 'then' $already 'execute'
$all = New-Branch 2200 600
$allGone = New-Operator 'GreaterEqual' 'GreaterEqual_IntInt' 'int' '' 'bool' 2050 850
Connect $sum 'ReturnValue' $allGone 'A'
(Get-Pin $allGone 'B').Default = '3'
Connect $allGone 'ReturnValue' $all 'Condition'
Connect $already 'else' $all 'execute'
$opened = SetSelf 'Opened' 'bool' 'true' 2450 600
Connect $all 'then' $opened 'execute'
$hasLever = New-Branch 2700 600
Connect (Valid (New-VarGet 'Lever' $null 'object' '' $LEVER_CLASS 2500 800) 'Lever' 2600 800) 'ReturnValue' $hasLever 'Condition'
Connect $opened 'then' $hasLever 'execute'
$pull = New-VarSet 'Pulled' $LEVER_CLASS 'bool' $null 2950 600
(Get-Pin $pull 'Pulled').Default = 'true'
Connect (New-VarGet 'Lever' $null 'object' '' $LEVER_CLASS 2800 850) 'Lever' $pull 'self'
$stamp = New-VarSet 'PulledAt' $LEVER_CLASS 'real' $null 3250 600
(Get-Pin $stamp 'PulledAt').Sub = 'double'; (Get-Pin $stamp 'Output_Get').Sub = 'double'
Connect (New-VarGet 'Lever' $null 'object' '' $LEVER_CLASS 3100 850) 'Lever' $stamp 'self'
Connect (Now 3100 950) 'ReturnValue' $stamp 'PulledAt'
Connect $hasLever 'then' $pull 'execute'
Connect $pull 'then' $stamp 'execute'
# The show: only with a camera, and not when the level starts with the shards already gone.
$showIt = New-Branch 3550 600
$camValid = Valid (New-VarGet 'ShowCamera' $null 'object' '' $ACTOR 3300 1100) 'ShowCamera' 3450 1100
$late = Op 'Greater' 'Greater_DoubleDouble' (Now 3300 1250) 'ReturnValue' $null '1.5' 3450 1250 'bool'
Connect (Both $camValid 'ReturnValue' $late 'ReturnValue' 'BooleanAND' 3600 1150) 'ReturnValue' $showIt 'Condition'
Connect $stamp 'then' $showIt 'execute'
Connect $hasLever 'else' $showIt 'execute'
$hold = InputCall 'DisableInput' 3850 600
$toCamera = ViewTarget 4150 600
Connect (New-VarGet 'ShowCamera' $null 'object' '' $ACTOR 3950 950) 'ShowCamera' $toCamera 'NewViewTarget'
$watch = Delay '0.0' 4500 600
Connect (Real 'ShowSeconds' 4350 850) 'ShowSeconds' $watch 'Duration'
$toPlayer = ViewTarget 4800 600
Connect (Player 4600 950) 'ReturnValue' $toPlayer 'NewViewTarget'
$back = Delay $BLEND 5150 600
$free = InputCall 'EnableInput' 5450 600
Connect $showIt 'then' $hold 'execute'
Chain @($hold, $toCamera, $watch, $toPlayer, $back, $free)

# 1: the light.
$target = New-Call $MATH 'SelectFloat' $true 400 1700
Add-Pin $target 'A' 'in' 'real' 'double' $null '1.0'
Add-Pin $target 'B' 'in' 'real' 'double' $null '0.0'
Add-Pin $target 'bPickA' 'in' 'bool'
Add-Pin $target 'ReturnValue' 'out' 'real' 'double'
Connect (Bool 'Opened' 200 1800) 'Opened' $target 'bPickA'
$blendSafe = MathCall 'FMax' @('A', 'B') 'real' 'double' 'real' 'double' 400 1900
Connect (Real 'BlendSeconds' 200 1950) 'BlendSeconds' $blendSafe 'A'
(Get-Pin $blendSafe 'B').Default = '0.1'
$speed = Op 'Divide' 'Divide_DoubleDouble' $null '1.0' $blendSafe 'ReturnValue' 600 1900
$ease = New-Call $MATH 'FInterpTo_Constant' $true 800 1700
Add-Pin $ease 'Current' 'in' 'real' 'double'
Add-Pin $ease 'Target' 'in' 'real' 'double'
Add-Pin $ease 'DeltaTime' 'in' 'real' 'double'
Add-Pin $ease 'InterpSpeed' 'in' 'real' 'double'
Add-Pin $ease 'ReturnValue' 'out' 'real' 'double'
Connect (Real 'LightAlpha' 600 1650) 'LightAlpha' $ease 'Current'
Connect $target 'ReturnValue' $ease 'Target'
Connect $tick 'DeltaSeconds' $ease 'DeltaTime'
Connect $speed 'ReturnValue' $ease 'InterpSpeed'
$setAlpha = SetReal 'LightAlpha' 1050 1500
Connect $ease 'ReturnValue' $setAlpha 'LightAlpha'
Connect $seq 'then_1' $setAlpha 'execute'
$hasSun = New-Branch 1350 1500
Connect (Valid (New-VarGet 'Sun' $null 'object' '' $DIR_LIGHT 1150 1700) 'Sun' 1250 1700) 'ReturnValue' $hasSun 'Condition'
Connect $setAlpha 'then' $hasSun 'execute'
$angle = New-Call $MATH 'RLerp' $true 1500 1800
Add-Pin $angle 'A' 'in' 'struct' '' $ROTATOR
Add-Pin $angle 'B' 'in' 'struct' '' $ROTATOR
Add-Pin $angle 'Alpha' 'in' 'real' 'float'
Add-Pin $angle 'bShortestPath' 'in' 'bool' '' $null 'true'
Add-Pin $angle 'ReturnValue' 'out' 'struct' '' $ROTATOR
Connect (Rot 'DarkRotation' 1300 1850) 'DarkRotation' $angle 'A'
Connect (Rot 'BrightRotation' 1300 1950) 'BrightRotation' $angle 'B'
Connect $setAlpha 'Output_Get' $angle 'Alpha'
$turn = New-Call $ACTOR 'K2_SetActorRotation' $false 1650 1500
Add-Pin $turn 'self' 'in' 'object' '' $ACTOR
Add-Pin $turn 'NewRotation' 'in' 'struct' '' $ROTATOR
Add-Pin $turn 'bTeleportPhysics' 'in' 'bool' '' $null 'false'
Add-Pin $turn 'ReturnValue' 'out' 'bool'
Connect (New-VarGet 'Sun' $null 'object' '' $DIR_LIGHT 1450 1700) 'Sun' $turn 'self'
Connect $angle 'ReturnValue' $turn 'NewRotation'
$bright = New-Call $LIGHT 'SetBrightness' $false 2000 1500
Add-Pin $bright 'self' 'in' 'object' '' $LIGHT
Add-Pin $bright 'NewBrightness' 'in' 'real' 'float'
Connect (New-VarGet 'Sun' $null 'object' '' $DIR_LIGHT 1800 1700) 'Sun' $bright 'self'
Connect (Lerp (Real 'DarkSun' 1700 1900) (Real 'BrightSun' 1700 2000) @($setAlpha, 'Output_Get') 1900 1900) 'ReturnValue' $bright 'NewBrightness'
Connect $hasSun 'then' $turn 'execute'
Connect $turn 'then' $bright 'execute'
$hasSky = New-Branch 2350 1500
Connect (Valid (New-VarGet 'Sky' $null 'object' '' $SKY_LIGHT 2150 1700) 'Sky' 2250 1700) 'ReturnValue' $hasSky 'Condition'
Connect $bright 'then' $hasSky 'execute'
Connect $hasSun 'else' $hasSky 'execute'
$skyComp = New-VarGet 'LightComponent' $SKY_LIGHT 'object' '' $SKY_COMP 2450 1800
Connect (New-VarGet 'Sky' $null 'object' '' $SKY_LIGHT 2250 1850) 'Sky' $skyComp 'self'
$skyBright = New-Call $SKY_COMP 'SetIntensity' $false 2700 1500
Add-Pin $skyBright 'self' 'in' 'object' '' $SKY_COMP
Add-Pin $skyBright 'NewIntensity' 'in' 'real' 'float'
Connect $skyComp 'LightComponent' $skyBright 'self'
Connect (Lerp (Real 'DarkSky' 2400 1950) (Real 'BrightSky' 2400 2050) @($setAlpha, 'Output_Get') 2600 1950) 'ReturnValue' $skyBright 'NewIntensity'
Connect $hasSky 'then' $skyBright 'execute'
Write-Graph 'BP_Iwato_EventGraph.txt'
