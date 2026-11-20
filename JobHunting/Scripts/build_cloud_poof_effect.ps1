# Builds the vanishing cloud's effects (BP_VanishCloud, area 3; the user, 2026-11-19), into
# SourceArt/Effects/CloudPoof (the puff texture copied from GearSteam, a glint drawn here):
#   CloudPoof  one shot as the cloud vanishes: soft pastel puffs burst out all round and a little up, swelling and
#              thinning, with a few gold glints.
#   CloudForm  one shot as it comes back: puffs drift in from all round to the middle, shrinking, then a soft glow.
# The emitter sits at the cloud's middle; the actor's scale (the cloud's size) stretches the ring with it.
# Units: 1 Effekseer unit = 20 cm, Y up; the cloud is 100 cm (5 units) across at scale 1. Import: setup_vanish_cloud_look.py.
#   powershell -File build_cloud_poof_effect.ps1 [-Effekseer <path to Effekseer.exe>]
param([string]$Effekseer = (Join-Path $env:USERPROFILE 'Desktop\Effekseer160Win\Effekseer160Win\Tool\Effekseer.exe'))
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\SourceArt\Effects'))
$out = Join-Path $root 'CloudPoof'
New-Item -ItemType Directory -Force (Join-Path $out 'Texture') | Out-Null
Copy-Item (Join-Path $root 'GearSteam\Texture\SteamPuff.png') (Join-Path $out 'Texture\CloudPuff.png') -Force
Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @'
using System;
using System.Drawing;
using System.Drawing.Imaging;
public static class GlintTexture {
    // A four-pointed glint: a bright core and two thin crossing rays.
    public static void Draw(string path) {
        int s = 64;
        var bmp = new Bitmap(s, s, PixelFormat.Format32bppArgb);
        for (int y = 0; y < s; y++)
            for (int x = 0; x < s; x++) {
                double u = (x + 0.5) / s - 0.5, v = (y + 0.5) / s - 0.5;
                double r = Math.Sqrt(u * u + v * v) * 2.0;
                double core = Math.Exp(-r * r * 30.0);
                double rays = Math.Exp(-Math.Abs(u) * 60.0) * Math.Max(0.0, 1.0 - Math.Abs(v) * 2.0)
                            + Math.Exp(-Math.Abs(v) * 60.0) * Math.Max(0.0, 1.0 - Math.Abs(u) * 2.0);
                double a = Math.Min(1.0, core + 0.8 * rays);
                bmp.SetPixel(x, y, Color.FromArgb((int)(a * 255.0 + 0.5), 255, 255, 255));
            }
        bmp.Save(path, ImageFormat.Png);
        bmp.Dispose();
    }
}
'@
[GlintTexture]::Draw((Join-Path $out 'Texture\Glint.png'))

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
  "<Node><CommonValues><MaxGeneration><Value>$count</Value></MaxGeneration>$(Range Life $life $life $life)$(Range GenerationTime $every $every $every)</CommonValues>" +
  "<RotationValues><Type>1</Type><PVA><Rotation><Y><Max>180</Max><Min>-180</Min></Y></Rotation></PVA></RotationValues>" +
  "<DrawingValues><Type>0</Type></DrawingValues><Name>$name</Name><Children>$children</Children></Node>"
}
function Project($children, $end) {
  "<?xml version=`"1.0`" encoding=`"utf-8`"?><EffekseerProject><Root><Name>Root</Name><Children>$children</Children></Root><ToolVersion>1.30</ToolVersion><Version>3</Version><StartFrame>0</StartFrame><EndFrame>$end</EndFrame><IsLoop>False</IsLoop></EffekseerProject>"
}
$PINK = @(255, 228, 238, 220); $PINK_OUT = @(255, 240, 248, 0)

