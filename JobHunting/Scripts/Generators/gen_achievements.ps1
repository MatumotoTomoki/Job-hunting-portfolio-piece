param([string]$OutDir)
# Paste text for the achievements' foundation in BP_MyGameInstance (variables, the save and the empty function graphs
# from setup_achievements.py; the plan is Scripts/Achievements_Plan.md):
#   GI_LoadAchievements.txt   the body of the function LoadAchievements: once per game, if the "Achievements" slot
#                             exists, UnlockedAchievements and FreeAchievementCount come from BP_AchievementSave; then
#                             AchievementsLoaded.
#   GI_UnlockAchievement.txt  the body of the function UnlockAchievement (input ID, Name, added by hand): LastAchievement
#                             = ID; LoadAchievements; if ID is a known achievement not yet taken, it goes on
#                             UnlockedAchievements (and FreeAchievementCount + 1 if it is a free one), the slot is
#                             saved, and its name joins AchievementQueue for the corner notice. An unknown ID prints
#                             a warning.
#   WBP_AchievementNotice_EventGraph.txt   the corner notice's graph (step 2; widget and variables from
#                             setup_achievement_notice.py): see its section below.
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
# its name joins AchievementQueue: WBP_AchievementNotice shows it (step 2)
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
$queue = ArrayCall 'Array_Add' $false 4250 0
Add-Pin $queue 'TargetArray' 'in' 'text' '' $null $null 'Array'
Add-Pin $queue 'NewItem' 'in' 'text'
Add-Pin $queue 'ReturnValue' 'out' 'int'
Connect (SelfGet 'AchievementQueue' 'text' 4050 250 'Array') 'AchievementQueue' $queue 'TargetArray'
Connect $nameItem 'Output' $queue 'NewItem'
Connect $write 'then' $queue 'execute'
Write-Body 'GI_UnlockAchievement.txt' $setLast

# ===== WBP_AchievementNotice ==================================================================================
# Construct: invisible. Every frame (paused too: widgets keep ticking):
#   showing: Age += InDeltaTime; past SHOW seconds it is done (invisible again); before that its opacity is
#     clamp(min(Age / FADE_IN, (SHOW - Age) / FADE_OUT), 0, 1) and it slides in from SLIDE px to the right as it fades in;
#   not showing and AchievementQueue has a name: NoticeText = the first name, which leaves the queue; Age 0, showing;
#     NoticeSound at SE Volume x Master Volume.
# The queue lives on the game instance, so a notice for an achievement taken just before a level change shows in the
# next level's HUD.
$USER_WIDGET = "/Script/CoreUObject.Class'/Script/UMG.UserWidget'"
$TEXT_BLOCK = "/Script/CoreUObject.Class'/Script/UMG.TextBlock'"
$GEOMETRY = "/Script/CoreUObject.ScriptStruct'/Script/SlateCore.Geometry'"
$VECTOR2D = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Vector2D'"
$SOUND_BASE = "/Script/CoreUObject.Class'/Script/Engine.SoundBase'"
$SHOW = '4.0'
$FADE_IN = '0.25'
$FADE_OUT = '0.6'
$SLIDE = '80.0'

function Op($operation, $func, $a, $aPin, $b, $bPin, [double]$x, [double]$y, $outCat = 'real') {
  $n = New-Operator $operation $func 'real' 'double' $outCat $x $y
  if ($outCat -eq 'real') { (Get-Pin $n 'ReturnValue').Sub = 'double' }
  if ($a) { Connect $a $aPin $n 'A' } else { (Get-Pin $n 'A').Default = $aPin }
  if ($b) { Connect $b $bPin $n 'B' } else { (Get-Pin $n 'B').Default = $bPin }
  return $n
}
# The fade and slide act on NoticeBox (the Border, Is Variable), never on the widget itself: Slate skips painting a
# widget at opacity 0, and a user widget only ticks while it is painted, so a fully transparent self would never tick.
$WIDGET = "/Script/CoreUObject.Class'/Script/UMG.Widget'"
$BORDER = "/Script/CoreUObject.Class'/Script/UMG.Border'"
function Box([double]$x, [double]$y) { New-VarGet 'NoticeBox' $null 'object' '' $BORDER $x $y }
function Opacity([double]$x, [double]$y, $value = $null) {
  $n = New-Call $WIDGET 'SetRenderOpacity' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $WIDGET
  Add-Pin $n 'InOpacity' 'in' 'real' 'float' $null $value
  Connect (Box ($x - 200) ($y + 150)) 'NoticeBox' $n 'self'
  return $n
}
function WidgetEvent($name, [double]$x, [double]$y) {
  $n = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$USER_WIDGET`",MemberName=`"$name`")", 'bOverrideFunction=True') $x $y
  Add-Pin $n 'then' 'out' 'exec'
  return $n
}
function Queue($cast, [double]$x, [double]$y) {
  $n = New-VarGet 'AchievementQueue' $GI_CLASS 'text' '' $null $x $y 'Array'
  Connect $cast $GI_OUT $n 'self'
  return $n
}

