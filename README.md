# 🎭 Real‑Time Open‑Source Avatar Pipeline

A full open-source system that transforms speech into talking avatars in near real time, using ASR → LLM → TTS → lip-sync → WebRTC streaming.

---

## 🚀 Technologies & Why They're Used

### 1. **Vosk** – Streaming ASR
- 📦 Offline, on-device speech-to-text toolkit with small (~50 MB) models  
- Offers **zero-latency streaming transcription** for smooth conversational turn-taking :contentReference[oaicite:1]{index=1}  
- Chosen for its speed, reliability, and privacy (runs locally)

---

### 2. **Local LLM (Hugging Face Model, e.g. Qwen‑7B‑chat)**
- 💬 Enables context-aware, dynamic replies without external APIs  
- Runs on GPU in `torch.float16` for fast (<300 ms) inference on a single consumer GPU  
- Keeps processing private and cost-effective

---

### 3. **Coqui TTS – Streaming Text-to-Speech**
- 🗣 Offers incremental, chunk-based audio synthesis (~50 ms chunks) for low-latency speech  
- Designed to start speaking as text is generated, avoiding delays :contentReference[oaicite:2]{index=2}

---

### 4. **Wav2Lip** – Real-Time Lip Sync
- 🎥 GAN-based lip-sync model that adapts any static face to the speech audio  
- Proven to work in real-time (~25–30 FPS) and is highly accurate with unseen identities :contentReference[oaicite:3]{index=3}  
- Provides visually convincing lip movements

---

### 5. **WebRTC (via aiortc + aiohttp)** – Real-Time Streaming
- 🌐 Peer-to-peer audio/video framework built on **asyncio**  
- Leverages **SDP + ICE over WebSockets** for signaling between the browser and Python server :contentReference[oaicite:4]{index=4}  
- Delivers sub-100 ms latency media streams

---

### 6. **asyncio** – High-Concurrency Pipeline
- Enables **non-blocking, concurrent stages** for ASR, LLM, TTS, lip-sync, and media streaming  
- Manages **queues and buffers** efficiently to maintain responsiveness

---

## 🧭 Workflow (Step-by-Step)

1. **Mic Audio → Vosk**  
   Captured in ~50 ms chunks → real-time transcription (partial & final)  
2. **LLM**  
   Converts transcripts into responsive dialogue  
3. **Coqui TTS**  
   Synthesizes speech in streaming chunks (~50 ms each)  
4. **Wav2Lip**  
   For each mel chunk, generates a matching facial frame using a single reference image  
5. **Media Queues & aiortc**  
   Frames and audio chunks are queued → streamed via WebRTC to the browser  
6. **Browser (`client.html`)**  
   Negotiates peers using WebSocket signaling → displays synchronized audio+video

---

## ⏱ Latency Breakdown (Target)

| Stage         | Target Latency |
|---------------|----------------|
| ASR           | ≤ 50 ms        |
| LLM           | ~200 ms        |
| TTS           | ~50 ms startup + streaming |
| Wav2Lip       | ~30–40 ms/frame |
| WebRTC        | ≤ 100 ms network delay |
| **Total**     | **~400–500 ms** (per chunk)

This achieves convincing real-time interaction comparable to commercial systems.

---

## 📁 Project Architecture

open_avatar/
│
├── asr_server.py # Vosk-based real-time audio transcription
├── llm_server.py # Local LLM generation logic
├── tts_server.py # Chunked TTS streaming via Coqui
├── lipsync_server.py # Wav2Lip-driven lip-sync, loading avatar image
├── signaling_server.py # Signaling using aiohttp WebSockets
├── webrtc_stream.py # aiortc tracks and streaming logic
├── main.py # Async orchestration pipeline wiring components
├── client.html # Browser client for SDP/ICE exchange and playback
└── requirements.txt


Each component is modular—swap models or SDKs, or scale them independently.

---

## ✅ Why This Setup is Effective

- **All Open-Source & Local**: No proprietary APIs—data stays private.
- **Real-Time Performance**: Streaming at each stage, with async concurrency.
- **Flexible & Modular**: Replace components (e.g. MuseTalk instead of Wav2Lip) with minimal changes :contentReference[oaicite:5]{index=5}.
- **Low Barrier to Entry**: Only Python 3.10+, consumer GPU, and pip installs required.

---

## 📌 Getting Started

Add setup steps here…

---

