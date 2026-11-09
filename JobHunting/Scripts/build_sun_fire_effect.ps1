# Builds the burning-sun effect for BP_Sun: draws its textures, writes SunFire.efkproj and exports SunFire.efk with
# Effekseer's command line, into SourceArt/Effects/SunFire. Import into UE with Scripts/import_sun_fire.py.
# Sizes: the UE import scales Effekseer units by 20, so the sun (radius 50 cm) is 2.5 units here. Layers, back to front:
#   Glow     a soft orange halo behind the sun
#   Rays     two slowly turning bursts of thin light rays
#   Corona   two rings of flame streaks around the rim, scrolling outward at different speeds (the burning edge)
#   Flames   three layers of billowing puffs welling up from the rim, swelling and cooling from yellow to red
#   Embers   sparks that leave the rim and fade out
# Flames and embers are born in the face's plane; BP_Sun turns its face to the camera (BP_Sun_EventGraph.txt), so they
# always ring the sun without covering its face. Everything loops for as long as the effect plays. Run:
#   powershell -File build_sun_fire_effect.ps1 [-Effekseer <path to Effekseer.exe>]
param([string]$Effekseer = (Join-Path $env:USERPROFILE 'Desktop\Effekseer160Win\Effekseer160Win\Tool\Effekseer.exe'))
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$out = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\SourceArt\Effects\SunFire'))
New-Item -ItemType Directory -Force (Join-Path $out 'Texture') | Out-Null

Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @'
using System;
using System.Drawing;
using System.Drawing.Imaging;

public static class SunTextures {
    // White pixels whose alpha comes from f(x, y) with x, y in 0..1.
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

    // Value noise that repeats every `cellsX` by `cellsY` cells, so the texture tiles.
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

    // Tongues of flame: fine across (u, around the ring), long along v (outward), tiling both ways.
    public static void Flame(string path) {
        Save(path, 256, (u, v) => {
            double n = 0.55 * Noise(u, v, 16, 2, 1) + 0.3 * Noise(u, v, 32, 4, 2) + 0.15 * Noise(u, v, 64, 8, 3);
            return Math.Pow(Math.Max(0.0, (n - 0.3) / 0.55), 1.4);
        });
    }

    // A billowing puff of fire: a soft blob whose edge and inside are broken up by noise, so overlapping puffs read
    // as rolling flames rather than discs.
    public static void Puff(string path) {
        Save(path, 256, (u, v) => {
            double dx = u - 0.5, dy = v - 0.5;
            double r = Math.Sqrt(dx * dx + dy * dy) * 2.0;
            double n = 0.5 * Noise(u, v, 4, 4, 11) + 0.3 * Noise(u, v, 8, 8, 12) + 0.2 * Noise(u, v, 16, 16, 13);
            double edge = 1.0 - Smooth(Math.Max(0.0, Math.Min(1.0, (r - 0.25 - 0.45 * n) / 0.35)));
            return edge * (0.45 + 0.75 * n);
        });
    }

    // A burst of thin rays of varying length and width from the middle.
    public static void Rays(string path) {
        var rnd = new Random(7);
        int count = 28;
        var angle = new double[count]; var length = new double[count]; var width = new double[count];
        for (int i = 0; i < count; i++) {
            angle[i] = (i + rnd.NextDouble() * 0.6) / count * 2.0 * Math.PI;
            length[i] = 0.55 + rnd.NextDouble() * 0.45;
            width[i] = 0.006 + rnd.NextDouble() * 0.01;
        }
        Save(path, 512, (u, v) => {
            double dx = u - 0.5, dy = v - 0.5;
            double r = Math.Sqrt(dx * dx + dy * dy) * 2.0;
            if (r >= 1.0) return 0.0;
            double a = Math.Atan2(dy, dx), sum = 0.0;
            for (int i = 0; i < count; i++) {
                double d = Math.Abs(Math.IEEERemainder(a - angle[i], 2.0 * Math.PI)) * r;
                double along = Math.Max(0.0, 1.0 - r / length[i]);
                sum += Math.Exp(-d * d / (width[i] * width[i])) * along * along;
            }
            return sum;
        });
    }
}
'@
[SunTextures]::Glow((Join-Path $out 'Texture\SunGlow.png'))
[SunTextures]::Flame((Join-Path $out 'Texture\SunFlame.png'))
[SunTextures]::Rays((Join-Path $out 'Texture\SunRays.png'))
[SunTextures]::Puff((Join-Path $out 'Texture\SunPuff.png'))

