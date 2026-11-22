# Builds the spider thread's effects (BP_SpiderThread; the user, 2026-11-22), silver-white like the thread:
#   SourceArt/Effects/ThreadFx/ThreadGrab.efk    caught hold of: a small flash and a ring of glints at the hand
#   SourceArt/Effects/ThreadFx/ThreadSnap.efk    it snaps: a red-white flash, bits of thread thrown out and falling
#   SourceArt/Effects/ThreadFx/ThreadReturn.efk  it is back: a flash at the top and glints running down the thread
#                                                (~14 m at scale 1, about the default Length 1500)
# Units: 1 Effekseer unit = 20 cm, Y up. Textures copied from SunImpact (CloudPuff, Glint).
#   powershell -File build_thread_effects.ps1 [-Effekseer <path to Effekseer.exe>]
param([string]$Effekseer = (Join-Path $env:USERPROFILE 'Desktop\Effekseer160Win\Effekseer160Win\Tool\Effekseer.exe'))
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\SourceArt\Effects'))
$out = Join-Path $root 'ThreadFx'
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

$white = @(250, 252, 255, 255)
$silver = @(185, 205, 255, 0)
$hotRed = @(255, 225, 215, 255)
$red = @(255, 70, 45, 0)

# ----- ThreadGrab -----
$flash = Puff @{ Name = 'Flash'; Life = @(12, 12, 12); Texture = 'CloudPuff.png'; Blend = 2; FadeIn = 1; FadeOut = 10
  Location = @($null, $null, $null); Velocity = @($null, $null, $null)
  SizeFrom = @(1.0, 1.0, 1.0); SizeTo = @(3.0, 3.0, 3.0); From = $white; To = $silver }
$ring = Puff @{ Name = 'Ring'; Life = @(18, 14, 22); Texture = 'Glint.png'; Blend = 2; FadeIn = 1; FadeOut = 10
  Location = @(@(0.3, 0.2, 0.4), @(0.0, -0.3, 0.3), $null); Velocity = @(@(0.2, 0.15, 0.25), @(0.0, -0.03, 0.03), $null)
  SizeFrom = @(0.45, 0.35, 0.55); SizeTo = @(0.1, 0.08, 0.14); From = $white; To = $silver }
Export 'ThreadGrab' ((Burst 'FlashOnce' 1 1 0 15 $flash) + (Burst 'RingOut' 14 0.1 0 25 $ring)) 30

# ----- ThreadSnap -----
$flash2 = Puff @{ Name = 'Flash'; Life = @(14, 14, 14); Texture = 'CloudPuff.png'; Blend = 2; FadeIn = 1; FadeOut = 12
  Location = @($null, $null, $null); Velocity = @($null, $null, $null)
  SizeFrom = @(1.5, 1.5, 1.5); SizeTo = @(4.5, 4.5, 4.5); From = $hotRed; To = $red }
$bits = Puff @{ Name = 'Bits'; Life = @(40, 32, 48); Texture = 'Glint.png'; Blend = 2; FadeIn = 1; FadeOut = 20
  Location = @(@(0.3, 0.1, 0.5), @(0.0, -1.0, 1.0), $null); Velocity = @(@(0.15, 0.08, 0.22), @(0.1, 0.0, 0.2), $null)
  Acceleration = @($null, @(-0.012, -0.015, -0.009), $null)
  SizeFrom = @(0.4, 0.3, 0.5); SizeTo = @(0.12, 0.08, 0.16); From = $hotRed; To = $silver }
Export 'ThreadSnap' ((Burst 'FlashOnce' 1 1 0 16 $flash2) + (Burst 'BitsOut' 18 0.1 0 50 $bits)) 55

# ----- ThreadReturn: glints running down from the top -----
$top = Puff @{ Name = 'Flash'; Life = @(20, 20, 20); Texture = 'CloudPuff.png'; Blend = 2; FadeIn = 3; FadeOut = 15
  Location = @($null, $null, $null); Velocity = @($null, $null, $null)
  SizeFrom = @(1.5, 1.5, 1.5); SizeTo = @(4.0, 4.0, 4.0); From = $white; To = $silver }
$down = Puff @{ Name = 'Down'; Life = @(45, 40, 48); Texture = 'Glint.png'; Blend = 2; FadeIn = 2; FadeOut = 15
  Location = @(@(0.0, -0.1, 0.1), $null, $null); Velocity = @($null, @(-1.6, -1.7, -1.5), $null)
  SizeFrom = @(1.2, 1.0, 1.4); SizeTo = @(0.6, 0.5, 0.7); From = $white; To = $silver }
Export 'ThreadReturn' ((Burst 'FlashOnce' 1 1 0 22 $top) + (Burst 'RunDown' 8 2 0 50 $down)) 60
Get-ChildItem $out -Recurse -File | Select-Object @{ n = 'File'; e = { $_.FullName.Substring($out.Length + 1) } }, Length
