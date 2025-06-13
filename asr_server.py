
from vosk import Model, KaldiRecognizer
import sounddevice as sd, queue, json

q = queue.Queue()
model = Model("/home/dhruv/Desktop/S-T-T_Pipeline/vosk-model-small-en-us-0.15")
rec = KaldiRecognizer(model, 16000)

def callback(indata, frames, time, status):
    q.put(bytes(indata))

def transcribe(callback_fn):
    with sd.RawInputStream(samplerate=16000, blocksize=8000,
                           dtype='int16', channels=1, callback=callback):
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                callback_fn(result["text"])
            else:
                partial = json.loads(rec.PartialResult())
                callback_fn(partial.get("partial", ""))

if __name__=="__main__":
    def print_cb(txt): print("[ASR]", txt)
    transcribe(print_cb)
