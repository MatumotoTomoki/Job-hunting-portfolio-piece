# Synthesises the screen-crack sound for the danger button (a heavy "BAKI!": thick glass breaking) into
# SourceArt/Models/DangerButton/S_GlassCrack.wav (44.1 kHz, mono, 16 bit, about 1.3 s):
#   a deep thump (a falling low tone) and a dull rumble of the hit, a hard crack on top of it, a crunch of smaller
#   cracks running on for a third of a second, the glass ringing low, and a short echo of a room round all of it,
#   driven a little into saturation to make it thicker.
# Change $Seed for a different crack. Run:
#   powershell -File build_crack_sound.ps1
param([int]$Seed = 3)
$ErrorActionPreference = 'Stop'
$out = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\SourceArt\Models\DangerButton'))
New-Item -ItemType Directory -Force $out | Out-Null

Add-Type -TypeDefinition @'
using System;
using System.IO;
public static class HeavyCrackSound {
    const int Rate = 44100;
    static double[] s;
    static Random r;

    // A burst of noise: `dark` 0 is bright and sharp, near 1 dull and low.
    static void Burst(double start, double length, double loud, double dark) {
        int a = (int)(start * Rate), len = (int)(length * Rate);
        double low = 0, last = 0;
        for (int i = 0; i < len && a + i < s.Length; i++) {
            double noise = r.NextDouble() * 2 - 1;
            low = low * dark + noise * (1 - dark);
            double bright = noise - last * 0.7; last = noise;
            double v = dark > 0.5 ? low * 4.0 : bright;
            s[a + i] += v * loud * Math.Exp(-i / (len * 0.25)) * Math.Min(1.0, i / 20.0);
        }
    }

    public static void Build(string path, int seed) {
        int n = (int)(Rate * 1.3);
        s = new double[n];
        r = new Random(seed);
        // The deep thump: a low tone falling from 110 to 40 Hz.
        double phase = 0;
        for (int i = 0; i < (int)(0.4 * Rate); i++) {
            double t = (double)i / Rate;
            double f = 40 + 70 * Math.Exp(-t / 0.05);
            phase += 2 * Math.PI * f / Rate;
            s[i] += 1.1 * (Math.Sin(phase) + 0.3 * Math.Sin(2 * phase)) * Math.Exp(-t / 0.11) * Math.Min(1, t / 0.001);
        }
        // The dull rumble of the hit, and the hard crack on top.
        Burst(0.0, 0.25, 0.9, 0.96);
        Burst(0.0, 0.07, 1.0, 0.0);
        Burst(0.004, 0.05, 0.6, 0.75);
        // The crunch: smaller cracks running on, some sharp, some dull, getting quieter.
        double when = 0.02;
        for (int k = 0; k < 22; k++) {
            when += 0.004 + r.NextDouble() * 0.018;
            double fade = 1 - k / 24.0;
            Burst(when, 0.006 + r.NextDouble() * 0.02, (0.25 + 0.5 * r.NextDouble()) * fade, r.NextDouble() < 0.4 ? 0.8 : 0.0);
        }
        // The glass ringing, low and short.
        double[] tones = { 1650, 2390, 3480, 4720 };
        for (int k = 0; k < tones.Length; k++) {
            double p = r.NextDouble() * 6.28, decay = 0.15 + 0.15 * r.NextDouble(), loud = 0.07 / (1 + k * 0.5);
            for (int i = 0; i < n; i++) {
                double t = (double)i / Rate;
                s[i] += loud * Math.Sin(2 * Math.PI * tones[k] * t + p) * Math.Exp(-t / decay) * Math.Min(1, t / 0.003);
            }
        }
        // A few heavy bits of glass falling.
        for (int k = 0; k < 4; k++) Burst(0.25 + r.NextDouble() * 0.45, 0.012, 0.18, 0.0);
        // Saturation for weight.
        for (int i = 0; i < n; i++) s[i] = Math.Tanh(s[i] * 1.6);
        // A short room echo: three feedback delays.
        var wet = new double[n];
        int[] delays = { (int)(0.031 * Rate), (int)(0.043 * Rate), (int)(0.059 * Rate) };
        foreach (int d in delays) {
            var line = new double[n];
            for (int i = 0; i < n; i++) {
                line[i] = s[i] + (i >= d ? line[i - d] * 0.55 : 0);
                wet[i] += line[i] / delays.Length;
            }
        }
        double peak = 0;
        for (int i = 0; i < n; i++) {
            s[i] = s[i] * 0.8 + wet[i] * 0.35;
            double tail = (double)(n - i) / (0.15 * Rate);
            if (tail < 1) s[i] *= tail;
            peak = Math.Max(peak, Math.Abs(s[i]));
        }
        using (var w = new BinaryWriter(File.Create(path))) {
            w.Write("RIFF".ToCharArray()); w.Write(36 + n * 2); w.Write("WAVE".ToCharArray());
            w.Write("fmt ".ToCharArray()); w.Write(16); w.Write((short)1); w.Write((short)1);
            w.Write(Rate); w.Write(Rate * 2); w.Write((short)2); w.Write((short)16);
            w.Write("data".ToCharArray()); w.Write(n * 2);
            for (int i = 0; i < n; i++) w.Write((short)(s[i] / peak * 0.89 * 32767));
        }
    }
}
'@
$file = Join-Path $out 'S_GlassCrack.wav'
[HeavyCrackSound]::Build($file, $Seed)
Get-Item $file | Select-Object Name, Length
