param([string]$OutDir)
# Paste text for the achievements' foundation in BP_MyGameInstance (variables, the save and the empty function graphs
# from setup_achievements.py; the plan is Scripts/Achievements_Plan.md):
#   GI_LoadAchievements.txt   the body of the function LoadAchievements: once per game, if the "Achievements" slot
#                             exists, UnlockedAchievements and FreeAchievementCount come from BP_AchievementSave; then
#                             AchievementsLoaded.
#   GI_UnlockAchievement.txt  the body of the function UnlockAchievement (input ID, Name, added by hand): LastAchievement
#                             = ID; LoadAchievements; if ID is a known achievement not yet taken, it goes on
#                             UnlockedAchievements (and FreeAchievementCount + 1 if it is a free one), the slot is
#                             saved, and for now a Print String shows its name (the corner notice is step 2). An
#                             unknown ID prints a warning.
# Each body's first node is left for the user to wire from the function's entry (paste text cannot link to it).
if (-not $OutDir) { throw 'OutDir is required' }
$cageGen = Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_hell_cage.ps1'
$defs = Get-Content -LiteralPath $cageGen -Encoding UTF8 | Select-Object -Skip 10 -First 172
. ([ScriptBlock]::Create(($defs -join "`n")))

# As gen_heaven_light's: const-ref pins and a class pin's chosen class (DefaultObject).
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

