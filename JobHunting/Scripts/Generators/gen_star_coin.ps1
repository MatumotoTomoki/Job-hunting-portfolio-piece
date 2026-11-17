param([string]$OutDir)
# Paste text for BP_StarCoin (components and variables from import_star_coin.py):
#   Tick, at rest: Pivot turns SpinSpeed degrees a second.
#   Tick, once Collected: over COLLECT seconds (t 0..1) the spin speeds up to SpinSpeed + EXTRA_SPIN, Pivot rises LIFT cm
#       and shrinks to nothing (1 - t^2); then the coin is destroyed.
#   Touched by the player (Grab): Collected, and the game instance's StarCoins goes up by one.
if (-not $OutDir) { throw 'OutDir is required' }
$cageGen = Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_hell_cage.ps1'
$defs = Get-Content -LiteralPath $cageGen -Encoding UTF8 | Select-Object -Skip 10 -First 172
. ([ScriptBlock]::Create(($defs -join "`n")))

$SCENE = "/Script/CoreUObject.Class'/Script/Engine.SceneComponent'"
$SPHERE = "/Script/CoreUObject.Class'/Script/Engine.SphereComponent'"
$COLLECT = '0.7'
$EXTRA_SPIN = '1800.0'   # (not $BOOST: PowerShell names ignore case, $boost is a node below)
$LIFT = '60.0'

