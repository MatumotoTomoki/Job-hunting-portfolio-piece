# Draws the pause-menu row labels and the selection arrow in the same style as T_PauseTitle.png
# (white body, green scarf outline). Images are 2x the widget size so they stay crisp.
Add-Type -AssemblyName System.Drawing

$FontName = "HGMaruGothicMPRO"
$ArtDir = Join-Path $PSScriptRoot "Art"
# Widget sizes in the pause menu: labels 300x80, arrow 100x80.
$Scale = 2
$LabelWidth = 300 * $Scale
$LabelHeight = 80 * $Scale
$ArrowWidth = 100 * $Scale
$ArrowHeight = 80 * $Scale
# The value text ("10") sits on the right of the volume rows, so labels stay left-aligned.
$Labels = @(
    @{ Name = "T_Label_Volume"; Text = "音量" },
    @{ Name = "T_Label_SE"; Text = "SE" },
    @{ Name = "T_Label_Quit"; Text = "ゲームをやめる" }
)

$ScarfGreen = [System.Drawing.Color]::FromArgb(255, 38, 102, 52)
$DarkGreen = [System.Drawing.Color]::FromArgb(255, 20, 60, 30)
$BodyWhite = [System.Drawing.Color]::FromArgb(255, 255, 255, 255)
$SoftBlue = [System.Drawing.Color]::FromArgb(255, 222, 236, 250)
$HaloGold = [System.Drawing.Color]::FromArgb(255, 255, 214, 110)
$ShadowColor = [System.Drawing.Color]::FromArgb(110, 0, 0, 0)

# Outline widths at 2x; thinner than the title because the labels are smaller.
$OuterLine = 18
$InnerLine = 12
$RimLine = 5
$Margin = $OuterLine / 2 + 4

function New-RoundPen($color, $width) {
    $pen = New-Object System.Drawing.Pen($color, $width)
    $pen.LineJoin = [System.Drawing.Drawing2D.LineJoin]::Round
    $pen.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
    $pen.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
    return $pen
}

function New-Canvas($width, $height) {
    $bitmap = New-Object System.Drawing.Bitmap($width, $height, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $g = [System.Drawing.Graphics]::FromImage($bitmap)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.Clear([System.Drawing.Color]::Transparent)
    return @($bitmap, $g)
}

function New-TextPath($text) {
    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    $family = New-Object System.Drawing.FontFamily($FontName)
    $path.AddString($text, $family, [int][System.Drawing.FontStyle]::Bold, 100, (New-Object System.Drawing.PointF(0, 0)), [System.Drawing.StringFormat]::GenericTypographic)
    return $path
}

# Same layering as the title: shadow, dark and scarf-green outlines, white rim, white-to-blue body.
function Draw-Styled($g, $path) {
    $bounds = $path.GetBounds()
    $shadow = $path.Clone()
    $shift = New-Object System.Drawing.Drawing2D.Matrix
    $shift.Translate(0, 5)
    $shadow.Transform($shift)
    $g.DrawPath((New-RoundPen $ShadowColor $OuterLine), $shadow)
    $g.DrawPath((New-RoundPen $DarkGreen $OuterLine), $path)
    $g.DrawPath((New-RoundPen $ScarfGreen $InnerLine), $path)
    $g.DrawPath((New-RoundPen $BodyWhite $RimLine), $path)
    $fill = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
        (New-Object System.Drawing.PointF(0, ($bounds.Top - 1))),
        (New-Object System.Drawing.PointF(0, ($bounds.Bottom + 1))),
        $BodyWhite, $SoftBlue)
    $g.FillPath($fill, $path)
}

function Save-Canvas($bitmap, $g, $name) {
    $out = Join-Path $ArtDir ($name + ".png")
    $bitmap.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose()
    $bitmap.Dispose()
    Write-Output "Saved $out"
}

New-Item -ItemType Directory -Force $ArtDir | Out-Null

# Every label shares the letter height of "音量", sized to nearly fill the row height.
# A label too long for the 300 width gets a wider image instead of smaller letters.
$reference = (New-TextPath "音量").GetBounds()
$textScale = ($LabelHeight - 2 * $Margin - 6) / $reference.Height
$referenceHeight = $reference.Height * $textScale

foreach ($label in $Labels) {
    $path = New-TextPath $label.Text
    $textWidth = $path.GetBounds().Width * $textScale + 2 * $Margin
    $width = [int]([Math]::Ceiling([Math]::Max($LabelWidth, $textWidth) / (2 * $Scale)) * 2 * $Scale)
    $canvas = New-Canvas $width $LabelHeight
    Write-Output ("{0}: widget size {1} x {2}" -f $label.Name, ($width / $Scale), ($LabelHeight / $Scale))
    $b = $path.GetBounds()
    $matrix = New-Object System.Drawing.Drawing2D.Matrix
    $matrix.Translate($Margin, (($LabelHeight - $referenceHeight) / 2))
    $matrix.Scale($textScale, $textScale)
    $matrix.Translate(-$b.X, -(New-TextPath "音量").GetBounds().Y)
    $path.Transform($matrix)
    Draw-Styled $canvas[1] $path
    Save-Canvas $canvas[0] $canvas[1] $label.Name
}

# Chunky rounded arrow pointing right, with a small halo-gold sparkle.
$canvas = New-Canvas $ArrowWidth $ArrowHeight
$cx = $ArrowWidth / 2
$cy = $ArrowHeight / 2
$arrow = New-Object System.Drawing.Drawing2D.GraphicsPath
$arrow.AddPolygon([System.Drawing.PointF[]]@(
    (New-Object System.Drawing.PointF(($cx - 62), ($cy - 18))),
    (New-Object System.Drawing.PointF(($cx + 4), ($cy - 18))),
    (New-Object System.Drawing.PointF(($cx + 4), ($cy - 46))),
    (New-Object System.Drawing.PointF(($cx + 66), $cy)),
    (New-Object System.Drawing.PointF(($cx + 4), ($cy + 46))),
    (New-Object System.Drawing.PointF(($cx + 4), ($cy + 18))),
    (New-Object System.Drawing.PointF(($cx - 62), ($cy + 18)))))
Draw-Styled $canvas[1] $arrow
$sparkle = New-Object System.Drawing.SolidBrush($HaloGold)
$sx = $cx - 58; $sy = $cy - 46; $sr = 14
$canvas[1].FillPolygon($sparkle, [System.Drawing.PointF[]]@(
    (New-Object System.Drawing.PointF($sx, ($sy - $sr))),
    (New-Object System.Drawing.PointF(($sx + $sr * 0.3), ($sy - $sr * 0.3))),
    (New-Object System.Drawing.PointF(($sx + $sr), $sy)),
    (New-Object System.Drawing.PointF(($sx + $sr * 0.3), ($sy + $sr * 0.3))),
    (New-Object System.Drawing.PointF($sx, ($sy + $sr))),
    (New-Object System.Drawing.PointF(($sx - $sr * 0.3), ($sy + $sr * 0.3))),
    (New-Object System.Drawing.PointF(($sx - $sr), $sy)),
    (New-Object System.Drawing.PointF(($sx - $sr * 0.3), ($sy - $sr * 0.3)))))
Save-Canvas $canvas[0] $canvas[1] "T_Arrow"
