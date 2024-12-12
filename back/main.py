from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from packages.routers.crawler import scrape_instagram_comments, scrape_youtube_comments
from fastapi.responses import FileResponse, JSONResponse
from starlette.middleware.cors import CORSMiddleware
from models.predict import analyze_comments
from models.retrain import retrain_kobert_model
from pydantic import BaseModel
import asyncio
import os
import pandas as pd
import logging
from threading import Lock

# 로그 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

# 글로벌 변수 락 설정
feedback_data = []
feedback_lock = Lock()
FEEDBACK_THRESHOLD = 50  # 학습 트리거를 위한 최소 데이터 수

# 요청 데이터 모델 정의
class CrawlAnalyzeRequest(BaseModel):
    account: str
    start_date: str
    end_date: str
    platform: str


@app.post("/crawl-and-analyze")
async def crawl_and_analyze(
    request: CrawlAnalyzeRequest,
    background_tasks: BackgroundTasks,
):
    try:
        logger.info("Received request: %s", request)

        # 플랫폼에 따라 크롤링 함수 호출
        if request.platform.lower() == "instagram":
            logger.info(f"Scraping Instagram comments for {request.account} from {request.start_date} to {request.end_date}")
            comments, _ = scrape_instagram_comments(
                account=request.account, 
                start_date=request.start_date, 
                end_date=request.end_date
            )
        elif request.platform.lower() == "youtube":
            logger.info(f"Scraping YouTube comments for {request.account} from {request.start_date} to {request.end_date}")
            comments, _ = scrape_youtube_comments(
                account=request.account, 
                start_date=request.start_date, 
                end_date=request.end_date
            )
        else:
            logger.error("Invalid platform: %s", request.platform)
            raise HTTPException(status_code=400, detail="Invalid platform. Choose either 'instagram' or 'youtube'.")

        # comments가 list인지 확인하고 DataFrame으로 변환
        if isinstance(comments, list):
            logger.info("Converting comments from list to DataFrame")
            comments = pd.DataFrame(comments, columns=["date", "comment", "link"])

        # comments가 DataFrame인지 확인
        if not isinstance(comments, pd.DataFrame):
            logger.error("Expected comments to be a pandas DataFrame, got %s", type(comments))
            raise ValueError("Expected comments to be a pandas DataFrame.")

        # 기존 크롤링 데이터 파일 경로
        dataset_path = "./dataset/comments.csv"

        # 파일 존재 여부 확인
        if not os.path.exists(dataset_path):
            logger.error(f"Dataset file does not exist: {dataset_path}")
            raise FileNotFoundError(f"Dataset file not found at: {dataset_path}")

        # 기존 저장된 CSV 파일 로드
        logger.info(f"Loading dataset from: {dataset_path}")
        comments = pd.read_csv(dataset_path, encoding='utf-8-sig')

        # 데이터 확인
        if comments.empty:
            logger.error("Loaded dataset is empty.")
            raise ValueError("Loaded dataset is empty.")
        logger.info("Dataset successfully loaded.")

        # 모델 분석 수행 및 결과 저장
        logger.info("Starting analyze_comments function")
        try:
            analysis_result = analyze_comments(dataset_path)
            logger.info(f"Analysis Result: {analysis_result}")
        except Exception as e:
            logger.error(f"Error in analyze_comments: {e}")
            raise


        # 크롤링된 댓글 수 계산
        total_comments_count = len(comments)
        logger.info("Total comments count: %d", total_comments_count)

        # 파일 경로 반환
        return {
            "message": "Crawling and analysis started successfully.",
            "total_comments_count": total_comments_count,
            "files": {
                "comments": "./front/public/data/comments.csv",
                "ratio": "./front/public/data/ratio.csv",
                "count": "./front/public/data/count.csv",
            },
        }

    except Exception as e:
        logger.exception("Error during crawl and analyze process")
        raise HTTPException(status_code=500, detail=f"Error during processing: {str(e)}")


@app.post("/retrain")
async def receive_feedback(request: Request):
    global feedback_data
    try:
        new_data = await request.json()
        logger.info("Received feedback: %s", new_data)
        with feedback_lock:
            feedback_data.append(new_data)

            if len(feedback_data) >= FEEDBACK_THRESHOLD:
                feedback_file = "feedback_data.csv"
                pd.DataFrame(feedback_data).to_csv(feedback_file, index=False, encoding="utf-8-sig")
                logger.info("Feedback data saved to: %s", feedback_file)
                feedback_data = []  # 임시 데이터 초기화

                retrain_kobert_model(feedback_file)
                logger.info("Retraining initiated")
                return {"status": "Retraining initiated"}
            else:
                return {"status": "Data stored", "current_size": len(feedback_data)}

    except Exception as e:
        logger.exception("Error during feedback processing")
        raise HTTPException(status_code=500, detail=f"Error during feedback processing: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server")
    uvicorn.run(app, host="0.0.0.0", port=8000)
