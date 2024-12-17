import React, { useState, useEffect } from "react";
import { ResponsiveLine } from "@nivo/line";
import "./LineGraph.css";

const LineGraph = () => {
  const [data, setData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);

        // count.csv 파일을 public/data 디렉토리에서 불러옵니다.
        const response = await fetch(
          `${import.meta.env.BASE_URL}data/count.csv`
        );

        if (!response.ok) throw new Error("Failed to fetch count.csv");

        const text = await response.text();

        // CSV 파일을 읽어서 파싱
        const rows = text
          .trim()
          .split("\n")
          .slice(1) // 헤더 제외
          .map((row) => row.split(","));

        // 데이터를 Nivo Line 차트 형식으로 변환
        const formattedData = [
          {
            id: "긍정",
            color: "#316dec",
            data: rows.map((r) => ({ x: r[0], y: parseInt(r[1], 10) || 0 })),
          },
          {
            id: "중립",
            color: "#0f9b0f",
            data: rows.map((r) => ({ x: r[0], y: parseInt(r[2], 10) || 0 })),
          },
          {
            id: "부정",
            color: "#e93434",
            data: rows.map((r) => ({ x: r[0], y: parseInt(r[3], 10) || 0 })),
          },
        ];

        setData(formattedData);
      } catch (error) {
        console.error("Error loading LineGraph data:", error);
        setData([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData(); // 컴포넌트 마운트 시 데이터 로드
  }, []);

  if (isLoading) {
    return <p>데이터를 불러오는 중입니다...</p>;
  }

  return (
    <div className="linegraph-container">
      <h3 className="linegraph-title">감정 변화 추이</h3>
      <ResponsiveLine
        data={data}
        margin={{ top: 50, right: 110, bottom: 50, left: 60 }}
        xScale={{ type: "point" }}
        yScale={{
          type: "linear",
          min: "auto",
          max: "auto",
          stacked: false,
          reverse: false,
        }}
        axisTop={null}
        axisRight={null}
        axisBottom={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          legend: "기간",
          legendOffset: 36,
          legendPosition: "middle",
        }}
        axisLeft={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          legend: "감정 개수",
          legendOffset: -40,
          legendPosition: "middle",
        }}
        colors={{ datum: "color" }}
        pointSize={10}
        pointColor={{ theme: "background" }}
        pointBorderWidth={2}
        pointBorderColor={{ from: "serieColor" }}
        pointLabelYOffset={-12}
        useMesh={true}
        legends={[
          {
            anchor: "bottom-right",
            direction: "column",
            justify: false,
            translateX: 120,
            translateY: -10,
            itemsSpacing: 0,
            itemDirection: "left-to-right",
            itemWidth: 80,
            itemHeight: 25,
            itemOpacity: 0.75,
            symbolSize: 12,
            symbolShape: "circle",
            symbolBorderColor: "rgba(0, 0, 0, .5)",
            effects: [
              {
                on: "hover",
                style: {
                  itemBackground: "rgba(0, 0, 0, .03)",
                  itemOpacity: 1,
                },
              },
            ],
          },
        ]}
      />
    </div>
  );
};

export default LineGraph;
