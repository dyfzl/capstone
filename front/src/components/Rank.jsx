import React, { useMemo } from "react";
import "./Rank.css";

const Rank = ({ selectedSentiment, keywords }) => {
  const getBackgroundColor = () => {
    if (selectedSentiment === "긍정") {
      return "rgb(198, 232, 255)";
    } else if (selectedSentiment === "중립") {
      return "rgb(182, 255, 166)";
    } else if (selectedSentiment === "부정") {
      return "rgb(255, 223, 240)";
    }
    return "transparent";
  };

  return (
    <div className="rank-container">
      <ul className="rank-list">
        {keywords.map((keyword, index) => (
          <li
            key={index}
            className="rank-word"
            style={{ backgroundColor: getBackgroundColor() }}
          >
            <span className="rank-index">{index + 1}위:</span>{" "}
            <span className="rank-keyword">{keyword.word}</span>
            <span className="rank-count">{keyword.count}회</span>
          </li>
        ))}
      </ul>
    </div>
  );
};
export default Rank;
