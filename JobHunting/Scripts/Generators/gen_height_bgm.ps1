param([string]$OutDir)
# Generates Ctrl+V-pasteable node text: crossfade the BGM when the player climbs past set heights (controller Event Tick).

$GI_CLASS  = "/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPerson/Blueprints/BP_MyGameInstance.BP_MyGameInstance_C'"
$AUDIO     = "/Script/CoreUObject.Class'/Script/Engine.AudioComponent'"
$SOUND     = "/Script/CoreUObject.Class'/Script/Engine.SoundBase'"
$PAWN_CLASS = "/Script/CoreUObject.Class'/Script/Engine.Pawn'"
$ACTOR     = "/Script/CoreUObject.Class'/Script/Engine.Actor'"
$GAMEINST  = "/Script/CoreUObject.Class'/Script/Engine.GameInstance'"
$OBJECT    = "/Script/CoreUObject.Class'/Script/CoreUObject.Object'"
$VECTOR    = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Vector'"
$MATH      = "/Script/CoreUObject.Class'/Script/Engine.KismetMathLibrary'"
$SYSTEM    = "/Script/CoreUObject.Class'/Script/Engine.KismetSystemLibrary'"
$ARRAYLIB  = "/Script/CoreUObject.Class'/Script/Engine.KismetArrayLibrary'"
$STATICS   = "/Script/CoreUObject.Class'/Script/Engine.GameplayStatics'"

# Player Z (cm) at which each later BGM starts: platform Z + 50, so it switches once the player stands on it.
$BGM2_HEIGHT = '1410.000000'   # SM_Door15 (Z 1360)
$BGM3_HEIGHT = '2970.000000'   # UpperExtension_Platform_06 (Z 2920)
$FADE_SECONDS = '2.000000'

$script:nodes = [System.Collections.Generic.List[object]]::new()
$script:counter = 100

function New-Node($class, [string[]]$props, $x, $y) {
  $script:counter++
  $short = $class.Split('.')[-1]
  $n = [pscustomobject]@{ Class = $class; Name = "${short}_$($script:counter)"; Props = $props; X = $x; Y = $y; Pins = [System.Collections.Generic.List[object]]::new() }
  $script:nodes.Add($n)
  return $n
}

function Add-Pin($node, $name, $dir, $cat, $sub = '', $obj = $null, $default = $null, $container = 'None') {
  $p = [pscustomobject]@{ Id = [guid]::NewGuid().ToString('N').ToUpper(); Name = $name; Dir = $dir; Cat = $cat; Sub = $sub; Obj = $obj; Default = $default; Container = $container; Links = [System.Collections.Generic.List[string]]::new() }
  $node.Pins.Add($p)
}

function Get-Pin($node, $name) {
  $p = $node.Pins | Where-Object { $_.Name -eq $name } | Select-Object -First 1
  if (-not $p) { throw "Missing pin $($node.Name).$name" }
  return $p
}

function Connect($a, $aPin, $b, $bPin) {
  $pa = Get-Pin $a $aPin; $pb = Get-Pin $b $bPin
  $pa.Links.Add("$($b.Name) $($pb.Id)"); $pb.Links.Add("$($a.Name) $($pa.Id)")
}

function Add-Exec($node) { Add-Pin $node 'execute' 'in' 'exec'; Add-Pin $node 'then' 'out' 'exec' }

