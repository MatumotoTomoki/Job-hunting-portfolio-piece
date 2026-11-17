param([string]$OutDir, [string]$ControllerExport)
# Generates Ctrl+V-pasteable Blueprint node text for the SE volume pause menu feature.

$GI_CLASS = "/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPerson/Blueprints/BP_MyGameInstance.BP_MyGameInstance_C'"
$PAZU     = "/Script/UMG.WidgetBlueprintGeneratedClass'/Game/UI/pa-zu.pa-zu_C'"
$TEXTBLK  = "/Script/CoreUObject.Class'/Script/UMG.TextBlock'"
$WIDGET   = "/Script/CoreUObject.Class'/Script/UMG.Widget'"
$VIS      = "/Script/CoreUObject.Enum'/Script/UMG.ESlateVisibility'"
$AUDIO    = "/Script/CoreUObject.Class'/Script/Engine.AudioComponent'"
$GAMEINST = "/Script/CoreUObject.Class'/Script/Engine.GameInstance'"
$OBJECT   = "/Script/CoreUObject.Class'/Script/CoreUObject.Object'"
$MATH     = "/Script/CoreUObject.Class'/Script/Engine.KismetMathLibrary'"
$TEXTLIB  = "/Script/CoreUObject.Class'/Script/Engine.KismetTextLibrary'"
$STATICS  = "/Script/CoreUObject.Class'/Script/Engine.GameplayStatics'"

$script:nodes = $null
$script:counter = 0
$script:offX = 0
$script:offY = 0

function Reset-Graph($ox = 0, $oy = 0) {
  $script:nodes = [System.Collections.Generic.List[object]]::new(); $script:counter = 100
  $script:offX = $ox; $script:offY = $oy
}

function New-Node($class, [string[]]$props, $x, $y) {
  $script:counter++
  $short = $class.Split('.')[-1]
  $n = [pscustomobject]@{ Class = $class; Name = "${short}_$($script:counter)"; Props = $props; X = $x; Y = $y; Pins = [System.Collections.Generic.List[object]]::new() }
  $script:nodes.Add($n)
  return $n
}

function Add-Pin($node, $name, $dir, $cat, $sub = '', $obj = $null, $default = $null) {
  $p = [pscustomobject]@{ Id = [guid]::NewGuid().ToString('N').ToUpper(); Name = $name; Dir = $dir; Cat = $cat; Sub = $sub; Obj = $obj; Default = $default; Links = [System.Collections.Generic.List[string]]::new() }
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

function New-Call($parent, $func, [bool]$pure, $x, $y) {
  $props = @()
  if ($pure) { $props += 'bDefaultsToPureFunc=True' }
  $props += "FunctionReference=(MemberParent=`"$parent`",MemberName=`"$func`")"
  $n = New-Node '/Script/BlueprintGraph.K2Node_CallFunction' $props $x $y
  if (-not $pure) { Add-Exec $n }
  return $n
}

# ==, + and friends are K2Node_PromotableOperator in UE5; pasting them as plain calls drops their links.
function New-IntOperator($operation, $func, $outCat, $x, $y) {
  $props = "OperationName=`"$operation`"", 'bDefaultsToPureFunc=True', "FunctionReference=(MemberParent=`"$MATH`",MemberName=`"$func`")"
  $n = New-Node '/Script/BlueprintGraph.K2Node_PromotableOperator' $props $x $y
  Add-Pin $n 'A' 'in' 'int' '' $null '0'
  Add-Pin $n 'B' 'in' 'int' '' $null '0'
  Add-Pin $n 'ReturnValue' 'out' $outCat
  return $n
}

function New-IntEquals($value, $x, $y) {
  $n = New-IntOperator 'EqualEqual' 'EqualEqual_IntInt' 'bool' $x $y
  (Get-Pin $n 'B').Default = "$value"
  return $n
}

