param([string]$OutDir)
# Paste text for WBP_StarCoins (variables Pop, LastShown from import_star_coin.py; CoinText, a TextBlock made by hand
# in the designer with Is Variable on). Every frame:
#   in the area being played (GI AreaLevel is this level): shown, else collapsed;
#   taken = TakenInArea when TakenLevel is this level, else 0;
#   a new count pops the counter up (Pop = 1), Pop eases back to 0 (POP_FADE a second), render scale 1 + POP_SIZE * Pop;
#   CoinText = "taken / AreaCoinTotal".
if (-not $OutDir) { throw 'OutDir is required' }
$cageGen = Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_hell_cage.ps1'
$defs = Get-Content -LiteralPath $cageGen -Encoding UTF8 | Select-Object -Skip 10 -First 172
. ([ScriptBlock]::Create(($defs -join "`n")))

$USER_WIDGET = "/Script/CoreUObject.Class'/Script/UMG.UserWidget'"
$TEXT_BLOCK = "/Script/CoreUObject.Class'/Script/UMG.TextBlock'"
$TEXTS = "/Script/CoreUObject.Class'/Script/Engine.KismetTextLibrary'"
$GEOMETRY = "/Script/CoreUObject.ScriptStruct'/Script/SlateCore.Geometry'"
$VISIBILITY = "/Script/CoreUObject.Enum'/Script/UMG.ESlateVisibility'"
$VECTOR2D = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Vector2D'"
$POP_FADE = '3.0'
$POP_SIZE = '0.5'

function LevelName([double]$x, [double]$y) {
  $n = New-Call $STATICS 'GetCurrentLevelName' $false $x $y
  Add-Pin $n 'bRemovePrefixString' 'in' 'bool' '' $null 'true'
  Add-Pin $n 'ReturnValue' 'out' 'string'
  return $n
}
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
function IntText($source, $sourcePin, [double]$x, [double]$y) {
  $n = New-Call $STRINGS 'Conv_IntToString' $true $x $y
  Add-Pin $n 'InInt' 'in' 'int'
  Add-Pin $n 'ReturnValue' 'out' 'string'
  Connect $source $sourcePin $n 'InInt'
  return $n
}
function Visibility($value, [double]$x, [double]$y) {
  $n = New-Call $null 'SetVisibility' $false $x $y
  Add-Pin $n 'InVisibility' 'in' 'byte' '' $VISIBILITY $value
  return $n
}

