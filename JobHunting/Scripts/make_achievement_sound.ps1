# Writes SourceArt/Sounds/S_AchievementGet.wav: the achievement notice's "kirin!", two bell notes rising a fifth
# (E6 then B6, 0.11 s apart), each with bell-like partials dying away, 1.6 s, mono 16-bit 44.1 kHz.
# Run: powershell -File make_achievement_sound.ps1   (then setup_achievement_notice.py imports it)
$root = Split-Path -Parent $PSScriptRoot
$outDir = Join-Path $root 'SourceArt\Sounds'
New-Item -ItemType Directory -Force $outDir | Out-Null
$out = Join-Path $outDir 'S_AchievementGet.wav'

$rate = 44100
$seconds = 1.6
$count = [int]($rate * $seconds)
$notes = @(
  @{ Freq = 1318.5; Start = 0.0;  Amp = 0.8 },
  @{ Freq = 1975.5; Start = 0.11; Amp = 1.0 }
)
$partials = @(
  @{ Ratio = 1.0;  Amp = 1.0;  Decay = 0.55 },
  @{ Ratio = 2.0;  Amp = 0.35; Decay = 0.30 },
  @{ Ratio = 3.01; Amp = 0.18; Decay = 0.18 },
  @{ Ratio = 4.17; Amp = 0.08; Decay = 0.12 }
)
$samples = New-Object double[] $count
$peak = 0.0
for ($i = 0; $i -lt $count; $i++) {
  $v = 0.0
  foreach ($n in $notes) {
    $t = $i / $rate - $n.Start
    if ($t -lt 0) { continue }
    $s = 0.0
    foreach ($p in $partials) {
      $s += $p.Amp * [Math]::Exp(-$t / $p.Decay) * [Math]::Sin(2.0 * [Math]::PI * $n.Freq * $p.Ratio * $t)
    }
    $v += $n.Amp * $s * [Math]::Min(1.0, $t / 0.002)
  }
  $samples[$i] = $v
  if ([Math]::Abs($v) -gt $peak) { $peak = [Math]::Abs($v) }
}
$scale = 0.7 * 32767.0 / $peak

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
