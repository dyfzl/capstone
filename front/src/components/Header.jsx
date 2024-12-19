import React, { useState } from "react";
import "./Header.css";
import HeaderLogo from "./images/TeamLogo.png";
import InstagramLogo from "./images/instagram.png";
import YoutubeLogo from "./images/youtube.png";
import FacebookLogo from "./images/facebook.png";
import SearchIcon from "./images/search.png";

const Header = ({ onSearchComplete }) => {
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [keyword, setKeyword] = useState("");
  const [platform, setPlatform] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!startDate || !endDate) {
      alert("기간을 설정하세요");
      return;
    }
    if (keyword.trim().length < 2) {
      alert("검색어는 두 글자 이상으로 입력하세요");
      return;
    }
    if (!platform) {
      alert("플랫폼을 선택하세요");
      return;
    }

    console.log("Header handleSearch started");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/crawl-and-analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          account: keyword,
          start_date: startDate,
          end_date: endDate,
          platform: platform,
        }),
      });

      if (!response.ok) {
        console.error("Error:", response.status, response.statusText);
        throw new Error("Failed to fetch data from backend");
      }

      const data = await response.json();
      console.log("Response from Backend:", data);

      alert(
        `댓글 분석이 완료되었습니다.`
      );

      // onSearchComplete 콜백 호출
      if (onSearchComplete) {
        console.log("Executing onSearchComplete");
        onSearchComplete(data.files); // 파일 정보를 전달
      }
    } catch (error) {
      console.error("Failed to fetch data:", error);
      alert("크롤링 요청 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
      console.log("Header handleSearch ended");
    }
  };

  const handleEnterPress = (e) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  const refreshPage = () => {
    window.location.reload();
  };

  return (
    <div className="header-container">
      <img
        src={HeaderLogo}
        alt="Team Logo"
        className="header-logo"
        onClick={refreshPage}
      />
      <div className="header-content">
        <div className="search-period">
          <input
            type="date"
            id="start-date"
            className={`date-select ${startDate ? "date-active" : ""}`}
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
          ~
          <input
            type="date"
            id="end-date"
            className={`date-select ${endDate ? "date-active" : ""}`}
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
        </div>
        <div className="platform-select">
          <div className="custom-dropdown">
            <button
              className={`dropdown-button ${!platform ? "placeholder" : ""}`}
            >
              {platform ? (
                <>
                  <img
                    src={
                      platform === "youtube"
                        ? YoutubeLogo
                        : platform === "instagram"
                        ? InstagramLogo
                        : FacebookLogo
                    }
                    alt={platform}
                    className="dropdown-selected-icon"
                  />
                  {platform === "youtube"
                    ? "유튜브"
                    : platform === "instagram"
                    ? "인스타그램"
                    : "페이스북"}
                </>
              ) : (
                "플랫폼"
              )}
            </button>
            <div className="dropdown-menu">
              <div
                className="dropdown-item"
                onClick={() => setPlatform("youtube")}
              >
                <img
                  src={YoutubeLogo}
                  alt="YouTube Logo"
                  className="dropdown-icon"
                />
                유튜브
              </div>
              <div
                className="dropdown-item"
                onClick={() => setPlatform("instagram")}
              >
                <img
                  src={InstagramLogo}
                  alt="Instagram Logo"
                  className="dropdown-icon"
                />
                인스타그램
              </div>
              <div
                className="dropdown-item"
                onClick={() => setPlatform("facebook")}
              >
                <img
                  src={FacebookLogo}
                  alt="Facebook Logo"
                  className="dropdown-icon"
                />
                페이스북
              </div>
            </div>
          </div>
        </div>
        <div className="search-input">
          <input
            type="text"
            placeholder="Search"
            className={`input-height ${
              keyword.trim() !== "" ? "input-active" : ""
            }`}
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            onKeyDown={handleEnterPress}
          />
          <button className="input-button" onClick={handleSearch}>
            {loading ? (
              <p className="analyze-comment">분석 중...</p>
            ) : (
              <img src={SearchIcon} alt="Search Icon" className="search-icon" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Header;
