from transformers import AutoProcessor, MusicgenForConditionalGeneration
from pydub import AudioSegment
import scipy
import subprocess
import os

class Audio:
  #model_name = "facebook/musicgen-small"
  model_name = "facebook/musicgen-medium"
  ready = False
  processor = None
  model = None
  player = None
  temp_file = "data/temp.wav"

  def load_model():
    if Audio.model: return
    Audio.processor = AutoProcessor.from_pretrained(Audio.model_name)
    Audio.model = MusicgenForConditionalGeneration.from_pretrained(Audio.model_name)
    Audio.loaded = True

  def gen(path, *descriptions):
    print(f"generating audio {path}...")
    Audio.load_model()
    inputs = Audio.processor(
      text=descriptions,
      padding=True,
      return_tensors="pt",
    )
    output = Audio.model.generate(**inputs, max_new_tokens=512)
    # save file
    sampling_rate = Audio.model.config.audio_encoder.sampling_rate
    scipy.io.wavfile.write(path, rate=sampling_rate, data=output[0, 0].numpy())

  def stitch(path, *samples):
    audio = AudioSegment.empty()
    for sample in samples:
      print(f"adding audio {sample.duration_seconds}s")
      audio += sample
    # save file
    audio.export(path, format="wav")
    return audio

  def layer(path, *samples):
    if not len(samples): return 
    print(f"layering {len(samples)} samples...")
    audio = samples[0]
    for sample in samples[1:]:
      print(f"overlaying audio with duration: {sample.duration_seconds}s...")
      audio = audio.overlay(sample)
    # save file
    audio.export(path, format="wav")
    return audio

  def play(path):
    # play using os ffplay, hide all the warnings, no gui
    if Audio.player: Audio.player.terminate()
    print(f"resting playback for {path}...")
    Audio.player = subprocess.Popen(["ffplay", "-nodisp", "-autoexit", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  
  def play_live(clip):
    print(f"playing {clip.duration_seconds}s...")
    if Audio.player: Audio.player.terminate()
    clip.export(Audio.temp_file, format="wav")
    Audio.player = subprocess.Popen(["ffplay", "-nodisp", "-autoexit", Audio.temp_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if __name__ == "__main__":
  Audio.gen(Audio.temp_file, "dynamic trumpet dubstep")