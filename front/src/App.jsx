import React, { useState, useEffect, useRef } from "react";
import Header from "./components/Header";
import SideMenu from "./components/SideMenu";
import DefaultImage from "./components/images/default-img.png";
import WordCloudRank from "./components/WordCloudRank";
import WordCloud from "./components/WordCloud";
import PieChart from "./components/PieChart";
import LineGraph from "./components/LineGraph";
import Comments from "./components/Comments";
import Rank from "./components/Rank.jsx";
import "./App.css";

function App() {
  const [filePaths, setFilePaths] = useState({
    comments: "../data/comments.csv",
    ratio: "../data/ratio.csv",
    count: "../data/count.csv",
  }); // 파일 경로 상태 추가
  const [selectedEmotion, setSelectedEmotion] = useState("긍정");
  const [activeButton, setActiveButton] = useState(0);
  const [hasData, setHasData] = useState(false); // `hasData` 상태 추가

  // 참조 생성
  const wordCloudRef = useRef(null);
  const chartRef = useRef(null);
  const commentsRef = useRef(null);

  const handleSearchComplete = (files) => {
    setFilePaths(files); // Header에서 파일 경로를 받아 저장
  };

  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY;
      const wordCloudPosition = wordCloudRef.current?.offsetTop || 0;
      const chartPosition = chartRef.current?.offsetTop || 0;
      const commentsPosition = commentsRef.current?.offsetTop || 0;
      const chartHeight = chartRef.current?.offsetHeight || 0;

      if (
        scrollPosition >= wordCloudPosition &&
        scrollPosition < chartPosition - chartHeight / 1.2
      ) {
        setActiveButton(0);
      } else if (
        scrollPosition >= chartPosition - chartHeight / 2 &&
        scrollPosition < commentsPosition - chartHeight / 2
      ) {
        setActiveButton(1);
      } else if (scrollPosition >= commentsPosition - chartHeight / 2) {
        setActiveButton(2);
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div>
      <Header onSearchComplete={handleSearchComplete} />
      {filePaths && (
        <div>
          <div ref={wordCloudRef}>
            <WordCloudRank dataPath={filePaths.comments} />
            <WordCloud dataPath={filePaths.comments} />
          </div>
          <div ref={chartRef}>
            <Rank dataPath={filePaths.comments} />
            <PieChart dataPath={filePaths.ratio} />
            <LineGraph dataPath={filePaths.count} />
          </div>
          <div ref={commentsRef}>
            <Comments dataPath={filePaths.comments} />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
