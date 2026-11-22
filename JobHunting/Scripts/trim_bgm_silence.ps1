# Trims the silence the mp3 decode leaves at both ends of a 16-bit WAV (BGM loops; 2026-11-22), so a looping
# Sound Wave has no gap or click at the seam. Silence = every channel's sample within -Threshold of zero.
#   powershell -File trim_bgm_silence.ps1 <file.wav> [-Threshold 0]
param([Parameter(Mandatory)][string]$Path, [int]$Threshold = 0)
$code = @'
using System; using System.IO;
public static class WavTrim {
  public static string Run(string path, int threshold) {
    byte[] b = File.ReadAllBytes(path); int i = 12, ch = 1, dataAt = 0, len = 0;
    while (i < b.Length - 8) {
      string id = System.Text.Encoding.ASCII.GetString(b, i, 4); int l = BitConverter.ToInt32(b, i + 4);
      if (id == "fmt ") ch = BitConverter.ToInt16(b, i + 10);
      if (id == "data") { dataAt = i + 8; len = l; break; }
      i += 8 + l + (l % 2);
    }
    int n = len / 2 / ch;
    Func<int, bool> quiet = f => { for (int c = 0; c < ch; c++) if (Math.Abs((int)BitConverter.ToInt16(b, dataAt + 2 * (f * ch + c))) > threshold) return false; return true; };
    int first = 0; while (first < n && quiet(first)) first++;
    int last = n - 1; while (last > first && quiet(last)) last--;
    int keep = last - first + 1, bytes = keep * 2 * ch;
    using (var o = new BinaryWriter(File.Create(path))) {
      o.Write(System.Text.Encoding.ASCII.GetBytes("RIFF")); o.Write(36 + bytes); o.Write(System.Text.Encoding.ASCII.GetBytes("WAVE"));
      o.Write(System.Text.Encoding.ASCII.GetBytes("fmt ")); o.Write(16); o.Write((short)1); o.Write((short)ch);
      o.Write(44100); o.Write(44100 * 2 * ch); o.Write((short)(2 * ch)); o.Write((short)16);
      o.Write(System.Text.Encoding.ASCII.GetBytes("data")); o.Write(bytes); o.Write(b, dataAt + 2 * first * ch, bytes);
    }
    return string.Format("{0}: cut {1} head + {2} tail frames, {3:0.000} s left", Path.GetFileName(path), first, n - 1 - last, keep / 44100.0);
  }
}
'@
Add-Type -TypeDefinition $code
[WavTrim]::Run((Resolve-Path -LiteralPath $Path).Path, $Threshold)
