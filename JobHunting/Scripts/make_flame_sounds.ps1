# Writes the flame jet's sounds into SourceArt/Sounds (mono 16-bit 44.1 kHz), synthesized here (the user, 2026-11-22):
#   S_FlameWarn.wav   "bo-bo-bo": the vent sputtering as it flares up (~0.6 s, WarnSeconds)
#   S_FlameErupt.wav  "bwoh!": the column bursting out - a deep whoomp and a rush of air (~0.6 s)
#   S_FlameRoar.wav   loops (2 s): the column roaring while it stands, flickering; faded out as it stops
#   S_FlameHurt.wav   "jutt": a sizzle as the player is caught (~0.45 s)
# The loop wraps without a seam (noise filtered round it twice, flicker that fits the loop).
# setup_flame_effects.py imports them (S_FlameRoar looping). Run: powershell -File make_flame_sounds.ps1
$ErrorActionPreference = 'Stop'
$outDir = Join-Path (Split-Path -Parent $PSScriptRoot) 'SourceArt\Sounds'
New-Item -ItemType Directory -Force $outDir | Out-Null

Add-Type -TypeDefinition @'
using System;
using System.IO;

public static class FlameSounds {
    const int Rate = 44100;

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

    static void FadeEnd(double[] s, double seconds) {
        int fade = (int)(seconds * Rate);
        for (int i = 0; i < fade; i++) s[s.Length - 1 - i] *= (double)i / fade;
    }

    // A puff of fire: low-passed noise with a quick attack, dying over decay.
    static void Puff(double[] s, Random rnd, double at, double gain, double decay, double cut) {
        int start = (int)(at * Rate);
        double a = 0.0, b = 0.0;
        for (int j = 0; start + j < s.Length; j++) {
            double t = j / (double)Rate;
            if (t > decay * 6.0) break;
            a += cut * ((rnd.NextDouble() * 2.0 - 1.0) - a);
            b += cut * (a - b);
            s[start + j] += gain * b * Math.Min(1.0, t / 0.004) * Math.Exp(-t / decay);
        }
    }

    static void Crackle(double[] s, Random rnd, double at, double gain) {
        int start = (int)(at * Rate), n = (int)(0.003 * Rate);
        double prev = 0.0;
        for (int j = 0; j < n && start + j < s.Length; j++) {
            double w = rnd.NextDouble() * 2.0 - 1.0;
            s[start + j] += gain * (w - prev) * Math.Exp(-j / (0.0008 * Rate));
            prev = w;
        }
    }

    public static void Warn(string path) {
        var s = new double[(int)(0.6 * Rate)];
        var rnd = new Random(131);
        double at = 0.0;
        while (at < 0.5) {
            double u = at / 0.5;
            Puff(s, rnd, at, 6.0 * (0.4 + 0.6 * u), 0.03, 0.06);
            at += 0.07 - 0.03 * u + 0.02 * rnd.NextDouble();
        }
        for (int k = 0; k < 25; k++) Crackle(s, rnd, 0.6 * rnd.NextDouble(), 0.25 + 0.25 * rnd.NextDouble());
        FadeEnd(s, 0.08);
        Write(path, s, 0.6);
    }

    public static void Erupt(string path) {
        var s = new double[(int)(0.6 * Rate)];
        var rnd = new Random(137);
        double phase = 0.0;
        for (int i = 0; i < s.Length; i++) {
            double t = i / (double)Rate;
            phase += 2.0 * Math.PI * 55.0 * (1.0 + 1.2 * Math.Exp(-t / 0.03)) / Rate;
            s[i] += 0.8 * Math.Sin(phase) * Math.Min(1.0, t / 0.005) * Math.Exp(-t / 0.09);
        }
        Puff(s, rnd, 0.0, 14.0, 0.18, 0.12);
        Puff(s, rnd, 0.01, 6.0, 0.12, 0.35);
        for (int k = 0; k < 30; k++) Crackle(s, rnd, 0.5 * rnd.NextDouble(), 0.2 + 0.3 * rnd.NextDouble());
        FadeEnd(s, 0.15);
        Write(path, s, 0.85);
    }

    public static void Roar(string path) {
        int n = 2 * Rate;
        var s = new double[n];
        var rnd = new Random(139);
        var white = new double[n];
        for (int i = 0; i < n; i++) white[i] = rnd.NextDouble() * 2.0 - 1.0;
        double a = 0.0, b = 0.0, c = 0.0;
        for (int pass = 0; pass < 2; pass++)
            for (int i = 0; i < n; i++) {
                a += 0.05 * (white[i] - a);          // the body of the roar (~350 Hz top)
                b += 0.05 * (a - b);
                c += 0.4 * (white[i] - c);           // a thinner hiss on top
                if (pass == 1) {
                    double t = i / (double)Rate;
                    double flicker = 0.8 + 0.12 * Math.Sin(2.0 * Math.PI * 7.0 * t) + 0.08 * Math.Sin(2.0 * Math.PI * 11.5 * t + 1.3);
                    s[i] = (6.0 * b + 0.25 * (white[i] - c)) * flicker;
                }
            }
        // Crackles in the middle only, away from the seam's 5 ms.
        for (int k = 0; k < 60; k++) Crackle(s, rnd, 0.01 + 1.97 * rnd.NextDouble(), 0.3 + 0.3 * rnd.NextDouble());
        Write(path, s, 0.6);
    }

    public static void Hurt(string path) {
        var s = new double[(int)(0.45 * Rate)];
        var rnd = new Random(149);
        double prev = 0.0, lp = 0.0;
        for (int i = 0; i < s.Length; i++) {
            double t = i / (double)Rate;
            double w = rnd.NextDouble() * 2.0 - 1.0;
            double hp = w - prev; prev = w;
            lp += 0.6 * (hp - lp);
            s[i] += lp * Math.Min(1.0, t / 0.005) * Math.Exp(-t / 0.15) * (0.7 + 0.3 * Math.Sin(2.0 * Math.PI * 40.0 * t));
        }
        for (int k = 0; k < 40; k++) Crackle(s, rnd, 0.35 * rnd.NextDouble() * rnd.NextDouble(), 0.4 + 0.4 * rnd.NextDouble());
        Puff(s, rnd, 0.0, 4.0, 0.05, 0.1);
        FadeEnd(s, 0.1);
        Write(path, s, 0.7);
    }
}
'@
[FlameSounds]::Warn((Join-Path $outDir 'S_FlameWarn.wav'))
[FlameSounds]::Erupt((Join-Path $outDir 'S_FlameErupt.wav'))
[FlameSounds]::Roar((Join-Path $outDir 'S_FlameRoar.wav'))
[FlameSounds]::Hurt((Join-Path $outDir 'S_FlameHurt.wav'))
Get-ChildItem $outDir -Filter 'S_Flame*.wav' | Select-Object Name, Length
