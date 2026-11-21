# Achievements step 5b (2026-11-21): the pause menu gets a 実績 row between SE and ゲームをやめる.
#   rows by SelectedIndex: 0 音量, 1 SE, 2 実績 (new), 3 ゲームをやめる (was 2)
# Input: the whole BP_ThirdPersonPlayerController event graph as copied by the user (Ctrl+A, Ctrl+C), saved as
# Scripts/bp_export/controller_1121.txt. Output: Scripts/PauseMenu_Achievements_Controller.txt, that same graph with
#   - up/down: both Clamp Max 2 -> 3; a new arrow step for pa-zu's ArrowAchievements (row 2) between SE and Quit;
#     Quit's arrow now on row 3
#   - confirm: Quit on row 3; row 2 creates WBP_AchievementList (RestoreGameInput = true), adds it over the menu
#     (ZOrder 60) and hands it the keys (Set Input Mode UI Only, focus on the list, flush input), so the game's menu
#     keys stop while it is open. The list's 戻る puts Game Only back (Scripts/WBP_AchievementList_BackRestore.txt).
# The user replaces the whole event graph (Ctrl+A, Delete, Ctrl+V), so nothing outside these two sections changes.
# Also writes Scripts/WBP_AchievementList_BackRestore.txt (3 nodes, wired after the list's Remove from Parent).
param([string]$Export = (Join-Path $PSScriptRoot '..\bp_export\controller_1121.txt'))

$OutDir = Split-Path -Parent $PSScriptRoot
# The node builders and export helpers of gen_pause_menu.ps1 (its lines 4-226).
$helpers = (Get-Content (Join-Path $PSScriptRoot 'gen_pause_menu.ps1') -Encoding UTF8)[3..225] -join "`n"
Invoke-Expression $helpers

$LIST_CLASS = "/Script/UMGEditor.WidgetBlueprintGeneratedClass'/Game/UI/WBP_AchievementList.WBP_AchievementList_C'"
$IMAGE = "/Script/CoreUObject.Class'/Script/UMG.Image'"
$USERWIDGET = "/Script/CoreUObject.Class'/Script/UMG.UserWidget'"
$CONTROLLER = "/Script/CoreUObject.Class'/Script/Engine.PlayerController'"
$WIDGETLIB = "/Script/CoreUObject.Class'/Script/UMG.WidgetBlueprintLibrary'"

