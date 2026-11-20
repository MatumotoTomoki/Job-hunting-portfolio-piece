# Builds the toggle switch's and the switch blocks' effects (the user, 2026-11-20), each in red and blue:
#   SourceArt/Effects/SwitchFx/SwitchBurst{Red,Blue}.efk  one shot at the button: a ring of glints thrown out flat,
#                                                          a quick flash, a few motes rising - in the colour now on
#   SourceArt/Effects/SwitchFx/BlockForm{Red,Blue}.efk    one shot at a block turning solid: motes drawn in from all
#                                                          round to the middle, then a flash there
#   SourceArt/Effects/SwitchFx/BlockVanish{Red,Blue}.efk  one shot at a block turning to a ghost: motes scattering out
#                                                          and up, and a faint puff
# Units: 1 Effekseer unit = 20 cm, Y up. Textures copied from SunImpact (CloudPuff, Glint). A parent node turned at
# random about Y throws its children along their own X: out from the middle, or (moving -X from out at X) in to it.
#   powershell -File build_switch_effects.ps1 [-Effekseer <path to Effekseer.exe>]
param([string]$Effekseer = (Join-Path $env:USERPROFILE 'Desktop\Effekseer160Win\Effekseer160Win\Tool\Effekseer.exe'))
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\SourceArt\Effects'))
$out = Join-Path $root 'SwitchFx'
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

# Bright core -> the colour (RGBA, 0-255).
$colours = @{
  Red  = @{ Hot = @(255, 215, 200, 255); Tint = @(255, 70, 45, 0); Soft = @(255, 90, 60, 150) }
  Blue = @{ Hot = @(205, 225, 255, 255); Tint = @(60, 125, 255, 0); Soft = @(80, 140, 255, 150) }
}
foreach ($c in 'Red', 'Blue') {
  $hot = $colours[$c].Hot; $tint = $colours[$c].Tint; $soft = $colours[$c].Soft

  # ----- SwitchBurst -----
  $ring = Puff @{ Name = 'Glint'; Life = @(18, 14, 22); Texture = 'Glint.png'; Blend = 2; FadeIn = 1; FadeOut = 10
    Location = @(@(0.6, 0.4, 0.8), $null, $null); Velocity = @(@(0.28, 0.22, 0.34), @(0.03, 0.0, 0.06), $null)
    SizeFrom = @(0.5, 0.4, 0.6); SizeTo = @(0.15, 0.1, 0.2); From = $hot; To = $tint }
  $flash = Puff @{ Name = 'Flash'; Life = @(12, 12, 12); Texture = 'CloudPuff.png'; Blend = 2; FadeIn = 1; FadeOut = 9
    Location = @($null, @(0.3, 0.3, 0.3), $null); Velocity = @($null, $null, $null)
    SizeFrom = @(1.2, 1.2, 1.2); SizeTo = @(3.2, 3.2, 3.2); From = $hot; To = $tint }
  $rise = Puff @{ Name = 'Mote'; Life = @(40, 30, 50); Texture = 'Glint.png'; Blend = 2; FadeIn = 4; FadeOut = 24
    Location = @(@(0.8, 0.0, 1.6), @(0.4, 0.0, 0.8), $null); Velocity = @($null, @(0.07, 0.04, 0.1), $null)
    SizeFrom = @(0.3, 0.2, 0.4); SizeTo = @(0.1, 0.08, 0.14); From = $hot; To = $tint }
  Export "SwitchBurst$c" ((Burst 'Ring' 16 0.1 0 30 $ring) + (Burst 'FlashOnce' 1 1 0 20 $flash) + (Burst 'Rise' 8 1 2 60 $rise)) 70

  # ----- BlockForm: in from 3-4.5 units out over 24 frames, a flash at 20 -----
  $gather = Puff @{ Name = 'Gather'; Life = @(24, 24, 24); Texture = 'Glint.png'; Blend = 2; FadeIn = 6; FadeOut = 5
    Location = @(@(3.8, 3.2, 4.4), @(0.0, -1.2, 1.2), $null); Velocity = @(@(-0.16, -0.14, -0.18), $null, $null)
    SizeFrom = @(0.35, 0.25, 0.45); SizeTo = @(0.55, 0.45, 0.65); From = $tint; To = $hot }
  $formFlash = Puff @{ Name = 'Flash'; Life = @(14, 14, 14); Texture = 'CloudPuff.png'; Blend = 2; FadeIn = 1; FadeOut = 11
    Location = @($null, $null, $null); Velocity = @($null, $null, $null)
    SizeFrom = @(2.0, 2.0, 2.0); SizeTo = @(5.5, 5.5, 5.5); From = $hot; To = $tint }
  Export "BlockForm$c" ((Burst 'In' 22 0.4 0 40 $gather) + (Burst 'FlashOnce' 1 1 20 20 $formFlash)) 50

  # ----- BlockVanish: out and up, fading -----
  $scatter = Puff @{ Name = 'Scatter'; Life = @(30, 24, 36); Texture = 'Glint.png'; Blend = 2; FadeIn = 1; FadeOut = 20
    Location = @(@(1.4, 0.0, 2.8), @(0.0, -0.8, 0.8), $null); Velocity = @(@(0.11, 0.07, 0.15), @(0.05, 0.02, 0.08), $null)
    SizeFrom = @(0.45, 0.35, 0.55); SizeTo = @(0.1, 0.08, 0.12); From = $hot; To = $tint }
  $haze = Puff @{ Name = 'Haze'; Life = @(16, 16, 16); Texture = 'CloudPuff.png'; Blend = 2; FadeIn = 1; FadeOut = 14
    Location = @($null, $null, $null); Velocity = @($null, $null, $null)
    SizeFrom = @(3.5, 3.5, 3.5); SizeTo = @(5.0, 5.0, 5.0); From = $soft; To = $tint }
  Export "BlockVanish$c" ((Burst 'Out' 18 0.2 0 45 $scatter) + (Burst 'HazeOnce' 1 1 0 20 $haze)) 50
}
Get-ChildItem $out -Recurse -File | Select-Object @{ n = 'File'; e = { $_.FullName.Substring($out.Length + 1) } }, Length