Reset-Graph 500
$construct = WidgetEvent 'Construct' 0 -400
$hidden = Opacity 300 -400 '0.0'
Connect $construct 'then' $hidden 'execute'

$tick = WidgetEvent 'Tick' 0 0
Add-Pin $tick 'MyGeometry' 'out' 'struct' '' $GEOMETRY
Add-Pin $tick 'InDeltaTime' 'out' 'real' 'float'
$cast = GameInstance 300 0
Connect $tick 'then' $cast 'execute'
$showing = New-Branch 650 0
Connect (SelfGet 'Showing' 'bool' 450 200) 'Showing' $showing 'Condition'
Connect $cast 'then' $showing 'execute'

# --- showing: age, fade, slide ---
$older = SelfSet 'Age' 'real' 950 -300
foreach ($pin in 'Age', 'Output_Get') { (Get-Pin $older $pin).Sub = 'double' }
$sum = Op 'Add' 'Add_DoubleDouble' (New-VarGet 'Age' $null 'real' 'double' $null 650 -450) 'Age' $tick 'InDeltaTime' 850 -450
Connect $sum 'ReturnValue' $older 'Age'
Connect $showing 'then' $older 'execute'
$done = New-Branch 1250 -300
Connect (Op 'GreaterEqual' 'GreaterEqual_DoubleDouble' $older 'Output_Get' $null $SHOW 1150 -100 'bool') 'ReturnValue' $done 'Condition'
Connect $older 'then' $done 'execute'
$stop = SelfSet 'Showing' 'bool' 1550 -550 'None' 'false'
Connect $done 'then' $stop 'execute'
$gone = Opacity 1850 -550 '0.0'
Connect $stop 'then' $gone 'execute'
$rise = Op 'Divide' 'Divide_DoubleDouble' $older 'Output_Get' $null $FADE_IN 1400 50
$left = Op 'Subtract' 'Subtract_DoubleDouble' $null $SHOW $older 'Output_Get' 1400 200
$fall = Op 'Divide' 'Divide_DoubleDouble' $left 'ReturnValue' $null $FADE_OUT 1600 200
$lower = New-Call $MATH 'FMin' $true 1800 100
Add-Pin $lower 'A' 'in' 'real' 'double'
Add-Pin $lower 'B' 'in' 'real' 'double'
Add-Pin $lower 'ReturnValue' 'out' 'real' 'double'
Connect $rise 'ReturnValue' $lower 'A'
Connect $fall 'ReturnValue' $lower 'B'
$alpha = New-Call $MATH 'FClamp' $true 2000 100
Add-Pin $alpha 'Value' 'in' 'real' 'double'
Add-Pin $alpha 'Min' 'in' 'real' 'double' $null '0.0'
Add-Pin $alpha 'Max' 'in' 'real' 'double' $null '1.0'
Add-Pin $alpha 'ReturnValue' 'out' 'real' 'double'
Connect $lower 'ReturnValue' $alpha 'Value'
$fadeTo = Opacity 1850 -250
Connect $alpha 'ReturnValue' $fadeTo 'InOpacity'
Connect $done 'else' $fadeTo 'execute'
$away = Op 'Subtract' 'Subtract_DoubleDouble' $null '1.0' $alpha 'ReturnValue' 2200 200
$offset = Op 'Multiply' 'Multiply_DoubleDouble' $away 'ReturnValue' $null $SLIDE 2400 200
$where = New-Call $MATH 'MakeVector2D' $true 2600 200
Add-Pin $where 'X' 'in' 'real' 'double'
Add-Pin $where 'Y' 'in' 'real' 'double' $null '0.0'
Add-Pin $where 'ReturnValue' 'out' 'struct' '' $VECTOR2D
Connect $offset 'ReturnValue' $where 'X'
$slide = New-Call $WIDGET 'SetRenderTranslation' $false 2200 -250
Add-Pin $slide 'self' 'in' 'object' '' $WIDGET
Add-Pin $slide 'Translation' 'in' 'struct' '' $VECTOR2D
Connect (Box 2000 -100) 'NoticeBox' $slide 'self'
Connect $where 'ReturnValue' $slide 'Translation'
Connect $fadeTo 'then' $slide 'execute'

