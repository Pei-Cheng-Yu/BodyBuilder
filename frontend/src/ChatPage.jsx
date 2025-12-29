import React, { useState, useRef, useEffect } from "react";
import "./ChatPage.css";
import { Send, Paperclip, X } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const API_BASE = import.meta.env.VITE_API_URL;
const PROGRESS_ID = "progress";

const ChatPage = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: "assistant",
      content:
        "哈囉！我是 BodyBuilder AI。請上傳 InBody PDF 或輸入問題，讓我為您分析。",
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

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
      next[idx] = progressMsg;
      return next;
    });
  };

  const removeProgress = () => {
    setMessages((prev) => prev.filter((m) => m.id !== PROGRESS_ID));
  };

  // --- SSE parser over fetch stream ---
  const streamSSE = async (response) => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";
    let doneReading = false;
    while (!doneReading) {
      const { done, value } = await reader.read();
      if (done) {
        doneReading = true;
        break;
      }

      buffer += decoder.decode(value, { stream: true });

      // events separated by blank line
      const parts = buffer.split("\n\n");
      buffer = parts.pop() || "";

      for (const chunk of parts) {
        const dataLine = chunk.split("\n").find((l) => l.startsWith("data: "));
        if (!dataLine) continue;

        const jsonStr = dataLine.slice("data: ".length).trim();
        if (!jsonStr) continue;

        const data = JSON.parse(jsonStr);

        if (data.type === "progress") {
          upsertProgress(data.message);
        } else if (data.type === "message") {
          removeProgress();
          setMessages((prev) => [
            ...prev,
            { id: Date.now(), role: "assistant", content: data.content },
          ]);
        } else if (data.type === "error") {
          removeProgress();
          setMessages((prev) => [
            ...prev,
            { id: Date.now(), role: "assistant", content: `❌ ${data.error}` },
          ]);
        } else if (data.type === "end") {
          return;
        }
      }
    }
  };

  const sendToBackend = async ({ text, file }) => {
    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append("message", text ?? "");
      if (file) formData.append("inbody_pdf", file);

      const res = await fetch(`${API_BASE}/chat/stream`, {
        method: "POST",
        body: formData,
        credentials: "include",
      });

      if (!res.ok) {
        const t = await res.text();
        throw new Error(`HTTP ${res.status}: ${t}`);
      }

      await streamSSE(res);
    } catch (e) {
      removeProgress();
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          role: "assistant",
          content: "連線中斷，請再試一次。",
        },
      ]);
      throw new Error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = async () => {
    if (isLoading) return;

    const hasText = inputValue.trim().length > 0;
    const hasFile = !!selectedFile;
    if (!hasText && !hasFile) return;

    // render user message locally
    if (hasText) {
      setMessages((prev) => [
        ...prev,
        { id: Date.now(), role: "user", content: inputValue },
      ]);
    } else {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          role: "user",
          content: `（已送出檔案：${selectedFile.name}）`,
        },
      ]);
    }

    const textToSend = hasText
      ? inputValue
      : "I just uploaded my InBody report PDF. Please analyze it.";
    const fileToSend = selectedFile;

    setInputValue("");
    setSelectedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";

    await sendToBackend({ text: textToSend, file: fileToSend });
  };

  const handleFilePickClick = () => {
    if (isLoading) return;
    fileInputRef.current?.click();
  };

  const handleFileChange = (e) => {
    const f = e.target.files?.[0] || null;
    if (!f) return;
    setSelectedFile(f);
    // If you want "send immediately" on select, uncomment:
    // handleSend();
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const disabled = isLoading;

  return (
    <div className="chat-container">
      <header className="chat-header">
        <h1>BodyBuilder AI Agent</h1>
      </header>

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

        {isLoading && (
          <div className="message-row ai-row">
            <div className="message-bubble assistant loading-bubble">
              <span className="dot">.</span>
              <span className="dot">.</span>
              <span className="dot">.</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf"
          style={{ display: "none" }}
          disabled={disabled}
          onChange={handleFileChange}
        />

        <button
          type="button"
          className="icon-button"
          disabled={disabled}
          onClick={handleFilePickClick}
          title="上傳 InBody PDF"
        >
          <Paperclip size={20} />
        </button>

        {selectedFile && (
          <div className="file-chip">
            <span className="file-name">{selectedFile.name}</span>
            <button
              type="button"
              className="chip-x"
              disabled={disabled}
              onClick={() => {
                setSelectedFile(null);
                if (fileInputRef.current) fileInputRef.current.value = "";
              }}
              title="移除檔案"
            >
              <X size={14} />
            </button>
          </div>
        )}

        <input
          type="text"
          placeholder="輸入您的問題..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyPress}
          disabled={disabled}
        />

        <button
          onClick={handleSend}
          disabled={disabled || (!inputValue.trim() && !selectedFile)}
          className="send-button"
          title="送出"
        >
          <Send size={20} />
        </button>
      </div>
    </div>
  );
};

export default ChatPage;
