# Draws the sun's faces into one atlas, SourceArt/Models/Sun/T_SunFaces.png: 4 x 2 cells of 512 px, read left to right,
# top row first, so face N is column N % 4, row N / 4 (M_SunFace picks one with its FaceIndex parameter).
#   0  the first face: upright oval eyes and an "ω" mouth
#   1  (´Д｀)
#   2  (╯‵□′)╯   the arms stick out past the cheeks
#   3  (＃°Д°)
#   4  (´。＿。｀)
# A cell covers the face patch of SM_Sun: -0.8..0.8 of the sun's radius across and up, as seen from the front. Each part
# is placed in those units (x to the viewer's right, y up) and sized to a height or width. Run:
#   powershell -File build_sun_faces.ps1
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$out = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\SourceArt\Models\Sun'))
$CELL = 512
$SPAN = 0.8
$FONT = [Drawing.FontFamily]::new('Yu Gothic')
$fill = [Drawing.Color]::FromArgb(255, 200, 30, 45)
$edge = [Drawing.Color]::FromArgb(255, 120, 10, 25)
$shine = [Drawing.Color]::FromArgb(110, 255, 150, 150)

function Px([int]$face, [double]$x, [double]$y) {
  $s = $CELL / (2 * $SPAN)
  [Drawing.PointF]::new([float](($face % 4) * $CELL + ($x + $SPAN) * $s), [float]([math]::Floor($face / 4) * $CELL + ($SPAN - $y) * $s))
}

# Fills a path in the face colour with a darker rim and a soft highlight on its upper left.
function Paint($g, $path) {
  $pen = [Drawing.Pen]::new($edge, 7); $pen.LineJoin = 'Round'
  $g.DrawPath($pen, $path)
  $g.FillPath([Drawing.SolidBrush]::new($fill), $path)
  # Inside the shape: the highlight colour, then the face colour again shifted down-right, leaving a thin bright rim.
  $g.SetClip($path)
  $g.FillPath([Drawing.SolidBrush]::new($shine), $path)
  $shifted = $path.Clone()
  $m = [Drawing.Drawing2D.Matrix]::new(); $m.Translate(3, 4)
  $shifted.Transform($m)
  $g.FillPath([Drawing.SolidBrush]::new($fill), $shifted)
  $g.ResetClip()
}

# A text part (a glyph or a few) centred on (x, y), scaled so its ink is $size tall, or wide with -Wide.
function Glyph($g, [int]$face, $text, [double]$x, [double]$y, [double]$size, [switch]$Wide, [switch]$Mirror) {
  $path = [Drawing.Drawing2D.GraphicsPath]::new()
  $path.AddString($text, $FONT, [int][Drawing.FontStyle]::Bold, 200, [Drawing.PointF]::new(0, 0), [Drawing.StringFormat]::GenericTypographic)
  $b = $path.GetBounds()
  $target = $size * $CELL / (2 * $SPAN)
  $k = if ($Wide) { $target / $b.Width } else { $target / $b.Height }
  $c = Px $face $x $y
  $m = [Drawing.Drawing2D.Matrix]::new()
  $m.Translate($c.X, $c.Y)
  $m.Scale($(if ($Mirror) { -$k } else { $k }), $k)
  $m.Translate(-($b.X + $b.Width / 2), -($b.Y + $b.Height / 2))
  $path.Transform($m)
  Paint $g $path
}

function Oval($g, [int]$face, [double]$x, [double]$y, [double]$halfW, [double]$halfH) {
  $path = [Drawing.Drawing2D.GraphicsPath]::new()
  $a = Px $face ($x - $halfW) ($y + $halfH); $b = Px $face ($x + $halfW) ($y - $halfH)
  $path.AddEllipse($a.X, $a.Y, $b.X - $a.X, $b.Y - $a.Y)
  Paint $g $path
}

$bmp = [Drawing.Bitmap]::new(4 * $CELL, 2 * $CELL, [Drawing.Imaging.PixelFormat]::Format32bppArgb)
$g = [Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = 'AntiAlias'
# Transparent, but in the face colour, so filtering at the edges does not darken them.
$g.Clear([Drawing.Color]::FromArgb(0, 200, 30, 45))

# 0: the first face, as the Blender model had it.
Oval $g 0 -0.27 0.03 0.05 0.11
Oval $g 0 0.27 0.03 0.05 0.11
Glyph $g 0 'ω' 0 -0.06 0.28 -Wide
# 1: (´Д｀)
Glyph $g 1 '´' -0.3 0.12 0.16
Glyph $g 1 '｀' 0.3 0.12 0.16
Glyph $g 1 'Д' 0 -0.1 0.3
# 2: (╯‵□′)╯
Glyph $g 2 '‵' -0.27 0.1 0.2
Glyph $g 2 '′' 0.27 0.1 0.2
Glyph $g 2 '□' 0 -0.12 0.26
Glyph $g 2 '╯' -0.6 -0.2 0.26
Glyph $g 2 '╯' 0.6 -0.2 0.26
# 3: (＃°Д°)
Glyph $g 3 '＃' -0.46 0.36 0.22
Glyph $g 3 '°' -0.26 0.1 0.13
Glyph $g 3 '°' 0.26 0.1 0.13
Glyph $g 3 'Д' 0 -0.12 0.3
# 4: (´。＿。｀)
Glyph $g 4 '´' -0.33 0.24 0.12
Glyph $g 4 '｀' 0.33 0.24 0.12
Glyph $g 4 '。' -0.24 0.04 0.14
Glyph $g 4 '。' 0.24 0.04 0.14
Glyph $g 4 '＿' 0 -0.14 0.3 -Wide

$g.Dispose()
$path = Join-Path $out 'T_SunFaces.png'
$bmp.Save($path, [Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
Get-Item $path | Select-Object Name, Length
