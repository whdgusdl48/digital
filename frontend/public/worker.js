// worker.js
self.onmessage = async function (e) {
  const { base64Image } = e.data;

  try {
    const response = await fetch("http://127.0.0.1:8000/upload", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image: base64Image }),
    });

    if (response.ok) {
      const result = await response.json();
      self.postMessage(result); // 메인 스레드로 결과 전달
    } else {
      console.error("서버 오류:", response.statusText);
      self.postMessage({ error: "Server error" });
    }
  } catch (error) {
    console.error("전송 오류:", error);
    self.postMessage({ error: "Transmission error" });
  }
};
