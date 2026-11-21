param([string]$OutDir)
# Paste text for hooking an achievement into an existing blueprint: Scripts/AchievementHooks/Unlock_<ID>.txt, one per
# achievement in setup_achievements.py. Each holds three nodes: Get Game Instance -> Cast To BP_MyGameInstance ->
# Unlock Achievement (ID filled in). Paste it next to the moment the achievement is earned and wire it in by hand:
# <that node>.then -> Cast, Unlock Achievement.then -> whatever <that node> led to before (if anything).
# Run: powershell -File Generators/gen_achievement_hooks.ps1 -OutDir <Scripts folder>
if (-not $OutDir) { throw 'OutDir is required' }
$cageGen = Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_hell_cage.ps1'
$defs = Get-Content -LiteralPath $cageGen -Encoding UTF8 | Select-Object -Skip 10 -First 172
. ([ScriptBlock]::Create(($defs -join "`n")))

$setup = Get-Content -LiteralPath (Join-Path (Split-Path -Parent $GenDir) 'setup_achievements.py') -Encoding UTF8
$ids = $setup | ForEach-Object { if ($_ -match '^\s*\("(ACH_\w+)"') { $Matches[1] } }
$folder = Join-Path (Resolve-Path -LiteralPath $OutDir).Path 'AchievementHooks'
New-Item -ItemType Directory -Force $folder | Out-Null

function Unlock($cast, $id, $x) {
  $unlock = New-Call $GI_CLASS 'UnlockAchievement' $false $x 0
  Add-Pin $unlock 'self' 'in' 'object' '' $GI_CLASS
  Add-Pin $unlock 'ID' 'in' 'name' '' $null $id
  Connect $cast $GI_OUT $unlock 'self'
  return $unlock
}
# Written without Write-Graph's checks: the Cast's exec input is left for the user to wire.
function Save-Hook($file) {
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
  [IO.File]::WriteAllText((Join-Path $folder $file), $sb.ToString(), [Text.UTF8Encoding]::new($false))
}

foreach ($id in $ids) {
  Reset-Graph 900
  $cast = GameInstance 250 0
  Connect $cast 'then' (Unlock $cast $id 600) 'execute'
  Save-Hook "Unlock_$id.txt"
}

# The character's fall check (after Stop Movement Immediately, before the ActiveFlag branch): ACH_FIRST_FALL and the
# run's RunFell (for ACH_NO_FALL at the clear).
Reset-Graph 900
$cast = GameInstance 250 0
$unlock = Unlock $cast 'ACH_FIRST_FALL' 600
$fell = GiSet $cast 'RunFell' 'bool' '' 950 0 'true'
Connect $cast 'then' $unlock 'execute'
Connect $unlock 'then' $fell 'execute'
Save-Hook 'Fall_FirstFall.txt'
# The same check's flag side (the ActiveFlag branch's True, before the move to the flag): RunUsedFlag (for ACH_NO_FLAG
# and ACH_PURIST at the clear).
Reset-Graph 900
$cast = GameInstance 250 0
Connect $cast 'then' (GiSet $cast 'RunUsedFlag' 'bool' '' 600 0 'true') 'execute'
Save-Hook 'Fall_UsedFlag.txt'

