import React, { useState, useEffect } from "react";
import { ResponsivePie } from "@nivo/pie";
import "./PieChart.css";

const PieChart = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // ratio.csv 파일을 public/data 디렉토리에서 불러옵니다
        const response = await fetch(
          `${import.meta.env.BASE_URL}data/ratio.csv`
        );

        if (!response.ok) {
          throw new Error("Failed to fetch ratio.csv");
        }

        // CSV 파일 내용 파싱
        const text = await response.text();
        const rows = text.trim().split("\n").slice(1); // 첫 번째 행(헤더) 제외

        // 비율 데이터를 파싱하여 Nivo Pie 형식에 맞게 변환
        const parsedData = [
          {
            id: "긍정",
            label: "긍정",
            value: parseFloat(rows[0]) || 0, // 두 번째 행 (긍정 비율)
            color: "#316dec",
          },
          {
            id: "중립",
            label: "중립",
            value: parseFloat(rows[1]) || 0, // 세 번째 행 (중립 비율)
            color: "#0f9b0f",
          },
          {
            id: "부정",
            label: "부정",
            value: parseFloat(rows[2]) || 0, // 네 번째 행 (부정 비율)
            color: "#e93434",
          },
        ];

        // 상태에 데이터 저장
        setData(parsedData);
      } catch (error) {
        console.error("Error loading ratio.csv:", error);
        setData([]); // 에러 시 빈 배열 설정
      }
    };

    fetchData(); // 컴포넌트 마운트 시 데이터 로드
  }, []);

  return (
    <div className="circlechart-container">
      <h2 className="piechart-title">감정 비율</h2>
      {data.length > 0 ? (
        <ResponsivePie
          data={data}
          margin={{ top: 40, right: 80, bottom: 80, left: 80 }}
          innerRadius={0.5}
          padAngle={0.7}
          cornerRadius={3}
          activeOuterRadiusOffset={8}
          colors={{ datum: "data.color" }}
          borderWidth={1}
          borderColor={{ from: "color", modifiers: [["darker", 0.2]] }}
          arcLinkLabelsSkipAngle={10}
          arcLinkLabelsTextColor="#333333"
          arcLinkLabelsThickness={2}
          arcLabelsSkipAngle={10}
          arcLabelsTextColor={{ from: "color", modifiers: [["darker", 2]] }}
          legends={[
            {
              anchor: "bottom",
              direction: "row",
              translateX: 0,
              translateY: 40,
              itemWidth: 100,
              itemHeight: 18,
              itemTextColor: "#999",
              symbolSize: 18,
              symbolShape: "circle",
            },
          ]}
        />
      ) : (
        <p>데이터를 불러오는 중입니다...</p>
      )}
    </div>
  );
};

export default PieChart;
