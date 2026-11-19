# Builds the wind's look for BP_WindZone (area 3; the user, 2026-11-18: the old crossed streak planes were too hard to
# read): SourceArt/Effects/Wind/WindFlow.efk, a looping Effekseer effect that fills BP_WindZone's 100 cm box, which the
# actor's scale stretches to the zone's size (so lines run the zone's whole length whatever its size; an updraft's box
# is turned pitch 90, and the lines go up with it).
#   WindLineV / WindLineH  thin white lines of wind racing along local X through the box (Effekseer X), fading in and
#                          out: flat quads (Fixed billboards) in the vertical and the horizontal plane through X, so
#                          they read as lines from any side, not dots.
#   Wisps                  a few faint puffs of cloud drifting through with them.
# Units: 1 Effekseer unit = 20 cm; Effekseer's Y is UE's up; the box is -2.5..2.5 units each way. Frames are 1/60 s.
# Textures (drawn here): Texture/WindLine.png (a tapered streak, bright at its head), Texture/WindPuff.png (GearSteam's
# puff). Import: Scripts/setup_wind_fx.py. Run:
#   powershell -File build_wind_effect.ps1 [-Effekseer <path to Effekseer.exe>]
param([string]$Effekseer = (Join-Path $env:USERPROFILE 'Desktop\Effekseer160Win\Effekseer160Win\Tool\Effekseer.exe'))
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\SourceArt\Effects'))
$out = Join-Path $root 'Wind'
New-Item -ItemType Directory -Force (Join-Path $out 'Texture') | Out-Null
Copy-Item (Join-Path $root 'GearSteam\Texture\SteamPuff.png') (Join-Path $out 'Texture\WindPuff.png') -Force

Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @'
using System;
using System.Drawing;
using System.Drawing.Imaging;
public static class WindTexture {
    // A streak along u: thin across v, tapering to nothing at its tail (u = 0) and fading fast at its head (u = 1).
    public static void Line(string path) {
        int w = 256, h = 32;
        var bmp = new Bitmap(w, h, PixelFormat.Format32bppArgb);
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++) {
                double u = (x + 0.5) / w, v = (y + 0.5) / h - 0.5;
                double along = Math.Pow(u, 1.6) * Math.Min(1.0, (1.0 - u) / 0.12);
                double across = Math.Exp(-v * v / (0.018 + 0.01 * u));
                double a = Math.Max(0.0, Math.Min(1.0, along * across));
                bmp.SetPixel(x, y, Color.FromArgb((int)(a * 255.0 + 0.5), 255, 255, 255));
            }
        bmp.Save(path, ImageFormat.Png);
        bmp.Dispose();
    }
}
'@
[WindTexture]::Line((Join-Path $out 'Texture\WindLine.png'))

