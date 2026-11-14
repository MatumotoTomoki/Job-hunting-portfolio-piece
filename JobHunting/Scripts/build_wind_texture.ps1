# Draws T_WindStreak.png into SourceArt/Models/Sky: thin white streaks running along U on a transparent 512 x 256
# texture, tiling in both directions. M_WindStreak scrolls it along U to show which way BP_WindZone blows. Run:
#   powershell -File build_wind_texture.ps1
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$out = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\SourceArt\Models\Sky'))
New-Item -ItemType Directory -Force $out | Out-Null
$W, $H = 512, 256
$bmp = New-Object Drawing.Bitmap $W, $H, ([Drawing.Imaging.PixelFormat]::Format32bppArgb)
$g = [Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = 'AntiAlias'
$g.Clear([Drawing.Color]::Transparent)
$rand = New-Object Random 5
for ($i = 0; $i -lt 26; $i++) {
  $y = $rand.Next(4, $H - 4)
  $len = $rand.Next(70, 220)
  $x = $rand.Next(0, $W)
  $width = 1.5 + $rand.NextDouble() * 2.0
  $alpha = $rand.Next(120, 230)
  # Drawn twice when it runs off the right edge, so the texture tiles.
  foreach ($shift in 0, (-$W)) {
    $x0 = $x + $shift
    $brush = New-Object Drawing.Drawing2D.LinearGradientBrush ((New-Object Drawing.PointF $x0, 0), (New-Object Drawing.PointF ($x0 + $len), 0), ([Drawing.Color]::FromArgb(0, 255, 255, 255)), ([Drawing.Color]::FromArgb($alpha, 255, 255, 255)))
    $pen = New-Object Drawing.Pen $brush, $width
    $pen.StartCap = 'Round'; $pen.EndCap = 'Round'
    $g.DrawLine($pen, [float]$x0, [float]$y, [float]($x0 + $len), [float]$y)
  }
}
$bmp.Save((Join-Path $out 'T_WindStreak.png'), [Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Get-Item (Join-Path $out 'T_WindStreak.png') | Select-Object Name, Length
