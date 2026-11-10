# Builds the flame jet effect for BP_FlameJet: draws its textures, writes FlameJet.efkproj and exports FlameJet.efk with
# Effekseer's command line, into SourceArt/Effects/FlameJet. Import into UE with Scripts/import_flame_jet.py.
# Sizes: the UE import scales Effekseer units by 20 and maps UE up to Effekseer's Y, so the 4 m column BP_FlameJet's
# HitBox covers is 20 units up Y. Puffs shoot up at about 0.85 units a frame and live about 25 frames: the column
# stands full height within half a second of the jet starting. Layers, back to front:
#   BaseGlow  a glow at the vent
#   Haze      wide, slow deep-red heat around the column
#   Smoke     dark smoke leaving the top
#   Flame     the main orange flames
#   Core      a narrow yellow-white core
#   Embers    sparks thrown up out of the jet
# Everything loops for as long as the emitter is active. Run:
#   powershell -File build_flame_jet_effect.ps1 [-Effekseer <path to Effekseer.exe>]
param([string]$Effekseer = (Join-Path $env:USERPROFILE 'Desktop\Effekseer160Win\Effekseer160Win\Tool\Effekseer.exe'))
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$out = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\SourceArt\Effects\FlameJet'))
New-Item -ItemType Directory -Force (Join-Path $out 'Texture') | Out-Null

Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @'
using System;
using System.Drawing;
using System.Drawing.Imaging;

public static class FlameJetTextures {
    static void Save(string path, int size, Func<double, double, double> f) {
        var bmp = new Bitmap(size, size, PixelFormat.Format32bppArgb);
        for (int y = 0; y < size; y++)
            for (int x = 0; x < size; x++) {
                double a = Math.Max(0.0, Math.Min(1.0, f((x + 0.5) / size, (y + 0.5) / size)));
                bmp.SetPixel(x, y, Color.FromArgb((int)(a * 255.0 + 0.5), 255, 255, 255));
            }
        bmp.Save(path, ImageFormat.Png);
        bmp.Dispose();
    }

    static double Smooth(double t) { return t * t * (3.0 - 2.0 * t); }

    static double Noise(double u, double v, int cellsX, int cellsY, int seed) {
        double x = u * cellsX, y = v * cellsY;
        int x0 = (int)Math.Floor(x), y0 = (int)Math.Floor(y);
        double fx = Smooth(x - x0), fy = Smooth(y - y0);
        Func<int, int, double> h = (i, j) => {
            i = ((i % cellsX) + cellsX) % cellsX; j = ((j % cellsY) + cellsY) % cellsY;
            uint n = (uint)(i * 374761393 + j * 668265263 + seed * 2147483647);
            n = (n ^ (n >> 13)) * 1274126177u;
            return ((n ^ (n >> 16)) & 0xffff) / 65535.0;
        };
        double a = h(x0, y0) + (h(x0 + 1, y0) - h(x0, y0)) * fx;
        double b = h(x0, y0 + 1) + (h(x0 + 1, y0 + 1) - h(x0, y0 + 1)) * fx;
        return a + (b - a) * fy;
    }

    public static void Glow(string path) {
        Save(path, 256, (u, v) => {
            double r = Math.Sqrt((u - 0.5) * (u - 0.5) + (v - 0.5) * (v - 0.5)) * 2.0;
            return r >= 1.0 ? 0.0 : Math.Pow(1.0 - r, 2.2);
        });
    }

    // A billowing puff of fire, its edge and inside broken up by noise.
    public static void Puff(string path) {
        Save(path, 256, (u, v) => {
            double dx = u - 0.5, dy = v - 0.5;
            double r = Math.Sqrt(dx * dx + dy * dy) * 2.0;
            double n = 0.5 * Noise(u, v, 4, 4, 21) + 0.3 * Noise(u, v, 8, 8, 22) + 0.2 * Noise(u, v, 16, 16, 23);
            double edge = 1.0 - Smooth(Math.Max(0.0, Math.Min(1.0, (r - 0.25 - 0.45 * n) / 0.35)));
            return edge * (0.45 + 0.75 * n);
        });
    }
}
'@
[FlameJetTextures]::Glow((Join-Path $out 'Texture\JetGlow.png'))
[FlameJetTextures]::Puff((Join-Path $out 'Texture\JetPuff.png'))

function Range($tag, $center, $min, $max) { "<$tag><Center>$center</Center><Max>$max</Max><Min>$min</Min></$tag>" }
function Mid($pair) { ($pair[0] + $pair[1]) / 2.0 }
# (Not 'R': that is an alias of Invoke-History, and aliases win over functions.)
function Spread($tag, $pair) { Range $tag (Mid $pair) $pair[0] $pair[1] }
function EasedColor($from, $to) {
  $parts = foreach ($p in @(@('Start', $from), @('End', $to))) {
    $c = $p[1]
    "<$($p[0])>$(Range R $c[0] $c[0] $c[0])$(Range G $c[1] $c[1] $c[1])$(Range B $c[2] $c[2] $c[2])$(Range A $c[3] $c[3] $c[3])</$($p[0])>"
  }
  "<ColorAll>2</ColorAll><ColorAll_Easing>$($parts -join '')</ColorAll_Easing>"
}

