# Builds the timed platform's effects (BP_TimedPlatform; the user, 2026-11-22), sized for its 3 x 3 m slab at scale 1,
# pale white-blue glints:
#   SourceArt/Effects/TimedFx/TimedVanish.efk  fading out: glints lift off all over the slab and drift up as it goes
#   SourceArt/Effects/TimedFx/TimedAppear.efk  solid again: a soft flash and a ring of glints running out
# Units: 1 Effekseer unit = 20 cm, Y up (the slab's half width is 7.5). Textures copied from SunImpact.
#   powershell -File build_timed_effects.ps1 [-Effekseer <path to Effekseer.exe>]
param([string]$Effekseer = (Join-Path $env:USERPROFILE 'Desktop\Effekseer160Win\Effekseer160Win\Tool\Effekseer.exe'))
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\SourceArt\Effects'))
$out = Join-Path $root 'TimedFx'
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

$bright = @(235, 245, 255, 255)
$pale = @(150, 190, 255, 0)

# ----- TimedVanish: glints all over the slab (radius 0..7), lifting off over the 0.5 s fade -----
$lift = Puff @{ Name = 'Lift'; Life = @(40, 32, 48); Texture = 'Glint.png'; Blend = 2; FadeIn = 3; FadeOut = 25
  Location = @(@(4.0, 0.5, 7.0), @(0.6, 0.4, 0.8), $null); Velocity = @(@(0.0, -0.01, 0.01), @(0.06, 0.04, 0.09), $null)
  SizeFrom = @(0.7, 0.5, 0.9); SizeTo = @(0.2, 0.15, 0.3); From = $bright; To = $pale }
Export 'TimedVanish' (Burst 'LiftOff' 28 1 0 50 $lift) 75

# ----- TimedAppear: solid again (2026-11-22, the user: mark the moment it can be stood on) - at once a soft flash
# over the slab and a ring of glints running out along its edge and rising a little -----
$flash = Puff @{ Name = 'Flash'; Life = @(18, 18, 18); Texture = 'CloudPuff.png'; Blend = 2; FadeIn = 1; FadeOut = 15
  Location = @($null, @(0.6, 0.6, 0.6), $null); Velocity = @($null, $null, $null)
  SizeFrom = @(6.0, 6.0, 6.0); SizeTo = @(10.0, 10.0, 10.0); From = @(210, 230, 255, 130); To = @(150, 190, 255, 0) }
$ring = Puff @{ Name = 'Ring'; Life = @(26, 22, 30); Texture = 'Glint.png'; Blend = 2; FadeIn = 1; FadeOut = 14
  Location = @(@(6.5, 6.0, 7.0), @(0.6, 0.5, 0.7), $null); Velocity = @(@(0.12, 0.09, 0.15), @(0.08, 0.05, 0.11), $null)
  SizeFrom = @(0.8, 0.6, 1.0); SizeTo = @(0.2, 0.15, 0.3); From = $bright; To = $pale }
Export 'TimedAppear' ((Burst 'FlashOnce' 1 1 0 20 $flash) + (Burst 'RingOut' 24 0.05 0 32 $ring)) 40
Get-ChildItem $out -Recurse -File | Select-Object @{ n = 'File'; e = { $_.FullName.Substring($out.Length + 1) } }, Length
