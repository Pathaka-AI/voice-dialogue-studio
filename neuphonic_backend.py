#!/usr/bin/env python3
"""
Simple Neuphonic Backend Application
Provides: Voice Cloning, Voice Listing, and Simple TTS Generation
"""

import os
import json
import argparse
from pathlib import Path

# Set environment variable for API key
# For production, set NEUPHONIC_API_KEY environment variable
API_KEY = os.getenv('NEUPHONIC_API_KEY', "your_api_key_here")
if API_KEY == "your_api_key_here":
    print("⚠️  Warning: Using placeholder API key. Set NEUPHONIC_API_KEY environment variable.")
    print("   For development, you can set it in your shell:")
    print("   export NEUPHONIC_API_KEY='your_actual_api_key'")
os.environ['NEUPHONIC_API_KEY'] = API_KEY

try:
    from pyneuphonic import Neuphonic, TTSConfig
except ImportError:
    print("❌ pyneuphonic not installed. Run: pip install pyneuphonic")
    exit(1)

class NeuphonicBackend:
    def __init__(self):
        self.client = Neuphonic(api_key=API_KEY)
        self.output_dir = Path("outputs")
        self.voice_mapping_file = Path("voice_mapping.json")
        
        # Create outputs directory
        self.output_dir.mkdir(exist_ok=True)
        
        print("🚀 Neuphonic Backend initialized")

    def list_voices(self, show_cloned_only=False):
        """List all available voices"""
        try:
            print("🔍 Fetching voices...")
            response = self.client.voices.list()
            voices = response.data['voices']
            
            if show_cloned_only:
                voices = [v for v in voices if v.get('type') == 'Cloned Voice']
                print(f"\n👥 Found {len(voices)} cloned voices:")
            else:
                print(f"\n📋 Found {len(voices)} total voices:")
            
            for voice in voices:
                name = voice.get('name', 'Unknown')
                voice_id = voice.get('voice_id', 'No ID')
                voice_type = voice.get('type', 'Unknown')
                lang = voice.get('lang_code', 'Unknown')
                tags = ', '.join(voice.get('tags', []))
                
                print(f"  🎙️  {name}")
                print(f"      ID: {voice_id}")
                print(f"      Type: {voice_type} | Language: {lang}")
                if tags:
                    print(f"      Tags: {tags}")
                print()
            
            return voices
            
        except Exception as e:
            print(f"❌ Failed to list voices: {str(e)}")
            return []

    def clone_voice(self, voice_name, audio_file_path, voice_tags=None):
        """Clone a voice from an audio sample"""
        try:
            audio_path = Path(audio_file_path)
            if not audio_path.exists():
                print(f"❌ Audio file not found: {audio_file_path}")
                return None
            
            print(f"🎵 Cloning voice '{voice_name}' from {audio_file_path}...")
            
            tags = voice_tags or []
            
            response = self.client.voices.clone(
                voice_name=voice_name,
                voice_tags=tags,
                voice_file_path=str(audio_path)
            )
            
            if response.data:
                voice_id = response.data.get('voice_id')
                print(f"✅ Voice cloned successfully!")
                print(f"   Name: {voice_name}")
                print(f"   ID: {voice_id}")
                
                # Update voice mapping
                self._update_voice_mapping(voice_name, voice_id)
                
                return voice_id
            else:
                print(f"❌ Failed to clone voice: {response}")
                return None
                
        except Exception as e:
            print(f"❌ Voice cloning failed: {str(e)}")
            return None

    def _save_high_quality_wav(self, audio_data, output_path, sampling_rate=48000):
        """Save audio data as high-quality WAV file with specified sampling rate"""
        import wave
        
        with wave.open(str(output_path), 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit samples
            wav_file.setframerate(sampling_rate)  # Use specified sampling rate
            wav_file.writeframes(audio_data)
        
        print(f"📊 Audio saved with {sampling_rate}Hz sampling rate")

    def generate_longform_audio(self, text, voice_name=None, voice_id=None, output_filename=None, speed=1.0):
        """Generate high-quality audio using Longform Inference (48kHz)"""
        try:
            import requests
            import time
            import json
            
            # Determine voice_id
            if voice_id is None:
                if voice_name is None:
                    print("❌ Either voice_name or voice_id must be provided")
                    return None
                
                voice_mapping = self._load_voice_mapping()
                voice_id = voice_mapping.get(voice_name)
                if voice_id is None:
                    print(f"❌ Voice '{voice_name}' not found in voice mapping")
                    return None
            
            print(f"🎵 Generating longform audio...")
            print(f"   Text: {text[:100]}{'...' if len(text) > 100 else ''}")
            print(f"   Voice ID: {voice_id}")
            print(f"   Speed: {speed}x")
            
            # Use Longform Inference for high-quality generation
            tts = self.client.tts.LongformInference()
            tts_config = TTSConfig(
                lang_code='en', 
                voice_id=voice_id,
                sampling_rate=48000,  # Use 48kHz for highest quality (longform inference only)
                speed=speed,          # Custom playback speed
                encoding='pcm_linear'  # Standard encoding
            )
            
            print("⏳ Submitting longform inference job...")
            
            # Post the job
            post_response = tts.post(text=text, tts_config=tts_config)
            response_data = json.loads(post_response.data)
            
            if response_data.get("status_code") != 200:
                print(f"❌ Failed to submit job: {response_data}")
                return None
            
            job_id = response_data["data"]["job_id"]
            print(f"✅ Job submitted successfully! Job ID: {job_id}")
            
            # Poll for completion with optimized timing
            print("⏳ Waiting for job completion...")
            print("💡 Optimized polling: checking every 20 seconds...")
            
            # Start checking after 25 seconds (balanced approach)
            time.sleep(25)
            
            max_attempts = 12  # 12 attempts with 20-second intervals = up to 4.5 minutes total
            attempt = 0
            
            while attempt < max_attempts:
                print(f"🔍 Status check {attempt + 1}/{max_attempts}...")
                get_response = tts.get(job_id)
                get_data = json.loads(get_response.data)
                
                if get_data.get("status_code") == 200:
                    # Job completed successfully
                    audio_url = get_data['data']['audio_url']
                    print(f"🎉 Audio generation completed!")
                    print(f"📁 Signed URL: {audio_url}")
                    
                    # Download the audio file
                    if not output_filename:
                        import time
                        timestamp = int(time.time())
                        output_filename = f"longform_{timestamp}.wav"
                    
                    output_path = self.output_dir / output_filename
                    
                    print(f"⬇️ Downloading audio to {output_path}...")
                    audio_response = requests.get(audio_url)
                    audio_response.raise_for_status()
                    
                    # Save with high-quality 48kHz sampling rate
                    self._save_high_quality_wav(audio_response.content, output_path, sampling_rate=48000)
                    
                    print(f"✅ High-quality 48kHz audio saved: {output_path}")
                    return str(output_path)
                
                elif get_data.get("status_code") == 202:
                    # Job still processing
                    print(f"⏳ Job still processing... (attempt {attempt + 1}/{max_attempts})")
                    time.sleep(20)  # Wait 20 seconds between checks (faster!)
                    attempt += 1
                else:
                    # Job failed
                    print(f"❌ Job failed: {get_data}")
                    return None
            
            print("⏰ Job timed out after waiting too long")
            return None
                
        except Exception as e:
            print(f"❌ Longform audio generation failed: {str(e)}")
            return None

    def generate_simple_audio(self, text, voice_name=None, voice_id=None, output_filename=None, speed=1.0):
        """Generate audio using simple TTS (SSE) - for shorter texts"""
        try:
            # Determine voice_id
            if voice_name and not voice_id:
                voice_mapping = self._load_voice_mapping()
                voice_id = voice_mapping.get(voice_name)
                if not voice_id:
                    print(f"❌ Voice '{voice_name}' not found in mapping")
                    return None
            
            if not voice_id:
                # Use first available English voice
                voices = self.client.voices.list().data['voices']
                english_voices = [v for v in voices if v.get('lang_code') == 'en']
                if english_voices:
                    voice_id = english_voices[0]['voice_id']
                    print(f"🎙️ Using default voice: {english_voices[0]['name']}")
                else:
                    print("❌ No English voices available")
                    return None
            
            print(f"🎵 Generating simple audio...")
            print(f"   Text: {text[:100]}{'...' if len(text) > 100 else ''}")
            print(f"   Voice ID: {voice_id}")
            print(f"   Speed: {speed}x")
            
            # Use SSE for simple generation
            sse = self.client.tts.SSEClient()
            tts_config = TTSConfig(
                lang_code='en', 
                voice_id=voice_id,
                sampling_rate=22050,  # Match docs exactly
                speed=speed
            )
            
            # Generate filename if not provided
            if not output_filename:
                import time
                timestamp = int(time.time())
                output_filename = f"simple_{timestamp}.wav"
            
            output_path = self.output_dir / output_filename
            
            print("⏳ Processing audio...")
            
            # Actually generate the audio using SSE
            audio_chunks = []
            try:
                for chunk in sse.send(text, tts_config):  # Remove format='wav' parameter
                    if hasattr(chunk, 'data') and chunk.data and hasattr(chunk.data, 'audio') and chunk.data.audio:
                        audio_chunks.append(chunk.data.audio)
                
                # Combine and save audio chunks
                if audio_chunks:
                    import wave
                    import struct
                    
                    # SSE returns raw PCM data, so we need to concatenate it first
                    raw_audio_data = b''.join(audio_chunks)
                    
                    # Write WAV file with proper header manually (more reliable than wave module for this case)
                    with open(str(output_path), 'wb') as f:
                        # WAV header for 22050Hz, 16-bit, mono
                        f.write(b'RIFF')
                        f.write(struct.pack('<I', 36 + len(raw_audio_data)))  # File size - 8
                        f.write(b'WAVE')
                        f.write(b'fmt ')
                        f.write(struct.pack('<I', 16))  # Subchunk1Size (16 for PCM)
                        f.write(struct.pack('<H', 1))   # AudioFormat (1 = PCM)
                        f.write(struct.pack('<H', 1))   # NumChannels (1 = mono)
                        f.write(struct.pack('<I', 22050))  # SampleRate
                        f.write(struct.pack('<I', 22050 * 2))  # ByteRate (SampleRate * NumChannels * BitsPerSample/8)
                        f.write(struct.pack('<H', 2))   # BlockAlign (NumChannels * BitsPerSample/8)
                        f.write(struct.pack('<H', 16))  # BitsPerSample
                        f.write(b'data')
                        f.write(struct.pack('<I', len(raw_audio_data)))  # Data size
                        f.write(raw_audio_data)  # Write the raw PCM data
                    
                    print(f"✅ Audio saved to: {output_path}")
                    return str(output_path)
                else:
                    print("❌ No audio chunks received")
                    return None
                    
            except Exception as sse_error:
                print(f"❌ SSE generation error: {sse_error}")
                print("💡 Tip: SSE works best with shorter texts (under 500 characters)")
                return None
                
        except Exception as e:
            print(f"❌ Failed to generate simple audio: {str(e)}")
            return None

    def _load_voice_mapping(self):
        """Load voice name to ID mapping"""
        if self.voice_mapping_file.exists():
            with open(self.voice_mapping_file, 'r') as f:
                return json.load(f)
        return {}

    def _update_voice_mapping(self, voice_name, voice_id):
        """Update voice mapping with new voice"""
        mapping = self._load_voice_mapping()
        mapping[voice_name] = voice_id
        
        with open(self.voice_mapping_file, 'w') as f:
            json.dump(mapping, f, indent=4)
        
        print(f"📝 Updated voice mapping: {voice_name} -> {voice_id}")

    def combine_audio_files_hq(self, audio_files, output_filename="combined_48khz.wav", sampling_rate=48000):
        """Combine multiple high-quality audio files maintaining 48kHz sampling rate"""
        try:
            import wave
            import os
            
            output_path = self.output_dir / output_filename
            
            print(f"🔗 Combining {len(audio_files)} audio files at {sampling_rate}Hz...")
            
            with wave.open(str(output_path), 'wb') as output_wav:
                output_wav.setnchannels(1)  # Mono
                output_wav.setsampwidth(2)  # 16-bit samples
                output_wav.setframerate(sampling_rate)  # Use high-quality sampling rate
                
                for i, file_path in enumerate(audio_files):
                    if os.path.exists(file_path):
                        print(f"  📄 Adding file {i+1}/{len(audio_files)}: {os.path.basename(file_path)}")
                        with wave.open(file_path, 'rb') as input_wav:
                            # Verify the input file has the expected sampling rate
                            input_rate = input_wav.getframerate()
                            if input_rate != sampling_rate:
                                print(f"⚠️  Warning: File {file_path} has {input_rate}Hz, expected {sampling_rate}Hz")
                            
                            frames = input_wav.readframes(input_wav.getnframes())
                            output_wav.writeframes(frames)
                    else:
                        print(f"❌ Warning: File {file_path} does not exist. Skipping.")
            
            print(f"✅ High-quality combined audio saved: {output_path}")
            print(f"📊 Final sampling rate: {sampling_rate}Hz")
            return str(output_path)
            
        except Exception as e:
            print(f"❌ Failed to combine audio files: {str(e)}")
            return None

    def create_podcast_from_script(self, script_file, output_filename="podcast_48khz.wav", use_longform=False, speed_mapping=None, use_parallel=False):
        """Create a complete podcast from a script file using high-quality 48kHz audio"""
        try:
            # Default speed mapping if none provided
            if speed_mapping is None:
                speed_mapping = {}
            
            # Process the script file (same format as your original)
            def process_script(input_path):
                with open(input_path, 'r') as file:
                    content = file.read()
                results = []
                splits = content.split('<')
                for split in splits:
                    if '>' in split:
                        voice_name, text = split.split('>', 1)
                        results.append((voice_name.strip(), text.strip()))
                return results
            
            voice_mapping = self._load_voice_mapping()
            processed_script = process_script(script_file)
            
            # Choose processing method
            if use_longform and use_parallel:
                print(f"🎬 Creating podcast from {len(processed_script)} segments using PARALLEL LONGFORM...")
                return self._create_podcast_parallel_longform(processed_script, voice_mapping, speed_mapping, output_filename)
            else:
                print(f"🎬 Creating podcast from {len(processed_script)} segments using SEQUENTIAL processing...")
                return self._create_podcast_sequential(processed_script, voice_mapping, speed_mapping, output_filename, use_longform)
                
        except Exception as e:
            print(f"❌ Failed to create podcast: {str(e)}")
            return None

    def _create_podcast_sequential(self, processed_script, voice_mapping, speed_mapping, output_filename, use_longform):
        """Sequential processing (original method)"""
        audio_files = []
        
        for i, (voice_name, text) in enumerate(processed_script):
            print(f"\n📍 Processing segment {i+1}/{len(processed_script)}: {voice_name}")
            
            voice_id = voice_mapping.get(voice_name)
            if not voice_id:
                print(f"❌ Voice '{voice_name}' not found in mapping. Skipping.")
                continue
            
            # Determine speed for this segment
            speed = speed_mapping.get(voice_name, 1.0)
            
            # Generate individual audio file
            segment_filename = f"segment_{i:03d}_{voice_name}.wav"
            if use_longform:
                audio_file = self.generate_longform_audio(
                    text=text,
                    voice_id=voice_id,
                    output_filename=segment_filename,
                    speed=speed
                )
            else:
                # Use SSE for faster generation
                audio_file = self.generate_simple_audio(
                    text=text,
                    voice_id=voice_id,
                    output_filename=segment_filename,
                    speed=speed
                )
            
            if audio_file:
                audio_files.append(audio_file)
            else:
                print(f"❌ Failed to generate audio for segment {i+1}")
        
        # Combine all segments
        if audio_files:
            # Use appropriate sampling rate based on generation method
            if use_longform:
                # Longform uses 48kHz
                final_podcast = self.combine_audio_files_hq(audio_files, output_filename, sampling_rate=48000)
            else:
                # SSE uses 22kHz
                final_podcast = self.combine_audio_files_hq(audio_files, output_filename, sampling_rate=22050)
            return final_podcast
        else:
            print("❌ No audio files were generated")
            return None

    def _create_podcast_parallel_longform(self, processed_script, voice_mapping, speed_mapping, output_filename):
        """Parallel longform processing with proper ordering"""
        from concurrent.futures import ThreadPoolExecutor
        
        # Prepare tasks with original indices
        tasks = []
        for i, (voice_name, text) in enumerate(processed_script):
            voice_id = voice_mapping.get(voice_name)
            if voice_id:
                speed = speed_mapping.get(voice_name, 1.0)
                segment_filename = f"segment_{i:03d}_{voice_name}.wav"
                tasks.append((i, voice_name, text, voice_id, speed, segment_filename))
            else:
                print(f"❌ Voice '{voice_name}' not found in mapping. Skipping segment {i+1}.")
        
        if not tasks:
            print("❌ No valid segments to process")
            return None
        
        print(f"🚀 Submitting {len(tasks)} longform jobs in parallel...")
        
        def generate_segment(task_data):
            """Generate a single segment in parallel"""
            i, voice_name, text, voice_id, speed, segment_filename = task_data
            print(f"🎵 Starting segment {i+1}: {voice_name} - {text[:50]}...")
            
            try:
                result = self.generate_longform_audio(
                    text=text,
                    voice_id=voice_id,
                    output_filename=segment_filename,
                    speed=speed
                )
                
                if result:
                    print(f"✅ Segment {i+1} ({voice_name}) completed")
                    return (i, result)  # Return with original index
                else:
                    print(f"❌ Segment {i+1} ({voice_name}) failed")
                    return (i, None)
                    
            except Exception as e:
                print(f"❌ Segment {i+1} ({voice_name}) error: {str(e)}")
                return (i, None)
        
        # Run parallel generation
        with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
            results = list(executor.map(generate_segment, tasks))
        
        # Sort results by original script order (critical!)
        results.sort(key=lambda x: x[0])
        
        # Extract successful audio files in correct order
        audio_files_ordered = []
        successful_indices = []
        
        for i, result in results:
            if result:
                audio_files_ordered.append(result)
                successful_indices.append(i+1)
        
        print(f"✅ Parallel processing completed: {len(audio_files_ordered)}/{len(tasks)} segments successful")
        print(f"📋 Successful segments (in script order): {successful_indices}")
        
        if audio_files_ordered:
            print(f"🔗 Combining {len(audio_files_ordered)} segments in correct script order...")
            final_podcast = self.combine_audio_files_hq(
                audio_files_ordered, 
                output_filename, 
                sampling_rate=48000
            )
            
            if len(audio_files_ordered) < len(tasks):
                failed_count = len(tasks) - len(audio_files_ordered)
                print(f"⚠️  Note: {failed_count} segments failed but podcast created with remaining segments in order")
            
            return final_podcast
        else:
            print("❌ All parallel jobs failed - no audio generated")
            return None

def main():
    parser = argparse.ArgumentParser(description='Simple Neuphonic Backend')
    parser.add_argument('action', choices=['list-voices', 'clone-voice', 'generate-audio', 'generate-longform', 'create-podcast'], 
                       help='Action to perform')
    
    # Voice listing options
    parser.add_argument('--cloned-only', action='store_true', 
                       help='Show only cloned voices')
    
    # Voice cloning options
    parser.add_argument('--voice-name', type=str, 
                       help='Name for the cloned voice')
    parser.add_argument('--audio-file', type=str, 
                       help='Path to audio file for cloning')
    parser.add_argument('--tags', type=str, nargs='+', 
                       help='Tags for the cloned voice')
    
    # Audio generation options
    parser.add_argument('--text', type=str, 
                       help='Text to convert to speech')
    parser.add_argument('--voice-id', type=str, 
                       help='Voice ID to use')
    parser.add_argument('--output', type=str, 
                       help='Output filename')
    
    # Podcast creation options
    parser.add_argument('--script', type=str, 
                       help='Path to script file for podcast creation')
    
    args = parser.parse_args()
    
    backend = NeuphonicBackend()
    
    if args.action == 'list-voices':
        backend.list_voices(show_cloned_only=args.cloned_only)
        
    elif args.action == 'clone-voice':
        if not args.voice_name or not args.audio_file:
            print("❌ Voice cloning requires --voice-name and --audio-file")
            return
        backend.clone_voice(args.voice_name, args.audio_file, args.tags)
        
    elif args.action == 'generate-audio':
        if not args.text:
            print("❌ Audio generation requires --text")
            return
        backend.generate_simple_audio(
            args.text, 
            voice_id=args.voice_id, 
            output_filename=args.output
        )
        
    elif args.action == 'generate-longform':
        if not args.text:
            print("❌ Longform generation requires --text")
            return
        backend.generate_longform_audio(
            args.text, 
            voice_id=args.voice_id, 
            output_filename=args.output
        )
        
    elif args.action == 'create-podcast':
        if not args.script:
            print("❌ Podcast creation requires --script")
            return
        backend.create_podcast_from_script(
            args.script, 
            output_filename=args.output or "podcast_48khz.wav"
        )

if __name__ == "__main__":
    backend = NeuphonicBackend()
    
    # Test longform generation with new voice configuration
    print("🎯 Testing LONGFORM generation with Hadrian's Wall script...")
    print("🎙️ Alex = Alex_Demo (bf779307-4b93-41d6-a43e-2099cc93fbc6) - Speed: 0.7x")
    print("🎙️ Rowan = Shiv_48k_A (1af220b3-371e-4e2c-96fb-bfaee9d9525d) - Speed: 0.9x")
    print("🏛️ Using script4.txt (Hadrian's Wall)")
    
    # Update voice mapping for the test
    voice_mapping = {
        "Alex": "bf779307-4b93-41d6-a43e-2099cc93fbc6",  # Alex_Demo
        "Rowan": "1af220b3-371e-4e2c-96fb-bfaee9d9525d",  # Shiv_48k_A
    }
    
    # Save the voice mapping
    with open("voice_mapping.json", "w") as f:
        json.dump(voice_mapping, f, indent=2)
    print("✅ Updated voice_mapping.json")
    
    # Test longform podcast creation
    try:
        output_file = backend.create_podcast_from_script(
            script_file="script4.txt",
            output_filename="hadrians_wall_longform.wav",
            use_longform=True,  # Enable longform generation
            speed_mapping={
                "Alex": 0.7,
                "Rowan": 0.9
            }
        )
        print(f"🎉 SUCCESS! Longform podcast created: {output_file}")
    except Exception as e:
        print(f"❌ Longform generation failed: {e}")
        print("📝 This might indicate the API issue isn't fully resolved yet.") 