import torch
import pandas as pd
import torch.nn as nn
from transformers import AdamW
from torch.utils.data import DataLoader

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


def retrain_kobert_model(feedback_data_path):
    # Load feedback data
    feedback_data = pd.read_csv(feedback_data_path)
    
    # Dataset & DataLoader
    tokenizer = ...  # KoBERT 토크나이저 로드
    train_dataset = BERTDataset(feedback_data, tokenizer, max_len=128)
    train_dataloader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    
    # Load existing model
    model = BERTClassifier(...).to("cuda")  # KoBERT 모델 로드
    model.load_state_dict(torch.load("existing_kobert_model.pt"))

    # Fine-tuning 설정
    optimizer = AdamW(model.classifier.parameters(), lr=5e-6, weight_decay=0.01)
    model.train()
    
    for epoch in range(3):  # 소량 데이터에 적합한 Epoch 수
        for batch in train_dataloader:
            optimizer.zero_grad()
            input_ids = batch["input_ids"].to("cuda")
            attention_mask = batch["attention_mask"].to("cuda")
            labels = batch["labels"].to("cuda")

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            loss = torch.nn.CrossEntropyLoss()(outputs, labels)
            loss.backward()
            optimizer.step()

    # Fine-tuned 모델 저장
    torch.save(model.state_dict(), "fine_tuned_kobert_model.pt")
    print("Fine-tuned model saved successfully!")
