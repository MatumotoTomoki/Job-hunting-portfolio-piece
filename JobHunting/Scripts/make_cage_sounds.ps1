# Writes the birdcage's sounds into SourceArt/Sounds (mono 16-bit 44.1 kHz), synthesized here (the user, 2026-11-22):
#   S_CageCreak.wav  "kiii": the brass door's hinge creaking as it swings open or shut (~0.9 s)
#   S_CageLock.wav   "gashan": the door slamming shut on the player and its latch dropping (~0.7 s)
#   S_CageRise.wav   "gachi, gachi...": the heavy chain snapping taut and a winch hauling the cage up into the dark,
#                    links knocking, a low strain under it (~2.4 s; remade 2026-11-22 - the first was a baby's rattle)
#   S_CageLand.wav   "dosun": the cage setting down, a clang and the chain settling (~0.9 s)
# Superseded 2026-11-22 by make_cage_stock_sounds.ps1 (bought files; the user found these synthesized ones wrong).
# Running this would overwrite those - run make_cage_stock_sounds.ps1 instead. Kept for reference.
# setup_cage_effects.py imports them. Run: powershell -File make_cage_sounds.ps1
$ErrorActionPreference = 'Stop'
$outDir = Join-Path (Split-Path -Parent $PSScriptRoot) 'SourceArt\Sounds'
New-Item -ItemType Directory -Force $outDir | Out-Null

Add-Type -TypeDefinition @'
using System;
using System.IO;

public static class CageSounds {
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

    // Struck metal: inharmonic partials, the higher dying faster.
    static void Clang(double[] s, double at, double f, double gain, double ring) {
        double[] ratio = { 1.0, 2.43, 4.25, 6.53, 8.9 };
        double[] level = { 1.0, 0.7, 0.5, 0.35, 0.2 };
        int start = (int)(at * Rate);
        for (int i = start; i < s.Length; i++) {
            double t = (i - start) / (double)Rate;
            if (t > ring * 8.0) break;
            double v = 0.0;
            for (int k = 0; k < ratio.Length; k++) v += level[k] * Math.Sin(2.0 * Math.PI * f * ratio[k] * t) * Math.Exp(-t * (1.0 + 0.6 * k) / ring);
            s[i] += gain * Math.Min(1.0, t / 0.0008) * v;
        }
    }

    // A heavy iron chain link knocking (2026-11-22: the first, tiny high pings sounded like a baby's rattle): a dull
    // low clank with a short noisy hit, inharmonic, dying fast.
    static void Link(double[] s, Random rnd, double at, double gain) {
        int start = (int)(at * Rate);
        double f = 450.0 + 650.0 * rnd.NextDouble(), f2 = f * (2.3 + 0.4 * rnd.NextDouble()), f3 = f * 3.9;
        double decay = 0.025 + 0.025 * rnd.NextDouble(), lp = 0.0;
        for (int j = 0; start + j < s.Length; j++) {
            double t = j / (double)Rate;
            if (t > decay * 6.0) break;
            lp += 0.25 * ((rnd.NextDouble() * 2.0 - 1.0) - lp);
            double hit = lp * Math.Exp(-t / 0.004);
            s[start + j] += gain * (Math.Sin(2.0 * Math.PI * f * t) + 0.5 * Math.Sin(2.0 * Math.PI * f2 * t) * Math.Exp(-t / (decay * 0.5))
                                    + 0.2 * Math.Sin(2.0 * Math.PI * f3 * t) * Math.Exp(-t / (decay * 0.3)) + 1.5 * hit) * Math.Exp(-t / decay);
        }
    }

    // The winch's pawl dropping into the next tooth: a hard short "gachi".
    static void Pawl(double[] s, Random rnd, double at, double gain) {
        Clang(s, at, 260.0 + 20.0 * rnd.NextDouble(), gain, 0.03);
        Link(s, rnd, at + 0.002, gain * 0.8);
    }

    static void Thud(double[] s, double at, double f, double gain, double decay) {
        int start = (int)(at * Rate);
        double phase = 0.0;
        for (int i = start; i < s.Length; i++) {
            double t = (i - start) / (double)Rate;
            if (t > decay * 8.0) break;
            phase += 2.0 * Math.PI * f * (1.0 + 0.7 * Math.Exp(-t / 0.02)) / Rate;
            s[i] += gain * Math.Min(1.0, t / 0.002) * Math.Sin(phase) * Math.Exp(-t / decay);
        }
    }

