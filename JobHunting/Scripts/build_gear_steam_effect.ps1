# Builds the gear exit's effects (BP_GearExit): draws their textures, writes the .efkproj files and exports the .efk
# files with Effekseer's command line, into SourceArt/Effects/GearSteam. Import with Scripts/setup_gear_effects.py.
# Units: the UE import scales Effekseer units by 20 (1 unit = 20 cm); Effekseer's Y is UE's up. Frames are 1/60 s.
# Both sit at the middle of the gear's thickness, on Lift; the gear's rim is 11 units (220 cm) out.
#   GearSteamBurst  one shot, stepping on: a ring of steam bursts out from under the rim all round and rolls
#                   outward, with a low quick puff of hot white at the rim.
#   GearRise        loops while the gear rises: eight steam jets, one every 45 degrees, blow out sideways from the
#                   rim; sparks spray from random points of the rim, fly out, fall and fade. Steam and sparks are
#                   left where they were born (LocationEffectType 1, "when creating"), so they trail behind the gear.
# Run:
#   powershell -File build_gear_steam_effect.ps1 [-Effekseer <path to Effekseer.exe>]
param([string]$Effekseer = (Join-Path $env:USERPROFILE 'Desktop\Effekseer160Win\Effekseer160Win\Tool\Effekseer.exe'))
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$out = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\SourceArt\Effects\GearSteam'))
New-Item -ItemType Directory -Force (Join-Path $out 'Texture') | Out-Null

Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @'
using System;
using System.Drawing;
using System.Drawing.Imaging;

public static class SteamTextures {
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

    static double Noise(double u, double v, int cells, int seed) {
        double x = u * cells, y = v * cells;
        int x0 = (int)Math.Floor(x), y0 = (int)Math.Floor(y);
        double fx = Smooth(x - x0), fy = Smooth(y - y0);
        Func<int, int, double> h = (i, j) => {
            i = ((i % cells) + cells) % cells; j = ((j % cells) + cells) % cells;
            uint n = (uint)(i * 374761393 + j * 668265263 + seed * 2147483647);
            n = (n ^ (n >> 13)) * 1274126177u;
            return ((n ^ (n >> 16)) & 0xffff) / 65535.0;
        };
        double a = h(x0, y0) + (h(x0 + 1, y0) - h(x0, y0)) * fx;
        double b = h(x0, y0 + 1) + (h(x0 + 1, y0 + 1) - h(x0, y0 + 1)) * fx;
        return a + (b - a) * fy;
    }

    // A soft, lumpy cloud of steam: a round blob broken up by noise at the edge and inside.
    public static void Steam(string path) {
        Save(path, 256, (u, v) => {
            double dx = u - 0.5, dy = v - 0.5;
            double r = Math.Sqrt(dx * dx + dy * dy) * 2.0;
            double n = 0.5 * Noise(u, v, 4, 21) + 0.3 * Noise(u, v, 8, 22) + 0.2 * Noise(u, v, 16, 23);
            double edge = 1.0 - Smooth(Math.Max(0.0, Math.Min(1.0, (r - 0.2 - 0.5 * n) / 0.4)));
            return edge * (0.35 + 0.65 * n);
        });
    }

    // A hot point of light: a bright core and a soft falloff.
    public static void Spark(string path) {
        Save(path, 64, (u, v) => {
            double r = Math.Sqrt((u - 0.5) * (u - 0.5) + (v - 0.5) * (v - 0.5)) * 2.0;
            if (r >= 1.0) return 0.0;
            return Math.Max(Math.Exp(-r * r * 18.0), Math.Pow(1.0 - r, 3.0) * 0.6);
        });
    }
}
'@
[SteamTextures]::Steam((Join-Path $out 'Texture\SteamPuff.png'))
[SteamTextures]::Spark((Join-Path $out 'Texture\Spark.png'))

