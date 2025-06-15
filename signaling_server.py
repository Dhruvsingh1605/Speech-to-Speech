import asyncio, json
from aiohttp import web, WSMsgType
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, RTCConfiguration, RTCIceServer
from audio_stream import AudioStreamTrack
from video_stream import VideoStreamTrack
from mel_utils import audio_bytes_to_mel_chunks
from asr_server import rec
from llm_server import generate
from tts_server import stream_tts
from lipsync_server import sync

pcs = set()
ice_config = RTCConfiguration(iceServers=[RTCIceServer(urls="stun:stun.l.google.com:19302")])
routes = web.RouteTableDef()

async def process_text(text, audio_q, video_q):
    resp = generate(text)
    for chunk in stream_tts(resp):
        print(f"[Pipeline] putting audio chunk, size: {len(chunk)}")
        await audio_q.put(chunk)
        mels = audio_bytes_to_mel_chunks(chunk)
        for mel in mels:
            frame = sync(mel)
            print("[Pipeline] putting video frame")
            await video_q.put(frame)

@routes.get("/")
async def index(req):
    return web.FileResponse("client.html")

@routes.get("/ws")
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    pc = RTCPeerConnection(ice_config)
    pcs.add(pc)

    audio_q = asyncio.Queue()
    video_q = asyncio.Queue()

    pc.addTrack(AudioStreamTrack(audio_q))
    pc.addTrack(VideoStreamTrack(video_q))

    async def handle_incoming_audio(track, audio_q, video_q):
        print("🟢 Receiving audio from client mic…")
        while True:
            frame = await track.recv()
            pcm = frame.to_ndarray().flatten().tobytes()
            if rec.AcceptWaveform(pcm):
                result = json.loads(rec.Result())["text"]
                print("[ASR] Recognized:", result)
                await process_text(result, audio_q, video_q)

    @pc.on("track")
    def on_track(track):
        if track.kind == "audio":
            print("✅ Server received audio track from client")
            asyncio.create_task(handle_incoming_audio(track, audio_q, video_q))

    @pc.on("icecandidate")
    async def on_icecandidate(event):
        print("Server ICE candidate:", event.candidate)
        if event.candidate:
            await ws.send_json({"candidate": event.candidate.to_sdp()})

    @pc.on("iceconnectionstatechange")
    async def on_ice_connection_change():
        print("Server ICE connection state:", pc.iceConnectionState)

    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            data = json.loads(msg.data)
            if "sdp" in data:
                await pc.setRemoteDescription(RTCSessionDescription(sdp=data["sdp"], type=data["type"]))
                answer = await pc.createAnswer()
                await pc.setLocalDescription(answer)
                await ws.send_json({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})
            elif "candidate" in data:
                await pc.addIceCandidate(RTCIceCandidate.sdp_parse(data["candidate"]))

    await pc.close()
    pcs.discard(pc)
    return ws

if __name__ == "__main__":
    app = web.Application()
    app.add_routes(routes)
    print("🚀 Starting signaling + pipeline server on ws://0.0.0.0:8080/ws")
    web.run_app(app, port=8080)