$SAVEGAME = "/Script/CoreUObject.Class'/Script/Engine.SaveGame'"
$SAVE_CLASS = "/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPerson/Blueprints/Achievements/BP_AchievementSave.BP_AchievementSave_C'"
$SAVE_PATH = '/Game/ThirdPerson/Blueprints/Achievements/BP_AchievementSave.BP_AchievementSave_C'
$SAVE_OUT = 'AsBP Achievement Save'
$TEXTLIB = "/Script/CoreUObject.Class'/Script/Engine.KismetTextLibrary'"
$SLOT = 'Achievements'

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
function ConstRef($node, [string[]]$names) { foreach ($name in $names) { (Get-Pin $node $name) | Add-Member -NotePropertyName ConstRef -NotePropertyValue $true -Force } }
function SelfGet($name, $cat, [double]$x, [double]$y, $container = 'None') { New-VarGet $name $null $cat '' $null $x $y $container }
function SelfSet($name, $cat, [double]$x, [double]$y, $container = 'None', $value = $null) {
  $n = New-VarSet $name $null $cat $null $x $y
  foreach ($pin in $name, 'Output_Get') { (Get-Pin $n $pin).Container = $container }
  if ($null -ne $value) { (Get-Pin $n $name).Default = $value }
  return $n
}
function ArrayCall($func, [bool]$pure, [double]$x, [double]$y) { New-Call $ARRAYLIB $func $pure $x $y '/Script/BlueprintGraph.K2Node_CallArrayFunction' }
# Array_Contains(array, item) with both wired.
function Contains($array, $arrayPin, $item, $itemPin, [double]$x, [double]$y) {
  $n = ArrayCall 'Array_Contains' $true $x $y
  Add-Pin $n 'TargetArray' 'in' 'name' '' $null $null 'Array'
  Add-Pin $n 'ItemToFind' 'in' 'name'
  Add-Pin $n 'ReturnValue' 'out' 'bool'
  Connect $array $arrayPin $n 'TargetArray'
  Connect $item $itemPin $n 'ItemToFind'
  return $n
}
function Slot($func, [bool]$pure, [double]$x, [double]$y) {
  $n = New-Call $STATICS $func $pure $x $y
  Add-Pin $n 'SlotName' 'in' 'string' '' $null $SLOT
  Add-Pin $n 'UserIndex' 'in' 'int' '' $null '0'
  ConstRef $n 'SlotName'
  return $n
}
function SaveCast([double]$x, [double]$y) {
  $n = New-Node '/Script/BlueprintGraph.K2Node_DynamicCast' @("TargetType=`"$SAVE_CLASS`"") $x $y
  Add-Exec $n
  Add-Pin $n 'CastFailed' 'out' 'exec'
  Add-Pin $n 'Object' 'in' 'object' '' $OBJECT
  Add-Pin $n $SAVE_OUT 'out' 'object' '' $SAVE_CLASS
  Add-Pin $n 'bSuccess' 'out' 'bool'
  return $n
}
function Print($stringNode, $stringPin, [double]$x, [double]$y) {
  $n = New-Call $SYSTEM 'PrintString' $false $x $y
  Add-Pin $n 'InString' 'in' 'string'
  Add-Pin $n 'bPrintToScreen' 'in' 'bool' '' $null 'true'
  Add-Pin $n 'bPrintToLog' 'in' 'bool' '' $null 'true'
  Add-Pin $n 'Duration' 'in' 'real' 'float' $null '5.000000'
  ConstRef $n 'InString'
  Connect $stringNode $stringPin $n 'InString'
  return $n
}
# Write-Graph, except that the body's first node is meant to be fed by the function entry (wired by hand).
function Write-Body($file, $first) {
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
  if ($text.Contains('@{')) { throw "$file : a node object leaked into a pin" }
  $names = [regex]::Matches($text, '(?m)^Begin Object Class=\S+ Name="(\w+)"') | ForEach-Object { $_.Groups[1].Value }
  if (($names | Sort-Object -Unique).Count -ne $names.Count) { throw "$file : duplicate node names" }
  foreach ($m in [regex]::Matches($text, 'LinkedTo=\(([^)]*)\)')) {
    foreach ($link in ($m.Groups[1].Value -split ',' | Where-Object { $_ })) {
      if ($names -notcontains ($link -split ' ')[0]) { throw "$file : dangling link $link" }
    }
  }
  foreach ($n in $script:nodes) {
    foreach ($p in $n.Pins) {
      if ($p.Cat -eq 'exec' -and $p.Dir -eq 'out' -and $p.Links.Count -gt 1) { throw "$file : exec output with several links: $($n.Name).$($p.Name)" }
      if ($p.Cat -eq 'exec' -and $p.Dir -eq 'in' -and $p.Links.Count -eq 0 -and $n -ne $first) { throw "$file : unreached node $($n.Name)" }
    }
  }
  $path = Join-Path (Resolve-Path -LiteralPath $OutDir).Path $file
  [IO.File]::WriteAllText($path, $text, [Text.UTF8Encoding]::new($false))
  "$path : $($names.Count) nodes"
}

# ===== LoadAchievements ======================================================================================
Reset-Graph 100
$loadedYet = New-Branch 300 0
Connect (SelfGet 'AchievementsLoaded' 'bool' 100 150) 'AchievementsLoaded' $loadedYet 'Condition'
$exists = Slot 'DoesSaveGameExist' $false 600 100
Add-Pin $exists 'ReturnValue' 'out' 'bool'
$hasSave = New-Branch 950 100
$load = Slot 'LoadGameFromSlot' $false 1250 100
Add-Pin $load 'ReturnValue' 'out' 'object' '' $SAVEGAME
$cast = SaveCast 1600 100
$setUnlocked = SelfSet 'UnlockedAchievements' 'name' 1950 100 'Array'
$saved = New-VarGet 'Unlocked' $SAVE_CLASS 'name' '' $null 1700 350 'Array'
$setCount = SelfSet 'FreeAchievementCount' 'int' 2300 100
$savedCount = New-VarGet 'FreeCount' $SAVE_CLASS 'int' '' $null 2050 400
$setLoaded = SelfSet 'AchievementsLoaded' 'bool' 2650 100 'None' 'true'
Connect $loadedYet 'else' $exists 'execute'
Connect $exists 'then' $hasSave 'execute'
Connect $exists 'ReturnValue' $hasSave 'Condition'
Connect $hasSave 'then' $load 'execute'
Connect $hasSave 'else' $setLoaded 'execute'
Connect $load 'then' $cast 'execute'
Connect $load 'ReturnValue' $cast 'Object'
Connect $cast 'then' $setUnlocked 'execute'
Connect $cast 'CastFailed' $setLoaded 'execute'
Connect $cast $SAVE_OUT $saved 'self'
Connect $saved 'Unlocked' $setUnlocked 'UnlockedAchievements'
Connect $setUnlocked 'then' $setCount 'execute'
Connect $cast $SAVE_OUT $savedCount 'self'
Connect $savedCount 'FreeCount' $setCount 'FreeAchievementCount'
Connect $setCount 'then' $setLoaded 'execute'
Write-Body 'GI_LoadAchievements.txt' $loadedYet

# ===== UnlockAchievement =====================================================================================
Reset-Graph 300
$setLast = SelfSet 'LastAchievement' 'name' 300 0
$callLoad = New-Node '/Script/BlueprintGraph.K2Node_CallFunction' @('FunctionReference=(MemberName="LoadAchievements",bSelfContext=True)') 600 0
Add-Exec $callLoad
Connect $setLast 'then' $callLoad 'execute'
$taken = New-Branch 900 0
Connect (Contains (SelfGet 'UnlockedAchievements' 'name' 550 200 'Array') 'UnlockedAchievements' (SelfGet 'LastAchievement' 'name' 550 300) 'LastAchievement' 750 200) 'ReturnValue' $taken 'Condition'
Connect $callLoad 'then' $taken 'execute'
$known = New-Branch 1200 0
Connect (Contains (SelfGet 'AchievementIds' 'name' 850 200 'Array') 'AchievementIds' (SelfGet 'LastAchievement' 'name' 850 300) 'LastAchievement' 1050 200) 'ReturnValue' $known 'Condition'
Connect $taken 'else' $known 'execute'
# unknown id: a warning
$idText = New-Call $STRINGS 'Conv_NameToString' $true 1250 450
Add-Pin $idText 'InName' 'in' 'name'
Add-Pin $idText 'ReturnValue' 'out' 'string'
Connect (SelfGet 'LastAchievement' 'name' 1050 450) 'LastAchievement' $idText 'InName'
$warn = Print (Concat $null '未登録の実績 ID: ' $idText 'ReturnValue' 1450 450) 'ReturnValue' 1700 350
Connect $known 'else' $warn 'execute'
# known and new: on the list, counted if free
$add = ArrayCall 'Array_Add' $false 1500 0
Add-Pin $add 'TargetArray' 'in' 'name' '' $null $null 'Array'
Add-Pin $add 'NewItem' 'in' 'name'
Add-Pin $add 'ReturnValue' 'out' 'int'
Connect (SelfGet 'UnlockedAchievements' 'name' 1250 150 'Array') 'UnlockedAchievements' $add 'TargetArray'
Connect (SelfGet 'LastAchievement' 'name' 1250 250) 'LastAchievement' $add 'NewItem'
Connect $known 'then' $add 'execute'
$free = New-Branch 1800 0
Connect (Contains (SelfGet 'FreeAchievements' 'name' 1600 200 'Array') 'FreeAchievements' (SelfGet 'LastAchievement' 'name' 1600 300) 'LastAchievement' 1800 200) 'ReturnValue' $free 'Condition'
Connect $add 'then' $free 'execute'
$countUp = SelfSet 'FreeAchievementCount' 'int' 2100 -150
$plusOne = New-Operator 'Add' 'Add_IntInt' 'int' '' 'int' 1950 -250
Connect (SelfGet 'FreeAchievementCount' 'int' 1750 -250) 'FreeAchievementCount' $plusOne 'A'
(Get-Pin $plusOne 'B').Default = '1'
Connect $plusOne 'ReturnValue' $countUp 'FreeAchievementCount'
Connect $free 'then' $countUp 'execute'
# saved
$create = New-Call $STATICS 'CreateSaveGameObject' $false 2450 0
Add-Pin $create 'SaveGameClass' 'in' 'class' '' $SAVEGAME
(Get-Pin $create 'SaveGameClass') | Add-Member -NotePropertyName DefaultObject -NotePropertyValue $SAVE_PATH
Add-Pin $create 'ReturnValue' 'out' 'object' '' $SAVEGAME
Connect $countUp 'then' $create 'execute'
Connect $free 'else' $create 'execute'
$cast2 = SaveCast 2800 0
Connect $create 'then' $cast2 'execute'
Connect $create 'ReturnValue' $cast2 'Object'
$putUnlocked = New-VarSet 'Unlocked' $SAVE_CLASS 'name' $null 3150 0
foreach ($pin in 'Unlocked', 'Output_Get') { (Get-Pin $putUnlocked $pin).Container = 'Array' }
Connect $cast2 $SAVE_OUT $putUnlocked 'self'
Connect (SelfGet 'UnlockedAchievements' 'name' 2950 250 'Array') 'UnlockedAchievements' $putUnlocked 'Unlocked'
Connect $cast2 'then' $putUnlocked 'execute'
$putCount = New-VarSet 'FreeCount' $SAVE_CLASS 'int' $null 3500 0
Connect $cast2 $SAVE_OUT $putCount 'self'
Connect (SelfGet 'FreeAchievementCount' 'int' 3300 300) 'FreeAchievementCount' $putCount 'FreeCount'
Connect $putUnlocked 'then' $putCount 'execute'
$write = New-Call $STATICS 'SaveGameToSlot' $false 3850 0
Add-Pin $write 'SaveGameObject' 'in' 'object' '' $SAVEGAME
Add-Pin $write 'SlotName' 'in' 'string' '' $null $SLOT
Add-Pin $write 'UserIndex' 'in' 'int' '' $null '0'
Add-Pin $write 'ReturnValue' 'out' 'bool'
ConstRef $write 'SlotName'
Connect $cast2 $SAVE_OUT $write 'SaveGameObject'
Connect $putCount 'then' $write 'execute'
# for now: its name on screen (step 2 replaces this with the corner notice)
$index = ArrayCall 'Array_Find' $true 3800 450
Add-Pin $index 'TargetArray' 'in' 'name' '' $null $null 'Array'
Add-Pin $index 'ItemToFind' 'in' 'name'
Add-Pin $index 'ReturnValue' 'out' 'int'
Connect (SelfGet 'AchievementIds' 'name' 3600 450 'Array') 'AchievementIds' $index 'TargetArray'
Connect (SelfGet 'LastAchievement' 'name' 3600 550) 'LastAchievement' $index 'ItemToFind'
$nameItem = New-Node '/Script/BlueprintGraph.K2Node_GetArrayItem' @() 4050 400
Add-Pin $nameItem 'Array' 'in' 'text' '' $null $null 'Array'
Add-Pin $nameItem 'Dimension 1' 'in' 'int' '' $null '0'
Add-Pin $nameItem 'Output' 'out' 'text'
Connect (SelfGet 'AchievementNames' 'text' 3850 350 'Array') 'AchievementNames' $nameItem 'Array'
Connect $index 'ReturnValue' $nameItem 'Dimension 1'
$nameText = New-Call $TEXTLIB 'Conv_TextToString' $true 4250 400
Add-Pin $nameText 'InText' 'in' 'text'
Add-Pin $nameText 'ReturnValue' 'out' 'string'
ConstRef $nameText 'InText'
Connect $nameItem 'Output' $nameText 'InText'
$show = Print (Concat $null '実績解除: ' $nameText 'ReturnValue' 4450 300) 'ReturnValue' 4200 0
Connect $write 'then' $show 'execute'
Write-Body 'GI_UnlockAchievement.txt' $setLast
