param([string]$OutDir)
# Achievements step 5: the list screen as an icon grid (the user's layout, 2026-11-21). Widgets and variables from
# setup_achievement_list.py; designer parts by hand (names below, all Is Variable). Writes:
#   WBP_AchievementList_EventGraph.txt   the list's whole Event Graph
#     Construct: LoadAchievements; HeaderText = "取得 N / 31　　自由枠 F / 12"; one WBP_AchievementSlot per achievement
#       (Index, Owner = this list) into Grid, COLUMNS a row (a Branch loop over Row: macro instances do not paste
#       reliably); the first cell is shown and, a moment later, takes keyboard focus (arrow keys move between cells).
#     ShowDetail(Index), a custom event the cells call: DetailIcon (its icon, or the Unknown one for a hidden one not
#       taken; darkened until taken), DetailName / DetailCondition ("？？？" for a hidden one not taken), DetailKind.
#     BackButton clicked: the list closes (Remove from Parent), showing whatever opened it.
#   WBP_AchievementSlot_EventGraph.txt   a cell: Construct sets IconImage as above; focused (keyboard, or the mouse
#     over SlotButton, which hands it focus) it grows a little and the list shows its detail; unfocused, normal size.
#   WBP_Title_OpenAchievements.txt       WBP_Title's AchievementsButton opens the list.
# Paste the list first and compile it (the cells call its ShowDetail), then the cell.
# Run: powershell -File Generators/gen_achievement_list.ps1 -OutDir <Scripts folder>
if (-not $OutDir) { throw 'OutDir is required' }
$cageGen = Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_hell_cage.ps1'
$defs = Get-Content -LiteralPath $cageGen -Encoding UTF8 | Select-Object -Skip 10 -First 172
. ([ScriptBlock]::Create(($defs -join "`n")))

# const-ref pins and a class pin's chosen class
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

$USER_WIDGET = "/Script/CoreUObject.Class'/Script/UMG.UserWidget'"
$WIDGET = "/Script/CoreUObject.Class'/Script/UMG.Widget'"
$TEXT_BLOCK = "/Script/CoreUObject.Class'/Script/UMG.TextBlock'"
$IMAGE = "/Script/CoreUObject.Class'/Script/UMG.Image'"
$BUTTON = "/Script/CoreUObject.Class'/Script/UMG.Button'"
$GRID = "/Script/CoreUObject.Class'/Script/UMG.UniformGridPanel'"
$GRID_SLOT = "/Script/CoreUObject.Class'/Script/UMG.UniformGridSlot'"
$TEXTURE = "/Script/CoreUObject.Class'/Script/Engine.Texture2D'"
$TEXTLIB = "/Script/CoreUObject.Class'/Script/Engine.KismetTextLibrary'"
$COLOR = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.LinearColor'"
$VECTOR2D = "/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Vector2D'"
$FOCUS_EVENT = "/Script/CoreUObject.ScriptStruct'/Script/SlateCore.FocusEvent'"
$LIST_CLASS = "/Script/UMGEditor.WidgetBlueprintGeneratedClass'/Game/UI/WBP_AchievementList.WBP_AchievementList_C'"
$SLOT_CLASS = "/Script/UMGEditor.WidgetBlueprintGeneratedClass'/Game/UI/WBP_AchievementSlot.WBP_AchievementSlot_C'"
$COLUMNS = '8'           # the user's choice, 2026-11-21
$FREE_NEEDED = '12'      # the hidden stage's free slots (Achievements_Plan.md)
$TAKEN_TINT = '(R=1.000000,G=1.000000,B=1.000000,A=1.000000)'
$LOCKED_TINT = '(R=0.250000,G=0.250000,B=0.250000,A=1.000000)'
$FOCUS_SCALE = '(X=1.150000,Y=1.150000)'
$NORMAL_SCALE = '(X=1.000000,Y=1.000000)'

