import tkinter as tk
from tkinter import ttk
from pattern import Pattern
from audio import Audio
import os
from pydub import AudioSegment

class Track(ttk.Frame):
  def __init__(self, parent, name, num_sections):
    super().__init__(parent)
    self.patterns = { "silence": None }
    self.name = name
    self.column_width = 20
    self.last_played = None
    # ui
    label = tk.Label(self, text=name)
    label.bind("<Configure>", lambda _: label.config(width=self.column_width, font=("helvetica", 24)))
    label.grid(row=0, column=0, sticky="nsew")
    # adjust pattern length (set start value to max) 
    self.slider_resolution = 1000
    self.slider = ttk.Scale(self, from_=1, to=self.slider_resolution, orient="horizontal")
    self.slider.set(self.slider_resolution)
    self.slider.config(length=200)
    self.slider.bind("<ButtonRelease-1>", lambda e: self._play_pattern(self.last_played))
    self.slider.grid(row=0, column=len(self.winfo_children()), sticky="nsew")
    self.pattern_length = lambda: self.slider.get() / self.slider_resolution
    # fill pattern sections
    for _ in range(num_sections): self.extend()
    # audio 
    self.path = f"data/{name}"
    self.audio = None
    if not os.path.exists(self.path): os.makedirs(self.path)
  
  def extend(self, font=("helvetica", 18)):
    self.columnconfigure(len(self.winfo_children()), weight=1)
    select = ttk.Combobox(self, values=list(self.patterns.keys()))
    select.option_add('*TCombobox*Listbox.font', f"{font[0]} {font[1]}")
    select.config(font=font, width=self.column_width)
    select.bind("<<ComboboxSelected>>", lambda e: self._play_pattern(e.widget.get()))
    select.grid(row=0, column=len(self.winfo_children()), sticky="nsew")

  def _play_pattern(self, name):
    if not name in self.patterns: 
      self.last_played = None
      return
    self.last_played = name
    # play pattern
    print(f"playing selected pattern '{name}'...")
    if name == "silence": return
    self.patterns[name].play(self.pattern_length())

  def gen_pattern(self, name, desc):
    path = f"data/{self.name}/{name}.wav"
    if not os.path.exists(path): Audio.gen(path, desc)
    self.add_pattern(name, path)

  def add_pattern(self, name, path):
    self.patterns[name] = Pattern(name, path)
    # update dropdowns
    for select in self.dropdowns():
      select.config(values=list(self.patterns.keys())) 

  def dropdowns(self):
    components = [] 
    for elem in self.winfo_children():
      if not isinstance(elem, ttk.Combobox): continue
      components.append(elem)
    return components

  def playlist(self):
    patterns = []
    for select in self.dropdowns():
      name = select.get()
      if not name in self.patterns: 
        patterns.append(None)
        continue
      pattern = self.patterns[name]
      patterns.append(pattern)
    return patterns

  def compile(self, measure_length):
    print(f"compiling track {self.name} with pattern length {measure_length}...")
    silence = AudioSegment.silent(duration=measure_length * 1000)
    # fix clip lengths
    clips = []
    for select in self.dropdowns():
      name = select.get()
      # prev clip
      if not name in self.patterns: 
        clips.append(clips[-1] if len(clips) else silence)
        continue
      # silence
      if name == "silence":
        clips.append(silence)
        continue
      # loop pattern
      clips.append(self.patterns[name].loop(measure_length, self.pattern_length()))
    # stitch audio
    self.audio = Audio.stitch(f"{self.path}/track.wav", *clips)
    print(f"compiled {self.name}")
    return self.audio

  def empty(self):
    for select in self.dropdowns():
      if select.get() in self.patterns: return False
    return True

  def zero_slider(self):
    self.slider.set(0)