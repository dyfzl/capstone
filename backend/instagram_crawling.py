from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time
import os

# Selenium WebDriver 설정
def create_webdriver():
    chromedriver_path = os.path.join(os.getcwd(), "chromedriver")
    driver_service = Service(chromedriver_path)
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=driver_service, options=chrome_options)

# Instagram 크롤링 함수
def scrape_comments(account, start_date, end_date):
    try:
        # Selenium WebDriver 시작
        driver = create_webdriver()
        driver.get(f"https://www.instagram.com/{account}/")
        time.sleep(5)  # 페이지 로드 대기

        # 스크롤하며 게시물 수집
        post_links = []
        while True:
            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                href = link.get_attribute("href")
                if "/p/" in href and href not in post_links:
                    post_links.append(href)

            # 페이지 스크롤
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            time.sleep(2)

            if len(post_links) >= 50:  # 수집할 게시물 수 제한
                break

        # 기간 필터링
        filtered_links = []
        for link in post_links:
            driver.get(link)
            time.sleep(3)

            # 게시물 날짜 가져오기
            try:
                date_element = driver.find_element(By.XPATH, '//time')  # 날짜 요소
                post_date = datetime.fromisoformat(date_element.get_attribute("datetime").split("T")[0])

                # 기간 확인
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")

                if start_dt <= post_date <= end_dt:
                    filtered_links.append(link)
            except Exception as e:
                print(f"날짜 파싱 실패: {e}")
                continue

        # 댓글 크롤링
        comments_data = []
        for link in filtered_links:
            driver.get(link)
            time.sleep(3)

            # 댓글 로드
            for _ in range(5):  # 최대 5번 스크롤
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
                time.sleep(2)

            # 댓글 텍스트 수집
            comment_elements = driver.find_elements(By.CSS_SELECTOR, "ul li div div div span")
            for comment in comment_elements:
                comments_data.append({"post_url": link, "comment": comment.text})

        driver.quit()
        return comments_data

    except Exception as e:
        print(f"오류 발생: {e}")
        return None

# 메인 실행부
if __name__ == '__main__':
    # 사용자 입력 받기
    account = input("Instagram 계정 이름을 입력하세요: ")
    start_date = input("크롤링 시작 날짜 (YYYY-MM-DD): ")
    end_date = input("크롤링 종료 날짜 (YYYY-MM-DD): ")

    # 크롤링 실행
    print(f"{account} 계정의 {start_date} ~ {end_date} 기간 동안의 댓글을 크롤링합니다.")
    comments = scrape_comments(account, start_date, end_date)

    if comments:
        print("크롤링 결과:")
        for comment in comments:
            print(f"URL: {comment['post_url']}, 댓글: {comment['comment']}")
    else:
        print("크롤링 실패.")
