param([string]$OutDir)
# Generates Ctrl+V-pasteable nodes for BP_ThirdPersonCharacter1: on the second jump, play AM_DoubleJump_Handmade.
# Hooked by hand to the free exec output at the end of the OnJumped chain, the jump effect's Set Life Span.

$helperFile = (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_height_bgm.ps1')
$helpers = Get-Content -LiteralPath $helperFile -Encoding UTF8 | Select-Object -Skip 3 -First 124
. ([ScriptBlock]::Create(($helpers -join "`n")))
# Stay clear of the node names already in the character graph.
$script:counter = 950

$MONTAGE_CLASS = "/Script/CoreUObject.Class'/Script/Engine.AnimMontage'"
$MONTAGE = '/Game/ThirdPerson/Blueprints/Plaey/Anim/AM_DoubleJump_Handmade.AM_DoubleJump_Handmade'

$x = 6400; $y = 1088
# JumpCurrentCount is already counted up when OnJumped fires: 2 = the double jump.
$count = New-VarGet 'JumpCurrentCount' $null 'int' '' $null ($x - 250) ($y + 200)
$isDouble = New-Operator 'GreaterEqual' 'GreaterEqual_IntInt' 'int' '' 'bool' $x ($y + 200)
(Get-Pin $isDouble 'B').Default = '2'
$branch = New-Branch ($x + 250) $y
Connect $count 'JumpCurrentCount' $isDouble 'A'
Connect $isDouble 'ReturnValue' $branch 'Condition'
$play = New-Call $null 'PlayAnimMontage' $false ($x + 550) $y
Add-Pin $play 'AnimMontage' 'in' 'object' '' $MONTAGE_CLASS
Add-Pin $play 'InPlayRate' 'in' 'real' 'float' $null '1.000000'
Add-Pin $play 'StartSectionName' 'in' 'name' '' $null 'None'
Add-Pin $play 'ReturnValue' 'out' 'real' 'float'
Connect $branch 'then' $play 'execute'

$sb = [System.Text.StringBuilder]::new()
foreach ($n in $script:nodes) {
  [void]$sb.AppendLine("Begin Object Class=$($n.Class) Name=`"$($n.Name)`"")
  foreach ($prop in $n.Props) { [void]$sb.AppendLine("   $prop") }
  [void]$sb.AppendLine("   NodePosX=$($n.X)")
  [void]$sb.AppendLine("   NodePosY=$($n.Y)")
  [void]$sb.AppendLine("   NodeGuid=$([guid]::NewGuid().ToString('N').ToUpper())")
  foreach ($p in $n.Pins) {
    $line = Format-Pin $p
    if ($p.Name -eq 'AnimMontage') { $line = $line -replace 'PersistentGuid=', "DefaultObject=`"$MONTAGE`",PersistentGuid=" }
    [void]$sb.AppendLine($line)
  }
  [void]$sb.AppendLine('End Object')
}
$text = $sb.ToString()
if ($text.Contains('@{')) { throw 'A node object leaked into a pin or reference (variable name collision)' }
[IO.File]::WriteAllText((Join-Path $OutDir 'DoubleJumpMontage_Character.txt'), $text, [Text.UTF8Encoding]::new($false))
"Generated $($script:nodes.Count) nodes"
