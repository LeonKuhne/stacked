import tkinter as tk
from track import Track
from audio import Audio

class TrackEditor(tk.Tk):

  def __init__(self):
    super().__init__()
    self.tracks = []
    self.num_sections = 8
    self.audio = None
    self.path = "data/track.wav"
    self._setup_ui()
    # sub/ambiance/texture/atmosphere
    self.add_track("environment", "atmosphere", ["nice saturday", "busy city", "stormy night", "alien world", "space", "underwater", "forest", "desert"])
    # drums/rhythm
    self.add_track("vitals", "drum rhythm",  ["relaxed", "energetic", "drowsy", "anxious", "alert", "content", "slow", "fast", "steady"])
    # harmony/accompaniment/timbre
    self.add_track("emotion", "accompaniment", ["happy", "sad", "angry", "melancholic", "excited", "calm", "nervous", "hopeful", "loving"])
    # lead/melody
    self.add_track("voice", "melody", ["graduating prison", "a good day", "fuck my ex", "dumpster diving", "crashed my car", "my new cat", "I got married", "my brother died", "a good night out"])

  def add_track(self, name, desc, options):
    print(f"adding track for {name}: {desc} with options: {options}")
    track = Track(self.screen, name, self.num_sections)
    # gen prompts
    for option in options:
      track.gen_pattern(option, f"{option} {desc} loop")
    # save to editor
    self.tracks.append(track)
    track.pack(fill=tk.BOTH, expand=True)

  def compile(self):
    # zero all sliders with empty tracks
    for track in self.tracks:
      if track.empty(): track.zero_slider()
    # compile audio
    print("compling song...")
    clips = [track.compile(self.max_pattern_duration()) for track in self.tracks]
    for clip in clips: print(f"track length: {clip.duration_seconds}")
    self.audio = Audio.layer(self.path, *clips)
    print(f"song compiled, playing...")
    Audio.play(self.path)

  def max_pattern_duration(self):
    max_duration = 0
    for track in self.tracks:
      for pattern in track.playlist():
        if not pattern: continue
        duration = pattern.audio.duration_seconds 
        if duration <= max_duration: continue
        max_duration = duration
    return max_duration

  def _setup_ui(self):
    canvas = tk.Canvas(self)
    self.screen = tk.Frame(canvas)
    self.title("Stacked | Track Editor")
    self.geometry("1720x220")
    self.bind("<Configure>", lambda e: (e.width, 220))
    # add playback button
    play = tk.Button(self, text="play", command=self.compile)
    play.pack(side="bottom")
    # setup scrollbar
    scrollbar = tk.Scrollbar(self, orient="horizontal", command=canvas.xview)
    scrollbar.pack(side='bottom', fill='x')
    canvas.configure(yscrollcommand=scrollbar.set, scrollregion=canvas.bbox('all'))
    canvas.pack(side='top', fill='both', expand=True)
    # setup main frame 
    canvas.create_window((0, 0), window=self.screen, anchor='nw')