# ----- CloudPoof -----
$poof = Puff @{ Name = 'Poof'; Life = @(42, 34, 50); Texture = 'CloudPuff.png'; Blend = 1; FadeIn = 1; FadeOut = 30
  Location = @(@(1.6, 0.8, 2.4), @(0.2, 0, 0.5), $null); Velocity = @(@(0.12, 0.08, 0.17), @(0.04, 0.02, 0.07), $null)
  Acceleration = @(@(-0.0025, -0.003, -0.002), $null, $null)
  SizeFrom = @(1.6, 1.3, 2.0); SizeTo = @(3.2, 2.6, 3.8); From = $PINK; To = $PINK_OUT }
$glint = Puff @{ Name = 'Glint'; Life = @(24, 18, 30); Texture = 'Glint.png'; Blend = 2; FadeIn = 2; FadeOut = 14
  Location = @(@(1.4, 0.5, 2.3), @(0.4, 0, 0.9), $null); Velocity = @(@(0.06, 0.03, 0.09), @(0.05, 0.02, 0.08), $null)
  SizeFrom = @(0.5, 0.35, 0.65); SizeTo = @(0.15, 0.1, 0.2); From = @(255, 225, 150, 255); To = @(255, 200, 120, 0) }
$poofProject = Project ((Burst 'PoofRing' 22 0.25 55 $poof) + (Burst 'GlintRing' 8 0.5 35 $glint)) 70

# ----- CloudForm -----
$gather = Puff @{ Name = 'Gather'; Life = @(26, 22, 30); Texture = 'CloudPuff.png'; Blend = 1; FadeIn = 8; FadeOut = 8
  Location = @(@(3.2, 2.8, 3.6), @(0.3, 0, 0.6), $null); Velocity = @(@(-0.11, -0.13, -0.09), @(-0.005, -0.01, 0), $null)
  SizeFrom = @(2.2, 1.8, 2.6); SizeTo = @(0.9, 0.7, 1.1); From = @(255, 235, 245, 200); To = @(255, 240, 248, 120) }
$bloom = "<Node><CommonValues><MaxGeneration><Value>1</Value></MaxGeneration>$(Range Life 26 26 26)$(Range GenerationTime 1 1 1)$(Range GenerationTimeOffset 18 18 18)</CommonValues>" +
  "<LocationValues><Type>0</Type><Fixed><Location><Y>0.3</Y></Location></Fixed></LocationValues>" +
  "<ScalingValues><Type>4</Type><SingleEasing>$(Range Start 2 2 2)$(Range End 5 5 5)<StartSpeed>20</StartSpeed><EndSpeed>-20</EndSpeed></SingleEasing></ScalingValues>" +
  "<RendererCommonValues><ColorTexture>Texture/CloudPuff.png</ColorTexture><AlphaBlend>2</AlphaBlend><ZWrite>False</ZWrite><FadeInType>1</FadeInType><FadeIn><Frame>4</Frame></FadeIn><FadeOutType>1</FadeOutType><FadeOut><Frame>18</Frame></FadeOut></RendererCommonValues>" +
  "<DrawingValues><Sprite>$(Colour @(255, 220, 190, 150) @(255, 230, 210, 0))</Sprite></DrawingValues><Name>Bloom</Name><Children /></Node>"
$formProject = Project ((Burst 'GatherRing' 18 0.5 35 $gather) + $bloom) 60

foreach ($variant in @(@('CloudPoof', $poofProject), @('CloudForm', $formProject))) {
  $xml = [xml]$variant[1]
  $projectPath = Join-Path $out ($variant[0] + '.efkproj')
  $xml.Save($projectPath)
  $efk = Join-Path $out ($variant[0] + '.efk')
  Remove-Item $efk -ErrorAction SilentlyContinue
  $p = Start-Process $Effekseer -ArgumentList '-cui', '-in', "`"$projectPath`"", '-e', "`"$efk`"" -PassThru -Wait -WindowStyle Hidden
  if ($p.ExitCode -ne 0 -or -not (Test-Path $efk)) { throw "Effekseer export failed for $($variant[0]) ($($p.ExitCode))" }
}
Get-ChildItem $out -Recurse -File | Select-Object @{ n = 'File'; e = { $_.FullName.Substring($out.Length + 1) } }, Length
