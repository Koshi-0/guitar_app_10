from flask import render_template, request, redirect, url_for, jsonify
from app import app
from utils.spectrogram import convert_to_spectrogram
from models.net import inference_cnn
import os
from werkzeug.utils import secure_filename

import pyaudio
import wave
import io
import base64

from threading import Thread, Event

# 録音のパラメータ
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 3
WAVE_OUTPUT_FILENAME = "recorded_audio.wav"

# メトロノームのパラメータ
METRONOME_FILE = os.path.join(app.root_path, 'static', 'metronome.wav')

@app.route('/')
def index():
    return render_template('index.html')

def play_metronome(event):
    wf = wave.open(METRONOME_FILE, 'rb')

    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(CHUNK)

    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()

    p.terminate()
    event.set()

def get_input_device_index(target_name="M-Audio"):
    p = pyaudio.PyAudio()
    device_index = None

    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if target_name in info['name'] and info['maxInputChannels'] > 0:
            device_index = i
            break

    # ここでデバイスのインデックスをログに出力
    print("Selected device index:", device_index)
    return device_index

@app.route('/start_recording', methods=['GET'])
def start_recording():
    event = Event()
    thread = Thread(target=play_metronome, args=(event,))
    thread.start()
    event.wait() 

    input_device_index = get_input_device_index()  # オーディオインターフェースの自動検出

    if input_device_index is not None:
        global p, stream
        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=input_device_index,  # 自動検出したインターフェースのインデックス
                        frames_per_buffer=CHUNK)

        print("* recording")

        global frames
        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("* done recording")
        
        # Close the stream
        stream.stop_stream()
        stream.close()
        p.terminate()

        # Save the recording to a BytesIO object instead of a file
        with io.BytesIO() as buffer:
            wf = wave.open(buffer, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            audio_data = buffer.getvalue()

        # audio_dataをBase64でエンコード
        audio_data_encoded = base64.b64encode(audio_data).decode('utf-8')

        return jsonify({'status': 'done', 'audio_data': audio_data_encoded})

    else:
        return jsonify({'status': 'error', 'message': 'No audio interface with an available input channel found.'})

@app.route('/upload', methods=['POST'])
def upload_file():
    audio_data_encoded = request.json['audio_data']
    audio_data = base64.b64decode(audio_data_encoded)
    audio_file = io.BytesIO(audio_data)

    # スペクトログラムの作成
    spectrogram_file = convert_to_spectrogram(audio_file)

    # ステータスメッセージとコード名を取得
    chord_name = inference_cnn(spectrogram_file)
    response_data = {'status': 'converting', 'chord_name': chord_name}

    # 結果を表示する
    return jsonify(response_data)

@app.route('/list_audio_devices', methods=['GET'])
def list_audio_devices():
    p = pyaudio.PyAudio()
    devices = []
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        devices.append(info)
        print(info)
    return "Listed all audio devices in console."