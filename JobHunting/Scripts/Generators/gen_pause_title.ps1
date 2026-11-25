# The pause menu gets a タイトルに戻る row (2026-11-25) between 実績 and ゲームをやめる.
#   rows by SelectedIndex: 0 音量, 1 SE, 2 実績, 3 タイトルに戻る (new), 4 ゲームをやめる (was 3)
# pa-zu's widgets came from Scripts/PauseMenu_pazu_Canvas.txt (HorizontalBox_Title + ArrowTitle).
# Input: the whole BP_ThirdPersonPlayerController event graph as copied by the user (Ctrl+A, Ctrl+C) after the 実績 row
# (gen_pause_achievements.ps1), saved as Scripts/bp_export/controller_1125.txt. Output:
# Scripts/PauseMenu_Title_Controller.txt, that same graph with
#   - up/down: both Clamp Max 3 -> 4; a new arrow step for ArrowTitle (row 3) between the 実績 step and the Quit step;
#     Quit's arrow now on row 4
#   - confirm: Quit on row 4; row 3 (after the 実績 check's False): unpause, open LV_Title
# The user replaces the whole event graph (Ctrl+A, Delete, Ctrl+V).
param([string]$Export = (Join-Path $PSScriptRoot '..\bp_export\controller_1125.txt'))

$OutDir = Split-Path -Parent $PSScriptRoot
$helpers = (Get-Content (Join-Path $PSScriptRoot 'gen_pause_menu.ps1') -Encoding UTF8)[3..225] -join "`n"
Invoke-Expression $helpers
$IMAGE = "/Script/CoreUObject.Class'/Script/UMG.Image'"
$GAMEPLAY = "/Script/CoreUObject.Class'/Script/Engine.GameplayStatics'"

