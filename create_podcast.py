import os
from pyneuphonic import Neuphonic, TTSConfig
import json
import time
import requests
import wave
import asyncio

semaphore = asyncio.Semaphore(3)

# Secure API key handling - use environment variable
API_KEY = os.getenv('NEUPHONIC_API_KEY')
if not API_KEY:
    print("⚠️  Error: NEUPHONIC_API_KEY environment variable not set.")
    print("   Please set your API key:")
    print("   export NEUPHONIC_API_KEY='your_actual_api_key'")
    print("   Or create a .env file with: NEUPHONIC_API_KEY=your_actual_api_key")
    raise ValueError("Missing NEUPHONIC_API_KEY environment variable")

def download_wav_from_presigned_url(job_id, presigned_url: str, output_path: str = 'output'):
    try:
        response = requests.get(presigned_url)
        response.raise_for_status()  # Raise exception for bad HTTP status
        wav_data = response.content
        if not wav_data:
            print("No data received from presigned URL.")
            return
        file_path = output_path + f"/{job_id}.wav"
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        with open(file_path, 'wb') as f:
            f.write(wav_data)
    except requests.RequestException as e:
        print(f"Failed to download file: {e}")



def generate_line(tts_client, text: str, voice_id: str = "None"):
    tts_config = TTSConfig(lang_code='en', voice_id = voice_id)
    response = tts_client.post(text=text, tts_config=tts_config)
    response = json.loads(response.data)
    if response["status_code"] != 200: 
        raise Exception(f"Failed to generate job: {response['errors']}")
    return response["data"]["job_id"]

def process_script(input_path = None):
    if input_path is None:
        return []
    content = []
    with open(input_path, 'r') as file:
        content = file.read()
    results = []
    splits= content.split('<')
    for split in splits:
        if '>' in split:
            voice_name, text = split.split('>', 1)
            results.append((voice_name.strip(), text.strip()))
    return results

def combine_audio_files(job_ids, output_path: str = 'output.wav'):
    output_file_path = os.path.join(output_path, 'podcast.wav')
    with wave.open(output_file_path, 'wb') as output_wav:
        output_wav.setnchannels(1)  # Mono
        output_wav.setsampwidth(2)  # 16-bit samples
        output_wav.setframerate(48000)  # Sample rate
        for job_id in job_ids:
            file_path = os.path.join(output_path, f"{job_id}.wav")
            if os.path.exists(file_path):
                with wave.open(file_path, 'rb') as input_wav:
                    frames = input_wav.readframes(input_wav.getnframes())
                    output_wav.writeframes(frames)
            else:
                print(f"Warning: File {file_path} does not exist. Skipping.")
    print(f"Combined audio saved to {output_file_path}")
    
    

def create_podcast_line(voice_name, text, output_path: str = 'output.wav', voice_name_to_id_mapping = None):
    # Initialize the TTS client
    client = Neuphonic(api_key=API_KEY)
    tts = client.tts.LongformInference()
    voice_id = voice_name_to_id_mapping[voice_name]
    print(f"Processing voice: {voice_name} with ID: {voice_id} and text: {text}")
    job_id = generate_line(tts, text, voice_id=voice_id)
    if job_id == None: 
        raise Exception(f"Failed to generate job for voice {voice_name} with text: {text}")
    print(f"Generated job ID: {job_id} for voice: {voice_id}")
    if job_id:
        raw_response = tts.get(job_id)
        response = json.loads(raw_response.data)
        while response["status_code"] != 200:
            print(f"Job {job_id} not ready yet, waiting...")
            time.sleep(5)
            raw_response = tts.get(job_id)
            if raw_response.errors:
                raise Exception(f"Error getting job {job_id}: {raw_response.errors}")
            response = json.loads(raw_response.data)
        if response["status_code"] == 200:
            audio_url = response['data']['audio_url']
            print(f"Presigned URL for job {job_id}: {audio_url}")
            download_wav_from_presigned_url(job_id, audio_url,output_path)
        else:
            raise Exception(f"Failed to get presigned URL for job {job_id}: {response['errors']}")
    return job_id

async def create_podcast(input_path = None, output_path: str = 'output.wav', voice_name_to_id_mapping = None, concurrency_limit: int = 3):
    processed_script = process_script(input_path)
    all_job_ids = [None] * len(processed_script)  # pre-allocate ordered list
    async def runner(index, voice_name, text):
        async with semaphore:
            job_id = await asyncio.to_thread(create_podcast_line, voice_name, text, output_path, voice_name_to_id_mapping)
            if job_id is None:
                raise Exception(f"Failed to create job for line {index}: {voice_name} with text: {text}")
            all_job_ids[index] = job_id  # store at correct position
    tasks = [asyncio.create_task(runner(i, voice_name, text)) for i, (voice_name, text) in enumerate(processed_script)]
    await asyncio.gather(*tasks)
    print(f"All jobs completed. Job IDs: {all_job_ids}")
    combine_audio_files(all_job_ids, output_path)


def main(input_path='script.txt', output_path='./podcast', voice_name_to_id_mapping=None):
    if voice_name_to_id_mapping is None:
        raise Exception("Voice name to ID mapping is required. Please provide a valid mapping.")
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"The input script file {input_path} does not exist.")
    asyncio.run(create_podcast(input_path, output_path, voice_name_to_id_mapping))
    print(f"Podcast created and saved to {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Create a podcast from a script.')
    parser.add_argument('--input', type=str, help='Path to the script file.')
    parser.add_argument('--voice_mapping', type=str, help='Path to the voice mapping JSON file.')
    parser.add_argument('--output', type=str, default='output.wav', help='Path to save the output podcast.')
    args = parser.parse_args()

    if args.voice_mapping:
        with open(args.voice_mapping, 'r') as f:
            voice_name_to_id_mapping = json.load(f)

    main(input_path=args.input, 
         output_path=args.output, 
         voice_name_to_id_mapping=voice_name_to_id_mapping if args.voice_mapping else None)
    
    # Command line usage example:
    # python create_podcast.py --input script.txt --voice_mapping voice_mapping.json --output podcast