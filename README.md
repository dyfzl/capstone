# 마인드서치
**캡스톤디자인 AI기반 소셜 미디어 뉴스 검색 및 감성 분석**

>*유튜브, 인스타그램의 댓글에 대한 감성 분석을 진행한 뒤 시각화 자료로 직관적인 정보 제공*
<br/>

본 프로젝트는 SNS에서 키워드 관련 컨텐츠를 검색하고 컨텐츠 댓글의 긍정, 부정, 중립의 감성으로 감성 분류를 진행한다. 워드클라우드와 각종 도표를 통해 분석 결과를 직관적으로 시각화하여 사용자에게 직관적인 정보 제공을 목표로 한다.

<br/>

## 🛠실행
다음 내용을 순차적으로 수행한다.

<br/>

**Node.js 설치(18버전 이상)** <https://nodejs.org/>

**VS Code 설치** <https://code.visualstudio.com/>

**Python(3.3버전 이상) 설치** <https://www.python.org/downloads/>

<br/>

git clone 후 vscode에서 폴더 오픈

>Key 파일 다운로드
* **.env**
  
  루트 디렉토리에 삽입

<br/>

vscode 터미널 2개 생성
> *터미널1*

```
    cd back

    pip install 'git+https://github.com/SKTBrain/KoBERT.git#egg=kobert_tokenizer&subdirectory=kobert_hf'
   
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload

    #kobert
    pip install 'git+https://github.com/SKTBrain/KoBERT.git#egg=kobert_tokenizer&subdirectory=kobert_hf'

```

<br/>

> *터미널2*

```
    cd front

    npm install

    npm run dev
    
```

<br/>



<br/>

## 💻프로젝트 소개
* 메인 화면
   * 기간, 플랫폼, 키워드 입력
   * 워드클라우드, 감정 비율, 감정 추이, 댓글 분석 확인 가능
   * 감정에 오류가 있을 경우 사용자의 피드백으로 모델의 재학습을 통해 모델 성능 향상 가능


<br/>


## ⚙개발환경
* Visual Studio Code
* React Native
* Node.js
* 언어 : Javascript, Python
* 프레임워크 : FastAPI
* 모델 : Kobert

<br/><br/>

