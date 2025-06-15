# video_stream.py
from aiortc import MediaStreamTrack
import av

class VideoStreamTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, video_queue):
        super().__init__()
        self.video_queue = video_queue

    async def recv(self):
        img = await self.video_queue.get()
        print(f"[Video recv] got frame shape {img.shape}")
        frame = av.VideoFrame.from_ndarray(img, format="rgb24")
        frame.pts, frame.time_base = await self.next_timestamp()
        return frame