# ----- BP_StarCoin, at the end of the pickup chain (after the last Set TakenInArea; step 4b) -----
# Every coin of this area taken this run (TakenInArea >= AreaCoinTotal, counted in the area BP_AreaStart set up, an
# LV_AreaN level): ACH_COIN_A<N>, N being the level name's 8th character. Then, with all four on UnlockedAchievements:
# ACH_COIN_ALL.
# As gen_achievements' Format-Pin: const-ref pins (the string library's inputs).
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
function ConstRef($node, [string[]]$names) { foreach ($name in $names) { (Get-Pin $node $name) | Add-Member -NotePropertyName ConstRef -NotePropertyValue $true -Force } }
function Pure($lib, $func, $x, $y, $inputs, $outCat) {
  $n = New-Call $lib $func $true $x $y
  foreach ($in in $inputs) { Add-Pin $n $in[0] 'in' $in[1] '' $in[2] $in[3] }
  Add-Pin $n 'ReturnValue' 'out' $outCat
  return $n
}
function BoolAnd($a, $aPin, $b, $bPin, $x, $y) {
  $n = Pure $MATH 'BooleanAND' $x $y @(@('A', 'bool'), @('B', 'bool')) 'bool'
  Connect $a $aPin $n 'A'
  Connect $b $bPin $n 'B'
  return $n
}
function HasTaken($cast, $id, $x, $y) {
  $list = New-VarGet 'UnlockedAchievements' $GI_CLASS 'name' '' $null ($x - 250) $y 'Array'
  Connect $cast $GI_OUT $list 'self'
  $n = New-Call $ARRAYLIB 'Array_Contains' $true $x $y '/Script/BlueprintGraph.K2Node_CallArrayFunction'
  Add-Pin $n 'TargetArray' 'in' 'name' '' $null $null 'Array'
  Add-Pin $n 'ItemToFind' 'in' 'name' '' $null $id
  Add-Pin $n 'ReturnValue' 'out' 'bool'
  Connect $list 'UnlockedAchievements' $n 'TargetArray'
  return $n
}
Reset-Graph 900
$cast = GameInstance 250 0
$area = GiGet $cast 'AreaLevel' 'name' '' 100 450
$areaText = Pure $STRINGS 'Conv_NameToString' 300 450 @(,@('InName', 'name')) 'string'
Connect $area 'AreaLevel' $areaText 'InName'
$enough = New-Operator 'GreaterEqual' 'GreaterEqual_IntInt' 'int' '' 'bool' 550 250
Connect (GiGet $cast 'TakenInArea' 'int' '' 350 250) 'TakenInArea' $enough 'A'
Connect (GiGet $cast 'AreaCoinTotal' 'int' '' 350 350) 'AreaCoinTotal' $enough 'B'
$here = New-Operator 'EqualEqual' 'EqualEqual_NameName' 'name' '' 'bool' 550 550
Connect (GiGet $cast 'TakenLevel' 'name' '' 350 600) 'TakenLevel' $here 'A'
Connect $area 'AreaLevel' $here 'B'
$isArea = Pure $STRINGS 'StartsWith' 550 700 @(@('SourceString', 'string'), @('InPrefix', 'string', $null, 'LV_Area'), @('SearchCase', 'byte', "/Script/CoreUObject.Enum'/Script/CoreUObject.ESearchCase'", 'IgnoreCase')) 'bool'
ConstRef $isArea @('SourceString', 'InPrefix')
Connect $areaText 'ReturnValue' $isArea 'SourceString'
$all = New-Branch 1000 0
Connect (BoolAnd (BoolAnd $enough 'ReturnValue' $here 'ReturnValue' 800 350) 'ReturnValue' $isArea 'ReturnValue' 1000 450) 'ReturnValue' $all 'Condition'
Connect $cast 'then' $all 'execute'
$digit = Pure $STRINGS 'GetSubstring' 800 850 @(@('SourceString', 'string'), @('StartIndex', 'int', $null, '7'), @('Length', 'int', $null, '1')) 'string'
ConstRef $digit @('SourceString')
Connect $areaText 'ReturnValue' $digit 'SourceString'
$idText = Pure $STRINGS 'Concat_StrStr' 1050 850 @(@('A', 'string', $null, 'ACH_COIN_A'), @('B', 'string')) 'string'
ConstRef $idText @('A', 'B')
Connect $digit 'ReturnValue' $idText 'B'
$idName = Pure $STRINGS 'Conv_StringToName' 1300 850 @(,@('InString', 'string')) 'name'
ConstRef $idName @('InString')
Connect $idText 'ReturnValue' $idName 'InString'
$areaUnlock = New-Call $GI_CLASS 'UnlockAchievement' $false 1300 0
Add-Pin $areaUnlock 'self' 'in' 'object' '' $GI_CLASS
Add-Pin $areaUnlock 'ID' 'in' 'name'
Connect $cast $GI_OUT $areaUnlock 'self'
Connect $idName 'ReturnValue' $areaUnlock 'ID'
Connect $all 'then' $areaUnlock 'execute'
$four = BoolAnd (BoolAnd (HasTaken $cast 'ACH_COIN_A1' 1500 300) 'ReturnValue' (HasTaken $cast 'ACH_COIN_A2' 1500 400) 'ReturnValue' 1750 350) 'ReturnValue' (BoolAnd (HasTaken $cast 'ACH_COIN_A3' 1500 500) 'ReturnValue' (HasTaken $cast 'ACH_COIN_A4' 1500 600) 'ReturnValue' 1750 550) 'ReturnValue' 1950 450
$everyArea = New-Branch 1700 0
Connect $four 'ReturnValue' $everyArea 'Condition'
Connect $areaUnlock 'then' $everyArea 'execute'
Connect $everyArea 'then' (Unlock $cast 'ACH_COIN_ALL' 2000) 'execute'
Save-Hook 'StarCoin_AreaCoins.txt'

