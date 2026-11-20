# Builds the tower sun's landing effect (BP_TowerSun / BP_SunMarker, area 4; the user, 2026-11-20):
# SourceArt/Effects/SunImpact/SunImpact.efk, one shot, born on the ground where the ball lands:
#   Flash   a bright warm burst at the ground, gone in a third of a second
#   Shock   a thin ring of light lying flat on the ground, racing out to ~5 m and fading
#   Shock2  a slower, smaller orange ring behind it
#   Dust    pale dust puffs rolling out along the ground all round, swelling and thinning
#   Embers  sparks of fire thrown up and out, falling back
# Units: 1 Effekseer unit = 20 cm, Y up. Textures: CloudPuff and Glint copied from CloudPoof; ShockRing drawn here.
#   powershell -File build_sun_impact_effect.ps1 [-Effekseer <path to Effekseer.exe>]
param([string]$Effekseer = (Join-Path $env:USERPROFILE 'Desktop\Effekseer160Win\Effekseer160Win\Tool\Effekseer.exe'))
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\SourceArt\Effects'))
$out = Join-Path $root 'SunImpact'
New-Item -ItemType Directory -Force (Join-Path $out 'Texture') | Out-Null
foreach ($name in 'CloudPuff.png', 'Glint.png') { Copy-Item (Join-Path $root "CloudPoof\Texture\$name") (Join-Path $out "Texture\$name") -Force }
Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @'
using System;
using System.Drawing;
using System.Drawing.Imaging;
public static class RingTexture {
    // A thin bright ring near the edge, soft on both sides, a faint glow inside it.
    public static void Draw(string path) {
        int s = 256;
        var bmp = new Bitmap(s, s, PixelFormat.Format32bppArgb);
        for (int y = 0; y < s; y++)
            for (int x = 0; x < s; x++) {
                double u = (x + 0.5) / s - 0.5, v = (y + 0.5) / s - 0.5;
                double r = Math.Sqrt(u * u + v * v) * 2.0;
                double ring = Math.Exp(-Math.Pow((r - 0.9) / 0.035, 2.0));
                double inner = r < 0.9 ? 0.25 * Math.Pow(r / 0.9, 3.0) : 0.0;
                double a = Math.Min(1.0, ring + inner);
                bmp.SetPixel(x, y, Color.FromArgb((int)(a * 255.0 + 0.5), 255, 255, 255));
            }
        bmp.Save(path, ImageFormat.Png);
        bmp.Dispose();
    }
}
'@
[RingTexture]::Draw((Join-Path $out 'Texture\ShockRing.png'))

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
function Flat($name, $life, $sizeFrom, $sizeTo, $from, $to, $fadeOut) {
  # One sprite lying flat on the ground (a Fixed billboard turned flat), swelling fast then slowing.
  "<Node><CommonValues><MaxGeneration><Value>1</Value></MaxGeneration>$(Range Life $life $life $life)</CommonValues>" +
  "<LocationValues><Type>0</Type><Fixed><Location><Y>0.15</Y></Location></Fixed></LocationValues>" +
  "<RotationValues><Type>0</Type><Fixed><Rotation><X>90</X></Rotation></Fixed></RotationValues>" +
  "<ScalingValues><Type>4</Type><SingleEasing>$(Range Start $sizeFrom $sizeFrom $sizeFrom)$(Range End $sizeTo $sizeTo $sizeTo)<StartSpeed>40</StartSpeed><EndSpeed>-40</EndSpeed></SingleEasing></ScalingValues>" +
  "<RendererCommonValues><ColorTexture>Texture/ShockRing.png</ColorTexture><AlphaBlend>2</AlphaBlend><ZWrite>False</ZWrite><FadeOutType>1</FadeOutType><FadeOut><Frame>$fadeOut</Frame></FadeOut></RendererCommonValues>" +
  "<DrawingValues><Sprite><Billboard>2</Billboard>$(Colour $from $to)</Sprite></DrawingValues><Name>$name</Name><Children /></Node>"
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
  "<Node><CommonValues><MaxGeneration><Value>$count</Value></MaxGeneration>$(Range Life $life $life $life)$(Range GenerationTime $every $every $every)</CommonValues>" +
  "<RotationValues><Type>1</Type><PVA><Rotation><Y><Max>180</Max><Min>-180</Min></Y></Rotation></PVA></RotationValues>" +
  "<DrawingValues><Type>0</Type></DrawingValues><Name>$name</Name><Children>$children</Children></Node>"
}