function Get-VarRef($name, $memberParent) {
  if ($memberParent) { return "VariableReference=(MemberParent=`"$memberParent`",MemberName=`"$name`")", 'SelfContextInfo=NotSelfContext' }
  return , "VariableReference=(MemberName=`"$name`",bSelfContext=True)"
}

function New-VarGet($name, $memberParent, $cat, $sub, $obj, $x, $y) {
  $n = New-Node '/Script/BlueprintGraph.K2Node_VariableGet' (Get-VarRef $name $memberParent) $x $y
  Add-Pin $n $name 'out' $cat $sub $obj
  if ($memberParent) { Add-Pin $n 'self' 'in' 'object' '' $memberParent }
  return $n
}

function New-VarSet($name, $memberParent, $cat, $sub, $obj, $x, $y) {
  $n = New-Node '/Script/BlueprintGraph.K2Node_VariableSet' (Get-VarRef $name $memberParent) $x $y
  Add-Exec $n
  Add-Pin $n $name 'in' $cat $sub $obj
  Add-Pin $n 'Output_Get' 'out' $cat $sub $obj
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

function New-CastToGameInstance([bool]$pure, $x, $y) {
  $props = @("TargetType=`"$GI_CLASS`"")
  if ($pure) { $props += 'bIsPureCast=True' }
  $n = New-Node '/Script/BlueprintGraph.K2Node_DynamicCast' $props $x $y
  if (-not $pure) { Add-Exec $n; Add-Pin $n 'CastFailed' 'out' 'exec' }
  Add-Pin $n 'Object' 'in' 'object' '' $OBJECT
  Add-Pin $n 'AsBP My Game Instance' 'out' 'object' '' $GI_CLASS
  Add-Pin $n 'bSuccess' 'out' 'bool'
  return $n
}

function New-GetGameInstance($x, $y) {
  $n = New-Call $STATICS 'GetGameInstance' $true $x $y
  Add-Pin $n 'ReturnValue' 'out' 'object' '' $GAMEINST
  return $n
}

function New-IntToText($x, $y) {
  $n = New-Call $TEXTLIB 'Conv_IntToText' $true $x $y
  Add-Pin $n 'Value' 'in' 'int' '' $null '0'
  Add-Pin $n 'ReturnValue' 'out' 'text'
  return $n
}

function New-SetText($x, $y) {
  $n = New-Call $TEXTBLK 'SetText' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $TEXTBLK
  Add-Pin $n 'InText' 'in' 'text'
  return $n
}

function New-SetVisibility($visibility, $x, $y) {
  $n = New-Call $WIDGET 'SetVisibility' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $WIDGET
  Add-Pin $n 'InVisibility' 'in' 'byte' '' $VIS $visibility
  return $n
}

