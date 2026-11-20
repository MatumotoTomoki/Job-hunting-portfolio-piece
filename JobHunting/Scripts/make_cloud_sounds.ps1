# Writes the vanishing cloud's sounds into SourceArt/Sounds (mono 16-bit 44.1 kHz), synthesized here:
#   S_CloudPoof.wav  0.7 s: the cloud vanishing - a soft, muffled airy "poof" (softened 2026-11-19: slower attack,
#                    darker, no tonal thump or shimmer).
#   S_CloudForm.wav  0.9 s: the cloud coming back - a breathy swell rising in, ending in a gentle soft puff.
# BP_VanishCloud plays them (setup_vanish_cloud_look.py), spatialized so far clouds stay quiet.
#   powershell -File make_cloud_sounds.ps1
$ErrorActionPreference = 'Stop'
$outDir = Join-Path (Split-Path -Parent $PSScriptRoot) 'SourceArt\Sounds'
New-Item -ItemType Directory -Force $outDir | Out-Null
Add-Type -TypeDefinition @'
using System;
using System.IO;
public static class CloudSounds {
    const int Rate = 44100;
    static void Write(string path, double[] s, double peakTo) {
        int fade = (int)(0.08 * Rate);
        for (int i = 0; i < fade; i++) s[s.Length - 1 - i] *= (double)i / fade;
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
    public static void Poof(string path) {
        var s = new double[(int)(0.7 * Rate)];
        var rnd = new Random(31);
        double a = 0.0, b = 0.0, phase = 0.0;
        for (int i = 0; i < s.Length; i++) {
            double t = i / (double)Rate, w = rnd.NextDouble() * 2.0 - 1.0;
            double cut = 0.02 + 0.045 * Math.Exp(-t / 0.1);       // opens a little, then closes: a soft "po-of" (softened 2026-11-19)
            a += cut * (w - a); b += cut * (a - b);
            double puff = b * 7.0 * Math.Min(1.0, t / 0.03) * Math.Exp(-t / 0.2);
            phase += 2.0 * Math.PI * (180.0 - 80.0 * Math.Min(1.0, t / 0.2)) / Rate;
            double body = Math.Sin(phase) * Math.Exp(-t / 0.07) * 0.0;   // (no tonal thump: too hard)
            double shimmer = (Math.Sin(2.0 * Math.PI * 2900.0 * t) + Math.Sin(2.0 * Math.PI * 4100.0 * t)) * 0.0 * Math.Exp(-t / 0.18) * Math.Min(1.0, t / 0.03);   // (no shimmer: too bright)
            s[i] = puff + body + shimmer;
        }
        Write(path, s, 0.75);
    }
    public static void Form(string path) {
        var s = new double[(int)(0.9 * Rate)];
        var rnd = new Random(33);
        double a = 0.0, b = 0.0;
        for (int i = 0; i < s.Length; i++) {
            double t = i / (double)Rate, w = rnd.NextDouble() * 2.0 - 1.0;
            double k = Math.Min(1.0, t / 0.6);
            double cut = 0.012 + 0.035 * k;                        // brightening a little as it gathers (softened 2026-11-19)
            a += cut * (w - a); b += cut * (a - b);
            double swell = b * 6.0 * k * k * (t < 0.6 ? 1.0 : Math.Exp(-(t - 0.6) / 0.08));
            double settle = t > 0.6 ? b * 4.0 * Math.Exp(-(t - 0.6) / 0.18) : 0.0;
            s[i] = swell + settle;
        }
        Write(path, s, 0.6);
    }
}
'@
[CloudSounds]::Poof((Join-Path $outDir 'S_CloudPoof.wav'))
[CloudSounds]::Form((Join-Path $outDir 'S_CloudForm.wav'))
Get-ChildItem $outDir -Filter 'S_Cloud*.wav' | Select-Object Name, Length