Reset-Graph 100
$tick = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$USER_WIDGET`",MemberName=`"Tick`")", 'bOverrideFunction=True') 0 0
Add-Pin $tick 'then' 'out' 'exec'
Add-Pin $tick 'MyGeometry' 'out' 'struct' '' $GEOMETRY
Add-Pin $tick 'InDeltaTime' 'out' 'real' 'float'
$level = LevelName 250 0
$cast = GameInstance 650 0
$levelName = New-Call $STRINGS 'Conv_StringToName' $true 500 300
Add-Pin $levelName 'InString' 'in' 'string'
(Get-Pin $levelName 'InString') | Add-Member -NotePropertyName ConstRef -NotePropertyValue $true
Add-Pin $levelName 'ReturnValue' 'out' 'name'
Connect $level 'ReturnValue' $levelName 'InString'
Connect $tick 'then' $level 'execute'
Chain @($level, $cast)
# In an area?
$inArea = New-Branch 1000 0
$isArea = New-Operator 'EqualEqual' 'EqualEqual_NameName' 'name' '' 'bool' 850 250
Connect (GiGet $cast 'AreaLevel' 'name' '' 650 450) 'AreaLevel' $isArea 'A'
Connect $levelName 'ReturnValue' $isArea 'B'
Connect $isArea 'ReturnValue' $inArea 'Condition'
Connect $cast 'then' $inArea 'execute'
$hide = Visibility 'Collapsed' 1300 300
Connect $inArea 'else' $hide 'execute'
$show = Visibility 'HitTestInvisible' 1300 0
Connect $inArea 'then' $show 'execute'
# Taken here.
$takenHere = New-Operator 'EqualEqual' 'EqualEqual_NameName' 'name' '' 'bool' 1350 650
Connect (GiGet $cast 'TakenLevel' 'name' '' 1150 650) 'TakenLevel' $takenHere 'A'
Connect $levelName 'ReturnValue' $takenHere 'B'
$taken = New-Call $MATH 'SelectInt' $true 1550 550
Add-Pin $taken 'A' 'in' 'int'
Add-Pin $taken 'B' 'in' 'int' '' $null '0'
Add-Pin $taken 'bPickA' 'in' 'bool'
Add-Pin $taken 'ReturnValue' 'out' 'int'
Connect (GiGet $cast 'TakenInArea' 'int' '' 1350 500) 'TakenInArea' $taken 'A'
Connect $takenHere 'ReturnValue' $taken 'bPickA'
# A new count: pop.
$changed = New-Branch 1600 0
$differs = New-Operator 'NotEqual' 'NotEqual_IntInt' 'int' '' 'bool' 1750 250
Connect $taken 'ReturnValue' $differs 'A'
Connect (New-VarGet 'LastShown' $null 'int' '' $null 1550 350) 'LastShown' $differs 'B'
Connect $differs 'ReturnValue' $changed 'Condition'
$shown = New-VarSet 'LastShown' $null 'int' $null 1900 -250
Connect $taken 'ReturnValue' $shown 'LastShown'
$popped = New-VarSet 'Pop' $null 'real' $null 2150 -250
(Get-Pin $popped 'Pop').Sub = 'double'; (Get-Pin $popped 'Output_Get').Sub = 'double'
(Get-Pin $popped 'Pop').Default = '1.0'
Connect $show 'then' $changed 'execute'
Connect $changed 'then' $shown 'execute'
Connect $shown 'then' $popped 'execute'
# Pop eases back: max(Pop - InDeltaTime * POP_FADE, 0).
$fade = New-Operator 'Multiply' 'Multiply_DoubleDouble' 'real' 'double' 'real' 2150 350
(Get-Pin $fade 'ReturnValue').Sub = 'double'
Connect $tick 'InDeltaTime' $fade 'A'
(Get-Pin $fade 'B').Default = $POP_FADE
$less = New-Operator 'Subtract' 'Subtract_DoubleDouble' 'real' 'double' 'real' 2350 300
(Get-Pin $less 'ReturnValue').Sub = 'double'
Connect (New-VarGet 'Pop' $null 'real' 'double' $null 2150 250) 'Pop' $less 'A'
Connect $fade 'ReturnValue' $less 'B'
$floor = New-Call $MATH 'FMax' $true 2550 300
Add-Pin $floor 'A' 'in' 'real' 'double'
Add-Pin $floor 'B' 'in' 'real' 'double' $null '0.0'
Add-Pin $floor 'ReturnValue' 'out' 'real' 'double'
Connect $less 'ReturnValue' $floor 'A'
$decay = New-VarSet 'Pop' $null 'real' $null 2550 0
(Get-Pin $decay 'Pop').Sub = 'double'; (Get-Pin $decay 'Output_Get').Sub = 'double'
Connect $floor 'ReturnValue' $decay 'Pop'
Connect $changed 'else' $decay 'execute'
Connect $popped 'then' $decay 'execute'
# Scale 1 + POP_SIZE * Pop.
$grow = New-Operator 'Multiply' 'Multiply_DoubleDouble' 'real' 'double' 'real' 2800 300
(Get-Pin $grow 'ReturnValue').Sub = 'double'
Connect $decay 'Output_Get' $grow 'A'
(Get-Pin $grow 'B').Default = $POP_SIZE
$size = New-Operator 'Add' 'Add_DoubleDouble' 'real' 'double' 'real' 3000 300
(Get-Pin $size 'ReturnValue').Sub = 'double'
(Get-Pin $size 'A').Default = '1.0'
Connect $grow 'ReturnValue' $size 'B'
$both = New-Call $MATH 'MakeVector2D' $true 3200 300
Add-Pin $both 'X' 'in' 'real' 'double'
Add-Pin $both 'Y' 'in' 'real' 'double'
Add-Pin $both 'ReturnValue' 'out' 'struct' '' $VECTOR2D
Connect $size 'ReturnValue' $both 'X'
Connect $size 'ReturnValue' $both 'Y'
$scale = New-Call $null 'SetRenderScale' $false 2850 0
Add-Pin $scale 'Scale' 'in' 'struct' '' $VECTOR2D
Connect $both 'ReturnValue' $scale 'Scale'
Connect $decay 'then' $scale 'execute'
# "taken / total".
$label = Concat (IntText $taken 'ReturnValue' 3000 600) 'ReturnValue' (Concat $null ' / ' (IntText (GiGet $cast 'AreaCoinTotal' 'int' '' 2800 800) 'AreaCoinTotal' 3000 800) 'ReturnValue' 3200 750) 'ReturnValue' 3400 650
$asText = New-Call $TEXTS 'Conv_StringToText' $true 3600 650
Add-Pin $asText 'InString' 'in' 'string'
(Get-Pin $asText 'InString') | Add-Member -NotePropertyName ConstRef -NotePropertyValue $true
Add-Pin $asText 'ReturnValue' 'out' 'text'
Connect $label 'ReturnValue' $asText 'InString'
$write = New-Call $TEXT_BLOCK 'SetText' $false 3300 0
Add-Pin $write 'self' 'in' 'object' '' $TEXT_BLOCK
Add-Pin $write 'InText' 'in' 'text'
Connect (New-VarGet 'CoinText' $null 'object' '' $TEXT_BLOCK 3100 200) 'CoinText' $write 'self'
Connect $asText 'ReturnValue' $write 'InText'
Connect $scale 'then' $write 'execute'
Write-Graph 'WBP_StarCoins_EventGraph.txt'