### References
- Vosk real-time ASR :contentReference[oaicite:6]{index=6}  
- Wav2Lip architecture & effectiveness :contentReference[oaicite:7]{index=7}  
- aiortc & asyncio for WebRTC :contentReference[oaicite:8]{index=8}  
- Streaming audio & video synchronization best practices

---

This README gives an in-depth, technical overview of your architecture, the rationale behind each component, and how they work together to deliver a real-time, open-source avatar experience.

Let me know if you'd like me to add installation steps, Docker setup, or performance benchmarks!
::contentReference[oaicite:9]{index=9}


## 📡 What is WebRTC?

WebRTC—**Web Real-Time Communication**—is an open-source framework (initially released by Google in 2011) that enables **real-time peer-to-peer audio, video, and data streaming** directly between clients (browsers or native apps) :contentReference[oaicite:1]{index=1}.  

Key highlights:
- Uses **RTP/SRTP** for low-latency media streaming over UDP, typically under 500 ms :contentReference[oaicite:2]{index=2}.
- Handles network traversal via **ICE**, **STUN**, and **TURN** protocols :contentReference[oaicite:3]{index=3}.
- All WebRTC media is **automatically encrypted** via DTLS/SRTP :contentReference[oaicite:4]{index=4}.
- Exposes easy-to-use browser APIs like `RTCPeerConnection`, `getUserMedia()`, and `RTCDataChannel` :contentReference[oaicite:5]{index=5}.

### Why it’s used here:
- Enables **live video and audio streaming** of your lip-synced avatar to a browser with minimal lag.
- Works with **aiortc** in Python to implement signaling and media transport entirely in open-source.

---

## 🛠️ Libraries & Modules Used

### ✅ `aiohttp`
- Offers lightweight **async HTTP & WebSocket** support.
- Handles the **signaling channel** (SDP and ICE exchange) between browser and server.

### ✅ `aiortc`
- Native Python WebRTC implementation built on `asyncio`.
- Manages **peer connections**, **tracks**, **RTP/RTCP**, **DTLS/SRTP**, and **media relays** :contentReference[oaicite:6]{index=6}.
- Includes utilities like `MediaRecorder` (for file recording via FFmpeg) and `MediaRelay`.

### ✅ `asyncio`
- Enables **non-blocking**, **concurrent execution** of separate pipeline stages: ASR, LLM, TTS, lip-sync, streaming.
- Manages **queues and buffering** without blocking the media flow.

---

## 🤖 AI Modules

### ✅ `Vosk` – ASR
- **Offline**, low-latency speech recognition.
- Streams partial results in ~50 ms, ideal for real-time transcription without external API calls.

### ✅ `transformers` + `torch` – Local LLM
- Enables **contextual response generation** with zero external dependency.
- Uses `torch.float16` on GPU for faster inference (~200 ms per prompt).

### ✅ `Coqui TTS` – Streaming Text-to-Speech
- Can **stream audio chunks** (~50 ms) as text is generated.
- Vital for overlapping TTS + lip-sync work efficiently.

### ✅ `Wav2Lip` – Real-Time Lip Sync
- GAN-based lip-sync engine that binds audio chunks to your **static avatar image**.
- Executes in real-time (~30–40 ms per frame).

---

## 🎞 Media Components & FFmpeg

- **aiortc** uses **PyAV/FFmpeg** under the hood for encoding/recording.
- Though not required for **direct WebRTC streaming**, FFmpeg becomes useful when:
  - **Recording** the avatar to a file (e.g., `.mp4`, `.webm` via `MediaRecorder`) :contentReference[oaicite:7]{index=7}.
  - **Transcoding** media or handling external camera/webcam inputs.

---

## 🔄 Overall Pipeline

```text
Browser client (client.html)
    ↕ (WebSocket for SDP/ICE)
Signaling (aiohttp)
    ↕
Media (aiortc with asyncio)

real-time pipeline:
Mic → Vosk ASR → LLM → Coqui TTS (streaming) → Wav2Lip lip-sync → aiortc WebRTC → Browser video display


🔄 Workflow Breakdown
Terminal 1 (signaling_server.py):
Listens on ws://localhost:8080/ws to manage SDP and ICE exchanges with the browser.

Terminal 2 (main.py):
Processes microphone input, generates audio and video frames, and sends media via aiortc through the established peer connection.

Terminal 3 (http.server 8000):
Makes client.html accessible in your browser at http://localhost:8000/client.html.

