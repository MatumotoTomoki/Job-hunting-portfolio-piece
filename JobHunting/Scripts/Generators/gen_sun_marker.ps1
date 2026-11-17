param([string]$OutDir)
# Paste text for BP_SunMarker (component and variable from setup_sun_marker.py):
#   Tick, with a Sun: showing = its Phase is 1 (aim) or 2 (charge). Showing: the actor stands on the sun's Target,
#   48 cm down (the ground under the ball's aim), and shows; otherwise it hides.
if (-not $OutDir) { throw 'OutDir is required' }
$lightGen = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_heaven_light.ps1') -Encoding UTF8
$cut = ($lightGen | Select-String -Pattern '^# ===== BP_LightBeam' | Select-Object -First 1).LineNumber - 1
$helpers = $lightGen[1..($cut - 1)] -join "`n"
. ([ScriptBlock]::Create($helpers))

$SUN_CLASS = "/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPerson/Blueprints/Gimmicks/Heaven/BP_TowerSun.BP_TowerSun_C'"

function SunVar($name, $cat, $sub, $obj, [double]$x, [double]$y) {
  $n = New-VarGet $name $SUN_CLASS $cat $sub $obj $x $y
  Connect (Comp 'Sun' $SUN_CLASS ($x - 200) ($y + 60)) 'Sun' $n 'self'
  return $n
}
function Hide($value, [double]$x, [double]$y) {
  $n = New-Call $ACTOR 'SetActorHiddenInGame' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $ACTOR
  Add-Pin $n 'bNewHidden' 'in' 'bool' '' $null $value
  return $n
}

Reset-Graph 100
$tick = Event 'ReceiveTick' 0 0
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$hasSun = New-Branch 300 0
Connect (Valid (Comp 'Sun' $SUN_CLASS 0 200) 'Sun' 150 200) 'ReturnValue' $hasSun 'Condition'
Connect $tick 'then' $hasSun 'execute'
$aiming = New-Operator 'EqualEqual' 'EqualEqual_IntInt' 'int' '' 'bool' 500 350
Connect (SunVar 'Phase' 'int' '' $null 300 350) 'Phase' $aiming 'A'
(Get-Pin $aiming 'B').Default = '1'
$charging = New-Operator 'EqualEqual' 'EqualEqual_IntInt' 'int' '' 'bool' 500 500
Connect (SunVar 'Phase' 'int' '' $null 300 500) 'Phase' $charging 'A'
(Get-Pin $charging 'B').Default = '2'
$showing = New-Branch 700 0
Connect (Both $aiming 'ReturnValue' $charging 'ReturnValue' 'BooleanOR' 700 400) 'ReturnValue' $showing 'Condition'
Connect $hasSun 'then' $showing 'execute'
$down = New-Call $MATH 'MakeVector' $true 800 750
Add-Pin $down 'X' 'in' 'real' 'double' $null '0.0'
Add-Pin $down 'Y' 'in' 'real' 'double' $null '0.0'
Add-Pin $down 'Z' 'in' 'real' 'double' $null '48.0'
Add-Pin $down 'ReturnValue' 'out' 'struct' '' $VECTOR
$ground = New-Operator 'Subtract' 'Subtract_VectorVector' 'struct' '' 'struct' 1000 650
foreach ($pin in 'A', 'B', 'ReturnValue') { (Get-Pin $ground $pin).Obj = $VECTOR }
Connect (SunVar 'Target' 'struct' '' $VECTOR 800 600) 'Target' $ground 'A'
Connect $down 'ReturnValue' $ground 'B'
$place = New-Call $ACTOR 'K2_SetActorLocation' $false 1000 -200
Add-Pin $place 'self' 'in' 'object' '' $ACTOR
Add-Pin $place 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $place 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $place 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $place 'bTeleport' 'in' 'bool' '' $null 'true'
Add-Pin $place 'ReturnValue' 'out' 'bool'
Connect $ground 'ReturnValue' $place 'NewLocation'
$show = Hide 'false' 1350 -200
$hide = Hide 'true' 1000 200
Connect $showing 'then' $place 'execute'
Connect $place 'then' $show 'execute'
Connect $showing 'else' $hide 'execute'
Write-Graph 'BP_SunMarker_EventGraph.txt'
