import asyncio, re, pathlib
from pyneuphonic import Neuphonic, TTSConfig
from pyneuphonic._utils import async_save_audio
from pydub import AudioSegment
import glob
import os

API_KEY = "4e2860a0031af3527f9b6f3618b7665a360fd15fb7f165af3c877e53aaecf8ca.19edd346-a252-4167-98b4-6caecb7433c4"

semaphore = asyncio.Semaphore(3) # I WOULD RECOMMEND NOT EXCEEDING 3 CONCURRENT REQUESTS

def parse_script(path: str) -> list[tuple[str, str]]:
    pat, out = re.compile(r"^\s*<([^>]+)>\s*(.+)$"), []
    with open(path, encoding="utf-8") as fp:
        for ln in fp:
            m = pat.match(ln)
            if m:
                out.append((m.group(1).strip(), m.group(2).strip()))
    return out

async def synthesize(text: str, out_path: pathlib.Path, voice_id: str, speed: float = 0.9):
    async with semaphore:
        client = Neuphonic(api_key=API_KEY)
        sse      = client.tts.AsyncSSEClient()
        cfg      = TTSConfig(
            lang_code="en", 
            voice_id=voice_id,
            speed=speed  # Custom speed per voice
        )
        resp     = sse.send(text, tts_config=cfg)
        await async_save_audio(resp, str(out_path))
        print(f"✅ Generated: {out_path.name} (speed: {speed}x)")

def merge_segments(folder: str, outfile: str, gap_sec: float = 0.3,) -> None:
    gap, podcast = AudioSegment.silent(int(gap_sec * 1000)), AudioSegment.silent(0)
    seg_files = sorted([f for f in glob.glob(f"{folder}*.wav")])
    print(f"🔗 Merging {len(seg_files)} segments...")
    for i, fname in enumerate(seg_files):
        print(f"  📄 Adding: {fname}")
        seg = AudioSegment.from_wav(fname)
        podcast += seg
        if i < len(seg_files) - 1:
            podcast += gap
    podcast.export(outfile, format="wav")
    print(f"🎉 Final podcast saved: {outfile}")

async def main(script="script.txt", output_folder=""):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    lines = parse_script(script)
    print(f"🎬 Processing {len(lines)} segments...")
    
    tasks = []
    for idx, (speaker, text) in enumerate(lines, 1):
        out_path = pathlib.Path(f"{output_folder}/{idx:02d}_{speaker}.wav")
        voice_id = VOICE_MAP.get(speaker)
        
        # Get speed for this voice
        speed = get_speed_for_voice(speaker)
            
        if voice_id:
            print(f"📍 Queuing segment {idx}: {speaker} (speed: {speed}x) - {text[:50]}...")
            tasks.append(synthesize(text, out_path, voice_id, speed))
        else:
            print(f"❌ Voice '{speaker}' not found in mapping. Skipping.")
    
    await asyncio.gather(*tasks)
    print("✅ All segments generated!")

if __name__ == "__main__":
    # Updated voice mapping to use Shiv_48k_A for Rowan
    VOICE_MAP = {
        "Alex": "bf779307-4b93-41d6-a43e-2099cc93fbc6",  # Your cloned Alex_Demo voice
        "Rowan": "1af220b3-371e-4e2c-96fb-bfaee9d9525d",  # Shiv_48k_A voice
    }
    
    # Set different speeds per voice
    def get_speed_for_voice(speaker):
        if speaker == "Alex":
            return 0.7   # Slow and deliberate for Alex
        elif speaker == "Rowan":
            return 0.9   # Slightly slower than normal for Rowan
        else:
            return 0.9   # Default speed
    
    OUTPUTFOLDER = "podcast_hadrians_wall/"
    
    print("🚀 Starting SSE-based podcast creation - Hadrian's Wall episode...")
    print(f"🎙️ Alex = Alex_Demo (ID: {VOICE_MAP['Alex']}) - Speed: 0.7x (slow)")
    print(f"🎙️ Rowan = Shiv_48k_A (ID: {VOICE_MAP['Rowan']}) - Speed: 0.9x (normal-slow)")
    print("🏛️ Using Hadrian's Wall script (script4.txt)")
    asyncio.run(main(script="script4.txt", output_folder=OUTPUTFOLDER))
    merge_segments(folder=OUTPUTFOLDER, outfile=f"{OUTPUTFOLDER}/hadrians_wall_podcast.wav", gap_sec=0.3)