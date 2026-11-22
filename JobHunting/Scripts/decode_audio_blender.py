# Decodes any audio file Blender's audaspace (ffmpeg) can read - mp3 included - to a 16-bit 44.1 kHz WAV, mono by
# default, or kept stereo with --stereo (for music; 2026-11-22).
# (Its own sound.write fails with "filling the audio frame failed" here, so the samples are written by hand.)
#   blender -b --factory-startup --python decode_audio_blender.py -- <source> <target.wav> [--stereo]
import struct
import sys

import aud
import numpy

args = sys.argv[sys.argv.index("--") + 1:]
stereo = "--stereo" in args
source, target = [a for a in args if a != "--stereo"]
data = aud.Sound(source).resample(44100, False).data()   # frames x channels, floats
if data.ndim == 1:
    data = data.reshape(-1, 1)
if stereo:
    out_data = data[:, :2] if data.shape[1] >= 2 else numpy.repeat(data, 2, axis=1)
else:
    out_data = data.mean(axis=1).reshape(-1, 1)
channels = out_data.shape[1]
ints = numpy.clip(numpy.round(out_data * 32767.0), -32767, 32767).astype("<i2")
raw = ints.tobytes()
with open(target, "wb") as out:
    out.write(b"RIFF" + struct.pack("<I", 36 + len(raw)) + b"WAVE")
    out.write(b"fmt " + struct.pack("<IHHIIHH", 16, 1, channels, 44100, 44100 * 2 * channels, 2 * channels, 16))
    out.write(b"data" + struct.pack("<I", len(raw)) + raw)
print("decoded", target, round(out_data.shape[0] / 44100.0, 2), "s", channels, "ch")
