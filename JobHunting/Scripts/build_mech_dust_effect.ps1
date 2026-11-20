# Builds the big mechanisms' dust (BP_Mechanism; the user, 2026-11-20: "more weight as they come out"), into
# SourceArt/Effects/MechDust. The emitters keep world scale 1 (mechanism actors are scaled to size their body), born at
# the actor's origin, the top of the body:
#   MechDust  loops while a part moves: dust sifting down from round its top edge (~3 m across) and small pebbles
#             dropping out of it, a few at a time
#   MechThud  one shot as a part comes to rest: a ring of dust rolling out from it and a puff hanging in the air
# Units: 1 Effekseer unit = 20 cm, Y up. Texture CloudPuff copied from SunImpact.
#   powershell -File build_mech_dust_effect.ps1 [-Effekseer <path to Effekseer.exe>]
param([string]$Effekseer = (Join-Path $env:USERPROFILE 'Desktop\Effekseer160Win\Effekseer160Win\Tool\Effekseer.exe'))
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\SourceArt\Effects'))
$out = Join-Path $root 'MechDust'
New-Item -ItemType Directory -Force (Join-Path $out 'Texture') | Out-Null
Copy-Item (Join-Path $root 'SunImpact\Texture\CloudPuff.png') (Join-Path $out 'Texture\CloudPuff.png') -Force

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
# One kind of particle. $gen: 'loop' (every $p.Every frames, forever) or 'burst' ($p.Count of them at once, each
# turned to a random yaw so Location X fans them all round).
function Particle($p) {
  $accel = if ($p.Acceleration) { "<Acceleration>$(Axis $p.Acceleration[0] $p.Acceleration[1] $p.Acceleration[2])</Acceleration>" } else { '' }
  $common = if ($p.Every) { "<MaxGeneration><Infinite>True</Infinite></MaxGeneration>$(Range GenerationTime $p.Every $p.Every $p.Every)" }
            else { "<MaxGeneration><Value>$($p.Count)</Value></MaxGeneration>$(Range GenerationTime 0.2 0.2 0.2)" }
  $turn = if ($p.Every) { '' } else { "<RotationValues><Type>1</Type><PVA><Rotation><Y><Max>180</Max><Min>-180</Min></Y></Rotation></PVA></RotationValues>" }
  $child = "<Node><CommonValues><LocationEffectType>1</LocationEffectType><RotationEffectType>1</RotationEffectType><ScaleEffectType>1</ScaleEffectType>$(Range Life $p.Life[0] $p.Life[1] $p.Life[2])</CommonValues>" +
    "<LocationValues><Type>1</Type><PVA><Location>$(Axis $p.Location[0] $p.Location[1] $p.Location[2])</Location><Velocity>$(Axis $p.Velocity[0] $p.Velocity[1] $p.Velocity[2])</Velocity>$accel</PVA></LocationValues>" +
    "<RotationValues><Type>1</Type><PVA><Rotation><Z><Max>180</Max><Min>-180</Min></Z></Rotation><Velocity><Z><Max>2</Max><Min>-2</Min></Z></Velocity></PVA></RotationValues>" +
    "<ScalingValues><Type>4</Type><SingleEasing>$(Range Start $p.SizeFrom[0] $p.SizeFrom[1] $p.SizeFrom[2])$(Range End $p.SizeTo[0] $p.SizeTo[1] $p.SizeTo[2])<StartSpeed>20</StartSpeed><EndSpeed>-20</EndSpeed></SingleEasing></ScalingValues>" +
    "<RendererCommonValues><ColorTexture>Texture/CloudPuff.png</ColorTexture><AlphaBlend>1</AlphaBlend><ZWrite>False</ZWrite><FadeInType>1</FadeInType><FadeIn><Frame>$($p.FadeIn)</Frame></FadeIn><FadeOutType>1</FadeOutType><FadeOut><Frame>$($p.FadeOut)</Frame></FadeOut></RendererCommonValues>" +
    "<DrawingValues><Sprite>$(Colour $p.From $p.To)</Sprite></DrawingValues><Name>$($p.Name)</Name><Children /></Node>"
  "<Node><CommonValues>$common$(Range Life $p.HolderLife $p.HolderLife $p.HolderLife)</CommonValues>$turn<DrawingValues><Type>0</Type></DrawingValues><Name>$($p.Name)Gen</Name><Children>$child</Children></Node>"
}
function Export($name, $children, $end, $loop) {
  $project = "<?xml version=`"1.0`" encoding=`"utf-8`"?><EffekseerProject><Root><Name>Root</Name><Children>$children</Children></Root><ToolVersion>1.30</ToolVersion><Version>3</Version><StartFrame>0</StartFrame><EndFrame>$end</EndFrame><IsLoop>$loop</IsLoop></EffekseerProject>"
  $xml = [xml]$project
  $projectPath = Join-Path $out "$name.efkproj"
  $xml.Save($projectPath)
  $efk = Join-Path $out "$name.efk"
  Remove-Item $efk -ErrorAction SilentlyContinue
  $p = Start-Process $Effekseer -ArgumentList '-cui', '-in', "`"$projectPath`"", '-e', "`"$efk`"" -PassThru -Wait -WindowStyle Hidden
  if ($p.ExitCode -ne 0 -or -not (Test-Path $efk)) { throw "Effekseer export failed for $name ($($p.ExitCode))" }
}
$DUST = @(200, 185, 160, 150); $DUST_OUT = @(210, 198, 180, 0)