function Color($tag, $r, $g, $b, $a) { "<$tag><R>$r</R><G>$g</G><B>$b</B><A>$a</A></$tag>" }
function Range($tag, $center, $min, $max) { "<$tag><Center>$center</Center><Max>$max</Max><Min>$min</Min></$tag>" }
# A node that lives for as long as the effect plays.
function Lasting() { "<CommonValues>$(Range Life 60 60 60)<RemoveWhenLifeIsExtinct>False</RemoveWhenLifeIsExtinct></CommonValues>" }
function Spin($start, $speed) { "<RotationValues><Type>1</Type><PVA><Rotation><Z>$(Range '' $start $start $start)</Z></Rotation><Velocity><Z>$(Range '' $speed $speed $speed)</Z></Velocity></PVA></RotationValues>" -replace '<>|</>', '' }
function Scale($s) { "<ScalingValues><Fixed><Scale><X>$s</X><Y>$s</Y><Z>$s</Z></Scale></Fixed></ScalingValues>" }
function Look($texture, $extra) { "<RendererCommonValues><ColorTexture>Texture/$texture</ColorTexture><AlphaBlend>2</AlphaBlend><ZWrite>False</ZWrite>$extra</RendererCommonValues>" }

function Sprite($name, $texture, $size, $color, $spin) {
  "<Node>$(Lasting)$spin$(Scale $size)$(Look $texture '')<DrawingValues><Sprite>$color</Sprite></DrawingValues><Name>$name</Name><Children /></Node>"
}
function Corona($name, $inner, $outer, $ratio, $speedX, $speedY, $innerColor, $centerColor, $outerColor) {
  $scroll = "<UV>3</UV><UVScroll><Size><X>256</X><Y>256</Y></Size><Speed><X>$speedX</X><Y>$speedY</Y></Speed></UVScroll>"
  "<Node>$(Lasting)$(Look 'SunFlame.png' $scroll)<DrawingValues><Type>4</Type><Ring><VertexCount>72</VertexCount>" +
  "<Outer_Fixed><Location><X>$outer</X></Location></Outer_Fixed><Inner_Fixed><Location><X>$inner</X></Location></Inner_Fixed>" +
  "<CenterRatio_Fixed>$ratio</CenterRatio_Fixed>$outerColor$centerColor$innerColor</Ring></DrawingValues><Name>$name</Name><Children /></Node>"
}

$glow = Sprite 'Glow' 'SunGlow.png' 12 "<ColorAll_Fixed><R>255</R><G>130</G><B>40</B><A>190</A></ColorAll_Fixed>" ''
$rays = Sprite 'Rays' 'SunRays.png' 17 "<ColorAll_Fixed><R>255</R><G>190</G><B>110</B><A>150</A></ColorAll_Fixed>" (Spin 0 0.08)
$rays2 = Sprite 'RaysBack' 'SunRays.png' 13 "<ColorAll_Fixed><R>255</R><G>140</G><B>60</B><A>120</A></ColorAll_Fixed>" (Spin 7 -0.12)
$coronaA = Corona 'Corona' 2.3 4.2 0.25 0.25 1.0 (Color InnerColor_Fixed 255 230 150 255) (Color CenterColor_Fixed 255 140 40 230) (Color OuterColor_Fixed 255 60 0 0)
$coronaB = Corona 'CoronaInner' 2.3 3.3 0.3 -0.4 1.7 (Color InnerColor_Fixed 255 245 200 255) (Color CenterColor_Fixed 255 170 70 200) (Color OuterColor_Fixed 255 90 10 0)

