
let message;

export async function getMessage() {
  const response = await fetch("http://127.0.0.1:8000/hello");
  const json = await response.json();
  return json.message;
}

export async function startCamera(videoElement) {
  try {
    // getUserMedia를 사용하여 카메라 스트림 가져오기
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    videoElement.srcObject = stream; // 비디오 요소에 스트림 연결
    videoElement.play(); // 비디오 재생
    return stream; // 필요하면 스트림 반환
  } catch (err) {
    console.error("카메라 접근 오류:", err);
    throw new Error("카메라 접근을 허용해주세요.");
  }
}

export function captureFrame(videoElement) {
  const canvas = document.createElement("canvas");
  const context = canvas.getContext("2d");

  // 캔버스 크기를 비디오 크기에 맞춤
  canvas.width = videoElement.videoWidth;
  canvas.height = videoElement.videoHeight;

  // 비디오 프레임을 캔버스에 그리기
  context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

  // 캔버스의 픽셀 데이터를 가져오기
  const frameData = context.getImageData(0, 0, canvas.width, canvas.height);

  return frameData; // ImageData 객체 반환
}
export function captureFrameAsBase64(videoElement) {
  const canvas = document.createElement("canvas");
  const context = canvas.getContext("2d");

  canvas.width = videoElement.videoWidth;
  canvas.height = videoElement.videoHeight;

  context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

  // Base64로 변환
  return canvas.toDataURL("image/png"); // 예: "data:image/png;base64,..."
}