function Range($tag, $center, $min, $max) { "<$tag><Center>$center</Center><Max>$max</Max><Min>$min</Min></$tag>" }
function Axis($x, $y, $z) {
  # Each of $x, $y, $z: @(center, min, max), or $null for nothing on that axis.
  $s = ''
  foreach ($pair in @(@('X', $x), @('Y', $y), @('Z', $z))) { if ($pair[1]) { $s += Range $pair[0] $pair[1][0] $pair[1][1] $pair[1][2] } }
  return $s
}
function EasedColor($from, $to) {
  $parts = foreach ($pair in @(@('Start', $from), @('End', $to))) {
    $c = $pair[1]
    "<$($pair[0])>$(Range R $c[0] $c[0] $c[0])$(Range G $c[1] $c[1] $c[1])$(Range B $c[2] $c[2] $c[2])$(Range A $c[3] $c[3] $c[3])</$($pair[0])>"
  }
  "<ColorAll>2</ColorAll><ColorAll_Easing>$($parts -join '')</ColorAll_Easing>"
}
function Look($texture, $blend, $fadeIn, $fadeOut) {
  "<RendererCommonValues><ColorTexture>Texture/$texture</ColorTexture><AlphaBlend>$blend</AlphaBlend><ZWrite>False</ZWrite>" +
  "<FadeInType>1</FadeInType><FadeIn><Frame>$fadeIn</Frame></FadeIn><FadeOutType>1</FadeOutType><FadeOut><Frame>$fadeOut</Frame></FadeOut></RendererCommonValues>"
}
# One particle, left where it was born: placed and moving along its parent's X (outward), Y up.
#   $p: Life, Location (x, y, z), Velocity (x, y, z), Acceleration (x, y, z), SizeFrom, SizeTo, Texture, Blend,
#       FadeIn, FadeOut, From, To (RGBA), Name, Generation (frames between, or $null for one), Count (or $null)
function Particle($p) {
  $gen = ''
  if ($p.Count) { $gen += "<MaxGeneration><Value>$($p.Count)</Value></MaxGeneration>" }
  elseif ($p.Every) { $gen += '<MaxGeneration><Infinite>True</Infinite></MaxGeneration>' }
  if ($p.Every) { $gen += Range GenerationTime $p.Every $p.Every $p.Every }
  $accel = if ($p.Acceleration) { "<Acceleration>$(Axis $p.Acceleration[0] $p.Acceleration[1] $p.Acceleration[2])</Acceleration>" } else { '' }
  $node = "<Node><CommonValues>$gen<LocationEffectType>1</LocationEffectType><RotationEffectType>1</RotationEffectType><ScaleEffectType>1</ScaleEffectType>$(Range Life $p.Life[0] $p.Life[1] $p.Life[2])</CommonValues>" +
    "<LocationValues><Type>1</Type><PVA><Location>$(Axis $p.Location[0] $p.Location[1] $p.Location[2])</Location><Velocity>$(Axis $p.Velocity[0] $p.Velocity[1] $p.Velocity[2])</Velocity>$accel</PVA></LocationValues>" +
    "<RotationValues><Type>1</Type><PVA><Rotation><Z><Max>180</Max><Min>-180</Min></Z></Rotation><Velocity><Z><Max>2</Max><Min>-2</Min></Z></Velocity></PVA></RotationValues>" +
    "<ScalingValues><Type>4</Type><SingleEasing>$(Range Start $p.SizeFrom[0] $p.SizeFrom[1] $p.SizeFrom[2])$(Range End $p.SizeTo[0] $p.SizeTo[1] $p.SizeTo[2])<StartSpeed>20</StartSpeed><EndSpeed>-20</EndSpeed></SingleEasing></ScalingValues>" +
    (Look $p.Texture $p.Blend $p.FadeIn $p.FadeOut) +
    "<DrawingValues><Sprite>$(EasedColor $p.From $p.To)</Sprite></DrawingValues><Name>$($p.Name)</Name><Children /></Node>"
  return $node
}
# A spawner: a node that draws nothing, turned about the up axis, carrying its particles. Random: a fresh random turn
# for each spawner, one every $every frames ($count of them, or forever); fixed: one at $yaw for the whole effect.
function RandomSpawner($name, $every, $count, $life, $children) {
  $gen = if ($count) { "<MaxGeneration><Value>$count</Value></MaxGeneration>" } else { '<MaxGeneration><Infinite>True</Infinite></MaxGeneration>' }
  "<Node><CommonValues>$gen$(Range Life $life $life $life)$(Range GenerationTime $every $every $every)</CommonValues>" +
  "<RotationValues><Type>1</Type><PVA><Rotation><Y><Max>180</Max><Min>-180</Min></Y></Rotation></PVA></RotationValues>" +
  "<DrawingValues><Type>0</Type></DrawingValues><Name>$name</Name><Children>$children</Children></Node>"
}
function FixedSpawner($name, $yaw, $children) {
  "<Node><CommonValues>$(Range Life 60 60 60)<RemoveWhenLifeIsExtinct>False</RemoveWhenLifeIsExtinct></CommonValues>" +
  "<RotationValues><Type>0</Type><Fixed><Rotation><Y>$yaw</Y></Rotation></Fixed></RotationValues>" +
  "<DrawingValues><Type>0</Type></DrawingValues><Name>$name</Name><Children>$children</Children></Node>"
}
function Project($children, $endFrame, $loop) {
  @"
<?xml version="1.0" encoding="utf-8"?>
<EffekseerProject>
  <Root>
    <Name>Root</Name>
    <Children>$children</Children>
  </Root>
  <ToolVersion>1.30</ToolVersion>
  <Version>3</Version>
  <StartFrame>0</StartFrame>
  <EndFrame>$endFrame</EndFrame>
  <IsLoop>$loop</IsLoop>
</EffekseerProject>
"@
}