# --- not showing: the next name, if any ---
$waiting = New-Branch 950 500
$length = ArrayCall 'Array_Length' $true 750 700
Add-Pin $length 'TargetArray' 'in' 'text' '' $null $null 'Array'
Add-Pin $length 'ReturnValue' 'out' 'int'
Connect (Queue $cast 550 700) 'AchievementQueue' $length 'TargetArray'
$any = New-Operator 'Greater' 'Greater_IntInt' 'int' '' 'bool' 900 700
Connect $length 'ReturnValue' $any 'A'
(Get-Pin $any 'B').Default = '0'
Connect $any 'ReturnValue' $waiting 'Condition'
Connect $showing 'else' $waiting 'execute'
$first = New-Node '/Script/BlueprintGraph.K2Node_GetArrayItem' @() 1300 750
Add-Pin $first 'Array' 'in' 'text' '' $null $null 'Array'
Add-Pin $first 'Dimension 1' 'in' 'int' '' $null '0'
Add-Pin $first 'Output' 'out' 'text'
Connect (Queue $cast 1100 750) 'AchievementQueue' $first 'Array'
$write = New-Call $TEXT_BLOCK 'SetText' $false 1300 500
Add-Pin $write 'self' 'in' 'object' '' $TEXT_BLOCK
Add-Pin $write 'InText' 'in' 'text'
Connect (New-VarGet 'NoticeText' $null 'object' '' $TEXT_BLOCK 1100 650) 'NoticeText' $write 'self'
Connect $first 'Output' $write 'InText'
Connect $waiting 'then' $write 'execute'
$take = ArrayCall 'Array_Remove' $false 1650 500
Add-Pin $take 'TargetArray' 'in' 'text' '' $null $null 'Array'
Add-Pin $take 'IndexToRemove' 'in' 'int' '' $null '0'
Connect (Queue $cast 1450 750) 'AchievementQueue' $take 'TargetArray'
Connect $write 'then' $take 'execute'
$fresh = SelfSet 'Age' 'real' 1950 500 'None' '0.0'
foreach ($pin in 'Age', 'Output_Get') { (Get-Pin $fresh $pin).Sub = 'double' }
Connect $take 'then' $fresh 'execute'
$start = SelfSet 'Showing' 'bool' 2250 500 'None' 'true'
Connect $fresh 'then' $start 'execute'
$volume = Op 'Multiply' 'Multiply_DoubleDouble' (GiGet $cast 'SE Volume' 'real' 'double' 2300 800) 'SE Volume' (GiGet $cast 'Master Volume' 'real' 'double' 2300 900) 'Master Volume' 2550 850
$ding = New-Call $STATICS 'PlaySound2D' $false 2550 500
Add-Pin $ding 'Sound' 'in' 'object' '' $SOUND_BASE
Add-Pin $ding 'VolumeMultiplier' 'in' 'real' 'float'
Add-Pin $ding 'PitchMultiplier' 'in' 'real' 'float' $null '1.0'
Add-Pin $ding 'StartTime' 'in' 'real' 'float' $null '0.0'
Connect (New-VarGet 'NoticeSound' $null 'object' '' $SOUND_BASE 2350 700) 'NoticeSound' $ding 'Sound'
Connect $volume 'ReturnValue' $ding 'VolumeMultiplier'
Connect $start 'then' $ding 'execute'
Write-Body 'WBP_AchievementNotice_EventGraph.txt' $null
