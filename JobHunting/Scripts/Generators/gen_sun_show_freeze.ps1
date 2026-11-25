param([string]$OutDir)
# Paste text for BPC_SunShowFreeze (setup_sun_show_freeze.py, 2026-11-25), the sun's component: every tick, a show is
# on when the player controller's view target is not the player's pawn. When that changes (Frozen differs): Frozen = it,
# and the owner's (the sun's) Tick is turned off for a show, back on after.
if (-not $OutDir) { throw 'OutDir is required' }
$lightGen = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_heaven_light.ps1') -Encoding UTF8
$cut = ($lightGen | Select-String -Pattern '^# ===== BP_LightBeam' | Select-Object -First 1).LineNumber - 1
. ([ScriptBlock]::Create(($lightGen[1..($cut - 1)] -join "`n")))
$ACTOR_COMPONENT_C = "/Script/CoreUObject.Class'/Script/Engine.ActorComponent'"

Reset-Graph 100
$tick = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$ACTOR_COMPONENT_C`",MemberName=`"ReceiveTick`")", 'bOverrideFunction=True') 0 0
Add-Pin $tick 'then' 'out' 'exec'
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
# a show: the camera is on something other than the player
$view = New-Call $CONTROLLER 'GetViewTarget' $true 200 300
Add-Pin $view 'self' 'in' 'object' '' $CONTROLLER
Add-Pin $view 'ReturnValue' 'out' 'object' '' $ACTOR
Connect (Controller 0 300) 'ReturnValue' $view 'self'
$pawn = New-Call $STATICS 'GetPlayerPawn' $true 200 450
Add-Pin $pawn 'PlayerIndex' 'in' 'int' '' $null '0'
Add-Pin $pawn 'ReturnValue' 'out' 'object' '' "/Script/CoreUObject.Class'/Script/Engine.Pawn'"
$inShow = New-Call $MATH 'NotEqual_ObjectObject' $true 450 350
Add-Pin $inShow 'A' 'in' 'object' '' $OBJECT
Add-Pin $inShow 'B' 'in' 'object' '' $OBJECT
Add-Pin $inShow 'ReturnValue' 'out' 'bool'
Connect $view 'ReturnValue' $inShow 'A'
Connect $pawn 'ReturnValue' $inShow 'B'
$changed = New-Call $MATH 'NotEqual_BoolBool' $true 650 200
Add-Pin $changed 'A' 'in' 'bool'
Add-Pin $changed 'B' 'in' 'bool'
Add-Pin $changed 'ReturnValue' 'out' 'bool'
Connect $inShow 'ReturnValue' $changed 'A'
Connect (Bool 'Frozen' 500 200) 'Frozen' $changed 'B'
$turn = New-Branch 300 0
Connect $changed 'ReturnValue' $turn 'Condition'
Connect $tick 'then' $turn 'execute'
$setFrozen = SetSelf 'Frozen' 'bool' $null 650 0
Connect $inShow 'ReturnValue' $setFrozen 'Frozen'
$running = New-Call $MATH 'Not_PreBool' $true 850 250
Add-Pin $running 'A' 'in' 'bool'
Add-Pin $running 'ReturnValue' 'out' 'bool'
Connect $setFrozen 'Output_Get' $running 'A'
$owner = New-Call $ACTOR_COMPONENT_C 'GetOwner' $true 850 400
Add-Pin $owner 'ReturnValue' 'out' 'object' '' $ACTOR
$tickOwner = New-Call $ACTOR 'SetActorTickEnabled' $false 1050 0
Add-Pin $tickOwner 'self' 'in' 'object' '' $ACTOR
Add-Pin $tickOwner 'bEnabled' 'in' 'bool'
Connect $owner 'ReturnValue' $tickOwner 'self'
Connect $running 'ReturnValue' $tickOwner 'bEnabled'
Connect $turn 'then' $setFrozen 'execute'
Connect $setFrozen 'then' $tickOwner 'execute'
Write-Graph 'BPC_SunShowFreeze_EventGraph.txt'
