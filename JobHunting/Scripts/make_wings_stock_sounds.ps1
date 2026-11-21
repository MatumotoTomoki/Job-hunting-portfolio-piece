# The wings' spreading sounds from bought Audiostock files (the user, 2026-11-21: "a basa first, then the wind
# cutting past"), replacing the synthesized S_WingFlap / S_WingGlide of make_wings_sounds.ps1:
#   SourceArt/Sounds/Stock/  the originals, kept as bought
#     AS_1663144_羽を広げる（バサッ）15.wav          1.5 s, mono 44.1 kHz
#     AS_56501_フォァァァ。ジャンプ・舞い降りる音.mp3   2.9 s, decoded with Blender (decode_audio_blender.py)
#   S_WingFlap.wav   the basa, its silent lead-in (first 0.08 s) cut, ending by 1.0 s; peak 0.85
#   S_WingGlide.wav  loops (1.6 s; the user: "loop the fwaaa part"): the "fwoaaa" from 0.45 s, its loudness evened out
#                    and its seam crossfaded; peak 0.7. BP_Wings fades it in over 0.6 s as the wings spread (so it
#                    rises after the basa) and out over 0.4 s as they fold.
# setup_wings_effects.py imports them (S_WingGlide looping). Run:
#   powershell -File make_wings_stock_sounds.ps1 [-Downloads <folder with the bought files>]
param([string]$Downloads = (Join-Path $env:USERPROFILE 'Downloads'),
      [string]$Blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe')
$ErrorActionPreference = 'Stop'
$sounds = Join-Path (Split-Path -Parent $PSScriptRoot) 'SourceArt\Sounds'
$stock = Join-Path $sounds 'Stock'
New-Item -ItemType Directory -Force $stock | Out-Null
foreach ($pattern in 'AS_1663144*.wav', 'AS_56501*.mp3') {
  $found = Get-ChildItem $Downloads -Filter $pattern | Select-Object -First 1
  if ($found) { Copy-Item $found.FullName (Join-Path $stock $found.Name) -Force }
}
$flapSource = (Get-ChildItem $stock -Filter 'AS_1663144*.wav' | Select-Object -First 1).FullName
$windSource = (Get-ChildItem $stock -Filter 'AS_56501*.mp3' | Select-Object -First 1).FullName
if (-not $flapSource -or -not $windSource) { throw "The bought files are not in $Downloads or $stock" }
$windWav = Join-Path $env:TEMP 'wings_wind_decoded.wav'
& $Blender -b --factory-startup --python (Join-Path $PSScriptRoot 'decode_audio_blender.py') -- $windSource $windWav | Select-String 'decoded'
if (-not (Test-Path $windWav)) { throw 'Decoding the wind failed' }

Add-Type -TypeDefinition @'
using System;
using System.IO;

public static class WingStock {
    const int Rate = 44100;

    // The mono 16-bit samples of a PCM WAV (chunks in any order).
    public static double[] Read(string path) {
        byte[] b = File.ReadAllBytes(path);
        int i = 12;
        while (i < b.Length - 8) {
            string id = System.Text.Encoding.ASCII.GetString(b, i, 4);
            int len = BitConverter.ToInt32(b, i + 4);
            if (id == "data") {
                var s = new double[len / 2];
                for (int k = 0; k < s.Length; k++) s[k] = BitConverter.ToInt16(b, i + 8 + 2 * k) / 32768.0;
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

    // A seamless loop of loopSeconds from the source's from.. part: its loudness evened out (divided by a smoothed
    // 120 ms RMS, so the swell and the dying away are gone), then its first crossSeconds crossfaded (equal power)
    // with what follows the loop's end, so the end runs straight on into the start.
    public static double[] Loop(double[] src, double from, double loopSeconds, double crossSeconds) {
        int a = (int)(from * Rate), L = (int)(loopSeconds * Rate), C = (int)(crossSeconds * Rate);
        int n = Math.Min(src.Length - a, L + C);
        if (n < L + C) throw new Exception("the source is too short for that loop");
        var r = new double[n];
        int win = (int)(0.12 * Rate);
        double sum = 0.0;
        var sq = new double[n];
        for (int k = 0; k < n; k++) sq[k] = src[a + k] * src[a + k];
        var level = new double[n];
        // centred moving RMS, window clipped at the ends
        double run = 0.0; int lo = 0, hi = -1;
        for (int k = 0; k < n; k++) {
            int wantLo = Math.Max(0, k - win / 2), wantHi = Math.Min(n - 1, k + win / 2);
            while (hi < wantHi) { hi++; run += sq[hi]; }
            while (lo < wantLo) { run -= sq[lo]; lo++; }
            level[k] = Math.Sqrt(Math.Max(1e-12, run / (hi - lo + 1)));
            sum += level[k];
        }
        double mean = sum / n;
        for (int k = 0; k < n; k++) r[k] = src[a + k] * mean / Math.Max(level[k], mean * 0.2);
        var s = new double[L];
        for (int k = 0; k < L; k++) s[k] = r[k];
        for (int k = 0; k < C; k++) {
            double u = k / (double)C;
            s[k] = r[k] * Math.Sin(0.5 * Math.PI * u) + r[L + k] * Math.Cos(0.5 * Math.PI * u);
        }
        return s;
    }

    // from..to seconds of the source, a 5 ms fade in and a fadeOut-second fade out, after lead seconds of silence.
    public static double[] Cut(double[] src, double from, double to, double lead, double fadeOut) {
        int a = (int)(from * Rate), b = Math.Min(src.Length, (int)(to * Rate)), pad = (int)(lead * Rate);
        var s = new double[pad + (b - a)];
        int fin = (int)(0.005 * Rate), fout = (int)(fadeOut * Rate);
        for (int k = 0; k < b - a; k++) {
            double g = Math.Min(1.0, k / (double)fin) * Math.Min(1.0, (b - a - 1 - k) / (double)Math.Max(1, fout));
            s[pad + k] = src[a + k] * g;
        }
        return s;
    }
}
'@
[WingStock]::Write((Join-Path $sounds 'S_WingFlap.wav'), [WingStock]::Cut([WingStock]::Read($flapSource), 0.08, 1.0, 0.0, 0.15), 0.85)
[WingStock]::Write((Join-Path $sounds 'S_WingGlide.wav'), [WingStock]::Loop([WingStock]::Read($windWav), 0.45, 1.6, 0.4), 0.7)
Remove-Item $windWav
Get-ChildItem $sounds -Filter 'S_Wing*.wav' | Select-Object Name, Length
Get-ChildItem $stock | Select-Object Name, Length
