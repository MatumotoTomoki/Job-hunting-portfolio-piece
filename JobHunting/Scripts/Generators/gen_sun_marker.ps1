param([string]$OutDir)
# Paste text for BP_SunMarker (components and variables from setup_sun_marker.py and setup_sun_marker_look.py):
#   Begin Play: the actor shows (older placed ones started hidden); Disk gets its own dynamic material (DiskMaterial).
#   Tick, with a Sun: showing = its Phase is 1 (aim) or 2 (charge). Showing: the actor stands on the sun's Target,
#   48 cm down (the ground under the ball's aim), Disk shows, and DiskMaterial's Charge is 1 while charging, else 0.
#   Otherwise Disk hides. Then, the tick the Phase goes from 2 (charge) to 3 (landed), Impact plays where the marker
#   stands; LastPhase remembers the Phase.
if (-not $OutDir) { throw 'OutDir is required' }
$lightGen = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_heaven_light.ps1') -Encoding UTF8
$cut = ($lightGen | Select-String -Pattern '^# ===== BP_LightBeam' | Select-Object -First 1).LineNumber - 1
$helpers = $lightGen[1..($cut - 1)] -join "`n"
. ([ScriptBlock]::Create($helpers))

$SUN_CLASS = "/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPerson/Blueprints/Gimmicks/Heaven/BP_TowerSun.BP_TowerSun_C'"
$MATERIAL = "/Script/CoreUObject.Class'/Script/Engine.MaterialInterface'"
$DYNAMIC = "/Script/CoreUObject.Class'/Script/Engine.MaterialInstanceDynamic'"
$EMITTER = "/Script/CoreUObject.Class'/Script/Effekseer.EffekseerEmitterComponent'"
$ACTOR_COMP = "/Script/CoreUObject.Class'/Script/Engine.ActorComponent'"

function SunVar($name, $cat, $sub, $obj, [double]$x, [double]$y) {
  $n = New-VarGet $name $SUN_CLASS $cat $sub $obj $x $y
  Connect (Comp 'Sun' $SUN_CLASS ($x - 200) ($y + 60)) 'Sun' $n 'self'
  return $n
}
function PhaseIs($value, $phaseNode, [double]$x, [double]$y) {
  $n = New-Operator 'EqualEqual' 'EqualEqual_IntInt' 'int' '' 'bool' $x $y
  Connect $phaseNode 'Phase' $n 'A'
  (Get-Pin $n 'B').Default = $value
  return $n
}

Reset-Graph 100
# ----- Begin Play -----
$begin = Event 'ReceiveBeginPlay' 0 (-700)
$unhide = New-Call $ACTOR 'SetActorHiddenInGame' $false 300 (-700)
Add-Pin $unhide 'self' 'in' 'object' '' $ACTOR
Add-Pin $unhide 'bNewHidden' 'in' 'bool' '' $null 'false'
$make = New-Call $PRIMITIVE 'CreateDynamicMaterialInstance' $false 650 (-700)
Add-Pin $make 'self' 'in' 'object' '' $PRIMITIVE
Add-Pin $make 'ElementIndex' 'in' 'int' '' $null '0'
Add-Pin $make 'SourceMaterial' 'in' 'object' '' $MATERIAL
Add-Pin $make 'OptionalName' 'in' 'name' '' $null 'None'
Add-Pin $make 'ReturnValue' 'out' 'object' '' $DYNAMIC
Connect (Comp 'Disk' $STATIC_MESH 450 (-500)) 'Disk' $make 'self'
$keep = New-VarSet 'DiskMaterial' $null 'object' $DYNAMIC 1050 (-700)
Connect $make 'ReturnValue' $keep 'DiskMaterial'
Connect $begin 'then' $unhide 'execute'
Connect $unhide 'then' $make 'execute'
Connect $make 'then' $keep 'execute'

