import logging
import os
import pandas as pd
import torch
import torch.nn as nn
from transformers import AdamW
from kobert_tokenizer import KoBERTTokenizer
from transformers import BertModel
from fastapi import FastAPI
from .check import preprocess_dataframe, preprocess_multiline_csv

# 로그 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 핸들러와 포맷터 추가
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

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
def analyze_comments(input_path: str, batch_size: int = 64, max_len: int = 128):
    try:
        # 1. 원본 데이터 로드
        original_df = pd.read_csv(
            input_path,
            quotechar='"',
            escapechar="\\",
            encoding="utf-8"
        )

        # 2. 댓글 전처리
        processed_df = preprocess_dataframe(original_df.copy(), text_column='comment')

        if processed_df.empty:
          raise ValueError("Processed DataFrame is empty after preprocessing.")
        

        # 3. NaN 값 제거 (전처리 단계에서 모든 NaN 삭제)
        processed_df.dropna(inplace=True)

        if processed_df.empty:
            raise ValueError("Processed DataFrame is empty after removing NaN values.")


        # 3. 날짜 변환 및 비정상 값 제거
        processed_df['Date'] = pd.to_datetime(processed_df['date'], errors='coerce')
        processed_df = processed_df.dropna(subset=['Date'])

        # 4. BERT 데이터셋 생성 및 감정 분석
        dataset = BERTDataset(processed_df, tokenizer, max_len)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=False)

        predictions = []
        with torch.no_grad():
            for batch in dataloader:
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                outputs = model(input_ids=input_ids, attention_mask=attention_mask)

                # 정수형 변환 및 추가
                batch_predictions = torch.argmax(outputs, dim=1).cpu().numpy()
                predictions.extend([int(pred) for pred in batch_predictions])

        # 5. 감정 결과 통합
        processed_df['Feelings'] = predictions
        original_df['Feelings'] = processed_df['Feelings'].astype(int)  # 하드코딩으로 명시적 정수 변환

        # 6. 데이터 저장 경로 설정
        save_dir = os.path.abspath("../front/public/data")
        os.makedirs(save_dir, exist_ok=True)

        # 7. 댓글 데이터 저장 (원본 데이터에 감정 추가)
        comments_file = os.path.join(save_dir, "comments.csv")
        original_df['Feelings'] = original_df['Feelings'].apply(int)
        original_df.to_csv(comments_file, index=False, encoding='utf-8-sig', float_format='%.0f')

        # 8. 감정 비율 계산 및 저장
        ratio_file = os.path.join(save_dir, "ratio.csv")
        emotion_counts = processed_df['Feelings'].value_counts()
        total_comments = len(processed_df)
        emotion_ratios = {
            0: round(emotion_counts.get(0, 0) / total_comments * 100, 2),
            1: round(emotion_counts.get(1, 0) / total_comments * 100, 2),
            2: round(emotion_counts.get(2, 0) / total_comments * 100, 2),
        }
        pd.DataFrame({
            "Ratio": [emotion_ratios[0], emotion_ratios[1], emotion_ratios[2]],
        }, index=["Positive", "Neutral", "Negative"]).to_csv(ratio_file, index=False, encoding='utf-8-sig')

        # 9. 연도-분기별 감정 데이터 집계
        min_date, max_date = processed_df['Date'].min(), processed_df['Date'].max()
        if pd.isna(min_date) or pd.isna(max_date):
            raise ValueError("Date range is invalid. Ensure the 'Date' column has valid entries.")
        
        date_ranges = pd.date_range(start=min_date, end=max_date, periods=5)
        labels = [date_ranges[i].strftime('%Y-%m-%d') for i in range(len(date_ranges) - 1)]

        processed_df['Period'] = pd.cut(
            processed_df['Date'], 
            bins=date_ranges, 
            labels=labels, 
            right=False 
        )

        period_counts = (
            processed_df.groupby(['Period', 'Feelings'])
            .size()
            .unstack(fill_value=0)
            .reset_index()
        )

        if period_counts.empty:
            raise ValueError("Period counts DataFrame is empty. Check the input data.")

        count_file = os.path.join(save_dir, "count.csv")
        period_counts.to_csv(count_file, index=False, encoding='utf-8-sig')

        # 10. 감정 결과 통합
        null_count = original_df['Feelings'].isnull().sum()  # Null 값 계산
        logger.info(f"Null values in Feelings column: {null_count}")

        # Null 값 삭제
        original_df = original_df.dropna(subset=['Feelings'])
        logger.info("Null values removed from Feelings column.")

        # 11. 결과 반환
        return {
            "message": "분석 완료",
            "comments_file": comments_file,
            "ratio_file": ratio_file,
            "count_file": count_file,
            "null_values_in_feelings": null_count,
            "results": processed_df[['comment', 'Feelings']].to_dict(orient="records"),
        }

    except Exception as e:
        return {
            "error": str(e),
            "comments_file": None,
            "ratio_file": None,
            "count_file": None,
            "null_values_in_feelings": None,
        }
