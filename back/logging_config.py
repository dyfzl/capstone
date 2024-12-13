import logging
import os

# 로그 디렉토리 설정
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 로그 파일 경로
LOG_FILE = os.path.join(LOG_DIR, "application.log")

# 로거 설정 함수
def setup_logger(name=None):
    # 기존 로거가 있으면 그대로 반환
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger

    # 로거 레벨 설정
    logger.setLevel(logging.INFO)

    # 포맷터 설정
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 콘솔 핸들러 추가
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 파일 핸들러 추가
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    # 로거에 핸들러 추가
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
