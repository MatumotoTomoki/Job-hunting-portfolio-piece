# Writes the light shard's pick-up sound into SourceArt/Sounds (mono 16-bit 44.1 kHz), synthesized here (the user,
# 2026-11-21):
#   S_ShardGet.wav  "kiran... riririn": a bright glassy ping, a quick rising arpeggio of bell notes (C6 E6 G6 C7) and
#                   an airy shimmer that floats away (~1.8 s). Played with PlaySoundAtLocation, so it outlives the
#                   shard (destroyed 0.9 s after it is taken).
# setup_shard_effects.py imports it. Run: powershell -File make_shard_sounds.ps1
$ErrorActionPreference = 'Stop'
$outDir = Join-Path (Split-Path -Parent $PSScriptRoot) 'SourceArt\Sounds'
New-Item -ItemType Directory -Force $outDir | Out-Null

Add-Type -TypeDefinition @'
using System;
using System.IO;

public static class ShardSounds {
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
        double[] ratios = { 1.0, 2.0, 3.01, 4.17 };
        double[] amps = { 1.0, 0.3, 0.12, 0.06 };
        for (int i = start; i < s.Length; i++) {
            double t = (i - start) / (double)Rate, v = 0.0;
            for (int k = 0; k < ratios.Length; k++) v += amps[k] * Math.Sin(2.0 * Math.PI * f * ratios[k] * t) * Math.Exp(-t / (ring / (1.0 + 0.7 * k)));
            s[i] += gain * Math.Min(1.0, t / 0.002) * v;
        }
    }

    public static void Get(string path) {
        var s = new double[(int)(1.9 * Rate)];
        var rnd = new Random(53);
        // The glass ping: inharmonic high partials, quick and bright.
        double[] glass = { 2637.0, 3951.0, 5274.0, 6643.0 };
        for (int i = 0; i < (int)(0.8 * Rate); i++) {
            double t = i / (double)Rate, v = 0.0;
            for (int k = 0; k < glass.Length; k++) v += Math.Sin(2.0 * Math.PI * glass[k] * t + k) * Math.Exp(-t / (0.25 / (1.0 + k))) / (1.0 + k);
            s[i] += 0.5 * Math.Min(1.0, t / 0.001) * v;
        }
        // The arpeggio, rising.
        double[] notes = { 1046.5, 1318.5, 1568.0, 2093.0 };
        for (int k = 0; k < notes.Length; k++) Bell(s, 0.06 + 0.07 * k, notes[k], 0.32 + 0.04 * k, 0.6 + 0.15 * k);
        // The shimmer: soft high noise with a slow tremolo, swelling in and fading away.
        double lpA = 0.0, lpB = 0.0;
        for (int i = 0; i < s.Length; i++) {
            double t = i / (double)Rate, w = rnd.NextDouble() * 2.0 - 1.0;
            lpA += 0.5 * (w - lpA);
            lpB += 0.12 * (lpA - lpB);
            double env = Math.Min(1.0, t / 0.25) * Math.Exp(-Math.Max(0.0, t - 0.25) / 0.45);
            double trem = 0.6 + 0.4 * Math.Sin(2.0 * Math.PI * 9.0 * t);
            s[i] += 0.12 * (lpA - lpB) * env * trem;
        }
        // A few twinkles in the tail.
        for (int c = 0; c < 6; c++) Bell(s, 0.45 + 0.9 * rnd.NextDouble(), 3000.0 + 2000.0 * rnd.NextDouble(), 0.05, 0.12);
        int fade = (int)(0.2 * Rate);
        for (int i = 0; i < fade; i++) s[s.Length - 1 - i] *= (double)i / fade;
        Write(path, s, 0.8);
    }
}
'@
[ShardSounds]::Get((Join-Path $outDir 'S_ShardGet.wav'))
Get-Item (Join-Path $outDir 'S_ShardGet.wav') | Select-Object Name, Length
