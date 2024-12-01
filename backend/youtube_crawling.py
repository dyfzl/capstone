from googleapiclient.discovery import build
import csv
import os
from googleapiclient.errors import HttpError

# API 키 설정
API_KEY = 'AIzaSyAPTAHUqK4qIYut2-4H_BrdYlcLrIQ0lhI'

# YouTube API 클라이언트 생성
youtube = build('youtube', 'v3', developerKey=API_KEY)

# 검색어로 채널 ID 가져오기
def get_channel_id(query):
    response = youtube.search().list(
        part='snippet',
        q=query,
        type='channel',
        maxResults=1
    ).execute()

    if response['items']:
        channel_id = response['items'][0]['id']['channelId']
        print(f"검색어 '{query}'에 대한 채널 ID: {channel_id}")
        return channel_id
    else:
        print(f"'{query}'에 대한 채널을 찾을 수 없습니다.")
        return None

# 비디오 ID와 제목 가져오기
def get_video_ids_and_titles(channel_id):
    video_data = []
    response = youtube.search().list(
        part='id,snippet',
        channelId=channel_id,
        maxResults=50,
        order='date',
        type='video'
    ).execute()

    while response and len(video_data) < 50:  # 50개로 제한
        for item in response['items']:
            video_id = item['id']['videoId']
            video_title = item['snippet']['title']
            video_data.append((video_url, video_title))
            if len(video_data) >= 50:
                break

        # 다음 페이지 요청
        if 'nextPageToken' in response and len(video_data) < 50:
            response = youtube.search().list(
                part='id,snippet',
                channelId=channel_id,
                maxResults=50,
                order='date',
                type='video',
                pageToken=response['nextPageToken']
            ).execute()
        else:
            break

    return video_data

# 댓글 가져오기
def get_comments(video_id):
    comments = []
    try:
        response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            textFormat='plainText',
            maxResults=100
        ).execute()

        while response:
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                published_at = item['snippet']['topLevelComment']['snippet']['publishedAt']
                comments.append((comment, published_at))

            if 'nextPageToken' in response:
                response = youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    textFormat='plainText',
                    pageToken=response['nextPageToken'],
                    maxResults=100
                ).execute()
            else:
                break

    except HttpError as e:
        if e.resp.status == 403:
            print(f"댓글이 비활성화된 비디오 ID: {video_id}로 인한 오류 발생")
        else:
            print(f"오류 발생: {e}")

    return comments

# 사용자 입력을 통한 검색어 처리
query = input("유튜브 채널이름을 입력하세요: ")
channel_id = get_channel_id(query)

if channel_id:
    # 채널의 비디오 ID와 제목 목록 가져오기
    video_data = get_video_ids_and_titles(channel_id)

    # 결과를 저장할 CSV 파일 열기
    output_file = 'youtube_comments.csv'  # 파일 이름 지정

    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Video URL', 'Video Title', 'Comment', 'Published At'])  # 헤더 작성

            # 비디오 ID와 제목 리스트를 한 줄에 표시
            print(f"이 비디오들의 댓글들을 가져옵니다: {[video[0] for video in video_data]}")

            for video_id, video_title in video_data:
                comments = get_comments(video_id)

                # 각 비디오의 댓글과 작성시간을 CSV에 작성
                for comment, published_at in comments:
                    writer.writerow([video_id, video_title, comment, published_at])  # 비디오 ID, 제목, 댓글, 작성시간 작성

        print("댓글 크롤링 완료! 'youtube_comments.csv' 파일을 확인하세요.")
        print(f"파일 위치: {os.path.abspath(output_file)}")  # 파일 경로 출력
    except Exception as e:
        print(f"오류 발생: {e}")
