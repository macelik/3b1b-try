"""Her seslendirme satırını Piper (yerel, ücretsiz Türkçe ses modeli) ile üretir.

Piper her çalıştırmada biraz farklı bir okuma üretir. Her satır için birkaç
deneme üretilir; Whisper ile geri yazıya dökülüp metne en çok benzeyen seçilir.

Çıktı: audio/<sahne>__<anahtar>.wav ve audio/durations.json
Kullanım: python3 tts.py [satır_adı ...]   (ad verilmezse eksik olanlar üretilir)
"""
import difflib
import json
import os
import re
import subprocess
import sys
import wave

import numpy as np

from narration import SCENES, tts_text

VOICE = os.environ.get(
    "PIPER_VOICE",
    "/home/user/voices/vits-piper-tr_TR-fahrettin-medium/tr_TR-fahrettin-medium.onnx",
)
WHISPER = os.environ.get("WHISPER_DIR", "/home/user/voices/sherpa-onnx-whisper-small")
LENGTH_SCALE = os.environ.get("PIPER_LENGTH_SCALE", "1.12")
TAKES = int(os.environ.get("TTS_TAKES", "4"))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")

_recognizer = None


def recognizer():
    global _recognizer
    if _recognizer is None and os.path.isdir(WHISPER):
        import sherpa_onnx
        _recognizer = sherpa_onnx.OfflineRecognizer.from_whisper(
            encoder=f"{WHISPER}/small-encoder.int8.onnx",
            decoder=f"{WHISPER}/small-decoder.int8.onnx",
            tokens=f"{WHISPER}/small-tokens.txt",
            language="tr", task="transcribe", num_threads=4,
        )
    return _recognizer


def synth(text: str, dst: str) -> None:
    raw = dst + ".raw.wav"
    subprocess.run(
        ["piper", "-m", VOICE, "--length-scale", LENGTH_SCALE, "--sentence-silence", "0.25", "-f", raw],
        input=text.encode(), check=True, capture_output=True,
    )
    # Hafif oda tınısı + ses seviyesi normalizasyonu + baş/son sessizliği kırpma, 48 kHz stereo
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", raw,
         "-af", "highpass=f=70,aecho=0.8:0.5:40:0.12,loudnorm=I=-16:TP=-1.5:LRA=7,"
                "silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
                "silenceremove=start_periods=1:start_threshold=-50dB,areverse",
         "-ar", "48000", "-ac", "2", dst],
        check=True,
    )
    os.remove(raw)


def transcribe(path: str) -> str:
    pcm = subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-i", path, "-af", "apad=pad_dur=1.5,adelay=300:all=1",
         "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
        capture_output=True, check=True,
    ).stdout
    s = recognizer().create_stream()
    s.accept_waveform(16000, np.frombuffer(pcm, np.int16).astype(np.float32) / 32768)
    recognizer().decode_stream(s)
    return s.result.text.strip()


def _norm(t: str) -> str:
    return " ".join(re.sub(r"[^a-zçğıöşü0-9 ]", "", t.replace("İ", "i").replace("I", "ı").lower()).split())


def score(text: str, heard: str) -> float:
    return difflib.SequenceMatcher(None, _norm(text), _norm(heard)).ratio()


def best_take(text: str, dst: str) -> None:
    if TAKES <= 1 or recognizer() is None:
        synth(text, dst)
        return
    best = (-1.0, None)
    for i in range(TAKES):
        cand = f"{dst}.take{i}.wav"
        synth(text, cand)
        heard = transcribe(cand)
        sc = score(text, heard)
        print(f"    take {i}: {sc:.3f}  {heard}")
        if sc > best[0]:
            if best[1]:
                os.remove(best[1])
            best = (sc, cand)
        else:
            os.remove(cand)
        if sc > 0.985:
            break
    os.replace(best[1], dst)


def duration(path: str) -> float:
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


def main(only=None):
    os.makedirs(OUT, exist_ok=True)
    durations = {}
    for scene, lines in SCENES.items():
        for key, text in lines:
            name = f"{scene}__{key}"
            path = os.path.join(OUT, name + ".wav")
            if (only and name in only) or not os.path.exists(path):
                print(name)
                best_take(tts_text(text), path)
            durations[name] = round(duration(path), 3)
            print(f"{durations[name]:6.2f}s  {name}")
    with open(os.path.join(OUT, "durations.json"), "w") as f:
        json.dump(durations, f, indent=1)
    print(f"Toplam: {sum(durations.values()):.1f}s")


if __name__ == "__main__":
    main(set(sys.argv[1:]) or None)
