param([string]$OutDir)
# Paste text for the checkpoint flag as it works since 2026-11-19 (the user: the flags stand in the level from the
# start, broken; touched, a flag stands up and from then on every fall comes back to it): BP_CheckpointFlag_EventGraph.txt
# (components and variables from setup_checkpoint_flags.py).
#   Begin Play: the top half (Upper) lies tipped over (BreakFlag's pose: roll 85 at the 55 cm joint).
#   Touched by the player (Touch box), the first time only: Raised, the player's ActiveFlag = this flag, the top half
#     swings up straight in 0.35 s (eased). The character's fall check then sends the player to this flag's
#     RespawnPoint on every fall (its "break and forget" nodes removed by hand, see setup_checkpoint_flags.py).
#   BreakFlag (kept: the character's old plant-a-flag graph still calls it): the top snaps over, the flag is removed.
if (-not $OutDir) { throw 'OutDir is required' }
$lightGen = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_heaven_light.ps1') -Encoding UTF8
$cut = ($lightGen | Select-String -Pattern '^# ===== BP_LightBeam' | Select-Object -First 1).LineNumber - 1
$helpers = $lightGen[1..($cut - 1)] -join "`n"
. ([ScriptBlock]::Create($helpers))

$CHARACTER_BP = "/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter1.BP_ThirdPersonCharacter1_C'"
$FLAG_BP = "/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPerson/Item/Checkpoint/BP_CheckpointFlag.BP_CheckpointFlag_C'"
$JOINT = '0.000000,0.000000,55.000000'
$BROKEN = '0.000000,0.000000,85.000000'    # Pitch, Yaw, Roll: tipped over sideways
$UPRIGHT = '0.000000,0.000000,0.000000'

function MoveTo($componentName, $where, $rotation, $seconds, [double]$x, [double]$y) {
  $n = New-Call $SYSTEM 'MoveComponentTo' $false $x $y
  $n.Props = @('bWantsEnumToExecExpansion=True') + $n.Props
  $n.Pins.Clear()
  Add-Pin $n 'Move' 'in' 'exec'
  Add-Pin $n 'then' 'out' 'exec'
  Add-Pin $n 'Component' 'in' 'object' '' $SCENE
  Add-Pin $n 'TargetRelativeLocation' 'in' 'struct' '' $VECTOR $where
  Add-Pin $n 'TargetRelativeRotation' 'in' 'struct' '' $ROTATOR $rotation
  Add-Pin $n 'bEaseOut' 'in' 'bool' '' $null 'true'
  Add-Pin $n 'bEaseIn' 'in' 'bool' '' $null 'false'
  Add-Pin $n 'OverTime' 'in' 'real' 'float' $null $seconds
  Add-Pin $n 'bForceShortestRotationPath' 'in' 'bool' '' $null 'true'
  Connect (Comp $componentName $SCENE ($x - 200) ($y + 250)) $componentName $n 'Component'
  return $n
}

Reset-Graph 100
# ----- Begin Play: broken -----
$begin = Event 'ReceiveBeginPlay' 0 0
$lie = New-Call $SCENE 'K2_SetRelativeLocationAndRotation' $false 300 0
Add-Pin $lie 'self' 'in' 'object' '' $SCENE
Add-Pin $lie 'NewLocation' 'in' 'struct' '' $VECTOR $JOINT
Add-Pin $lie 'NewRotation' 'in' 'struct' '' $ROTATOR $BROKEN
Add-Pin $lie 'bSweep' 'in' 'bool' '' $null 'false'
Add-Pin $lie 'SweepHitResult' 'out' 'struct' '' $HIT
Add-Pin $lie 'bTeleport' 'in' 'bool' '' $null 'true'
Connect (Comp 'Upper' $SCENE 100 200) 'Upper' $lie 'self'
Connect $begin 'then' $lie 'execute'

# ----- touched: stands up, becomes the checkpoint -----
$touch = Event 'ReceiveActorBeginOverlap' 0 500
Add-Pin $touch 'OtherActor' 'out' 'object' '' $ACTOR
$once = New-Branch 300 500
Connect (Bool 'Raised' 150 700) 'Raised' $once 'Condition'
$inside = New-Call $PRIMITIVE 'IsOverlappingActor' $true 400 750
Add-Pin $inside 'self' 'in' 'object' '' $PRIMITIVE
Add-Pin $inside 'Other' 'in' 'object' '' $ACTOR
Add-Pin $inside 'ReturnValue' 'out' 'bool'
Connect (Comp 'Touch' $BOX 200 750) 'Touch' $inside 'self'
Connect (Player 200 850) 'ReturnValue' $inside 'Other'
$isPlayer = New-Branch 600 500
Connect $inside 'ReturnValue' $isPlayer 'Condition'
$raised = SetSelf 'Raised' 'bool' 'true' 850 500
$cast = New-Node '/Script/BlueprintGraph.K2Node_DynamicCast' @("TargetType=`"$CHARACTER_BP`"") 1100 500
Add-Exec $cast
Add-Pin $cast 'CastFailed' 'out' 'exec'
Add-Pin $cast 'Object' 'in' 'object' '' $OBJECT
Add-Pin $cast 'AsBP Third Person Character 1' 'out' 'object' '' $CHARACTER_BP
Add-Pin $cast 'bSuccess' 'out' 'bool'
Connect (Player 900 700) 'ReturnValue' $cast 'Object'
$remember = New-VarSet 'ActiveFlag' $CHARACTER_BP 'object' $FLAG_BP 1450 500
Connect $cast 'AsBP Third Person Character 1' $remember 'self'
$self = New-Node '/Script/BlueprintGraph.K2Node_Self' @() 1250 750
Add-Pin $self 'self' 'out' 'object' '' $ACTOR
Connect $self 'self' $remember 'ActiveFlag'
$standUp = MoveTo 'Upper' $JOINT $UPRIGHT '0.35' 1800 500
Connect $touch 'then' $once 'execute'
Connect $once 'else' $isPlayer 'execute'
Connect $isPlayer 'then' $raised 'execute'
Connect $raised 'then' $cast 'execute'
Connect $cast 'then' $remember 'execute'
Connect $remember 'then' $standUp 'Move'

# ----- BreakFlag (kept for the character's old plant-a-flag graph) -----
$breakEvent = New-Node '/Script/BlueprintGraph.K2Node_CustomEvent' @('CustomFunctionName="BreakFlag"') 0 1200
Add-Pin $breakEvent 'then' 'out' 'exec'
$snap = MoveTo 'Upper' $JOINT $BROKEN '0.35' 400 1200
$linger = Delay '0.8' 800 1200
$remove = New-Call $ACTOR 'K2_DestroyActor' $false 1100 1200
Add-Pin $remove 'self' 'in' 'object' '' $ACTOR
Connect $breakEvent 'then' $snap 'Move'
Connect $snap 'then' $linger 'execute'
Connect $linger 'then' $remove 'execute'
Write-Graph 'BP_CheckpointFlag_EventGraph.txt'
