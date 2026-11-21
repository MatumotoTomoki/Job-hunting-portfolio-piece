# Achievements step 6 (2026-11-21): BP_SecretDoor's whole event graph -> Scripts/BP_SecretDoor_EventGraph.txt.
#   BeginPlay -> Refresh.  ActorBeginOverlap (the player) -> Refresh -> if IsOpen and the player is in EnterBox:
#   Open Level LV_Secret.
#   Refresh: GI LoadAchievements; lamp i glows when FreeAchievementCount > i (12 lamps); emblem i glows when
#   ACH_COIN_A(i+1) is unlocked; IsOpen = all 4 coins and FreeAchievementCount >= NeedFree; open = Door hidden and
#   without collision, closed = shown and blocking.
# Components come from setup_secret_door.py: Door, Light00..Light11, Emblem0..Emblem3, ApproachBox, EnterBox.
$OutDir = Split-Path -Parent $PSScriptRoot
$helpers = (Get-Content (Join-Path $PSScriptRoot 'gen_pause_menu.ps1') -Encoding UTF8)[3..225] -join "`n"
Invoke-Expression $helpers

$CHAR = "/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter1.BP_ThirdPersonCharacter1_C'"
$ACTOR = "/Script/CoreUObject.Class'/Script/Engine.Actor'"
$SMC = "/Script/CoreUObject.Class'/Script/Engine.StaticMeshComponent'"
$BOXC = "/Script/CoreUObject.Class'/Script/Engine.BoxComponent'"
$PRIM = "/Script/CoreUObject.Class'/Script/Engine.PrimitiveComponent'"
$MESH = "/Script/CoreUObject.Class'/Script/Engine.MeshComponent'"   # SetScalarParameterValueOnMaterials lives on UMeshComponent
$SCENE = "/Script/CoreUObject.Class'/Script/Engine.SceneComponent'"
$ARRAYLIB = "/Script/CoreUObject.Class'/Script/Engine.KismetArrayLibrary'"
$COLLISION = "/Script/CoreUObject.Enum'/Script/Engine.ECollisionEnabled'"

Reset-Graph

function New-Event($member, $x, $y) {
  $n = New-Node '/Script/BlueprintGraph.K2Node_Event' @("EventReference=(MemberParent=`"$ACTOR`",MemberName=`"$member`")", 'bOverrideFunction=True') $x $y
  Add-Pin $n 'then' 'out' 'exec'
  return $n
}
function New-CallRefresh($x, $y) {
  $n = New-Node '/Script/BlueprintGraph.K2Node_CallFunction' @('FunctionReference=(MemberName="Refresh",bSelfContext=True)') $x $y
  Add-Exec $n
  return $n
}
function New-And($x, $y) {
  $n = New-Call $MATH 'BooleanAND' $true $x $y
  Add-Pin $n 'A' 'in' 'bool' '' $null 'false'
  Add-Pin $n 'B' 'in' 'bool' '' $null 'false'
  Add-Pin $n 'ReturnValue' 'out' 'bool'
  return $n
}
function New-SelectFloat($x, $y) {
  $n = New-Call $MATH 'SelectFloat' $true $x $y
  Add-Pin $n 'A' 'in' 'real' 'double' $null '8.0'
  Add-Pin $n 'B' 'in' 'real' 'double' $null '0.0'
  Add-Pin $n 'bPickA' 'in' 'bool' '' $null 'false'
  Add-Pin $n 'ReturnValue' 'out' 'real' 'double'
  return $n
}
function New-SetGlow($x, $y) {
  $n = New-Call $MESH 'SetScalarParameterValueOnMaterials' $false $x $y
  Add-Pin $n 'self' 'in' 'object' '' $MESH
  Add-Pin $n 'ParameterName' 'in' 'name' '' $null 'Glow'
  Add-Pin $n 'ParameterValue' 'in' 'real' 'float' $null '0.0'
  return $n
}

# ----- BeginPlay -----
$begin = New-Event 'ReceiveBeginPlay' 0 (-600)
$refresh0 = New-CallRefresh 300 (-600)
Connect $begin 'then' $refresh0 'execute'

