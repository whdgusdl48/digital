from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
from MobileNet import mobilenetv3_small
from fastapi import FastAPI, File, UploadFile
from PIL import Image
from io import BytesIO
import os
import torch.nn as nn
import torch
from torchvision import datasets, models, transforms
import math

class ResNet50Model(nn.Module):
    def __init__(self, num_classes=1000):
        super(ResNet50Model, self).__init__()
        self.resnet50 = models.resnet50(pretrained=True)
        self.resnet50.fc = nn.Linear(self.resnet50.fc.in_features, num_classes)

    def forward(self, x):
        return self.resnet50(x)

model = ResNet50Model(num_classes=7).to('cpu')

# 가중치 로드
PATH = './Resnet50.pt'
model.load_state_dict(torch.load(PATH, map_location=torch.device('cpu')))  # CPU에서 로드
model.eval()
app = FastAPI()


# 허용할 도메인 설정
origins = [
    "http://127.0.0.1:5173",  # Svelte 개발 서버 주소
    "http://localhost:5173",  # localhost 버전도 추가
]

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 허용할 도메인 목록
    allow_credentials=True,
    allow_methods=["*"],    # 모든 HTTP 메서드 허용
    allow_headers=["*"],    # 모든 헤더 허용
)

class ImageData(BaseModel):
    image: str  # Base64 형식의 이미지 데이터

@app.get("/hello")
def hello():
    return {"message": "안녕하세요 파이보"}

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_image(data: ImageData):
    try:
        # Base64 데이터 처리
        header, encoded = data.image.split(",", 1)  # "data:image/png;base64,..." 형식 처리
        image_data = base64.b64decode(encoded)

        image = Image.open(BytesIO(image_data)).convert('RGB')

        #2. 변환 정의
        transform = transforms.Compose([
            transforms.Resize((384, 384)),  # 이미지 크기 조정
            transforms.ToTensor(),  # 텐서로 변환
            transforms.Normalize(  # 정규화 (평균과 표준편차)
                mean=[0.485, 0.456, 0.406],  # ImageNet 기준 평균값
                std=[0.229, 0.224, 0.225]  # ImageNet 기준 표준편차
            )
        ])
        predict_area = ['Angry', 'Happy', 'Neutral', 'Sad', 'Surprise']
        tensor_image = transform(image).to('cpu')
        predict = model(tensor_image.unsqueeze(0))
        _, preds = torch.max(predict, 1)
        prediction_result = predict_area[preds]
        return {"message": "Image uploaded successfully", "path" :prediction_result}
    except Exception as e:
        return {"error": str(e)}