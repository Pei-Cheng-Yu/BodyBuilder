import React, { useState, useRef, useEffect } from "react";
import "./ChatPage.css"; // 引入樣式
import { Send } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
const API_BASE = import.meta.env.VITE_API_URL;
const PROGRESS_ID = "progress";
const ChatPage = () => {
  // 1. 定義狀態 (State)
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: "assistant",
      content:
        "哈囉！我是 BodyBuilder AI。請上傳照片或輸入數據，讓我為您分析。",
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const upsertProgress = (text) => {
    setMessages((prev) => {
      const idx = prev.findIndex((m) => m.id === PROGRESS_ID);
      const progressMsg = {
        id: PROGRESS_ID,
        role: "assistant",
        content: text,
        kind: "progress",
      };

      if (idx === -1) return [...prev, progressMsg];

      const next = [...prev];
      next[idx] = progressMsg; // replace content
      return next;
    });
  };

  const removeProgress = () => {
    setMessages((prev) => prev.filter((m) => m.id !== PROGRESS_ID));
  };
  // 用來控制捲軸自動滾到底部
  const messagesEndRef = useRef(null);

  // 2. 自動捲動效果：每當 messages 變動，就滾到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // 3. 處理發送訊息
  const handleSend = async () => {
    if (inputValue.trim() === "") return;

    const userMsg = {
      id: Date.now(),
      role: "user",
      content: inputValue,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputValue("");
    setIsLoading(true);

    const encodedMessage = encodeURIComponent(userMsg.content);

    const evtSource = new EventSource(
      `${API_BASE}/chat/stream?message=${encodedMessage}`,
      { withCredentials: true },
    );

    evtSource.onopen = () => {
      console.log("✅ SSE opened:", evtSource.url);
    };

    evtSource.onmessage = (event) => {
      console.log("📩 SSE:", event.data);
      const data = JSON.parse(event.data);

      if (data.type === "progress") {
        upsertProgress(data.message);
        return;
      }
      if (data.type === "message") {
        removeProgress();
        setMessages((prev) => [
          ...prev,
          { id: Date.now(), role: "assistant", content: data.content },
        ]);
      }

      if (data.type === "end") {
        console.log("✅ SSE ended");
        setIsLoading(false);
        evtSource.close();
      }
    };

    evtSource.onerror = (err) => {
      // ⚠️ 不要立刻 close，先觀察是不是短暫網路/自動重連
      console.warn(
        "⚠️ SSE error (will auto-reconnect):",
        err,
        "readyState:",
        evtSource.readyState,
      );

      // readyState === 2 代表 CLOSED（真的斷了）
      if (evtSource.readyState === 2) {
        setIsLoading(false);
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now(),
            role: "assistant",
            content: "連線中斷，請再試一次。",
          },
        ]);
      }
    };
  };
  // 支援按 Enter 發送
  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-container">
      {/* 標題列 */}
      <header className="chat-header">
        <h1>BodyBuilder AI Agent</h1>
      </header>
      {/* 訊息顯示區 */}
      <div className="messages-area">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`message-row ${msg.role === "user" ? "user-row" : "ai-row"}`}
          >
            <div className={`message-bubble ${msg.role}`}>
              {msg.role === "assistant" ? (
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {String(msg.content)}
                </ReactMarkdown>
              ) : (
                <span style={{ whiteSpace: "pre-wrap" }}>{msg.content}</span>
              )}
            </div>
          </div>
        ))}

        {/* Loading 動畫 (三個跳動的點) */}
        {isLoading && (
          <div className="message-row ai-row">
            <div className="message-bubble assistant loading-bubble">
              <span className="dot">.</span>
              <span className="dot">.</span>
              <span className="dot">.</span>
            </div>
          </div>
        )}

        {/* 隱藏的元素，用來定位捲軸底部 */}
        <div ref={messagesEndRef} />
      </div>

      {/* 輸入區 */}
      <div className="input-area">
        <input
          type="text"
          placeholder="輸入您的問題..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyPress}
          disabled={isLoading} // Loading 時鎖住輸入框
        />
        <button
          onClick={handleSend}
          disabled={isLoading || !inputValue.trim()}
          className="send-button"
        >
          {/* 2. 將「發送」換成圖示 */}
          <Send size={20} />
        </button>
      </div>
    </div>
  );
};

export default ChatPage;
