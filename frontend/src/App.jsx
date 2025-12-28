import React, { useState } from "react";
import ChatPage from "./ChatPage";
import WeeklyPlanPage from "./WeeklyPlanPage";

function App() {
  const [view, setView] = useState("plan");

  return (
    <div
      style={{
        display: "flex",
        width: "100vw",
        height: "100vh",
        overflow: "hidden",
        backgroundColor: "#f5f7fa",
        fontFamily: "sans-serif",
      }}
    >
      {/* 左側側邊欄 */}
      <aside
        style={{
          width: "240px",
          backgroundColor: "#1a1c23",
          color: "white",
          display: "flex",
          flexDirection: "column",
          padding: "20px 0",
          zIndex: 1000,
        }}
      >
        <div
          style={{
            padding: "0 20px 30px",
            fontSize: "1.2rem",
            fontWeight: "bold",
            color: "#3b82f6",
          }}
        >
          BODYBUILDER AI
        </div>

        <nav style={{ display: "flex", flexDirection: "column", gap: "5px" }}>
          <button
            onClick={() => setView("plan")}
            style={sidebarBtnStyle(view === "plan")}
          >
            📅 每週訓練計畫
          </button>
          <button
            onClick={() => setView("chat")}
            style={sidebarBtnStyle(view === "chat")}
          >
            💬 AI 健身助手
          </button>
        </nav>
      </aside>

      {/* 右側內容區 */}
      <main
        style={{
          flex: 1,
          position: "relative",
          overflowY: "auto",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {view === "plan" ? <WeeklyPlanPage /> : <ChatPage />}
      </main>
    </div>
  );
}

const sidebarBtnStyle = (active) => ({
  padding: "15px 25px",
  textAlign: "left",
  border: "none",
  background: active ? "#2d3748" : "transparent",
  color: active ? "#3b82f6" : "#cbd5e0",
  cursor: "pointer",
  fontSize: "0.95rem",
  fontWeight: "600",
  borderLeft: active ? "4px solid #3b82f6" : "4px solid transparent",
  transition: "0.2s",
});

export default App;