# ----- GearSteamBurst: stepping on -----
# 36 spawners in 9 frames, each blowing one big puff out from under the rim; it slows as it rolls out and swells.
$burstPuff = Particle @{
  Name = 'Steam'; Life = @(75, 60, 90); Texture = 'SteamPuff.png'; Blend = 1; FadeIn = 3; FadeOut = 45
  Location = @(@(10, 9, 11), @(-0.5, -0.8, 0), @(0, -0.6, 0.6)); Velocity = @(@(0.3, 0.2, 0.42), @(0.03, 0.01, 0.06), $null)
  Acceleration = @(@(-0.004, -0.005, -0.003), @(0.002, 0.001, 0.003), $null)
  SizeFrom = @(3, 2.5, 3.5); SizeTo = @(10, 8, 12); From = @(245, 245, 240, 210); To = @(200, 200, 200, 0)
}
$burstHot = Particle @{
  Name = 'HotPuff'; Life = @(25, 20, 30); Texture = 'SteamPuff.png'; Blend = 2; FadeIn = 1; FadeOut = 18
  Location = @(@(10.5, 10, 11), @(0, -0.3, 0.3), $null); Velocity = @(@(0.35, 0.25, 0.45), $null, $null)
  SizeFrom = @(2, 1.5, 2.5); SizeTo = @(5, 4, 6); From = @(255, 240, 210, 150); To = @(255, 200, 140, 0)
}
$burst = RandomSpawner 'BurstSpawner' 0.25 36 95 ($burstPuff + $burstHot)
$burstProject = Project $burst 120 'False'

# ----- GearRise: rising -----
# Eight jets, one every 45 degrees: a puff every 2 frames each, fast at first, slowing, swelling.
$jets = foreach ($i in 0..7) {
  $jet = Particle @{
    Name = "Jet$i"; Every = 2; Life = @(40, 32, 48); Texture = 'SteamPuff.png'; Blend = 1; FadeIn = 2; FadeOut = 25
    Location = @(@(11, 10.5, 11.5), @(0, -0.3, 0.3), @(0, -0.4, 0.4)); Velocity = @(@(0.45, 0.35, 0.55), @(0, -0.04, 0.04), @(0, -0.05, 0.05))
    Acceleration = @(@(-0.008, -0.009, -0.007), @(0.003, 0.002, 0.004), $null)
    SizeFrom = @(1.2, 1, 1.5); SizeTo = @(6, 5, 7.5); From = @(250, 250, 245, 200); To = @(210, 210, 210, 0)
  }
  FixedSpawner "JetSpawner$i" ($i * 45 + 22.5) $jet
}
# Sparks: a fresh spawner every half frame at a random point of the rim; the spark flies out and up, then falls.
# Since the user's note (2026-11-17): the sparks come from where the axle rubs out of the floor, not the gear, so
# RiseFx sits on the actor's root at floor level and the sparks start on the axle's surface (radius 45 cm = 2.25).
$spark = Particle @{
  Name = 'Spark'; Life = @(40, 28, 52); Texture = 'Spark.png'; Blend = 2; FadeIn = 0; FadeOut = 15
  Location = @(@(2.3, 2.2, 2.4), @(0.2, 0.05, 0.4), $null); Velocity = @(@(0.3, 0.12, 0.5), @(0.3, 0.12, 0.5), @(0, -0.1, 0.1))
  Acceleration = @(@(0, 0, 0), @(-0.022, -0.026, -0.018), $null)
  SizeFrom = @(1.0, 0.7, 1.3); SizeTo = @(0.3, 0.2, 0.4); From = @(255, 245, 190, 255); To = @(255, 120, 30, 0)
}
$sparks = RandomSpawner 'SparkSpawner' 0.5 $null 55 $spark
# A wisp of thin, hot steam hugging the rim, so the edge itself seems to smoke.
$wisp = Particle @{
  Name = 'RimWisp'; Life = @(30, 24, 36); Texture = 'SteamPuff.png'; Blend = 1; FadeIn = 4; FadeOut = 20
  Location = @(@(10.5, 9.5, 11.5), @(0, -0.3, 0.3), $null); Velocity = @(@(0.08, 0.04, 0.12), @(0.04, 0.02, 0.06), $null)
  SizeFrom = @(1.5, 1.2, 2); SizeTo = @(3.5, 3, 4.5); From = @(240, 240, 235, 120); To = @(220, 220, 220, 0)
}
$wisps = RandomSpawner 'WispSpawner' 1 $null 40 $wisp
# The user dropped the rising steam (jets and wisps): sparks only, bigger (2026-11-17).
$riseProject = Project $sparks 240 'True'

foreach ($variant in @(@('GearSteamBurst', $burstProject), @('GearRise', $riseProject))) {
  $xml = [xml]$variant[1]   # well-formed check
  $projectPath = Join-Path $out ($variant[0] + '.efkproj')
  $xml.Save($projectPath)
  $efk = Join-Path $out ($variant[0] + '.efk')
  Remove-Item $efk -ErrorAction SilentlyContinue
  $p = Start-Process $Effekseer -ArgumentList '-cui', '-in', "`"$projectPath`"", '-e', "`"$efk`"" -PassThru -Wait -WindowStyle Hidden
  if ($p.ExitCode -ne 0 -or -not (Test-Path $efk)) { throw "Effekseer export failed for $($variant[0]) ($($p.ExitCode))" }
}
Get-ChildItem $out -Recurse -File | Select-Object @{ n = 'File'; e = { $_.FullName.Substring($out.Length + 1) } }, Length