$shock = Flat 'Shock' 26 2 26 @(255, 245, 215, 255) @(255, 200, 120, 0) 20
$shock2 = Flat 'Shock2' 36 1.5 16 @(255, 150, 50, 230) @(255, 90, 20, 0) 28
$flash = Puff @{ Name = 'Flash'; Life = @(10, 10, 10); Texture = 'CloudPuff.png'; Blend = 2; FadeIn = 1; FadeOut = 8
  Location = @($null, @(1.5, 1.5, 1.5), $null); Velocity = @($null, $null, $null)
  SizeFrom = @(4, 4, 4); SizeTo = @(12, 12, 12); From = @(255, 240, 200, 255); To = @(255, 180, 90, 0) }
$dust = Puff @{ Name = 'Dust'; Life = @(55, 45, 65); Texture = 'CloudPuff.png'; Blend = 1; FadeIn = 2; FadeOut = 40
  Location = @(@(2.5, 2.0, 3.0), @(0.4, 0.2, 0.7), $null); Velocity = @(@(0.32, 0.24, 0.4), @(0.04, 0.02, 0.06), $null)
  Acceleration = @(@(-0.0055, -0.0065, -0.0045), @(-0.0004, -0.0006, -0.0002), $null)
  SizeFrom = @(2.2, 1.8, 2.6); SizeTo = @(5.5, 4.5, 6.5); From = @(225, 205, 175, 200); To = @(235, 220, 200, 0) }
$ember = Puff @{ Name = 'Ember'; Life = @(34, 26, 42); Texture = 'Glint.png'; Blend = 2; FadeIn = 1; FadeOut = 16
  Location = @(@(1.0, 0.5, 1.5), @(0.5, 0.3, 0.8), $null); Velocity = @(@(0.18, 0.1, 0.28), @(0.32, 0.22, 0.42), $null)
  Acceleration = @($null, @(-0.016, -0.018, -0.014), $null)
  SizeFrom = @(0.7, 0.5, 0.9); SizeTo = @(0.2, 0.15, 0.25); From = @(255, 230, 150, 255); To = @(255, 120, 40, 0) }
$children = $flash + $shock + $shock2 + (Burst 'DustRing' 24 0.2 70 $dust) + (Burst 'EmberRing' 18 0.25 45 $ember)
$project = "<?xml version=`"1.0`" encoding=`"utf-8`"?><EffekseerProject><Root><Name>Root</Name><Children>$children</Children></Root><ToolVersion>1.30</ToolVersion><Version>3</Version><StartFrame>0</StartFrame><EndFrame>80</EndFrame><IsLoop>False</IsLoop></EffekseerProject>"
$xml = [xml]$project
$projectPath = Join-Path $out 'SunImpact.efkproj'
$xml.Save($projectPath)
$efk = Join-Path $out 'SunImpact.efk'
Remove-Item $efk -ErrorAction SilentlyContinue
$p = Start-Process $Effekseer -ArgumentList '-cui', '-in', "`"$projectPath`"", '-e', "`"$efk`"" -PassThru -Wait -WindowStyle Hidden
if ($p.ExitCode -ne 0 -or -not (Test-Path $efk)) { throw "Effekseer export failed ($($p.ExitCode))" }
Get-ChildItem $out -Recurse -File | Select-Object @{ n = 'File'; e = { $_.FullName.Substring($out.Length + 1) } }, Length