function Format-Pin($p) {
  $obj = if ($p.Obj) { "`"$($p.Obj)`"" } else { 'None' }
  $s = "PinId=$($p.Id),PinName=`"$($p.Name)`","
  if ($p.Dir -eq 'out') { $s += 'Direction="EGPD_Output",' }
  $s += "PinType.PinCategory=`"$($p.Cat)`",PinType.PinSubCategory=`"$($p.Sub)`",PinType.PinSubCategoryObject=$obj,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,"
  if ($null -ne $p.Default) { $s += "DefaultValue=`"$($p.Default)`"," }
  if ($p.Links.Count) { $s += 'LinkedTo=(' + (($p.Links | ForEach-Object { "$_," }) -join '') + '),' }
  $s += 'PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,'
  return "   CustomProperties Pin ($s)"
}

function Format-Graph {
  $sb = [System.Text.StringBuilder]::new()
  foreach ($n in $script:nodes) {
    [void]$sb.AppendLine("Begin Object Class=$($n.Class) Name=`"$($n.Name)`"")
    foreach ($prop in $n.Props) { [void]$sb.AppendLine("   $prop") }
    [void]$sb.AppendLine("   NodePosX=$($n.X + $script:offX)")
    [void]$sb.AppendLine("   NodePosY=$($n.Y + $script:offY)")
    [void]$sb.AppendLine("   NodeGuid=$([guid]::NewGuid().ToString('N').ToUpper())")
    foreach ($p in $n.Pins) { [void]$sb.AppendLine((Format-Pin $p)) }
    [void]$sb.AppendLine('End Object')
  }
  return $sb.ToString()
}

function Save-Text($fileName, $text) {
  [IO.File]::WriteAllText((Join-Path $OutDir $fileName), $text, [Text.UTF8Encoding]::new($false))
}

# --- Helpers for reusing nodes copied out of the existing controller graph ------------
function Read-Blocks($path) {
  $text = [IO.File]::ReadAllText($path, [Text.Encoding]::UTF8)
  $map = [ordered]@{}
  foreach ($m in [regex]::Matches($text, '(?ms)^Begin Object Class=\S+ Name="(\w+)".*?^End Object\r?$')) { $map[$m.Groups[1].Value] = $m.Value.TrimEnd("`r") }
  return $map
}

function Get-LinkedNodes($block) {
  foreach ($m in [regex]::Matches($block, 'LinkedTo=\(([^)]*)\)')) {
    $m.Groups[1].Value -split ',' | Where-Object { $_ } | ForEach-Object { ($_ -split ' ')[0] }
  }
}

function Get-Section($blocks, $start) {
  $seen = [System.Collections.Generic.List[string]]::new(); $queue = [System.Collections.Generic.Queue[string]]::new()
  $queue.Enqueue($start)
  while ($queue.Count) {
    $name = $queue.Dequeue()
    if ($seen.Contains($name)) { continue }
    $seen.Add($name)
    foreach ($next in Get-LinkedNodes $blocks[$name]) { $queue.Enqueue($next) }
  }
  return $seen
}

function Get-ExportPinId($block, $pinName) {
  if ($block -match "PinId=(\w+),PinName=`"$([regex]::Escape($pinName))`"") { return $Matches[1] }
  throw "Pin $pinName not found"
}

function Set-ExportPin($block, $pinName, [string[]]$links, [bool]$append, $default = $null) {
  $lines = $block -split "`n"
  for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -notmatch "^\s*CustomProperties Pin \(PinId=\w+,PinName=`"$([regex]::Escape($pinName))`"") { continue }
    $line = $lines[$i]
    if ($null -ne $default) { $line = $line -replace '(?<![A-Za-z])DefaultValue="[^"]*"', "DefaultValue=`"$default`"" }
    if ($null -ne $links) {
      $existing = if ($append -and $line -match 'LinkedTo=\(([^)]*)\),') { $Matches[1] } else { '' }
      $line = $line -replace 'LinkedTo=\([^)]*\),', ''
      $all = $existing + (($links | ForEach-Object { "$_," }) -join '')
      if ($all) { $line = $line -replace 'PersistentGuid=', "LinkedTo=($all),PersistentGuid=" }
    }
    $lines[$i] = $line
    return ($lines -join "`n")
  }
  throw "Pin $pinName not found for patching"
}

function Assert-LinksResolve($text) {
  $names = [regex]::Matches($text, '(?m)^Begin Object Class=\S+ Name="(\w+)"') | ForEach-Object { $_.Groups[1].Value }
  foreach ($target in Get-LinkedNodes $text) { if ($names -notcontains $target) { throw "Dangling link to $target" } }
}

# --- 1. pa-zu: show the SE volume when the menu opens -------------------------------
Reset-Graph
$gi = New-GetGameInstance 0 160
$cast = New-CastToGameInstance $false 300 0
$seLevel = New-VarGet 'SeVolumeLevel' $GI_CLASS 'int' '' $null 650 160
$toText = New-IntToText 900 160
$seText = New-VarGet 'SeVolumeValueText' $null 'object' '' $TEXTBLK 900 260
$setText = New-SetText 1200 0
Connect $gi 'ReturnValue' $cast 'Object'
Connect $cast 'then' $setText 'execute'
Connect $cast 'AsBP My Game Instance' $seLevel 'self'
Connect $seLevel 'SeVolumeLevel' $toText 'Value'
Connect $toText 'ReturnValue' $setText 'InText'
Connect $seText 'SeVolumeValueText' $setText 'self'
Save-Text 'PauseMenu_1_pazu_Construct.txt' (Format-Graph)

if ($ControllerExport) {
$blocks = Read-Blocks $ControllerExport

# --- 2. Controller: up/down input, whole section (0 = BGM, 1 = SE, 2 = Quit) ----------
$keep = 'K2Node_EnhancedInputAction_1', 'K2Node_CallFunction_10', 'K2Node_PromotableOperator_0', 'K2Node_VariableGet_5', 'K2Node_CallFunction_11', 'K2Node_VariableSet_1'
Reset-Graph 3800 300
$menu = New-VarGet 'PauseMenuWidget' $null 'object' '' $PAZU 0 400
$selected = New-VarGet 'SelectedIndex' $null 'int' '' $null 0 200
$prevExec = $null
$firstBranch = $null
$rows = @(@{ Arrow = 'ArrowVolume'; Index = 0 }, @{ Arrow = 'ArrowSe'; Index = 1 }, @{ Arrow = 'ArrowQuit'; Index = 2 })
$x = 300
foreach ($row in $rows) {
  $arrow = New-VarGet $row.Arrow $PAZU 'object' '' $TEXTBLK ($x + 100) 450
  $equals = New-IntEquals $row.Index $x 200
  $branch = New-Branch ($x + 200) 0
  $show = New-SetVisibility 'Visible' ($x + 450) -100
  $hide = New-SetVisibility 'Hidden' ($x + 450) 150
  Connect $menu 'PauseMenuWidget' $arrow 'self'
  Connect $selected 'SelectedIndex' $equals 'A'
  Connect $equals 'ReturnValue' $branch 'Condition'
  Connect $branch 'then' $show 'execute'
  Connect $branch 'else' $hide 'execute'
  Connect $arrow $row.Arrow $show 'self'
  Connect $arrow $row.Arrow $hide 'self'
  if ($prevExec) { foreach ($prev in $prevExec) { Connect $prev 'then' $branch 'execute' } }
  if (-not $firstBranch) { $firstBranch = $branch }
  $prevExec = @($show, $hide)
  $x += 800
}
$setIndex = $blocks['K2Node_VariableSet_1']
(Get-Pin $firstBranch 'execute').Links.Add("K2Node_VariableSet_1 $(Get-ExportPinId $setIndex 'then')")
$setIndex = Set-ExportPin $setIndex 'then' @("$($firstBranch.Name) $((Get-Pin $firstBranch 'execute').Id)") $false
$clampIndex = Set-ExportPin $blocks['K2Node_CallFunction_11'] 'Max' $null $false '2'
$parts = foreach ($name in $keep) {
  switch ($name) { 'K2Node_VariableSet_1' { $setIndex } 'K2Node_CallFunction_11' { $clampIndex } default { $blocks[$name] } }
}
$text = ($parts -join "`n") + "`n" + (Format-Graph)
Assert-LinksResolve $text
Save-Text 'PauseMenu_2_Controller_Vertical.txt' $text

# --- 3. Controller: left/right input, whole section (existing BGM + new SE) ----------
$section = Get-Section $blocks 'K2Node_EnhancedInputAction_2'
Reset-Graph 2700 1900
$selected = New-VarGet 'SelectedIndex' $null 'int' '' $null 0 150
$isSeRow = New-IntEquals 1 200 150
$branch = New-Branch 450 0
$gi = New-GetGameInstance 450 250
$cast = New-CastToGameInstance $false 750 0
$round = New-Call $MATH 'Round' $true 750 350
Add-Pin $round 'A' 'in' 'real' 'double' $null '0.0'
Add-Pin $round 'ReturnValue' 'out' 'int'
$seLevel = New-VarGet 'SeVolumeLevel' $GI_CLASS 'int' '' $null 1050 250
$add = New-IntOperator 'Add' 'Add_IntInt' 'int' 1300 300
$clamp = New-Call $MATH 'Clamp' $true 1550 300
Add-Pin $clamp 'Value' 'in' 'int' '' $null '0'
Add-Pin $clamp 'Min' 'in' 'int' '' $null '0'
Add-Pin $clamp 'Max' 'in' 'int' '' $null '10'
Add-Pin $clamp 'ReturnValue' 'out' 'int'
$setLevel = New-VarSet 'SeVolumeLevel' $GI_CLASS 'int' '' $null 1850 0
$menu = New-VarGet 'PauseMenuWidget' $null 'object' '' $PAZU 1850 350
$seText = New-VarGet 'SeVolumeValueText' $PAZU 'object' '' $TEXTBLK 2100 350
$toText = New-IntToText 2150 200
$setText = New-SetText 2450 0
Connect $selected 'SelectedIndex' $isSeRow 'A'
Connect $isSeRow 'ReturnValue' $branch 'Condition'
Connect $branch 'then' $cast 'execute'
Connect $gi 'ReturnValue' $cast 'Object'
Connect $cast 'then' $setLevel 'execute'
Connect $cast 'AsBP My Game Instance' $seLevel 'self'
Connect $cast 'AsBP My Game Instance' $setLevel 'self'
Connect $round 'ReturnValue' $add 'A'
Connect $seLevel 'SeVolumeLevel' $add 'B'
Connect $add 'ReturnValue' $clamp 'Value'
Connect $clamp 'ReturnValue' $setLevel 'SeVolumeLevel'
Connect $setLevel 'then' $setText 'execute'
Connect $setLevel 'Output_Get' $toText 'Value'
Connect $toText 'ReturnValue' $setText 'InText'
Connect $menu 'PauseMenuWidget' $seText 'self'
Connect $seText 'SeVolumeValueText' $setText 'self'
# Wire the new SE branch into the existing nodes: BGM-row branch False -> SE branch, Action Value -> SE Round.
$bgmBranch = $blocks['K2Node_IfThenElse_3']
$inputEvent = $blocks['K2Node_EnhancedInputAction_2']
(Get-Pin $branch 'execute').Links.Add("K2Node_IfThenElse_3 $(Get-ExportPinId $bgmBranch 'else')")
(Get-Pin $round 'A').Links.Add("K2Node_EnhancedInputAction_2 $(Get-ExportPinId $inputEvent 'ActionValue')")
$bgmBranch = Set-ExportPin $bgmBranch 'else' @("$($branch.Name) $((Get-Pin $branch 'execute').Id)") $false
$inputEvent = Set-ExportPin $inputEvent 'ActionValue' @("$($round.Name) $((Get-Pin $round 'A').Id)") $true
$parts = foreach ($name in $section) {
  switch ($name) { 'K2Node_IfThenElse_3' { $bgmBranch } 'K2Node_EnhancedInputAction_2' { $inputEvent } default { $blocks[$name] } }
}
$text = ($parts -join "`n") + "`n" + (Format-Graph)
Assert-LinksResolve $text
Save-Text 'PauseMenu_3_Controller_Horizontal.txt' $text
"Horizontal section nodes: $($section -join ', ')"
}

# --- 4. Character: SE volume (0.001 - 1.0) for footsteps and the jump sound ---------
Reset-Graph
$gi = New-GetGameInstance 0 150
$cast = New-CastToGameInstance $true 250 150
$seLevel = New-VarGet 'SeVolumeLevel' $GI_CLASS 'int' '' $null 550 150
$toDouble = New-Call $MATH 'Conv_IntToDouble' $true 800 150
Add-Pin $toDouble 'InInt' 'in' 'int' '' $null '0'
Add-Pin $toDouble 'ReturnValue' 'out' 'real' 'double'
$divide = New-Call $MATH 'SafeDivide' $true 1050 150
Add-Pin $divide 'A' 'in' 'real' 'double' $null '0.0'
Add-Pin $divide 'B' 'in' 'real' 'double' $null '10.000000'
Add-Pin $divide 'ReturnValue' 'out' 'real' 'double'
$clamp = New-Call $MATH 'FClamp' $true 1300 150
Add-Pin $clamp 'Value' 'in' 'real' 'double' $null '0.0'
Add-Pin $clamp 'Min' 'in' 'real' 'double' $null '0.001000'
Add-Pin $clamp 'Max' 'in' 'real' 'double' $null '1.000000'
Add-Pin $clamp 'ReturnValue' 'out' 'real' 'double'
$footsteps = New-VarGet '歩く' $null 'object' '' $AUDIO 1300 0
$setVolume = New-Call $AUDIO 'SetVolumeMultiplier' $false 1600 0
Add-Pin $setVolume 'self' 'in' 'object' '' $AUDIO
Add-Pin $setVolume 'NewVolumeMultiplier' 'in' 'real' 'float' $null '1.0'
Connect $gi 'ReturnValue' $cast 'Object'
Connect $cast 'AsBP My Game Instance' $seLevel 'self'
Connect $seLevel 'SeVolumeLevel' $toDouble 'InInt'
Connect $toDouble 'ReturnValue' $divide 'A'
Connect $divide 'ReturnValue' $clamp 'Value'
Connect $clamp 'ReturnValue' $setVolume 'NewVolumeMultiplier'
Connect $footsteps '歩く' $setVolume 'self'
Save-Text 'PauseMenu_4_Character_SeVolume.txt' (Format-Graph)

"Generated into $OutDir"
