<script>
  import { onMount } from "svelte";
  import { startCamera, captureFrameAsBase64 } from "./project.js";

  let videoElement;
  let isCapturing = false;
  let buttonLabel = "Start Capture";
  let message = ""; // 모델 예측 결과 저장
  let showImage = false;
  let randomImage = "";
  let imageInterval = null;
  let worker; // Web Worker 인스턴스
  let isBackground = false; // 현재 브라우저가 백그라운드인지 상태를 저장

  const imagePaths = ["pic1.png", "pic2.png", "pic3.png", "pic4.png", "pic5.png"];

  function getRandomImage() {
    const randomIndex = Math.floor(Math.random() * imagePaths.length);
    randomImage = imagePaths[randomIndex];
  }

  function startImageRotation() {
    if (!imageInterval) {
      getRandomImage();
      imageInterval = setInterval(() => {
        if (message === "Happy") {
          stopImageRotation();
        } else {
          getRandomImage();
        }
      }, 3000);
    }
  }

  function stopImageRotation() {
    clearInterval(imageInterval);
    imageInterval = null;
  }

  function requestNotificationPermission() {
    if (Notification.permission === "default") {
      Notification.requestPermission().then((permission) => {
        if (permission !== "granted") {
          console.error("Notification permission not granted");
        }
      });
    }
  }

  function showNotification(message) {
    if (isBackground && Notification.permission === "granted") {
      new Notification("얼굴 상태 알림", { body: message, icon: "alert-icon.png" });
    }
  }

  function startWorker() {
    if (!worker) {
      worker = new Worker("/worker.js");

      worker.onmessage = function (e) {
        const result = e.data;

        if (result.error) {
          console.error("Worker 오류:", result.error);
          return;
        }

        message = result.path;

        if (message === "Happy") {
          stopImageRotation();
          showImage = false;
        } else if (message === "Angry" || message === "Sad") {
          showImage = true;
          startImageRotation();
          showNotification(`현재 상태: ${message}`);
        }
      };
    }
  }

  async function processFrame() {
    if (!isCapturing) return; // 캡처가 중단되면 종료

    const base64Image = captureFrameAsBase64(videoElement);
    if (worker) {
      worker.postMessage({ base64Image }); // Web Worker로 데이터 전송
    }

    if (isCapturing) {
      requestAnimationFrame(processFrame); // 활성화된 경우에만 다음 프레임 예약
    }
  }

  function toggleCapture() {
    isCapturing = !isCapturing;
    buttonLabel = isCapturing ? "Stop Capture" : "Start Capture";

    if (isCapturing) {
      console.log("Frame capture started.");
      processFrame();
    } else {
      console.log("Frame capture stopped.");
      if (worker) {
        worker.terminate(); // Web Worker 종료
        worker = null; // Worker 참조 해제
      }
      stopImageRotation(); // 이미지 변경 중지
    }
  }

  function handleVisibilityChange() {
    isBackground = document.hidden;
    console.log(isBackground ? "탭이 비활성화되었습니다." : "탭이 활성화되었습니다.");
  }

  function cleanupResources() {
    if (worker) {
      worker.terminate(); // Web Worker 종료
      worker = null;
    }
    stopImageRotation();
  }

  onMount(() => {
    document.addEventListener("visibilitychange", handleVisibilityChange);
    window.addEventListener("beforeunload", cleanupResources); // 페이지 종료 시 정리
    startCamera(videoElement).catch((error) => alert(error.message));
    requestNotificationPermission();
    startWorker();
  });
</script>

<main>
  <p>상태: {message}</p>

  <div class="video-image-container">
    <div class="video-wrapper">
      <video autoplay playsinline bind:this={videoElement} width="640" height="480"></video>
    </div>

    {#if showImage}
      <div class="image-wrapper">
        <img src={randomImage} alt="Random Image" width="200" height="200" />
        <button on:click={() => (showImage = false)}>닫기</button>
      </div>
    {/if}
  </div>

  <button on:click={toggleCapture}>{buttonLabel}</button>
</main>

<style>
  .video-image-container {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 2em;
  }

  .video-wrapper {
    flex: 1;
  }

  .image-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1em;
  }

  .hide-button {
    margin-top: 1em;
    padding: 0.5em 1em;
    background-color: #ff4d4d;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  .hide-button:hover {
    background-color: #ff3333;
  }
</style>
