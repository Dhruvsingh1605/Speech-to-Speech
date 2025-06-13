const pc = new RTCPeerConnection();

// Here's where your snippet goes:
pc.addTransceiver("audio", { direction: "recvonly" });
pc.addTransceiver("video", { direction: "recvonly" });

async function negotiate() {
  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);

  // Wait for ICE gathering
  await new Promise(resolve => {
    if (pc.iceGatheringState === "complete") return resolve();
    pc.addEventListener("icegatheringstatechange", () => {
      if (pc.iceGatheringState === "complete") resolve();
    });
  });

  const resp = await fetch("/offer", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sdp: pc.localDescription.sdp,
      type: offer.type
    })
  });
  const answer = await resp.json();
  await pc.setRemoteDescription(answer);
}

pc.ontrack = evt => {
  if (evt.track.kind === "video") {
    document.getElementById("remote").srcObject = evt.streams[0];
  }
};

// Kick things off
negotiate();