# Sparks: each spawner faces a random direction and drops one spark on the surface that drifts outward along it.
$ember = "<Node><CommonValues>$(Range Life 45 35 55)</CommonValues>" +
  "<LocationValues><Type>1</Type><PVA><Location><X>$(Range '' 0 -0.4 0.4)</X><Y>$(Range '' 2.6 2.4 2.8)</Y></Location><Velocity><Y>$(Range '' 0.04 0.025 0.06)</Y></Velocity></PVA></LocationValues>" +
  "<ScalingValues><Type>3</Type><SinglePVA>$(Range Scale 0.7 0.45 0.95)$(Range Velocity -0.007 -0.007 -0.007)</SinglePVA></ScalingValues>" +
  "<RendererCommonValues><ColorTexture>Texture/SunGlow.png</ColorTexture><AlphaBlend>2</AlphaBlend><ZWrite>False</ZWrite><FadeInType>1</FadeInType><FadeIn><Frame>5</Frame></FadeIn><FadeOutType>1</FadeOutType><FadeOut><Frame>20</Frame></FadeOut></RendererCommonValues>" +
  "<DrawingValues><Sprite><ColorAll_Fixed><R>255</R><G>175</G><B>70</B><A>255</A></ColorAll_Fixed></Sprite></DrawingValues><Name>Ember</Name><Children /></Node>"
$ember = $ember -replace '<>|</>', ''
$embers = "<Node><CommonValues><MaxGeneration><Infinite>True</Infinite></MaxGeneration>$(Range Life 60 60 60)$(Range GenerationTime 3 3 3)</CommonValues>" +
  "<RotationValues><Type>1</Type><PVA><Rotation><X><Max>180</Max><Min>-180</Min></X></Rotation></PVA></RotationValues>" +
  "<DrawingValues><Type>0</Type></DrawingValues><Name>EmberSpawner</Name><Children>$ember</Children></Node>"

