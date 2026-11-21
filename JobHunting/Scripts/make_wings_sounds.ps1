# Writes the wings' sounds into SourceArt/Sounds (mono 16-bit 44.1 kHz), synthesized here (the user, 2026-11-21):
#   S_WingsGet.wav    "fwaaan": a holy major chord (C5 E5 G5 C6, gently detuned) swelling in over a soft whoosh,
#                     with bell sparkles on top (~2.4 s). Played as the wings are taken.
#   S_WingFlap.wav    "basa": two quick feathery whooshes as the wings spread.
#   S_WingGlide.wav   loops (3 s): soft wind past the wings, swelling and easing. Played while they are spread.
# The loop wraps without a seam (noise filtered round it twice, swells that fit the loop).
# setup_wings_effects.py imports them. Run: powershell -File make_wings_sounds.ps1
$ErrorActionPreference = 'Stop'
$outDir = Join-Path (Split-Path -Parent $PSScriptRoot) 'SourceArt\Sounds'
New-Item -ItemType Directory -Force $outDir | Out-Null

Add-Type -TypeDefinition @'
using System;
using System.IO;

public static class WingsSounds {
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

    static void Bell(double[] s, double at, double f, double gain, double ring) {
        int start = (int)(at * Rate);
        for (int i = start; i < s.Length; i++) {
            double t = (i - start) / (double)Rate;
            s[i] += gain * Math.Min(1.0, t / 0.002) * (Math.Sin(2.0 * Math.PI * f * t) * Math.Exp(-t / ring) + 0.25 * Math.Sin(2.0 * Math.PI * f * 2.0 * t) * Math.Exp(-t / (ring * 0.5)));
        }
    }

    // A whoosh: band noise whose filter opens and closes over its length.
    static void Whoosh(double[] s, Random rnd, double at, double length, double gain, double brightness) {
        int start = (int)(at * Rate), n = (int)(length * Rate);
        double lpA = 0.0, lpB = 0.0;
        for (int j = 0; j < n && start + j < s.Length; j++) {
            double u = j / (double)n, shape = Math.Sin(Math.PI * Math.Pow(u, 0.6));
            double top = 0.02 + brightness * shape;
            lpA += top * ((rnd.NextDouble() * 2.0 - 1.0) - lpA);
            lpB += top * 0.2 * (lpA - lpB);
            s[start + j] += gain * (lpA - lpB) * shape * shape;
        }
    }

    public static void Get(string path) {
        var s = new double[(int)(2.4 * Rate)];
        var rnd = new Random(61);
        double[] chord = { 523.25, 659.25, 783.99, 1046.5 };
        for (int i = 0; i < s.Length; i++) {
            double t = i / (double)Rate;
            double env = Math.Min(1.0, t / 0.35) * Math.Exp(-Math.Max(0.0, t - 0.6) / 0.6);
            double v = 0.0;
            foreach (double f in chord)
                for (int d = -1; d <= 1; d++) {
                    double fd = f * (1.0 + 0.0025 * d);
                    v += (Math.Sin(2.0 * Math.PI * fd * t) + 0.2 * Math.Sin(2.0 * Math.PI * fd * 2.0 * t)) / 3.0;
                }
            s[i] += 0.22 * v * env * (0.85 + 0.15 * Math.Sin(2.0 * Math.PI * 5.0 * t));
        }
        Whoosh(s, rnd, 0.0, 0.7, 2.0, 0.25);
        double[] notes = { 2093.0, 2637.0, 3136.0, 4186.0, 3136.0 };
        for (int k = 0; k < notes.Length; k++) Bell(s, 0.25 + 0.09 * k, notes[k], 0.12, 0.5);
        int fade = (int)(0.3 * Rate);
        for (int i = 0; i < fade; i++) s[s.Length - 1 - i] *= (double)i / fade;
        Write(path, s, 0.8);
    }

    // "fusa" (softened 2026-11-21: the first one was too harsh): one slow, gentle sweep of soft feathers - a dull
    // filter, a slow rise and fall, a faint second brush. No thump.
    public static void Flap(string path) {
        var s = new double[(int)(0.55 * Rate)];
        var rnd = new Random(67);
        Whoosh(s, rnd, 0.0, 0.34, 2.2, 0.12);
        Whoosh(s, rnd, 0.16, 0.34, 1.0, 0.08);
        int fade = (int)(0.08 * Rate);
        for (int i = 0; i < fade; i++) s[s.Length - 1 - i] *= (double)i / fade;
        Write(path, s, 0.45);
    }

    // Loops (3 s), a light breeze (redone 2026-11-21: the first one sounded like a storm): airy band noise
    // ~600-2500 Hz, no rumble underneath, swelling gently.
    public static void Glide(string path) {
        int n = 3 * Rate;
        var s = new double[n];
        var rnd = new Random(71);
        var white = new double[n];
        for (int i = 0; i < n; i++) white[i] = rnd.NextDouble() * 2.0 - 1.0;
        double lpA = 0.0, lpB = 0.0;
        for (int pass = 0; pass < 2; pass++)
            for (int i = 0; i < n; i++) {
                lpA += 0.3 * (white[i] - lpA);      // ~2.5 kHz top
                lpB += 0.085 * (lpA - lpB);         // ~600 Hz bottom
                if (pass == 1) {
                    double t = i / (double)Rate;
                    double swell = 0.75 + 0.2 * Math.Sin(2.0 * Math.PI * t / 3.0) + 0.05 * Math.Sin(2.0 * Math.PI * t * 4.0 / 3.0 + 1.0);
                    s[i] += (lpA - lpB) * swell;
                }
            }
        Write(path, s, 0.35);
    }
}
'@
[WingsSounds]::Get((Join-Path $outDir 'S_WingsGet.wav'))
# S_WingFlap / S_WingGlide now come from bought files (make_wings_stock_sounds.ps1, 2026-11-21); the synthesized
# versions stay here, unused: [WingsSounds]::Flap(...), [WingsSounds]::Glide(...).
Get-ChildItem $outDir -Filter 'S_Wing*.wav' | Select-Object Name, Length