# ----- the player walks in -----
$overlap = New-Event 'ReceiveActorBeginOverlap' 0 (-300)
Add-Pin $overlap 'OtherActor' 'out' 'object' '' $ACTOR
$castPlayer = New-Node '/Script/BlueprintGraph.K2Node_DynamicCast' @("TargetType=`"$CHAR`"") 300 (-300)
Add-Exec $castPlayer
Add-Pin $castPlayer 'CastFailed' 'out' 'exec'
Add-Pin $castPlayer 'Object' 'in' 'object' '' $OBJECT
Add-Pin $castPlayer 'AsBP Third Person Character 1' 'out' 'object' '' $CHAR
Add-Pin $castPlayer 'bSuccess' 'out' 'bool'
$refresh1 = New-CallRefresh 650 (-300)
$enterBox = New-VarGet 'EnterBox' $null 'object' '' $BOXC 650 (-100)
$inside = New-Call $PRIM 'IsOverlappingActor' $true 900 (-100)
Add-Pin $inside 'self' 'in' 'object' '' $PRIM
Add-Pin $inside 'Other' 'in' 'object' '' $ACTOR
Add-Pin $inside 'ReturnValue' 'out' 'bool'
$isOpen0 = New-VarGet 'IsOpen' $null 'bool' '' $null 900 0
$both = New-And 1150 (-100)
$go = New-Branch 1350 (-300)
$open = New-Call $STATICS 'OpenLevel' $false 1650 (-300)
Add-Pin $open 'LevelName' 'in' 'name' '' $null 'LV_Secret'
Add-Pin $open 'bAbsolute' 'in' 'bool' '' $null 'true'
Add-Pin $open 'Options' 'in' 'string' '' $null ''
Connect $overlap 'then' $castPlayer 'execute'
Connect $overlap 'OtherActor' $castPlayer 'Object'
Connect $castPlayer 'then' $refresh1 'execute'
Connect $refresh1 'then' $go 'execute'
Connect $enterBox 'EnterBox' $inside 'self'
Connect $overlap 'OtherActor' $inside 'Other'
Connect $isOpen0 'IsOpen' $both 'A'
Connect $inside 'ReturnValue' $both 'B'
Connect $both 'ReturnValue' $go 'Condition'
Connect $go 'then' $open 'execute'

# ----- Refresh -----
$event = New-Node '/Script/BlueprintGraph.K2Node_CustomEvent' @('CustomFunctionName="Refresh"') 0 400
Add-Pin $event 'then' 'out' 'exec'
$gi = New-GetGameInstance 0 600
$cast = New-CastToGameInstance $false 250 400
$load = New-Call $GI_CLASS 'LoadAchievements' $false 550 400
Add-Pin $load 'self' 'in' 'object' '' $GI_CLASS
$free = New-VarGet 'FreeAchievementCount' $GI_CLASS 'int' '' $null 550 700
$unlocked = New-VarGet 'UnlockedAchievements' $GI_CLASS 'name' '' $null 550 900
Connect $event 'then' $cast 'execute'
Connect $gi 'ReturnValue' $cast 'Object'
Connect $cast 'then' $load 'execute'
Connect $cast 'AsBP My Game Instance' $load 'self'
Connect $cast 'AsBP My Game Instance' $free 'self'
Connect $cast 'AsBP My Game Instance' $unlocked 'self'

$prev = $load
$x = 850
for ($i = 0; $i -lt 12; $i++) {
  $lamp = New-VarGet ('Light{0:D2}' -f $i) $null 'object' '' $SMC ($x - 100) 650
  $lit = New-IntOperator 'Greater' 'Greater_IntInt' 'bool' ($x - 150) 800
  (Get-Pin $lit 'B').Default = "$i"
  $pick = New-SelectFloat $x 800
  $set = New-SetGlow $x 400
  Connect $free 'FreeAchievementCount' $lit 'A'
  Connect $lit 'ReturnValue' $pick 'bPickA'
  Connect $pick 'ReturnValue' $set 'ParameterValue'
  Connect $lamp ('Light{0:D2}' -f $i) $set 'self'
  Connect $prev 'then' $set 'execute'
  $prev = $set
  $x += 350
}
$coins = @()
for ($i = 0; $i -lt 4; $i++) {
  $emblem = New-VarGet "Emblem$i" $null 'object' '' $SMC ($x - 100) 650
  $has = New-Node '/Script/BlueprintGraph.K2Node_CallArrayFunction' @('bDefaultsToPureFunc=True', "FunctionReference=(MemberParent=`"$ARRAYLIB`",MemberName=`"Array_Contains`")") ($x - 150) 950
  Add-Pin $has 'TargetArray' 'in' 'name'
  Add-Pin $has 'ItemToFind' 'in' 'name' '' $null "ACH_COIN_A$($i + 1)"
  Add-Pin $has 'ReturnValue' 'out' 'bool'
  $pick = New-SelectFloat $x 800
  $set = New-SetGlow $x 400
  Connect $unlocked 'UnlockedAchievements' $has 'TargetArray'
  Connect $has 'ReturnValue' $pick 'bPickA'
  Connect $pick 'ReturnValue' $set 'ParameterValue'
  Connect $emblem "Emblem$i" $set 'self'
  Connect $prev 'then' $set 'execute'
  $prev = $set
  $coins += $has
  $x += 350
}
$and1 = New-And $x 900
$and2 = New-And $x 1050
$and3 = New-And ($x + 200) 950
$need = New-VarGet 'NeedFree' $null 'int' '' $null $x 1200
$enough = New-IntOperator 'GreaterEqual' 'GreaterEqual_IntInt' 'bool' ($x + 200) 1150
$all = New-And ($x + 400) 1000
$setOpen = New-VarSet 'IsOpen' $null 'bool' '' $null ($x + 600) 400
Connect $coins[0] 'ReturnValue' $and1 'A'
Connect $coins[1] 'ReturnValue' $and1 'B'
Connect $coins[2] 'ReturnValue' $and2 'A'
Connect $coins[3] 'ReturnValue' $and2 'B'
Connect $and1 'ReturnValue' $and3 'A'
Connect $and2 'ReturnValue' $and3 'B'
Connect $free 'FreeAchievementCount' $enough 'A'
Connect $need 'NeedFree' $enough 'B'
Connect $and3 'ReturnValue' $all 'A'
Connect $enough 'ReturnValue' $all 'B'
Connect $all 'ReturnValue' $setOpen 'IsOpen'
Connect $prev 'then' $setOpen 'execute'
$branch = New-Branch ($x + 900) 400
Connect $setOpen 'then' $branch 'execute'
Connect $setOpen 'Output_Get' $branch 'Condition'
$doorGet = New-VarGet 'Door' $null 'object' '' $SMC ($x + 900) 750
foreach ($state in @(@{ Pin = 'then'; Show = 'false'; Collide = 'NoCollision'; Y = 300 }, @{ Pin = 'else'; Show = 'true'; Collide = 'QueryAndPhysics'; Y = 550 })) {
  $vis = New-Call $SCENE 'SetVisibility' $false ($x + 1150) $state.Y
  Add-Pin $vis 'self' 'in' 'object' '' $SCENE
  Add-Pin $vis 'bNewVisibility' 'in' 'bool' '' $null $state.Show
  Add-Pin $vis 'bPropagateToChildren' 'in' 'bool' '' $null 'false'
  $col = New-Call $PRIM 'SetCollisionEnabled' $false ($x + 1450) $state.Y
  Add-Pin $col 'self' 'in' 'object' '' $PRIM
  Add-Pin $col 'NewType' 'in' 'byte' '' $COLLISION $state.Collide
  Connect $branch $state.Pin $vis 'execute'
  Connect $vis 'then' $col 'execute'
  Connect $doorGet 'Door' $vis 'self'
  Connect $doorGet 'Door' $col 'self'
}

$text = Format-Graph
# The Refresh event goes first, so the Refresh calls pasted with it find it (else their pins come in orphaned).
$blocks = [regex]::Matches($text, '(?ms)^Begin Object .*?^End Object\r?\n') | ForEach-Object Value
$text = ((@($blocks | Where-Object { $_ -match 'K2Node_CustomEvent' }) + @($blocks | Where-Object { $_ -notmatch 'K2Node_CustomEvent' })) -join '')
# Array pins: the helpers write ContainerType=None; mark UnlockedAchievements and Array_Contains' TargetArray.
$text = [regex]::Replace($text, '(PinName="(?:UnlockedAchievements|TargetArray)",[^\r\n]*?PinType\.ContainerType=)None', '${1}Array')
Assert-LinksResolve $text
Save-Text 'BP_SecretDoor_EventGraph.txt' $text
"BP_SecretDoor: $($script:nodes.Count) nodes"
