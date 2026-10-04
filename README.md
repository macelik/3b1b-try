# İman — Ses ve Mana

İman kelimesinin kökündeki seslerin (hemze, mîm, nûn) İbn Cinnî'nin ses–mana
yaklaşımından hareketle estetik bir okumasını anlatan, 3Blue1Brown tarzında
(Manim ile) hazırlanmış kısa bir Türkçe video.

## Dosyalar

| Dosya | Görevi |
|---|---|
| `narration.py` | Seslendirme / altyazı metni (sahne sahne). Metni değiştirmek için burayı düzenleyin. |
| `tts.py` | Her satırı Piper (ücretsiz, yerel çalışan Türkçe ses modeli) ile seslendirir. Her satır için birkaç okuma üretip Whisper ile en doğru telaffuz edileni seçer. |
| `video.py` | Manim sahneleri. Animasyon süreleri gerçek ses sürelerine göre ayarlanır. |
| `build.sh` | Sesleri üretir, sahneleri render eder, tek bir `output/iman_ses_ve_mana.mp4` ve `.srt` altyazı dosyası oluşturur. |
| `tools/` | Telaffuz kontrolü (`asr_check.py`), önizleme kareleri (`contact.py`), altyazı (`make_srt.py`). |

## Gereksinimler

```bash
apt-get install libcairo2-dev libpango1.0-dev ffmpeg fonts-hosny-amiri fonts-cmu
pip install manim piper-tts sherpa-onnx
```

Ses modeli (CC0 lisanslı `tr_TR-fahrettin-medium`) ve telaffuz kontrolü için Whisper:

```bash
mkdir -p /home/user/voices && cd /home/user/voices
curl -L https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-tr_TR-fahrettin-medium.tar.bz2 | tar xj
curl -L https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-small.tar.bz2 | tar xj
```

Model yolları `PIPER_VOICE` ve `WHISPER_DIR` ortam değişkenleriyle değiştirilebilir.
Diğer Türkçe sesler: `tr_TR-dfki-medium` (CC BY-NC-SA), `tr_TR-fettah-medium` (CC0).

## Kullanım

```bash
python3 tts.py                 # eksik sesleri üret
python3 tts.py S06_Mim__dudak  # tek bir satırı yeniden seslendir
./build.sh                     # 1080p30 render + birleştirme
QUALITY=480p15 ./build.sh      # hızlı önizleme
```

Kendi sesinizi kullanmak isterseniz `audio/<Sahne>__<anahtar>.wav` dosyalarını
kendi kayıtlarınızla değiştirip `python3 tts.py` çalıştırın (yalnızca süreleri
günceller), ardından `./build.sh`.
