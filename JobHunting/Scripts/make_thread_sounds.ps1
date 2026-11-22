# Writes the spider thread's sounds into SourceArt/Sounds (mono 16-bit 44.1 kHz), synthesized here (the user, 2026-11-22):
#   S_ThreadGrab.wav    "pin~": a soft silvery pluck of a fine string with a faint glint (~0.9 s). Caught hold of.
#   S_ThreadFray.wav    "giri-giri": the string straining - its tone creeping up, fine crackles growing (~1.1 s).
#                       Played once as the thread turns red.
#   S_ThreadSnap.wav    "puchin": a sharp snap, the string's twang dropping, sparkles falling away (~1.4 s).
#   S_ThreadReturn.wav  "kirari-n": a soft rising run of bells as the thread is back (~1.3 s).
# setup_thread_effects.py imports them. Run: powershell -File make_thread_sounds.ps1
$ErrorActionPreference = 'Stop'
$outDir = Join-Path (Split-Path -Parent $PSScriptRoot) 'SourceArt\Sounds'
New-Item -ItemType Directory -Force $outDir | Out-Null

Add-Type -TypeDefinition @'
using System;
using System.IO;

public static class ThreadSounds {
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

    static void Bell(double[] s, double at, double f, double gain, double ring) {
        int start = (int)(at * Rate);
        for (int i = start; i < s.Length; i++) {
            double t = (i - start) / (double)Rate;
            s[i] += gain * Math.Min(1.0, t / 0.002) * (Math.Sin(2.0 * Math.PI * f * t) * Math.Exp(-t / ring) + 0.25 * Math.Sin(2.0 * Math.PI * f * 2.0 * t) * Math.Exp(-t / (ring * 0.5)));
        }
    }

    // A plucked fine string: harmonics dying faster the higher they are; the pitch glides from f*bend to f over
    // bendTime (bend 1 = steady).
    static void Pluck(double[] s, double at, double f, double gain, double ring, double bend, double bendTime) {
        int start = (int)(at * Rate);
        double phase = 0.0;
        for (int i = start; i < s.Length; i++) {
            double t = (i - start) / (double)Rate;
            double ff = f * (1.0 + (bend - 1.0) * Math.Exp(-t / Math.Max(1e-4, bendTime)));
            phase += 2.0 * Math.PI * ff / Rate;
            double v = 0.0;
            for (int h = 1; h <= 5; h++)
                v += Math.Sin(phase * h * (1.0 + 0.0015 * h * h)) * Math.Exp(-t * h / ring) / h;
            s[i] += gain * Math.Min(1.0, t / 0.001) * v;
        }
    }

    // A soft high whoosh of air (filtered noise opening and closing).
    static void Air(double[] s, Random rnd, double at, double length, double gain) {
        int start = (int)(at * Rate), n = (int)(length * Rate);
        double lpA = 0.0, lpB = 0.0;
        for (int j = 0; j < n && start + j < s.Length; j++) {
            double u = j / (double)n, shape = Math.Sin(Math.PI * u);
            lpA += 0.35 * ((rnd.NextDouble() * 2.0 - 1.0) - lpA);
            lpB += 0.12 * (lpA - lpB);
            s[start + j] += gain * (lpA - lpB) * shape * shape;
        }
    }

    // A tiny crackle: a few milliseconds of bright noise.
    static void Crackle(double[] s, Random rnd, double at, double gain) {
        int start = (int)(at * Rate), n = (int)(0.004 * Rate);
        double prev = 0.0;
        for (int j = 0; j < n && start + j < s.Length; j++) {
            double w = rnd.NextDouble() * 2.0 - 1.0;
            s[start + j] += gain * (w - prev) * Math.Exp(-j / (0.001 * Rate));
            prev = w;
        }
    }

    public static void Grab(string path) {
        var s = new double[(int)(0.9 * Rate)];
        var rnd = new Random(81);
        Pluck(s, 0.0, 987.77, 0.5, 0.35, 1.0, 0.0);
        Pluck(s, 0.0, 1975.5, 0.12, 0.2, 1.0, 0.0);
        Air(s, rnd, 0.0, 0.12, 0.6);
        Bell(s, 0.03, 3951.0, 0.06, 0.25);
        FadeEnd(s, 0.2);
        Write(path, s, 0.6);
    }

    public static void Fray(string path) {
        var s = new double[(int)(1.1 * Rate)];
        var rnd = new Random(83);
        double phase = 0.0;
        for (int i = 0; i < s.Length; i++) {
            double t = i / (double)Rate;
            double f = 620.0 + 260.0 * t;
            phase += 2.0 * Math.PI * f / Rate;
            double rough = 0.6 + 0.4 * Math.Sin(2.0 * Math.PI * 23.0 * t) * Math.Sin(2.0 * Math.PI * 7.0 * t);
            double env = Math.Min(1.0, t / 0.15) * Math.Min(1.0, (1.1 - t) / 0.3);
            s[i] += 0.18 * env * rough * (Math.Sin(phase) + 0.5 * Math.Sin(2.0 * phase) + 0.3 * Math.Sin(3.0 * phase));
        }
        double at = 0.05;
        while (at < 1.0) {
            Crackle(s, rnd, at, 0.5 + 0.5 * at);
            at += 0.09 - 0.06 * at + 0.03 * rnd.NextDouble();
        }
        FadeEnd(s, 0.2);
        Write(path, s, 0.55);
    }

    public static void Snap(string path) {
        var s = new double[(int)(1.4 * Rate)];
        var rnd = new Random(89);
        Crackle(s, rnd, 0.0, 3.0);
        Crackle(s, rnd, 0.003, 2.0);
        Pluck(s, 0.0, 1046.5, 0.5, 0.25, 1.5, 0.06);
        Air(s, rnd, 0.0, 0.18, 0.5);
        double[] notes = { 3136.0, 2637.0, 2093.0, 1568.0, 1318.5 };
        for (int k = 0; k < notes.Length; k++) Bell(s, 0.08 + 0.07 * k, notes[k], 0.09 - 0.01 * k, 0.4);
        FadeEnd(s, 0.3);
        Write(path, s, 0.8);
    }

    public static void Return(string path) {
        var s = new double[(int)(1.3 * Rate)];
        var rnd = new Random(97);
        Air(s, rnd, 0.0, 0.5, 0.25);
        double[] notes = { 1568.0, 2093.0, 2637.0, 3136.0, 4186.0 };
        for (int k = 0; k < notes.Length; k++) Bell(s, 0.02 + 0.07 * k, notes[k], 0.1, 0.45);
        FadeEnd(s, 0.3);
        Write(path, s, 0.5);
    }
}
'@
[ThreadSounds]::Grab((Join-Path $outDir 'S_ThreadGrab.wav'))
[ThreadSounds]::Fray((Join-Path $outDir 'S_ThreadFray.wav'))
[ThreadSounds]::Snap((Join-Path $outDir 'S_ThreadSnap.wav'))
[ThreadSounds]::Return((Join-Path $outDir 'S_ThreadReturn.wav'))
Get-ChildItem $outDir -Filter 'S_Thread*.wav' | Select-Object Name, Length
