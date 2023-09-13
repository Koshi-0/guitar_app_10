import os
import numpy as np
import librosa
import librosa.display

import matplotlib
matplotlib.use('Agg')  # GUIの問題を回避
import matplotlib.pyplot as plt

import io

def convert_to_spectrogram(audio_file):
     # オーディオファイルを読み込み（サンプリングレートも取得）
        audio_data, sample_rate = librosa.load(audio_file, sr=None)

        # STFTを計算
        stft = librosa.stft(audio_data)

        # スペクトログラムに変換
        spectrogram = librosa.amplitude_to_db(np.abs(stft))

        # スペクトログラムを画像としてバッファに保存
        with io.BytesIO() as buffer:
         plt.figure(figsize=(8, 6))
         librosa.display.specshow(spectrogram, sr=sample_rate, x_axis='time', y_axis='log')
         plt.savefig(buffer, format='png')
         plt.close()  # プロットのクローズ

         buffer.seek(0)
         img_data = buffer.getvalue()

         return img_data