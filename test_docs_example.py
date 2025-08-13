import os
from pyneuphonic import Neuphonic, TTSConfig
from pyneuphonic.player import AudioPlayer

# Ensure the API key is set in your environment
client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_KEY'))

tts = client.tts.LongformInference()

# TTSConfig is a pydantic model so check out the source code for all valid options
tts_config = TTSConfig(
    lang_code='en', # replace the lang_code with the desired language code.
    sampling_rate=48000, # for Longform Inference, it is possible to use 48 kHz sampling rate
    voice_id=None
)

post_response = tts.post(
        text = "Testing the Longform Inference",
        tts_config=tts_config
    )
print(post_response) 