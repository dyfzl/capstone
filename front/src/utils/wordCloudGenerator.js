import * as d3 from "d3";
import WordCloud from "wordcloud";

export const generateWordCloudData = async () => {
  try {
    const response = await fetch(
      `${import.meta.env.BASE_URL}data/comments.csv`
    );
    if (!response.ok) {
      throw new Error("Failed to load CSV file");
    }

    const text = await response.text();

    // CSV 파싱 및 유효성 검사
    const rows = text
      .trim()
      .split("\n")
      .map((row) => row.split(","))
      .filter((row) => row.length >= 4 && row[1] && row[3]); // 유효한 행만 포함

    console.log("Valid Parsed CSV Rows:", rows);

    const positiveComments = [];
    const neutralComments = [];
    const negativeComments = [];

    // 댓글 내용과 감정 값 추출
    rows.slice(1).forEach((row) => {
      const content = row[1].replace(/"/g, "").trim(); // 댓글 내용에서 따옴표 제거
      const sentiment = row[3].trim(); // 감정 값 (0, 1, 2)

      if (sentiment === "0") positiveComments.push(content);
      else if (sentiment === "1") neutralComments.push(content);
      else if (sentiment === "2") negativeComments.push(content);
    });

    return {
      긍정: positiveComments.join(" "),
      중립: neutralComments.join(" "),
      부정: negativeComments.join(" "),
    };
  } catch (error) {
    console.error("Error loading CSV data:", error);
    return { 긍정: "", 중립: "", 부정: "" };
  }
};

// 워드클라우드를 생성하여 지정된 HTML 엘리먼트에 렌더링
export const renderWordCloud = (text, element) => {
  if (!text || text.trim() === "") {
    console.warn("No words to render in Word Cloud.");
    return;
  }

  const wordCounts = d3.rollup(
    text.split(/\s+/),
    (v) => v.length,
    (word) => word
  );

  const entries = Array.from(wordCounts)
    .filter(([word]) => word.length > 1) // 단어 길이가 1 이하인 경우 제외
    .map(([word, count]) => ({
      text: word,
      size: Math.min(count * 10, 100), // 단어 크기 상한 설정
    }));

  const options = {
    list: entries.map(({ text, size }) => [text, size]),
    gridSize: 8, // 단어 간격 설정
    weightFactor: (size) => size * 2, // 단어 크기 비율 설정
    fontFamily: "Nanum Gothic",
    color: () => d3.schemeCategory10[Math.floor(Math.random() * 10)], // 색상 랜덤 지정
    rotateRatio: 0, // 단어 회전 비율
    backgroundColor: "#ffffff", // 배경색
    drawOutOfBound: false, // 경계 내로 제한
  };

  if (element) {
    WordCloud(element, options);
  }
};