# A stream of sprites born at the vent (or wherever $y says) and sent up.
#   every: frames between births; life: frames; spread: +- across X and Z; y: birth height; rise: units a frame up;
#   drift: +- units a frame sideways; size: start and end ranges; blend: 2 add (fire), 1 alpha (smoke).
function Stream($name, $texture, $every, $life, $spread, $y, $rise, $drift, $sizeFrom, $sizeTo, $from, $to, $fadeIn, $fadeOut, $blend) {
  $node = "<Node><CommonValues><MaxGeneration><Infinite>True</Infinite></MaxGeneration>$(Spread Life $life)$(Range GenerationTime $every $every $every)</CommonValues>" +
    "<LocationValues><Type>1</Type><PVA><Location><X>$(Spread '' @(-$spread, $spread))</X><Y>$(Spread '' $y)</Y><Z>$(Spread '' @(-$spread, $spread))</Z></Location>" +
    "<Velocity><X>$(Spread '' @(-$drift, $drift))</X><Y>$(Spread '' $rise)</Y><Z>$(Spread '' @(-$drift, $drift))</Z></Velocity></PVA></LocationValues>" +
    "<RotationValues><Type>1</Type><PVA><Rotation><Z><Max>180</Max><Min>-180</Min></Z></Rotation><Velocity><Z><Max>3</Max><Min>-3</Min></Z></Velocity></PVA></RotationValues>" +
    "<ScalingValues><Type>4</Type><SingleEasing>$(Spread Start $sizeFrom)$(Spread End $sizeTo)<StartSpeed>20</StartSpeed><EndSpeed>-20</EndSpeed></SingleEasing></ScalingValues>" +
    "<RendererCommonValues><ColorTexture>Texture/$texture</ColorTexture><AlphaBlend>$blend</AlphaBlend><ZWrite>False</ZWrite><FadeInType>1</FadeInType><FadeIn><Frame>$fadeIn</Frame></FadeIn><FadeOutType>1</FadeOutType><FadeOut><Frame>$fadeOut</Frame></FadeOut></RendererCommonValues>" +
    "<DrawingValues><Sprite>$(EasedColor $from $to)</Sprite></DrawingValues><Name>$name</Name><Children /></Node>"
  return $node -replace '<>|</>', ''
}

# Lives as long as the effect plays: the vent's glow.
$glow = "<Node><CommonValues>$(Range Life 60 60 60)<RemoveWhenLifeIsExtinct>False</RemoveWhenLifeIsExtinct></CommonValues>" +
  "<LocationValues><Type>0</Type><Fixed><Location><Y>1</Y></Location></Fixed></LocationValues>" +
  "<ScalingValues><Fixed><Scale><X>11</X><Y>11</Y><Z>11</Z></Scale></Fixed></ScalingValues>" +
  "<RendererCommonValues><ColorTexture>Texture/JetGlow.png</ColorTexture><AlphaBlend>2</AlphaBlend><ZWrite>False</ZWrite><FadeInType>1</FadeInType><FadeIn><Frame>6</Frame></FadeIn></RendererCommonValues>" +
  "<DrawingValues><Sprite><ColorAll_Fixed><R>255</R><G>110</G><B>30</B><A>170</A></ColorAll_Fixed></Sprite></DrawingValues><Name>BaseGlow</Name><Children /></Node>"

$haze = Stream 'Haze' 'JetPuff.png' 1 @(30, 40) 1.8 @(0, 1) @(0.5, 0.65) 0.03 @(4, 5) @(8, 10) @(255, 90, 30, 110) @(120, 15, 5, 0) 4 18 2
$smoke = Stream 'Smoke' 'JetPuff.png' 2 @(40, 50) 2.0 @(13, 17) @(0.15, 0.25) 0.04 @(4, 5) @(8, 10) @(60, 30, 20, 140) @(20, 10, 10, 0) 10 25 1
$flame = Stream 'Flame' 'JetPuff.png' 0.5 @(26, 34) 1.2 @(0, 0.5) @(0.6, 0.8) 0.02 @(2.5, 3.5) @(5, 7) @(255, 170, 60, 220) @(200, 40, 10, 0) 3 14 2
$core = Stream 'Core' 'JetPuff.png' 0.5 @(22, 28) 0.6 @(0, 0.5) @(0.75, 0.95) 0.01 @(1.5, 2.0) @(3, 4) @(255, 240, 180, 255) @(255, 120, 30, 0) 3 10 2
$embers = Stream 'Embers' 'JetGlow.png' 1 @(30, 45) 1.0 @(0, 2) @(0.6, 1.1) 0.08 @(0.3, 0.45) @(0.1, 0.15) @(255, 200, 120, 255) @(255, 80, 20, 0) 2 15 2

$project = @"
<?xml version="1.0" encoding="utf-8"?>
<EffekseerProject>
  <Root>
    <Name>Root</Name>
    <Children>$glow$haze$smoke$flame$core$embers</Children>
  </Root>
  <ToolVersion>1.30</ToolVersion>
  <Version>3</Version>
  <StartFrame>0</StartFrame>
  <EndFrame>240</EndFrame>
  <IsLoop>True</IsLoop>
</EffekseerProject>
"@
$xml = [xml]$project   # well-formed check
$projectPath = Join-Path $out 'FlameJet.efkproj'
$xml.Save($projectPath)
$efk = Join-Path $out 'FlameJet.efk'
Remove-Item $efk -ErrorAction SilentlyContinue
$p = Start-Process $Effekseer -ArgumentList '-cui', '-in', "`"$projectPath`"", '-e', "`"$efk`"" -PassThru -Wait -WindowStyle Hidden
if ($p.ExitCode -ne 0 -or -not (Test-Path $efk)) { throw "Effekseer export failed ($($p.ExitCode))" }
Get-ChildItem $out -Recurse -File | Select-Object @{ n = 'File'; e = { $_.FullName.Substring($out.Length + 1) } }, Length
