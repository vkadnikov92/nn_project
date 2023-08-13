import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import requests
from io import BytesIO

# 1. Загрузка и модификация модели

device='cpu'

def load_resnet():
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    resnet = models.resnet18(pretrained=False)
    num_features = resnet.fc.in_features
    resnet.fc = nn.Linear(num_features, 2)  # Замена последнего слоя для классификации котов и собак
    resnet.to(device)

    # 2. Загрузка сохраненных весов
    resnet.load_state_dict(torch.load('models/cat_dog_resnet18_weights.pt', map_location=device)) #model-test-cat_dog
    resnet.eval()
    return resnet








# 3. Препроцессинг изображений
data_transforms = {
    'val': transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
}

# 4. Функциональность для классификации изображения из URL
def predict_from_url(url, model):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content)).convert('RGB')
    preprocess = data_transforms['val']
    image = preprocess(image).unsqueeze(0).to(device)
    with torch.no_grad():
        output = model(image)
        _, predicted = torch.max(output, 1)
        return 'Cat' if predicted.item() == 0 else 'Dog'


# Тестирование
url = "https://s0.rbk.ru/v6_top_pics/media/img/4/97/756723916815974.webp"
resnet = load_resnet()
prediction = predict_from_url(url, resnet)
print(f"This image likely contains a: {prediction}")