# Billowing flames, the main look. The face points along +X (UE's forward is Effekseer's X, UE's up is its Y), and
# BP_Sun keeps it turned to the camera, so the puffs are born in the face's plane (YZ) just inside the rim: spawners
# turn about X to a random angle, and each drops a puff that drifts outward, swells, turns and cools from yellow to red.
function EasedColor($from, $to) {
  $parts = foreach ($pair in @(@('Start', $from), @('End', $to))) {
    $c = $pair[1]
    "<$($pair[0])>$(Range R $c[0] $c[0] $c[0])$(Range G $c[1] $c[1] $c[1])$(Range B $c[2] $c[2] $c[2])$(Range A $c[3] $c[3] $c[3])</$($pair[0])>"
  }
  "<ColorAll>2</ColorAll><ColorAll_Easing>$($parts -join '')</ColorAll_Easing>"
}
function Flames($name, $every, $radius, $outward, $life, $sizeFrom, $sizeTo, $from, $to, $fadeOut) {
  $puff = "<Node><CommonValues>$(Range Life $life[0] $life[1] $life[2])</CommonValues>" +
    "<LocationValues><Type>1</Type><PVA><Location><X>$(Range '' 0 -0.3 0.3)</X><Y>$(Range '' $radius[0] $radius[1] $radius[2])</Y></Location>" +
    "<Velocity><Y>$(Range '' $outward[0] $outward[1] $outward[2])</Y></Velocity></PVA></LocationValues>" +
    "<RotationValues><Type>1</Type><PVA><Rotation><Z><Max>180</Max><Min>-180</Min></Z></Rotation><Velocity><Z><Max>1.5</Max><Min>-1.5</Min></Z></Velocity></PVA></RotationValues>" +
    "<ScalingValues><Type>4</Type><SingleEasing>$(Range Start $sizeFrom[0] $sizeFrom[1] $sizeFrom[2])$(Range End $sizeTo[0] $sizeTo[1] $sizeTo[2])<StartSpeed>20</StartSpeed><EndSpeed>-20</EndSpeed></SingleEasing></ScalingValues>" +
    "<RendererCommonValues><ColorTexture>Texture/SunPuff.png</ColorTexture><AlphaBlend>2</AlphaBlend><ZWrite>False</ZWrite><FadeInType>1</FadeInType><FadeIn><Frame>8</Frame></FadeIn><FadeOutType>1</FadeOutType><FadeOut><Frame>$fadeOut</Frame></FadeOut></RendererCommonValues>" +
    "<DrawingValues><Sprite>$(EasedColor $from $to)</Sprite></DrawingValues><Name>$name</Name><Children /></Node>"
  $puff = $puff -replace '<>|</>', ''
  "<Node><CommonValues><MaxGeneration><Infinite>True</Infinite></MaxGeneration>$(Range Life ($life[2] + 5) ($life[2] + 5) ($life[2] + 5))$(Range GenerationTime $every $every $every)</CommonValues>" +
  "<RotationValues><Type>1</Type><PVA><Rotation><X><Max>180</Max><Min>-180</Min></X></Rotation></PVA></RotationValues>" +
  "<DrawingValues><Type>0</Type></DrawingValues><Name>${name}Spawner</Name><Children>$puff</Children></Node>"
}
# Wide, slow, deep red haze furthest out; the main orange flames; quick bright tongues hugging the rim.
$haze = Flames 'FlameHaze' 2 @(2.4, 2.1, 2.7) @(0.022, 0.012, 0.032) @(80, 65, 95) @(2.5, 2.0, 3.0) @(6.0, 5.0, 7.5) @(255, 120, 40, 120) @(170, 30, 10, 0) 40
$flames = Flames 'Flame' 1 @(2.3, 2.0, 2.6) @(0.03, 0.018, 0.045) @(55, 40, 70) @(1.6, 1.2, 2.0) @(4.0, 3.2, 5.0) @(255, 200, 90, 230) @(255, 70, 15, 0) 25
$tongues = Flames 'FlameCore' 1 @(2.3, 2.1, 2.5) @(0.02, 0.01, 0.03) @(30, 22, 38) @(1.0, 0.8, 1.3) @(2.2, 1.8, 2.8) @(255, 245, 190, 255) @(255, 150, 40, 0) 15

$project = @"
<?xml version="1.0" encoding="utf-8"?>
<EffekseerProject>
  <Root>
    <Name>Root</Name>
    <Children>$glow$rays2$rays$haze$coronaA$flames$coronaB$tongues$embers</Children>
  </Root>
  <ToolVersion>1.30</ToolVersion>
  <Version>3</Version>
  <StartFrame>0</StartFrame>
  <EndFrame>240</EndFrame>
  <IsLoop>True</IsLoop>
</EffekseerProject>
"@
# SunFireBlue: the same fire with red and blue swapped (orange 255,130,40 -> blue 40,130,255). BP_Sun fades from
# SunFire to it as the sun gets angrier.
$blue = $project -replace '<(/?)R>', '<$1TMP>' -replace '<(/?)B>', '<$1R>' -replace '<(/?)TMP>', '<$1B>'
foreach ($variant in @(@('SunFire', $project), @('SunFireBlue', $blue))) {
  $xml = [xml]$variant[1]   # well-formed check
  $projectPath = Join-Path $out ($variant[0] + '.efkproj')
  $xml.Save($projectPath)
  $efk = Join-Path $out ($variant[0] + '.efk')
  Remove-Item $efk -ErrorAction SilentlyContinue
  $p = Start-Process $Effekseer -ArgumentList '-cui', '-in', "`"$projectPath`"", '-e', "`"$efk`"" -PassThru -Wait -WindowStyle Hidden
  if ($p.ExitCode -ne 0 -or -not (Test-Path $efk)) { throw "Effekseer export failed for $($variant[0]) ($($p.ExitCode))" }
}
Get-ChildItem $out -Recurse -File | Select-Object @{ n = 'File'; e = { $_.FullName.Substring($out.Length + 1) } }, Length
