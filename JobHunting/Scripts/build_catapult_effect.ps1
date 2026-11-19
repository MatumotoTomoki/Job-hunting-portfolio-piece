# Builds the steam catapult's effects (area 2's exit, BP_SteamCatapult): .efkproj files exported to .efk with
# Effekseer's command line, into SourceArt/Effects/Catapult (the steam puff texture is copied from GearSteam).
# Units: 1 Effekseer unit = 20 cm in UE; Effekseer's Y is UE's up; frames are 1/60 s. Both sit at the catapult's
# middle, on its base; its four vents stand 2.8 m (14 units) out, at 45, 135, 225 and 315 degrees.
#   CatapultCharge  loops while the pressure builds: steam jets up out of the four vents, thicker and faster puffs,
#                   with a low hot haze rolling off the base.
#   CatapultBlast   one shot, the launch: a tall column of steam shoots straight up from the pad and a ring of steam
#                   bursts out across the floor.
# Import with Scripts/setup_steam_catapult.py. Run:
#   powershell -File build_catapult_effect.ps1 [-Effekseer <path to Effekseer.exe>]
param([string]$Effekseer = (Join-Path $env:USERPROFILE 'Desktop\Effekseer160Win\Effekseer160Win\Tool\Effekseer.exe'))
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\SourceArt\Effects'))
$out = Join-Path $root 'Catapult'
New-Item -ItemType Directory -Force (Join-Path $out 'Texture') | Out-Null
Copy-Item (Join-Path $root 'GearSteam\Texture\SteamPuff.png') (Join-Path $out 'Texture\SteamPuff.png') -Force

