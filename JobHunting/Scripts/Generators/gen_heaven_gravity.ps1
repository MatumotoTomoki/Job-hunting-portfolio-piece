param([string]$OutDir)
# Paste text for BP_GravityZone (components and variables from setup_heaven_gravity.py):
#   Tick: inside = Zone overlaps the player. When that differs from Flipped: Flipped = inside, and the player's
#   CharacterMovement SetGravityDirection(Direction if inside, else (0, 0, -1)).
if (-not $OutDir) { throw 'OutDir is required' }
$lightGen = Get-Content -LiteralPath (Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_heaven_light.ps1') -Encoding UTF8
$cut = ($lightGen | Select-String -Pattern '^# ===== BP_LightBeam' | Select-Object -First 1).LineNumber - 1
$helpers = $lightGen[1..($cut - 1)] -join "`n"
. ([ScriptBlock]::Create($helpers))

Reset-Graph 100
$tick = Event 'ReceiveTick' 0 0
Add-Pin $tick 'DeltaSeconds' 'out' 'real' 'float'
$inside = New-Call $PRIMITIVE 'IsOverlappingActor' $true 300 300
Add-Pin $inside 'self' 'in' 'object' '' $PRIMITIVE
Add-Pin $inside 'Other' 'in' 'object' '' $ACTOR
Add-Pin $inside 'ReturnValue' 'out' 'bool'
Connect (Comp 'Zone' $BOX 100 300) 'Zone' $inside 'self'
Connect (Player 100 400) 'ReturnValue' $inside 'Other'
$changed = New-Operator 'NotEqual' 'NotEqual_BoolBool' 'bool' '' 'bool' 500 300
Connect $inside 'ReturnValue' $changed 'A'
Connect (Bool 'Flipped' 300 450) 'Flipped' $changed 'B'
$branch = New-Branch 300 0
Connect $changed 'ReturnValue' $branch 'Condition'
Connect $tick 'then' $branch 'execute'
$flip = SetSelf 'Flipped' 'bool' $null 600 0
Connect $inside 'ReturnValue' $flip 'Flipped'
Connect $branch 'then' $flip 'execute'
# The direction: Direction inside, straight down outside. (A by-ref vector input needs a node wired in.)
$down = New-Call $MATH 'MakeVector' $true 600 450
Add-Pin $down 'X' 'in' 'real' 'double' $null '0.0'
Add-Pin $down 'Y' 'in' 'real' 'double' $null '0.0'
Add-Pin $down 'Z' 'in' 'real' 'double' $null '-1.0'
Add-Pin $down 'ReturnValue' 'out' 'struct' '' $VECTOR
$pick = New-Call $MATH 'SelectVector' $true 850 350
Add-Pin $pick 'A' 'in' 'struct' '' $VECTOR
Add-Pin $pick 'B' 'in' 'struct' '' $VECTOR
Add-Pin $pick 'bPickA' 'in' 'bool'
Add-Pin $pick 'ReturnValue' 'out' 'struct' '' $VECTOR
Connect (Vec 'Direction' 650 300) 'Direction' $pick 'A'
Connect $down 'ReturnValue' $pick 'B'
Connect $flip 'Output_Get' $pick 'bPickA'
$set = New-Call $CHAR_MOVE 'SetGravityDirection' $false 1100 0
Add-Pin $set 'self' 'in' 'object' '' $CHAR_MOVE
Add-Pin $set 'GravityDir' 'in' 'struct' '' $VECTOR
(Get-Pin $set 'GravityDir') | Add-Member -NotePropertyName ConstRef -NotePropertyValue $true
Connect (Movement 900 200) 'CharacterMovement' $set 'self'
Connect $pick 'ReturnValue' $set 'GravityDir'
Connect $flip 'then' $set 'execute'
Write-Graph 'BP_GravityZone_EventGraph.txt'
