import React, { useEffect, useState, useRef } from "react";
import "./WordCloud.css";
import { renderWordCloud } from "../utils/wordCloudGenerator";

const WordCloud = ({ dataPath, hasData, size }) => {
  const [data, setData] = useState([]);
  const [isLoading, setIsLoading] = useState(false); // 로딩 상태 추가
  const wordCloudRef = useRef(null);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true); // 로딩 시작
      try {
        const response = await fetch(`http://127.0.0.1:8000/data/${dataPath}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const text = await response.text();
        const rows = text.split("\n").map((row) => row.split(","));

        // 데이터 파싱
        const parsedData = rows.slice(1).map((row) => ({
          word: row[0],
          count: parseInt(row[1], 10) || 0,
        }));

        setData(parsedData);
      } catch (error) {
        console.error("Error loading word cloud data:", error);
        setData([]);
      } finally {
        setIsLoading(false); // 로딩 종료
      }
    };

    fetchData();
  }, [dataPath]); // 의존성 배열에 dataPath 추가

  useEffect(() => {
    if (hasData && data && wordCloudRef.current) {
      renderWordCloud(data, wordCloudRef.current);
    }
  }, [data, hasData]);

  if (isLoading) {
    return (
      <div
        className={`wordcloud-container loading ${
          size === "large" ? "large" : ""
        }`}
      >
        <p className="loading-text">Loading WordCloud...</p>
      </div>
    );
  }

  if (!hasData || !data || data.length === 0) {
    return (
      <div
        className={`wordcloud-container no-data ${
          size === "large" ? "large" : ""
        }`}
      >
        <p className="no-data-text">No WordCloud Data Available</p>
      </div>
    );
  }

  return (
    <div className="wordcloud-wrapper">
      <div
        className={`wordcloud-container ${size === "large" ? "large" : ""}`}
        ref={wordCloudRef} // DOM 참조 전달
        style={{ width: "100%", height: "400px" }} // 크기 설정
      ></div>
    </div>
  );
};

export default WordCloud;
