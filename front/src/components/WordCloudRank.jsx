import React, { useState, useEffect } from "react";
import WordCloud from "./WordCloud";
import Rank from "./Rank";
import "./WordCloudRank.css";

const WordCloudRank = () => {
  const [selectedSentiment, setSelectedSentiment] = useState("긍정");
  const [wordCloudData, setWordCloudData] = useState("");
  const [keywords, setKeywords] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // comments.csv 파일을 public/data 디렉토리에서 불러옵니다
        const response = await fetch(
          `${import.meta.env.BASE_URL}data/comments.csv`
        );

        if (!response.ok) {
          throw new Error("Failed to fetch comments.csv");
        }

        // CSV 데이터 읽기 및 파싱
        const text = await response.text();
        const rows = text
          .trim()
          .split("\n")
          .slice(1) // 헤더 제외
          .map((row) => row.split(","));

        // 감정별 댓글 분류
        const positiveComments = [];
        const neutralComments = [];
        const negativeComments = [];

        rows.forEach((row) => {
          const content = row[1]?.replace(/"/g, "").trim(); // 댓글 내용
          const sentiment = row[3]?.trim(); // 감정 값 (0, 1, 2)

          if (sentiment === "0") positiveComments.push(content);
          else if (sentiment === "1") neutralComments.push(content);
          else if (sentiment === "2") negativeComments.push(content);
        });

        // 감정에 따라 텍스트 설정
        const data = {
          긍정: positiveComments.join(" "),
          중립: neutralComments.join(" "),
          부정: negativeComments.join(" "),
        };

        const sentimentText = data[selectedSentiment] || "";
        setWordCloudData(sentimentText);

        // 키워드와 빈도 계산
        const wordCounts = sentimentText.split(/\s+/).reduce((acc, word) => {
          acc[word] = (acc[word] || 0) + 1;
          return acc;
        }, {});

        // 상위 5개 키워드 추출
        const sortedKeywords = Object.entries(wordCounts)
          .sort(([, a], [, b]) => b - a)
          .slice(0, 5)
          .map(([word, count]) => ({ word, count }));

        setKeywords(sortedKeywords);
      } catch (error) {
        console.error("Error loading WordCloud data:", error);
        setWordCloudData("");
        setKeywords([]);
      }
    };

    fetchData();
  }, [selectedSentiment]);

  return (
    <div className="wordcloud-rank-wrapper">
      <div className="wordcloud-content">
        <div className="checkbox-container">
          <input
            type="radio"
            id="positive"
            name="sentiment"
            value="긍정"
            checked={selectedSentiment === "긍정"}
            onChange={() => setSelectedSentiment("긍정")}
          />
          <label htmlFor="positive" className="positive-circle"></label>
          <input
            type="radio"
            id="neutral"
            name="sentiment"
            value="중립"
            checked={selectedSentiment === "중립"}
            onChange={() => setSelectedSentiment("중립")}
          />
          <label htmlFor="neutral" className="neutral-circle"></label>
          <input
            type="radio"
            id="negative"
            name="sentiment"
            value="부정"
            checked={selectedSentiment === "부정"}
            onChange={() => setSelectedSentiment("부정")}
          />
          <label htmlFor="negative" className="negative-circle"></label>
        </div>
        <h2 className="wordcloud-title">워드클라우드</h2>
        <WordCloud
          title={selectedSentiment}
          data={wordCloudData}
          hasData={wordCloudData && wordCloudData.length > 0}
          size="large"
        />
      </div>
      <div className="rank-content">
        <h2 className="rank-title">키워드 순위</h2>
        <Rank selectedSentiment={selectedSentiment} keywords={keywords} />
      </div>
    </div>
  );
};

export default WordCloudRank;
