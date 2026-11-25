# Each achievement's own icon (the user, 2026-11-25: "an icon that pictures each one"): the kinds' badge from
# make_achievement_icons.ps1 (the kind's colour, the gold rim) with a white picture of that achievement, saved as
# SourceArt/UI/Achievements/T_AchIcon_<ID>.png; setup_achievement_list.py then uses them instead of the kind's sign.
# Pictures are glyphs of Segoe UI Symbol (drawn as white shapes) and simple drawn shapes; overlays: a gold number disc,
# a crack (the hidden stages' "collapsed" things), a ban sign.
# Run: powershell -File make_achievement_own_icons.ps1 [-Preview <png>]   (-Preview also writes a contact sheet)
param([string]$Preview = '')
Add-Type -AssemblyName System.Drawing
$out = Join-Path (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)) 'SourceArt\UI\Achievements'
New-Item -ItemType Directory -Force $out | Out-Null
$S = 256
$COLOURS = @{ Progress = @(40, 90, 200); Collect = @(205, 130, 20); Fail = @(190, 45, 45); Skill = @(40, 150, 70); Hidden = @(120, 60, 170) }
$SYMBOL = 'Segoe UI Symbol'
$GOLD = [System.Drawing.Color]::FromArgb(255, 236, 196, 92)

function P([double]$v) { [single]($v * $S) }
function Points([double[]]$xy) {
  $list = New-Object 'System.Collections.Generic.List[System.Drawing.PointF]'
  for ($i = 0; $i -lt $xy.Count; $i += 2) { $list.Add([System.Drawing.PointF]::new((P $xy[$i]), (P $xy[$i + 1]))) }
  return $list.ToArray()
}
# A glyph as a filled shape, its box centred on (cx, cy) and `size` (fraction of the badge) tall; turned by `angle`.
function Glyph($g, [string]$text, [double]$size, [double]$cx, [double]$cy, $brush, [double]$angle = 0, [string]$font = $SYMBOL) {
  $path = New-Object System.Drawing.Drawing2D.GraphicsPath
  $family = New-Object System.Drawing.FontFamily $font
  $path.AddString($text, $family, 0, [single]100, [System.Drawing.PointF]::new(0, 0), [System.Drawing.StringFormat]::GenericTypographic)
  $b = $path.GetBounds()
  $k = (P $size) / [Math]::Max($b.Width, $b.Height)
  $m = New-Object System.Drawing.Drawing2D.Matrix
  $m.Translate((P $cx), (P $cy))
  if ($angle) { $m.Rotate([single]$angle) }
  $m.Scale([single]$k, [single]$k)
  $m.Translate([single](-$b.X - $b.Width / 2), [single](-$b.Y - $b.Height / 2))
  $path.Transform($m)
  $g.FillPath($brush, $path)
}
function Star($g, $brush, [double]$cx, [double]$cy, [double]$r) {
  $xy = @()
  for ($i = 0; $i -lt 10; $i++) {
    $rr = if ($i % 2) { $r * 0.42 } else { $r }
    $a = -[Math]::PI / 2 + $i * [Math]::PI / 5
    $xy += $cx + $rr * [Math]::Cos($a); $xy += $cy + $rr * [Math]::Sin($a)
  }
  $g.FillPolygon($brush, (Points $xy))
}
function Number($g, [string]$n) {
  $g.FillEllipse((New-Object System.Drawing.SolidBrush $GOLD), (P 0.6), (P 0.6), (P 0.26), (P 0.26))
  Glyph $g $n 0.15 0.73 0.73 (New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 70, 40, 10))) 0 'Arial Black'
}
function Crack($g, [int[]]$rgb) {
  $pen = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(255, [int]($rgb[0] * 0.55), [int]($rgb[1] * 0.55), [int]($rgb[2] * 0.55))), (P 0.035)
  $pen.LineJoin = 'Round'
  $g.DrawLines($pen, (Points @(0.36,0.24, 0.5,0.4, 0.43,0.5, 0.58,0.62, 0.52,0.78)))
}
function Ban($g) {
  $pen = New-Object System.Drawing.Pen ([System.Drawing.Color]::White), (P 0.045)
  $g.DrawEllipse($pen, (P 0.24), (P 0.24), (P 0.52), (P 0.52))
  $g.DrawLine($pen, (P 0.32), (P 0.32), (P 0.68), (P 0.68))
}
function Thick($width) { $p = New-Object System.Drawing.Pen ([System.Drawing.Color]::White), (P $width); $p.StartCap = 'Round'; $p.EndCap = 'Round'; $p.LineJoin = 'Round'; return $p }

