param([string]$OutDir)
# Paste text for BP_AreaBgm (setup_area_bgm.py; the user, 2026-11-22: "the BGM by area, not by height").
#   Begin Play: the player controller's HeightBgmList becomes just this level's AreaBgm. Its Tick (the old height
#   BGM, HeightBgm_Controller_Tick.txt) then always picks index 0 - this track - and crossfades to it from whatever
#   the game instance was playing, as before. No controller yet: try again 0.2 s later.
#   If the game instance still plays its launch track (GameBgm_Cue, started at Init), SetSound swaps it at once.
if (-not $OutDir) { throw 'OutDir is required' }
$lightGen = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_heaven_light.ps1') -Encoding UTF8
$cut = ($lightGen | Select-String -Pattern '^# ===== BP_LightBeam' | Select-Object -First 1).LineNumber - 1
$helpers = $lightGen[1..($cut - 1)] -join "`n"
. ([ScriptBlock]::Create($helpers))

$SOUND_BASE = "/Script/CoreUObject.Class'/Script/Engine.SoundBase'"
$PC_CLASS = "/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPerson/Blueprints/BP_ThirdPersonPlayerController.BP_ThirdPersonPlayerController_C'"

Reset-Graph 100
$begin = Event 'ReceiveBeginPlay' 0 0
$cast = New-Node '/Script/BlueprintGraph.K2Node_DynamicCast' @("TargetType=`"$PC_CLASS`"") 400 0
Add-Exec $cast
Add-Pin $cast 'CastFailed' 'out' 'exec'
Add-Pin $cast 'Object' 'in' 'object' '' $OBJECT
Add-Pin $cast 'AsBP Third Person Player Controller' 'out' 'object' '' $PC_CLASS
Add-Pin $cast 'bSuccess' 'out' 'bool'
Connect (Controller 150 200) 'ReturnValue' $cast 'Object'
Connect $begin 'then' $cast 'execute'

$one = New-Node '/Script/BlueprintGraph.K2Node_MakeArray' @('NumInputs=1') 700 250
Add-Pin $one '[0]' 'in' 'object' '' $SOUND_BASE
Add-Pin $one 'Array' 'out' 'object' '' $SOUND_BASE $null 'Array'
Connect (New-VarGet 'AreaBgm' $null 'object' '' $SOUND_BASE 500 300) 'AreaBgm' $one '[0]'

$set = New-Node '/Script/BlueprintGraph.K2Node_VariableSet' @("VariableReference=(MemberParent=`"$PC_CLASS`",MemberName=`"HeightBgmList`")", 'SelfContextInfo=NotSelfContext') 1000 0
Add-Exec $set
Add-Pin $set 'HeightBgmList' 'in' 'object' '' $SOUND_BASE $null 'Array'
Add-Pin $set 'Output_Get' 'out' 'object' '' $SOUND_BASE $null 'Array'
Add-Pin $set 'self' 'in' 'object' '' $PC_CLASS
Connect $cast 'AsBP Third Person Player Controller' $set 'self'
Connect $one 'Array' $set 'HeightBgmList'
Connect $cast 'then' $set 'execute'

$retry = Delay '0.2' 400 450
Connect $cast 'CastFailed' $retry 'execute'
Connect $retry 'then' $cast 'execute'

