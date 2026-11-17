# Writes the gear exit's sounds into SourceArt/Sounds (mono 16-bit 44.1 kHz), all synthesized here:
#   S_GearClunk.wav   "ga-gon": a lighter metal knock, then 0.11 s later a heavy one - a low thump, a falling clank
#                     of inharmonic metal partials and a burst of grit.
#   S_GearHiss.wav    "pshhh": a short low puff, then bright hissing steam that fades over about 1.5 s.
#   S_GearSpin.wav    loops (2 s): the gear turning - a low machine rumble with a ratchet tick 8 times a second.
#   S_GearSparks.wav  loops (2 s): sparks - a high sizzle and random sharp crackles.
# The loops wrap without a seam: the rumble is made of sines that fit the loop exactly, the ticks and crackles wrap
# round its end, and the sizzle's filter is run round the loop twice so its state matches at the join.
# BP_GearExit plays them (setup_gear_sounds.py). Run: powershell -File make_gear_sounds.ps1
$ErrorActionPreference = 'Stop'
$outDir = Join-Path (Split-Path -Parent $PSScriptRoot) 'SourceArt\Sounds'
New-Item -ItemType Directory -Force $outDir | Out-Null

Add-Type -TypeDefinition @'
using System;
using System.IO;

public static class GearSounds {
    const int Rate = 44100;

    // A one-shot ends in silence: the last 0.15 s fades out (no click or DC step at its end).
    static void FadeOut(double[] s) {
        int n = (int)(0.15 * Rate);
        for (int i = 0; i < n; i++) s[s.Length - 1 - i] *= (double)i / n;
    }

