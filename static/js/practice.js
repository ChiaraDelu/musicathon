document.querySelectorAll(".practice-word").forEach((item) => {
  const word = item.dataset.word;
  const btn = item.querySelector(".practice-btn");
  const feedback = item.querySelector(".practice-feedback");

  btn.addEventListener("click", async () => {
    btn.disabled = true;
    feedback.textContent = "🎙️ Listening...";

    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (err) {
      feedback.textContent = `Microphone error: ${err.message}`;
      btn.disabled = false;
      return;
    }

    const recorder = new MediaRecorder(stream);
    const chunks = [];

    recorder.addEventListener("dataavailable", (e) => chunks.push(e.data));
    recorder.addEventListener("stop", async () => {
      stream.getTracks().forEach((track) => track.stop());

      const blob = new Blob(chunks, { type: "audio/webm" });
      const formData = new FormData();
      formData.append("audio", blob, "practice.webm");
      formData.append("word", word);

      feedback.textContent = "Checking...";

      try {
        const response = await fetch("/check-pronunciation", { method: "POST", body: formData });
        const result = await response.json();

        if (!response.ok) {
          feedback.textContent = `Error: ${result.error}`;
        } else if (result.correct) {
          feedback.textContent = "✅ Great job!";
        } else {
          feedback.textContent = `❌ Try again (heard: "${result.transcript}")`;
        }
      } catch (err) {
        feedback.textContent = `Error: ${err.message}`;
      }

      btn.disabled = false;
    });

    recorder.start();
    feedback.textContent = "🎙️ Say the word now...";
    setTimeout(() => recorder.stop(), 2500);
  });
});
