# import vosk
# import sys
# import sounddevice as sd
# import queue
# import json
#
# model = vosk.Model("model_small")
# samplerate = 16000
# device = 1
#
# q = queue.Queue()
#
#
# def q_callback(indata, frames, time, status):
#     if status:
#         print(status, file=sys.stderr)
#     q.put(bytes(indata))
#
#
# def va_listen(callback):
#     with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device, dtype='int16',
#                            channels=1, callback=q_callback):
#
#         rec = vosk.KaldiRecognizer(model, samplerate)
#         while True:
#             data = q.get()
#             if rec.AcceptWaveform(data):
#                 callback(json.loads(rec.Result())["text"])

import pyaudio
import websockets
import asyncio
import base64
import json
import webbrowser
from deepgram import Deepgram


dg_client = Deepgram("5d0fd764-a200-4ed9-8e8a-4d0440b9161f")
deepgramLive = await Deepgram.transcription.live({'language': 'rus'})
deepgramLive.registerHandler(deepgramLive.event.OPEN, lambda c: print(f'Connection opened'))
deepgramLive.registerHandler(deepgramLive.event.MESSEGE, lambda c: print(f'Messege is ready for send {c}.'))

async def connect():
    async with websockets.connect('wss://api.speechace.co/websocket/asr?lang=en-US') as websocket:
        await websocket.send(json.dumps({
            "action": "start",
            "content-type": "audio/webm",
            "continuous": True,
            "interim_results": True,
            "word_confidence": True,
            "timestamps": True,
            "max_alternatives": 1,
            "inactivity_timeout": 600,
            "background_noise_suppression": False
        }))

        async for message in websocket:
            print(message)


