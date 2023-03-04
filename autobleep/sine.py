"""Play a fixed frequency sound."""
from __future__ import division
import math
import wave

from pyaudio import PyAudio

try:
    from itertools import izip
except ImportError:  # Python 3
    izip = zip
    xrange = range


def sine_tone(frequency, duration, volume=1, sample_rate=44100):
    n_samples = int(sample_rate * duration)
    restframes = n_samples % sample_rate

    p = PyAudio()
    stream = p.open(
        format=p.get_format_from_width(1),  # 8bit
        channels=1,  # mono
        rate=sample_rate,
        output=False,
    )
    s = lambda t: volume * math.sin(2 * math.pi * frequency * t / sample_rate)
    samples = (int(s(t) * 0x7F + 0x80) for t in xrange(n_samples))
    for buf in izip(*[samples] * sample_rate):  # write several samples at a time
        stream.write(bytes(bytearray(buf)))

    # fill remainder of frameset with silence
    stream.write(b"\x80" * restframes)

    stream.stop_stream()
    stream.close()
    p.terminate()
