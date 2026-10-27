# Draws the pause-menu title image (T_PauseTitle.png) to match the player:
# white round body, green swirl scarf, golden halo.
Add-Type -AssemblyName System.Drawing

$Text = "ポーズメニュー"
$FontName = "HGMaruGothicMPRO"
$OutPath = Join-Path $PSScriptRoot "Art\T_PauseTitle.png"
$Width = 1024
$Height = 256

$ScarfGreen = [System.Drawing.Color]::FromArgb(255, 38, 102, 52)
$DarkGreen = [System.Drawing.Color]::FromArgb(255, 20, 60, 30)
$BodyWhite = [System.Drawing.Color]::FromArgb(255, 255, 255, 255)
$SoftBlue = [System.Drawing.Color]::FromArgb(255, 222, 236, 250)
$HaloGold = [System.Drawing.Color]::FromArgb(255, 255, 214, 110)
$HaloGlow = [System.Drawing.Color]::FromArgb(90, 255, 225, 140)

function New-RoundPen($color, $width) {
    $pen = New-Object System.Drawing.Pen($color, $width)
    $pen.LineJoin = [System.Drawing.Drawing2D.LineJoin]::Round
    $pen.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
    $pen.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
    return $pen
}

# Swirl like the scarf pattern, centred at (cx, cy).
function New-SwirlPath($cx, $cy, $radius, $turns) {
    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    $steps = [int](60 * $turns)
    $points = for ($i = 0; $i -le $steps; $i++) {
        $t = $i / $steps
        $angle = $t * $turns * 2 * [Math]::PI
        $r = $radius * $t
        New-Object System.Drawing.PointF(($cx + $r * [Math]::Cos($angle)), ($cy + $r * [Math]::Sin($angle)))
    }
    $path.AddLines([System.Drawing.PointF[]]$points)
    return $path
}

$bitmap = New-Object System.Drawing.Bitmap($Width, $Height, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$g = [System.Drawing.Graphics]::FromImage($bitmap)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.Clear([System.Drawing.Color]::Transparent)

# Build each character separately with a little bounce and tilt so the title feels soft and playful.
$font = New-Object System.Drawing.FontFamily($FontName)
$fontSize = 128
$format = [System.Drawing.StringFormat]::GenericTypographic
$charPaths = @()
$x = 0.0
$index = 0
foreach ($ch in $Text.ToCharArray()) {
    $p = New-Object System.Drawing.Drawing2D.GraphicsPath
    $p.AddString([string]$ch, $font, [int][System.Drawing.FontStyle]::Bold, $fontSize, (New-Object System.Drawing.PointF(0, 0)), $format)
    $b = $p.GetBounds()
    $matrix = New-Object System.Drawing.Drawing2D.Matrix
    $bounce = if ($index % 2 -eq 0) { -6 } else { 6 }
    $tilt = if ($index % 2 -eq 0) { -4 } else { 4 }
    $matrix.Translate(($x - $b.X), $bounce)
    $matrix.RotateAt($tilt, (New-Object System.Drawing.PointF(($b.X + $b.Width / 2), ($b.Y + $b.Height / 2))))
    $p.Transform($matrix)
    $charPaths += $p
    $x += $b.Width + 6
    $index++
}

$textPath = New-Object System.Drawing.Drawing2D.GraphicsPath
foreach ($p in $charPaths) { $textPath.AddPath($p, $false) }
$tb = $textPath.GetBounds()
# Centre the text, leaving room on the left for the halo-wearing swirl mark.
$offsetX = ($Width - $tb.Width) / 2 - $tb.X + 40
$offsetY = ($Height - $tb.Height) / 2 - $tb.Y + 18
$center = New-Object System.Drawing.Drawing2D.Matrix
$center.Translate($offsetX, $offsetY)
$textPath.Transform($center)
$tb = $textPath.GetBounds()

# Shadow, thick green outline, white rim, then the white body with a soft blue bottom like the character's shading.
$shadow = $textPath.Clone()
$shift = New-Object System.Drawing.Drawing2D.Matrix
$shift.Translate(0, 8)
$shadow.Transform($shift)
$g.DrawPath((New-RoundPen ([System.Drawing.Color]::FromArgb(110, 0, 0, 0)) 30), $shadow)
$g.DrawPath((New-RoundPen $DarkGreen 30), $textPath)
$g.DrawPath((New-RoundPen $ScarfGreen 22), $textPath)
$g.DrawPath((New-RoundPen $BodyWhite 8), $textPath)
$fill = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
    (New-Object System.Drawing.PointF(0, $tb.Top)),
    (New-Object System.Drawing.PointF(0, $tb.Bottom)),
    $BodyWhite, $SoftBlue)
$g.FillPath($fill, $textPath)

# Little round "body" mark with a swirl and a halo on the left.
$markX = $tb.Left - 70
$markY = $Height / 2 + 14
$g.FillEllipse((New-Object System.Drawing.SolidBrush($DarkGreen)), ($markX - 44), ($markY - 44), 88, 88)
$g.FillEllipse((New-Object System.Drawing.SolidBrush($ScarfGreen)), ($markX - 38), ($markY - 38), 76, 76)
$g.DrawPath((New-RoundPen $BodyWhite 7), (New-SwirlPath $markX $markY 28 2.2))
$haloRect = New-Object System.Drawing.RectangleF(($markX - 40), ($markY - 82), 80, 22)
$g.DrawEllipse((New-RoundPen $HaloGlow 18), $haloRect)
$g.DrawEllipse((New-RoundPen $HaloGold 8), $haloRect)
$g.DrawEllipse((New-RoundPen $BodyWhite 2), $haloRect)

# Small swirl and sparkle on the right to balance the mark.
$g.DrawPath((New-RoundPen $DarkGreen 9), (New-SwirlPath ($tb.Right + 42) ($markY - 6) 20 1.8))
$g.DrawPath((New-RoundPen $BodyWhite 4), (New-SwirlPath ($tb.Right + 42) ($markY - 6) 20 1.8))
$sparkle = New-Object System.Drawing.SolidBrush($HaloGold)
foreach ($s in @(@(($tb.Right + 40), ($tb.Top + 4), 12), @(($tb.Left + 20), ($tb.Top - 6), 9))) {
    $sx = $s[0]; $sy = $s[1]; $sr = $s[2]
    $star = [System.Drawing.PointF[]]@(
        (New-Object System.Drawing.PointF($sx, ($sy - $sr))),
        (New-Object System.Drawing.PointF(($sx + $sr * 0.3), ($sy - $sr * 0.3))),
        (New-Object System.Drawing.PointF(($sx + $sr), $sy)),
        (New-Object System.Drawing.PointF(($sx + $sr * 0.3), ($sy + $sr * 0.3))),
        (New-Object System.Drawing.PointF($sx, ($sy + $sr))),
        (New-Object System.Drawing.PointF(($sx - $sr * 0.3), ($sy + $sr * 0.3))),
        (New-Object System.Drawing.PointF(($sx - $sr), $sy)),
        (New-Object System.Drawing.PointF(($sx - $sr * 0.3), ($sy - $sr * 0.3))))
    $g.FillPolygon($sparkle, $star)
}

New-Item -ItemType Directory -Force (Split-Path $OutPath) | Out-Null
$bitmap.Save($OutPath, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose()
$bitmap.Dispose()
Write-Output "Saved $OutPath"
