# Draws the screen cracks for the danger button into SourceArt/Models/DangerButton (transparent PNGs, 1920 x 1080,
# shown full screen over the game by WBP_DangerOverlay):
#   T_Crack1.png  the first press: one impact, cracks running out from it, a few rings of broken glass round it
#   T_Crack2.png  the second press: a second, bigger impact; meant to be shown on top of T_Crack1
# Each crack is a jagged white line with a dark line beside it, as in cracked glass. Run:
#   powershell -File build_screen_cracks.ps1
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$out = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\SourceArt\Models\DangerButton'))
New-Item -ItemType Directory -Force $out | Out-Null
$W, $H = 1920, 1080

function Draw-Impact($g, $rand, $cx, $cy, $count, $reach, $rings) {
  $light = New-Object Drawing.Pen ([Drawing.Color]::FromArgb(230, 255, 255, 255)), 2.2
  $shade = New-Object Drawing.Pen ([Drawing.Color]::FromArgb(150, 0, 0, 0)), 2.0
  $thin = New-Object Drawing.Pen ([Drawing.Color]::FromArgb(170, 255, 255, 255)), 1.2
  $ends = @()
  for ($i = 0; $i -lt $count; $i++) {
    $angle = 2.0 * [Math]::PI * ($i + $rand.NextDouble() * 0.6) / $count
    $length = $reach * (0.45 + 0.75 * $rand.NextDouble())
    $points = New-Object Collections.Generic.List[Drawing.PointF]
    $x, $y = $cx, $cy
    $points.Add((New-Object Drawing.PointF $x, $y))
    $steps = 9
    for ($s = 1; $s -le $steps; $s++) {
      $a = $angle + ($rand.NextDouble() - 0.5) * 0.5
      $x += [Math]::Cos($a) * $length / $steps
      $y += [Math]::Sin($a) * $length / $steps
      $points.Add((New-Object Drawing.PointF $x, $y))
      # Now and then a branch.
      if ($rand.NextDouble() -lt 0.25) {
        $b = $a + ($rand.NextDouble() - 0.5) * 1.6
        $bl = $length * (0.1 + 0.2 * $rand.NextDouble())
        $g.DrawLine($thin, [float]$x, [float]$y, [float]($x + [Math]::Cos($b) * $bl), [float]($y + [Math]::Sin($b) * $bl))
      }
    }
    $array = $points.ToArray()
    $offset = $array | ForEach-Object { New-Object Drawing.PointF ($_.X + 1.8), ($_.Y + 1.8) }
    $g.DrawLines($shade, [Drawing.PointF[]]$offset)
    $g.DrawLines($light, $array)
    $ends += , $array
  }
  # Rings: short jagged segments joining neighbouring cracks at a few distances out.
  foreach ($ring in $rings) {
    for ($i = 0; $i -lt $ends.Count; $i++) {
      if ($rand.NextDouble() -lt 0.35) { continue }
      $a = $ends[$i]; $b = $ends[($i + 1) % $ends.Count]
      $k = [Math]::Min([int]($ring * ($a.Count - 1)), $a.Count - 1)
      $k2 = [Math]::Min([int]($ring * ($b.Count - 1)), $b.Count - 1)
      $mid = New-Object Drawing.PointF ((($a[$k].X + $b[$k2].X) / 2) + ($rand.NextDouble() - 0.5) * 20), ((($a[$k].Y + $b[$k2].Y) / 2) + ($rand.NextDouble() - 0.5) * 20)
      $g.DrawLines($thin, [Drawing.PointF[]]@($a[$k], $mid, $b[$k2]))
    }
  }
  # The impact itself: a small white burst.
  $burst = New-Object Drawing.SolidBrush ([Drawing.Color]::FromArgb(120, 255, 255, 255))
  $g.FillEllipse($burst, [float]($cx - 14), [float]($cy - 14), 28, 28)
}

function New-Crack($file, $impacts, $seed) {
  $bmp = New-Object Drawing.Bitmap $W, $H, ([Drawing.Imaging.PixelFormat]::Format32bppArgb)
  $g = [Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode = 'AntiAlias'
  $g.Clear([Drawing.Color]::Transparent)
  $rand = New-Object Random $seed
  foreach ($impact in $impacts) { Draw-Impact $g $rand $impact[0] $impact[1] $impact[2] $impact[3] $impact[4] }
  $bmp.Save((Join-Path $out $file), [Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose()
}

New-Crack 'T_Crack1.png' @(, @(1180, 420, 12, 520, @(0.15, 0.35))) 7
New-Crack 'T_Crack2.png' @(@(560, 680, 16, 900, @(0.12, 0.3, 0.55)), @(1500, 820, 9, 420, @(0.2))) 11
Get-ChildItem $out -Filter 'T_Crack*.png' | Select-Object Name, Length