# The game instance starts GameBgm_Cue at Init (2026-11-22: "GameBGM cuts in at the start"). If that launch
# track is still what plays, swap it for this area's at once (SetSound restarts it), so the crossfade never runs.
$AUDIO = "/Script/CoreUObject.Class'/Script/Engine.AudioComponent'"
$GAME_BGM = '/Game/Sound/BGM/GameBgm_Cue.GameBgm_Cue'
$giCast = GameInstance 1300 0
Connect $set 'then' $giCast 'execute'
$bgm = New-VarGet 'BgmAudioComponent' $GI_CLASS 'object' '' $AUDIO 1350 300
Connect $giCast $GI_OUT $bgm 'self'
$bgmValid = Valid $bgm 'BgmAudioComponent' 1600 300
$playing = New-VarGet 'Sound' $AUDIO 'object' '' $SOUND_BASE 1600 450
Connect $bgm 'BgmAudioComponent' $playing 'self'
# Plain calls, not promotable operators: B is an asset literal.
function SameObject($func, [double]$x, [double]$y) {
  $n = New-Call $MATH $func $true $x $y
  Add-Pin $n 'A' 'in' 'object' '' $OBJECT
  Add-Pin $n 'B' 'in' 'object' '' $OBJECT
  Add-Pin $n 'ReturnValue' 'out' 'bool'
  return $n
}
$isLaunch = SameObject 'EqualEqual_ObjectObject' 1850 450
Connect $playing 'Sound' $isLaunch 'A'
(Get-Pin $isLaunch 'B') | Add-Member DefaultObject $GAME_BGM
$areaBgm = New-VarGet 'AreaBgm' $null 'object' '' $SOUND_BASE 1600 600
$isOther = SameObject 'NotEqual_ObjectObject' 1850 600
Connect $areaBgm 'AreaBgm' $isOther 'A'
(Get-Pin $isOther 'B') | Add-Member DefaultObject $GAME_BGM
$launchStill = Both $isLaunch 'ReturnValue' $isOther 'ReturnValue' 'BooleanAND' 2050 500
# Two branches, not one AND: a pure AND reads every input, so Sound was read from a None component (PIE error).
$hasBgm = New-Branch 2000 0
Connect $giCast 'then' $hasBgm 'execute'
Connect $bgmValid 'ReturnValue' $hasBgm 'Condition'
$branch = New-Branch 2450 0
Connect $hasBgm 'then' $branch 'execute'
Connect $launchStill 'ReturnValue' $branch 'Condition'
$setSound = New-Call $AUDIO 'SetSound' $false 2700 0
Add-Pin $setSound 'self' 'in' 'object' '' $AUDIO
Add-Pin $setSound 'NewSound' 'in' 'object' '' $SOUND_BASE
Connect $bgm 'BgmAudioComponent' $setSound 'self'
Connect $areaBgm 'AreaBgm' $setSound 'NewSound'
Connect $branch 'then' $setSound 'execute'

# No BGM yet (the game instance's Init waits 0.2 s before its GameBgm, and now skips it once one exists):
# start this area's track here, the way the controller would (kept alive, persists), and register it.
$create = New-Call $STATICS 'CreateSound2D' $false 2450 800
Add-Pin $create 'Sound' 'in' 'object' '' $SOUND_BASE
Add-Pin $create 'VolumeMultiplier' 'in' 'real' 'float' $null '1.0'
Add-Pin $create 'bPersistAcrossLevelTransition' 'in' 'bool' '' $null 'true'
Add-Pin $create 'bAutoDestroy' 'in' 'bool' '' $null 'false'
Add-Pin $create 'ReturnValue' 'out' 'object' '' $AUDIO
Connect (New-VarGet 'AreaBgm' $null 'object' '' $SOUND_BASE 2200 1000) 'AreaBgm' $create 'Sound'
$volume = New-Operator 'Multiply' 'Multiply_DoubleDouble' 'real' 'double' 'real' 2200 1150
(Get-Pin $volume 'ReturnValue').Sub = 'double'
Connect (GiGet $giCast 'BGM Volume' 'real' 'double' 1950 1150) 'BGM Volume' $volume 'A'
Connect (GiGet $giCast 'Master Volume' 'real' 'double' 1950 1300) 'Master Volume' $volume 'B'
Connect $volume 'ReturnValue' $create 'VolumeMultiplier'
Connect $hasBgm 'else' $create 'execute'
$fadeIn = New-Call $AUDIO 'FadeIn' $false 2750 800
Add-Pin $fadeIn 'self' 'in' 'object' '' $AUDIO
Add-Pin $fadeIn 'FadeInDuration' 'in' 'real' 'float' $null '1.0'
Add-Pin $fadeIn 'FadeVolumeLevel' 'in' 'real' 'float' $null '1.0'
Connect $create 'ReturnValue' $fadeIn 'self'
Connect $create 'then' $fadeIn 'execute'
$register = GiSet $giCast 'BgmAudioComponent' 'object' '' 3050 800
(Get-Pin $register 'BgmAudioComponent').Obj = $AUDIO; (Get-Pin $register 'Output_Get').Obj = $AUDIO
Connect $create 'ReturnValue' $register 'BgmAudioComponent'
Connect $fadeIn 'then' $register 'execute'
Write-Graph 'BP_AreaBgm_EventGraph.txt'