function Pure($lib, $func, [double]$x, [double]$y, $inputs, $outCat, [string[]]$constRef = @(), $outObj = $null) {
  $n = New-Call $lib $func $true $x $y
  foreach ($in in $inputs) { Add-Pin $n $in[0] 'in' $in[1] '' $in[3] $in[2] }
  Add-Pin $n 'ReturnValue' 'out' $outCat '' $outObj
  foreach ($name in $constRef) { (Get-Pin $n $name) | Add-Member -NotePropertyName ConstRef -NotePropertyValue $true -Force }
  return $n
}
# A + B as strings; a $null node takes the next argument as a literal instead. (Not "Cat": that is Get-Content.)
function Join-Str($a, $aPin, $b, $bPin, [double]$x, [double]$y) {
  $n = Pure $STRINGS 'Concat_StrStr' $x $y @(@('A', 'string'), @('B', 'string')) 'string' @('A', 'B')
  if ($a) { Connect $a $aPin $n 'A' } else { (Get-Pin $n 'A').Default = $aPin }
  if ($b) { Connect $b $bPin $n 'B' } else { (Get-Pin $n 'B').Default = $bPin }
  return $n
}
function IntText($node, $pin, [double]$x, [double]$y) {
  $n = Pure $STRINGS 'Conv_IntToString' $x $y @(,@('InInt', 'int')) 'string'
  Connect $node $pin $n 'InInt'
  return $n
}
function GiArray($cast, $name, $cat, [double]$x, [double]$y, $obj = $null) {
  $n = New-VarGet $name $GI_CLASS $cat '' $obj $x $y 'Array'
  Connect $cast $GI_OUT $n 'self'
  return $n
}
function Length($array, $pin, $cat, [double]$x, [double]$y) {
  $n = New-Call $ARRAYLIB 'Array_Length' $true $x $y '/Script/BlueprintGraph.K2Node_CallArrayFunction'
  Add-Pin $n 'TargetArray' 'in' $cat '' $null $null 'Array'
  Add-Pin $n 'ReturnValue' 'out' 'int'
  Connect $array $pin $n 'TargetArray'
  return $n
}
function Has($array, $pin, $item, $itemPin, [double]$x, [double]$y) {
  $n = New-Call $ARRAYLIB 'Array_Contains' $true $x $y '/Script/BlueprintGraph.K2Node_CallArrayFunction'
  Add-Pin $n 'TargetArray' 'in' 'name' '' $null $null 'Array'
  Add-Pin $n 'ItemToFind' 'in' 'name'
  Add-Pin $n 'ReturnValue' 'out' 'bool'
  Connect $array $pin $n 'TargetArray'
  Connect $item $itemPin $n 'ItemToFind'
  return $n
}
# array[index] (index: a node and pin)
function Item($array, $pin, $cat, $index, $indexPin, [double]$x, [double]$y, $obj = $null) {
  $n = New-Node '/Script/BlueprintGraph.K2Node_GetArrayItem' @() $x $y
  Add-Pin $n 'Array' 'in' $cat '' $obj $null 'Array'
  Add-Pin $n 'Dimension 1' 'in' 'int' '' $null '0'
  Add-Pin $n 'Output' 'out' $cat '' $obj
  Connect $array $pin $n 'Array'
  Connect $index $indexPin $n 'Dimension 1'
  return $n
}
function PickString($a, $aPin, $b, $bPin, $pickA, $pickPin, [double]$x, [double]$y) {
  $n = Pure $MATH 'SelectString' $x $y @(@('A', 'string'), @('B', 'string'), @('bPickA', 'bool')) 'string' @('A', 'B')
  if ($a) { Connect $a $aPin $n 'A' } else { (Get-Pin $n 'A').Default = $aPin }
  if ($b) { Connect $b $bPin $n 'B' } else { (Get-Pin $n 'B').Default = $bPin }
  Connect $pickA $pickPin $n 'bPickA'
  return $n
}
function TextAsString($node, $pin, [double]$x, [double]$y) {
  $n = Pure $TEXTLIB 'Conv_TextToString' $x $y @(,@('InText', 'text')) 'string' @('InText')
  Connect $node $pin $n 'InText'
  return $n
}
function SelfObject($name, $obj, [double]$x, [double]$y) { New-VarGet $name $null 'object' '' $obj $x $y }
function ShowText($widgetName, $string, $pin, [double]$x, [double]$y) {
  $asText = Pure $TEXTLIB 'Conv_StringToText' ($x - 250) ($y + 200) @(,@('InString', 'string')) 'text' @('InString')
  Connect $string $pin $asText 'InString'
  $n = New-Call $TEXT_BLOCK 'SetText' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $TEXT_BLOCK
  Add-Pin $n 'InText' 'in' 'text'
  Connect (SelfObject $widgetName $TEXT_BLOCK ($x - 200) ($y + 120)) $widgetName $n 'self'
  Connect $asText 'ReturnValue' $n 'InText'
  return $n
}
function Event($owner, $name, [double]$x, [double]$y) {
  $n = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$owner`",MemberName=`"$name`")", 'bOverrideFunction=True') $x $y
  Add-Pin $n 'then' 'out' 'exec'
  return $n
}
function ButtonEvent($button, $delegate, $signature, $owner, [double]$x, [double]$y) {
  $n = New-Node '/Script/BlueprintGraph.K2Node_ComponentBoundEvent' @(
    "DelegatePropertyName=`"$delegate`"",
    "DelegateOwnerClass=`"$BUTTON`"",
    "ComponentPropertyName=`"$button`"",
    "EventReference=(MemberParent=`"/Script/CoreUObject.Package'/Script/UMG'`",MemberName=`"$signature`")",
    "CustomFunctionName=`"BndEvt__${owner}_${button}_K2Node_ComponentBoundEvent_${delegate}_$signature`"") $x $y
  Add-Pin $n 'then' 'out' 'exec'
  return $n
}
# The icon of achievement `index` onto an Image (by name): its own, or Unknown when hidden and not taken; darkened
# until taken. Returns @(first, last) exec nodes.
function PaintIcon($cast, $imageName, $index, $indexPin, [double]$x, [double]$y) {
  $id = Item (GiArray $cast 'AchievementIds' 'name' ($x - 300) ($y + 400)) 'AchievementIds' 'name' $index $indexPin ($x - 100) ($y + 400)
  $got = Has (GiArray $cast 'UnlockedAchievements' 'name' ($x - 100) ($y + 550)) 'UnlockedAchievements' $id 'Output' ($x + 100) ($y + 500)
  $hidden = Has (GiArray $cast 'HiddenAchievements' 'name' ($x - 100) ($y + 700)) 'HiddenAchievements' $id 'Output' ($x + 100) ($y + 650)
  $open = Pure $MATH 'Not_PreBool' ($x + 300) ($y + 650) @(,@('A', 'bool')) 'bool'
  Connect $hidden 'ReturnValue' $open 'A'
  $show = Pure $MATH 'BooleanOR' ($x + 500) ($y + 550) @(@('A', 'bool'), @('B', 'bool')) 'bool'
  Connect $got 'ReturnValue' $show 'A'
  Connect $open 'ReturnValue' $show 'B'
  $known = New-Branch $x $y
  Connect $show 'ReturnValue' $known 'Condition'
  function Brush($picture, $picturePin, [double]$bx, [double]$by) {   # (not $texture: names ignore case, it would hide $TEXTURE)
    $n = New-Call $IMAGE 'SetBrushFromTexture' $false $bx $by
    Add-Pin $n 'self' 'in' 'object' '' $IMAGE
    Add-Pin $n 'Texture' 'in' 'object' '' $TEXTURE
    Add-Pin $n 'bMatchSize' 'in' 'bool' '' $null 'false'
    Connect (SelfObject $imageName $IMAGE ($bx - 200) ($by + 120)) $imageName $n 'self'
    Connect $picture $picturePin $n 'Texture'
    return $n
  }
  $own = Item (GiArray $cast 'AchievementIcons' 'object' ($x + 100) ($y - 350) $TEXTURE) 'AchievementIcons' 'object' $index $indexPin ($x + 300) ($y - 350) $TEXTURE
  $yes = Brush $own 'Output' ($x + 550) ($y - 200)
  $unknown = New-VarGet 'UnknownAchievementIcon' $GI_CLASS 'object' '' $TEXTURE ($x + 350) ($y + 250)
  Connect $cast $GI_OUT $unknown 'self'
  $no = Brush $unknown 'UnknownAchievementIcon' ($x + 550) ($y + 150)
  Connect $known 'then' $yes 'execute'
  Connect $known 'else' $no 'execute'
  $tint = New-Call $IMAGE 'SetColorAndOpacity' $false ($x + 900) $y
  Add-Pin $tint 'self' 'in' 'object' '' $IMAGE
  Add-Pin $tint 'InColorAndOpacity' 'in' 'struct' '' $COLOR
  Connect (SelfObject $imageName $IMAGE ($x + 700) ($y + 150)) $imageName $tint 'self'
  $shade = Pure $MATH 'SelectColor' ($x + 700) ($y + 350) @(@('A', 'struct', $TAKEN_TINT, $COLOR), @('B', 'struct', $LOCKED_TINT, $COLOR), @('bPickA', 'bool')) 'struct' @() $COLOR
  Connect $got 'ReturnValue' $shade 'bPickA'
  Connect $shade 'ReturnValue' $tint 'InColorAndOpacity'
  Connect $yes 'then' $tint 'execute'
  Connect $no 'then' $tint 'execute'
  return @($known, $tint, $got, $show, $id)
}

# =====================================================================================================================
# WBP_AchievementList
# =====================================================================================================================
Reset-Graph 100
$construct = Event $USER_WIDGET 'Construct' 0 0
$cast = GameInstance 300 0
Connect $construct 'then' $cast 'execute'
$load = New-Call $GI_CLASS 'LoadAchievements' $false 600 0
Add-Pin $load 'self' 'in' 'object' '' $GI_CLASS
Connect $cast $GI_OUT $load 'self'
Connect $cast 'then' $load 'execute'
# header
$taken = IntText (Length (GiArray $cast 'UnlockedAchievements' 'name' 400 400) 'UnlockedAchievements' 'name' 600 400) 'ReturnValue' 800 400
$all = IntText (Length (GiArray $cast 'AchievementIds' 'name' 400 500) 'AchievementIds' 'name' 600 500) 'ReturnValue' 800 500
$free = IntText (GiGet $cast 'FreeAchievementCount' 'int' '' 600 600) 'FreeAchievementCount' 800 600
$h = Join-Str $null '取得 ' $taken 'ReturnValue' 1000 400
$h = Join-Str $h 'ReturnValue' $null ' / ' 1200 400
$h = Join-Str $h 'ReturnValue' $all 'ReturnValue' 1400 450
$h = Join-Str $h 'ReturnValue' $null '　　自由枠 ' 1600 450
$h = Join-Str $h 'ReturnValue' $free 'ReturnValue' 1800 500
$h = Join-Str $h 'ReturnValue' $null " / $FREE_NEEDED" 2000 500
$header = ShowText 'HeaderText' $h 'ReturnValue' 2300 0
Connect $load 'then' $header 'execute'
# the cells: Row 0.. while Row < number of achievements
$start = New-VarSet 'Row' $null 'int' $null 2600 0
(Get-Pin $start 'Row').Default = '0'
Connect $header 'then' $start 'execute'
$more = New-Branch 2850 0
$less = New-Operator 'Less' 'Less_IntInt' 'int' '' 'bool' 2750 250
Connect (New-VarGet 'Row' $null 'int' '' $null 2550 250) 'Row' $less 'A'
Connect (Length (GiArray $cast 'AchievementIds' 'name' 2350 350) 'AchievementIds' 'name' 2550 350) 'ReturnValue' $less 'B'
Connect $less 'ReturnValue' $more 'Condition'
Connect $start 'then' $more 'execute'
$make = New-Node '/Script/UMGEditor.K2Node_CreateWidget' @() 3100 0
Add-Pin $make 'execute' 'in' 'exec'
Add-Pin $make 'then' 'out' 'exec'
Add-Pin $make 'Class' 'in' 'class' '' $USER_WIDGET
(Get-Pin $make 'Class') | Add-Member -NotePropertyName DefaultObject -NotePropertyValue $SLOT_CLASS
Add-Pin $make 'OwningPlayer' 'in' 'object' '' "/Script/CoreUObject.Class'/Script/Engine.PlayerController'"
Add-Pin $make 'ReturnValue' 'out' 'object' '' $SLOT_CLASS
Connect $more 'then' $make 'execute'
$setIndex = New-VarSet 'Index' $SLOT_CLASS 'int' $null 3450 0
Connect $make 'ReturnValue' $setIndex 'self'
Connect (New-VarGet 'Row' $null 'int' '' $null 3250 250) 'Row' $setIndex 'Index'
$setOwner = New-VarSet 'Owner' $SLOT_CLASS 'object' $LIST_CLASS 3750 0
Connect $make 'ReturnValue' $setOwner 'self'
$me = New-Node '/Script/BlueprintGraph.K2Node_Self' @() 3600 250
Add-Pin $me 'self' 'out' 'object' '' $USER_WIDGET
Connect $me 'self' $setOwner 'Owner'
Chain @($make, $setIndex, $setOwner)
$place = New-Call $GRID 'AddChildToUniformGrid' $false 4050 0
Add-Pin $place 'self' 'in' 'object' '' $GRID
Add-Pin $place 'Content' 'in' 'object' '' $WIDGET
Add-Pin $place 'InRow' 'in' 'int' '' $null '0'
Add-Pin $place 'InColumn' 'in' 'int' '' $null '0'
Add-Pin $place 'ReturnValue' 'out' 'object' '' $GRID_SLOT
Connect (SelfObject 'Grid' $GRID 3850 250) 'Grid' $place 'self'
Connect $make 'ReturnValue' $place 'Content'
$down = New-Operator 'Divide' 'Divide_IntInt' 'int' '' 'int' 3950 400
Connect (New-VarGet 'Row' $null 'int' '' $null 3750 400) 'Row' $down 'A'
(Get-Pin $down 'B').Default = $COLUMNS
Connect $down 'ReturnValue' $place 'InRow'
$across = New-Operator 'Percent' 'Percent_IntInt' 'int' '' 'int' 3950 550
Connect (New-VarGet 'Row' $null 'int' '' $null 3750 550) 'Row' $across 'A'
(Get-Pin $across 'B').Default = $COLUMNS
Connect $across 'ReturnValue' $place 'InColumn'
Connect $setOwner 'then' $place 'execute'
# the first cell is remembered (focused at the end)
$isFirst = New-Branch 4350 0
$zero = New-Operator 'EqualEqual' 'EqualEqual_IntInt' 'int' '' 'bool' 4250 250
Connect (New-VarGet 'Row' $null 'int' '' $null 4050 700) 'Row' $zero 'A'
(Get-Pin $zero 'B').Default = '0'
Connect $zero 'ReturnValue' $isFirst 'Condition'
Connect $place 'then' $isFirst 'execute'
$keepFirst = New-VarSet 'FirstSlot' $null 'object' $SLOT_CLASS 4600 -150
Connect $make 'ReturnValue' $keepFirst 'FirstSlot'
Connect $isFirst 'then' $keepFirst 'execute'
$next = New-VarSet 'Row' $null 'int' $null 4900 0
$plus = New-Operator 'Add' 'Add_IntInt' 'int' '' 'int' 4800 250
Connect (New-VarGet 'Row' $null 'int' '' $null 4650 250) 'Row' $plus 'A'
(Get-Pin $plus 'B').Default = '1'
Connect $plus 'ReturnValue' $next 'Row'
Connect $keepFirst 'then' $next 'execute'
Connect $isFirst 'else' $next 'execute'
Connect $next 'then' $more 'execute'   # back round the loop
# done: the first one shown and, once the cells exist on screen, focused
$showFirst = New-Node '/Script/BlueprintGraph.K2Node_CallFunction' @('FunctionReference=(MemberName="ShowDetail",bSelfContext=True)') 3100 -500
Add-Exec $showFirst
Add-Pin $showFirst 'Index' 'in' 'int' '' $null '0'
Connect $more 'else' $showFirst 'execute'
$settle = Delay '0.05' 3400 -500
Connect $showFirst 'then' $settle 'execute'
$focus = New-Call $WIDGET 'SetKeyboardFocus' $false 3900 -500
Add-Pin $focus 'self' 'in' 'object' '' $WIDGET
$firstButton = New-VarGet 'SlotButton' $SLOT_CLASS 'object' '' $BUTTON 3700 -300
Connect (SelfObject 'FirstSlot' $SLOT_CLASS 3500 -300) 'FirstSlot' $firstButton 'self'
Connect $firstButton 'SlotButton' $focus 'self'
Connect $settle 'then' $focus 'execute'

# ----- ShowDetail(Index): the right-hand side -----
$detail = New-Node '/Script/BlueprintGraph.K2Node_CustomEvent' @('CustomFunctionName="ShowDetail"') 0 1600
Add-Pin $detail 'then' 'out' 'exec'
Add-Pin $detail 'Index' 'out' 'int'
$detail.Props += 'CustomProperties UserDefinedPin (PinName="Index",PinType=(PinCategory="int"),DesiredPinDirection=EGPD_Output,PinDefaultValue="0")'
$cast2 = GameInstance 300 1600
Connect $detail 'then' $cast2 'execute'
$paint = PaintIcon $cast2 'DetailIcon' $detail 'Index' 650 1600
Connect $cast2 'then' $paint[0] 'execute'
$got = $paint[2]; $show = $paint[3]
$name = PickString (TextAsString (Item (GiArray $cast2 'AchievementNames' 'text' 1300 2400) 'AchievementNames' 'text' $detail 'Index' 1500 2400) 'Output' 1700 2400) 'ReturnValue' $null '？？？' $show 'ReturnValue' 1950 2350
$cond = PickString (TextAsString (Item (GiArray $cast2 'AchievementDescriptions' 'text' 1300 2600) 'AchievementDescriptions' 'text' $detail 'Index' 1500 2600) 'Output' 1700 2600) 'ReturnValue' $null '？？？' $show 'ReturnValue' 1950 2550
$kind = Item (GiArray $cast2 'AchievementKinds' 'string' 1300 2800) 'AchievementKinds' 'string' $detail 'Index' 1500 2800
$state = PickString $null '　取得済み' $null '　未取得' $got 'ReturnValue' 1700 2900
$kindLine = Join-Str (Join-Str $null '種類: ' $kind 'Output' 1950 2800) 'ReturnValue' $state 'ReturnValue' 2150 2850
$writeName = ShowText 'DetailName' $name 'ReturnValue' 2400 1600
$writeCond = ShowText 'DetailCondition' $cond 'ReturnValue' 2700 1600
$writeKind = ShowText 'DetailKind' $kindLine 'ReturnValue' 3000 1600
Connect $paint[1] 'then' $writeName 'execute'
Chain @($writeName, $writeCond, $writeKind)

# ----- Back -----
$back = ButtonEvent 'BackButton' 'OnClicked' 'OnButtonClickedEvent__DelegateSignature' 'WBP_AchievementList' 0 -800
$close = New-Call $WIDGET 'RemoveFromParent' $false 350 -800
Add-Pin $close 'self' 'in' 'object' '' $WIDGET
Connect $back 'then' $close 'execute'
Write-Graph 'WBP_AchievementList_EventGraph.txt'

# =====================================================================================================================
# WBP_AchievementSlot
# =====================================================================================================================
Reset-Graph 100
$construct = Event $USER_WIDGET 'Construct' 0 0
$cast = GameInstance 300 0
Connect $construct 'then' $cast 'execute'
$paint = PaintIcon $cast 'IconImage' (New-VarGet 'Index' $null 'int' '' $null 400 700) 'Index' 650 0
Connect $cast 'then' $paint[0] 'execute'
function Grow($scale, [double]$x, [double]$y) {
  $n = New-Call $WIDGET 'SetRenderScale' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $WIDGET
  Add-Pin $n 'Scale' 'in' 'struct' '' $VECTOR2D $scale
  return $n
}
# focused: bigger, and the list shows it
$focused = Event $USER_WIDGET 'OnAddedToFocusPath' 0 1500
Add-Pin $focused 'InFocusEvent' 'out' 'struct' '' $FOCUS_EVENT
$tell = New-Call $LIST_CLASS 'ShowDetail' $false 350 1500
Add-Pin $tell 'self' 'in' 'object' '' $LIST_CLASS
Add-Pin $tell 'Index' 'in' 'int'
Connect (SelfObject 'Owner' $LIST_CLASS 150 1700) 'Owner' $tell 'self'
Connect (New-VarGet 'Index' $null 'int' '' $null 150 1800) 'Index' $tell 'Index'
Connect $focused 'then' $tell 'execute'
$big = Grow $FOCUS_SCALE 700 1500
Connect $tell 'then' $big 'execute'
$left = Event $USER_WIDGET 'OnRemovedFromFocusPath' 0 2000
Add-Pin $left 'InFocusEvent' 'out' 'struct' '' $FOCUS_EVENT
$small = Grow $NORMAL_SCALE 350 2000
Connect $left 'then' $small 'execute'
# the mouse over the button hands it focus, so mouse and keys work the same way
$hover = ButtonEvent 'SlotButton' 'OnHovered' 'OnButtonHoverEvent__DelegateSignature' 'WBP_AchievementSlot' 0 2400
$take = New-Call $WIDGET 'SetKeyboardFocus' $false 350 2400
Add-Pin $take 'self' 'in' 'object' '' $WIDGET
Connect (SelfObject 'SlotButton' $BUTTON 150 2600) 'SlotButton' $take 'self'
Connect $hover 'then' $take 'execute'
Write-Graph 'WBP_AchievementSlot_EventGraph.txt'

# =====================================================================================================================
# WBP_Title: AchievementsButton opens the list over the title
# =====================================================================================================================
Reset-Graph 100
$clicked = ButtonEvent 'AchievementsButton' 'OnClicked' 'OnButtonClickedEvent__DelegateSignature' 'WBP_Title' 0 0
$make = New-Node '/Script/UMGEditor.K2Node_CreateWidget' @() 300 0
Add-Pin $make 'execute' 'in' 'exec'
Add-Pin $make 'then' 'out' 'exec'
Add-Pin $make 'Class' 'in' 'class' '' $USER_WIDGET
(Get-Pin $make 'Class') | Add-Member -NotePropertyName DefaultObject -NotePropertyValue $LIST_CLASS
Add-Pin $make 'OwningPlayer' 'in' 'object' '' "/Script/CoreUObject.Class'/Script/Engine.PlayerController'"
Add-Pin $make 'ReturnValue' 'out' 'object' '' $LIST_CLASS
Connect $clicked 'then' $make 'execute'
$show = New-Call $USER_WIDGET 'AddToViewport' $false 650 0
Add-Pin $show 'self' 'in' 'object' '' $USER_WIDGET
Add-Pin $show 'ZOrder' 'in' 'int' '' $null '50'
Connect $make 'ReturnValue' $show 'self'
Connect $make 'then' $show 'execute'
Write-Graph 'WBP_Title_OpenAchievements.txt'
