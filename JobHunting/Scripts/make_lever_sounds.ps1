# Writes the lever's and the big mechanisms' sounds into SourceArt/Sounds (mono 16-bit 44.1 kHz), synthesized here
# (the user, 2026-11-20):
#   S_LeverPull.wav    "kacha... ga-kon": the latch clicks free, the handle ratchets over (four quickening ticks) and
#                      lands 0.38 s in with a heavy iron clunk (BP_Lever's swing takes 0.4 s).
#   S_LeverReturn.wav  "ka-chan": the spring throws it back - a quick ratchet and a lighter clank.
#   S_MechRumble.wav   loops (3 s): stone grinding on stone - a deep rumble, a rough scraping that swells and fades,
#                      and bits of grit. Played while a BP_Mechanism moves.
#   S_MechStop.wav     "ga-kon": a mechanism part coming to rest (the drawer steps knock home one after another).
# The loop wraps without a seam (sines that fit the loop, noise filtered round it twice, grit wrapping round the end).
# setup_lever_sounds.py imports them. Run: powershell -File make_lever_sounds.ps1
$ErrorActionPreference = 'Stop'
$outDir = Join-Path (Split-Path -Parent $PSScriptRoot) 'SourceArt\Sounds'
New-Item -ItemType Directory -Force $outDir | Out-Null

Add-Type -TypeDefinition @'
using System;
using System.IO;

public static class LeverSounds {
    const int Rate = 44100;

