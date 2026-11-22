# Writes the timed platform's sounds into SourceArt/Sounds (mono 16-bit 44.1 kHz), synthesized here (the user, 2026-11-22).
# They play every cycle on every timed platform, so both are soft and short:
#   S_TimedVanish.wav  "shuwaa": a hiss of fine glitter thinning out under a few falling glassy notes (~0.7 s; the
#                      fade is 0.5 s)
#   S_TimedAppear.wav  "kirin": solid again - a quick bright glitter and two rising notes at once (~0.7 s)
# setup_timed_effects.py imports them. Run: powershell -File make_timed_sounds.ps1
$ErrorActionPreference = 'Stop'
$outDir = Join-Path (Split-Path -Parent $PSScriptRoot) 'SourceArt\Sounds'
New-Item -ItemType Directory -Force $outDir | Out-Null

Add-Type -TypeDefinition @'
using System;
using System.IO;

public static class TimedSounds {
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
            s[i] += gain * Math.Min(1.0, t / 0.004) * (Math.Sin(2.0 * Math.PI * f * t) * Math.Exp(-t / ring) + 0.2 * Math.Sin(2.0 * Math.PI * f * 2.76 * t) * Math.Exp(-t / (ring * 0.4)));
        }
    }

    // Glitter: bright noise (high-passed) made grainy by random tiny swells, shaped by env(u), u = 0..1.
    static void Glitter(double[] s, Random rnd, double gain, Func<double, double> env) {
        double prev = 0.0, lp = 0.0, grain = 0.0;
        for (int i = 0; i < s.Length; i++) {
            double w = rnd.NextDouble() * 2.0 - 1.0;
            double hp = w - prev; prev = w;
            lp += 0.5 * (hp - lp);
            if (rnd.NextDouble() < 0.002) grain = 1.0;
            grain *= 0.9985;
            s[i] += gain * lp * (0.35 + 0.65 * grain) * env(i / (double)s.Length);
        }
    }

    public static void Vanish(string path) {
        var s = new double[(int)(0.7 * Rate)];
        var rnd = new Random(113);
        Glitter(s, rnd, 0.6, u => Math.Min(1.0, u / 0.03) * Math.Pow(1.0 - u, 1.5));
        double[] notes = { 2637.0, 2093.0, 1760.0, 1318.5 };
        for (int k = 0; k < notes.Length; k++) Bell(s, 0.02 + 0.1 * k, notes[k], 0.12 - 0.015 * k, 0.25);
        int fade = (int)(0.12 * Rate);
        for (int i = 0; i < fade; i++) s[s.Length - 1 - i] *= (double)i / fade;
        Write(path, s, 0.4);
    }

    // (2026-11-22, the user: play it as the platform can be stood on again, so it marks that moment - no swell first.)
    public static void Appear(string path) {
        var s = new double[(int)(0.7 * Rate)];
        var rnd = new Random(127);
        Glitter(s, rnd, 0.5, u => Math.Min(1.0, u / 0.01) * Math.Pow(1.0 - u, 2.0));
        double[] notes = { 1760.0, 2637.0, 3520.0 };
        for (int k = 0; k < notes.Length; k++) Bell(s, 0.005 + 0.05 * k, notes[k], 0.13 - 0.02 * k, 0.3);
        int fade = (int)(0.12 * Rate);
        for (int i = 0; i < fade; i++) s[s.Length - 1 - i] *= (double)i / fade;
        Write(path, s, 0.4);
    }
}
'@
[TimedSounds]::Vanish((Join-Path $outDir 'S_TimedVanish.wav'))
[TimedSounds]::Appear((Join-Path $outDir 'S_TimedAppear.wav'))
Get-ChildItem $outDir -Filter 'S_Timed*.wav' | Select-Object Name, Length
