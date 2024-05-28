import os
from fuzzywuzzy import fuzz
import pvporcupine
import vosk
import queue
import sys
import time
from pvrecorder import PvRecorder
import struct
import json
import subprocess
import yaml
import openai
from openai import error
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import (
    AudioUtilities,
    IAudioEndpointVolume
)

import config
import tts


print(f"{config.VA_NAME} начал свою работу ...")


CDIR = os.getcwd()
print(CDIR)
VA_CMD_LIST = yaml.safe_load(
    open('commands.yaml', 'rt', encoding='utf8'),
)

system_message = {"role": "system", "content": "Ты тестовый голосовой ассистент"}
message_log = [system_message]

openai.api_key = config.OPENAI_TOKEN

porcupine = pvporcupine.create(
    access_key=config.PICOVOICE_TOKEN,
    keywords=['americano'],
    sensitivities=[1]
)


# VOSK
model = vosk.Model("model_small")
samplerate = 16000
device = config.MICROPHONE_INDEX
kaldi_rec = vosk.KaldiRecognizer(model, samplerate)
q = queue.Queue()

def gpt_answer():
    global message_log

    model_engine = "gpt-3.5-turbo"
    max_tokens = 256  # default 1024
    try:
        response = openai.ChatCompletion.create(
            model=model_engine,
            messages=message_log,
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=1,
            stop=None
        )
    except (error.TryAgain, error.ServiceUnavailableError):
        return "ChatGPT перегружен!"
    except openai.OpenAIError as ex:
        # если ошибка - это макс длина контекста, то возвращаем ответ с очищенным контекстом
        if ex.code == "context_length_exceeded":
            message_log = [system_message, message_log[-1]]
            return gpt_answer()
        else:
            return "OpenAI токен не действителен"

    # Находит первый ответ от чат-бота, в котором есть текст (при условии, что в сообщении есть текст)
    for choice in response.choices:
        if "text" in choice:
            return choice.text

    # Если ответ с текстом не найден, вернуть содержимое первого ответа (которое может быть пустым)
    return response.choices[0].message.content


def q_callback(indata, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


def va_respond(voice: str):
    global recorder, message_log, first_request
    print(f"Распознано: {voice}")

    cmd = recognize_cmd(filter_cmd(voice))

    print(cmd)
    if len(cmd['cmd'].strip()) <= 0:
                return False
    if fuzz.ratio(voice.join(voice.split()[:1]).strip(), "скажи") > 75:
        message_log.append({"role": "user", "content": voice})
        response = gpt_answer()
        recorder.stop()
        tts.va_speak(response)
        time.sleep(0.7)
        recorder.start()
        return False
    else:
        execute_cmd(cmd['cmd'], voice)
        return True

def filter_cmd(raw_voice: str):
    cmd = raw_voice

    for x in config.VA_ALIAS:
        cmd = cmd.replace(x, "").strip()

    for x in config.VA_TBR:
        cmd = cmd.replace(x, "").strip()

    return cmd


def recognize_cmd(cmd: str):
    rc = {'cmd': '', 'percent': 0}
    for c, v in VA_CMD_LIST.items():
        for x in v:
            vrt = fuzz.ratio(cmd, x)
            if vrt > rc['percent']:
                rc['cmd'] = c
                rc['percent'] = vrt

    return rc


def execute_cmd(cmd: str, voice: str):
    if cmd == 'open_browser':
        subprocess.Popen([f'{CDIR}\\custom-commands\\Run browser.exe'])

    elif cmd == 'open_youtube':
        subprocess.Popen([f'{CDIR}\\custom-commands\\Run youtube.exe'])

    elif cmd == 'run_music':
        subprocess.Popen([f'{CDIR}\\custom-commands\\Run music.exe'])

    elif cmd == 'music_off':
        subprocess.Popen([f'{CDIR}\\custom-commands\\Stop music.exe'])
        time.sleep(0.2)

    elif cmd == 'music_save':
        subprocess.Popen([f'{CDIR}\\custom-commands\\Save music.exe'])
        time.sleep(0.2)

    elif cmd == 'music_next':
        subprocess.Popen([f'{CDIR}\\custom-commands\\Next music.exe'])
        time.sleep(0.2)

    elif cmd == 'sound_off':
        tts.va_speak("Отключаю звук ...")
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMute(1, None)

    elif cmd == 'sound_on':
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMute(0, None)
        tts.va_speak("Хорошо")

    elif cmd == 'music_prev':
        subprocess.Popen([f'{CDIR}\\custom-commands\\Prev music.exe'])
        time.sleep(0.2)

    elif cmd == 'off':
        tts.va_speak("Отключаю")

        porcupine.delete()
        exit(0)

recorder = PvRecorder(device_index=config.MICROPHONE_INDEX, frame_length=porcupine.frame_length)
recorder.start()
print('Using device: %s' % recorder.selected_device)

print(f"Голосовой ассистент начал свою работу ...")
time.sleep(0.5)

ltc = time.time() - 1000

while True:
    try:
        pcm = recorder.read()
        keyword_index = porcupine.process(pcm)

        if keyword_index >= 0:
            recorder.stop()
            tts.va_speak("Слушаю вас")
            print("Слушаю вас")
            recorder.start()  # prevent self recording
            ltc = time.time()

        while time.time() - ltc <= 10:
            pcm = recorder.read()
            sp = struct.pack("h" * len(pcm), *pcm)

            if kaldi_rec.AcceptWaveform(sp):
                if va_respond(json.loads(kaldi_rec.Result())["text"]):
                    ltc = time.time()

                break

    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise

