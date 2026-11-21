# Builds the wings' effects (BP_Wings; the user, 2026-11-21), white and gold like the heaven palace:
#   SourceArt/Effects/WingsFx/Texture/Feather.png  a soft white feather (drawn here)
#   SourceArt/Effects/WingsFx/WingsGet.efk         one shot as they are taken: a flash, a ring of glints and white
#                                                  feathers bursting out and drifting down, swaying
#   SourceArt/Effects/WingsFx/WingGlide.efk        loops while they are spread: a feather or a glint now and then,
#                                                  left behind in the air (bound only when born) and drifting down
# Units: 1 Effekseer unit = 20 cm, Y up. CloudPuff and Glint copied from SunImpact.
#   powershell -File build_wings_effects.ps1 [-Effekseer <path to Effekseer.exe>]
param([string]$Effekseer = (Join-Path $env:USERPROFILE 'Desktop\Effekseer160Win\Effekseer160Win\Tool\Effekseer.exe'))
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\SourceArt\Effects'))
$out = Join-Path $root 'WingsFx'
New-Item -ItemType Directory -Force (Join-Path $out 'Texture') | Out-Null
foreach ($name in 'CloudPuff.png', 'Glint.png') { Copy-Item (Join-Path $root "SunImpact\Texture\$name") (Join-Path $out "Texture\$name") -Force }

