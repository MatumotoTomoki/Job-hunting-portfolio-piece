# Heaven's Gate's sounds (BP_HeavenGate, area 4's ending; 2026-11-22):
#   SourceArt/Sounds/Stock/  free SE from 効果音ラボ (soundeffect-lab.info: game use and editing OK, no credit; the
#                            files themselves must not be handed out), kept as downloaded:
#     SEL_stone-wall-slide1.mp3   "石の壁がスライドする遺跡の仕掛け" 1.7 s
#     SEL_magic-quake1.mp3        "地震魔法1地響き" 4.0 s
#   S_GateOpen.wav   the doors (~4.3 s): the stone slide at 0.6x speed (2.9 s, lower and heavier: a huge door), a
#                    second copy at 0.45x under it, and the rumble beneath; fades out as the doors come to rest
#   S_GateLight.wav  the light pouring out (synthesized, ~8 s): a choir-like chord swelling up, glints over it
# setup_gate_sounds.py imports them. Run:
#   powershell -File make_gate_sounds.ps1 [-From <folder with the downloaded mp3s>]
param([string]$From = '',
      [string]$Blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe')
$ErrorActionPreference = 'Stop'
$sounds = Join-Path (Split-Path -Parent $PSScriptRoot) 'SourceArt\Sounds'
$stock = Join-Path $sounds 'Stock'
New-Item -ItemType Directory -Force $stock | Out-Null
$names = 'stone-wall-slide1', 'magic-quake1'
foreach ($n in $names) {
  if ($From -and (Test-Path (Join-Path $From "$n.mp3"))) { Copy-Item (Join-Path $From "$n.mp3") (Join-Path $stock "SEL_$n.mp3") -Force }
  if (-not (Test-Path (Join-Path $stock "SEL_$n.mp3"))) { throw "SEL_$n.mp3 is not in $stock (pass -From)" }
}
$wav = @{}
foreach ($n in $names) {
  $wav[$n] = Join-Path $env:TEMP "gate_$n.wav"
  & $Blender -b --factory-startup --python (Join-Path $PSScriptRoot 'decode_audio_blender.py') -- (Join-Path $stock "SEL_$n.mp3") $wav[$n] | Select-String 'decoded'
}

Add-Type -TypeDefinition @'
using System;
using System.IO;

public static class GateSound {
    const int Rate = 44100;

    public static double[] Read(string path) {
        byte[] b = File.ReadAllBytes(path);
        int i = 12, ch = 1;
        while (i < b.Length - 8) {
            string id = System.Text.Encoding.ASCII.GetString(b, i, 4);
            int len = BitConverter.ToInt32(b, i + 4);
            if (id == "fmt ") ch = BitConverter.ToInt16(b, i + 10);
            if (id == "data") {
                int n = len / 2 / ch;
                var s = new double[n];
                for (int k = 0; k < n; k++) {
                    double v = 0.0;
                    for (int c = 0; c < ch; c++) v += BitConverter.ToInt16(b, i + 8 + 2 * (k * ch + c)) / 32768.0;
                    s[k] = v / ch;
                }
                return s;
            }
            i += 8 + len + (len % 2);
        }
        throw new Exception("no data chunk in " + path);
    }

    public static void Write(string path, double[] s, double peakTo) {
        double peak = 1e-9;
        foreach (double v in s) peak = Math.Max(peak, Math.Abs(v));
        double scale = peakTo * 32767.0 / peak;
        using (var w = new BinaryWriter(File.Create(path))) {
            int bytes = s.Length * 2;
            w.Write(System.Text.Encoding.ASCII.GetBytes("RIFF")); w.Write(36 + bytes); w.Write(System.Text.Encoding.ASCII.GetBytes("WAVE"));
            w.Write(System.Text.Encoding.ASCII.GetBytes("fmt ")); w.Write(16); w.Write((short)1); w.Write((short)1);
            w.Write(Rate); w.Write(Rate * 2); w.Write((short)2); w.Write((short)16);
            w.Write(System.Text.Encoding.ASCII.GetBytes("data")); w.Write(bytes);
            foreach (double v in s) w.Write((short)Math.Round(Math.Max(-32767.0, Math.Min(32767.0, v * scale))));
        }
    }

    // Played at speed (< 1 = slower and lower), linear interpolation.
    public static double[] Speed(double[] src, double speed) {
        int n = (int)(src.Length / speed);
        var s = new double[n];
        for (int k = 0; k < n; k++) {
            double p = k * speed; int a = (int)p; double f = p - a;
            s[k] = a + 1 < src.Length ? src[a] * (1 - f) + src[a + 1] * f : src[src.Length - 1];
        }
        return s;
    }

    static double Peak(double[] s) { double p = 1e-9; foreach (double v in s) p = Math.Max(p, Math.Abs(v)); return p; }

    public static void Mix(double[] s, double[] part, double at, double level) {
        int start = (int)(at * Rate);
        double g = level / Peak(part);
        for (int k = 0; k < part.Length && start + k < s.Length; k++) s[start + k] += part[k] * g;
    }

    public static double[] Silence(double seconds) { return new double[(int)(seconds * Rate)]; }

    public static void Fade(double[] s, double inSeconds, double outSeconds) {
        int fin = Math.Max(1, (int)(inSeconds * Rate)), fout = Math.Max(1, (int)(outSeconds * Rate));
        for (int i = 0; i < s.Length; i++) s[i] *= Math.Min(1.0, i / (double)fin) * Math.Min(1.0, (s.Length - 1 - i) / (double)fout);
    }

    // A choir-like chord: each note three slightly detuned voices of a few soft harmonics with a slow vibrato,
    // swelling over attack seconds, holding, and dying away over release seconds; glints (short high pings)
    // grow denser with it.
    public static double[] Light(double seconds, double attack, double release) {
        var s = Silence(seconds);
        double[] notes = { 220.0, 277.18, 329.63, 440.0, 493.88, 659.25 };   // A3 C#4 E4 A4 B4 E5
        double[] detune = { -0.004, 0.0, 0.005 };
        double[] harm = { 1.0, 0.5, 0.35, 0.2, 0.1 };
        for (int i = 0; i < s.Length; i++) {
            double t = i / (double)Rate;
            double env = Math.Min(1.0, Math.Pow(t / attack, 2.0)) * Math.Min(1.0, (seconds - t) / release);
            double v = 0.0;
            for (int n = 0; n < notes.Length; n++)
                for (int d = 0; d < detune.Length; d++) {
                    double f = notes[n] * (1.0 + detune[d]) * (1.0 + 0.004 * Math.Sin(2.0 * Math.PI * (5.0 + d * 0.7) * t + n));
                    for (int h = 0; h < harm.Length; h++) v += harm[h] * Math.Sin(2.0 * Math.PI * f * (h + 1) * t + n * 1.3 + d * 2.1);
                }
            s[i] = v * env / (notes.Length * detune.Length);
        }
        var rnd = new Random(7);
        double[] glintNotes = { 1760.0, 2217.46, 2637.0, 3520.0, 4434.92 };
        for (double at = 0.4; at < seconds - 0.5; at += 0.05 + rnd.NextDouble() * 0.25) {
            double grow = Math.Min(1.0, at / attack) * Math.Min(1.0, (seconds - at) / release);
            if (rnd.NextDouble() > 0.35 + 0.6 * grow) continue;
            double f = glintNotes[rnd.Next(glintNotes.Length)];
            int start = (int)(at * Rate);
            for (int k = 0; k < Rate && start + k < s.Length; k++) {
                double t = k / (double)Rate;
                s[start + k] += 0.12 * grow * Math.Min(1.0, t / 0.003) * Math.Exp(-t / 0.25) * Math.Sin(2.0 * Math.PI * f * t);
            }
        }
        return s;
    }
}
'@
$slide = [GateSound]::Read($wav['stone-wall-slide1'])
$quake = [GateSound]::Read($wav['magic-quake1'])

$open = [GateSound]::Silence(4.3)
$slow = [GateSound]::Speed($slide, 0.6)
[GateSound]::Fade($slow, 0.05, 0.6)
[GateSound]::Mix($open, $slow, 0.1, 1.0)
$slower = [GateSound]::Speed($slide, 0.45)
[GateSound]::Fade($slower, 0.2, 0.8)
[GateSound]::Mix($open, $slower, 0.0, 0.45)
[GateSound]::Mix($open, $quake, 0.0, 0.5)
[GateSound]::Fade($open, 0.02, 0.9)
[GateSound]::Write((Join-Path $sounds 'S_GateOpen.wav'), $open, 0.9)

[GateSound]::Write((Join-Path $sounds 'S_GateLight.wav'), [GateSound]::Light(8.0, 3.0, 2.5), 0.7)

foreach ($n in $names) { Remove-Item $wav[$n] }
Get-ChildItem $sounds -Filter 'S_Gate*.wav' | Select-Object Name, Length
