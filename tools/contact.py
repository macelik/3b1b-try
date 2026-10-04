"""Her sahne için, seslendirme satırlarının sonundaki kareleri bir araya getirir."""
import json, os, subprocess, sys
q = sys.argv[1] if len(sys.argv) > 1 else "480p15"
out = sys.argv[2] if len(sys.argv) > 2 else "media/contact"
os.makedirs(out, exist_ok=True)
from narration import SCENE_ORDER
for sc in SCENE_ORDER:
    cues = json.load(open(f"media/cues/{sc}.json"))
    times = [c["end"] - 0.05 for c in cues["cues"]] + [cues["duration"] - 1.0]
    files = []
    for i, t in enumerate(times):
        f = f"{out}/{sc}_{i}.png"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(max(t, 0)), "-i", f"media/videos/video/{q}/{sc}.mp4",
                        "-frames:v", "1", "-vf", "scale=640:-1", f], check=True)
        files.append(f)
    n = len(files); cols = 2; rows = (n + 1) // 2
    inputs = sum([["-i", f] for f in files], [])
    if n % 2: inputs += ["-f", "lavfi", "-i", "color=black:s=640x360:d=1"]; n += 1
    layout = "|".join(f"{(i%cols)*640}_{(i//cols)*360}" for i in range(n))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex",
                    f"xstack=inputs={n}:layout={layout}", "-frames:v", "1", f"{out}/{sc}.png"], check=True)
    for f in files: os.remove(f)
    print(f"{out}/{sc}.png")
