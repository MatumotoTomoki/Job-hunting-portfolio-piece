# Writes SourceArt/Sounds/S_Chime.wav: a glassy bell at A5 (880 Hz), 2 s, mono 16-bit 44.1 kHz. Bell-like partials
# (1, 2, 3.01, 4.17, 5.43 x the base), each dying away on its own, a 3 ms attack. BP_ChimeJewel plays it at other
# pitches with PitchMultiplier. Run: powershell -File make_chime_sound.ps1
$root = Split-Path -Parent $PSScriptRoot
$outDir = Join-Path $root 'SourceArt\Sounds'
New-Item -ItemType Directory -Force $outDir | Out-Null
$out = Join-Path $outDir 'S_Chime.wav'

$rate = 44100
$seconds = 2.0
$count = [int]($rate * $seconds)
$base = 880.0
$partials = @(
  @{ Ratio = 1.0;  Amp = 1.0;  Decay = 1.10 },
  @{ Ratio = 2.0;  Amp = 0.45; Decay = 0.70 },
  @{ Ratio = 3.01; Amp = 0.28; Decay = 0.45 },
  @{ Ratio = 4.17; Amp = 0.14; Decay = 0.30 },
  @{ Ratio = 5.43; Amp = 0.08; Decay = 0.22 }
)
$samples = New-Object double[] $count
$peak = 0.0
for ($i = 0; $i -lt $count; $i++) {
  $t = $i / $rate
  $v = 0.0
  foreach ($p in $partials) {
    $v += $p.Amp * [Math]::Exp(-$t / $p.Decay) * [Math]::Sin(2.0 * [Math]::PI * $base * $p.Ratio * $t)
  }
  $v *= [Math]::Min(1.0, $t / 0.003)
  $samples[$i] = $v
  if ([Math]::Abs($v) -gt $peak) { $peak = [Math]::Abs($v) }
}
$scale = 0.8 * 32767.0 / $peak

$stream = [IO.File]::Create($out)
$w = New-Object IO.BinaryWriter $stream
$dataBytes = $count * 2
$w.Write([Text.Encoding]::ASCII.GetBytes('RIFF')); $w.Write([int](36 + $dataBytes)); $w.Write([Text.Encoding]::ASCII.GetBytes('WAVE'))
$w.Write([Text.Encoding]::ASCII.GetBytes('fmt ')); $w.Write([int]16); $w.Write([int16]1); $w.Write([int16]1)
$w.Write([int]$rate); $w.Write([int]($rate * 2)); $w.Write([int16]2); $w.Write([int16]16)
$w.Write([Text.Encoding]::ASCII.GetBytes('data')); $w.Write([int]$dataBytes)
for ($i = 0; $i -lt $count; $i++) { $w.Write([int16][Math]::Round($samples[$i] * $scale)) }
$w.Close()
"wrote $out ($count samples)"
