(() => {
  const audio = document.getElementById("player");
  const words = document.querySelectorAll(".word");

  if (audio && words.length) {
    const update = () => {
      const t = audio.currentTime;

      words.forEach((span) => {
        const start = parseFloat(span.dataset.start);
        const end = parseFloat(span.dataset.end);
        span.classList.toggle("active", t >= start && t < end);
      });

      if (!audio.paused && !audio.ended) {
        requestAnimationFrame(update);
      }
    };

    audio.addEventListener("play", () => requestAnimationFrame(update));
    audio.addEventListener("seeking", update);
  }
})();
