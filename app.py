import asyncio, json
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
from audio_stream import AudioStreamTrack
from video_stream import VideoStreamTrack
from mel_utils import audio_bytes_to_mel_chunks
from asr_server import transcribe
from llm_server import generate
from tts_server import stream_tts
from lipsync_server import sync

pcs = set()
ice_config = RTCConfiguration(iceServers=[RTCIceServer(urls="stun:stun.l.google.com:19302")])

async def pipeline(audio_q, video_q):
    def asr_cb(text):
        asyncio.get_event_loop().create_task(process_text(text, audio_q, video_q))

    transcribe(asr_cb)

async def process_text(text, audio_q, video_q):
    resp = generate(text)
    for chunk in stream_tts(resp):
        await audio_q.put(chunk)
        mels = audio_bytes_to_mel_chunks(chunk)
        for mel in mels:
            frame = sync(mel)
            await video_q.put(frame)

routes = web.RouteTableDef()

@routes.get("/")
async def index(req):
    return web.FileResponse("client/index.html")

@routes.post("/offer")
async def offer(req):
    params = await req.json()

    pc = RTCPeerConnection(ice_config)
    pcs.add(pc)

    # Add transceivers *before* setting remote desc to ensure recvonly directions
    pc.addTransceiver("audio", direction="recvonly")
    pc.addTransceiver("video", direction="recvonly")

    audio_q = asyncio.Queue()
    video_q = asyncio.Queue()

    pc.addTrack(AudioStreamTrack(audio_q))
    pc.addTrack(VideoStreamTrack(video_q))

    @pc.on("connectionstatechange")
    async def on_state_change():
        if pc.connectionState in ["failed", "closed"]:
            await pc.close()
            pcs.discard(pc)

    asyncio.create_task(pipeline(audio_q, video_q))

    # Now set remote and answer
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.json_response({
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    })


app = web.Application()
app.add_routes(routes)
web.run_app(app, port=8080)
