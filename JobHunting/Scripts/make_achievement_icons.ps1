# Placeholder achievement icons, one per kind (Achievements_Plan.md, step 5, 2026-11-21): 256 x 256 PNGs in
# SourceArt/UI/Achievements, imported by setup_achievement_list.py. A round badge in the kind's colour, a gold rim and
# a white sign:
#   T_AchIcon_Progress  進行  blue,   an arrow up
#   T_AchIcon_Collect   収集  amber,  a star
#   T_AchIcon_Fail      失敗  red,    an arrow down
#   T_AchIcon_Skill     腕前  green,  a crown
#   T_AchIcon_Hidden    隠し  purple, a keyhole
#   T_AchIcon_Unknown   a hidden one not yet taken: grey, "?"
# An achievement's own picture replaces its kind's: save it as SourceArt/UI/Achievements/T_AchIcon_<ID>.png (for
# example T_AchIcon_ACH_DANGER.png) and run setup_achievement_list.py again.
# Run: powershell -File make_achievement_icons.ps1
Add-Type -AssemblyName System.Drawing
$out = Join-Path (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)) 'SourceArt\UI\Achievements'
New-Item -ItemType Directory -Force $out | Out-Null
$S = 256

function Points([double[]]$xy) {
  $list = New-Object 'System.Collections.Generic.List[System.Drawing.PointF]'
  for ($i = 0; $i -lt $xy.Count; $i += 2) { $list.Add([System.Drawing.PointF]::new($xy[$i] * $S, $xy[$i + 1] * $S)) }
  return $list.ToArray()
}

function Badge($name, [int[]]$rgb, [scriptblock]$sign) {
  $bmp = New-Object System.Drawing.Bitmap $S, $S, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode = 'AntiAlias'
  $g.Clear([System.Drawing.Color]::Transparent)
  $rim = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 236, 196, 92))
  $g.FillEllipse($rim, 6, 6, $S - 12, $S - 12)
  $inner = New-Object System.Drawing.Drawing2D.LinearGradientBrush ([System.Drawing.Point]::new(0, 20)), ([System.Drawing.Point]::new(0, $S - 20)),
    ([System.Drawing.Color]::FromArgb(255, [Math]::Min(255, $rgb[0] + 60), [Math]::Min(255, $rgb[1] + 60), [Math]::Min(255, $rgb[2] + 60))),
    ([System.Drawing.Color]::FromArgb(255, $rgb[0], $rgb[1], $rgb[2]))
  $g.FillEllipse($inner, 20, 20, $S - 40, $S - 40)
  $white = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::White)
  & $sign $g $white
  $g.Dispose()
  $bmp.Save((Join-Path $out "$name.png"), [System.Drawing.Imaging.ImageFormat]::Png)
  $bmp.Dispose()
  "$name.png"
}

Badge 'T_AchIcon_Progress' @(40, 90, 200) { param($g, $w) $g.FillPolygon($w, (Points @(0.5,0.24, 0.74,0.5, 0.6,0.5, 0.6,0.76, 0.4,0.76, 0.4,0.5, 0.26,0.5))) }
Badge 'T_AchIcon_Collect' @(205, 130, 20) {
  param($g, $w)
  $xy = @()
  for ($i = 0; $i -lt 10; $i++) {
    $r = if ($i % 2) { 0.11 } else { 0.27 }
    $a = -[Math]::PI / 2 + $i * [Math]::PI / 5
    $xy += 0.5 + $r * [Math]::Cos($a); $xy += 0.52 + $r * [Math]::Sin($a)
  }
  $g.FillPolygon($w, (Points $xy))
}
Badge 'T_AchIcon_Fail' @(190, 45, 45) { param($g, $w) $g.FillPolygon($w, (Points @(0.5,0.76, 0.74,0.5, 0.6,0.5, 0.6,0.24, 0.4,0.24, 0.4,0.5, 0.26,0.5))) }
Badge 'T_AchIcon_Skill' @(40, 150, 70) { param($g, $w) $g.FillPolygon($w, (Points @(0.27,0.68, 0.27,0.34, 0.39,0.48, 0.5,0.3, 0.61,0.48, 0.73,0.34, 0.73,0.68))) }
Badge 'T_AchIcon_Hidden' @(120, 60, 170) {
  param($g, $w)
  $g.FillEllipse($w, 0.4 * $S, 0.27 * $S, 0.2 * $S, 0.2 * $S)
  $g.FillPolygon($w, (Points @(0.46,0.42, 0.54,0.42, 0.6,0.74, 0.4,0.74)))
}
Badge 'T_AchIcon_Unknown' @(80, 80, 90) {
  param($g, $w)
  $font = New-Object System.Drawing.Font 'Arial', ([single](0.42 * $S)), ([System.Drawing.FontStyle]::Bold), ([System.Drawing.GraphicsUnit]::Pixel)
  $format = New-Object System.Drawing.StringFormat
  $format.Alignment = 'Center'; $format.LineAlignment = 'Center'
  $g.DrawString('?', $font, $w, [System.Drawing.RectangleF]::new(0, 0.02 * $S, $S, $S), $format)
}
