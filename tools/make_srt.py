"""Sahne ipuçlarından (media/cues/*.json) Türkçe altyazı dosyası üretir."""
import json, subprocess, sys, textwrap
sys.path.insert(0, ".")
from narration import SCENE_ORDER

q = sys.argv[1] if len(sys.argv) > 1 else "1080p30"


def ts(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def video_len(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout
    return float(out)


offset, n = 0.0, 1
for sc in SCENE_ORDER:
    for c in json.load(open(f"media/cues/{sc}.json"))["cues"]:
        print(n); n += 1
        print(f"{ts(offset + c['start'])} --> {ts(offset + c['end'])}")
        print("\n".join(textwrap.wrap(c["text"], 48)) + "\n")
    offset += video_len(f"media/videos/video/{q}/{sc}.mp4")
