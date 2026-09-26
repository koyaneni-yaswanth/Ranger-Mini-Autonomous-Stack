# Voice & Speech Pipeline

## 1. Modular Architecture
```text
Microphone -> Voice Activity Detection (VAD) -> Wake Word ("JARVIS") -> Speech-to-Text (STT)
  -> JARVIS Brain -> Task -> Robot -> Text-to-Speech (TTS) -> Speaker
```

## 2. Modality & Debugging Fallback
- Supports wake word `"JARVIS"` (case-insensitive).
- Operates with real microphones/speakers or headless text console fallback (`/jarvis/voice_raw`, `/jarvis/recognized_speech`, `/jarvis/tts_say`).
