"use strict";
const videos = [...document.querySelectorAll("video")];
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

function pauseVideos() {
  videos.forEach(video => video.pause());
}

function playVideos() {
  if (document.hidden || reducedMotion.matches) return;
  videos.forEach(video => {
    video.muted = true;
    const playback = video.play();
    if (playback) playback.catch(() => { video.controls = true; });
  });
}

if (reducedMotion.matches) pauseVideos();
else playVideos();

document.addEventListener("visibilitychange", () => {
  if (document.hidden) pauseVideos();
  else playVideos();
});
reducedMotion.addEventListener("change", () => {
  if (reducedMotion.matches) pauseVideos();
  else playVideos();
});

const copyCitation = document.getElementById("copy-citation");
const citationBibtex = document.getElementById("citation-bibtex");
if (copyCitation && citationBibtex) {
  copyCitation.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(citationBibtex.textContent.trim() + "\n");
      copyCitation.textContent = "Copied!";
      setTimeout(() => { copyCitation.textContent = "Copy BibTeX"; }, 2000);
    } catch {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(citationBibtex);
      selection.removeAllRanges();
      selection.addRange(range);
      copyCitation.textContent = "Text selected";
      setTimeout(() => { copyCitation.textContent = "Copy BibTeX"; }, 2000);
    }
  });
}