function Range($tag, $center, $min, $max) { "<$tag><Center>$center</Center><Max>$max</Max><Min>$min</Min></$tag>" }
function Fade($from, $to) {
  $parts = foreach ($pair in @(@('Start', $from), @('End', $to))) {
    $c = $pair[1]
    "<$($pair[0])>$(Range R $c[0] $c[0] $c[0])$(Range G $c[1] $c[1] $c[1])$(Range B $c[2] $c[2] $c[2])$(Range A $c[3] $c[3] $c[3])</$($pair[0])>"
  }
  "<ColorAll>2</ColorAll><ColorAll_Easing>$($parts -join '')</ColorAll_Easing>"
}
# A wind line: born at the box's back end (X -2.6) anywhere across it, flying through to the front in its life.
function Line($name, $tilt) {
  "<Node><CommonValues><MaxGeneration><Infinite>True</Infinite></MaxGeneration>$(Range Life 36 28 44)$(Range GenerationTime 1.2 1.2 1.2)</CommonValues>" +
  "<LocationValues><Type>1</Type><PVA><Location>$(Range X -2.6 -2.8 -2.2)$(Range Y 0 -2.3 2.3)$(Range Z 0 -2.3 2.3)</Location>" +
  "<Velocity>$(Range X 0.16 0.13 0.2)</Velocity></PVA></LocationValues>" +
  "<RotationValues><Type>0</Type><Fixed><Rotation><X>$tilt</X></Rotation></Fixed></RotationValues>" +
  "<ScalingValues><Type>1</Type><PVA><Scale>$(Range X 1.1 0.7 1.5)$(Range Y 0.05 0.035 0.065)$(Range Z 1 1 1)</Scale></PVA></ScalingValues>" +
  "<RendererCommonValues><ColorTexture>Texture/WindLine.png</ColorTexture><AlphaBlend>2</AlphaBlend><ZWrite>False</ZWrite>" +
  "<FadeInType>1</FadeInType><FadeIn><Frame>6</Frame></FadeIn><FadeOutType>1</FadeOutType><FadeOut><Frame>10</Frame></FadeOut></RendererCommonValues>" +
  "<DrawingValues><Sprite><Billboard>2</Billboard>$(Fade @(235, 245, 255, 210) @(235, 245, 255, 170))</Sprite></DrawingValues><Name>$name</Name><Children /></Node>"
}
$wisps = "<Node><CommonValues><MaxGeneration><Infinite>True</Infinite></MaxGeneration>$(Range Life 50 40 60)$(Range GenerationTime 5 5 5)</CommonValues>" +
  "<LocationValues><Type>1</Type><PVA><Location>$(Range X -2.4 -2.6 -1.8)$(Range Y 0 -2.0 2.0)$(Range Z 0 -2.0 2.0)</Location>" +
  "<Velocity>$(Range X 0.1 0.08 0.12)</Velocity></PVA></LocationValues>" +
  "<RotationValues><Type>1</Type><PVA><Rotation><Z><Max>180</Max><Min>-180</Min></Z></Rotation></PVA></RotationValues>" +
  "<ScalingValues><Type>4</Type><SingleEasing>$(Range Start 0.5 0.4 0.6)$(Range End 0.9 0.7 1.1)<StartSpeed>20</StartSpeed><EndSpeed>-20</EndSpeed></SingleEasing></ScalingValues>" +
  "<RendererCommonValues><ColorTexture>Texture/WindPuff.png</ColorTexture><AlphaBlend>1</AlphaBlend><ZWrite>False</ZWrite>" +
  "<FadeInType>1</FadeInType><FadeIn><Frame>12</Frame></FadeIn><FadeOutType>1</FadeOutType><FadeOut><Frame>20</Frame></FadeOut></RendererCommonValues>" +
  "<DrawingValues><Sprite>$(Fade @(250, 252, 255, 80) @(250, 252, 255, 50))</Sprite></DrawingValues><Name>Wisps</Name><Children /></Node>"
$project = @"
<?xml version="1.0" encoding="utf-8"?>
<EffekseerProject>
  <Root>
    <Name>Root</Name>
    <Children>$(Line 'WindLineV' 0)$(Line 'WindLineH' 90)$wisps</Children>
  </Root>
  <ToolVersion>1.30</ToolVersion>
  <Version>3</Version>
  <StartFrame>0</StartFrame>
  <EndFrame>240</EndFrame>
  <IsLoop>True</IsLoop>
</EffekseerProject>
"@
$xml = [xml]$project
$projectPath = Join-Path $out 'WindFlow.efkproj'
$xml.Save($projectPath)
$efk = Join-Path $out 'WindFlow.efk'
Remove-Item $efk -ErrorAction SilentlyContinue
$p = Start-Process $Effekseer -ArgumentList '-cui', '-in', "`"$projectPath`"", '-e', "`"$efk`"" -PassThru -Wait -WindowStyle Hidden
if ($p.ExitCode -ne 0 -or -not (Test-Path $efk)) { throw "Effekseer export failed ($($p.ExitCode))" }
Get-ChildItem $out -Recurse -File | Select-Object @{ n = 'File'; e = { $_.FullName.Substring($out.Length + 1) } }, Length
