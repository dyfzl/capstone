import os
import pandas as pd
import torch
import torch.nn as nn
from transformers import AdamW
from kobert_tokenizer import KoBERTTokenizer
from transformers import BertModel
from fastapi import FastAPI
from .check import preprocess_dataframe

app = FastAPI()

# 모델 정의
class BERTClassifier(nn.Module):
    def __init__(self, bert, dr_rate=0.5):
        super(BERTClassifier, self).__init__()
        self.bert = bert
        self.dropout = nn.Dropout(p=dr_rate)
        self.classifier = nn.Linear(self.bert.config.hidden_size, 3)

    def forward(self, input_ids, attention_mask):
        output = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = output.pooler_output
        dropped_output = self.dropout(pooled_output)
        return self.classifier(dropped_output)

# GPU 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# KoBERT 모델 및 토크나이저 로드
tokenizer = KoBERTTokenizer.from_pretrained("skt/kobert-base-v1")

bert_model = BertModel.from_pretrained("skt/kobert-base-v1")

# 사전 학습된 모델 불러오기
MODEL_PATH = "models/best_kobert_model.pt"
model = BERTClassifier(bert_model).to(device)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.eval()

# 데이터셋 클래스 정의
class BERTDataset(torch.utils.data.Dataset):
    def __init__(self, df, tokenizer, max_len):
        self.texts = df['comment'].tolist()
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        inputs = self.tokenizer(
            text,
            padding="max_length",
            truncation=True,
            max_length=self.max_len,
            return_tensors="pt",
        )
        return {
            "input_ids": inputs["input_ids"].squeeze(0),
            "attention_mask": inputs["attention_mask"].squeeze(0),
        }



@app.post("/analyze-comments/")
def analyze_comments(batch_size: int = 64, max_len: int = 128):
    # 데이터셋 경로
    dataset_path = "dataset/comments.csv"

    # 데이터 로드
    df = pd.read_csv(dataset_path)

    # 데이터 전처리
    df = preprocess_dataframe(df, text_column='comment')

    # 데이터셋 생성
    dataset = BERTDataset(df, tokenizer, max_len)
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=False)

    # 예측
    predictions = []
    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            batch_predictions = torch.argmax(outputs, dim=1).cpu().numpy()
            predictions.extend(batch_predictions)

    # 감정 레이블 재분류
    emotion_map = {0: "Positive", 1: "Neutral", 2: "Negative"}
    df['Feelings'] = [emotion_map[pred] for pred in predictions]

    # 결과 저장 디렉토리
    SAVE_DIR = "../front/public/data"
    os.makedirs(SAVE_DIR, exist_ok=True)

    # 파일 저장
    comments_file = os.path.join(SAVE_DIR, "comments.csv")
    df.to_csv(comments_file, index=False, encoding='utf-8-sig')

    ratio_file = os.path.join(SAVE_DIR, "ratio.csv")
    emotion_counts = df['Feelings'].value_counts()
    pd.DataFrame({
        "Count": [emotion_counts.get("Positive", 0), emotion_counts.get("Neutral", 0), emotion_counts.get("Negative", 0)],
    }).to_csv(ratio_file, index=False, encoding='utf-8-sig')
    # 분기별 감정 계산
    df['Date'] = pd.to_datetime(df['date'])  # 날짜 변환
    min_date, max_date = df['Date'].min(), df['Date'].max()
    date_ranges = pd.date_range(min_date, max_date, periods=5)  # 5개의 경계값 생성
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']  # 4개의 레이블로 수정

    # pd.cut에서 bins와 labels의 길이를 맞춤
    df['Quarter'] = pd.cut(df['Date'], bins=date_ranges, labels=quarters, right=False)

    quarter_counts = df.groupby(['Quarter', 'Feelings']).size().unstack(fill_value=0)
    quarter_counts = quarter_counts.reindex(columns=['Positive', 'Neutral', 'Negative'], fill_value=0)
    quarter_counts.insert(0, 'Date', [d.strftime('%Y-%m-%d') for d in date_ranges[:-1]])  # 분기 시작 날짜 추가

    count_file = os.path.join(SAVE_DIR, "count.csv")
    quarter_counts.reset_index(drop=True, inplace=True)
    quarter_counts.to_csv(count_file, index=False, encoding='utf-8-sig')
    
    return {
        "message": "분석 완료",
        "comments_file": comments_file,
        "ratio_file": ratio_file,
        "count_file": count_file,
        "results": df[['comment', 'Feelings']].to_dict(orient="records"),
    }