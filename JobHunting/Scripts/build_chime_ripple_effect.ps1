# Builds the ringing jewel's chime effect (BP_ChimeJewel, area 4; the user, 2026-11-20):
# SourceArt/Effects/ChimeRipple/ChimeRipple.efk, one shot as a jewel rings, at the jewel's middle (the emitter keeps
# world scale 1, so the 220 cm jewels' squashed actor scale does not squash it):
#   Ripple   a ring of light lying flat, spreading from the jewel's edge (2.2 m) out to ~4.5 m, like a struck bell
#   Ripple2  a fainter second ring a beat behind
#   Notes    glints rising from round the jewel's rim and fading, a little sway
# White, so the emitter's AllColor can tint it with the jewel's colour. Textures copied from SunImpact (ShockRing, Glint).
# Units: 1 Effekseer unit = 20 cm, Y up.
#   powershell -File build_chime_ripple_effect.ps1 [-Effekseer <path to Effekseer.exe>]
param([string]$Effekseer = (Join-Path $env:USERPROFILE 'Desktop\Effekseer160Win\Effekseer160Win\Tool\Effekseer.exe'))
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\SourceArt\Effects'))
$out = Join-Path $root 'ChimeRipple'
New-Item -ItemType Directory -Force (Join-Path $out 'Texture') | Out-Null
foreach ($name in 'ShockRing.png', 'Glint.png') { Copy-Item (Join-Path $root "SunImpact\Texture\$name") (Join-Path $out "Texture\$name") -Force }

function Range($tag, $center, $min, $max) { "<$tag><Center>$center</Center><Max>$max</Max><Min>$min</Min></$tag>" }
function Colour($from, $to) {
  $parts = foreach ($pair in @(@('Start', $from), @('End', $to))) {
    $c = $pair[1]
    "<$($pair[0])>$(Range R $c[0] $c[0] $c[0])$(Range G $c[1] $c[1] $c[1])$(Range B $c[2] $c[2] $c[2])$(Range A $c[3] $c[3] $c[3])</$($pair[0])>"
  }
  "<ColorAll>2</ColorAll><ColorAll_Easing>$($parts -join '')</ColorAll_Easing>"
}
function Flat($name, $delay, $life, $sizeFrom, $sizeTo, $alpha) {
  "<Node><CommonValues><MaxGeneration><Value>1</Value></MaxGeneration>$(Range Life $life $life $life)$(Range GenerationTimeOffset $delay $delay $delay)</CommonValues>" +
  "<LocationValues><Type>0</Type><Fixed><Location><Y>0.6</Y></Location></Fixed></LocationValues>" +
  "<RotationValues><Type>0</Type><Fixed><Rotation><X>90</X></Rotation></Fixed></RotationValues>" +
  "<ScalingValues><Type>4</Type><SingleEasing>$(Range Start $sizeFrom $sizeFrom $sizeFrom)$(Range End $sizeTo $sizeTo $sizeTo)<StartSpeed>30</StartSpeed><EndSpeed>-30</EndSpeed></SingleEasing></ScalingValues>" +
  "<RendererCommonValues><ColorTexture>Texture/ShockRing.png</ColorTexture><AlphaBlend>2</AlphaBlend><ZWrite>False</ZWrite><FadeOutType>1</FadeOutType><FadeOut><Frame>$([int]($life * 0.8))</Frame></FadeOut></RendererCommonValues>" +
  "<DrawingValues><Sprite><Billboard>2</Billboard>$(Colour @(255, 255, 255, $alpha) @(255, 255, 255, 0))</Sprite></DrawingValues><Name>$name</Name><Children /></Node>"
}
$note = "<Node><CommonValues><LocationEffectType>1</LocationEffectType>$(Range Life 50 40 60)</CommonValues>" +
  "<LocationValues><Type>1</Type><PVA><Location>$(Range X 5.2 4.6 5.8)$(Range Y 1 0.5 1.5)</Location><Velocity>$(Range X 0 -0.02 0.02)$(Range Y 0.12 0.08 0.16)$(Range Z 0 -0.03 0.03)</Velocity></PVA></LocationValues>" +
  "<ScalingValues><Type>4</Type><SingleEasing>$(Range Start 1.1 0.8 1.4)$(Range End 0.3 0.2 0.4)<StartSpeed>0</StartSpeed><EndSpeed>0</EndSpeed></SingleEasing></ScalingValues>" +
  "<RendererCommonValues><ColorTexture>Texture/Glint.png</ColorTexture><AlphaBlend>2</AlphaBlend><ZWrite>False</ZWrite><FadeInType>1</FadeInType><FadeIn><Frame>4</Frame></FadeIn><FadeOutType>1</FadeOutType><FadeOut><Frame>24</Frame></FadeOut></RendererCommonValues>" +
  "<DrawingValues><Sprite>$(Colour @(255, 255, 255, 255) @(255, 255, 255, 0))</Sprite></DrawingValues><Name>Note</Name><Children /></Node>"
$notes = "<Node><CommonValues><MaxGeneration><Value>10</Value></MaxGeneration>$(Range Life 65 65 65)$(Range GenerationTime 1 1 1)</CommonValues>" +
  "<RotationValues><Type>1</Type><PVA><Rotation><Y><Max>180</Max><Min>-180</Min></Y></Rotation></PVA></RotationValues>" +
  "<DrawingValues><Type>0</Type></DrawingValues><Name>Notes</Name><Children>$note</Children></Node>"
$children = (Flat 'Ripple' 0 34 11 24 255) + (Flat 'Ripple2' 8 34 11 20 150) + $notes
$project = "<?xml version=`"1.0`" encoding=`"utf-8`"?><EffekseerProject><Root><Name>Root</Name><Children>$children</Children></Root><ToolVersion>1.30</ToolVersion><Version>3</Version><StartFrame>0</StartFrame><EndFrame>80</EndFrame><IsLoop>False</IsLoop></EffekseerProject>"
$xml = [xml]$project
$projectPath = Join-Path $out 'ChimeRipple.efkproj'
$xml.Save($projectPath)
$efk = Join-Path $out 'ChimeRipple.efk'
Remove-Item $efk -ErrorAction SilentlyContinue
$p = Start-Process $Effekseer -ArgumentList '-cui', '-in', "`"$projectPath`"", '-e', "`"$efk`"" -PassThru -Wait -WindowStyle Hidden
if ($p.ExitCode -ne 0 -or -not (Test-Path $efk)) { throw "Effekseer export failed ($($p.ExitCode))" }
Get-ChildItem $out -Recurse -File | Select-Object @{ n = 'File'; e = { $_.FullName.Substring($out.Length + 1) } }, Length
