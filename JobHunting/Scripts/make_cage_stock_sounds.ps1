# The birdcage's sounds from bought Audiostock files (the user, 2026-11-22: the synthesized creak "felt wrong", the
# chain like a baby's rattle; "use them, change them as much as you like"), replacing make_cage_sounds.ps1's:
#   SourceArt/Sounds/Stock/  the originals, kept as bought
#     AS_1615686_【環境音】鉄格子の扉を閉じる.wav   1.2 s stereo: a short squeal, the clang at 0.14 s, ringing to 0.7 s
#     AS_62314_ガシャガシャ.mp3                    1.7 s: metal and chain jangling, loudest 0.1-0.5 s (decoded with Blender)
#   S_CageCreak.wav  the door swinging (DoorSound): the gate from 0.06 s, quieter
#   S_CageLock.wav   the door shut on the player: the gate in full, a low thud under its clang for weight
#   S_CageRise.wav   hauled up (~2.5 s): the jangle twice (the second softer, 1 s on), a faint low strain under it
#   S_CageLand.wav   set down: a low thud and clang (synthesized) with the jangle's first burst
# setup_cage_effects.py imports them. Run:
#   powershell -File make_cage_stock_sounds.ps1 [-Downloads <folder with the bought files>]
param([string]$Downloads = (Join-Path $env:USERPROFILE 'Downloads'),
      [string]$Blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe')
$ErrorActionPreference = 'Stop'
$sounds = Join-Path (Split-Path -Parent $PSScriptRoot) 'SourceArt\Sounds'
$stock = Join-Path $sounds 'Stock'
New-Item -ItemType Directory -Force $stock | Out-Null
foreach ($pattern in 'AS_1615686*.wav', 'AS_62314*.mp3') {
  $found = Get-ChildItem $Downloads -Filter $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($found) { Copy-Item $found.FullName (Join-Path $stock $found.Name) -Force }
}
$gateSource = (Get-ChildItem $stock -Filter 'AS_1615686*.wav' | Select-Object -First 1).FullName
$chainSource = (Get-ChildItem $stock -Filter 'AS_62314*.mp3' | Select-Object -First 1).FullName
if (-not $gateSource -or -not $chainSource) { throw "The bought files are not in $Downloads or $stock" }
$chainWav = Join-Path $env:TEMP 'cage_chain_decoded.wav'
& $Blender -b --factory-startup --python (Join-Path $PSScriptRoot 'decode_audio_blender.py') -- $chainSource $chainWav | Select-String 'decoded'
if (-not (Test-Path $chainWav)) { throw 'Decoding the chain failed' }

Add-Type -TypeDefinition @'
using System;
using System.IO;

public static class CageStock {
    const int Rate = 44100;

    // 16-bit PCM WAV at 44.1 kHz, any channel count (mixed down), chunks in any order.
    public static double[] Read(string path) {
        byte[] b = File.ReadAllBytes(path);
        int i = 12, ch = 1, rate = Rate;
        while (i < b.Length - 8) {
            string id = System.Text.Encoding.ASCII.GetString(b, i, 4);
            int len = BitConverter.ToInt32(b, i + 4);
            if (id == "fmt ") { ch = BitConverter.ToInt16(b, i + 10); rate = BitConverter.ToInt32(b, i + 12); }
            if (id == "data") {
                if (rate != Rate) throw new Exception(path + " is not 44.1 kHz");
                int n = len / 2 / ch;
                var s = new double[n];
                for (int k = 0; k < n; k++) {
                    double v = 0.0;
                    for (int c = 0; c < ch; c++) v += BitConverter.ToInt16(b, i + 8 + 2 * (k * ch + c)) / 32768.0;
                    s[k] = v / ch;
                }
                return s;
            }
            i += 8 + len + (len % 2);
        }
        throw new Exception("no data chunk in " + path);
    }

    public static void Write(string path, double[] s, double peakTo) {
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

    // from..to seconds of src, a 5 ms fade in and a fadeOut-second fade out.
    public static double[] Cut(double[] src, double from, double to, double fadeOut) {
        int a = (int)(from * Rate), b = Math.Min(src.Length, (int)(to * Rate));
        var s = new double[b - a];
        int fin = (int)(0.005 * Rate), fout = Math.Max(1, (int)(fadeOut * Rate));
        for (int k = 0; k < s.Length; k++)
            s[k] = src[a + k] * Math.Min(1.0, k / (double)fin) * Math.Min(1.0, (s.Length - 1 - k) / (double)fout);
        return s;
    }

    static double Peak(double[] s) { double p = 1e-9; foreach (double v in s) p = Math.Max(p, Math.Abs(v)); return p; }

    // Adds part (scaled so its peak is level) into s at seconds.
    public static void Mix(double[] s, double[] part, double at, double level) {
        int start = (int)(at * Rate);
        double g = level / Peak(part);
        for (int k = 0; k < part.Length && start + k < s.Length; k++) s[start + k] += part[k] * g;
    }

    public static double[] Silence(double seconds) { return new double[(int)(seconds * Rate)]; }

    public static void Thud(double[] s, double at, double f, double level, double decay) {
        int start = (int)(at * Rate);
        double phase = 0.0;
        for (int i = start; i < s.Length; i++) {
            double t = (i - start) / (double)Rate;
            if (t > decay * 8.0) break;
            phase += 2.0 * Math.PI * f * (1.0 + 0.7 * Math.Exp(-t / 0.02)) / Rate;
            s[i] += level * Math.Min(1.0, t / 0.002) * Math.Sin(phase) * Math.Exp(-t / decay);
        }
    }

    public static void Clang(double[] s, double at, double f, double level, double ring) {
        double[] ratio = { 1.0, 2.43, 4.25 };
        int start = (int)(at * Rate);
        for (int i = start; i < s.Length; i++) {
            double t = (i - start) / (double)Rate;
            if (t > ring * 8.0) break;
            double v = 0.0;
            for (int k = 0; k < ratio.Length; k++) v += Math.Sin(2.0 * Math.PI * f * ratio[k] * t) * Math.Exp(-t * (1.0 + 0.6 * k) / ring) / (1 + k);
            s[i] += level * Math.Min(1.0, t / 0.001) * v;
        }
    }

    // A faint low strain: a deep hum with a soft rush of air, rising a little, fading at both ends.
    public static void Strain(double[] s, double from, double to, double level) {
        var rnd = new Random(173);
        int a = (int)(from * Rate), b = Math.Min(s.Length, (int)(to * Rate));
        double phase = 0.0, lp = 0.0, lp2 = 0.0;
        for (int i = a; i < b; i++) {
            double u = (i - a) / (double)(b - a);
            phase += 2.0 * Math.PI * (55.0 + 10.0 * u) / Rate;
            lp += 0.03 * ((rnd.NextDouble() * 2.0 - 1.0) - lp);
            lp2 += 0.01 * (lp - lp2);
            double env = Math.Sin(Math.PI * u);
            s[i] += level * env * (Math.Sin(phase) + 0.4 * Math.Sin(2.0 * phase) + 3.0 * (lp - lp2));
        }
    }

    public static void FadeEnd(double[] s, double seconds) {
        int fade = (int)(seconds * Rate);
        for (int i = 0; i < fade; i++) s[s.Length - 1 - i] *= (double)i / fade;
    }
}
'@
$gate = [CageStock]::Read($gateSource)
$chain = [CageStock]::Read($chainWav)

[CageStock]::Write((Join-Path $sounds 'S_CageCreak.wav'), [CageStock]::Cut($gate, 0.06, 0.75, 0.12), 0.55)

$lock = [CageStock]::Silence(0.85)
[CageStock]::Mix($lock, [CageStock]::Cut($gate, 0.06, 0.9, 0.15), 0.0, 1.0)
[CageStock]::Thud($lock, 0.08, 60.0, 0.5, 0.07)
[CageStock]::Write((Join-Path $sounds 'S_CageLock.wav'), $lock, 0.9)

$rise = [CageStock]::Silence(2.5)
$jangle = [CageStock]::Cut($chain, 0.02, 1.45, 0.3)
[CageStock]::Mix($rise, $jangle, 0.0, 1.0)
[CageStock]::Mix($rise, $jangle, 1.0, 0.6)
[CageStock]::Strain($rise, 0.0, 2.5, 0.04)
[CageStock]::FadeEnd($rise, 0.5)
[CageStock]::Write((Join-Path $sounds 'S_CageRise.wav'), $rise, 0.7)

$land = [CageStock]::Silence(0.9)
[CageStock]::Thud($land, 0.0, 60.0, 1.0, 0.08)
[CageStock]::Clang($land, 0.0, 410.0, 0.25, 0.12)
[CageStock]::Mix($land, [CageStock]::Cut($chain, 0.08, 0.6, 0.15), 0.02, 0.6)
[CageStock]::FadeEnd($land, 0.2)
[CageStock]::Write((Join-Path $sounds 'S_CageLand.wav'), $land, 0.85)

Remove-Item $chainWav
Get-ChildItem $sounds -Filter 'S_Cage*.wav' | Select-Object Name, Length
Get-ChildItem $stock -Filter 'AS_*' | Select-Object Name, Length
