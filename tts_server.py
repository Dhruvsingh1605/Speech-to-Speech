# tts_server.py
from TTS.api import TTS

tts = TTS("tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=True)

def stream_tts(text):
    for chunk in tts.stream(text, chunk_size=0.05):
        yield chunk
