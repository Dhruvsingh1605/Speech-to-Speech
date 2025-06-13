# mel_utils.py
import numpy as np
import librosa

def audio_bytes_to_mel_chunks(audio_bytes, sample_rate=22050, n_fft=1024,
                              hop_length=200, win_length=800, n_mels=80):
    waveform = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    mel = librosa.feature.melspectrogram(
        y=waveform,
        sr=sample_rate,
        n_fft=n_fft,
        hop_length=hop_length,
        win_length=win_length,
        n_mels=n_mels
    )
    mel_db = librosa.power_to_db(mel, ref=np.max)
    mel_norm = mel_db / 80.0 + 1
    return mel_norm.T.astype(np.float32)  # time × mel_bins
