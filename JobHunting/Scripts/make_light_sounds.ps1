# Writes the light pillar's sounds (area 3 -> 4; the user, 2026-11-20) into SourceArt/Sounds (mono 16-bit 44.1 kHz):
#   S_BeamDescend.wav  2.4 s: the pillar coming down - soft bell tones climbing an arpeggio (C E G B D), each ringing
#                      on, over a quiet swelling pad.
#   S_BeamAscend.wav   4.0 s: rising into the light - a warm detuned major chord swelling in slowly, its pitch lifting
#                      a little, with a faint airy shimmer on top.
#   S_BeamFade.wav     3.4 s: the light dying in area 4 - a soft minor chord (A C E) sinking a little and fading away.
# BP_LightGate and BP_LightArrival play them (setup_light_transition.py).  powershell -File make_light_sounds.ps1
$ErrorActionPreference = 'Stop'
$outDir = Join-Path (Split-Path -Parent $PSScriptRoot) 'SourceArt\Sounds'
New-Item -ItemType Directory -Force $outDir | Out-Null
Add-Type -TypeDefinition @'
using System;
using System.IO;
public static class LightSounds {
    const int Rate = 44100;
    static void Write(string path, double[] s, double peakTo) {
        int fade = (int)(0.2 * Rate);
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
    // A soft pad note: a few detuned sines, slow attack.
    static double Pad(double f, double t, double attack) {
        double env = Math.Min(1.0, t / attack);
        env = env * env * (3.0 - 2.0 * env);
        return env * (Math.Sin(2 * Math.PI * f * t) + 0.6 * Math.Sin(2 * Math.PI * f * 1.003 * t + 1.0) + 0.6 * Math.Sin(2 * Math.PI * f * 0.997 * t + 2.0)
                      + 0.2 * Math.Sin(2 * Math.PI * f * 2.0 * t));
    }
    static double Bell(double f, double t) {
        if (t < 0) return 0.0;
        double a = Math.Min(1.0, t / 0.004);
        return a * (Math.Sin(2 * Math.PI * f * t) * Math.Exp(-t / 1.1) + 0.4 * Math.Sin(2 * Math.PI * f * 2.0 * t) * Math.Exp(-t / 0.6)
                    + 0.2 * Math.Sin(2 * Math.PI * f * 3.01 * t) * Math.Exp(-t / 0.35));
    }
    public static void Descend(string path) {
        var s = new double[(int)(2.4 * Rate)];
        double[] notes = { 523.25, 659.25, 783.99, 987.77, 1174.66 };
        for (int i = 0; i < s.Length; i++) {
            double t = i / (double)Rate, v = 0.0;
            for (int k = 0; k < notes.Length; k++) v += 0.5 * Bell(notes[k], t - 0.16 * k);
            v += 0.12 * (Pad(261.63, t, 1.2) + Pad(392.0, t, 1.2));
            s[i] = v;
        }
        Write(path, s, 0.7);
    }
    public static void Ascend(string path) {
        var s = new double[(int)(4.0 * Rate)];
        var rnd = new Random(41);
        double lp = 0.0;
        double[] chord = { 261.63, 329.63, 392.0, 523.25 };
        double[] phase = new double[chord.Length * 3];
        for (int i = 0; i < s.Length; i++) {
            double t = i / (double)Rate, lift = 1.0 + 0.06 * Math.Min(1.0, t / 4.0);
            double env = Math.Min(1.0, t / 2.2); env = env * env * (3.0 - 2.0 * env);
            double v = 0.0;
            for (int k = 0; k < chord.Length; k++)
                for (int d = 0; d < 3; d++) {
                    phase[k * 3 + d] += 2 * Math.PI * chord[k] * lift * (1.0 + (d - 1) * 0.003) / Rate;
                    v += Math.Sin(phase[k * 3 + d]) * (d == 1 ? 1.0 : 0.6);
                }
            double w = rnd.NextDouble() * 2.0 - 1.0;
            lp += 0.3 * (w - lp);
            double air = (w - lp) * 0.25 * env;
            s[i] = env * v * 0.25 + air;
        }
        Write(path, s, 0.65);
    }
    public static void Fade(string path) {
        var s = new double[(int)(3.4 * Rate)];
        double[] chord = { 220.0, 261.63, 329.63, 440.0 };
        double[] phase = new double[chord.Length * 3];
        for (int i = 0; i < s.Length; i++) {
            double t = i / (double)Rate, sink = 1.0 - 0.04 * Math.Min(1.0, t / 3.4);
            double env = Math.Min(1.0, t / 0.6) * Math.Exp(-Math.Max(0.0, t - 0.6) / 1.4);
            double v = 0.0;
            for (int k = 0; k < chord.Length; k++)
                for (int d = 0; d < 3; d++) {
                    phase[k * 3 + d] += 2 * Math.PI * chord[k] * sink * (1.0 + (d - 1) * 0.003) / Rate;
                    v += Math.Sin(phase[k * 3 + d]) * (d == 1 ? 1.0 : 0.6);
                }
            s[i] = env * v;
        }
        Write(path, s, 0.6);
    }
}
'@
[LightSounds]::Descend((Join-Path $outDir 'S_BeamDescend.wav'))
[LightSounds]::Ascend((Join-Path $outDir 'S_BeamAscend.wav'))
[LightSounds]::Fade((Join-Path $outDir 'S_BeamFade.wav'))
Get-ChildItem $outDir -Filter 'S_Beam*.wav' | Select-Object Name, Length
