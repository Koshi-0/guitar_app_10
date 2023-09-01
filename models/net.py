# 必要なモジュールのインポート
from torchvision import transforms
from PIL import Image
import pytorch_lightning as pl
import torch
import torch.nn.functional as F
import torch.nn as nn
import os

# 学習済みモデルに合わせた前処理を追加
transform = transforms.Compose([
    transforms.ToTensor()
])

#　ネットワークの定義
class Net(pl.LightningModule):

    def __init__(self):
        super().__init__()

        #学習時に使ったのと同じ学習済みモデルを定義
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=6, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(6)
        self.conv2 = nn.Conv2d(in_channels=6, out_channels=12, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(12)
        self.conv3 = nn.Conv2d(in_channels=12, out_channels=12, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(12)
        self.fc = nn.Linear(90000,28)

    def forward(self, x):
        #学習時に使ったのと同じ順伝播
        h = self.conv1(x)
        h = F.relu(h)
        h = self.bn1(h)
        h = F.max_pool2d(h, kernel_size=2, stride=2)

        h = self.conv2(h)
        h = F.relu(h)
        h = self.bn2(h)
        h = F.max_pool2d(h, kernel_size=2, stride=2)

        h = self.conv3(h)
        h = F.relu(h)
        h = self.bn3(h)
        h = F.max_pool2d(h, kernel_size=2, stride=2)

        h = h.view(-1, 90000)
        h = self.fc(h)
        return h

#　推論したラベルからコード名を返す関数
def getName(label):
    chord_names = [
        'A', 'AM7', 'Am', 'Am7', 'B',
        'BM7', 'Bm', 'Bm7', 'C', 'CM7',
        'Cm', 'Cm7', 'D', 'DM7', 'Dm',
        'Dm7', 'E', 'EM7', 'Em', 'Em7',
        'F', 'FM7', 'Fm', 'Fm7', 'G',
        'GM7', 'Gm', 'Gm7'
    ]
    return chord_names[label]

# 推論
def inference_cnn(img_path, model_path=os.path.join('..', 'models', 'M7&m7.pt')):
    # モデルの初期化と読み込み
    net = Net().cpu().eval()
    net.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))

    #　データの前処理
    img = Image.open(img_path)
    img = transform(img)
    img = img.unsqueeze(0) # 1次元増やす

    #　推論
    y = torch.argmax(net(img), dim=1).cpu().detach().numpy()
    return getName(y[0])