# Builds the flame jet's extra effects (BP_FlameJet; the user, 2026-11-22), at the vent, scale 1. The column itself
# stays the FlameJet effect and the warning the CageFire one:
#   SourceArt/Effects/FlameFx/FlameErupt.efk  the column bursting out: an orange flash and sparks thrown up and out
#   SourceArt/Effects/FlameFx/FlameSmoke.efk  the column gone: dark smoke puffing up from the vent, a few embers
# Units: 1 Effekseer unit = 20 cm, Y up (the vent's radius is 3.5). Textures copied from SunImpact.
#   powershell -File build_flame_effects.ps1 [-Effekseer <path to Effekseer.exe>]
param([string]$Effekseer = (Join-Path $env:USERPROFILE 'Desktop\Effekseer160Win\Effekseer160Win\Tool\Effekseer.exe'))
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\SourceArt\Effects'))
$out = Join-Path $root 'FlameFx'
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

$hot = @(255, 230, 160, 255)
$ember = @(255, 90, 20, 0)

# ----- FlameErupt: a flash at the vent and sparks thrown up and out, falling back -----
$flash = Puff @{ Name = 'Flash'; Life = @(14, 14, 14); Texture = 'CloudPuff.png'; Blend = 2; FadeIn = 1; FadeOut = 12
  Location = @($null, @(1.5, 1.5, 1.5), $null); Velocity = @($null, $null, $null)
  SizeFrom = @(4.0, 4.0, 4.0); SizeTo = @(9.0, 9.0, 9.0); From = @(255, 200, 110, 200); To = @(255, 80, 20, 0) }
$sparks = Puff @{ Name = 'Sparks'; Life = @(35, 25, 45); Texture = 'Glint.png'; Blend = 2; FadeIn = 1; FadeOut = 15
  Location = @(@(1.0, 0.2, 2.5), @(0.5, 0.0, 1.0), $null); Velocity = @(@(0.15, 0.05, 0.25), @(0.45, 0.3, 0.6), $null)
  Acceleration = @($null, @(-0.018, -0.022, -0.014), $null)
  SizeFrom = @(0.5, 0.35, 0.65); SizeTo = @(0.15, 0.1, 0.2); From = $hot; To = $ember }
Export 'FlameErupt' ((Burst 'FlashOnce' 1 1 0 16 $flash) + (Burst 'SparksOut' 26 0.15 0 50 $sparks)) 55

# ----- FlameSmoke: smoke puffing up from the vent as the column goes, a few embers drifting -----
$smoke = Puff @{ Name = 'Smoke'; Life = @(60, 50, 70); Texture = 'CloudPuff.png'; Blend = 1; FadeIn = 8; FadeOut = 40
  Location = @(@(1.0, 0.0, 2.5), @(1.0, 0.5, 2.0), $null); Velocity = @(@(0.02, 0.0, 0.04), @(0.08, 0.06, 0.11), $null)
  SizeFrom = @(2.5, 2.0, 3.0); SizeTo = @(7.0, 5.5, 8.5); From = @(70, 60, 55, 170); To = @(90, 80, 75, 0) }
$embers = Puff @{ Name = 'Embers'; Life = @(50, 40, 60); Texture = 'Glint.png'; Blend = 2; FadeIn = 2; FadeOut = 25
  Location = @(@(1.5, 0.0, 3.0), @(1.0, 0.5, 2.0), $null); Velocity = @(@(0.0, -0.02, 0.02), @(0.1, 0.06, 0.14), $null)
  SizeFrom = @(0.35, 0.25, 0.45); SizeTo = @(0.1, 0.08, 0.14); From = $hot; To = $ember }
Export 'FlameSmoke' ((Burst 'SmokeUp' 10 3 0 75 $smoke) + (Burst 'EmbersUp' 8 4 0 65 $embers)) 100
Get-ChildItem $out -Recurse -File | Select-Object @{ n = 'File'; e = { $_.FullName.Substring($out.Length + 1) } }, Length