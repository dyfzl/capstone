import React, { useState, useEffect } from "react";
import Papa from "papaparse"; // Papaparse 추가
import "./Comments.css";

const Comments = () => {
  const [comments, setComments] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedSentiments, setSelectedSentiments] = useState({
    긍정: true,
    중립: true,
    부정: true,
  });

  const commentsPerPage = 7;

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(
          `${import.meta.env.BASE_URL}data/comments.csv`
        );
        const text = await response.text();

        // PapaParse를 사용해 CSV 파일 파싱
        Papa.parse(text, {
          header: true, // 첫 번째 행을 헤더로 처리
          skipEmptyLines: true,
          dynamicTyping: true, // 숫자 변환
          complete: (result) => {
            const parsedComments = result.data.map((row) => ({
              date: row.date,
              content: row.comment,
              link: row.link,
              sentiment:
                row.Feelings === 0
                  ? "긍정"
                  : row.Feelings === 1
                  ? "중립"
                  : "부정",
            }));
            setComments(parsedComments);
          },
        });
      } catch (error) {
        console.error("Error loading CSV data:", error);
      }
    };

    fetchData();
  }, []);

  const filteredComments = comments.filter(
    (comment) => selectedSentiments[comment.sentiment]
  );

  const totalPages = Math.ceil(filteredComments.length / commentsPerPage);
  const startIndex = (currentPage - 1) * commentsPerPage;
  const displayedComments = filteredComments.slice(
    startIndex,
    startIndex + commentsPerPage
  );

  return (
    <div className="comments-container">
      <div className="comment-header">
        <div className="col">날짜</div>
        <div className="col">댓글</div>
        <div className="col">감정</div>
      </div>
      <div className="comment-content">
        {displayedComments.map((comment, index) => (
          <div key={index} className="comment-row">
            <div className="col">{comment.date}</div>
            <div className="col">
              <a
                href={comment.link}
                target="_blank"
                rel="noopener noreferrer"
                className="comment-link"
              >
                {comment.content}
              </a>
            </div>
            <div className="col">
              <span
                className={`sentiment-container sentiment-${comment.sentiment.toLowerCase()}`}
              >
                {comment.sentiment}
              </span>
            </div>
          </div>
        ))}
      </div>
      {totalPages > 1 && (
        <div className="pagination">
          <button
            className="pagination-btn"
            onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
            disabled={currentPage === 1}
          >
            {"<"}
          </button>
          <span className="pagination-info">
            {currentPage} / {totalPages}
          </span>
          <button
            className="pagination-btn"
            onClick={() =>
              setCurrentPage((prev) => Math.min(prev + 1, totalPages))
            }
            disabled={currentPage === totalPages}
          >
            {">"}
          </button>
        </div>
      )}
    </div>
  );
};

export default Comments;
