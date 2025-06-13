# lipsync_server.py
import torch
from PIL import Image
import numpy as np
import sys
sys.path.append("/home/dhruv/Desktop/S-T-T_Pipeline/Wav2Lip")  
from Wav2Lip.models.wav2lip import Wav2Lip

model = torch.jit.load(
    "/home/dhruv/Desktop/S-T-T_Pipeline/Wav2Lip/checkpoints/Wav2Lip-SD-GAN.pt",
    map_location="cuda"  # use "cpu" if no GPU
).eval().cuda()


# Load and preprocess base face image
base_face = Image.open("/home/dhruv/Desktop/S-T-T_Pipeline/avatar_face.png").convert("RGB")
# Resize & normalize
face_size = (96, 96)
base_face = base_face.resize(face_size)
base_face_arr = np.array(base_face) / 255.0
# Format as (C, H, W) tensor
face_tensor = torch.FloatTensor(base_face_arr).permute(2, 0, 1).unsqueeze(0).cuda()

def sync(mel_chunk: np.ndarray) -> np.ndarray:
    """
    Sync lips for one mel chunk, returning a frame.
    mel_chunk: numpy array shape (mel_length, mel_bins)
    """

    # Prepare mel spectrogram for model
    mel = torch.FloatTensor(mel_chunk).unsqueeze(0).unsqueeze(0).cuda()

    with torch.no_grad():
        pred = model(mel, face_tensor)
    
    # post-process & reshape
    pred = pred.squeeze(0).cpu().permute(1, 2, 0).numpy()
    pred = (pred * 255).astype(np.uint8)
    return pred
