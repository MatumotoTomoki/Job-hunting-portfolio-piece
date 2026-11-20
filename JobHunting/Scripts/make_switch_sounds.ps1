# Writes the toggle switch's and the switch blocks' sounds into SourceArt/Sounds (mono 16-bit 44.1 kHz), synthesized
# here (the user, 2026-11-20):
#   S_SwitchClick.wav  "kachi... pon": the button snaps down and a bright two-note chime rings out (the colour flips).
#   S_BlockForm.wav    "shuin": a rising airy sweep and a rising glassy tone that settles into a short shimmer as the
#                      block turns solid.
#   S_BlockVanish.wav  "fu": a soft falling puff of air and a sinking tone as the block turns to a ghost.
# setup_switch_effects.py imports them. Run: powershell -File make_switch_sounds.ps1
$ErrorActionPreference = 'Stop'
$outDir = Join-Path (Split-Path -Parent $PSScriptRoot) 'SourceArt\Sounds'
New-Item -ItemType Directory -Force $outDir | Out-Null

Add-Type -TypeDefinition @'
using System;
using System.IO;

public static class SwitchSounds {
    const int Rate = 44100;

    static void Fade(double[] s, double seconds) {
        int n = (int)(seconds * Rate);
        for (int i = 0; i < n && i < s.Length; i++) s[s.Length - 1 - i] *= (double)i / n;
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

    // A bell-ish note: a sine with a few soft partials, quick attack, ringing out.
    static void Bell(double[] s, double at, double f, double gain, double ring) {
        int start = (int)(at * Rate);
        double[] ratios = { 1.0, 2.0, 3.01, 4.2 };
        double[] amps = { 1.0, 0.35, 0.15, 0.08 };
        for (int i = start; i < s.Length; i++) {
            double t = (i - start) / (double)Rate, v = 0.0;
            for (int k = 0; k < ratios.Length; k++) v += amps[k] * Math.Sin(2.0 * Math.PI * f * ratios[k] * t) * Math.Exp(-t / (ring / (1.0 + k)));
            s[i] += gain * Math.Min(1.0, t / 0.003) * v;
        }
    }

    // "kachi... pon": a plastic-metal snap, then E6 and B6 a breath apart.
    public static void Click(string path) {
        var s = new double[(int)(0.9 * Rate)];
        var rnd = new Random(41);
        double hp = 0.0;
        for (int j = 0; j < (int)(0.05 * Rate); j++) {
            double t = j / (double)Rate, w = rnd.NextDouble() * 2.0 - 1.0;
            hp += 0.35 * (w - hp);
            s[j] += (w - hp) * Math.Exp(-t / 0.003) * 1.2 + 0.5 * Math.Sin(2.0 * Math.PI * 3100.0 * t) * Math.Exp(-t / 0.008)
                    + 0.4 * Math.Sin(2.0 * Math.PI * 180.0 * t) * Math.Exp(-t / 0.015);
        }
        Bell(s, 0.04, 1318.5, 0.45, 0.35);
        Bell(s, 0.11, 1975.5, 0.4, 0.45);
        Fade(s, 0.1);
        Write(path, s, 0.85);
    }

    // "shuin": band noise sweeping up (filter opening 0 -> 0.45 s), a glide 400 -> 1200 Hz, then a shimmer of three
    // high notes.
    public static void Form(string path) {
        var s = new double[(int)(0.9 * Rate)];
        var rnd = new Random(43);
        double lpA = 0.0, lpB = 0.0, phase = 0.0;
        for (int i = 0; i < s.Length; i++) {
            double t = i / (double)Rate;
            double rise = Math.Min(1.0, t / 0.45);
            double top = 0.02 + 0.3 * rise * rise, bottom = top * 0.25;
            double w = rnd.NextDouble() * 2.0 - 1.0;
            lpA += top * (w - lpA);
            lpB += bottom * (lpA - lpB);
            double env = Math.Sin(Math.PI * Math.Min(1.0, t / 0.55)) * (t < 0.55 ? 1.0 : 0.0);
            s[i] += 1.6 * (lpA - lpB) * env;
            double f = 400.0 + 800.0 * (1.0 - Math.Pow(1.0 - rise, 2.0));
            phase += 2.0 * Math.PI * f / Rate;
            double toneEnv = Math.Min(1.0, t / 0.1) * Math.Exp(-Math.Max(0.0, t - 0.4) / 0.12);
            s[i] += 0.35 * (Math.Sin(phase) + 0.3 * Math.Sin(2.0 * phase)) * toneEnv;
        }
        Bell(s, 0.40, 2349.3, 0.18, 0.3);
        Bell(s, 0.45, 2793.8, 0.14, 0.3);
        Bell(s, 0.50, 3520.0, 0.1, 0.25);
        Fade(s, 0.12);
        Write(path, s, 0.8);
    }

    // "fu": a soft low puff of air with a closing filter, and a tone sinking 700 -> 250 Hz.
    public static void Vanish(string path) {
        var s = new double[(int)(0.5 * Rate)];
        var rnd = new Random(47);
        double lpA = 0.0, lpB = 0.0, phase = 0.0;
        for (int i = 0; i < s.Length; i++) {
            double t = i / (double)Rate;
            double close = Math.Exp(-t / 0.12);
            double top = 0.015 + 0.12 * close, bottom = top * 0.3;
            double w = rnd.NextDouble() * 2.0 - 1.0;
            lpA += top * (w - lpA);
            lpB += bottom * (lpA - lpB);
            double env = Math.Min(1.0, t / 0.02) * Math.Exp(-t / 0.14);
            s[i] += 2.2 * (lpA - lpB) * env;
            double f = 250.0 + 450.0 * Math.Exp(-t / 0.1);
            phase += 2.0 * Math.PI * f / Rate;
            s[i] += 0.25 * Math.Sin(phase) * Math.Min(1.0, t / 0.01) * Math.Exp(-t / 0.1);
        }
        Fade(s, 0.08);
        Write(path, s, 0.65);
    }
}
'@
[SwitchSounds]::Click((Join-Path $outDir 'S_SwitchClick.wav'))
[SwitchSounds]::Form((Join-Path $outDir 'S_BlockForm.wav'))
[SwitchSounds]::Vanish((Join-Path $outDir 'S_BlockVanish.wav'))
Get-ChildItem $outDir -Filter 'S_*.wav' | Where-Object { $_.Name -match 'SwitchClick|BlockForm|BlockVanish' } | Select-Object Name, Length