$made = @()
function Icon($id, $kind, [scriptblock]$draw) {
  $rgb = $COLOURS[$kind]
  $bmp = New-Object System.Drawing.Bitmap $S, $S, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode = 'AntiAlias'
  $g.Clear([System.Drawing.Color]::Transparent)
  $g.FillEllipse((New-Object System.Drawing.SolidBrush $GOLD), 6, 6, $S - 12, $S - 12)
  $inner = New-Object System.Drawing.Drawing2D.LinearGradientBrush ([System.Drawing.Point]::new(0, 20)), ([System.Drawing.Point]::new(0, $S - 20)),
    ([System.Drawing.Color]::FromArgb(255, [Math]::Min(255, $rgb[0] + 60), [Math]::Min(255, $rgb[1] + 60), [Math]::Min(255, $rgb[2] + 60))),
    ([System.Drawing.Color]::FromArgb(255, $rgb[0], $rgb[1], $rgb[2]))
  $g.FillEllipse($inner, 20, 20, $S - 40, $S - 40)
  $w = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::White)
  & $draw $g $w $rgb
  $g.Dispose()
  $file = Join-Path $out "T_AchIcon_$id.png"
  $bmp.Save($file, [System.Drawing.Imaging.ImageFormat]::Png)
  $bmp.Dispose()
  $script:made += $file
}

