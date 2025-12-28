import React, { useState, useRef, useEffect } from 'react';
import './ChatPage.css'; // 引入樣式
import { sendMessageToBackend } from './services/api'; // 引入剛剛寫的假 API
import { Send } from 'lucide-react';

const ChatPage = () => {
  // 1. 定義狀態 (State)
  const [messages, setMessages] = useState([
    { id: 1, role: 'assistant', content: '哈囉！我是 BodyBuilder AI。請上傳照片或輸入數據，讓我為您分析。' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // 用來控制捲軸自動滾到底部
  const messagesEndRef = useRef(null);

  // 2. 自動捲動效果：每當 messages 變動，就滾到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // 3. 處理發送訊息
  const handleSend = async () => {
    if (inputValue.trim() === '') return; // 防止傳送空字串

    // A. 立即顯示使用者的訊息
    const userMsg = { 
      id: Date.now(), 
      role: 'user', 
      content: inputValue 
    };
    setMessages((prev) => [...prev, userMsg]);
    setInputValue(''); // 清空輸入框
    setIsLoading(true); // 開始轉圈圈

    try {
      // B. 呼叫 (模擬) 後端 API
      const response = await sendMessageToBackend(userMsg.content);

      // C. 收到回應後，顯示 AI 的訊息
      const aiMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.reply // 對應 api.js 回傳的欄位
      };
      setMessages((prev) => [...prev, aiMsg]);
      
    } catch (error) {
      console.error("API Error:", error);
      // 錯誤處理：顯示錯誤訊息給使用者
      setMessages((prev) => [...prev, { id: Date.now(), role: 'assistant', content: '抱歉，伺服器出了點問題。' }]);
    } finally {
      setIsLoading(false); // 結束轉圈圈
    }
  };

  // 支援按 Enter 發送
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
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
          <div key={msg.id} className={`message-row ${msg.role === 'user' ? 'user-row' : 'ai-row'}`}>
            <div className={`message-bubble ${msg.role}`}>
              {msg.content}
            </div>
          </div>
        ))}
        
        {/* Loading 動畫 (三個跳動的點) */}
        {isLoading && (
          <div className="message-row ai-row">
            <div className="message-bubble assistant loading-bubble">
              <span className="dot">.</span><span className="dot">.</span><span className="dot">.</span>
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