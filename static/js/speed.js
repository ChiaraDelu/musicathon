(() => {
  const audio = document.getElementById("player");
  const speedButtons = document.querySelectorAll(".speed-btn");

  if (audio && speedButtons.length) {
    speedButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        audio.playbackRate = parseFloat(btn.dataset.speed);
        speedButtons.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
      });
    });
  }
})();
