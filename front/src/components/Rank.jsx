import React, { useEffect, useState } from "react";
import "./Rank.css";

const Rank = ({ selectedSentiment, dataPath }) => {
  const [stateKeywords, setStateKeywords] = useState([]); // State 이름 변경
  const [isLoading, setIsLoading] = useState(false); // 로딩 상태 추가

  useEffect(() => {
    // 데이터 경로가 없을 경우 처리
    if (!dataPath) {
      console.error("No data path provided.");
      return;
    }

    const fetchData = async () => {
      setIsLoading(true); // 로딩 시작
      try {
        const response = await fetch(dataPath);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const text = await response.text();
        const rows = text.split("\n").map((row) => row.split(","));

        // 데이터 파싱
        const parsedKeywords = rows.slice(1).map((row) => ({
          word: row[0],
          count: parseInt(row[1], 10) || 0,
        }));

        setStateKeywords(parsedKeywords); // State 업데이트
      } catch (error) {
        console.error("Error loading keyword data:", error);
        setStateKeywords([]); // 에러 발생 시 빈 배열로 초기화
      } finally {
        setIsLoading(false); // 로딩 종료
      }
    };

    fetchData();
  }, [dataPath]); // 의존성 배열에 dataPath 추가

  const getBackgroundColor = () => {
    if (selectedSentiment === "긍정") {
      return "rgb(186, 227, 255)";
    } else if (selectedSentiment === "중립") {
      return "rgb(164, 255, 144)";
    } else if (selectedSentiment === "부정") {
      return "rgb(255, 231, 243)";
    }
    return "transparent";
  };

  if (isLoading) {
    return (
      <div className="rank-container">
        <p className="loading-text">Loading...</p>
      </div>
    );
  }

  if (stateKeywords.length === 0) {
    return (
      <div className="rank-container">
        <p className="no-data-text">No keywords available</p>
      </div>
    );
  }

  return (
    <div className="rank-container">
      <ul className="rank-list">
        {stateKeywords.map((keyword, index) => (
          <li
            key={index}
            className="rank-word"
            style={{ backgroundColor: getBackgroundColor() }}
          >
            {index + 1}위: {keyword.word} ({keyword.count}회)
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Rank;
