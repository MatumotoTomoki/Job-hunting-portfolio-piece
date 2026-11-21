# Builds the lever's pull effect (BP_Lever; the user, 2026-11-20): SourceArt/Effects/LeverSpark/LeverSpark.efk, one
# shot, born at the lever's pivot (50 cm up). Everything waits 22 frames (0.37 s), the moment the handle lands with
# S_LeverPull's clunk:
#   Sparks  a burst of hot sparks thrown up and out from the pivot, falling back
#   Dust    a few small dust puffs at the base, drifting out and thinning
# Units: 1 Effekseer unit = 20 cm, Y up. Textures copied from SunImpact (CloudPuff, Glint).
#   powershell -File build_lever_spark_effect.ps1 [-Effekseer <path to Effekseer.exe>]
param([string]$Effekseer = (Join-Path $env:USERPROFILE 'Desktop\Effekseer160Win\Effekseer160Win\Tool\Effekseer.exe'))
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\SourceArt\Effects'))
$out = Join-Path $root 'LeverSpark'
New-Item -ItemType Directory -Force (Join-Path $out 'Texture') | Out-Null
foreach ($name in 'CloudPuff.png', 'Glint.png') { Copy-Item (Join-Path $root "SunImpact\Texture\$name") (Join-Path $out "Texture\$name") -Force }
$DELAY = 22

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
function Burst($name, $count, $every, $life, $children) {
  "<Node><CommonValues><MaxGeneration><Value>$count</Value></MaxGeneration>$(Range Life $life $life $life)$(Range GenerationTime $every $every $every)$(Range GenerationTimeOffset $DELAY $DELAY $DELAY)</CommonValues>" +
  "<RotationValues><Type>1</Type><PVA><Rotation><Y><Max>180</Max><Min>-180</Min></Y></Rotation></PVA></RotationValues>" +
  "<DrawingValues><Type>0</Type></DrawingValues><Name>$name</Name><Children>$children</Children></Node>"
}

$spark = Puff @{ Name = 'Spark'; Life = @(26, 18, 34); Texture = 'Glint.png'; Blend = 2; FadeIn = 1; FadeOut = 12
  Location = @(@(0.2, 0, 0.4), $null, $null); Velocity = @(@(0.14, 0.06, 0.24), @(0.22, 0.12, 0.32), $null)
  Acceleration = @($null, @(-0.02, -0.022, -0.018), $null)
  SizeFrom = @(0.45, 0.3, 0.6); SizeTo = @(0.1, 0.08, 0.14); From = @(255, 235, 160, 255); To = @(255, 110, 30, 0) }
$dust = Puff @{ Name = 'Dust'; Life = @(40, 32, 48); Texture = 'CloudPuff.png'; Blend = 1; FadeIn = 2; FadeOut = 30
  Location = @(@(1.0, 0.6, 1.4), @(-2.2, -2.2, -2.2), $null); Velocity = @(@(0.05, 0.03, 0.08), @(0.01, 0.0, 0.02), $null)
  SizeFrom = @(1.0, 0.8, 1.2); SizeTo = @(2.4, 2.0, 2.8); From = @(200, 185, 160, 170); To = @(210, 200, 185, 0) }
$children = (Burst 'SparkBurst' 14 0.2 40 $spark) + (Burst 'DustRing' 6 0.5 50 $dust)
$project = "<?xml version=`"1.0`" encoding=`"utf-8`"?><EffekseerProject><Root><Name>Root</Name><Children>$children</Children></Root><ToolVersion>1.30</ToolVersion><Version>3</Version><StartFrame>0</StartFrame><EndFrame>90</EndFrame><IsLoop>False</IsLoop></EffekseerProject>"
$xml = [xml]$project
$projectPath = Join-Path $out 'LeverSpark.efkproj'
$xml.Save($projectPath)
$efk = Join-Path $out 'LeverSpark.efk'
Remove-Item $efk -ErrorAction SilentlyContinue
$p = Start-Process $Effekseer -ArgumentList '-cui', '-in', "`"$projectPath`"", '-e', "`"$efk`"" -PassThru -Wait -WindowStyle Hidden
if ($p.ExitCode -ne 0 -or -not (Test-Path $efk)) { throw "Effekseer export failed ($($p.ExitCode))" }
Get-ChildItem $out -Recurse -File | Select-Object @{ n = 'File'; e = { $_.FullName.Substring($out.Length + 1) } }, Length
