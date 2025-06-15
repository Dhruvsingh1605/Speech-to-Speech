import os
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"
import torch
import asyncio
from asr_server import transcribe
from llm_server import generate
from tts_server import stream_tts
from lipsync_server import sync
from webrtc_stream import run
from signaling_server import pcs
from PIL import Image

preload_face_img = Image.open("avatar_face.png").convert("RGB")

audio_q = asyncio.Queue()
video_q = asyncio.Queue()


async def pipeline():
    loop = asyncio.get_event_loop()

    def asr_callback(text):
        audio_q.put_nowait(text)

    asyncio.get_event_loop().run_in_executor(None, transcribe, asr_callback)

    while True:
        text = await audio_q.get()
        reply = generate(text)
        mel_gen = stream_tts(reply)
        for mel in mel_gen:
            frame = sync(preload_face_img, mel)
            await video_q.put(frame)

asyncio.run(pipeline())
