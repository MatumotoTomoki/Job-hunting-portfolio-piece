param([string]$OutDir)
# Paste text for coyote time on BP_ThirdPersonCharacter1 (variables from setup_coyote_time.py):
#   On Movement Mode Changed: now falling with no upward speed (walked off an edge, or the floor went away - not a jump
#   or a launch) -> CoyoteReady, LeftGroundAt = now. Any other change (a jump, landing, ...) -> not CoyoteReady.
#   TryCoyoteJump (custom event): falling, CoyoteReady and within CoyoteTime of leaving the ground -> CoyoteReady off
#   and the movement put back to Walking for a moment, so the Jump called right after it jumps as from the ground
#   (a normal first jump: the jump count, the double jump and the jump effects work as ever).
#   A "Try Coyote Jump" call node comes with it: put it between IA_Jump's Started and Jump.
if (-not $OutDir) { throw 'OutDir is required' }
$OutDir = [IO.Path]::GetFullPath($OutDir)
$helperFile = (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_height_bgm.ps1')
$helpers = Get-Content -LiteralPath $helperFile -Encoding UTF8 | Select-Object -Skip 3 -First 124
. ([ScriptBlock]::Create(($helpers -join "`n")))
# Above the numbers already in the character graph (the ledge grab went from _1100).
$script:counter = 1400

$CHARACTER_CLASS = "/Script/CoreUObject.Class'/Script/Engine.Character'"
$MOVEMENT_CLASS = "/Script/CoreUObject.Class'/Script/Engine.CharacterMovementComponent'"
$NAV_MOVE = "/Script/CoreUObject.Class'/Script/Engine.NavMovementInterface'"
$MOVEMENT_MODE = "/Script/CoreUObject.Enum'/Script/Engine.EMovementMode'"

function Movement([double]$x, [double]$y) { New-VarGet 'CharacterMovement' $null 'object' '' $MOVEMENT_CLASS $x $y }
function Falling([double]$x, [double]$y) {
  $n = New-Call $NAV_MOVE 'IsFalling' $true $x $y
  Add-Pin $n 'self' 'in' 'object' '' $MOVEMENT_CLASS
  Add-Pin $n 'ReturnValue' 'out' 'bool'
  Connect (Movement ($x - 220) ($y + 80)) 'CharacterMovement' $n 'self'
  return $n
}
function Now([double]$x, [double]$y) {
  $n = New-Call $SYSTEM 'GetGameTimeInSeconds' $true $x $y
  Add-Pin $n 'ReturnValue' 'out' 'real' 'double'
  return $n
}
function AndOf($a, $aPin, $b, $bPin, [double]$x, [double]$y) {
  $n = New-Call $MATH 'BooleanAND' $true $x $y
  Add-Pin $n 'A' 'in' 'bool'
  Add-Pin $n 'B' 'in' 'bool'
  Add-Pin $n 'ReturnValue' 'out' 'bool'
  Connect $a $aPin $n 'A'
  Connect $b $bPin $n 'B'
  return $n
}
function SetBool($name, $value, [double]$x, [double]$y) {
  $n = New-VarSet $name $null 'bool' $null $x $y
  (Get-Pin $n $name).Default = $value
  return $n
}

$X0 = 0; $Y0 = 3000
# ----- On Movement Mode Changed -----
$changed = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$CHARACTER_CLASS`",MemberName=`"K2_OnMovementModeChanged`")", 'bOverrideFunction=True') $X0 $Y0
Add-Pin $changed 'then' 'out' 'exec'
Add-Pin $changed 'PrevMovementMode' 'out' 'byte' '' $MOVEMENT_MODE
Add-Pin $changed 'NewMovementMode' 'out' 'byte' '' $MOVEMENT_MODE
Add-Pin $changed 'PrevCustomMode' 'out' 'byte'
Add-Pin $changed 'NewCustomMode' 'out' 'byte'
$velocity = New-Call $null 'GetVelocity' $true ($X0 + 100) ($Y0 + 350)
Add-Pin $velocity 'ReturnValue' 'out' 'struct' '' $VECTOR
$parts = New-Call $MATH 'BreakVector' $true ($X0 + 300) ($Y0 + 350)
Add-Pin $parts 'InVec' 'in' 'struct' '' $VECTOR
Add-Pin $parts 'X' 'out' 'real' 'double'
Add-Pin $parts 'Y' 'out' 'real' 'double'
Add-Pin $parts 'Z' 'out' 'real' 'double'
Connect $velocity 'ReturnValue' $parts 'InVec'
$notRising = New-Operator 'LessEqual' 'LessEqual_DoubleDouble' 'real' 'double' 'bool' ($X0 + 550) ($Y0 + 350)
Connect $parts 'Z' $notRising 'A'
(Get-Pin $notRising 'B').Default = '10.0'
$walkedOff = AndOf (Falling ($X0 + 550) ($Y0 + 200)) 'ReturnValue' $notRising 'ReturnValue' ($X0 + 750) ($Y0 + 250)
$offEdge = New-Branch ($X0 + 350) $Y0
Connect $walkedOff 'ReturnValue' $offEdge 'Condition'
Connect $changed 'then' $offEdge 'execute'
$stamp = New-VarSet 'LeftGroundAt' $null 'real' $null ($X0 + 1000) ($Y0 - 150)
(Get-Pin $stamp 'LeftGroundAt').Sub = 'double'; (Get-Pin $stamp 'Output_Get').Sub = 'double'
Connect (Now ($X0 + 800) ($Y0 - 50)) 'ReturnValue' $stamp 'LeftGroundAt'
$ready = SetBool 'CoyoteReady' 'true' ($X0 + 1300) ($Y0 - 150)
$notReady = SetBool 'CoyoteReady' 'false' ($X0 + 1000) ($Y0 + 150)
Connect $offEdge 'then' $stamp 'execute'
Connect $stamp 'then' $ready 'execute'
Connect $offEdge 'else' $notReady 'execute'

