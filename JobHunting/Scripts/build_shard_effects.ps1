# Builds the light shard's effects (BP_LightShard; the user, 2026-11-21), warm gold-white like the crystal:
#   SourceArt/Effects/ShardFx/ShardIdle.efk  loops while it waits: little glints rising slowly round it, so it can be
#                                            spotted from afar
#   SourceArt/Effects/ShardFx/ShardGet.efk   one shot as it is taken: a flash, a ring of glints thrown out and motes
#                                            shooting up - over within 50 frames (the shard is destroyed at 0.9 s and
#                                            takes its emitters with it)
# Units: 1 Effekseer unit = 20 cm, Y up. Textures copied from SunImpact (CloudPuff, Glint).
#   powershell -File build_shard_effects.ps1 [-Effekseer <path to Effekseer.exe>]
param([string]$Effekseer = (Join-Path $env:USERPROFILE 'Desktop\Effekseer160Win\Effekseer160Win\Tool\Effekseer.exe'))
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\SourceArt\Effects'))
$out = Join-Path $root 'ShardFx'
New-Item -ItemType Directory -Force (Join-Path $out 'Texture') | Out-Null
foreach ($name in 'CloudPuff.png', 'Glint.png') { Copy-Item (Join-Path $root "SunImpact\Texture\$name") (Join-Path $out "Texture\$name") -Force }

function Range($tag, $center, $min, $max) { "<$tag><Center>$center</Center><Max>$max</Max><Min>$min</Min></$tag>" }
function Axis($x, $y, $z) {
  $s = ''
  foreach ($pair in @(@('X', $x), @('Y', $y), @('Z', $z))) { if ($pair[1]) { $s += Range $pair[0] $pair[1][0] $pair[1][1] $pair[1][2] } }
  return $s
}
function Colour($from, $to) {
  $parts = foreach ($pair in @(@('Start', $from), @('End', $to))) {
    $c = $pair[1]
    "<$($pair[0])>$(Range R $c[0] $c[0] $c[0])$(Range G $c[1] $c[1] $c[1])$(Range B $c[2] $c[2] $c[2])$(Range A $c[3] $c[3] $c[3])</$($pair[0])>"
  }
  "<ColorAll>2</ColorAll><ColorAll_Easing>$($parts -join '')</ColorAll_Easing>"
}
function Puff($p) {
  $accel = if ($p.Acceleration) { "<Acceleration>$(Axis $p.Acceleration[0] $p.Acceleration[1] $p.Acceleration[2])</Acceleration>" } else { '' }
  "<Node><CommonValues><LocationEffectType>1</LocationEffectType><RotationEffectType>1</RotationEffectType><ScaleEffectType>1</ScaleEffectType>$(Range Life $p.Life[0] $p.Life[1] $p.Life[2])</CommonValues>" +
  "<LocationValues><Type>1</Type><PVA><Location>$(Axis $p.Location[0] $p.Location[1] $p.Location[2])</Location><Velocity>$(Axis $p.Velocity[0] $p.Velocity[1] $p.Velocity[2])</Velocity>$accel</PVA></LocationValues>" +
  "<RotationValues><Type>1</Type><PVA><Rotation><Z><Max>180</Max><Min>-180</Min></Z></Rotation><Velocity><Z><Max>2</Max><Min>-2</Min></Z></Velocity></PVA></RotationValues>" +
  "<ScalingValues><Type>4</Type><SingleEasing>$(Range Start $p.SizeFrom[0] $p.SizeFrom[1] $p.SizeFrom[2])$(Range End $p.SizeTo[0] $p.SizeTo[1] $p.SizeTo[2])<StartSpeed>20</StartSpeed><EndSpeed>-20</EndSpeed></SingleEasing></ScalingValues>" +
  "<RendererCommonValues><ColorTexture>Texture/$($p.Texture)</ColorTexture><AlphaBlend>$($p.Blend)</AlphaBlend><ZWrite>False</ZWrite><FadeInType>1</FadeInType><FadeIn><Frame>$($p.FadeIn)</Frame></FadeIn><FadeOutType>1</FadeOutType><FadeOut><Frame>$($p.FadeOut)</Frame></FadeOut></RendererCommonValues>" +
  "<DrawingValues><Sprite>$(Colour $p.From $p.To)</Sprite></DrawingValues><Name>$($p.Name)</Name><Children /></Node>"
}
# $count 0 = forever.
function Burst($name, $count, $every, $delay, $life, $children) {
  $generation = if ($count -eq 0) { '<MaxGeneration><Infinite>True</Infinite></MaxGeneration>' } else { "<MaxGeneration><Value>$count</Value></MaxGeneration>" }
  "<Node><CommonValues>$generation$(Range Life $life $life $life)$(Range GenerationTime $every $every $every)$(Range GenerationTimeOffset $delay $delay $delay)</CommonValues>" +
  "<RotationValues><Type>1</Type><PVA><Rotation><Y><Max>180</Max><Min>-180</Min></Y></Rotation></PVA></RotationValues>" +
  "<DrawingValues><Type>0</Type></DrawingValues><Name>$name</Name><Children>$children</Children></Node>"
}
function Export($name, $children, $frames, $loop) {
  $project = "<?xml version=`"1.0`" encoding=`"utf-8`"?><EffekseerProject><Root><Name>Root</Name><Children>$children</Children></Root><ToolVersion>1.30</ToolVersion><Version>3</Version><StartFrame>0</StartFrame><EndFrame>$frames</EndFrame><IsLoop>$loop</IsLoop></EffekseerProject>"
  $projectPath = Join-Path $out "$name.efkproj"
  ([xml]$project).Save($projectPath)
  $efk = Join-Path $out "$name.efk"
  Remove-Item $efk -ErrorAction SilentlyContinue
  $p = Start-Process $Effekseer -ArgumentList '-cui', '-in', "`"$projectPath`"", '-e', "`"$efk`"" -PassThru -Wait -WindowStyle Hidden
  if ($p.ExitCode -ne 0 -or -not (Test-Path $efk)) { throw "Effekseer export failed for $name ($($p.ExitCode))" }
}

