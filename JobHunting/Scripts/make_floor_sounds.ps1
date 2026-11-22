# Writes the crumbling floor's sounds into SourceArt/Sounds (mono 16-bit 44.1 kHz), synthesized here (the user, 2026-11-22):
#   S_FloorCrack.wav   "mishi... gogogo": a crack and a thud as it is stepped on, then a low rumble shaking in step
#                      with the floor (12.5 Hz, its 0.08 s shake steps) and grit trickling (~1.0 s)
#   S_FloorFall.wav    "garagara": it gives way - a heavy thud and crack, a burst of rubble rattling, dying away as
#                      it drops (~1.6 s; it also rides down with the floor)
#   S_FloorReturn.wav  "bofu": a soft puff as it is back (with the smoke) (~0.6 s)
# setup_floor_effects.py imports them. Run: powershell -File make_floor_sounds.ps1
$ErrorActionPreference = 'Stop'
$outDir = Join-Path (Split-Path -Parent $PSScriptRoot) 'SourceArt\Sounds'
New-Item -ItemType Directory -Force $outDir | Out-Null

Add-Type -TypeDefinition @'
using System;
using System.IO;

public static class FloorSounds {
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

    // A low thud: a sine dropping in pitch, dying fast.
    static void Thud(double[] s, double at, double f, double gain, double decay) {
        int start = (int)(at * Rate);
        double phase = 0.0;
        for (int i = start; i < s.Length; i++) {
            double t = (i - start) / (double)Rate;
            if (t > decay * 8.0) break;
            phase += 2.0 * Math.PI * f * (1.0 + 0.8 * Math.Exp(-t / 0.02)) / Rate;
            s[i] += gain * Math.Min(1.0, t / 0.002) * Math.Sin(phase) * Math.Exp(-t / decay);
        }
    }

    // A crack: a few milliseconds of bright noise.
    static void Crack(double[] s, Random rnd, double at, double gain, double length) {
        int start = (int)(at * Rate), n = (int)(length * Rate);
        double prev = 0.0;
        for (int j = 0; j < n && start + j < s.Length; j++) {
            double w = rnd.NextDouble() * 2.0 - 1.0;
            s[start + j] += gain * (w - prev) * Math.Exp(-j / (0.25 * n));
            prev = w;
        }
    }

    // A grain of grit: a tiny ringing tick at a random pitch.
    static void Grit(double[] s, Random rnd, double at, double gain) {
        int start = (int)(at * Rate);
        double f = 1500.0 + 3500.0 * rnd.NextDouble(), decay = 0.003 + 0.004 * rnd.NextDouble();
        for (int j = 0; start + j < s.Length; j++) {
            double t = j / (double)Rate;
            if (t > decay * 6.0) break;
            s[start + j] += gain * Math.Sin(2.0 * Math.PI * f * t) * Math.Exp(-t / decay);
        }
    }

    // A rock knock: a lower, duller tick.
    static void Knock(double[] s, Random rnd, double at, double gain) {
        int start = (int)(at * Rate);
        double f = 250.0 + 500.0 * rnd.NextDouble(), decay = 0.008 + 0.01 * rnd.NextDouble();
        for (int j = 0; start + j < s.Length; j++) {
            double t = j / (double)Rate;
            if (t > decay * 6.0) break;
            s[start + j] += gain * (Math.Sin(2.0 * Math.PI * f * t) + 0.4 * (rnd.NextDouble() - 0.5)) * Math.Exp(-t / decay);
        }
    }

    // A low rumble: noise filtered down to ~100-200 Hz, shaped by env(t).
    static void Rumble(double[] s, Random rnd, double at, double length, double gain, Func<double, double> env) {
        int start = (int)(at * Rate), n = (int)(length * Rate);
        double a = 0.0, b = 0.0;
        for (int j = 0; j < n && start + j < s.Length; j++) {
            a += 0.02 * ((rnd.NextDouble() * 2.0 - 1.0) - a);
            b += 0.02 * (a - b);
            s[start + j] += gain * 12.0 * b * env(j / (double)Rate);
        }
    }

    public static void CrackSound(string path) {
        var s = new double[(int)(1.0 * Rate)];
        var rnd = new Random(101);
        Crack(s, rnd, 0.0, 1.0, 0.012);
        Crack(s, rnd, 0.025, 0.6, 0.008);
        Thud(s, 0.0, 75.0, 0.9, 0.06);
        Rumble(s, rnd, 0.0, 1.0, 1.0, t => Math.Min(1.0, t / 0.08) * Math.Min(1.0, (1.0 - t) / 0.25) * (0.65 + 0.35 * Math.Sin(2.0 * Math.PI * 12.5 * t)));
        double at = 0.05;
        while (at < 0.95) {
            Grit(s, rnd, at, 0.12 + 0.1 * rnd.NextDouble());
            if (rnd.NextDouble() < 0.25) Knock(s, rnd, at + 0.01, 0.2);
            at += 0.02 + 0.05 * rnd.NextDouble();
        }
        FadeEnd(s, 0.15);
        Write(path, s, 0.75);
    }

    public static void FallSound(string path) {
        var s = new double[(int)(1.6 * Rate)];
        var rnd = new Random(103);
        Crack(s, rnd, 0.0, 1.2, 0.02);
        Thud(s, 0.0, 55.0, 1.2, 0.12);
        Thud(s, 0.04, 90.0, 0.5, 0.05);
        Rumble(s, rnd, 0.0, 1.6, 1.6, t => Math.Min(1.0, t / 0.02) * Math.Exp(-t / 0.45));
        double at = 0.01;
        while (at < 1.5) {
            double density = Math.Exp(-at / 0.5);
            Grit(s, rnd, at, (0.1 + 0.15 * rnd.NextDouble()) * (0.3 + density));
            if (rnd.NextDouble() < 0.5 * density + 0.1) Knock(s, rnd, at + 0.005, (0.3 + 0.3 * rnd.NextDouble()) * (0.3 + density));
            at += 0.006 + 0.06 * (1.0 - density) * rnd.NextDouble() + 0.01 * rnd.NextDouble();
        }
        FadeEnd(s, 0.3);
        Write(path, s, 0.85);
    }

    public static void ReturnSound(string path) {
        var s = new double[(int)(0.6 * Rate)];
        var rnd = new Random(107);
        double a = 0.0, b = 0.0;
        for (int i = 0; i < s.Length; i++) {
            double t = i / (double)Rate;
            a += 0.08 * ((rnd.NextDouble() * 2.0 - 1.0) - a);
            b += 0.03 * (a - b);
            double env = Math.Min(1.0, t / 0.02) * Math.Exp(-t / 0.12);
            s[i] += env * (a - 0.5 * b);
        }
        Thud(s, 0.0, 110.0, 0.25, 0.04);
        FadeEnd(s, 0.15);
        Write(path, s, 0.45);
    }
}
'@
[FloorSounds]::CrackSound((Join-Path $outDir 'S_FloorCrack.wav'))
[FloorSounds]::FallSound((Join-Path $outDir 'S_FloorFall.wav'))
[FloorSounds]::ReturnSound((Join-Path $outDir 'S_FloorReturn.wav'))
Get-ChildItem $outDir -Filter 'S_Floor*.wav' | Select-Object Name, Length
