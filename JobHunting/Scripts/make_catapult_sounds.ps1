# Writes the steam catapult's sounds into SourceArt/Sounds (mono 16-bit 44.1 kHz), synthesized here:
#   S_CatapultCharge.wav  1.5 s: pressure building - a hiss that swells and climbs, a low rumble rising in pitch and
#                         a few metal creaks; it is still rising at its end (the launch cuts in).
#   S_CatapultBoom.wav    1.8 s: the launch - a deep thump falling in pitch, a blast of noise and a long whoosh
#                         sweeping down.
#   S_CloudLand.wav       1.0 s: landing on area 3's cloud harbour - a soft, muffled puff and a light thud.
# BP_SteamCatapult and BP_SkyLanding play them (setup_steam_catapult.py). Run: powershell -File make_catapult_sounds.ps1
$ErrorActionPreference = 'Stop'
$outDir = Join-Path (Split-Path -Parent $PSScriptRoot) 'SourceArt\Sounds'
New-Item -ItemType Directory -Force $outDir | Out-Null

Add-Type -TypeDefinition @'
using System;
using System.IO;

public static class CatapultSounds {
    const int Rate = 44100;

    static void Write(string path, double[] s, double peakTo, bool fadeOut) {
        if (fadeOut) {
            int n = (int)(0.12 * Rate);
            for (int i = 0; i < n; i++) s[s.Length - 1 - i] *= (double)i / n;
        }
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

    public static void Charge(string path) {
        var s = new double[(int)(1.5 * Rate)];
        var rnd = new Random(21);
        double lpA = 0.0, lpB = 0.0, phase = 0.0;
        for (int i = 0; i < s.Length; i++) {
            double t = i / (double)Rate, k = t / 1.5;
            double white = rnd.NextDouble() * 2.0 - 1.0;
            // hiss: high-passed noise whose brightness and loudness climb
            lpA += (0.25 - 0.17 * k) * (white - lpA);
            double hiss = (white - lpA) * (0.15 + 0.85 * k * k);
            // rumble: a low tone rising from 45 to 110 Hz, with a lowpassed noise bed
            phase += 2.0 * Math.PI * (45.0 + 65.0 * k * k) / Rate;
            lpB += 0.01 * (white - lpB);
            double rumble = (0.6 * Math.Sin(phase) + 0.5 * Math.Sin(2.0 * phase) * 0.3 + lpB * 6.0) * (0.3 + 0.7 * k);
            s[i] = 0.8 * hiss + 0.7 * rumble;
        }
        // three metal creaks
        foreach (double at in new[] { 0.25, 0.7, 1.1 }) {
            int start = (int)(at * Rate);
            double f = 600.0 + rnd.NextDouble() * 300.0;
            for (int j = 0; j < (int)(0.18 * Rate) && start + j < s.Length; j++) {
                double t = j / (double)Rate;
                s[start + j] += 0.35 * Math.Sin(2.0 * Math.PI * (f + 400.0 * t) * t) * Math.Exp(-t / 0.05) * (0.6 + 0.4 * Math.Sin(t * 180.0));
            }
        }
        Write(path, s, 0.85, false);
    }

    public static void Boom(string path) {
        var s = new double[(int)(1.8 * Rate)];
        var rnd = new Random(23);
        double phase = 0.0, lp = 0.0, bp1 = 0.0, bp2 = 0.0;
        for (int i = 0; i < s.Length; i++) {
            double t = i / (double)Rate;
            double white = rnd.NextDouble() * 2.0 - 1.0;
            phase += 2.0 * Math.PI * (38.0 + 70.0 * Math.Exp(-t / 0.08)) / Rate;
            double thump = Math.Sin(phase) * Math.Exp(-t / 0.35);
            lp += 0.3 * (white - lp);
            double blast = lp * Math.Exp(-t / 0.12);
            // whoosh: band-passed noise whose band sweeps down
            double cut = 0.25 * Math.Exp(-t / 0.6) + 0.02;
            bp1 += cut * (white - bp1);
            bp2 += cut * (bp1 - bp2);
            double whoosh = (bp1 - bp2) * Math.Min(1.0, t / 0.05) * Math.Exp(-t / 0.7);
            s[i] = 1.2 * thump + 0.9 * blast + 2.5 * whoosh;
        }
        Write(path, s, 0.95, true);
    }

    public static void Land(string path) {
        var s = new double[(int)(1.0 * Rate)];
        var rnd = new Random(25);
        double lp = 0.0, lp2 = 0.0, phase = 0.0;
        for (int i = 0; i < s.Length; i++) {
            double t = i / (double)Rate;
            double white = rnd.NextDouble() * 2.0 - 1.0;
            lp += 0.06 * (white - lp);
            lp2 += 0.06 * (lp - lp2);
            double puff = lp2 * 8.0 * Math.Min(1.0, t / 0.01) * Math.Exp(-t / 0.22);
            phase += 2.0 * Math.PI * (70.0 + 40.0 * Math.Exp(-t / 0.05)) / Rate;
            double thud = Math.Sin(phase) * Math.Exp(-t / 0.12) * 0.6;
            s[i] = puff + thud;
        }
        Write(path, s, 0.8, true);
    }
}
'@
[CatapultSounds]::Charge((Join-Path $outDir 'S_CatapultCharge.wav'))
[CatapultSounds]::Boom((Join-Path $outDir 'S_CatapultBoom.wav'))
[CatapultSounds]::Land((Join-Path $outDir 'S_CloudLand.wav'))
Get-ChildItem $outDir -Filter 'S_Catapult*.wav' | Select-Object Name, Length
Get-ChildItem $outDir -Filter 'S_CloudLand.wav' | Select-Object Name, Length
