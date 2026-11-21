# Decodes any audio file Blender's audaspace (ffmpeg) can read - mp3 included - to a mono 16-bit 44.1 kHz WAV.
# (Its own sound.write fails with "filling the audio frame failed" here, so the samples are written by hand.)
#   blender -b --factory-startup --python decode_audio_blender.py -- <source> <target.wav>
import struct
import sys

import aud

source, target = sys.argv[sys.argv.index("--") + 1:]
data = aud.Sound(source).resample(44100, False).data()   # frames x channels, floats
mono = data.mean(axis=1) if data.ndim == 2 else data
samples = [max(-32767, min(32767, int(round(float(v) * 32767.0)))) for v in mono]
raw = struct.pack("<%dh" % len(samples), *samples)
with open(target, "wb") as out:
    out.write(b"RIFF" + struct.pack("<I", 36 + len(raw)) + b"WAVE")
    out.write(b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, 44100, 88200, 2, 16))
    out.write(b"data" + struct.pack("<I", len(raw)) + raw)
print("decoded", target, round(len(samples) / 44100.0, 2), "s")
