param([string]$OutDir)
# Paste text for the danger button (variables from import_danger_button.py and setup_danger_button_effects.py):
#   BP_DangerButton_EventGraph.txt   Begin Play: DangerStage back to 0. The player in front of it (Trigger): it takes
#       input; E (IA_UseItem) there, once at a time: the button goes down and up, DangerStage + 1. The third press: the
#       player held still, PressSound plays; when it ends DangerStage 4 (the finale on screen); FinaleSeconds later the
#       game quits.
#   WBP_DangerOverlay_EventGraph.txt   every frame: Crack1 shown from stage 1, Crack2 from stage 2 (both gone in the
#       finale), Finale shown at stage 4 with its material's T counting up from 0.
if (-not $OutDir) { throw 'OutDir is required' }
$cageGen = Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_hell_cage.ps1'
$defs = Get-Content -LiteralPath $cageGen -Encoding UTF8 | Select-Object -Skip 10 -First 172
. ([ScriptBlock]::Create(($defs -join "`n")))

$SCENE = "/Script/CoreUObject.Class'/Script/Engine.SceneComponent'"
$SOUND_BASE = "/Script/CoreUObject.Class'/Script/Engine.SoundBase'"
$USER_WIDGET = "/Script/CoreUObject.Class'/Script/UMG.UserWidget'"
$WIDGET_CLASS = "/Script/CoreUObject.Class'/Script/UMG.Widget'"
$IMAGE = "/Script/CoreUObject.Class'/Script/UMG.Image'"
$MID = "/Script/CoreUObject.Class'/Script/Engine.MaterialInstanceDynamic'"
$GEOMETRY = "/Script/CoreUObject.ScriptStruct'/Script/SlateCore.Geometry'"
$QUIT_ENUM = "/Script/CoreUObject.Enum'/Script/Engine.EQuitPreference'"
$INPUT_ACTION = "/Script/CoreUObject.Class'/Script/EnhancedInput.InputAction'"
$USE_ITEM = "/Script/EnhancedInput.InputAction'/Game/Input/Actions/IA_UseItem.IA_UseItem'"
$CAP_UP = '0.000000,0.000000,162.000000'
$CAP_DOWN = '0.000000,0.000000,150.000000'

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
function Real($name, [double]$x, [double]$y) { New-VarGet $name $null 'real' 'double' $null $x $y }
function PlayerIn([double]$x, [double]$y) {
  $n = New-Call $PRIMITIVE 'IsOverlappingActor' $true $x $y
  Add-Pin $n 'self' 'in' 'object' '' $PRIMITIVE
  Add-Pin $n 'Other' 'in' 'object' '' $ACTOR
  Add-Pin $n 'ReturnValue' 'out' 'bool'
  Connect (New-VarGet 'Trigger' $null 'object' '' $BOX ($x - 200) $y) 'Trigger' $n 'self'
  Connect (Player ($x - 250) ($y + 100)) 'ReturnValue' $n 'Other'
  return $n
}
# This actor's own input on or off (a self call: the player's controller).
function OwnInput($func, [double]$x, [double]$y) {
  $n = New-Call $null $func $false $x $y
  Add-Pin $n 'PlayerController' 'in' 'object' '' $CONTROLLER
  Connect (Controller ($x - 200) ($y + 200)) 'ReturnValue' $n 'PlayerController'
  return $n
}
function PlayerInput($func, [double]$x, [double]$y) {
  $n = New-Call $ACTOR $func $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR
  Add-Pin $n 'PlayerController' 'in' 'object' '' $CONTROLLER
  Connect (Player ($x - 200) ($y + 200)) 'ReturnValue' $n 'self'
  Connect (Controller ($x - 200) ($y + 300)) 'ReturnValue' $n 'PlayerController'
  return $n
}
function CapTo($where, $seconds, [double]$x, [double]$y) {
  $n = New-Call $SYSTEM 'MoveComponentTo' $false $x $y
  $n.Props = @('bWantsEnumToExecExpansion=True') + $n.Props
  $n.Pins.Clear()
  Add-Pin $n 'Move' 'in' 'exec'
  Add-Pin $n 'then' 'out' 'exec'
  Add-Pin $n 'Component' 'in' 'object' '' $SCENE
  Add-Pin $n 'TargetRelativeLocation' 'in' 'struct' '' $VECTOR $where
  Add-Pin $n 'TargetRelativeRotation' 'in' 'struct' '' $ROTATOR '0, 0, 0'
  Add-Pin $n 'bEaseOut' 'in' 'bool' '' $null 'true'
  Add-Pin $n 'bEaseIn' 'in' 'bool' '' $null 'false'
  Add-Pin $n 'OverTime' 'in' 'real' 'float' $null $seconds
  Add-Pin $n 'bForceShortestRotationPath' 'in' 'bool' '' $null 'false'
  Connect (New-VarGet 'Cap' $null 'object' '' "/Script/CoreUObject.Class'/Script/Engine.StaticMeshComponent'" ($x - 200) ($y + 250)) 'Cap' $n 'Component'
  return $n
}

