import React, { useState } from "react";
import "./WeeklyPlanPage.css";
const EXERCISE_CACHE_PREFIX = "exercise:";
const CACHE_TTL = 1000 * 60 * 60 * 24 * 7;
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
      { id: "exr_41n2hdo2vCtq4F3E", title: "臥推", sets: "4x10" },
      { id: "exr_41n2hdo2vCtq4F3E", title: "啞鈴飛鳥", sets: "3x12" },
    ],
  },
  {
    id: "block-2",
    day: "Wednesday",
    title: "背部與二頭訓練",
    exercises: [
      { id: "exr_41n2hdo2vCtq4F3E", title: "引體向上", sets: "3xMax" },
    ],
  },
];
function getCachedExercise(exerciseId) {
  const raw = localStorage.getItem(EXERCISE_CACHE_PREFIX + exerciseId);
  if (!raw) return null;

  try {
    const parsed = JSON.parse(raw);

    // TTL check
    if (Date.now() - parsed.cachedAt > CACHE_TTL) {
      localStorage.removeItem(EXERCISE_CACHE_PREFIX + exerciseId);
      return null;
    }

    return parsed.data;
  } catch {
    return null;
  }
}
function setCachedExercise(exerciseId, data) {
  localStorage.setItem(
    EXERCISE_CACHE_PREFIX + exerciseId,
    JSON.stringify({
      cachedAt: Date.now(),
      data,
    }),
  );
}

const WeeklyPlanPage = () => {
  const [blocks, setBlocks] = useState(INITIAL_DATA);
  const [draggedItem, setDraggedItem] = useState(null);

  // 優化狀態：搜尋中與彈出視窗資料
  const [isSearching, setIsSearching] = useState(false);
  const [modalData, setModalData] = useState(null);

  // --- API 查詢邏輯 (優化版) ---
  const handleExerciseDoubleClick = async (exerciseId) => {
    try {
      setIsSearching(true);

      // 1. Check cache first
      const cached = getCachedExercise(exerciseId);
      if (cached) {
        setModalData(cached);
        return;
      }

      // 2. Fetch from backend
      const res = await fetch(
        `http://localhost:8001/api/exercises/${exerciseId}`,
      );

      if (!res.ok) {
        throw new Error("Failed to fetch exercise detail");
      }

      const data = await res.json();

      const modalPayload = {
        name: data.name,
        description: data.overview,
        bodyParts: data.bodyParts,
        image: data.imageUrl,
        video: data.videoUrl,
        instructions: data.instructions,
        exerciseTips: data.exerciseTips,
      };

      // 3. Cache it
      setCachedExercise(exerciseId, modalPayload);

      // 4. Update UI
      setModalData(modalPayload);
    } catch (err) {
      console.error(err);
      alert("Failed to load exercise detail");
    } finally {
      setIsSearching(false);
    }
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
                          onDoubleClick={() => handleExerciseDoubleClick(ex.id)}
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

      {modalData && (
        <div className="modal-overlay" onClick={() => setModalData(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setModalData(null)}>
              &times;
            </button>

            {/* Title */}
            <h2 className="modal-title">{modalData.name}</h2>
            {/* Description */}
            {modalData.description && (
              <p className="modal-description">{modalData.description}</p>
            )}
            {/* Body parts */}
            {modalData.bodyParts?.length > 0 && (
              <div className="modal-tags">
                {modalData.bodyParts.map((part) => (
                  <span key={part} className="tag">
                    {part}
                  </span>
                ))}
              </div>
            )}

            {/* Image */}
            {modalData.image && (
              <img
                src={modalData.image}
                alt={modalData.name}
                className="modal-image"
                loading="lazy"
              />
            )}

            {/* Instructions */}
            {modalData.instructions?.length > 0 && (
              <div className="modal-section">
                <h3>Instructions</h3>
                <ol>
                  {modalData.instructions.map((step, idx) => (
                    <li key={idx}>{step}</li>
                  ))}
                </ol>
              </div>
            )}

            {/* Tips */}
            {modalData.exerciseTips?.length > 0 && (
              <div className="modal-section">
                <h3>Tips</h3>
                <ul>
                  {modalData.exerciseTips.map((tip, idx) => (
                    <li key={idx}>{tip}</li>
                  ))}
                </ul>
              </div>
            )}
            {/* Video */}
            {modalData.video && (
              <video controls preload="metadata" className="modal-video">
                <source src={modalData.video} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            )}
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