    // A hinge creak: a buzzy tone sliding in pitch, driven by stick-slip pulses.
    public static void Creak(string path) {
        var s = new double[(int)(0.9 * Rate)];
        var rnd = new Random(151);
        double phase = 0.0, pulse = 0.0, lp = 0.0;
        for (int i = 0; i < s.Length; i++) {
            double t = i / (double)Rate, u = t / 0.9;
            double f = 380.0 + 160.0 * Math.Sin(Math.PI * u) + 25.0 * Math.Sin(2.0 * Math.PI * 3.0 * t);
            phase += 2.0 * Math.PI * f / Rate;
            if (rnd.NextDouble() < 45.0 / Rate) pulse = 1.0;
            pulse *= 0.9993;
            double tone = Math.Sin(phase) + 0.6 * Math.Sin(2.0 * phase + 0.3) + 0.4 * Math.Sin(3.0 * phase) + 0.25 * Math.Sin(5.0 * phase);
            lp += 0.3 * (tone - lp);
            double env = Math.Min(1.0, t / 0.05) * Math.Min(1.0, (0.9 - t) / 0.2);
            s[i] += lp * env * (0.35 + 0.65 * pulse);
        }
        FadeEnd(s, 0.1);
        Write(path, s, 0.45);
    }

    public static void Lock(string path) {
        var s = new double[(int)(0.7 * Rate)];
        var rnd = new Random(157);
        Thud(s, 0.0, 90.0, 0.6, 0.05);
        Clang(s, 0.0, 520.0, 0.5, 0.18);
        Clang(s, 0.004, 733.0, 0.3, 0.12);
        Clang(s, 0.13, 1450.0, 0.25, 0.05);   // the latch
        for (int k = 0; k < 3; k++) Link(s, rnd, 0.03 + 0.2 * rnd.NextDouble(), 0.12);
        FadeEnd(s, 0.15);
        Write(path, s, 0.8);
    }

    public static void Rise(string path) {
        var s = new double[(int)(2.4 * Rate)];
        var rnd = new Random(163);
        // (2026-11-22, remade heavy: iron chain and a winch, not a rattle.)
        Thud(s, 0.0, 70.0, 0.7, 0.08);
        Clang(s, 0.0, 240.0, 0.4, 0.12);      // the chain snapping taut
        // The winch: a pawl clack every ~0.13 s, slowing a little as the cage gets heavy on it.
        double at = 0.05;
        while (at < 2.2) {
            Pawl(s, rnd, at, 0.35 * Math.Max(0.0, 1.0 - at / 2.4));
            at += 0.13 + 0.03 * at / 2.2;
        }
        // Links knocking now and then as the chain sways.
        at = 0.08;
        while (at < 2.1) {
            Link(s, rnd, at, (0.12 + 0.1 * rnd.NextDouble()) * Math.Max(0.0, 1.0 - at / 2.3));
            at += 0.05 + 0.12 * rnd.NextDouble();
        }
        // A low groan of strain underneath, and the air as it goes up.
        double a = 0.0, b = 0.0, phase = 0.0;
        for (int i = 0; i < s.Length; i++) {
            double t = i / (double)Rate, u = t / 2.4;
            phase += 2.0 * Math.PI * (55.0 + 10.0 * u) / Rate;
            double env = Math.Min(1.0, t / 0.2) * Math.Max(0.0, 1.0 - u);
            s[i] += 0.12 * env * (Math.Sin(phase) + 0.4 * Math.Sin(2.0 * phase));
            a += 0.03 * ((rnd.NextDouble() * 2.0 - 1.0) - a);
            b += 0.01 * (a - b);
            s[i] += 0.6 * (a - b) * env;
        }
        FadeEnd(s, 0.6);
        Write(path, s, 0.6);
    }

    public static void Land(string path) {
        var s = new double[(int)(0.9 * Rate)];
        var rnd = new Random(167);
        Thud(s, 0.0, 60.0, 1.0, 0.08);
        Clang(s, 0.0, 410.0, 0.3, 0.15);
        double at = 0.04;
        while (at < 0.6) {
            Link(s, rnd, at, 0.2 * (1.0 - at / 0.6));
            at += 0.05 + 0.08 * rnd.NextDouble();
        }
        FadeEnd(s, 0.2);
        Write(path, s, 0.8);
    }
}
'@
[CageSounds]::Creak((Join-Path $outDir 'S_CageCreak.wav'))
[CageSounds]::Lock((Join-Path $outDir 'S_CageLock.wav'))
[CageSounds]::Rise((Join-Path $outDir 'S_CageRise.wav'))
[CageSounds]::Land((Join-Path $outDir 'S_CageLand.wav'))
Get-ChildItem $outDir -Filter 'S_Cage*.wav' | Select-Object Name, Length
