const recordBtn = document.getElementById("recordBtn");
const stopBtn = document.getElementById("stopBtn");
const cloneBtn = document.getElementById("cloneBtn");
const status = document.getElementById("status");
const preview = document.getElementById("preview");

let mediaRecorder;
let chunks = [];
let audioBlob;

recordBtn.addEventListener("click", async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  chunks = [];

  mediaRecorder.addEventListener("dataavailable", (e) => chunks.push(e.data));
  mediaRecorder.addEventListener("stop", () => {
    audioBlob = new Blob(chunks, { type: "audio/webm" });
    preview.src = URL.createObjectURL(audioBlob);
    preview.style.display = "block";
    cloneBtn.disabled = false;
    stream.getTracks().forEach((track) => track.stop());
  });

  mediaRecorder.start();
  recordBtn.disabled = true;
  stopBtn.disabled = false;
  cloneBtn.disabled = true;
  status.textContent = "Recording... speak naturally for at least 30 seconds.";
});

stopBtn.addEventListener("click", () => {
  mediaRecorder.stop();
  recordBtn.disabled = false;
  stopBtn.disabled = true;
  status.textContent = "Recording stopped. Listen back, then clone your voice.";
});

cloneBtn.addEventListener("click", async () => {
  if (!audioBlob) return;

  cloneBtn.disabled = true;
  status.textContent = "Cloning your voice with ElevenLabs...";

  const formData = new FormData();
  formData.append("audio", audioBlob, "voice_sample.webm");

  try {
    const response = await fetch("/clone-voice", { method: "POST", body: formData });
    const data = await response.json();

    if (response.ok) {
      status.textContent = "Voice cloned! Search for a song and it will be read in your voice.";
    } else {
      status.textContent = `Error: ${data.error}`;
      cloneBtn.disabled = false;
    }
  } catch (err) {
    status.textContent = `Error: ${err.message}`;
    cloneBtn.disabled = false;
  }
});