# ----- MechDust (loop) -----
$sift = Particle @{ Name = 'Sift'; Every = 3; HolderLife = 60; Life = @(60, 45, 75); FadeIn = 6; FadeOut = 40
  Location = @(@(0, -7.5, 7.5), @(-0.5, -1.0, 0), @(0, -7.5, 7.5)); Velocity = @(@(0, -0.01, 0.01), @(-0.03, -0.05, -0.015), @(0, -0.01, 0.01))
  SizeFrom = @(1.4, 1.0, 1.8); SizeTo = @(3.2, 2.6, 3.8); From = $DUST; To = $DUST_OUT }
$pebble = Particle @{ Name = 'Pebble'; Every = 6; HolderLife = 60; Life = @(40, 32, 48); FadeIn = 1; FadeOut = 8
  Location = @(@(0, -7.0, 7.0), @(-0.5, -1.0, 0), @(0, -7.0, 7.0)); Velocity = @(@(0, -0.02, 0.02), @(0, -0.02, 0.0), @(0, -0.02, 0.02))
  Acceleration = @($null, @(-0.02, -0.022, -0.018), $null)
  SizeFrom = @(0.22, 0.15, 0.3); SizeTo = @(0.2, 0.14, 0.28); From = @(90, 80, 70, 255); To = @(90, 80, 70, 200) }
Export 'MechDust' ($sift + $pebble) 120 'True'

# ----- MechThud (one shot) -----
$roll = Particle @{ Name = 'Roll'; Count = 16; HolderLife = 70; Life = @(55, 45, 65); FadeIn = 2; FadeOut = 40
  Location = @(@(4.0, 3.0, 5.0), @(-1.0, -1.5, -0.5), $null); Velocity = @(@(0.18, 0.12, 0.24), @(0.02, 0.0, 0.04), $null)
  Acceleration = @(@(-0.003, -0.004, -0.002), $null, $null)
  SizeFrom = @(2.0, 1.6, 2.4); SizeTo = @(4.5, 3.8, 5.2); From = @(205, 190, 165, 190); To = $DUST_OUT }
$hang = Particle @{ Name = 'Hang'; Count = 6; HolderLife = 90; Life = @(80, 70, 90); FadeIn = 4; FadeOut = 60
  Location = @(@(2.0, 0.5, 3.5), @(0.0, -0.5, 0.5), $null); Velocity = @(@(0.03, 0.01, 0.05), @(0.015, 0.005, 0.025), $null)
  SizeFrom = @(3.0, 2.5, 3.5); SizeTo = @(6.0, 5.0, 7.0); From = @(210, 198, 175, 120); To = $DUST_OUT }
Export 'MechThud' ($roll + $hang) 100 'False'
Get-ChildItem $out -Recurse -File | Select-Object @{ n = 'File'; e = { $_.FullName.Substring($out.Length + 1) } }, Length
