# ベースとなるイメージを選択
FROM python:3.9-slim

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y portaudio19-dev libsndfile1 && apt-get clean

# ワーキングディレクトリを設定
WORKDIR /app

# 依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのソースコードをコピー
COPY . .

# アプリケーションの起動コマンドを設定
CMD ["python", "main.py"]