# ----- TryCoyoteJump -----
$Y1 = $Y0 + 700
$try = New-Node '/Script/BlueprintGraph.K2Node_CustomEvent' @('CustomFunctionName="TryCoyoteJump"') $X0 $Y1
Add-Pin $try 'then' 'out' 'exec'
$since = New-Operator 'Subtract' 'Subtract_DoubleDouble' 'real' 'double' 'real' ($X0 + 300) ($Y1 + 450)
(Get-Pin $since 'ReturnValue').Sub = 'double'
Connect (Now ($X0 + 100) ($Y1 + 400)) 'ReturnValue' $since 'A'
Connect (New-VarGet 'LeftGroundAt' $null 'real' 'double' $null ($X0 + 100) ($Y1 + 500)) 'LeftGroundAt' $since 'B'
$inTime = New-Operator 'LessEqual' 'LessEqual_DoubleDouble' 'real' 'double' 'bool' ($X0 + 500) ($Y1 + 450)
Connect $since 'ReturnValue' $inTime 'A'
Connect (New-VarGet 'CoyoteTime' $null 'real' 'double' $null ($X0 + 300) ($Y1 + 550)) 'CoyoteTime' $inTime 'B'
$armed = AndOf (Falling ($X0 + 300) ($Y1 + 200)) 'ReturnValue' (New-VarGet 'CoyoteReady' $null 'bool' '' $null ($X0 + 300) ($Y1 + 300)) 'CoyoteReady' ($X0 + 550) ($Y1 + 250)
$allowed = AndOf $armed 'ReturnValue' $inTime 'ReturnValue' ($X0 + 750) ($Y1 + 300)
$can = New-Branch ($X0 + 300) $Y1
Connect $allowed 'ReturnValue' $can 'Condition'
Connect $try 'then' $can 'execute'
$used = SetBool 'CoyoteReady' 'false' ($X0 + 1000) $Y1
$ground = New-Call $MOVEMENT_CLASS 'SetMovementMode' $false ($X0 + 1300) $Y1
Add-Pin $ground 'self' 'in' 'object' '' $MOVEMENT_CLASS
Add-Pin $ground 'NewMovementMode' 'in' 'byte' '' $MOVEMENT_MODE 'MOVE_Walking'
Add-Pin $ground 'NewCustomMode' 'in' 'byte' '' $null '0'
Connect (Movement ($X0 + 1100) ($Y1 + 200)) 'CharacterMovement' $ground 'self'
Connect $can 'then' $used 'execute'
Connect $used 'then' $ground 'execute'

# The call to put between IA_Jump (Started) and Jump.
$call = New-Call $null 'TryCoyoteJump' $false ($X0 + 1700) ($Y1 - 200)

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
if ($text.Contains('@{')) { throw 'A node object leaked into a pin or reference (variable name collision)' }
$names = [regex]::Matches($text, '(?m)^Begin Object Class=\S+ Name="(\w+)"') | ForEach-Object { $_.Groups[1].Value }
foreach ($m in [regex]::Matches($text, 'LinkedTo=\(([^)]*)\)')) {
  foreach ($link in ($m.Groups[1].Value -split ',' | Where-Object { $_ })) {
    if ($names -notcontains ($link -split ' ')[0]) { throw "Dangling link: $link" }
  }
}
foreach ($n in $script:nodes) {
  foreach ($p in $n.Pins) {
    if ($p.Cat -eq 'exec' -and $p.Dir -eq 'out' -and $p.Links.Count -gt 1) { throw "Exec output with several links: $($n.Name).$($p.Name)" }
  }
}
[IO.File]::WriteAllText((Join-Path $OutDir 'CoyoteTime_Character.txt'), $text, [Text.UTF8Encoding]::new($false))
"Generated $($script:nodes.Count) nodes"
