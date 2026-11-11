# Draws the danger button's textures into SourceArt/Models/DangerButton (build_danger_button_blender.py maps them):
#   T_DangerStripes.png  yellow and black hazard stripes, for the band round the pedestal (tiles across)
#   T_DangerSign.png     a "do not press" sign: a hand pressing a button, crossed out in red
#   T_DangerLabel.png    "BUTTON" in white on red, wrapped once round the button's base
# Run: powershell -File build_danger_button_textures.ps1
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$out = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\SourceArt\Models\DangerButton'))
New-Item -ItemType Directory -Force $out | Out-Null
$yellow = [Drawing.Color]::FromArgb(255, 245, 196, 0)
$black = [Drawing.Color]::FromArgb(255, 20, 20, 20)
$red = [Drawing.Color]::FromArgb(255, 200, 20, 20)

function New-Canvas($w, $h) {
  $bmp = New-Object Drawing.Bitmap $w, $h
  $g = [Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode = 'AntiAlias'
  $g.TextRenderingHint = 'AntiAliasGridFit'
  return @($bmp, $g)
}

# Stripes: 45 degree bands, tiling left to right.
$bmp, $g = New-Canvas 512 128
$g.Clear($yellow)
$brush = New-Object Drawing.SolidBrush $black
for ($x = -256; $x -lt 768; $x += 128) {
  $points = [Drawing.PointF[]]@((New-Object Drawing.PointF ($x), 0), (New-Object Drawing.PointF ($x + 64), 0), (New-Object Drawing.PointF ($x + 64 - 128), 128), (New-Object Drawing.PointF ($x - 128), 128))
  $g.FillPolygon($brush, $points)
}
$bmp.Save((Join-Path $out 'T_DangerStripes.png'), [Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()

# Sign: white disc, a hand pressing a button, a red ring and slash over it.
$bmp, $g = New-Canvas 256 256
$g.Clear($black)
$g.FillEllipse([Drawing.Brushes]::White, 24, 24, 208, 208)
$ink = New-Object Drawing.SolidBrush $black
$g.FillRectangle($ink, 78, 170, 100, 18)            # the button's base
$g.FillEllipse($ink, 98, 150, 60, 30)                # the button
$g.FillRectangle($ink, 116, 70, 24, 80)              # the pointing finger
$g.FillEllipse($ink, 116, 60, 24, 24)
$g.FillRectangle($ink, 140, 96, 36, 44)              # the fist
$g.FillEllipse($ink, 150, 88, 34, 60)
$pen = New-Object Drawing.Pen $red, 22
$g.DrawEllipse($pen, 36, 36, 184, 184)
$g.DrawLine($pen, 66, 66, 190, 190)
$bmp.Save((Join-Path $out 'T_DangerSign.png'), [Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()

# Label: BUTTON, twice round the base (front and back).
$bmp, $g = New-Canvas 1024 128
$g.Clear($red)
$font = New-Object Drawing.Font 'Arial Black', 64, ([Drawing.FontStyle]::Bold), ([Drawing.GraphicsUnit]::Pixel)
$format = New-Object Drawing.StringFormat
$format.Alignment = 'Center'
$format.LineAlignment = 'Center'
foreach ($cx in 256, 768) {
  $g.DrawString('BUTTON', $font, [Drawing.Brushes]::White, (New-Object Drawing.RectangleF ($cx - 256), 0, 512, 128), $format)
}
$bmp.Save((Join-Path $out 'T_DangerLabel.png'), [Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Get-ChildItem $out -Filter *.png | Select-Object Name, Length
