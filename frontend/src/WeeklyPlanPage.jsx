import React, { useState, useEffect } from "react";
import "./WeeklyPlanPage.css";
const API_BASE = import.meta.env.VITE_API_URL;
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

async function patchBlockDay(blockId, day) {
  const res = await fetch(`${API_BASE}/blocks/${blockId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ day }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function patchMoveExercise(exerciseInstanceId, blockId, order) {
  const res = await fetch(`${API_BASE}/exercises/move/${exerciseInstanceId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ blockId, order }),
  });
  if (!res.ok) {
    const t = await res.text();
    console.log("❌ move exercise error:", t);
    throw new Error(t);
  }
  return res.json();
}

const WeeklyPlanPage = () => {
  const [blocks, setBlocks] = useState(null);
  const [draggedItem, setDraggedItem] = useState(null);

  // 優化狀態：搜尋中與彈出視窗資料
  const [isSearching, setIsSearching] = useState(false);
  const [modalData, setModalData] = useState(null);

  useEffect(() => {
    const loadPlan = async () => {
      try {
        const res = await fetch(`${API_BASE}/plans`, {
          method: "GET",
          credentials: "include",
        });

        if (!res.ok) {
          const t = await res.text();
          throw new Error(`HTTP ${res.status}: ${t}`);
        }

        const data = await res.json();

        // backend guarantees frontend format
        setBlocks(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error("Failed to load weekly plan:", err);
        setBlocks([]); // fallback = no plan
      }
    };

    loadPlan();
  }, []);
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

  const handleDrop = async (
    e,
    targetDay,
    targetBlockId = null,
    targetExId = null,
  ) => {
    e.preventDefault();
    e.stopPropagation();
    if (!draggedItem) return;

    const { type, id, sourceBlockId } = draggedItem;

    // snapshot for rollback
    const prevBlocks = blocks;

    if (type === "BLOCK") {
      // 1) optimistic UI
      setBlocks((prev) =>
        prev.map((b) => (b.id === id ? { ...b, day: targetDay } : b)),
      );

      // 2) persist
      try {
        await patchBlockDay(id, targetDay);
      } catch (err) {
        console.error(err);
        alert("更新失敗，已還原");
        setBlocks(prevBlocks); // rollback
      }
      return;
    } else if (type === "EXERCISE") {
      // Save snapshot for rollback
      const prevBlocks = blocks;

      // Determine destination block
      const destBlockId = targetBlockId ?? sourceBlockId;

      // We'll compute insert order and also do optimistic update
      let insertOrder = 0;

      setBlocks((prev) => {
        const next = JSON.parse(JSON.stringify(prev));

        const sourceBlock = next.find((b) => b.id === sourceBlockId);
        const destBlock = next.find((b) => b.id === destBlockId);
        if (!sourceBlock || !destBlock) return prev;

        const exIndex = sourceBlock.exercises.findIndex((ex) => ex.id === id);
        if (exIndex === -1) return prev;

        const [movedEx] = sourceBlock.exercises.splice(exIndex, 1);

        // compute insert order: before targetExId, else append
        if (targetExId) {
          const idx = destBlock.exercises.findIndex(
            (ex) => ex.id === targetExId,
          );
          insertOrder = idx === -1 ? destBlock.exercises.length : idx;
        } else {
          insertOrder = destBlock.exercises.length;
        }

        destBlock.exercises.splice(insertOrder, 0, movedEx);
        return next;
      });

      // Persist to backend (PATCH)
      try {
        await patchMoveExercise(id, destBlockId, insertOrder);
      } catch (err) {
        console.error(err);
        alert("更新失敗，已還原");
        setBlocks(prevBlocks); // rollback
      }
    }
  };

  if (blocks === null) {
    return (
      <div className="weekly-container">
        <h1>訓練週計畫</h1>
        <p>載入中...</p>
      </div>
    );
  }

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
      {blocks.length === 0 && (
        <div className="empty-plan">
          <p>目前尚未建立訓練計畫。</p>
          <p>請先產生或設定一個週計畫。</p>
        </div>
      )}
      <div className="board-columns">
        {DAYS.map((day) => {
          const dayBlocks = blocks.filter((b) => b.day === day);
          const activeBlocks = dayBlocks.filter((b) => !b.is_rest_day);
          return (
            <div
              key={day}
              className="day-column"
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => handleDrop(e, day)}
            >
              <div className="column-header">{day}</div>

              {/* ✅ only render content area if this day has blocks */}
              {
                <div className="column-content">
                  {activeBlocks.map((block) => (
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
                              handleExerciseDoubleClick(ex.exercise_id)
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
              }
            </div>
          );
        })}
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