$blocks = Read-Blocks $Export
$order = @($blocks.Keys)
foreach ($need in 'K2Node_CallFunction_11', 'K2Node_CallFunction_909', 'K2Node_PromotableOperator_114', 'K2Node_CallFunction_14',
                  'K2Node_CallFunction_40', 'K2Node_IfThenElse_115', 'K2Node_VariableGet_101', 'K2Node_VariableGet_9',
                  'K2Node_PromotableOperator_4', 'K2Node_IfThenElse_5', 'K2Node_VariableGet_10') {
  if (-not $blocks.Contains($need)) { throw "The export has no $need; the controller graph changed, look again" }
}
foreach ($check in @(@('K2Node_CallFunction_11', 'Max', '2'), @('K2Node_CallFunction_909', 'Max', '2'),
                     @('K2Node_PromotableOperator_114', 'B', '2'), @('K2Node_PromotableOperator_4', 'B', '2'))) {
  if ($blocks[$check[0]] -notmatch "PinName=`"$($check[1])`"[^\r\n]*?DefaultValue=`"$($check[2])`"") { throw "$($check[0]).$($check[1]) is not $($check[2]); already patched?" }
}

Reset-Graph
$script:counter = 3000   # clear of every node name in the export

# ----- up/down: the 実績 arrow (row 2) between the SE step and the Quit step -----
$arrow = New-VarGet 'ArrowAchievements' $PAZU 'object' '' $IMAGE 8300 2950
$isRow = New-IntEquals 2 8300 2800
$branch = New-Branch 8450 2700
$show = New-SetVisibility 'Visible' 8750 2650
$hide = New-SetVisibility 'Hidden' 8750 2900
Connect $isRow 'ReturnValue' $branch 'Condition'
Connect $branch 'then' $show 'execute'
Connect $branch 'else' $hide 'execute'
Connect $arrow 'ArrowAchievements' $show 'self'
Connect $arrow 'ArrowAchievements' $hide 'self'
(Get-Pin $arrow 'self').Links.Add("K2Node_VariableGet_101 $(Get-ExportPinId $blocks['K2Node_VariableGet_101'] 'PauseMenuWidget')")
(Get-Pin $isRow 'A').Links.Add("K2Node_VariableGet_9 $(Get-ExportPinId $blocks['K2Node_VariableGet_9'] 'SelectedIndex')")
$quitBranch = 'K2Node_IfThenElse_115'
$quitIn = Get-ExportPinId $blocks[$quitBranch] 'execute'
(Get-Pin $show 'then').Links.Add("$quitBranch $quitIn")
(Get-Pin $hide 'then').Links.Add("$quitBranch $quitIn")
$branchIn = "$($branch.Name) $((Get-Pin $branch 'execute').Id)"
foreach ($se in 'K2Node_CallFunction_14', 'K2Node_CallFunction_40') {
  (Get-Pin $branch 'execute').Links.Add("$se $(Get-ExportPinId $blocks[$se] 'then')")
  $blocks[$se] = Set-ExportPin $blocks[$se] 'then' @($branchIn) $false
}
$blocks[$quitBranch] = Set-ExportPin $blocks[$quitBranch] 'execute' @("$($show.Name) $((Get-Pin $show 'then').Id)", "$($hide.Name) $((Get-Pin $hide 'then').Id)") $false
$blocks['K2Node_VariableGet_101'] = Set-ExportPin $blocks['K2Node_VariableGet_101'] 'PauseMenuWidget' @("$($arrow.Name) $((Get-Pin $arrow 'self').Id)") $true
$blocks['K2Node_VariableGet_9'] = Set-ExportPin $blocks['K2Node_VariableGet_9'] 'SelectedIndex' @("$($isRow.Name) $((Get-Pin $isRow 'A').Id)") $true
$blocks['K2Node_CallFunction_11'] = Set-ExportPin $blocks['K2Node_CallFunction_11'] 'Max' $null $false '3'
$blocks['K2Node_CallFunction_909'] = Set-ExportPin $blocks['K2Node_CallFunction_909'] 'Max' $null $false '3'
$blocks['K2Node_PromotableOperator_114'] = Set-ExportPin $blocks['K2Node_PromotableOperator_114'] 'B' $null $false '3'

# ----- confirm: Quit on row 3, the list on row 2 -----
$blocks['K2Node_PromotableOperator_4'] = Set-ExportPin $blocks['K2Node_PromotableOperator_4'] 'B' $null $false '3'
$isList = New-IntEquals 2 2816 2150
$listBranch = New-Branch 3072 2000
$self = New-Node '/Script/BlueprintGraph.K2Node_Self' @() 3072 2300
Add-Pin $self 'self' 'out' 'object' 'self'
$create = New-Node '/Script/UMGEditor.K2Node_CreateWidget' @() 3350 2000
Add-Exec $create
Add-Pin $create 'Class' 'in' 'class' '' $USERWIDGET
(Get-Pin $create 'Class').Default = $null
Add-Pin $create 'OwningPlayer' 'in' 'object' '' $CONTROLLER
Add-Pin $create 'ReturnValue' 'out' 'object' '' $LIST_CLASS
$restore = New-VarSet 'RestoreGameInput' $LIST_CLASS 'bool' '' $null 3700 2000
(Get-Pin $restore 'RestoreGameInput').Default = 'true'
$add = New-Call $USERWIDGET 'AddToViewport' $false 4000 2000
Add-Pin $add 'self' 'in' 'object' '' $USERWIDGET
Add-Pin $add 'ZOrder' 'in' 'int' '' $null '60'
$uiOnly = New-Call $WIDGETLIB 'SetInputMode_UIOnlyEx' $false 4300 2000
Add-Pin $uiOnly 'PlayerController' 'in' 'object' '' $CONTROLLER
Add-Pin $uiOnly 'InWidgetToFocus' 'in' 'object' '' "/Script/CoreUObject.Class'/Script/UMG.Widget'"
Add-Pin $uiOnly 'bFlushInput' 'in' 'bool' '' $null 'true'
Connect $isList 'ReturnValue' $listBranch 'Condition'
Connect $listBranch 'then' $create 'execute'
Connect $self 'self' $create 'OwningPlayer'
Connect $self 'self' $uiOnly 'PlayerController'
Connect $create 'then' $restore 'execute'
Connect $create 'ReturnValue' $restore 'self'
Connect $create 'ReturnValue' $add 'self'
Connect $create 'ReturnValue' $uiOnly 'InWidgetToFocus'
Connect $restore 'then' $add 'execute'
Connect $add 'then' $uiOnly 'execute'
$quitCheck = 'K2Node_IfThenElse_5'
(Get-Pin $listBranch 'execute').Links.Add("$quitCheck $(Get-ExportPinId $blocks[$quitCheck] 'else')")
$blocks[$quitCheck] = Set-ExportPin $blocks[$quitCheck] 'else' @("$($listBranch.Name) $((Get-Pin $listBranch 'execute').Id)") $false
(Get-Pin $isList 'A').Links.Add("K2Node_VariableGet_10 $(Get-ExportPinId $blocks['K2Node_VariableGet_10'] 'SelectedIndex')")
$blocks['K2Node_VariableGet_10'] = Set-ExportPin $blocks['K2Node_VariableGet_10'] 'SelectedIndex' @("$($isList.Name) $((Get-Pin $isList 'A').Id)") $true

# Format-Graph writes no DefaultObject; the class pin needs one.
$new = (Format-Graph) -replace "(PinName=`"Class`",PinType\.PinCategory=`"class`"[^\r\n]*?PinType\.bSerializeAsSinglePrecisionFloat=False,)", "`$1DefaultObject=`"$LIST_CLASS`","
$text = (($order | ForEach-Object { $blocks[$_] }) -join "`n") + "`n" + $new
Assert-LinksResolve $text
Save-Text 'PauseMenu_Achievements_Controller.txt' $text
"Controller graph: $($order.Count) nodes + $($script:nodes.Count) new"

# ----- the list's 戻る: back to Game Only when the pause menu opened it -----
Reset-Graph 700 -800
$flag = New-VarGet 'RestoreGameInput' $null 'bool' '' $null 0 150
$check = New-Branch 0 0
$owner = New-Call $USERWIDGET 'GetOwningPlayer' $true 250 150
Add-Pin $owner 'ReturnValue' 'out' 'object' '' $CONTROLLER
$gameOnly = New-Call $WIDGETLIB 'SetInputMode_GameOnly' $false 500 0
Add-Pin $gameOnly 'PlayerController' 'in' 'object' '' $CONTROLLER
Add-Pin $gameOnly 'bFlushInput' 'in' 'bool' '' $null 'true'
Connect $flag 'RestoreGameInput' $check 'Condition'
Connect $check 'then' $gameOnly 'execute'
Connect $owner 'ReturnValue' $gameOnly 'PlayerController'
Save-Text 'WBP_AchievementList_BackRestore.txt' (Format-Graph)
"List back restore: $($script:nodes.Count) nodes"