# ----- items and flags (step 4b-2): "<level>.<this actor>" goes on a GI list once; the list full -> the achievement -----
#   Item_Taken.txt   in each item BP (BP_Item, BP_Item2, BP_2jump), just before its Destroy Actor: also RunTookItem
#   Flag_Raised.txt  in BP_CheckpointFlag, after Set Raised (the first touch)
# Wire BOTH the Branch's False and Unlock Achievement's then on to the node that came next: paste text cannot link out,
# and with False left open the rest of the flag/item graph stops until the list is full (the flag stopped rising, 11-21).
function Collected($list, $total, $id, $tookItem) {
  Reset-Graph 900
  $cast = GameInstance 250 0
  $first = $cast
  if ($tookItem) {
    $took = GiSet $cast 'RunTookItem' 'bool' '' 550 0 'true'
    Connect $cast 'then' $took 'execute'
    $first = $took
  }
  # GetCurrentLevelName has exec pins (a pure copy is pruned): it goes in the chain.
  $level = New-Call $STATICS 'GetCurrentLevelName' $false 850 0
  Add-Pin $level 'bRemovePrefixString' 'in' 'bool' '' $null 'true'
  Add-Pin $level 'ReturnValue' 'out' 'string'
  Connect $first 'then' $level 'execute'
  $first = $level
  $self = New-Node '/Script/BlueprintGraph.K2Node_Self' @() 600 550
  Add-Pin $self 'self' 'out' 'object' '' $ACTOR
  $objectName = Pure $SYSTEM 'GetObjectName' 800 550 @(,@('Object', 'object', $OBJECT)) 'string'
  Connect $self 'self' $objectName 'Object'
  $dot = Pure $STRINGS 'Concat_StrStr' 850 350 @(@('A', 'string'), @('B', 'string', $null, '.')) 'string'
  ConstRef $dot @('A', 'B')
  Connect $level 'ReturnValue' $dot 'A'
  $whole = Pure $STRINGS 'Concat_StrStr' 1050 450 @(@('A', 'string'), @('B', 'string')) 'string'
  ConstRef $whole @('A', 'B')
  Connect $dot 'ReturnValue' $whole 'A'
  Connect $objectName 'ReturnValue' $whole 'B'
  $asName = Pure $STRINGS 'Conv_StringToName' 1250 450 @(,@('InString', 'string')) 'name'
  ConstRef $asName @('InString')
  Connect $whole 'ReturnValue' $asName 'InString'
  $add = New-Call $ARRAYLIB 'Array_AddUnique' $false 1450 0 '/Script/BlueprintGraph.K2Node_CallArrayFunction'
  Add-Pin $add 'TargetArray' 'in' 'name' '' $null $null 'Array'
  Add-Pin $add 'NewItem' 'in' 'name'
  Add-Pin $add 'ReturnValue' 'out' 'int'
  $listGet = New-VarGet $list $GI_CLASS 'name' '' $null 1200 250 'Array'
  Connect $cast $GI_OUT $listGet 'self'
  Connect $listGet $list $add 'TargetArray'
  Connect $asName 'ReturnValue' $add 'NewItem'
  Connect $first 'then' $add 'execute'
  $listGet2 = New-VarGet $list $GI_CLASS 'name' '' $null 1500 350 'Array'
  Connect $cast $GI_OUT $listGet2 'self'
  $length = New-Call $ARRAYLIB 'Array_Length' $true 1700 350 '/Script/BlueprintGraph.K2Node_CallArrayFunction'
  Add-Pin $length 'TargetArray' 'in' 'name' '' $null $null 'Array'
  Add-Pin $length 'ReturnValue' 'out' 'int'
  Connect $listGet2 $list $length 'TargetArray'
  $full = New-Operator 'GreaterEqual' 'GreaterEqual_IntInt' 'int' '' 'bool' 1900 350
  Connect $length 'ReturnValue' $full 'A'
  Connect (GiGet $cast $total 'int' '' 1700 500) $total $full 'B'
  $done = New-Branch 1850 0
  Connect $full 'ReturnValue' $done 'Condition'
  Connect $add 'then' $done 'execute'
  Connect $done 'then' (Unlock $cast $id 2150) 'execute'
}
Collected 'TakenItems' 'ItemTotal' 'ACH_ITEM_ALL' $true
Save-Hook 'Item_Taken.txt'
Collected 'RaisedFlags' 'FlagTotal' 'ACH_FLAGS' $false
Save-Hook 'Flag_Raised.txt'
"$($ids.Count) hooks + 2 fall hooks + StarCoin_AreaCoins + Item_Taken + Flag_Raised in $folder"