$hot = @(255, 252, 235, 255)
$gold = @(255, 205, 110, 0)

# ----- ShardIdle: one glint every 7 frames, 1.5-3.5 units out, rising slowly, twinkling in and out -----
$glint = Puff @{ Name = 'Glint'; Life = @(60, 45, 75); Texture = 'Glint.png'; Blend = 2; FadeIn = 15; FadeOut = 30
  Location = @(@(2.5, 1.5, 3.5), @(0.0, -2.0, 2.0), $null); Velocity = @(@(0.0, -0.01, 0.01), @(0.03, 0.02, 0.045), $null)
  SizeFrom = @(0.35, 0.25, 0.45); SizeTo = @(0.15, 0.1, 0.2); From = $hot; To = $gold }
Export 'ShardIdle' (Burst 'Rising' 0 7 0 80 $glint) 120 'True'

# ----- ShardGet -----
$flash = Puff @{ Name = 'Flash'; Life = @(16, 16, 16); Texture = 'CloudPuff.png'; Blend = 2; FadeIn = 1; FadeOut = 13
  Location = @($null, $null, $null); Velocity = @($null, $null, $null)
  SizeFrom = @(2.0, 2.0, 2.0); SizeTo = @(6.5, 6.5, 6.5); From = $hot; To = $gold }
$ring = Puff @{ Name = 'Ring'; Life = @(22, 18, 26); Texture = 'Glint.png'; Blend = 2; FadeIn = 1; FadeOut = 12
  Location = @(@(0.5, 0.3, 0.7), $null, $null); Velocity = @(@(0.3, 0.24, 0.36), @(0.0, -0.03, 0.03), $null)
  SizeFrom = @(0.6, 0.5, 0.7); SizeTo = @(0.15, 0.1, 0.2); From = $hot; To = $gold }
$up = Puff @{ Name = 'Up'; Life = @(34, 26, 42); Texture = 'Glint.png'; Blend = 2; FadeIn = 2; FadeOut = 18
  Location = @(@(0.6, 0.0, 1.2), @(0.0, -0.5, 0.5), $null); Velocity = @(@(0.03, 0.0, 0.06), @(0.24, 0.16, 0.32), $null)
  Acceleration = @($null, @(-0.004, -0.005, -0.003), $null)
  SizeFrom = @(0.45, 0.35, 0.55); SizeTo = @(0.1, 0.08, 0.14); From = $hot; To = $gold }
Export 'ShardGet' ((Burst 'FlashOnce' 1 1 0 20 $flash) + (Burst 'RingOut' 20 0.1 0 30 $ring) + (Burst 'Rise' 14 0.5 1 45 $up)) 50 'False'
Get-ChildItem $out -Recurse -File | Select-Object @{ n = 'File'; e = { $_.FullName.Substring($out.Length + 1) } }, Length
