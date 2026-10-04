'use strict';
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const heroVideos = [...document.querySelectorAll('.hero-videos video')];
const playButton = document.getElementById('play-showcase');
let playbackRequested = false;

function updatePlayButton() {
  const playing = heroVideos.some(video => !video.paused);
  playButton.setAttribute('aria-pressed', String(playing));
  playButton.innerHTML = playing ? '<span aria-hidden="true">Ⅱ</span> Pause examples' : '<span aria-hidden="true">▶</span> Play examples';
}
playButton.addEventListener('click', async () => {
  playbackRequested = !heroVideos.some(video => !video.paused);
  if (playbackRequested) await Promise.allSettled(heroVideos.map(video => video.play()));
  else heroVideos.forEach(video => video.pause());
  updatePlayButton();
});
heroVideos.forEach(video => {
  video.addEventListener('play', updatePlayButton);
  video.addEventListener('pause', updatePlayButton);
});
document.querySelectorAll('.clip-picker button').forEach(button => {
  button.addEventListener('click', async () => {
    const card = button.closest('.video-card');
    const video = card.querySelector('video');
    const task = card.dataset.task;
    card.querySelectorAll('.clip-picker button').forEach(choice => choice.setAttribute('aria-pressed', String(choice === button)));
    video.pause();
    video.poster = `media/${task}-30ep-${button.dataset.sample}.jpg`;
    video.src = `media/${task}-30ep-${button.dataset.sample}.mp4`;
    video.load();
    if (playbackRequested) await video.play().catch(() => {});
    updatePlayButton();
  });
});
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    heroVideos.forEach(video => video.pause());
    document.querySelectorAll('#native-gallery video').forEach(video => video.pause());
    playbackRequested = false;
    updatePlayButton();
  }
});
reducedMotion.addEventListener('change', event => {
  if (event.matches) {
    heroVideos.forEach(video => video.pause());
    playbackRequested = false;
    updatePlayButton();
  }
});

// Native media is configured from verified saved outputs, rather than guessed paths.
fetch('data/native-media.json').then(response => {
  if (!response.ok) throw new Error('Native media manifest unavailable');
  return response.json();
}).then(manifest => {
  if (!Array.isArray(manifest.clips) || !manifest.clips.length) return;
  const gallery = document.getElementById('native-gallery');
  manifest.clips.forEach(clip => {
    const article = document.createElement('article');
    article.className = 'video-card';
    const heading = document.createElement('div');
    heading.className = 'card-heading';
    const title = document.createElement('h3');
    title.textContent = clip.title;
    const model = document.createElement('span');
    model.textContent = clip.model;
    heading.append(title, model);
    const labels = document.createElement('div');
    labels.className = 'panel-labels';
    clip.panels.forEach(label => {
      const span = document.createElement('span');
      span.textContent = label;
      labels.append(span);
    });
    labels.style.gridTemplateColumns = `repeat(${clip.panels.length}, 1fr)`;
    const video = document.createElement('video');
    video.src = clip.src;
    video.poster = clip.poster;
    video.controls = true;
    video.muted = true;
    video.loop = true;
    video.playsInline = true;
    video.preload = 'metadata';
    video.setAttribute('aria-label', clip.alt);
    const caption = document.createElement('p');
    caption.className = 'caption';
    caption.textContent = clip.caption;
    article.append(heading);
    if (!clip.labels_in_media) article.append(labels);
    article.append(video, caption);
    gallery.append(article);
  });
  gallery.hidden = false;
}).catch(() => {});
