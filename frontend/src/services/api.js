// 這是用來模擬後端回應的假 API
// 等後端完成後，我們只要把這裡換成 fetch() 就可以了

export const sendMessageToBackend = async (userMessage) => {
  // 模擬網路延遲 1 秒 (1000ms)
  return new Promise((resolve) => {
    setTimeout(() => {
      // 這裡模擬後端回傳的 Schema
      // 假設未來的 Agent 會針對你的輸入做回應
      resolve({
        reply: `(模擬回應) 我收到了你的訊息：「${userMessage}」。我是 BodyBuilder AI 助手，請問有什麼我可以幫你的？`,
        timestamp: new Date().toISOString()
      });
    }, 1000); 
  });
};