# Builds the light pillar's effect for the area 3 -> 4 move (BP_LightGate / BP_LightArrival; the user, 2026-11-20):
# SourceArt/Effects/LightMotes/LightMotes.efk, looping, at the pillar's foot:
#   Halo   a soft warm glow lying flat on the ground under the pillar (a Fixed billboard turned flat), breathing slowly
#   Motes  small bright motes of light rising from the ground inside the pillar and fading high up
#   Glints a few four-pointed glints drifting up among them
# Units: 1 Effekseer unit = 20 cm, Y up; the pillar is 3 m across. Textures copied from CloudPoof (CloudPuff, Glint).
#   powershell -File build_light_motes_effect.ps1 [-Effekseer <path to Effekseer.exe>]
param([string]$Effekseer = (Join-Path $env:USERPROFILE 'Desktop\Effekseer160Win\Effekseer160Win\Tool\Effekseer.exe'))
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\SourceArt\Effects'))
$out = Join-Path $root 'LightMotes'
New-Item -ItemType Directory -Force (Join-Path $out 'Texture') | Out-Null
foreach ($name in 'CloudPuff.png', 'Glint.png') { Copy-Item (Join-Path $root "CloudPoof\Texture\$name") (Join-Path $out "Texture\$name") -Force }

function Range($tag, $center, $min, $max) { "<$tag><Center>$center</Center><Max>$max</Max><Min>$min</Min></$tag>" }
function Colour($from, $to) {
  $parts = foreach ($pair in @(@('Start', $from), @('End', $to))) {
    $c = $pair[1]
    "<$($pair[0])>$(Range R $c[0] $c[0] $c[0])$(Range G $c[1] $c[1] $c[1])$(Range B $c[2] $c[2] $c[2])$(Range A $c[3] $c[3] $c[3])</$($pair[0])>"
  }
  "<ColorAll>2</ColorAll><ColorAll_Easing>$($parts -join '')</ColorAll_Easing>"
}
function Rising($name, $texture, $every, $life, $size, $speed, $from, $to) {
  "<Node><CommonValues><MaxGeneration><Infinite>True</Infinite></MaxGeneration>$(Range Life $life[0] $life[1] $life[2])$(Range GenerationTime $every $every $every)<LocationEffectType>1</LocationEffectType></CommonValues>" +
  "<LocationValues><Type>1</Type><PVA><Location>$(Range X 0 -6 6)$(Range Y 0.3 0 1)$(Range Z 0 -6 6)</Location><Velocity>$(Range X 0 -0.01 0.01)$(Range Y $speed[0] $speed[1] $speed[2])$(Range Z 0 -0.01 0.01)</Velocity></PVA></LocationValues>" +
  "<RotationValues><Type>1</Type><PVA><Rotation><Z><Max>180</Max><Min>-180</Min></Z></Rotation><Velocity><Z><Max>1.5</Max><Min>-1.5</Min></Z></Velocity></PVA></RotationValues>" +
  "<ScalingValues><Type>4</Type><SingleEasing>$(Range Start $size[0] $size[0] $size[1])$(Range End $size[2] $size[2] $size[3])<StartSpeed>0</StartSpeed><EndSpeed>0</EndSpeed></SingleEasing></ScalingValues>" +
  "<RendererCommonValues><ColorTexture>Texture/$texture</ColorTexture><AlphaBlend>2</AlphaBlend><ZWrite>False</ZWrite><FadeInType>1</FadeInType><FadeIn><Frame>15</Frame></FadeIn><FadeOutType>1</FadeOutType><FadeOut><Frame>30</Frame></FadeOut></RendererCommonValues>" +
  "<DrawingValues><Sprite>$(Colour $from $to)</Sprite></DrawingValues><Name>$name</Name><Children /></Node>"
}
# The halo: lasts the whole effect, flat on the ground, gently swelling.
$halo = "<Node><CommonValues>$(Range Life 120 120 120)<RemoveWhenLifeIsExtinct>False</RemoveWhenLifeIsExtinct></CommonValues>" +
  "<LocationValues><Type>0</Type><Fixed><Location><Y>0.05</Y></Location></Fixed></LocationValues>" +
  "<RotationValues><Type>0</Type><Fixed><Rotation><X>90</X></Rotation></Fixed></RotationValues>" +
  "<ScalingValues><Type>0</Type><Fixed><Scale><X>17</X><Y>17</Y><Z>1</Z></Scale></Fixed></ScalingValues>" +
  "<RendererCommonValues><ColorTexture>Texture/CloudPuff.png</ColorTexture><AlphaBlend>2</AlphaBlend><ZWrite>False</ZWrite></RendererCommonValues>" +
  "<DrawingValues><Sprite><Billboard>2</Billboard><ColorAll_Fixed><R>255</R><G>235</G><B>190</B><A>150</A></ColorAll_Fixed></Sprite></DrawingValues><Name>Halo</Name><Children /></Node>"
$motes = Rising 'Motes' 'CloudPuff.png' 0.5 @(90, 70, 110) @(0.35, 0.5, 0.12, 0.18) @(0.11, 0.07, 0.15) @(255, 248, 225, 255) @(255, 230, 180, 0)
$glints = Rising 'Glints' 'Glint.png' 4 @(80, 60, 100) @(0.6, 0.8, 0.25, 0.35) @(0.08, 0.05, 0.11) @(255, 240, 200, 255) @(255, 220, 160, 0)
$project = "<?xml version=`"1.0`" encoding=`"utf-8`"?><EffekseerProject><Root><Name>Root</Name><Children>$halo$motes$glints</Children></Root><ToolVersion>1.30</ToolVersion><Version>3</Version><StartFrame>0</StartFrame><EndFrame>240</EndFrame><IsLoop>True</IsLoop></EffekseerProject>"
$xml = [xml]$project
$projectPath = Join-Path $out 'LightMotes.efkproj'
$xml.Save($projectPath)
$efk = Join-Path $out 'LightMotes.efk'
Remove-Item $efk -ErrorAction SilentlyContinue
$p = Start-Process $Effekseer -ArgumentList '-cui', '-in', "`"$projectPath`"", '-e', "`"$efk`"" -PassThru -Wait -WindowStyle Hidden
if ($p.ExitCode -ne 0 -or -not (Test-Path $efk)) { throw "Effekseer export failed ($($p.ExitCode))" }
Get-ChildItem $out -Recurse -File | Select-Object @{ n = 'File'; e = { $_.FullName.Substring($out.Length + 1) } }, Length
