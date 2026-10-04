"""Üretilen seslendirmeyi Whisper ile geri yazıya döker (telaffuz kontrolü için)."""
import glob, subprocess, sys
import numpy as np, sherpa_onnx
D = "/home/user/voices/sherpa-onnx-whisper-small"
rec = sherpa_onnx.OfflineRecognizer.from_whisper(
    encoder=f"{D}/small-encoder.int8.onnx", decoder=f"{D}/small-decoder.int8.onnx",
    tokens=f"{D}/small-tokens.txt", language="tr", task="transcribe", num_threads=4)
for p in sorted(glob.glob(sys.argv[1] if len(sys.argv) > 1 else "audio/*.wav")):
    pcm = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", p, "-af", "apad=pad_dur=1.5,adelay=300:all=1", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    s = rec.create_stream()
    s.accept_waveform(16000, np.frombuffer(pcm, np.int16).astype(np.float32) / 32768)
    rec.decode_stream(s)
    print(p.split("/")[-1][:-4], "|", s.result.text.strip())