function Event($name, $x, $y) {
  $n = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$ACTOR`",MemberName=`"$name`")", 'bOverrideFunction=True') $x $y
  Add-Pin $n 'then' 'out' 'exec'
  return $n
}
$STRINGS = "/Script/CoreUObject.Class'/Script/Engine.KismetStringLibrary'"
# A + B as text; a $null node takes the next argument as a literal instead.
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
# GetCurrentLevelName has exec pins: put it in the chain.
function LevelName([double]$x, [double]$y) {
  $n = New-Call $STATICS 'GetCurrentLevelName' $false $x $y
  Add-Pin $n 'bRemovePrefixString' 'in' 'bool' '' $null 'true'
  Add-Pin $n 'ReturnValue' 'out' 'string'
  return $n
}
function ToName($level, [double]$x, [double]$y) {
  $n = New-Call $STRINGS 'Conv_StringToName' $true $x $y
  Add-Pin $n 'InString' 'in' 'string'
  (Get-Pin $n 'InString') | Add-Member -NotePropertyName ConstRef -NotePropertyValue $true
  Add-Pin $n 'ReturnValue' 'out' 'name'
  Connect $level 'ReturnValue' $n 'InString'
  return $n
}
function Real($name, $x, $y) { New-VarGet $name $null 'real' 'double' $null $x $y }
function Pivot($x, $y) { New-VarGet 'Pivot' $null 'object' '' $SCENE $x $y }
function Times($a, $aPin, $b, $bPin, $x, $y) {
  $n = New-Operator 'Multiply' 'Multiply_DoubleDouble' 'real' 'double' 'real' $x $y
  (Get-Pin $n 'ReturnValue').Sub = 'double'
  Connect $a $aPin $n 'A'
  Connect $b $bPin $n 'B'
  return $n
}
# Pivot turned by `degrees` about Z this frame.
function Spin($degrees, $degreesPin, [double]$x, [double]$y) {
  # (Typed: a bare -300 argument arrives as text, and -300 + 250 would become -300250.)
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
Connect (New-VarGet 'Collected' $null 'bool' '' $null 150 200) 'Collected' $taken 'Condition'
Connect $tick 'then' $taken 'execute'
# At rest.
$restSpin = Spin (Times (Real 'SpinSpeed' 400 650) 'SpinSpeed' $tick 'DeltaSeconds' 600 650) 'ReturnValue' 900 450
Connect $taken 'else' $restSpin 'execute'
# Taken.
$count = New-VarSet 'CollectedFor' $null 'real' $null 650 -300
(Get-Pin $count 'CollectedFor').Sub = 'double'; (Get-Pin $count 'Output_Get').Sub = 'double'
$plus = New-Operator 'Add' 'Add_DoubleDouble' 'real' 'double' 'real' 500 -100
(Get-Pin $plus 'ReturnValue').Sub = 'double'
Connect (Real 'CollectedFor' 300 -100) 'CollectedFor' $plus 'A'
Connect $tick 'DeltaSeconds' $plus 'B'
Connect $plus 'ReturnValue' $count 'CollectedFor'
Connect $taken 'then' $count 'execute'
$t = New-Call $MATH 'MapRangeClamped' $true 900 -100
Add-Pin $t 'Value' 'in' 'real' 'double'
Add-Pin $t 'InRangeA' 'in' 'real' 'double' $null '0.0'
Add-Pin $t 'InRangeB' 'in' 'real' 'double' $null $COLLECT
Add-Pin $t 'OutRangeA' 'in' 'real' 'double' $null '0.0'
Add-Pin $t 'OutRangeB' 'in' 'real' 'double' $null '1.0'
Add-Pin $t 'ReturnValue' 'out' 'real' 'double'
Connect $count 'Output_Get' $t 'Value'
# Faster and faster: (SpinSpeed + EXTRA_SPIN * t) * DeltaSeconds.
$boost = New-Operator 'Multiply' 'Multiply_DoubleDouble' 'real' 'double' 'real' 1150 -150
(Get-Pin $boost 'ReturnValue').Sub = 'double'
Connect $t 'ReturnValue' $boost 'A'
(Get-Pin $boost 'B').Default = $EXTRA_SPIN
$rate = New-Operator 'Add' 'Add_DoubleDouble' 'real' 'double' 'real' 1350 -150
(Get-Pin $rate 'ReturnValue').Sub = 'double'
Connect (Real 'SpinSpeed' 1150 -50) 'SpinSpeed' $rate 'A'
Connect $boost 'ReturnValue' $rate 'B'
$fastSpin = Spin (Times $rate 'ReturnValue' $tick 'DeltaSeconds' 1550 -150) 'ReturnValue' 1950 -300
Connect $count 'then' $fastSpin 'execute'
# Shrinking: 1 - t^2, on all three axes.
$square = New-Operator 'Multiply' 'Multiply_DoubleDouble' 'real' 'double' 'real' 2100 0
(Get-Pin $square 'ReturnValue').Sub = 'double'
Connect $t 'ReturnValue' $square 'A'
Connect $t 'ReturnValue' $square 'B'
$left = New-Operator 'Subtract' 'Subtract_DoubleDouble' 'real' 'double' 'real' 2300 0
(Get-Pin $left 'ReturnValue').Sub = 'double'
(Get-Pin $left 'A').Default = '1.0'
Connect $square 'ReturnValue' $left 'B'
$asVector = New-Call $MATH 'Conv_DoubleToVector' $true 2500 0
Add-Pin $asVector 'InDouble' 'in' 'real' 'double'
Add-Pin $asVector 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $left 'ReturnValue' $asVector 'InDouble'
$shrink = New-Call $SCENE 'SetRelativeScale3D' $false 2750 -300
Add-Pin $shrink 'self' 'in' 'object' '' $SCENE
Add-Pin $shrink 'NewScale3D' 'in' 'struct' '' $VECTOR
Connect (Pivot 2550 -150) 'Pivot' $shrink 'self'
Connect $asVector 'ReturnValue' $shrink 'NewScale3D'
# Rising: LIFT * t up.
$up = New-Operator 'Multiply' 'Multiply_DoubleDouble' 'real' 'double' 'real' 2900 100
(Get-Pin $up 'ReturnValue').Sub = 'double'
Connect $t 'ReturnValue' $up 'A'
(Get-Pin $up 'B').Default = $LIFT
$where = New-Call $MATH 'MakeVector' $true 3100 100
Add-Pin $where 'X' 'in' 'real' 'double' $null '0.0'
Add-Pin $where 'Y' 'in' 'real' 'double' $null '0.0'
Add-Pin $where 'Z' 'in' 'real' 'double'
Add-Pin $where 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect $up 'ReturnValue' $where 'Z'
$rise = New-Call $SCENE 'K2_SetRelativeLocation' $false 3100 -300
Add-Pin $rise 'self' 'in' 'object' '' $SCENE
Add-Pin $rise 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $rise 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $rise 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $rise 'bTeleport' 'in' 'bool' '' $null 'false'
Connect (Pivot 2900 -150) 'Pivot' $rise 'self'
Connect $where 'ReturnValue' $rise 'NewLocation'
# Gone.
$over = New-Branch 3450 -300
$done = New-Operator 'GreaterEqual' 'GreaterEqual_DoubleDouble' 'real' 'double' 'bool' 3300 -100
Connect $t 'ReturnValue' $done 'A'
(Get-Pin $done 'B').Default = '1.0'
Connect $done 'ReturnValue' $over 'Condition'
$destroy = New-Call $ACTOR 'K2_DestroyActor' $false 3700 -300
Add-Pin $destroy 'self' 'in' 'object' '' $ACTOR
Chain @($fastSpin, $shrink, $rise, $over)
Connect $over 'then' $destroy 'execute'

# Touched.
$touch = Event 'ReceiveActorBeginOverlap' 0 1000
Add-Pin $touch 'OtherActor' 'out' 'object' '' $ACTOR
$once = New-Branch 300 1000
Connect (New-VarGet 'Collected' $null 'bool' '' $null 150 1200) 'Collected' $once 'Condition'
$isPlayer = New-Branch 550 1000
$overlap = New-Call $PRIMITIVE 'IsOverlappingActor' $true 450 1250
Add-Pin $overlap 'self' 'in' 'object' '' $PRIMITIVE
Add-Pin $overlap 'Other' 'in' 'object' '' $ACTOR
Add-Pin $overlap 'ReturnValue' 'out' 'bool'
Connect (New-VarGet 'Grab' $null 'object' '' $SPHERE 250 1250) 'Grab' $overlap 'self'
Connect (Player 200 1350) 'ReturnValue' $overlap 'Other'
Connect $overlap 'ReturnValue' $isPlayer 'Condition'
$got = New-VarSet 'Collected' $null 'bool' $null 800 1000
(Get-Pin $got 'Collected').Default = 'true'
$cast = GameInstance 1300 1000
$more = GiSet $cast 'StarCoins' 'int' '' 1600 1000
$add = New-Operator 'Add' 'Add_IntInt' 'int' '' 'int' 1450 1250
Connect (GiGet $cast 'StarCoins' 'int' '' 1250 1250) 'StarCoins' $add 'A'
(Get-Pin $add 'B').Default = '1'
Connect $add 'ReturnValue' $more 'StarCoins'
Connect $touch 'then' $once 'execute'
Connect $once 'else' $isPlayer 'execute'
Connect $isPlayer 'then' $got 'execute'
Connect $got 'then' $cast 'execute'
Connect $cast 'then' $more 'execute'
# Remembered for the run: its id on the list, and one more taken in this level.
$remember = GiSet $cast 'TakenCoinIds' 'string' '' 1900 1000
Connect (Concat (GiGet $cast 'TakenCoinIds' 'string' '' 1650 1250) 'TakenCoinIds' (New-VarGet 'CoinId' $null 'string' '' $null 1650 1350) 'CoinId' 1850 1250) 'ReturnValue' $remember 'TakenCoinIds'
$level = LevelName 2200 1000
$asName = ToName $level 2400 1250
$same = New-Branch 2500 1000
$isSame = New-Operator 'EqualEqual' 'EqualEqual_NameName' 'name' '' 'bool' 2600 1250
Connect (GiGet $cast 'TakenLevel' 'name' '' 2400 1400) 'TakenLevel' $isSame 'A'
Connect $asName 'ReturnValue' $isSame 'B'
Connect $isSame 'ReturnValue' $same 'Condition'
$newLevel = GiSet $cast 'TakenLevel' 'name' '' 2800 1200
Connect $asName 'ReturnValue' $newLevel 'TakenLevel'
$zero = GiSet $cast 'TakenInArea' 'int' '' 3100 1200 '0'
$inArea = GiSet $cast 'TakenInArea' 'int' '' 3400 1000
$plusOne = New-Operator 'Add' 'Add_IntInt' 'int' '' 'int' 3250 1400
Connect (GiGet $cast 'TakenInArea' 'int' '' 3050 1450) 'TakenInArea' $plusOne 'A'
(Get-Pin $plusOne 'B').Default = '1'
Connect $plusOne 'ReturnValue' $inArea 'TakenInArea'
Chain @($more, $remember, $level, $same)
Connect $same 'then' $inArea 'execute'
Connect $same 'else' $newLevel 'execute'
Chain @($newLevel, $zero, $inArea)

# Begin Play: CoinId = "|<level>.<this coin's name>|"; gone already if it is on the run's list.
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
$left = Concat $null '|' $named 'ReturnValue' 1000 2050
$id = Concat $left 'ReturnValue' $null '|' 1200 2050
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
Write-Graph 'BP_StarCoin_EventGraph.txt'
