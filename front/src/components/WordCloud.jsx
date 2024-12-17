import React, { useEffect, useRef } from "react";
import "./WordCloud.css";
import { renderWordCloud } from "../utils/wordCloudGenerator";

const WordCloud = ({ data, hasData, size }) => {
  const wordCloudRef = useRef(null);

  useEffect(() => {
    if (hasData && data && wordCloudRef.current) {
      try {
        renderWordCloud(data, wordCloudRef.current);
      } catch (error) {
        console.error("Error rendering WordCloud:", error);
      }
    }
  }, [data, hasData]);

  if (!hasData || !data || data.length === 0) {
    return (
      <div
        className={`wordcloud-container no-data ${
          size === "large" ? "large" : ""
        }`}
      >
        <p className="no-data-text">워드클라우드 데이터를 불러오는 중입니다.</p>
      </div>
    );
  }

  return (
    <div className="wordcloud-wrapper">
      <div
        className={`wordcloud-container ${size === "large" ? "large" : ""}`}
        ref={wordCloudRef}
        style={{ width: "100%", height: "400px" }}
      ></div>
    </div>
  );
};

export default WordCloud;
