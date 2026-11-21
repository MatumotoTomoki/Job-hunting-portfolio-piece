param([string]$OutDir)
# Paste text for hooking an achievement into an existing blueprint: Scripts/AchievementHooks/Unlock_<ID>.txt, one per
# achievement in setup_achievements.py. Each holds three nodes: Get Game Instance -> Cast To BP_MyGameInstance ->
# Unlock Achievement (ID filled in). Paste it next to the moment the achievement is earned and wire it in by hand:
# <that node>.then -> Cast, Unlock Achievement.then -> whatever <that node> led to before (if anything).
# Run: powershell -File Generators/gen_achievement_hooks.ps1 -OutDir <Scripts folder>
if (-not $OutDir) { throw 'OutDir is required' }
$cageGen = Join-Path $(if ($PSScriptRoot) { ($GenDir = $PSScriptRoot) } else { $GenDir }) 'gen_hell_cage.ps1'
$defs = Get-Content -LiteralPath $cageGen -Encoding UTF8 | Select-Object -Skip 10 -First 172
. ([ScriptBlock]::Create(($defs -join "`n")))

$setup = Get-Content -LiteralPath (Join-Path (Split-Path -Parent $GenDir) 'setup_achievements.py') -Encoding UTF8
$ids = $setup | ForEach-Object { if ($_ -match '^\s*\("(ACH_\w+)"') { $Matches[1] } }
$folder = Join-Path (Resolve-Path -LiteralPath $OutDir).Path 'AchievementHooks'
New-Item -ItemType Directory -Force $folder | Out-Null

foreach ($id in $ids) {
  Reset-Graph 900
  $cast = GameInstance 250 0
  $unlock = New-Call $GI_CLASS 'UnlockAchievement' $false 600 0
  Add-Pin $unlock 'self' 'in' 'object' '' $GI_CLASS
  Add-Pin $unlock 'ID' 'in' 'name' '' $null $id
  Connect $cast 'then' $unlock 'execute'
  Connect $cast $GI_OUT $unlock 'self'
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
  [IO.File]::WriteAllText((Join-Path $folder "Unlock_$id.txt"), $sb.ToString(), [Text.UTF8Encoding]::new($false))
}
"$($ids.Count) hooks in $folder"
