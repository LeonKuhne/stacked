from pydub import AudioSegment
from audio import Audio

class Pattern:

  def __init__(self, name, path):
    self.name = name
    self.path = path 
    self.audio = AudioSegment.from_file(path, format="wav")
    self.cache = {}

  # TODO try 48000Hz
  def loop(self, clip_length, pattern_length, sample_rate=44100):
    key = clip_length * pattern_length
    if key in self.cache: return self.cache[key]
    # shorten pattern
    sample = self.shorten(pattern_length)
    # loop pattern
    clip = AudioSegment.empty()
    while clip.duration_seconds < clip_length: clip += sample
    # trim remainder
    clip = clip[:clip_length * sample_rate]
    # save to cache
    print(f"looping pattern {self.name}: {self.audio.duration_seconds} -> {clip.duration_seconds}s...")
    self.cache[key] = clip
    return clip

  def play(self, pattern_length):
    print(f"playing pattern '{self.name}'...")
    Audio.play_live(self.shorten(pattern_length))

  def shorten(self, factor):
    return self.audio[:(factor * len(self.audio))]