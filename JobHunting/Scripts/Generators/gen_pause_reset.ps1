# The pause menu gets a リセット row (2026-11-25) between 実績 and タイトルに戻る.
#   rows by SelectedIndex: 0 音量, 1 SE, 2 実績, 3 リセット (new), 4 タイトルに戻る (was 3), 5 ゲームをやめる (was 4)
# pa-zu's widgets: Scripts/PauseMenu_pazu_Canvas.txt (HorizontalBox_Reset + ArrowReset). The reset itself is the game
# instance's ResetStage (gen_stage_reset.ps1).
# Input: Scripts/PauseMenu_Title_Controller.txt (gen_pause_title.ps1's output, the whole controller event graph).
# Output: Scripts/PauseMenu_Reset_Controller.txt, that graph with
#   - up/down: both Clamp Max 4 -> 5; a new arrow step for ArrowReset (row 3) between the 実績 step and the タイトル step;
#     the タイトル arrow on row 4, Quit's on row 5
#   - confirm: Quit on row 5; タイトル on row 4 (and it clears GI SnapshotLevel, so a new game from the title snapshots
#     its first stage again); row 3 -> GI ResetStage
# The user replaces the whole event graph (Ctrl+A, Delete, Ctrl+V).
param([string]$Export = (Join-Path $PSScriptRoot '..\PauseMenu_Title_Controller.txt'))

$OutDir = Split-Path -Parent $PSScriptRoot
$helpers = (Get-Content (Join-Path $PSScriptRoot 'gen_pause_menu.ps1') -Encoding UTF8)[3..225] -join "`n"
Invoke-Expression $helpers
$IMAGE = "/Script/CoreUObject.Class'/Script/UMG.Image'"

