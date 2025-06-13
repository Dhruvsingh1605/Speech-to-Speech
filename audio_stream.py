# audio_stream.py
from aiortc import MediaStreamTrack
import av
import numpy as np

class AudioStreamTrack(MediaStreamTrack):
    kind = "audio"

    def __init__(self, audio_queue, sample_rate=22050):
        super().__init__()
        self.audio_queue = audio_queue
        self.sample_rate = sample_rate
        self._ts = 0

    async def recv(self):
        samples = await self.audio_queue.get()  # numpy shape (N,)
        fmt = 'flt' if samples.dtype == np.float32 else 's16'
        frame = av.AudioFrame.from_ndarray(samples, format=fmt, layout='mono')
        frame.sample_rate = self.sample_rate
        frame.pts = self._ts
        frame.time_base = av.AudioFrame.time_base = 1 / self.sample_rate
        self._ts += frame.samples
        return frame