    static void Write(string path, double[] s, double peakTo) {
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

    // One metal knock at `at` seconds: thump (sine falling from f0 * 1.6 to f0), inharmonic clank, grit.
    static void Knock(double[] s, Random rnd, double at, double f0, double gain, double ring) {
        int start = (int)(at * Rate);
        double[] ratios = { 1.0, 2.76, 5.40, 8.93, 13.3 };
        double[] amps = { 1.0, 0.55, 0.35, 0.22, 0.12 };
        double phase = 0.0, lp = 0.0;
        for (int i = start; i < s.Length; i++) {
            double t = (i - start) / (double)Rate;
            double f = f0 * (1.0 + 0.6 * Math.Exp(-t / 0.03));
            phase += 2.0 * Math.PI * f / Rate;
            double thump = Math.Sin(phase) * Math.Exp(-t / 0.22);
            double clank = 0.0;
            for (int k = 0; k < ratios.Length; k++)
                clank += amps[k] * Math.Sin(2.0 * Math.PI * f0 * 3.1 * ratios[k] * t) * Math.Exp(-t / (ring / (1.0 + k * 0.6)));
            lp += 0.25 * ((rnd.NextDouble() * 2.0 - 1.0) - lp);
            double grit = lp * Math.Exp(-t / 0.025);
            double attack = Math.Min(1.0, t / 0.0015);
            s[i] += gain * attack * (1.0 * thump + 0.45 * clank + 0.7 * grit);
        }
    }

    public static void Clunk(string path) {
        var s = new double[(int)(1.3 * Rate)];
        var rnd = new Random(5);
        Knock(s, rnd, 0.00, 78.0, 0.55, 0.18);   // ga
        Knock(s, rnd, 0.11, 52.0, 1.00, 0.35);   // gon
        FadeOut(s);
        Write(path, s, 0.9);
    }

    public static void Hiss(string path) {
        var s = new double[(int)(1.8 * Rate)];
        var rnd = new Random(9);
        double lpPuff = 0.0, lpA = 0.0, lpB = 0.0, flutter = 0.0;
        for (int i = 0; i < s.Length; i++) {
            double t = i / (double)Rate;
            double white = rnd.NextDouble() * 2.0 - 1.0;
            // "pu": a dull puff of air, the first 80 ms.
            lpPuff += 0.04 * (white - lpPuff);
            double puff = lpPuff * 6.0 * Math.Min(1.0, t / 0.004) * Math.Exp(-t / 0.05);
            // "shhh": high-passed noise (white minus a low-pass), a little band-limited at the top.
            lpA += 0.08 * (white - lpA);
            double high = white - lpA;
            lpB += 0.55 * (high - lpB);
            flutter += 0.0005 * ((rnd.NextDouble() * 2.0 - 1.0) - flutter);
            double env = Math.Min(1.0, Math.Max(0.0, (t - 0.02) / 0.05)) * Math.Exp(-Math.Max(0.0, t - 0.25) / 0.55);
            s[i] = puff + lpB * env * (0.85 + 6.0 * flutter);
        }
        FadeOut(s);
        Write(path, s, 0.85);
    }

    public static void Spin(string path) {
        int n = 2 * Rate;
        var s = new double[n];
        var rnd = new Random(13);
        // Rumble: sines on the loop's 0.5 Hz grid, 30..220 Hz, random strength and phase.
        for (int k = 60; k <= 440; k++) {
            double f = k * 0.5, amp = (rnd.NextDouble() * 0.8 + 0.2) / Math.Sqrt(f), ph = rnd.NextDouble() * 2.0 * Math.PI;
            for (int i = 0; i < n; i++) s[i] += amp * Math.Sin(2.0 * Math.PI * f * i / Rate + ph);
        }
        // A machine hum: 50 Hz and its overtones, slightly beating.
        for (int i = 0; i < n; i++) {
            double t = i / (double)Rate;
            s[i] += 0.5 * Math.Sin(2.0 * Math.PI * 50.0 * t) + 0.25 * Math.Sin(2.0 * Math.PI * 100.5 * t) + 0.12 * Math.Sin(2.0 * Math.PI * 151.0 * t);
        }
        // Ratchet ticks: 16 a loop, each a click of grit and a short metal ring, wrapping round the end.
        for (int c = 0; c < 16; c++) {
            int start = c * n / 16 + rnd.Next(-300, 300);
            double ringF = 900.0 + rnd.NextDouble() * 250.0, gain = 0.7 + rnd.NextDouble() * 0.4, lp = 0.0;
            for (int j = 0; j < (int)(0.09 * Rate); j++) {
                double t = j / (double)Rate;
                lp += 0.4 * ((rnd.NextDouble() * 2.0 - 1.0) - lp);
                double v = gain * (lp * Math.Exp(-t / 0.006) * 1.6 + 0.5 * Math.Sin(2.0 * Math.PI * ringF * t) * Math.Exp(-t / 0.02));
                s[((start + j) % n + n) % n] += v;
            }
        }
        Write(path, s, 0.8);
    }

    public static void Sparks(string path) {
        int n = 2 * Rate;
        var s = new double[n];
        var rnd = new Random(17);
        // Sizzle: white noise high-passed round the loop twice, so it joins without a click.
        var white = new double[n];
        for (int i = 0; i < n; i++) white[i] = rnd.NextDouble() * 2.0 - 1.0;
        double lp = 0.0;
        for (int pass = 0; pass < 2; pass++)
            for (int i = 0; i < n; i++) {
                lp += 0.15 * (white[i] - lp);
                if (pass == 1) s[i] = 0.12 * (white[i] - lp);
            }
        // Crackles: 140 sharp little bursts, some bigger, wrapping round the end.
        for (int c = 0; c < 140; c++) {
            int start = rnd.Next(n);
            double gain = Math.Pow(rnd.NextDouble(), 2.5) * 1.0 + 0.08;
            double decay = 0.0015 + rnd.NextDouble() * 0.006, hp = 0.0;
            for (int j = 0; j < (int)(decay * 6.0 * Rate); j++) {
                double t = j / (double)Rate, w = rnd.NextDouble() * 2.0 - 1.0;
                hp += 0.5 * (w - hp);
                s[(start + j) % n] += gain * (w - hp) * Math.Exp(-t / decay);
            }
        }
        Write(path, s, 0.8);
    }
}
'@
[GearSounds]::Clunk((Join-Path $outDir 'S_GearClunk.wav'))
[GearSounds]::Hiss((Join-Path $outDir 'S_GearHiss.wav'))
[GearSounds]::Spin((Join-Path $outDir 'S_GearSpin.wav'))
[GearSounds]::Sparks((Join-Path $outDir 'S_GearSparks.wav'))
Get-ChildItem $outDir -Filter 'S_Gear*.wav' | Select-Object Name, Length