$blocks = Read-Blocks $Export
$order = @($blocks.Keys)
foreach ($check in @(@('K2Node_CallFunction_11', 'Max', '4'), @('K2Node_CallFunction_909', 'Max', '4'),
                     @('K2Node_PromotableOperator_114', 'B', '4'), @('K2Node_PromotableOperator_4', 'B', '4'),
                     @('K2Node_PromotableOperator_3102', 'B', '3'), @('K2Node_PromotableOperator_3106', 'B', '3'))) {
  if (-not $blocks.Contains($check[0])) { throw "No $($check[0]): the title patch's output changed" }
  if ($blocks[$check[0]] -notmatch "PinName=`"$($check[1])`"[^\r\n]*?DefaultValue=`"$($check[2])`"") { throw "$($check[0]).$($check[1]) is not $($check[2]); already patched?" }
}

Reset-Graph
$script:counter = 3200

# ----- up/down: the リセット arrow (row 3) between the 実績 step and the タイトル step -----
$arrow = New-VarGet 'ArrowReset' $PAZU 'object' '' $IMAGE 6800 3550
$isRow = New-IntEquals 3 6800 3400
$branch = New-Branch 6950 3300
$show = New-SetVisibility 'Visible' 7250 3250
$hide = New-SetVisibility 'Hidden' 7250 3500
Connect $isRow 'ReturnValue' $branch 'Condition'
Connect $branch 'then' $show 'execute'
Connect $branch 'else' $hide 'execute'
Connect $arrow 'ArrowReset' $show 'self'
Connect $arrow 'ArrowReset' $hide 'self'
(Get-Pin $arrow 'self').Links.Add("K2Node_VariableGet_101 $(Get-ExportPinId $blocks['K2Node_VariableGet_101'] 'PauseMenuWidget')")
(Get-Pin $isRow 'A').Links.Add("K2Node_VariableGet_9 $(Get-ExportPinId $blocks['K2Node_VariableGet_9'] 'SelectedIndex')")
$titleStep = 'K2Node_IfThenElse_3103'
$titleIn = Get-ExportPinId $blocks[$titleStep] 'execute'
(Get-Pin $show 'then').Links.Add("$titleStep $titleIn")
(Get-Pin $hide 'then').Links.Add("$titleStep $titleIn")
$branchIn = "$($branch.Name) $((Get-Pin $branch 'execute').Id)"
foreach ($step in 'K2Node_CallFunction_3004', 'K2Node_CallFunction_3005') {
  (Get-Pin $branch 'execute').Links.Add("$step $(Get-ExportPinId $blocks[$step] 'then')")
  $blocks[$step] = Set-ExportPin $blocks[$step] 'then' @($branchIn) $false
}
$blocks[$titleStep] = Set-ExportPin $blocks[$titleStep] 'execute' @("$($show.Name) $((Get-Pin $show 'then').Id)", "$($hide.Name) $((Get-Pin $hide 'then').Id)") $false
$blocks['K2Node_VariableGet_101'] = Set-ExportPin $blocks['K2Node_VariableGet_101'] 'PauseMenuWidget' @("$($arrow.Name) $((Get-Pin $arrow 'self').Id)") $true
$blocks['K2Node_VariableGet_9'] = Set-ExportPin $blocks['K2Node_VariableGet_9'] 'SelectedIndex' @("$($isRow.Name) $((Get-Pin $isRow 'A').Id)") $true
$blocks['K2Node_CallFunction_11'] = Set-ExportPin $blocks['K2Node_CallFunction_11'] 'Max' $null $false '5'
$blocks['K2Node_CallFunction_909'] = Set-ExportPin $blocks['K2Node_CallFunction_909'] 'Max' $null $false '5'
$blocks['K2Node_PromotableOperator_3102'] = Set-ExportPin $blocks['K2Node_PromotableOperator_3102'] 'B' $null $false '4'
$blocks['K2Node_PromotableOperator_114'] = Set-ExportPin $blocks['K2Node_PromotableOperator_114'] 'B' $null $false '5'

# ----- confirm: Quit row 5, タイトル row 4, リセット row 3 -----
$blocks['K2Node_PromotableOperator_4'] = Set-ExportPin $blocks['K2Node_PromotableOperator_4'] 'B' $null $false '5'
$blocks['K2Node_PromotableOperator_3106'] = Set-ExportPin $blocks['K2Node_PromotableOperator_3106'] 'B' $null $false '4'
$isReset = New-IntEquals 3 3350 2750
$resetBranch = New-Branch 3600 2600
$gi = New-GetGameInstance 3700 2850
$cast = New-CastToGameInstance $false 3950 2600
$call = New-Call $GI_CLASS 'ResetStage' $false 4300 2600
Add-Pin $call 'self' 'in' 'object' '' $GI_CLASS
Connect $isReset 'ReturnValue' $resetBranch 'Condition'
Connect $resetBranch 'then' $cast 'execute'
Connect $gi 'ReturnValue' $cast 'Object'
Connect $cast 'then' $call 'execute'
Connect $cast 'AsBP My Game Instance' $call 'self'
$listCheck = 'K2Node_IfThenElse_3007'
$titleBranch = 'K2Node_IfThenElse_3107'
(Get-Pin $resetBranch 'execute').Links.Add("$listCheck $(Get-ExportPinId $blocks[$listCheck] 'else')")
$blocks[$listCheck] = Set-ExportPin $blocks[$listCheck] 'else' @("$($resetBranch.Name) $((Get-Pin $resetBranch 'execute').Id)") $false
(Get-Pin $resetBranch 'else').Links.Add("$titleBranch $(Get-ExportPinId $blocks[$titleBranch] 'execute')")
$blocks[$titleBranch] = Set-ExportPin $blocks[$titleBranch] 'execute' @("$($resetBranch.Name) $((Get-Pin $resetBranch 'else').Id)") $false
(Get-Pin $isReset 'A').Links.Add("K2Node_VariableGet_10 $(Get-ExportPinId $blocks['K2Node_VariableGet_10'] 'SelectedIndex')")
$blocks['K2Node_VariableGet_10'] = Set-ExportPin $blocks['K2Node_VariableGet_10'] 'SelectedIndex' @("$($isReset.Name) $((Get-Pin $isReset 'A').Id)") $true
# タイトル: clear SnapshotLevel first (between the タイトル branch's True and the unpause)
$unpauseNode = 'K2Node_CallFunction_3108'
$gi2 = New-GetGameInstance 3900 2150
$cast2 = New-CastToGameInstance $false 4100 1950
$clear = New-VarSet 'SnapshotLevel' $GI_CLASS 'name' '' $null 4450 1950
(Get-Pin $clear 'SnapshotLevel').Default = 'None'
Connect $gi2 'ReturnValue' $cast2 'Object'
Connect $cast2 'then' $clear 'execute'
Connect $cast2 'AsBP My Game Instance' $clear 'self'
(Get-Pin $cast2 'execute').Links.Add("$titleBranch $(Get-ExportPinId $blocks[$titleBranch] 'then')")
$blocks[$titleBranch] = Set-ExportPin $blocks[$titleBranch] 'then' @("$($cast2.Name) $((Get-Pin $cast2 'execute').Id)") $false
(Get-Pin $clear 'then').Links.Add("$unpauseNode $(Get-ExportPinId $blocks[$unpauseNode] 'execute')")
$blocks[$unpauseNode] = Set-ExportPin $blocks[$unpauseNode] 'execute' @("$($clear.Name) $((Get-Pin $clear 'then').Id)") $false

$text = (($order | ForEach-Object { $blocks[$_] }) -join "`n") + "`n" + (Format-Graph)
Assert-LinksResolve $text
Save-Text 'PauseMenu_Reset_Controller.txt' $text
"Controller graph: $($order.Count) nodes + $($script:nodes.Count) new"
