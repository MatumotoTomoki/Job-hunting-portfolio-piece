param([string]$OutDir)
# Paste text for BP_ShardLock (setup_shard_lock.py; hidden area 3's locked light gate, 2026-11-23):
#   Begin Play: the Gate's Tick off (its pillar never comes, there is no way in).
#   Tick, not Opened: n = how many of Shard1..3 are gone (taken); both counters read "n / 3"; at 3: Opened, the Gate's
#     Tick on (it works as ever from then), the Seal and both counters hidden, S_GateLight at SE Volume x Master Volume.
if (-not $OutDir) { throw 'OutDir is required' }
$lightGen = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_heaven_light.ps1') -Encoding UTF8
$cut = ($lightGen | Select-String -Pattern '^# ===== BP_LightBeam' | Select-Object -First 1).LineNumber - 1
. ([ScriptBlock]::Create(($lightGen[1..($cut - 1)] -join "`n")))

$GATE_CLASS = "/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPerson/Blueprints/Gimmicks/Area/BP_LightGate.BP_LightGate_C'"
$TEXT_COMP = "/Script/CoreUObject.Class'/Script/Engine.TextRenderComponent'"
$SOUND_BASE = "/Script/CoreUObject.Class'/Script/Engine.SoundBase'"

function GateTick($value, [double]$x, [double]$y) {
  $n = New-Call $ACTOR 'SetActorTickEnabled' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR
  Add-Pin $n 'bEnabled' 'in' 'bool' '' $null $value
  Connect (New-VarGet 'Gate' $null 'object' '' $GATE_CLASS ($x - 200) ($y + 200)) 'Gate' $n 'self'
  return $n
}
function Gone($name, [double]$x, [double]$y) {
  $valid = Valid (New-VarGet $name $null 'object' '' $SHARD_CLASS ($x - 200) $y) $name $x $y
  $not = MathCall 'Not_PreBool' @('A') 'bool' '' 'bool' '' ($x + 150) $y
  Connect $valid 'ReturnValue' $not 'A'
  $int = MathCall 'Conv_BoolToInt' @('InBool') 'bool' '' 'int' '' ($x + 300) $y
  Connect $not 'ReturnValue' $int 'InBool'
  return $int
}
function SetWords($name, $text, [double]$x, [double]$y) {
  $n = New-Call $TEXT_COMP 'K2_SetText' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $TEXT_COMP
  Add-Pin $n 'Value' 'in' 'text'
  (Get-Pin $n 'Value') | Add-Member -NotePropertyName ConstRef -NotePropertyValue $true
  Connect (Comp $name $TEXT_COMP ($x - 200) ($y + 200)) $name $n 'self'
  Connect $text 'ReturnValue' $n 'Value'
  return $n
}

Reset-Graph 100
$begin = Event 'ReceiveBeginPlay' 0 0
$shut = GateTick 'false' 300 0
Connect $begin 'then' $shut 'execute'

$tick = Event 'ReceiveTick' 0 600
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$open = New-Branch 250 600
Connect (Bool 'Opened' 100 800) 'Opened' $open 'Condition'
Connect $tick 'then' $open 'execute'
$g1 = Gone 'Shard1' 300 900
$g2 = Gone 'Shard2' 300 1050
$g3 = Gone 'Shard3' 300 1200
$sum12 = New-Operator 'Add' 'Add_IntInt' 'int' '' 'int' 800 950
Connect $g1 'ReturnValue' $sum12 'A'
Connect $g2 'ReturnValue' $sum12 'B'
$count = New-Operator 'Add' 'Add_IntInt' 'int' '' 'int' 1000 1050
Connect $sum12 'ReturnValue' $count 'A'
Connect $g3 'ReturnValue' $count 'B'
$asString = New-Call $STRINGS 'Conv_IntToString' $true 1200 1050
Add-Pin $asString 'InInt' 'in' 'int'
Add-Pin $asString 'ReturnValue' 'out' 'string'
Connect $count 'ReturnValue' $asString 'InInt'
$words = New-Call $STRINGS 'Concat_StrStr' $true 1400 1050
Add-Pin $words 'A' 'in' 'string'
Add-Pin $words 'B' 'in' 'string' '' $null ' / 3'
foreach ($pin in 'A', 'B') { (Get-Pin $words $pin) | Add-Member -NotePropertyName ConstRef -NotePropertyValue $true }
Add-Pin $words 'ReturnValue' 'out' 'string'
Connect $asString 'ReturnValue' $words 'A'
$asText = New-Call $TEXTLIB 'Conv_StringToText' $true 1600 1050
Add-Pin $asText 'InString' 'in' 'string'
(Get-Pin $asText 'InString') | Add-Member -NotePropertyName ConstRef -NotePropertyValue $true
Add-Pin $asText 'ReturnValue' 'out' 'text'
Connect $words 'ReturnValue' $asText 'InString'
$front = SetWords 'CounterFront' $asText 1900 600
$back = SetWords 'CounterBack' $asText 2200 600
$all = New-Branch 2500 600
$enough = New-Operator 'GreaterEqual' 'GreaterEqual_IntInt' 'int' '' 'bool' 2350 850
Connect $count 'ReturnValue' $enough 'A'
(Get-Pin $enough 'B').Default = '3'
Connect $enough 'ReturnValue' $all 'Condition'
Connect $open 'else' $front 'execute'
Chain @($front, $back, $all)
$opened = SetSelf 'Opened' 'bool' 'true' 2750 600
$run = GateTick 'true' 3000 600
$sealOff = Visible 'Seal' 'false' 3300 600
$frontOff = Visible 'CounterFront' 'false' 3600 600
$backOff = Visible 'CounterBack' 'false' 3900 600
$gi = GameInstance 4200 600
$swell = New-Call $STATICS 'PlaySound2D' $false 4500 600
Add-Pin $swell 'Sound' 'in' 'object' '' $SOUND_BASE
(Get-Pin $swell 'Sound') | Add-Member DefaultObject '/Game/ThirdPerson/Blueprints/Gimmicks/Heaven/S_GateLight.S_GateLight'
Add-Pin $swell 'VolumeMultiplier' 'in' 'real' 'float'
Add-Pin $swell 'PitchMultiplier' 'in' 'real' 'float' $null '1.0'
Add-Pin $swell 'StartTime' 'in' 'real' 'float' $null '0.0'
Connect (Op 'Multiply' 'Multiply_DoubleDouble' (GiGet $gi 'SE Volume' 'real' 'double' 4250 850) 'SE Volume' (GiGet $gi 'Master Volume' 'real' 'double' 4250 950) 'Master Volume' 4450 900) 'ReturnValue' $swell 'VolumeMultiplier'
Connect $all 'then' $opened 'execute'
Chain @($opened, $run, $sealOff, $frontOff, $backOff, $gi)
Connect $gi 'then' $swell 'execute'
Write-Graph 'BP_ShardLock_EventGraph.txt'