    static void FadeOut(double[] s) {
        int n = (int)(0.12 * Rate);
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

    // A small metal click: a burst of bright grit and a short ring.
    static void Click(double[] s, Random rnd, double at, double ring, double gain) {
        int start = (int)(at * Rate);
        double hp = 0.0;
        for (int j = 0; j < (int)(0.08 * Rate) && start + j < s.Length; j++) {
            double t = j / (double)Rate, w = rnd.NextDouble() * 2.0 - 1.0;
            hp += 0.3 * (w - hp);
            s[start + j] += gain * ((w - hp) * Math.Exp(-t / 0.004) * 1.4 + 0.6 * Math.Sin(2.0 * Math.PI * ring * t) * Math.Exp(-t / 0.018)
                                    + 0.3 * Math.Sin(2.0 * Math.PI * ring * 2.71 * t) * Math.Exp(-t / 0.01));
        }
    }

    // A heavy iron knock: a falling thump, inharmonic clank and grit.
    static void Knock(double[] s, Random rnd, double at, double f0, double gain, double ring) {
        int start = (int)(at * Rate);
        double[] ratios = { 1.0, 2.76, 5.40, 8.93, 13.3 };
        double[] amps = { 1.0, 0.55, 0.35, 0.22, 0.12 };
        double phase = 0.0, lp = 0.0;
        for (int i = start; i < s.Length; i++) {
            double t = (i - start) / (double)Rate;
            double f = f0 * (1.0 + 0.6 * Math.Exp(-t / 0.03));
            phase += 2.0 * Math.PI * f / Rate;
            double thump = Math.Sin(phase) * Math.Exp(-t / 0.16);
            double clank = 0.0;
            for (int k = 0; k < ratios.Length; k++)
                clank += amps[k] * Math.Sin(2.0 * Math.PI * f0 * 3.4 * ratios[k] * t) * Math.Exp(-t / (ring / (1.0 + k * 0.6)));
            lp += 0.25 * ((rnd.NextDouble() * 2.0 - 1.0) - lp);
            double grit = lp * Math.Exp(-t / 0.02);
            s[i] += gain * Math.Min(1.0, t / 0.0015) * (thump + 0.5 * clank + 0.6 * grit);
        }
    }

    public static void Pull(string path) {
        var s = new double[(int)(1.2 * Rate)];
        var rnd = new Random(21);
        Click(s, rnd, 0.00, 2300.0, 0.7);                       // the latch
        double[] ticks = { 0.10, 0.19, 0.26, 0.32 };            // the ratchet, quickening
        for (int k = 0; k < ticks.Length; k++) Click(s, rnd, ticks[k], 1500.0 + 150.0 * k, 0.35 + 0.08 * k);
        Knock(s, rnd, 0.38, 70.0, 1.0, 0.3);                    // ga-kon
        FadeOut(s);
        Write(path, s, 0.9);
    }

    public static void Return(string path) {
        var s = new double[(int)(0.9 * Rate)];
        var rnd = new Random(23);
        double[] ticks = { 0.00, 0.05, 0.09, 0.12 };
        for (int k = 0; k < ticks.Length; k++) Click(s, rnd, ticks[k], 1900.0 - 120.0 * k, 0.3);
        Knock(s, rnd, 0.16, 105.0, 0.55, 0.22);
        Click(s, rnd, 0.17, 2600.0, 0.5);
        FadeOut(s);
        Write(path, s, 0.75);
    }

    // Soft saturation: makes the low end's overtones, so the weight still comes through small speakers.
    static double Drive(double v, double amount) { return Math.Tanh(v * amount) / Math.Tanh(amount); }

    // "DOOON... ga-kon... para-para": a big part coming to rest (2026-11-20 heavier): a driven sub boom with a long
    // tail, a stone knock on top, then pebbles pattering down for half a second.
    public static void Stop(string path) {
        var s = new double[(int)(1.6 * Rate)];
        var rnd = new Random(31);
        double phase = 0.0, lp = 0.0;
        for (int i = 0; i < s.Length; i++) {
            double t = i / (double)Rate;
            double f = 42.0 * (1.0 + 0.8 * Math.Exp(-t / 0.04));
            phase += 2.0 * Math.PI * f / Rate;
            lp += 0.03 * ((rnd.NextDouble() * 2.0 - 1.0) - lp);
            double boom = (Math.Sin(phase) + 6.0 * lp) * Math.Exp(-t / 0.45) * Math.Min(1.0, t / 0.002);
            s[i] += 1.3 * Drive(boom, 2.5);
        }
        Knock(s, rnd, 0.00, 95.0, 0.6, 0.14);
        Knock(s, rnd, 0.04, 55.0, 0.9, 0.25);
        for (int c = 0; c < 22; c++) Click(s, rnd, 0.12 + 0.5 * Math.Pow(rnd.NextDouble(), 1.6), 1200.0 + rnd.NextDouble() * 1800.0, 0.08 + 0.12 * rnd.NextDouble());
        FadeOut(s);
        Write(path, s, 0.9);
    }

    // Loops (3 s), heavier (2026-11-20): a driven deep rumble, thick 100-300 Hz grinding that judders 6-8 times a
    // second like stone catching on stone, irregular heavy "goto" knocks, and grit. Every part fits the loop.
    public static void Rumble(string path) {
        int n = 3 * Rate;
        var s = new double[n];
        var rnd = new Random(29);
        // Deep rumble: sines on the loop's 1/3 Hz grid, 25..110 Hz, then driven for overtones.
        var deep = new double[n];
        for (int k = 75; k <= 330; k++) {
            double f = k / 3.0, amp = (rnd.NextDouble() * 0.8 + 0.2) / Math.Sqrt(f), ph = rnd.NextDouble() * 2.0 * Math.PI;
            for (int i = 0; i < n; i++) deep[i] += amp * Math.Sin(2.0 * Math.PI * f * i / Rate + ph);
        }
        double peak = 1e-9;
        foreach (double v in deep) peak = Math.Max(peak, Math.Abs(v));
        for (int i = 0; i < n; i++) s[i] += 1.0 * Drive(deep[i] / peak, 3.0);
        // Grinding: 100-300 Hz band noise (filtered round the loop twice), juddering: |sin| at 7 Hz (21 per loop)
        // with a slower swell at 2/3 Hz.
        var white = new double[n];
        for (int i = 0; i < n; i++) white[i] = rnd.NextDouble() * 2.0 - 1.0;
        double lpA = 0.0, lpB = 0.0, lpC = 0.0;
        for (int pass = 0; pass < 2; pass++)
            for (int i = 0; i < n; i++) {
                lpA += 0.045 * (white[i] - lpA);      // ~320 Hz top
                lpB += 0.014 * (lpA - lpB);           // ~100 Hz bottom
                lpC += 0.25 * ((white[i] - lpA) - lpC);
                if (pass == 1) {
                    double t = i / (double)Rate;
                    double judder = 0.45 + 0.55 * Math.Abs(Math.Sin(Math.PI * 7.0 * t));
                    double swell = 0.7 + 0.3 * Math.Sin(2.0 * Math.PI * t * 2.0 / 3.0 + 0.7);
                    s[i] += 4.5 * (lpA - lpB) * judder * swell + 0.35 * lpC * judder * swell;
                }
            }
        // Heavy knocks: five a loop at uneven times, wrapping round the end.
        double[] knocks = { 0.2, 0.75, 1.5, 2.05, 2.6 };
        foreach (double at in knocks) {
            int start = (int)(at * Rate);
            double f0 = 60.0 + rnd.NextDouble() * 30.0, ph = 0.0, g = 0.45 + 0.35 * rnd.NextDouble();
            for (int j = 0; j < (int)(0.35 * Rate); j++) {
                double t = j / (double)Rate;
                ph += 2.0 * Math.PI * f0 * (1.0 + 0.5 * Math.Exp(-t / 0.02)) / Rate;
                s[(start + j) % n] += g * Drive(Math.Sin(ph) * Math.Exp(-t / 0.09), 2.0);
            }
        }
        // Grit: little cracks of stone, wrapping round the end.
        for (int c = 0; c < 60; c++) {
            int start = rnd.Next(n);
            double gain = Math.Pow(rnd.NextDouble(), 2.0) * 0.4 + 0.05, decay = 0.004 + rnd.NextDouble() * 0.01, lp = 0.0;
            for (int j = 0; j < (int)(decay * 6.0 * Rate); j++) {
                double t = j / (double)Rate;
                lp += 0.35 * ((rnd.NextDouble() * 2.0 - 1.0) - lp);
                s[(start + j) % n] += gain * lp * Math.Exp(-t / decay);
            }
        }
        Write(path, s, 0.9);
    }
}
'@
[LeverSounds]::Pull((Join-Path $outDir 'S_LeverPull.wav'))
[LeverSounds]::Return((Join-Path $outDir 'S_LeverReturn.wav'))
[LeverSounds]::Rumble((Join-Path $outDir 'S_MechRumble.wav'))
[LeverSounds]::Stop((Join-Path $outDir 'S_MechStop.wav'))
Get-ChildItem $outDir -Filter 'S_*.wav' | Where-Object { $_.Name -match 'Lever|MechRumble|MechStop' } | Select-Object Name, Length