function New-Call($parent, $func, [bool]$pure, $x, $y, $class = '/Script/BlueprintGraph.K2Node_CallFunction') {
  $props = @()
  if ($pure) { $props += 'bDefaultsToPureFunc=True' }
  if ($parent) { $props += "FunctionReference=(MemberParent=`"$parent`",MemberName=`"$func`")" }
  else { $props += "FunctionReference=(MemberName=`"$func`",bSelfContext=True)" }
  $n = New-Node $class $props $x $y
  if (-not $pure) { Add-Exec $n }
  return $n
}

# ==, +, >= etc. are K2Node_PromotableOperator in UE5; pasting them as plain calls drops their links.
function New-Operator($operation, $func, $inCat, $inSub, $outCat, $x, $y) {
  $props = "OperationName=`"$operation`"", 'bDefaultsToPureFunc=True', "FunctionReference=(MemberParent=`"$MATH`",MemberName=`"$func`")"
  $n = New-Node '/Script/BlueprintGraph.K2Node_PromotableOperator' $props $x $y
  Add-Pin $n 'A' 'in' $inCat $inSub
  Add-Pin $n 'B' 'in' $inCat $inSub
  Add-Pin $n 'ReturnValue' 'out' $outCat
  return $n
}

function Get-VarRef($name, $memberParent) {
  if ($memberParent) { return "VariableReference=(MemberParent=`"$memberParent`",MemberName=`"$name`")", 'SelfContextInfo=NotSelfContext' }
  return , "VariableReference=(MemberName=`"$name`",bSelfContext=True)"
}

function New-VarGet($name, $memberParent, $cat, $sub, $obj, $x, $y, $container = 'None') {
  $n = New-Node '/Script/BlueprintGraph.K2Node_VariableGet' (Get-VarRef $name $memberParent) $x $y
  Add-Pin $n $name 'out' $cat $sub $obj $null $container
  if ($memberParent) { Add-Pin $n 'self' 'in' 'object' '' $memberParent }
  return $n
}

function New-VarSet($name, $memberParent, $cat, $obj, $x, $y) {
  $n = New-Node '/Script/BlueprintGraph.K2Node_VariableSet' (Get-VarRef $name $memberParent) $x $y
  Add-Exec $n
  Add-Pin $n $name 'in' $cat '' $obj
  Add-Pin $n 'Output_Get' 'out' $cat '' $obj
  if ($memberParent) { Add-Pin $n 'self' 'in' 'object' '' $memberParent }
  return $n
}

function New-Branch($x, $y) {
  $n = New-Node '/Script/BlueprintGraph.K2Node_IfThenElse' @() $x $y
  Add-Pin $n 'execute' 'in' 'exec'
  Add-Pin $n 'Condition' 'in' 'bool' '' $null 'true'
  Add-Pin $n 'then' 'out' 'exec'
  Add-Pin $n 'else' 'out' 'exec'
  return $n
}

function New-IsValid($x, $y) {
  $n = New-Call $SYSTEM 'IsValid' $true $x $y
  Add-Pin $n 'Object' 'in' 'object' '' $OBJECT
  Add-Pin $n 'ReturnValue' 'out' 'bool'
  return $n
}

function New-PassedHeight($height, $x, $y) {
  $atLeast = New-Operator 'GreaterEqual' 'GreaterEqual_DoubleDouble' 'real' 'double' 'bool' $x $y
  (Get-Pin $atLeast 'B').Default = $height
  $toInt = New-Call $MATH 'Conv_BoolToInt' $true ($x + 200) $y
  Add-Pin $toInt 'InBool' 'in' 'bool'
  Add-Pin $toInt 'ReturnValue' 'out' 'int'
  Connect $atLeast 'ReturnValue' $toInt 'InBool'
  return @($atLeast, $toInt)
}

function Format-Pin($p) {
  $obj = if ($p.Obj) { "`"$($p.Obj)`"" } else { 'None' }
  $s = "PinId=$($p.Id),PinName=`"$($p.Name)`","
  if ($p.Dir -eq 'out') { $s += 'Direction="EGPD_Output",' }
  $s += "PinType.PinCategory=`"$($p.Cat)`",PinType.PinSubCategory=`"$($p.Sub)`",PinType.PinSubCategoryObject=$obj,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=$($p.Container),PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,"
  if ($null -ne $p.Default) { $s += "DefaultValue=`"$($p.Default)`"," }
  if ($p.Links.Count) { $s += 'LinkedTo=(' + (($p.Links | ForEach-Object { "$_," }) -join '') + '),' }
  $s += 'PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,'
  return "   CustomProperties Pin ($s)"
}

# --- Event Tick -> is there a pawn? ----------------------------------------------------
$tick = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$ACTOR`",MemberName=`"ReceiveTick`")", 'bOverrideFunction=True') 0 0
Add-Pin $tick 'then' 'out' 'exec'
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'

$pawn = New-Call $null 'K2_GetPawn' $true 0 200
Add-Pin $pawn 'ReturnValue' 'out' 'object' '' $PAWN_CLASS
$pawnValid = New-IsValid 250 200
$hasPawn = New-Branch 450 0
# The controller keeps ticking while paused; the pause menu BGM owns BgmAudioComponent then.
$gamePaused = New-Call $STATICS 'IsGamePaused' $true 450 -250
Add-Pin $gamePaused 'ReturnValue' 'out' 'bool'
$notPaused = New-Branch 600 -150

# --- Player height -> BGM index: one step per height passed ---------------------------
$location = New-Call $ACTOR 'K2_GetActorLocation' $true 250 450
Add-Pin $location 'self' 'in' 'object' '' $ACTOR
Add-Pin $location 'ReturnValue' 'out' 'struct' '' $VECTOR
$break = New-Call $MATH 'BreakVector' $true 500 450
Add-Pin $break 'InVec' 'in' 'struct' '' $VECTOR
Add-Pin $break 'X' 'out' 'real' 'double'
Add-Pin $break 'Y' 'out' 'real' 'double'
Add-Pin $break 'Z' 'out' 'real' 'double'
$bgm2 = New-PassedHeight $BGM2_HEIGHT 750 400
$bgm3 = New-PassedHeight $BGM3_HEIGHT 750 550
$index = New-Operator 'Add' 'Add_IntInt' 'int' '' 'int' 1200 450

$list = New-VarGet 'HeightBgmList' $null 'object' '' $SOUND 1200 650 'Array'
$lastIndex = New-Call $ARRAYLIB 'Array_LastIndex' $true 1450 650 '/Script/BlueprintGraph.K2Node_CallArrayFunction'
Add-Pin $lastIndex 'TargetArray' 'in' 'object' '' $SOUND $null 'Array'
Add-Pin $lastIndex 'ReturnValue' 'out' 'int'
$clamp = New-Call $MATH 'Clamp' $true 1700 450
Add-Pin $clamp 'Value' 'in' 'int' '' $null '0'
Add-Pin $clamp 'Min' 'in' 'int' '' $null '0'
Add-Pin $clamp 'Max' 'in' 'int' '' $null '0'
Add-Pin $clamp 'ReturnValue' 'out' 'int'
$wanted = New-Node '/Script/BlueprintGraph.K2Node_GetArrayItem' @() 1950 450
Add-Pin $wanted 'Array' 'in' 'object' '' $SOUND $null 'Array'
Add-Pin $wanted 'Dimension 1' 'in' 'int' '' $null '0'
Add-Pin $wanted 'Output' 'out' 'object' '' $SOUND

# --- Current BGM component in the game instance ---------------------------------------
$gi = New-Call $STATICS 'GetGameInstance' $true 450 200
Add-Pin $gi 'ReturnValue' 'out' 'object' '' $GAMEINST
$cast = New-Node '/Script/BlueprintGraph.K2Node_DynamicCast' @("TargetType=`"$GI_CLASS`"") 700 0
Add-Exec $cast
Add-Pin $cast 'CastFailed' 'out' 'exec'
Add-Pin $cast 'Object' 'in' 'object' '' $OBJECT
Add-Pin $cast 'AsBP My Game Instance' 'out' 'object' '' $GI_CLASS
Add-Pin $cast 'bSuccess' 'out' 'bool'
$bgm = New-VarGet 'BgmAudioComponent' $GI_CLASS 'object' '' $AUDIO 1000 200
$bgmValid = New-IsValid 1250 200
$hasBgm = New-Branch 1450 0

$current = New-VarGet 'Sound' $AUDIO 'object' '' $SOUND 1950 250
$differs = New-Operator 'NotEqual' 'NotEqual_ObjectObject' 'object' '' 'bool' 2200 250
(Get-Pin $differs 'A').Obj = $OBJECT; (Get-Pin $differs 'B').Obj = $OBJECT
$needsSwap = New-Branch 2400 0

function New-ArrayCall($func, [bool]$pure, $x, $y) {
  return New-Call $ARRAYLIB $func $pure $x $y '/Script/BlueprintGraph.K2Node_CallArrayFunction'
}

function New-AdjustVolume($level, $x, $y) {
  $n = New-Call $AUDIO 'AdjustVolume' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $AUDIO
  Add-Pin $n 'AdjustVolumeDuration' 'in' 'real' 'float' $null $FADE_SECONDS
  Add-Pin $n 'AdjustVolumeLevel' 'in' 'real' 'float' $null $level
  return $n
}

function New-SetPaused($paused, $x, $y) {
  $n = New-Call $AUDIO 'SetPaused' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $AUDIO
  Add-Pin $n 'bPause' 'in' 'bool' '' $null $paused
  return $n
}

function New-StorePlayer($x, $y) {
  $n = New-ArrayCall 'Array_Set' $false $x $y
  Add-Pin $n 'TargetArray' 'in' 'object' '' $AUDIO $null 'Array'
  Add-Pin $n 'Index' 'in' 'int' '' $null '0'
  Add-Pin $n 'Item' 'in' 'object' '' $AUDIO
  Add-Pin $n 'bSizeToFit' 'in' 'bool' '' $null 'true'
  return $n
}

# --- Leaving track: remember its player, fade it to silence, pause it later -----------
$players = New-VarGet 'HeightBgmPlayers' $null 'object' '' $AUDIO 2400 650 'Array'
$oldIndex = New-ArrayCall 'Array_Find' $true 2700 450
Add-Pin $oldIndex 'TargetArray' 'in' 'object' '' $SOUND $null 'Array'
Add-Pin $oldIndex 'ItemToFind' 'in' 'object' '' $SOUND
Add-Pin $oldIndex 'ReturnValue' 'out' 'int'
$storeOld = New-StorePlayer 2700 0
$setFading = New-VarSet 'FadingBgm' $null 'object' $AUDIO 3000 0
# Not exactly 0: a fade that reaches 0 can make the engine stop the sound, losing its position.
$fadeOld = New-AdjustVolume '0.001000' 3300 0

# --- Arriving track: resume its paused player, or create one the first time -----------
$slotValid = New-ArrayCall 'Array_IsValidIndex' $true 3300 450
Add-Pin $slotValid 'TargetArray' 'in' 'object' '' $AUDIO $null 'Array'
Add-Pin $slotValid 'IndexToTest' 'in' 'int' '' $null '0'
Add-Pin $slotValid 'ReturnValue' 'out' 'bool'
$hasSlot = New-Branch 3600 0
$saved = New-Node '/Script/BlueprintGraph.K2Node_GetArrayItem' @() 3600 450
Add-Pin $saved 'Array' 'in' 'object' '' $AUDIO $null 'Array'
Add-Pin $saved 'Dimension 1' 'in' 'int' '' $null '0'
Add-Pin $saved 'Output' 'out' 'object' '' $AUDIO
$savedValid = New-IsValid 3850 450
$hasPlayer = New-Branch 3900 0

$volume = New-VarGet 'VolumeMultiplier' $AUDIO 'real' 'float' $null 3900 650
# Paused still counts as playing; if the engine stopped it anyway, restart it instead of staying silent.
$isPlaying = New-Call $AUDIO 'IsPlaying' $true 4100 450
Add-Pin $isPlaying 'self' 'in' 'object' '' $AUDIO
Add-Pin $isPlaying 'ReturnValue' 'out' 'bool'
$stillPlaying = New-Branch 4150 -100
$restartVolume = New-Call $AUDIO 'SetVolumeMultiplier' $false 4500 -500
Add-Pin $restartVolume 'self' 'in' 'object' '' $AUDIO
Add-Pin $restartVolume 'NewVolumeMultiplier' 'in' 'real' 'float' $null '1.0'
$restart = New-Call $AUDIO 'FadeIn' $false 4800 -500
Add-Pin $restart 'self' 'in' 'object' '' $AUDIO
Add-Pin $restart 'FadeInDuration' 'in' 'real' 'float' $null $FADE_SECONDS
Add-Pin $restart 'FadeVolumeLevel' 'in' 'real' 'float' $null '1.000000'
$unpause = New-SetPaused 'false' 4200 -250
$syncVolume = New-Call $AUDIO 'SetVolumeMultiplier' $false 4500 -250
Add-Pin $syncVolume 'self' 'in' 'object' '' $AUDIO
Add-Pin $syncVolume 'NewVolumeMultiplier' 'in' 'real' 'float' $null '1.0'
$fadeUp = New-AdjustVolume '1.000000' 4800 -250
$registerResumed = New-VarSet 'BgmAudioComponent' $GI_CLASS 'object' $AUDIO 5100 -250

$create = New-Call $STATICS 'CreateSound2D' $false 4200 150
Add-Pin $create 'Sound' 'in' 'object' '' $SOUND
Add-Pin $create 'VolumeMultiplier' 'in' 'real' 'float' $null '1.0'
Add-Pin $create 'bPersistAcrossLevelTransition' 'in' 'bool' '' $null 'true'
# Kept alive so it can be paused and resumed later.
Add-Pin $create 'bAutoDestroy' 'in' 'bool' '' $null 'false'
Add-Pin $create 'ReturnValue' 'out' 'object' '' $AUDIO
$fadeIn = New-Call $AUDIO 'FadeIn' $false 4500 150
Add-Pin $fadeIn 'self' 'in' 'object' '' $AUDIO
Add-Pin $fadeIn 'FadeInDuration' 'in' 'real' 'float' $null $FADE_SECONDS
Add-Pin $fadeIn 'FadeVolumeLevel' 'in' 'real' 'float' $null '1.000000'
$storeNew = New-StorePlayer 4800 150
$registerCreated = New-VarSet 'BgmAudioComponent' $GI_CLASS 'object' $AUDIO 5100 150

# --- After the fade, pause the silent track unless the player came straight back -----
$wait = New-Call $SYSTEM 'RetriggerableDelay' $false 5400 0
Add-Pin $wait 'Duration' 'in' 'real' 'float' $null $FADE_SECONDS
$fading = New-VarGet 'FadingBgm' $null 'object' '' $AUDIO 5400 250
$stillFaded = New-Operator 'NotEqual' 'NotEqual_ObjectObject' 'object' '' 'bool' 5650 250
(Get-Pin $stillFaded 'A').Obj = $OBJECT; (Get-Pin $stillFaded 'B').Obj = $OBJECT
$shouldPause = New-Branch 5900 0
$pause = New-SetPaused 'true' 6200 0

Connect $tick 'then' $hasPawn 'execute'
Connect $pawn 'ReturnValue' $pawnValid 'Object'
Connect $pawnValid 'ReturnValue' $hasPawn 'Condition'
Connect $pawn 'ReturnValue' $location 'self'
Connect $location 'ReturnValue' $break 'InVec'
Connect $break 'Z' $bgm2[0] 'A'
Connect $break 'Z' $bgm3[0] 'A'
Connect $bgm2[1] 'ReturnValue' $index 'A'
Connect $bgm3[1] 'ReturnValue' $index 'B'
Connect $index 'ReturnValue' $clamp 'Value'
Connect $list 'HeightBgmList' $lastIndex 'TargetArray'
Connect $lastIndex 'ReturnValue' $clamp 'Max'
Connect $list 'HeightBgmList' $wanted 'Array'
Connect $clamp 'ReturnValue' $wanted 'Dimension 1'
Connect $hasPawn 'then' $notPaused 'execute'
Connect $gamePaused 'ReturnValue' $notPaused 'Condition'
Connect $notPaused 'else' $cast 'execute'
Connect $gi 'ReturnValue' $cast 'Object'
Connect $cast 'AsBP My Game Instance' $bgm 'self'
Connect $bgm 'BgmAudioComponent' $bgmValid 'Object'
Connect $bgmValid 'ReturnValue' $hasBgm 'Condition'
Connect $cast 'then' $hasBgm 'execute'
Connect $bgm 'BgmAudioComponent' $current 'self'
Connect $current 'Sound' $differs 'A'
Connect $wanted 'Output' $differs 'B'
Connect $differs 'ReturnValue' $needsSwap 'Condition'
Connect $hasBgm 'then' $needsSwap 'execute'
# Leaving track (the current BgmAudioComponent)
Connect $needsSwap 'then' $storeOld 'execute'
Connect $players 'HeightBgmPlayers' $storeOld 'TargetArray'
Connect $list 'HeightBgmList' $oldIndex 'TargetArray'
Connect $current 'Sound' $oldIndex 'ItemToFind'
Connect $oldIndex 'ReturnValue' $storeOld 'Index'
Connect $bgm 'BgmAudioComponent' $storeOld 'Item'
Connect $storeOld 'then' $setFading 'execute'
Connect $bgm 'BgmAudioComponent' $setFading 'FadingBgm'
Connect $setFading 'then' $fadeOld 'execute'
Connect $bgm 'BgmAudioComponent' $fadeOld 'self'
# Arriving track: resume if we already have a player for it
Connect $fadeOld 'then' $hasSlot 'execute'
Connect $players 'HeightBgmPlayers' $slotValid 'TargetArray'
Connect $clamp 'ReturnValue' $slotValid 'IndexToTest'
Connect $slotValid 'ReturnValue' $hasSlot 'Condition'
Connect $players 'HeightBgmPlayers' $saved 'Array'
Connect $clamp 'ReturnValue' $saved 'Dimension 1'
Connect $saved 'Output' $savedValid 'Object'
Connect $savedValid 'ReturnValue' $hasPlayer 'Condition'
Connect $hasSlot 'then' $hasPlayer 'execute'
Connect $bgm 'BgmAudioComponent' $volume 'self'
Connect $hasPlayer 'then' $stillPlaying 'execute'
Connect $saved 'Output' $isPlaying 'self'
Connect $isPlaying 'ReturnValue' $stillPlaying 'Condition'
Connect $stillPlaying 'else' $restartVolume 'execute'
Connect $saved 'Output' $restartVolume 'self'
Connect $volume 'VolumeMultiplier' $restartVolume 'NewVolumeMultiplier'
Connect $restartVolume 'then' $restart 'execute'
Connect $saved 'Output' $restart 'self'
Connect $restart 'then' $registerResumed 'execute'
Connect $stillPlaying 'then' $unpause 'execute'
Connect $saved 'Output' $unpause 'self'
Connect $unpause 'then' $syncVolume 'execute'
Connect $saved 'Output' $syncVolume 'self'
Connect $volume 'VolumeMultiplier' $syncVolume 'NewVolumeMultiplier'
Connect $syncVolume 'then' $fadeUp 'execute'
Connect $saved 'Output' $fadeUp 'self'
Connect $fadeUp 'then' $registerResumed 'execute'
Connect $cast 'AsBP My Game Instance' $registerResumed 'self'
Connect $saved 'Output' $registerResumed 'BgmAudioComponent'
# ...or create it the first time
Connect $hasSlot 'else' $create 'execute'
Connect $hasPlayer 'else' $create 'execute'
Connect $wanted 'Output' $create 'Sound'
Connect $volume 'VolumeMultiplier' $create 'VolumeMultiplier'
Connect $create 'then' $fadeIn 'execute'
Connect $create 'ReturnValue' $fadeIn 'self'
Connect $fadeIn 'then' $storeNew 'execute'
Connect $players 'HeightBgmPlayers' $storeNew 'TargetArray'
Connect $clamp 'ReturnValue' $storeNew 'Index'
Connect $create 'ReturnValue' $storeNew 'Item'
Connect $storeNew 'then' $registerCreated 'execute'
Connect $cast 'AsBP My Game Instance' $registerCreated 'self'
Connect $create 'ReturnValue' $registerCreated 'BgmAudioComponent'
# Pause the faded-out track once the fade is over
Connect $registerResumed 'then' $wait 'execute'
Connect $registerCreated 'then' $wait 'execute'
Connect $wait 'then' $shouldPause 'execute'
Connect $fading 'FadingBgm' $stillFaded 'A'
Connect $bgm 'BgmAudioComponent' $stillFaded 'B'
Connect $stillFaded 'ReturnValue' $shouldPause 'Condition'
Connect $shouldPause 'then' $pause 'execute'
Connect $fading 'FadingBgm' $pause 'self'

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
[IO.File]::WriteAllText((Join-Path $OutDir 'HeightBgm_Controller_Tick.txt'), $sb.ToString(), [Text.UTF8Encoding]::new($false))
"Generated $($script:nodes.Count) nodes"