# ----- 進行 -----
Icon 'ACH_AREA2' 'Progress' { param($g, $w, $rgb)                                                                   # a gear
  $xy = @()
  for ($i = 0; $i -lt 40; $i++) {
    $a = $i * [Math]::PI / 20
    $r = if (($i % 4) -lt 2) { 0.27 } else { 0.21 }
    $xy += 0.5 + $r * [Math]::Cos($a); $xy += 0.5 + $r * [Math]::Sin($a)
  }
  $g.FillPolygon($w, (Points $xy))
  $g.FillEllipse((New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, $rgb[0], $rgb[1], $rgb[2]))), (P 0.42), (P 0.42), (P 0.16), (P 0.16))
}
Icon 'ACH_AREA3' 'Progress' { param($g, $w)                                                                          # a cannon and its shot
  $state = $g.Save()
  $g.TranslateTransform((P 0.4), (P 0.64)); $g.RotateTransform(-40)
  $g.FillRectangle($w, (P -0.04), (P -0.08), (P 0.3), (P 0.16))
  $g.Restore($state)
  $g.FillEllipse($w, (P 0.24), (P 0.6), (P 0.2), (P 0.2))
  $g.FillRectangle($w, (P 0.2), (P 0.76), (P 0.36), (P 0.05))
  $g.FillEllipse($w, (P 0.62), (P 0.2), (P 0.14), (P 0.14))
  $pen = Thick 0.022
  foreach ($d in @(@(0.6,0.42,0.63,0.37), @(0.66,0.36,0.67,0.33))) { $g.DrawLine($pen, (P $d[0]), (P $d[1]), (P $d[2]), (P $d[3])) }
}
Icon 'ACH_AREA4' 'Progress' { param($g, $w)                                                                          # a pillar of light
  $g.FillRectangle($w, (P 0.43), (P 0.2), (P 0.14), (P 0.56))
  $pen = Thick 0.03
  foreach ($a in @(@(0.3,0.36,0.37,0.42), @(0.7,0.36,0.63,0.42), @(0.27,0.56,0.37,0.56), @(0.73,0.56,0.63,0.56))) { $g.DrawLine($pen, (P $a[0]), (P $a[1]), (P $a[2]), (P $a[3])) }
  $g.FillEllipse($w, (P 0.3), (P 0.72), (P 0.4), (P 0.08))
}
Icon 'ACH_IWATO' 'Progress' { param($g, $w, $rgb)                                                                    # the rock rolled aside, the sun out
  Glyph $g ([string][char]0x2600) 0.44 0.58 0.46 $w
  $g.FillPolygon((New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 200, 200, 210))), (Points @(0.22,0.78, 0.24,0.4, 0.34,0.3, 0.44,0.38, 0.46,0.78)))
}
Icon 'ACH_WINGS' 'Progress' { param($g, $w)                                                                          # a pair of wings
  foreach ($side in -1, 1) {
    for ($i = 0; $i -lt 3; $i++) {
      $state = $g.Save()
      $g.TranslateTransform((P (0.5 + $side * 0.04)), (P 0.46))
      $g.RotateTransform([single]($side * (-20 + 22 * $i)))
      $len = 0.3 - 0.05 * $i
      $x = if ($side -gt 0) { 0 } else { -$len }
      $g.FillEllipse($w, (P $x), (P -0.05), (P $len), (P 0.11))
      $g.Restore($state)
    }
  }
}
Icon 'ACH_CLEAR' 'Progress' { param($g, $w) Glyph $g ([string][char]0x26E9) 0.48 0.5 0.5 $w }                     # the gate
# ----- 収集 -----
foreach ($n in 1..4) { Icon "ACH_COIN_A$n" 'Collect' ([scriptblock]::Create("param(`$g, `$w) Star `$g `$w 0.47 0.48 0.27; Number `$g '$n'")) }
Icon 'ACH_COIN_ALL' 'Collect' { param($g, $w) Star $g $w 0.5 0.36 0.17; Star $g $w 0.32 0.62 0.15; Star $g $w 0.68 0.62 0.15 }
Icon 'ACH_ITEM_ALL' 'Collect' { param($g, $w) Glyph $g ([char]::ConvertFromUtf32(0x1F45F)) 0.5 0.5 0.52 $w }       # a shoe
Icon 'ACH_SHARDS' 'Collect' { param($g, $w)                                                                          # three shards of light
  $g.FillPolygon($w, (Points @(0.5,0.22, 0.58,0.42, 0.5,0.6, 0.42,0.42)))
  $g.FillPolygon($w, (Points @(0.3,0.46, 0.38,0.6, 0.3,0.76, 0.22,0.6)))
  $g.FillPolygon($w, (Points @(0.7,0.46, 0.78,0.6, 0.7,0.76, 0.62,0.6)))
}
Icon 'ACH_FLAGS' 'Collect' { param($g, $w) Glyph $g ([string][char]0x2691) 0.36 0.42 0.44 $w; Glyph $g ([string][char]0x2691) 0.36 0.6 0.6 $w }
# ----- 失敗 -----
Icon 'ACH_FIRST_FALL' 'Fail' { param($g, $w)                                                                         # falling, speed lines above
  $g.FillEllipse($w, (P 0.36), (P 0.46), (P 0.28), (P 0.28))
  $pen = Thick 0.03
  foreach ($x in 0.4, 0.5, 0.6) { $g.DrawLine($pen, (P $x), (P 0.22), (P $x), (P 0.38)) }
}
Icon 'ACH_HELL' 'Fail' { param($g, $w) Glyph $g ([char]::ConvertFromUtf32(0x1F525)) 0.52 0.5 0.5 $w }              # fire
Icon 'ACH_HELL_BACK' 'Fail' { param($g, $w)
  Glyph $g ([char]::ConvertFromUtf32(0x1F525)) 0.34 0.42 0.6 $w
  $g.FillPolygon($w, (Points @(0.66,0.22, 0.8,0.4, 0.71,0.4, 0.71,0.6, 0.61,0.6, 0.61,0.4, 0.52,0.4)))
}
Icon 'ACH_WRONG_CAGE' 'Fail' { param($g, $w)                                                                         # a birdcage, crossed
  $pen = Thick 0.028
  $g.DrawArc($pen, (P 0.3), (P 0.22), (P 0.4), (P 0.36), 180, 180)
  foreach ($x in 0.3, 0.4, 0.5, 0.6, 0.7) { $g.DrawLine($pen, (P $x), (P 0.4), (P $x), (P 0.74)) }
  $g.DrawLine($pen, (P 0.26), (P 0.76), (P 0.74), (P 0.76))
  $x = Thick 0.05
  $g.DrawLine($x, (P 0.58), (P 0.56), (P 0.78), (P 0.76)); $g.DrawLine($x, (P 0.78), (P 0.56), (P 0.58), (P 0.76))
}
Icon 'ACH_SUN_GRAB' 'Fail' { param($g, $w, $rgb)                                                                     # the sun behind bars
  Glyph $g ([string][char]0x2600) 0.5 0.5 0.5 $w
  $pen = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(255, 120, 20, 20)), (P 0.035)
  foreach ($x in 0.38, 0.5, 0.62) { $g.DrawLine($pen, (P $x), (P 0.28), (P $x), (P 0.72)) }
}
Icon 'ACH_THREAD' 'Fail' { param($g, $w)                                                                             # a snapped thread, the spider falling
  $pen = Thick 0.025
  $g.DrawLine($pen, (P 0.5), (P 0.18), (P 0.5), (P 0.32)); $g.DrawLine($pen, (P 0.5), (P 0.4), (P 0.5), (P 0.48))
  Glyph $g ([char]::ConvertFromUtf32(0x1F577)) 0.3 0.5 0.64 $w
}
Icon 'ACH_SO_CLOSE' 'Fail' { param($g, $w)                                                                           # the goal flag just out of reach
  Glyph $g ([char]::ConvertFromUtf32(0x1F3C1)) 0.32 0.62 0.38 $w
  $g.FillRectangle($w, (P 0.5), (P 0.56), (P 0.3), (P 0.06))
  $g.FillEllipse($w, (P 0.28), (P 0.62), (P 0.14), (P 0.14))
  $pen = Thick 0.022
  $g.DrawLine($pen, (P 0.31), (P 0.46), (P 0.31), (P 0.56)); $g.DrawLine($pen, (P 0.39), (P 0.46), (P 0.39), (P 0.56))
}
# ----- 腕前 -----
Icon 'ACH_NO_FALL' 'Skill' { param($g, $w) Glyph $g ([string][char]0x2714) 0.44 0.5 0.5 $w }
Icon 'ACH_TIME' 'Skill' { param($g, $w)                                                                              # a stopwatch
  $pen = Thick 0.04
  $g.DrawEllipse($pen, (P 0.29), (P 0.31), (P 0.42), (P 0.42))
  $g.FillRectangle($w, (P 0.46), (P 0.2), (P 0.08), (P 0.08))
  $g.DrawLine($pen, (P 0.5), (P 0.52), (P 0.5), (P 0.38)); $g.DrawLine($pen, (P 0.5), (P 0.52), (P 0.6), (P 0.58))
}
Icon 'ACH_NO_FLAG' 'Skill' { param($g, $w) Glyph $g ([string][char]0x2691) 0.3 0.5 0.5 $w; Ban $g }
Icon 'ACH_PURIST' 'Skill' { param($g, $w)
  Glyph $g ([char]::ConvertFromUtf32(0x1F45F)) 0.22 0.42 0.44 $w
  Glyph $g ([string][char]0x2691) 0.2 0.58 0.58 $w
  Ban $g
}
Icon 'ACH_SUN_DODGE' 'Skill' { param($g, $w)                                                                         # the sun, and a swerve past it
  Glyph $g ([string][char]0x2600) 0.3 0.4 0.4 $w
  $g.DrawArc((Thick 0.035), (P 0.34), (P 0.36), (P 0.4), (P 0.4), 100, -150)
  $g.FillPolygon($w, (Points @(0.66,0.46, 0.78,0.5, 0.68,0.6)))
}
Icon 'ACH_MELODY' 'Skill' { param($g, $w) Glyph $g ([string][char]0x266B) 0.46 0.5 0.5 $w }
# ----- 隠し -----
Icon 'ACH_BREAK_FLAG' 'Hidden' { param($g, $w)                                                                       # a flag snapped over
  $pen = Thick 0.035
  $g.DrawLine($pen, (P 0.38), (P 0.78), (P 0.38), (P 0.52))
  Glyph $g ([string][char]0x2691) 0.3 0.56 0.5 $w 70
}
Icon 'ACH_LEDGE' 'Hidden' { param($g, $w)                                                                            # hanging on by a hand
  $g.FillRectangle($w, (P 0.2), (P 0.26), (P 0.46), (P 0.14))
  $g.FillPolygon((New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 90, 40, 130))), (Points @(0.2,0.4, 0.66,0.4, 0.66,0.44, 0.2,0.44)))
  Glyph $g ([string][char]0x270B) 0.32 0.6 0.54 $w
}
Icon 'ACH_REWIND' 'Hidden' { param($g, $w) $g.FillPolygon($w, (Points @(0.5,0.32, 0.5,0.68, 0.26,0.5))); $g.FillPolygon($w, (Points @(0.74,0.32, 0.74,0.68, 0.5,0.5))) }
Icon 'ACH_DANGER' 'Hidden' { param($g, $w)                                                                           # the button
  $g.FillPie($w, (P 0.32), (P 0.36), (P 0.36), (P 0.3), 180, 180)
  $g.FillRectangle($w, (P 0.24), (P 0.54), (P 0.52), (P 0.12))
  Glyph $g '!' 0.18 0.5 0.28 $w 0 'Arial Black'
}
Icon 'ACH_SECRET_CLEAR' 'Hidden' { param($g, $w, $rgb) Glyph $g ([string][char]0x26E9) 0.48 0.5 0.5 $w; Crack $g $rgb }
foreach ($n in 1..4) {
  Icon "ACH_COIN_S$n" 'Hidden' ([scriptblock]::Create("param(`$g, `$w, `$rgb) Star `$g `$w 0.47 0.48 0.27; Crack `$g `$rgb; Number `$g '$n'"))
  Icon "ACH_ENTER_S$n" 'Hidden' ([scriptblock]::Create("param(`$g, `$w) Glyph `$g ([char]::ConvertFromUtf32(0x1F6AA)) 0.48 0.46 0.48 `$w; Number `$g '$n'"))
}
Icon 'ACH_COIN_SECRET_ALL' 'Hidden' { param($g, $w, $rgb) Star $g $w 0.5 0.36 0.17; Star $g $w 0.32 0.62 0.15; Star $g $w 0.68 0.62 0.15; Crack $g $rgb }

"{0} icons in {1}" -f $made.Count, $out
if ($Preview) {
  $cols = 8; $cell = 128
  $sheet = New-Object System.Drawing.Bitmap ($cols * $cell), ([Math]::Ceiling($made.Count / $cols) * ($cell + 18))
  $sg = [System.Drawing.Graphics]::FromImage($sheet)
  $sg.Clear([System.Drawing.Color]::FromArgb(255, 40, 40, 48))
  $font = New-Object System.Drawing.Font 'Arial', 8
  for ($i = 0; $i -lt $made.Count; $i++) {
    $img = [System.Drawing.Image]::FromFile($made[$i])
    $x = ($i % $cols) * $cell; $y = [Math]::Floor($i / $cols) * ($cell + 18)
    $sg.DrawImage($img, $x + 4, $y, $cell - 8, $cell - 8)
    $sg.DrawString(([IO.Path]::GetFileNameWithoutExtension($made[$i]) -replace 'T_AchIcon_ACH_', ''), $font, [System.Drawing.Brushes]::White, $x + 4, $y + $cell - 6)
    $img.Dispose()
  }
  $sheet.Save($Preview, [System.Drawing.Imaging.ImageFormat]::Png)
}
