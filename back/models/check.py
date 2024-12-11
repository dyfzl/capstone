import pandas as pd
import re
import unicodedata

def merge_feedback_with_train_data(train_data_path, feedback_data_path):
    train_data = pd.read_csv(train_data_path)
    feedback_data = pd.read_csv(feedback_data_path)
    merged_data = pd.concat([train_data, feedback_data], ignore_index=True)
    return merged_data

# 이모티콘 매핑
EMOTICON_MAP = {
    "❤️": "사랑해요", "🧡": "사랑해요", "💛": "사랑해요", "💚": "사랑해요",
    "💙": "사랑해요", "💞": "사랑해요", "💓": "사랑해요", "💜": "사랑해요",
    "❣️": "사랑해요", "💕": "사랑해요", "💘": "사랑해요", "💗": "사랑해요",
    "💝": "사랑해요", "💟": "사랑해요", "😻": "사랑해요", "💔": "싫어해요",
    "👍": "최고에요", "👎": "최악이에요", "🙌": "만세", "😘": "사랑해요",
    "😍": "사랑해요", "😃": "좋아요", "😄": "좋아요", "😁": "좋아요",
    "😆": "좋아요", "☺️": "좋아요", "😊": "좋아요", "😚": "좋아요",
    "🤗": "좋아요", "😭": "슬퍼요", "😢": "슬퍼요", "😤": "삐졌어요",
    "😠": "화났어요", "😡": "화났어요", "🤬": "화났어요", "😳": "잘 모르겠어요",
    "🤔": "고민해 볼게요", "^^": "좋아요", "♡": "사랑해요", "♥": "사랑해요"
}

# 이모티콘 처리 함수
def replace_emoticons(text):
    """
    Replace emoticons and special symbols in text with mapped expressions.
    Handles non-string types by converting them to strings.
    """
    if not isinstance(text, str):  # 문자열이 아닌 경우 처리
        return str(text)  # 문자열로 변환
    for emoticon, replacement in EMOTICON_MAP.items():
        text = text.replace(emoticon, replacement)
    return text

# 특수문자 제거 함수
def remove_special_characters(text):
    """
    Remove special characters except ^^, !, ?, ., ,.
    """
    return re.sub(r'(?!\^\^)[^\w\s!?.,]', '', text)

# 자모 분리 해결 및 중복 문자 정리 함수
def preprocess_text(text):
    """
    Normalize text to resolve Jamo separation and reduce repeated characters.
    """
    # 자모 분리 해결
    text = unicodedata.normalize('NFC', text)
    # 중복 문자 정리 (3회 이상 반복되는 문자 2회로 축소)
    text = re.sub(r"(.)\1{2,}", r"\1\1", text)
    return text

# 데이터프레임 전처리 함수
def preprocess_dataframe(df, text_column='comment'):
    """
    Preprocess a DataFrame by handling NaN, stripping whitespace, replacing emoticons,
    removing special characters, and normalizing text.
    Filters rows based on text length (5 to 300 characters).
    """
    # 1. 공백 및 NaN 값 처리
    df[text_column] = df[text_column].fillna('')  # NaN 값은 빈 문자열로 대체
    df[text_column] = df[text_column].str.strip()  # 문자열 양끝 공백 제거

    # 2. 이모티콘 처리
    df[text_column] = df[text_column].apply(replace_emoticons)

    # 3. 특수문자 제거
    df[text_column] = df[text_column].apply(remove_special_characters)

    # 4. 자모 분리 해결 및 중복 문자 정리
    df[text_column] = df[text_column].apply(preprocess_text)

    # 5. 텍스트 길이에 따라 필터링 (5 ~ 300자 사이)
    df = df[df[text_column].apply(len).between(5, 300)]

    return df