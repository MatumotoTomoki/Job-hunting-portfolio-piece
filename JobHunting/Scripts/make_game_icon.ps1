# Builds the game icon Build/Windows/Application.ico from Art/GameIcon_Source.png (transparent background).
# Crops to the character, centers it on a transparent square and writes the sizes Windows asks for.
param([string]$PreviewDir)
Add-Type -AssemblyName System.Drawing

$sourcePath = Join-Path $PSScriptRoot 'Art\GameIcon_Source.png'
$iconPath = Join-Path $PSScriptRoot '..\Build\Windows\Application.ico'
$sizes = 256, 128, 64, 48, 32, 24, 16
$alphaThreshold = 10
# Share of the square left empty around the character, on each side.
$margin = 0.03

function Get-AlphaBounds($bitmap) {
  $left = $bitmap.Width; $top = $bitmap.Height; $right = -1; $bottom = -1
  for ($y = 0; $y -lt $bitmap.Height; $y++) {
    for ($x = 0; $x -lt $bitmap.Width; $x++) {
      if ($bitmap.GetPixel($x, $y).A -gt $alphaThreshold) {
        if ($x -lt $left) { $left = $x }
        if ($x -gt $right) { $right = $x }
        if ($y -lt $top) { $top = $y }
        if ($y -gt $bottom) { $bottom = $y }
      }
    }
  }
  if ($right -lt 0) { throw 'The source image is fully transparent' }
  return [Drawing.Rectangle]::FromLTRB($left, $top, $right + 1, $bottom + 1)
}

function New-IconFrame($source, $bounds, $size) {
  $frame = [Drawing.Bitmap]::new($size, $size, [Drawing.Imaging.PixelFormat]::Format32bppArgb)
  $canvas = [Drawing.Graphics]::FromImage($frame)
  $canvas.InterpolationMode = [Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
  $canvas.PixelOffsetMode = [Drawing.Drawing2D.PixelOffsetMode]::HighQuality
  $canvas.SmoothingMode = [Drawing.Drawing2D.SmoothingMode]::HighQuality
  $scale = ($size * (1 - 2 * $margin)) / [Math]::Max($bounds.Width, $bounds.Height)
  $width = $bounds.Width * $scale
  $height = $bounds.Height * $scale
  $target = [Drawing.RectangleF]::new(($size - $width) / 2, ($size - $height) / 2, $width, $height)
  $canvas.DrawImage($source, $target, [Drawing.RectangleF]$bounds, [Drawing.GraphicsUnit]::Pixel)
  $canvas.Dispose()
  return $frame
}

# 256 is stored as PNG; smaller frames as uncompressed DIBs, which every icon reader accepts.
function Get-FrameBytes($frame) {
  $stream = [IO.MemoryStream]::new()
  if ($frame.Width -ge 256) {
    $frame.Save($stream, [Drawing.Imaging.ImageFormat]::Png)
    return , $stream.ToArray()
  }
  $writer = [IO.BinaryWriter]::new($stream)
  $maskStride = [int][Math]::Ceiling($frame.Width / 32.0) * 4
  $writer.Write([int32]40)
  $writer.Write([int32]$frame.Width)
  # Icon DIBs count the color rows and the mask rows together.
  $writer.Write([int32]($frame.Height * 2))
  $writer.Write([int16]1)
  $writer.Write([int16]32)
  $writer.Write([int32]0)
  $writer.Write([int32]($frame.Width * $frame.Height * 4 + $maskStride * $frame.Height))
  $writer.Write([int32]0); $writer.Write([int32]0); $writer.Write([int32]0); $writer.Write([int32]0)
  for ($y = $frame.Height - 1; $y -ge 0; $y--) {
    for ($x = 0; $x -lt $frame.Width; $x++) {
      $c = $frame.GetPixel($x, $y)
      $writer.Write([byte]$c.B); $writer.Write([byte]$c.G); $writer.Write([byte]$c.R); $writer.Write([byte]$c.A)
    }
  }
  # The alpha channel decides transparency, so the mask stays all zero.
  $writer.Write([byte[]]::new($maskStride * $frame.Height))
  $writer.Flush()
  return , $stream.ToArray()
}

$source = [Drawing.Bitmap]::new($sourcePath)
$bounds = Get-AlphaBounds $source
$frames = foreach ($size in $sizes) { New-IconFrame $source $bounds $size }

$output = [IO.MemoryStream]::new()
$icon = [IO.BinaryWriter]::new($output)
$icon.Write([int16]0)
$icon.Write([int16]1)
$icon.Write([int16]$frames.Count)
$offset = 6 + 16 * $frames.Count
$payloads = foreach ($frame in $frames) { , (Get-FrameBytes $frame) }
for ($i = 0; $i -lt $frames.Count; $i++) {
  # A width or height of 0 means 256 in an icon directory.
  $sizeByte = if ($frames[$i].Width -ge 256) { 0 } else { $frames[$i].Width }
  $icon.Write([byte]$sizeByte); $icon.Write([byte]$sizeByte)
  $icon.Write([byte]0); $icon.Write([byte]0)
  $icon.Write([int16]1); $icon.Write([int16]32)
  $icon.Write([int32]$payloads[$i].Length)
  $icon.Write([int32]$offset)
  $offset += $payloads[$i].Length
}
foreach ($payload in $payloads) { $icon.Write([byte[]]$payload) }
$icon.Flush()

New-Item -ItemType Directory -Force (Split-Path $iconPath) | Out-Null
[IO.File]::WriteAllBytes([IO.Path]::GetFullPath($iconPath), $output.ToArray())

if ($PreviewDir) {
  $sheet = [Drawing.Bitmap]::new(900, 280)
  $canvas = [Drawing.Graphics]::FromImage($sheet)
  $canvas.FillRectangle([Drawing.Brushes]::White, 0, 0, 450, 280)
  $canvas.FillRectangle([Drawing.Brushes]::DimGray, 450, 0, 450, 280)
  foreach ($origin in 0, 450) {
    $x = $origin + 10
    foreach ($frame in $frames) {
      if ($frame.Width -in 256, 48, 32, 16) {
        $canvas.DrawImageUnscaled($frame, $x, 10)
        $x += $frame.Width + 10
      }
    }
  }
  $canvas.Dispose()
  $sheet.Save((Join-Path $PreviewDir 'icon_preview.png'), [Drawing.Imaging.ImageFormat]::Png)
  $sheet.Dispose()
}
foreach ($frame in $frames) { $frame.Dispose() }
"Character bounds $bounds -> $([IO.Path]::GetFullPath($iconPath)) ($($output.Length) bytes)"
$source.Dispose()