# ----- Tick -----
$tick = Event 'ReceiveTick' 0 0
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$hasSun = New-Branch 300 0
Connect (Valid (Comp 'Sun' $SUN_CLASS 0 200) 'Sun' 150 200) 'ReturnValue' $hasSun 'Condition'
Connect $tick 'then' $hasSun 'execute'
$aiming = PhaseIs '1' (SunVar 'Phase' 'int' '' $null 300 350) 500 350
$charging = PhaseIs '2' (SunVar 'Phase' 'int' '' $null 300 500) 500 500
$showing = New-Branch 700 0
Connect (Both $aiming 'ReturnValue' $charging 'ReturnValue' 'BooleanOR' 700 400) 'ReturnValue' $showing 'Condition'
Connect $hasSun 'then' $showing 'execute'
# Showing: stand on the ground under the aim, show the disk, set Charge.
$down = New-Call $MATH 'MakeVector' $true 800 750
Add-Pin $down 'X' 'in' 'real' 'double' $null '0.0'
Add-Pin $down 'Y' 'in' 'real' 'double' $null '0.0'
Add-Pin $down 'Z' 'in' 'real' 'double' $null '48.0'
Add-Pin $down 'ReturnValue' 'out' 'struct' '' $VECTOR
$ground = New-Operator 'Subtract' 'Subtract_VectorVector' 'struct' '' 'struct' 1000 650
foreach ($pin in 'A', 'B', 'ReturnValue') { (Get-Pin $ground $pin).Obj = $VECTOR }
Connect (SunVar 'Target' 'struct' '' $VECTOR 800 600) 'Target' $ground 'A'
Connect $down 'ReturnValue' $ground 'B'
$place = New-Call $ACTOR 'K2_SetActorLocation' $false 1000 (-200)
Add-Pin $place 'self' 'in' 'object' '' $ACTOR
Add-Pin $place 'NewLocation' 'in' 'struct' '' $VECTOR
Add-Pin $place 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $place 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $place 'bTeleport' 'in' 'bool' '' $null 'true'
Add-Pin $place 'ReturnValue' 'out' 'bool'
Connect $ground 'ReturnValue' $place 'NewLocation'
$show = Visible 'Disk' 'true' 1400 (-200)
$charge = New-Call $MATH 'SelectFloat' $true 1600 0
Add-Pin $charge 'A' 'in' 'real' 'double' $null '1.0'
Add-Pin $charge 'B' 'in' 'real' 'double' $null '0.0'
Add-Pin $charge 'bPickA' 'in' 'bool'
Add-Pin $charge 'ReturnValue' 'out' 'real' 'double'
Connect (PhaseIs '2' (SunVar 'Phase' 'int' '' $null 1400 100) 1550 150) 'ReturnValue' $charge 'bPickA'
$setCharge = New-Call $DYNAMIC 'SetScalarParameterValue' $false 1800 (-200)
Add-Pin $setCharge 'self' 'in' 'object' '' $DYNAMIC
Add-Pin $setCharge 'ParameterName' 'in' 'name' '' $null 'Charge'
Add-Pin $setCharge 'Value' 'in' 'real' 'float'
Connect (New-VarGet 'DiskMaterial' $null 'object' '' $DYNAMIC 1600 (-100)) 'DiskMaterial' $setCharge 'self'
Connect $charge 'ReturnValue' $setCharge 'Value'
Connect $showing 'then' $place 'execute'
Connect $place 'then' $show 'execute'
Connect $show 'then' $setCharge 'execute'
# Not showing: hide the disk.
$hide = Visible 'Disk' 'false' 1000 300
Connect $showing 'else' $hide 'execute'
# Landed this tick (2 -> 3): play Impact. Then remember the Phase.
$landed = New-Branch 2300 0
$nowLanded = PhaseIs '3' (SunVar 'Phase' 'int' '' $null 2000 350) 2150 350
$wasCharging = New-Operator 'EqualEqual' 'EqualEqual_IntInt' 'int' '' 'bool' 2150 500
Connect (New-VarGet 'LastPhase' $null 'int' '' $null 1950 550) 'LastPhase' $wasCharging 'A'
(Get-Pin $wasCharging 'B').Default = '2'
Connect (Both $nowLanded 'ReturnValue' $wasCharging 'ReturnValue' 'BooleanAND' 2300 400) 'ReturnValue' $landed 'Condition'
Connect $setCharge 'then' $landed 'execute'
Connect $hide 'then' $landed 'execute'
$play = New-Call $ACTOR_COMP 'Activate' $false 2600 (-150)
Add-Pin $play 'self' 'in' 'object' '' $ACTOR_COMP
Add-Pin $play 'bReset' 'in' 'bool' '' $null 'true'
Connect (New-VarGet 'Impact' $null 'object' '' $EMITTER 2400 50) 'Impact' $play 'self'
$remember = SetSelf 'LastPhase' 'int' $null 2900 0
Connect (SunVar 'Phase' 'int' '' $null 2650 250) 'Phase' $remember 'LastPhase'
Connect $landed 'then' $play 'execute'
Connect $play 'then' $remember 'execute'
Connect $landed 'else' $remember 'execute'
Write-Graph 'BP_SunMarker_EventGraph.txt'
