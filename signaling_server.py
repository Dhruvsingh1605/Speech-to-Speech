# signaling_server.py
import json
from aiohttp import web, WSMsgType
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate

pcs = set()
routes = web.RouteTableDef()

@routes.get("/ws")
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    pcs.add(PC := RTCPeerConnection())

    @PC.on("icecandidate")
    async def on_icecandidate(event):
        print("Server ICE candidate:", event.candidate)
        if event.candidate:
            await ws.send_json({ "candidate": event.candidate.to_sdp() })

    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            data = json.loads(msg.data)
            if "sdp" in data:
                print("Server received SDP offer from client")
                await PC.setRemoteDescription(RTCSessionDescription(
                    sdp=data["sdp"], type=data["type"]
                ))
                answer = await PC.createAnswer()
                await PC.setLocalDescription(answer)
                print("Server sending SDP answer to client")
                await ws.send_json({
                    "sdp": PC.localDescription.sdp,
                    "type": PC.localDescription.type
                })
            elif "candidate" in data:
                print("Server received ICE candidate from client")
                await PC.addIceCandidate(RTCIceCandidate.sdp_parse(data["candidate"]))
    await PC.close()
    pcs.discard(PC)
    return ws

app = web.Application()
app.add_routes(routes)

if __name__ == "__main__":
    print("Starting signaling server on ws://0.0.0.0:8080/ws")
    web.run_app(app, port=8080)
