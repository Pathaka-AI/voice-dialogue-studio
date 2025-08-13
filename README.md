# Neuphonic High-Quality Backend

A simple but powerful backend for the Neuphonic TTS API that supports **48kHz high-quality audio generation**.

## Features ✨

1. **🎙️ Voice Cloning** - Clone voices from audio samples
2. **📋 Voice Listing** - List all available voices 
3. **🎵 High-Quality Audio Generation** - Generate 48kHz broadcast-quality audio
4. **🎬 Podcast Creation** - Create full podcasts from scripts

## Quick Start 🚀

### 1. List Your Voices
```bash
# List all voices
python3 neuphonic_backend.py list-voices

# List only cloned voices
python3 neuphonic_backend.py list-voices --cloned-only
```

### 2. Clone a Voice
```bash
python3 neuphonic_backend.py clone-voice \
  --voice-name "MyVoice" \
  --audio-file "path/to/audio.wav" \
  --tags "professional" "male"
```

### 3. Generate High-Quality Audio (48kHz)
```bash
python3 neuphonic_backend.py generate-longform \
  --text "Your text here" \
  --voice-id "your-voice-id" \
  --output "output.wav"
```

### 4. Create Full Podcast (48kHz)
```bash
python3 neuphonic_backend.py create-podcast \
  --script "script.txt" \
  --output "my_podcast.wav"
```

## Script Format 📝

For podcast creation, use this format in your script file:

```
<VoiceName> Text for this voice to speak.
<AnotherVoice> Text for the second voice.
<VoiceName> More text for the first voice.
```

## Output Quality 🔊

- **48kHz sampling rate** - Broadcast quality
- **16-bit depth** - Professional standard  
- **PCM Linear encoding** - Uncompressed audio
- **Mono channel** - Optimized for voice

## File Structure 📁

```
outputs/
├── individual_segments/    # Individual voice segments
├── combined_podcasts/      # Final combined podcasts
└── single_generations/     # One-off audio generations
```

## Your Current Voices 🎭

Based on your current setup:
- `Alex`: Holly (Female, American, Midwestern)
- `Rowan`: Miles (Male, American, Narrator)  
- `Alex_Demo`: Your cloned Alex voice
- `Shiv_Demo`: Your cloned Shiv voice

## Tips 💡

1. Use `generate-longform` for best quality (vs `generate-audio`)
2. 48kHz is only available with longform inference
3. Voice cloning works best with clear, 10-30 second samples
4. Check `voice_mapping.json` for your voice IDs

## Requirements 📦

```bash
pip install pyneuphonic requests
```

Set your API key as environment variable or it will use the hardcoded one. 