# ===== BP_DangerButton =====================================================================================
Reset-Graph 100
$begin = Event 'ReceiveBeginPlay' 0 0
$cast0 = GameInstance 300 0
$reset = GiSet $cast0 'DangerStage' 'int' '' 600 0 '0'
Connect $begin 'then' $cast0 'execute'
Connect $cast0 'then' $reset 'execute'

$enter = Event 'ReceiveActorBeginOverlap' 0 500
Add-Pin $enter 'OtherActor' 'out' 'object' '' $ACTOR
$came = New-Branch 300 500
Connect (PlayerIn 250 750) 'ReturnValue' $came 'Condition'
$listen = OwnInput 'EnableInput' 600 500
Connect $enter 'then' $came 'execute'
Connect $came 'then' $listen 'execute'

$leave = Event 'ReceiveActorEndOverlap' 0 1000
Add-Pin $leave 'OtherActor' 'out' 'object' '' $ACTOR
$gone = New-Branch 300 1000
Connect (PlayerIn 250 1250) 'ReturnValue' $gone 'Condition'
$deaf = OwnInput 'DisableInput' 600 1000
Connect $leave 'then' $gone 'execute'
Connect $gone 'else' $deaf 'execute'

$press = New-Node '/Script/InputBlueprintNodes.K2Node_EnhancedInputAction' @("InputAction=`"$USE_ITEM`"") 0 1600
foreach ($pin in 'Triggered', 'Started', 'Ongoing', 'Canceled', 'Completed') { Add-Pin $press $pin 'out' 'exec' }
Add-Pin $press 'ActionValue' 'out' 'bool'
Add-Pin $press 'ElapsedSeconds' 'out' 'real' 'double'
Add-Pin $press 'TriggeredSeconds' 'out' 'real' 'double'
Add-Pin $press 'InputAction' 'out' 'object' '' $INPUT_ACTION
$once = New-Branch 300 1600
Connect (New-VarGet 'Busy' $null 'bool' '' $null 150 1800) 'Busy' $once 'Condition'
$there = New-Branch 550 1600
Connect (PlayerIn 450 1850) 'ReturnValue' $there 'Condition'
$busy = SetSelf 'Busy' 'bool' 'true' 800 1600
$down = CapTo $CAP_DOWN '0.08' 1100 1600
$up = CapTo $CAP_UP '0.15' 1450 1600
$cast = GameInstance 1850 1600
$count = GiSet $cast 'DangerStage' 'int' '' 2150 1600
$plus = New-Operator 'Add' 'Add_IntInt' 'int' '' 'int' 2000 1850
Connect (GiGet $cast 'DangerStage' 'int' '' 1800 1850) 'DangerStage' $plus 'A'
(Get-Pin $plus 'B').Default = '1'
Connect $plus 'ReturnValue' $count 'DangerStage'
$third = New-Branch 2450 1600
$isThird = New-Operator 'GreaterEqual' 'GreaterEqual_IntInt' 'int' '' 'bool' 2350 1850
Connect $count 'Output_Get' $isThird 'A'
(Get-Pin $isThird 'B').Default = '3'
Connect $isThird 'ReturnValue' $third 'Condition'
# The first and second presses: the screen cracks with a "baki!" (a little lower the second time).
$crack = New-Call $STATICS 'PlaySound2D' $false 2750 2150
Add-Pin $crack 'Sound' 'in' 'object' '' $SOUND_BASE
Add-Pin $crack 'VolumeMultiplier' 'in' 'real' 'float' $null '1.0'
Add-Pin $crack 'PitchMultiplier' 'in' 'real' 'float'
Add-Pin $crack 'StartTime' 'in' 'real' 'float' $null '0.0'
Connect (New-VarGet 'CrackSound' $null 'object' '' $SOUND_BASE 2550 2350) 'CrackSound' $crack 'Sound'
$isSecond = New-Operator 'GreaterEqual' 'GreaterEqual_IntInt' 'int' '' 'bool' 2350 2450
Connect $count 'Output_Get' $isSecond 'A'
(Get-Pin $isSecond 'B').Default = '2'
$pitch = New-Call $MATH 'SelectFloat' $true 2550 2450
Add-Pin $pitch 'A' 'in' 'real' 'double' $null '0.85'
Add-Pin $pitch 'B' 'in' 'real' 'double' $null '1.0'
Add-Pin $pitch 'bPickA' 'in' 'bool'
Add-Pin $pitch 'ReturnValue' 'out' 'real' 'double'
Connect $isSecond 'ReturnValue' $pitch 'bPickA'
Connect $pitch 'ReturnValue' $crack 'PitchMultiplier'
$free = SetSelf 'Busy' 'bool' 'false' 3100 2150
$hold = PlayerInput 'DisableInput' 2750 1600
$play = New-Call $STATICS 'PlaySound2D' $false 3050 1600
Add-Pin $play 'Sound' 'in' 'object' '' $SOUND_BASE
Add-Pin $play 'VolumeMultiplier' 'in' 'real' 'float' $null '1.0'
Add-Pin $play 'PitchMultiplier' 'in' 'real' 'float' $null '1.0'
Add-Pin $play 'StartTime' 'in' 'real' 'float' $null '0.0'
Connect (New-VarGet 'PressSound' $null 'object' '' $SOUND_BASE 2850 1850) 'PressSound' $play 'Sound'
$listenEnd = Delay '0.0' 3350 1600
Connect (Real 'SoundSeconds' 3200 1850) 'SoundSeconds' $listenEnd 'Duration'
$cast2 = GameInstance 3650 1600
$finale = GiSet $cast2 'DangerStage' 'int' '' 3950 1600 '4'
# The finale's noise starts with it.
$noise = New-Call $STATICS 'PlaySound2D' $false 4250 1600
Add-Pin $noise 'Sound' 'in' 'object' '' $SOUND_BASE
Add-Pin $noise 'VolumeMultiplier' 'in' 'real' 'float' $null '1.0'
Add-Pin $noise 'PitchMultiplier' 'in' 'real' 'float' $null '1.0'
Add-Pin $noise 'StartTime' 'in' 'real' 'float' $null '0.0'
Connect (New-VarGet 'FinaleSound' $null 'object' '' $SOUND_BASE 4050 1850) 'FinaleSound' $noise 'Sound'
$watch = Delay '0.0' 4550 1600
Connect (Real 'FinaleSeconds' 4400 1850) 'FinaleSeconds' $watch 'Duration'
$quit = New-Call $SYSTEM 'QuitGame' $false 4850 1600
Add-Pin $quit 'SpecificPlayer' 'in' 'object' '' $CONTROLLER
Add-Pin $quit 'QuitPreference' 'in' 'byte' '' $QUIT_ENUM 'Quit'
Add-Pin $quit 'bIgnorePlatformRestrictions' 'in' 'bool' '' $null 'false'
Connect (Controller 4650 1850) 'ReturnValue' $quit 'SpecificPlayer'
Connect $press 'Started' $once 'execute'
Connect $once 'else' $there 'execute'
Connect $there 'then' $busy 'execute'
Connect $busy 'then' $down 'Move'
Connect $down 'then' $up 'Move'
Connect $up 'then' $cast 'execute'
Connect $cast 'then' $count 'execute'
Connect $count 'then' $third 'execute'
Connect $third 'else' $crack 'execute'
Connect $crack 'then' $free 'execute'
Connect $third 'then' $hold 'execute'
Chain @($hold, $play, $listenEnd, $cast2)
Connect $cast2 'then' $finale 'execute'
# Every other sound (the BGM too) down to 0 while the finale plays.
$mute = New-Call $STATICS 'PushSoundMixModifier' $false 4100 1350
Add-Pin $mute 'InSoundMixModifier' 'in' 'object' '' "/Script/CoreUObject.Class'/Script/Engine.SoundMix'"
Connect (New-VarGet 'FinaleMute' $null 'object' '' "/Script/CoreUObject.Class'/Script/Engine.SoundMix'" 3900 1450) 'FinaleMute' $mute 'InSoundMixModifier'
Chain @($finale, $mute, $noise, $watch, $quit)
Write-Graph 'BP_DangerButton_EventGraph.txt'

# ===== WBP_DangerOverlay ===================================================================================
Reset-Graph 100
function StageAtLeast($stage, $value, [double]$x, [double]$y) {
  $n = New-Operator 'GreaterEqual' 'GreaterEqual_IntInt' 'int' '' 'bool' $x $y
  Connect $stage 'DangerStage' $n 'A'
  (Get-Pin $n 'B').Default = $value
  return $n
}
function Opacity($imageName, $shown, $shownPin, [double]$x, [double]$y) {
  $pick = New-Call $MATH 'SelectFloat' $true ($x - 200) ($y + 250)
  Add-Pin $pick 'A' 'in' 'real' 'double' $null '1.0'
  Add-Pin $pick 'B' 'in' 'real' 'double' $null '0.0'
  Add-Pin $pick 'bPickA' 'in' 'bool'
  Add-Pin $pick 'ReturnValue' 'out' 'real' 'double'
  Connect $shown $shownPin $pick 'bPickA'
  $n = New-Call $WIDGET_CLASS 'SetRenderOpacity' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $WIDGET_CLASS
  Add-Pin $n 'InOpacity' 'in' 'real' 'float'
  Connect (New-VarGet $imageName $null 'object' '' $IMAGE ($x - 200) ($y + 150)) $imageName $n 'self'
  Connect $pick 'ReturnValue' $n 'InOpacity'
  return $n
}
function Both($a, $aPin, $b, $bPin, [double]$x, [double]$y) {
  $n = New-Call $MATH 'BooleanAND' $true $x $y
  Add-Pin $n 'A' 'in' 'bool'
  Add-Pin $n 'B' 'in' 'bool'
  Add-Pin $n 'ReturnValue' 'out' 'bool'
  Connect $a $aPin $n 'A'
  Connect $b $bPin $n 'B'
  return $n
}
$tick = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$USER_WIDGET`",MemberName=`"Tick`")", 'bOverrideFunction=True') 0 0
Add-Pin $tick 'then' 'out' 'exec'
Add-Pin $tick 'MyGeometry' 'out' 'struct' '' $GEOMETRY
Add-Pin $tick 'InDeltaTime' 'out' 'real' 'float'
$cast = GameInstance 300 0
$stage = GiGet $cast 'DangerStage' 'int' '' 300 300
$one = StageAtLeast $stage '1' 550 400
$two = StageAtLeast $stage '2' 550 500
$four = StageAtLeast $stage '4' 550 600
$notFinale = New-Call $MATH 'Not_PreBool' $true 750 650
Add-Pin $notFinale 'A' 'in' 'bool'
Add-Pin $notFinale 'ReturnValue' 'out' 'bool'
Connect $four 'ReturnValue' $notFinale 'A'
$c1 = Opacity 'Crack1' (Both $one 'ReturnValue' $notFinale 'ReturnValue' 950 400) 'ReturnValue' 1200 0
$c2 = Opacity 'Crack2' (Both $two 'ReturnValue' $notFinale 'ReturnValue' 950 550) 'ReturnValue' 1550 0
$fin = Opacity 'Finale' $four 'ReturnValue' 1900 0
$inFinale = New-Branch 2200 0
Connect $four 'ReturnValue' $inFinale 'Condition'
Connect $tick 'then' $cast 'execute'
Connect $cast 'then' $c1 'execute'
Chain @($c1, $c2, $fin, $inFinale)
$later = New-VarSet 'FinaleTime' $null 'real' $null 2500 0
(Get-Pin $later 'FinaleTime').Sub = 'double'; (Get-Pin $later 'Output_Get').Sub = 'double'
$sum = New-Operator 'Add' 'Add_DoubleDouble' 'real' 'double' 'real' 2350 250
(Get-Pin $sum 'ReturnValue').Sub = 'double'
Connect (Real 'FinaleTime' 2150 250) 'FinaleTime' $sum 'A'
Connect $tick 'InDeltaTime' $sum 'B'
Connect $sum 'ReturnValue' $later 'FinaleTime'
$dynamic = New-Call $IMAGE 'GetDynamicMaterial' $false 2800 0
Add-Pin $dynamic 'self' 'in' 'object' '' $IMAGE
Add-Pin $dynamic 'ReturnValue' 'out' 'object' '' $MID
Connect (New-VarGet 'Finale' $null 'object' '' $IMAGE 2600 200) 'Finale' $dynamic 'self'
$param = New-Call $MID 'SetScalarParameterValue' $false 3150 0
Add-Pin $param 'self' 'in' 'object' '' $MID
Add-Pin $param 'ParameterName' 'in' 'name' '' $null 'T'
Add-Pin $param 'Value' 'in' 'real' 'float'
Connect $dynamic 'ReturnValue' $param 'self'
Connect $later 'Output_Get' $param 'Value'
$zero = SetSelf 'FinaleTime' 'real' '0.0' 2500 300
(Get-Pin $zero 'FinaleTime').Sub = 'double'; (Get-Pin $zero 'Output_Get').Sub = 'double'
Connect $inFinale 'then' $later 'execute'
Chain @($later, $dynamic, $param)
Connect $inFinale 'else' $zero 'execute'
Write-Graph 'WBP_DangerOverlay_EventGraph.txt'
