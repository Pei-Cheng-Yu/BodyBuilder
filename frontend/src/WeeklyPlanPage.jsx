import React, { useState } from "react";
import "./WeeklyPlanPage.css";

const DAYS = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday",
];

const INITIAL_DATA = [
  {
    id: "block-1",
    day: "Monday",
    title: "胸部與三頭訓練",
    exercises: [
      { id: "e1", title: "臥推", sets: "4x10" },
      { id: "e2", title: "啞鈴飛鳥", sets: "3x12" },
    ],
  },
  {
    id: "block-2",
    day: "Wednesday",
    title: "背部與二頭訓練",
    exercises: [{ id: "e4", title: "引體向上", sets: "3xMax" }],
  },
];

const WeeklyPlanPage = () => {
  const [blocks, setBlocks] = useState(INITIAL_DATA);
  const [draggedItem, setDraggedItem] = useState(null);

  // 優化狀態：搜尋中與彈出視窗資料
  const [isSearching, setIsSearching] = useState(false);
  const [modalData, setModalData] = useState(null);

  // --- API 查詢邏輯 (優化版) ---
  const handleExerciseDoubleClick = async (exName) => {
    setIsSearching(true);

    // 模擬 API 請求延遲 1.5 秒
    setTimeout(() => {
      const mockResult = {
        name: exName,
        description: `這是關於 ${exName} 的詳細訓練說明。這項動作主要針對目標肌群進行強化，建議保持核心穩定。`,
        image: "https://via.placeholder.com/300x200?text=Exercise+Demo",
      };
      setModalData(mockResult);
      setIsSearching(false);
    }, 1500);
  };

  // --- 拖曳邏輯 (保持不變) ---
  const handleDragStart = (e, type, payload) => {
    setDraggedItem({ type, ...payload });
    if (type === "EXERCISE") e.stopPropagation();
    e.target.classList.add("is-dragging");
  };

  const handleDragEnd = (e) => {
    e.target.classList.remove("is-dragging");
    setDraggedItem(null);
  };

  const handleDrop = (
    e,
    targetDay,
    targetBlockId = null,
    targetExId = null,
  ) => {
    e.preventDefault();
    e.stopPropagation();
    if (!draggedItem) return;
    const { type, id, sourceBlockId } = draggedItem;

    if (type === "BLOCK") {
      setBlocks((prev) =>
        prev.map((b) => (b.id === id ? { ...b, day: targetDay } : b)),
      );
    } else if (type === "EXERCISE") {
      setBlocks((prev) => {
        const nextData = JSON.parse(JSON.stringify(prev));
        const sourceBlock = nextData.find((b) => b.id === sourceBlockId);
        const targetBlock = targetBlockId
          ? nextData.find((b) => b.id === targetBlockId)
          : sourceBlock;
        if (!sourceBlock || !targetBlock) return prev;
        const exIndex = sourceBlock.exercises.findIndex((ex) => ex.id === id);
        const [movedEx] = sourceBlock.exercises.splice(exIndex, 1);
        if (targetExId) {
          const targetIndex = targetBlock.exercises.findIndex(
            (ex) => ex.id === targetExId,
          );
          targetBlock.exercises.splice(targetIndex, 0, movedEx);
        } else {
          targetBlock.exercises.push(movedEx);
        }
        return nextData;
      });
    }
  };

  return (
    <div className="weekly-container">
      <div className="weekly-header">
        <h1>訓練週計畫</h1>
        {isSearching && (
          <div className="searching-indicator">
            <div className="spinner"></div>
            <span>搜尋資料庫中...</span>
          </div>
        )}
      </div>

      <div className="board-columns">
        {DAYS.map((day) => (
          <div
            key={day}
            className="day-column"
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => handleDrop(e, day)}
          >
            <div className="column-header">{day}</div>
            <div className="column-content">
              {blocks
                .filter((b) => b.day === day)
                .map((block) => (
                  <div
                    key={block.id}
                    className="workout-block"
                    draggable
                    onDragStart={(e) =>
                      handleDragStart(e, "BLOCK", { id: block.id })
                    }
                    onDragEnd={handleDragEnd}
                    onDrop={(e) => handleDrop(e, day, block.id)}
                  >
                    <div className="workout-block-header">{block.title}</div>
                    <div className="block-exercises">
                      {block.exercises.map((ex) => (
                        <div
                          key={ex.id}
                          className="exercise-mini-card"
                          draggable
                          onDragStart={(e) =>
                            handleDragStart(e, "EXERCISE", {
                              id: ex.id,
                              sourceBlockId: block.id,
                            })
                          }
                          onDragEnd={handleDragEnd}
                          onDrop={(e) => handleDrop(e, day, block.id, ex.id)}
                          onDragOver={(e) => e.preventDefault()}
                          onDoubleClick={() =>
                            handleExerciseDoubleClick(ex.title)
                          }
                        >
                          <span className="exercise-name">{ex.title}</span>
                          <span className="exercise-sets">{ex.sets}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
            </div>
          </div>
        ))}
      </div>

      {/* --- Modal 彈出視窗 --- */}
      {modalData && (
        <div className="modal-overlay" onClick={() => setModalData(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setModalData(null)}>
              &times;
            </button>
            <h2>{modalData.name}</h2>
            <img
              src={modalData.image}
              alt={modalData.name}
              className="modal-image"
            />
            <p>{modalData.description}</p>
            <button className="modal-btn" onClick={() => setModalData(null)}>
              關閉
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default WeeklyPlanPage;
