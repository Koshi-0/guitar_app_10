import os
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt

def convert_to_spectrogram(audio_file, upload_folder):
     # オーディオファイルを読み込み（サンプリングレートも取得）
        audio_data, sample_rate = librosa.load(audio_file)

        # STFTを計算
        stft = librosa.stft(audio_data)

        # スペクトログラムに変換
        spectrogram = librosa.amplitude_to_db(np.abs(stft))

        # 保存用のファイル名を生成（拡張子を除いたファイル名を使用）
        file_name_without_extension = os.path.splitext(os.path.basename(audio_file))[0]
        save_path = os.path.join(upload_folder, file_name_without_extension + '_spectrogram.png')

        # スペクトログラムを画像として保存
        plt.figure(figsize=(8,6))
        librosa.display.specshow(spectrogram, sr=sample_rate, x_axis='time', y_axis='log')

        plt.savefig(save_path)
        plt.close()  # プロットのクローズ

        return save_path