$blocks = Read-Blocks $Export
$order = @($blocks.Keys)
foreach ($need in 'K2Node_CallFunction_11', 'K2Node_CallFunction_909', 'K2Node_PromotableOperator_114', 'K2Node_CallFunction_3004',
                  'K2Node_CallFunction_3005', 'K2Node_IfThenElse_115', 'K2Node_VariableGet_101', 'K2Node_VariableGet_9',
                  'K2Node_PromotableOperator_4', 'K2Node_IfThenElse_3007', 'K2Node_VariableGet_10') {
  if (-not $blocks.Contains($need)) { throw "The export has no $need; the controller graph changed, look again" }
}
foreach ($check in @(@('K2Node_CallFunction_11', 'Max', '3'), @('K2Node_CallFunction_909', 'Max', '3'),
                     @('K2Node_PromotableOperator_114', 'B', '3'), @('K2Node_PromotableOperator_4', 'B', '3'))) {
  if ($blocks[$check[0]] -notmatch "PinName=`"$($check[1])`"[^\r\n]*?DefaultValue=`"$($check[2])`"") { throw "$($check[0]).$($check[1]) is not $($check[2]); already patched?" }
}

Reset-Graph
$script:counter = 3100   # clear of every node name in the export (the 実績 patch used 3000..3020)

# ----- up/down: the タイトルに戻る arrow (row 3) between the 実績 step and the Quit step -----
$arrow = New-VarGet 'ArrowTitle' $PAZU 'object' '' $IMAGE 7000 3250
$isRow = New-IntEquals 3 7000 3100
$branch = New-Branch 7150 3000
$show = New-SetVisibility 'Visible' 7450 2950
$hide = New-SetVisibility 'Hidden' 7450 3200
Connect $isRow 'ReturnValue' $branch 'Condition'
Connect $branch 'then' $show 'execute'
Connect $branch 'else' $hide 'execute'
Connect $arrow 'ArrowTitle' $show 'self'
Connect $arrow 'ArrowTitle' $hide 'self'
(Get-Pin $arrow 'self').Links.Add("K2Node_VariableGet_101 $(Get-ExportPinId $blocks['K2Node_VariableGet_101'] 'PauseMenuWidget')")
(Get-Pin $isRow 'A').Links.Add("K2Node_VariableGet_9 $(Get-ExportPinId $blocks['K2Node_VariableGet_9'] 'SelectedIndex')")
$quitBranch = 'K2Node_IfThenElse_115'
$quitIn = Get-ExportPinId $blocks[$quitBranch] 'execute'
(Get-Pin $show 'then').Links.Add("$quitBranch $quitIn")
(Get-Pin $hide 'then').Links.Add("$quitBranch $quitIn")
$branchIn = "$($branch.Name) $((Get-Pin $branch 'execute').Id)"
foreach ($step in 'K2Node_CallFunction_3004', 'K2Node_CallFunction_3005') {
  (Get-Pin $branch 'execute').Links.Add("$step $(Get-ExportPinId $blocks[$step] 'then')")
  $blocks[$step] = Set-ExportPin $blocks[$step] 'then' @($branchIn) $false
}
$blocks[$quitBranch] = Set-ExportPin $blocks[$quitBranch] 'execute' @("$($show.Name) $((Get-Pin $show 'then').Id)", "$($hide.Name) $((Get-Pin $hide 'then').Id)") $false
$blocks['K2Node_VariableGet_101'] = Set-ExportPin $blocks['K2Node_VariableGet_101'] 'PauseMenuWidget' @("$($arrow.Name) $((Get-Pin $arrow 'self').Id)") $true
$blocks['K2Node_VariableGet_9'] = Set-ExportPin $blocks['K2Node_VariableGet_9'] 'SelectedIndex' @("$($isRow.Name) $((Get-Pin $isRow 'A').Id)") $true
$blocks['K2Node_CallFunction_11'] = Set-ExportPin $blocks['K2Node_CallFunction_11'] 'Max' $null $false '4'
$blocks['K2Node_CallFunction_909'] = Set-ExportPin $blocks['K2Node_CallFunction_909'] 'Max' $null $false '4'
$blocks['K2Node_PromotableOperator_114'] = Set-ExportPin $blocks['K2Node_PromotableOperator_114'] 'B' $null $false '4'

# ----- confirm: Quit on row 4; row 3 -> unpause, the title -----
$blocks['K2Node_PromotableOperator_4'] = Set-ExportPin $blocks['K2Node_PromotableOperator_4'] 'B' $null $false '4'
$isTitle = New-IntEquals 3 3350 2450
$titleBranch = New-Branch 3600 2300
$unpause = New-Call $GAMEPLAY 'SetGamePaused' $false 3900 2300
Add-Pin $unpause 'bPaused' 'in' 'bool' '' $null 'false'
Add-Pin $unpause 'ReturnValue' 'out' 'bool'
$open = New-Call $GAMEPLAY 'OpenLevel' $false 4200 2300
Add-Pin $open 'LevelName' 'in' 'name' '' $null 'LV_Title'
Add-Pin $open 'bAbsolute' 'in' 'bool' '' $null 'true'
Add-Pin $open 'Options' 'in' 'string' '' $null ''
Connect $isTitle 'ReturnValue' $titleBranch 'Condition'
Connect $titleBranch 'then' $unpause 'execute'
Connect $unpause 'then' $open 'execute'
$listCheck = 'K2Node_IfThenElse_3007'
(Get-Pin $titleBranch 'execute').Links.Add("$listCheck $(Get-ExportPinId $blocks[$listCheck] 'else')")
$blocks[$listCheck] = Set-ExportPin $blocks[$listCheck] 'else' @("$($titleBranch.Name) $((Get-Pin $titleBranch 'execute').Id)") $false
(Get-Pin $isTitle 'A').Links.Add("K2Node_VariableGet_10 $(Get-ExportPinId $blocks['K2Node_VariableGet_10'] 'SelectedIndex')")
$blocks['K2Node_VariableGet_10'] = Set-ExportPin $blocks['K2Node_VariableGet_10'] 'SelectedIndex' @("$($isTitle.Name) $((Get-Pin $isTitle 'A').Id)") $true

$text = (($order | ForEach-Object { $blocks[$_] }) -join "`n") + "`n" + (Format-Graph)
Assert-LinksResolve $text
Save-Text 'PauseMenu_Title_Controller.txt' $text
"Controller graph: $($order.Count) nodes + $($script:nodes.Count) new"