# ----- the feather texture: 64 x 128, a leaf-shaped vane with a soft edge and a thin shaft -----
Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap 64, 128, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
for ($y = 0; $y -lt 128; $y++) {
  $v = $y / 127.0                                            # 0 at the tip, 1 at the quill
  $half = 26.0 * [Math]::Pow([Math]::Sin([Math]::PI * [Math]::Min(1.0, $v / 0.85)), 0.8) * (1.0 - 0.3 * $v)
  for ($x = 0; $x -lt 64; $x++) {
    $dx = [Math]::Abs($x - 31.5)
    $a = 0.0
    if ($half -gt 0.5) {
      $edge = [Math]::Max(0.0, [Math]::Min(1.0, ($half - $dx) / 4.0))
      $barbs = 0.85 + 0.15 * [Math]::Sin(($y + $dx * 0.8) * 1.1)  # faint barbs slanting out
      $a = $edge * $barbs * (0.55 + 0.45 * (1.0 - $dx / [Math]::Max(1.0, $half)))
    }
    $shade = 255
    if ($dx -lt 1.2 -and $v -lt 0.97) { $a = [Math]::Max($a, 0.9); $shade = 225 }   # the shaft
    if ($v -gt 0.85 -and $dx -lt 1.5) { $a = 0.9; $shade = 225 }                    # the quill
    $bmp.SetPixel($x, $y, [System.Drawing.Color]::FromArgb([int](255 * [Math]::Min(1.0, $a)), $shade, $shade, [Math]::Min(255, $shade + 5)))
  }
}
$bmp.Save((Join-Path $out 'Texture\Feather.png'), [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()

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
# $p.Bind: 1 = moves with the emitter only when born (left behind after), else 2 (always follows).
function Puff($p) {
  $bind = if ($p.Bind) { $p.Bind } else { 1 }
  $accel = if ($p.Acceleration) { "<Acceleration>$(Axis $p.Acceleration[0] $p.Acceleration[1] $p.Acceleration[2])</Acceleration>" } else { '' }
  $spin = if ($p.Spin) { $p.Spin } else { 2 }
  "<Node><CommonValues><LocationEffectType>$bind</LocationEffectType><RotationEffectType>1</RotationEffectType><ScaleEffectType>1</ScaleEffectType>$(Range Life $p.Life[0] $p.Life[1] $p.Life[2])</CommonValues>" +
  "<LocationValues><Type>1</Type><PVA><Location>$(Axis $p.Location[0] $p.Location[1] $p.Location[2])</Location><Velocity>$(Axis $p.Velocity[0] $p.Velocity[1] $p.Velocity[2])</Velocity>$accel</PVA></LocationValues>" +
  "<RotationValues><Type>1</Type><PVA><Rotation><Z><Max>180</Max><Min>-180</Min></Z></Rotation><Velocity><Z><Max>$spin</Max><Min>-$spin</Min></Z></Velocity></PVA></RotationValues>" +
  "<ScalingValues><Type>4</Type><SingleEasing>$(Range Start $p.SizeFrom[0] $p.SizeFrom[1] $p.SizeFrom[2])$(Range End $p.SizeTo[0] $p.SizeTo[1] $p.SizeTo[2])<StartSpeed>20</StartSpeed><EndSpeed>-20</EndSpeed></SingleEasing></ScalingValues>" +
  "<RendererCommonValues><ColorTexture>Texture/$($p.Texture)</ColorTexture><AlphaBlend>$($p.Blend)</AlphaBlend><ZWrite>False</ZWrite><FadeInType>1</FadeInType><FadeIn><Frame>$($p.FadeIn)</Frame></FadeIn><FadeOutType>1</FadeOutType><FadeOut><Frame>$($p.FadeOut)</Frame></FadeOut></RendererCommonValues>" +
  "<DrawingValues><Sprite>$(Colour $p.From $p.To)</Sprite></DrawingValues><Name>$($p.Name)</Name><Children /></Node>"
}
# $count 0 = forever.
function Burst($name, $count, $every, $delay, $life, $children) {
  $generation = if ($count -eq 0) { '<MaxGeneration><Infinite>True</Infinite></MaxGeneration>' } else { "<MaxGeneration><Value>$count</Value></MaxGeneration>" }
  "<Node><CommonValues>$generation$(Range Life $life $life $life)$(Range GenerationTime $every $every $every)$(Range GenerationTimeOffset $delay $delay $delay)</CommonValues>" +
  "<RotationValues><Type>1</Type><PVA><Rotation><Y><Max>180</Max><Min>-180</Min></Y></Rotation></PVA></RotationValues>" +
  "<DrawingValues><Type>0</Type></DrawingValues><Name>$name</Name><Children>$children</Children></Node>"
}
function Export($name, $children, $frames, $loop) {
  $project = "<?xml version=`"1.0`" encoding=`"utf-8`"?><EffekseerProject><Root><Name>Root</Name><Children>$children</Children></Root><ToolVersion>1.30</ToolVersion><Version>3</Version><StartFrame>0</StartFrame><EndFrame>$frames</EndFrame><IsLoop>$loop</IsLoop></EffekseerProject>"
  $projectPath = Join-Path $out "$name.efkproj"
  ([xml]$project).Save($projectPath)
  $efk = Join-Path $out "$name.efk"
  Remove-Item $efk -ErrorAction SilentlyContinue
  $p = Start-Process $Effekseer -ArgumentList '-cui', '-in', "`"$projectPath`"", '-e', "`"$efk`"" -PassThru -Wait -WindowStyle Hidden
  if ($p.ExitCode -ne 0 -or -not (Test-Path $efk)) { throw "Effekseer export failed for $name ($($p.ExitCode))" }
}

$white = @(255, 255, 255, 255)
$whiteOut = @(255, 250, 240, 0)
$hot = @(255, 252, 235, 255)
$gold = @(255, 205, 110, 0)

# ----- WingsGet -----
$flash = Puff @{ Name = 'Flash'; Life = @(18, 18, 18); Texture = 'CloudPuff.png'; Blend = 2; FadeIn = 1; FadeOut = 15
  Location = @($null, $null, $null); Velocity = @($null, $null, $null)
  SizeFrom = @(3.0, 3.0, 3.0); SizeTo = @(9.0, 9.0, 9.0); From = $hot; To = $gold }
$ring = Puff @{ Name = 'Ring'; Life = @(24, 20, 28); Texture = 'Glint.png'; Blend = 2; FadeIn = 1; FadeOut = 14
  Location = @(@(0.5, 0.3, 0.7), $null, $null); Velocity = @(@(0.32, 0.26, 0.38), @(0.02, -0.02, 0.06), $null)
  SizeFrom = @(0.6, 0.5, 0.7); SizeTo = @(0.15, 0.1, 0.2); From = $hot; To = $gold }
$feathers = Puff @{ Name = 'Feather'; Life = @(90, 70, 110); Texture = 'Feather.png'; Blend = 1; FadeIn = 3; FadeOut = 40; Spin = 4
  Location = @(@(0.8, 0.3, 1.3), @(0.5, -0.5, 1.5), $null); Velocity = @(@(0.14, 0.08, 0.2), @(0.12, 0.06, 0.18), $null)
  Acceleration = @(@(-0.002, -0.003, -0.001), @(-0.005, -0.006, -0.004), $null)
  SizeFrom = @(0.9, 0.7, 1.1); SizeTo = @(0.8, 0.6, 1.0); From = $white; To = $whiteOut }
Export 'WingsGet' ((Burst 'FlashOnce' 1 1 0 20 $flash) + (Burst 'RingOut' 20 0.1 0 30 $ring) + (Burst 'Feathers' 12 0.3 1 120 $feathers)) 130 'False'

# ----- WingGlide (loop): left behind across the wings' span -----
$trailFeather = Puff @{ Name = 'Feather'; Life = @(60, 45, 75); Texture = 'Feather.png'; Blend = 1; FadeIn = 4; FadeOut = 30; Spin = 4
  Location = @(@(0.0, -4.0, 4.0), @(0.0, -1.0, 1.0), $null); Velocity = @($null, @(-0.03, -0.045, -0.02), $null)
  SizeFrom = @(0.6, 0.45, 0.75); SizeTo = @(0.55, 0.4, 0.7); From = $white; To = $whiteOut }
$trailGlint = Puff @{ Name = 'Glint'; Life = @(30, 24, 36); Texture = 'Glint.png'; Blend = 2; FadeIn = 2; FadeOut = 20
  Location = @(@(0.0, -4.5, 4.5), @(0.0, -1.0, 1.0), $null); Velocity = @($null, @(-0.01, -0.02, 0.0), $null)
  SizeFrom = @(0.35, 0.25, 0.45); SizeTo = @(0.1, 0.08, 0.12); From = $hot; To = $gold }
# Not turned at random: the span runs along the emitter's own X, across the player's back.
function Trail($name, $every, $life, $child) {
  "<Node><CommonValues><MaxGeneration><Infinite>True</Infinite></MaxGeneration>$(Range Life $life $life $life)$(Range GenerationTime $every $every $every)</CommonValues>" +
  "<DrawingValues><Type>0</Type></DrawingValues><Name>$name</Name><Children>$child</Children></Node>"
}
Export 'WingGlide' ((Trail 'Feathers' 9 80 $trailFeather) + (Trail 'Glints' 4 40 $trailGlint)) 120 'True'
Get-ChildItem $out -Recurse -File | Select-Object @{ n = 'File'; e = { $_.FullName.Substring($out.Length + 1) } }, Length
