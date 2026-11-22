# Builds the crumbling floor's effects (BP_FallingFloor; the user, 2026-11-22), sized for its 3 x 3 m slab at scale 1:
#   SourceArt/Effects/FloorFx/FloorCrack.efk  stepped on (the ~1 s shake): grit trickling and dust puffing from under
#                                             its edges
#   SourceArt/Effects/FloorFx/FloorFall.efk   it gives way: a burst of dust spreading out and rubble falling
# (Its coming back keeps the FootSmoke it already had.)
# Units: 1 Effekseer unit = 20 cm, Y up (the slab's half width is 7.5). Texture copied from SunImpact (CloudPuff).
#   powershell -File build_floor_effects.ps1 [-Effekseer <path to Effekseer.exe>]
param([string]$Effekseer = (Join-Path $env:USERPROFILE 'Desktop\Effekseer160Win\Effekseer160Win\Tool\Effekseer.exe'))
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\SourceArt\Effects'))
$out = Join-Path $root 'FloorFx'
New-Item -ItemType Directory -Force (Join-Path $out 'Texture') | Out-Null
Copy-Item (Join-Path $root 'SunImpact\Texture\CloudPuff.png') (Join-Path $out 'Texture\CloudPuff.png') -Force

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
function Burst($name, $count, $every, $delay, $life, $children) {
  "<Node><CommonValues><MaxGeneration><Value>$count</Value></MaxGeneration>$(Range Life $life $life $life)$(Range GenerationTime $every $every $every)$(Range GenerationTimeOffset $delay $delay $delay)</CommonValues>" +
  "<RotationValues><Type>1</Type><PVA><Rotation><Y><Max>180</Max><Min>-180</Min></Y></Rotation></PVA></RotationValues>" +
  "<DrawingValues><Type>0</Type></DrawingValues><Name>$name</Name><Children>$children</Children></Node>"
}
function Export($name, $children, $frames) {
  $project = "<?xml version=`"1.0`" encoding=`"utf-8`"?><EffekseerProject><Root><Name>Root</Name><Children>$children</Children></Root><ToolVersion>1.30</ToolVersion><Version>3</Version><StartFrame>0</StartFrame><EndFrame>$frames</EndFrame><IsLoop>False</IsLoop></EffekseerProject>"
  $projectPath = Join-Path $out "$name.efkproj"
  ([xml]$project).Save($projectPath)
  $efk = Join-Path $out "$name.efk"
  Remove-Item $efk -ErrorAction SilentlyContinue
  $p = Start-Process $Effekseer -ArgumentList '-cui', '-in', "`"$projectPath`"", '-e', "`"$efk`"" -PassThru -Wait -WindowStyle Hidden
  if ($p.ExitCode -ne 0 -or -not (Test-Path $efk)) { throw "Effekseer export failed for $name ($($p.ExitCode))" }
}

# Alpha blended (1): dust and grit darken what is behind them.
$dust = @(210, 202, 188, 150)
$dustEnd = @(210, 202, 188, 0)
$grit = @(105, 96, 86, 255)
$gritEnd = @(105, 96, 86, 0)

# ----- FloorCrack: ~1 s, under the slab's edges -----
$trickle = Puff @{ Name = 'Grit'; Life = @(30, 24, 36); Texture = 'CloudPuff.png'; Blend = 1; FadeIn = 1; FadeOut = 10
  Location = @(@(6.0, 3.5, 7.5), @(-0.7, -0.9, -0.5), $null); Velocity = @($null, @(-0.04, -0.08, 0.0), $null)
  Acceleration = @($null, @(-0.02, -0.025, -0.015), $null)
  SizeFrom = @(0.35, 0.25, 0.45); SizeTo = @(0.25, 0.15, 0.3); From = $grit; To = $gritEnd }
$puff = Puff @{ Name = 'Dust'; Life = @(40, 32, 48); Texture = 'CloudPuff.png'; Blend = 1; FadeIn = 6; FadeOut = 25
  Location = @(@(6.5, 5.0, 8.0), @(-0.6, -0.8, -0.4), $null); Velocity = @(@(0.03, 0.01, 0.05), @(-0.02, -0.04, 0.0), $null)
  SizeFrom = @(2.0, 1.5, 2.5); SizeTo = @(4.5, 3.5, 5.5); From = $dust; To = $dustEnd }
Export 'FloorCrack' ((Burst 'Trickle' 20 3 0 40 $trickle) + (Burst 'Puffs' 10 5 0 50 $puff)) 100

# ----- FloorFall: a burst at the slab's place -----
$cloud = Puff @{ Name = 'Cloud'; Life = @(55, 45, 65); Texture = 'CloudPuff.png'; Blend = 1; FadeIn = 3; FadeOut = 35
  Location = @(@(4.0, 1.0, 7.5), @(0.0, -0.6, 0.4), $null); Velocity = @(@(0.1, 0.06, 0.14), @(-0.02, -0.05, 0.02), $null)
  SizeFrom = @(3.0, 2.5, 3.5); SizeTo = @(8.0, 6.5, 9.5); From = $dust; To = $dustEnd }
$rubble = Puff @{ Name = 'Rubble'; Life = @(50, 40, 60); Texture = 'CloudPuff.png'; Blend = 1; FadeIn = 1; FadeOut = 15
  Location = @(@(4.0, 0.5, 7.0), @(0.0, -0.3, 0.3), $null); Velocity = @(@(0.08, 0.03, 0.14), @(0.06, 0.0, 0.12), $null)
  Acceleration = @($null, @(-0.022, -0.026, -0.018), $null)
  SizeFrom = @(0.8, 0.5, 1.1); SizeTo = @(0.6, 0.4, 0.8); From = $grit; To = $gritEnd }
Export 'FloorFall' ((Burst 'CloudOut' 16 0.2 0 70 $cloud) + (Burst 'RubbleOut' 24 0.2 0 65 $rubble)) 75
Get-ChildItem $out -Recurse -File | Select-Object @{ n = 'File'; e = { $_.FullName.Substring($out.Length + 1) } }, Length
