from fastapi import FastAPI, Request, APIRouter
import pandas as pd
import json

app = FastAPI()
router = APIRouter(prefix="/api")

# 임시 데이터 저장소
feedback_data = []

@app.post("/retrain")
async def retrain_model(request: Request):
    new_data = await request.json()
    feedback_data.append(new_data)
    print("Received data:", new_data)
    return {"status": "Success", "message": "Data received for retraining"}


# 새 데이터를 Pandas 데이터프레임으로 변환 및 저장
def save_feedback_data(feedback_data, file_path="feedback_data.csv"):
    df = pd.DataFrame(feedback_data)
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"Feedback data saved at {file_path}")