function Range($tag, $center, $min, $max) { "<$tag><Center>$center</Center><Max>$max</Max><Min>$min</Min></$tag>" }
function Axis($x, $y, $z) {
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
# One puff, left where it was born, placed and moving in its parent's frame (X outward, Y up).
function Puff($p) {
  $gen = ''
  if ($p.Count) { $gen += "<MaxGeneration><Value>$($p.Count)</Value></MaxGeneration>" }
  elseif ($p.Every) { $gen += '<MaxGeneration><Infinite>True</Infinite></MaxGeneration>' }
  if ($p.Every) { $gen += Range GenerationTime $p.Every $p.Every $p.Every }
  $accel = if ($p.Acceleration) { "<Acceleration>$(Axis $p.Acceleration[0] $p.Acceleration[1] $p.Acceleration[2])</Acceleration>" } else { '' }
  "<Node><CommonValues>$gen<LocationEffectType>1</LocationEffectType><RotationEffectType>1</RotationEffectType><ScaleEffectType>1</ScaleEffectType>$(Range Life $p.Life[0] $p.Life[1] $p.Life[2])</CommonValues>" +
  "<LocationValues><Type>1</Type><PVA><Location>$(Axis $p.Location[0] $p.Location[1] $p.Location[2])</Location><Velocity>$(Axis $p.Velocity[0] $p.Velocity[1] $p.Velocity[2])</Velocity>$accel</PVA></LocationValues>" +
  "<RotationValues><Type>1</Type><PVA><Rotation><Z><Max>180</Max><Min>-180</Min></Z></Rotation><Velocity><Z><Max>2</Max><Min>-2</Min></Z></Velocity></PVA></RotationValues>" +
  "<ScalingValues><Type>4</Type><SingleEasing>$(Range Start $p.SizeFrom[0] $p.SizeFrom[1] $p.SizeFrom[2])$(Range End $p.SizeTo[0] $p.SizeTo[1] $p.SizeTo[2])<StartSpeed>20</StartSpeed><EndSpeed>-20</EndSpeed></SingleEasing></ScalingValues>" +
  "<RendererCommonValues><ColorTexture>Texture/SteamPuff.png</ColorTexture><AlphaBlend>$($p.Blend)</AlphaBlend><ZWrite>False</ZWrite><FadeInType>1</FadeInType><FadeIn><Frame>$($p.FadeIn)</Frame></FadeIn><FadeOutType>1</FadeOutType><FadeOut><Frame>$($p.FadeOut)</Frame></FadeOut></RendererCommonValues>" +
  "<DrawingValues><Sprite>$(EasedColor $p.From $p.To)</Sprite></DrawingValues><Name>$($p.Name)</Name><Children /></Node>"
}
# A node that draws nothing and lasts the whole effect, at a fixed spot and turn, carrying its puffs.
function Holder($name, $x, $z, $yaw, $children) {
  "<Node><CommonValues>$(Range Life 60 60 60)<RemoveWhenLifeIsExtinct>False</RemoveWhenLifeIsExtinct></CommonValues>" +
  "<LocationValues><Type>0</Type><Fixed><Location><X>$x</X><Z>$z</Z></Location></Fixed></LocationValues>" +
  "<RotationValues><Type>0</Type><Fixed><Rotation><Y>$yaw</Y></Rotation></Fixed></RotationValues>" +
  "<DrawingValues><Type>0</Type></DrawingValues><Name>$name</Name><Children>$children</Children></Node>"
}
function RandomSpawner($name, $every, $count, $life, $children) {
  $gen = if ($count) { "<MaxGeneration><Value>$count</Value></MaxGeneration>" } else { '<MaxGeneration><Infinite>True</Infinite></MaxGeneration>' }
  "<Node><CommonValues>$gen$(Range Life $life $life $life)$(Range GenerationTime $every $every $every)</CommonValues>" +
  "<RotationValues><Type>1</Type><PVA><Rotation><Y><Max>180</Max><Min>-180</Min></Y></Rotation></PVA></RotationValues>" +
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

# ----- CatapultCharge: the vents (Blender-free: Effekseer X/Z is UE's X/Y) -----
$vents = foreach ($k in 0..3) {
  $a = [Math]::PI / 4.0 + $k * [Math]::PI / 2.0
  $jet = Puff @{
    Name = "Vent$k"; Every = 2; Life = @(38, 30, 46); Blend = 1; FadeIn = 2; FadeOut = 22
    Location = @(@(0, -0.3, 0.3), @(4.5, 4.3, 4.7), @(0, -0.3, 0.3)); Velocity = @(@(0, -0.03, 0.03), @(0.4, 0.3, 0.5), @(0, -0.03, 0.03))
    Acceleration = @($null, @(-0.006, -0.007, -0.005), $null)
    SizeFrom = @(1.0, 0.8, 1.2); SizeTo = @(5.5, 4.5, 6.5); From = @(250, 250, 245, 210); To = @(215, 215, 215, 0)
  }
  Holder "VentAt$k" ([Math]::Round(14.0 * [Math]::Cos($a), 3)) ([Math]::Round(14.0 * [Math]::Sin($a), 3)) 0 $jet
}
$haze = Puff @{
  Name = 'BaseHaze'; Life = @(60, 50, 70); Blend = 1; FadeIn = 8; FadeOut = 35
  Location = @(@(11, 9, 13), @(0.5, 0.2, 0.8), $null); Velocity = @(@(0.08, 0.04, 0.12), @(0.02, 0.0, 0.04), $null)
  SizeFrom = @(3, 2.5, 3.5); SizeTo = @(8, 7, 10); From = @(240, 240, 235, 110); To = @(220, 220, 220, 0)
}
$hazes = RandomSpawner 'HazeSpawner' 3 $null 75 $haze
$chargeProject = Project (($vents -join '') + $hazes) 240 'True'

# ----- CatapultBlast: the launch -----
$column = Puff @{
  Name = 'Column'; Life = @(55, 45, 65); Blend = 1; FadeIn = 1; FadeOut = 35
  Location = @(@(0, -1.5, 1.5), @(1, 0, 2), @(0, -1.5, 1.5)); Velocity = @(@(0, -0.08, 0.08), @(1.2, 0.8, 1.6), @(0, -0.08, 0.08))
  Acceleration = @($null, @(-0.02, -0.025, -0.015), $null)
  SizeFrom = @(5, 4, 6); SizeTo = @(16, 13, 19); From = @(255, 255, 250, 230); To = @(225, 225, 225, 0)
}
$columnNode = "<Node><CommonValues><MaxGeneration><Value>40</Value></MaxGeneration>$(Range Life 70 70 70)$(Range GenerationTime 0.5 0.5 0.5)</CommonValues><DrawingValues><Type>0</Type></DrawingValues><Name>ColumnSpawner</Name><Children>$column</Children></Node>"
$ring = Puff @{
  Name = 'Ring'; Life = @(70, 55, 85); Blend = 1; FadeIn = 2; FadeOut = 45
  Location = @(@(12, 11, 13), @(0.3, 0, 0.6), $null); Velocity = @(@(0.45, 0.3, 0.6), @(0.03, 0.01, 0.05), $null)
  Acceleration = @(@(-0.006, -0.007, -0.005), $null, $null)
  SizeFrom = @(4, 3.5, 4.5); SizeTo = @(12, 10, 14); From = @(250, 250, 245, 220); To = @(215, 215, 215, 0)
}
$rings = RandomSpawner 'RingSpawner' 0.25 40 95 $ring
$blastProject = Project ($columnNode + $rings) 140 'False'

foreach ($variant in @(@('CatapultCharge', $chargeProject), @('CatapultBlast', $blastProject))) {
  $xml = [xml]$variant[1]
  $projectPath = Join-Path $out ($variant[0] + '.efkproj')
  $xml.Save($projectPath)
  $efk = Join-Path $out ($variant[0] + '.efk')
  Remove-Item $efk -ErrorAction SilentlyContinue
  $p = Start-Process $Effekseer -ArgumentList '-cui', '-in', "`"$projectPath`"", '-e', "`"$efk`"" -PassThru -Wait -WindowStyle Hidden
  if ($p.ExitCode -ne 0 -or -not (Test-Path $efk)) { throw "Effekseer export failed for $($variant[0]) ($($p.ExitCode))" }
}
Get-ChildItem $out -Recurse -File | Select-Object @{ n = 'File'; e = { $_.FullName.Substring($out.Length + 1) } }, Length
