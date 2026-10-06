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
