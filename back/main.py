from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from packages.routers.crawler import scrape_instagram_comments, scrape_youtube_comments
from fastapi.responses import FileResponse, JSONResponse
from starlette.middleware.cors import CORSMiddleware
from packages.routers import crawler
from models.predict import analyze_comments
from pydantic import BaseModel
from models.retrain import retrain_kobert_model
import os

app = FastAPI()

# CORS 설정
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/download-csv")
def download_csv():
    # CSV 파일 경로 설정
    file_path = "dataset/comments.csv"
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type='text/csv', filename="example.csv")
    return {"error": "File not found"}

# 요청 데이터 모델 정의
class CrawlAnalyzeRequest(BaseModel):
    account: str
    start_date: str
    end_date: str
    platform: str

# 이게 메인임~!~!
@app.post("/crawl-and-analyze")
async def crawl_and_analyze(
    request: CrawlAnalyzeRequest,  # Pydantic 모델로 요청 데이터 받기
    background_tasks: BackgroundTasks,
):
    """
    1. 크롤링 수행
    2. 크롤링된 데이터 다운로드
    3. 백그라운드에서 모델 분석 실행
    """

    try:
        # 플랫폼에 따라 크롤링 함수 호출
        if request.platform.lower() == "instagram":
            comments = scrape_instagram_comments(request.account, request.start_date, request.end_date)
        elif request.platform.lower() == "youtube":
            comments = scrape_youtube_comments(request.account, request.start_date, request.end_date)
        else:
            raise HTTPException(status_code=400, detail="Invalid platform. Choose either 'instagram' or 'youtube'.")
    
    except Exception as e:
        # 크롤링 중 오류 발생 시 처리
        return JSONResponse({"error": f"Error during crawling: {str(e)}"}, status_code=500)

    # 크롤링 데이터 저장 확인
    dataset_path = "dataset/comments.csv"
    if not os.path.exists(dataset_path):
        raise FileNotFoundError("Crawling failed. No data saved.")

    # 백그라운드에서 모델 분석 수행
    def run_analysis():
        try:
            analyze_comments()  # 모델 분석 수행
            print("Model analysis completed.")
        except Exception as e:
            print(f"Error during analysis: {e}")

    background_tasks.add_task(run_analysis)

    # 크롤링된 댓글 수 계산
    total_comments_count = len(comments)


    # 파일 경로 반환
    return {
        "message": "Crawling and analysis started successfully.",
        "total_comments_count": total_comments_count,  # 크롤링된 댓글 수 추가
        "files": {
            "comments": "front/public/data/comments.csv",
            "ratio": "front/public/data/ratio.csv",
            "count": "front/public/data/count.csv",
        },
    }


# 임시 데이터 저장
feedback_data = []
FEEDBACK_THRESHOLD = 50  # 학습 트리거를 위한 최소 데이터 수

@app.post("/retrain")
async def receive_feedback(request: Request):
    global feedback_data
    new_data = await request.json()
    feedback_data.append(new_data)
    print(f"Received feedback: {new_data}")

    if len(feedback_data) >= FEEDBACK_THRESHOLD:
        # 저장 및 재학습 실행
        feedback_file = "feedback_data.csv"
        pd.DataFrame(feedback_data).to_csv(feedback_file, index=False, encoding="utf-8-sig")
        feedback_data = []  # 임시 데이터 초기화
        retrain_kobert_model(feedback_file)
        return {"status": "Retraining initiated"}
    else:
        return {"status": "Data stored", "current_size": len(feedback_data)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
