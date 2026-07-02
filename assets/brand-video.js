/* Pleiades brand video playlist controller
   Static GitHub Pages cannot automatically list a folder, so this uses:
   /assets/video/brand-playlists.json
*/
(function () {
  'use strict';

  const MANIFEST_PATH = '/Pleiades/assets/video/brand-playlists.json';
  const STORAGE_KEYS = {
    scenery: 'pleiades.sceneryMode',
    audio: 'pleiades.videoAudio',
    volume: 'pleiades.videoVolume'
  };

  let activeVideo = null;
  let activePlaylist = [];
  let activeQueue = [];
  let activeIndex = 0;
  let activeSettings = {};

  function getBrandKey() {
    const required = document.body ? document.body.getAttribute('data-requires-access') || '' : '';
    return required.replace(/-.*/, '');
  }

  function isMobileWidth() {
    return window.matchMedia && window.matchMedia('(max-width: 760px)').matches;
  }

  function prefersReducedMotion() {
    return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  async function fetchManifest() {
    try {
      const response = await fetch(MANIFEST_PATH + '?v=' + Date.now(), { cache: 'no-store' });
      if (!response.ok) throw new Error('HTTP ' + response.status);
      return await response.json();
    } catch (error) {
      console.warn('[Pleiades Video] Manifest not available:', error.message);
      return null;
    }
  }

  function waitForVideo() {
    return new Promise(resolve => {
      const existing = document.querySelector('#pleiadesBrandCinematic video.brand-video-bg');
      if (existing) return resolve(existing);
      let tries = 0;
      const timer = setInterval(() => {
        const video = document.querySelector('#pleiadesBrandCinematic video.brand-video-bg');
        tries += 1;
        if (video || tries > 40) {
          clearInterval(timer);
          resolve(video || null);
        }
      }, 150);
    });
  }

  function buildPlaylist(brandConfig) {
    if (!brandConfig || !brandConfig.folder || !Array.isArray(brandConfig.videos)) return [];
    return brandConfig.videos
      .filter(Boolean)
      .map(file => file.startsWith('/') || file.startsWith('http') ? file : brandConfig.folder + file);
  }

  function shuffle(list) {
    const copy = list.slice();
    for (let i = copy.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      [copy[i], copy[j]] = [copy[j], copy[i]];
    }
    return copy;
  }

  function getVolume() {
    const stored = Number(localStorage.getItem(STORAGE_KEYS.volume));
    if (Number.isFinite(stored)) return Math.min(1, Math.max(0, stored));
    return 0.25;
  }

  function setVideoAudioState(video) {
    if (!video) return;
    const audioOn = localStorage.getItem(STORAGE_KEYS.audio) === 'on';
    video.muted = !audioOn;
    video.volume = getVolume();
  }

  function setVideoSource(video, src) {
    if (!video || !src) return;
    video.pause();
    video.loop = activePlaylist.length <= 1;
    video.innerHTML = '';
    const source = document.createElement('source');
    source.src = src;
    source.type = 'video/mp4';
    video.appendChild(source);
    setVideoAudioState(video);
    video.load();
    const playAttempt = video.play();
    if (playAttempt && typeof playAttempt.catch === 'function') playAttempt.catch(() => {});
    updateStatus(src);
  }

  function playCurrent() {
    if (!activeVideo || !activeQueue.length) return;
    setVideoSource(activeVideo, activeQueue[activeIndex]);
  }

  function playNext() {
    if (!activeQueue.length) return;
    activeIndex += 1;
    if (activeIndex >= activeQueue.length) {
      activeIndex = 0;
      if (activeSettings.mode === 'random') activeQueue = shuffle(activePlaylist);
    }
    playCurrent();
  }

  function playPrevious() {
    if (!activeQueue.length) return;
    activeIndex -= 1;
    if (activeIndex < 0) activeIndex = activeQueue.length - 1;
    playCurrent();
  }

  function createControls() {
    if (document.getElementById('brandVideoControls')) return;
    const controls = document.createElement('div');
    controls.id = 'brandVideoControls';
    controls.className = 'brand-video-controls';
    controls.innerHTML = `
      <button id="brandSceneryToggle" type="button">Enjoy the scenery</button>
      <button id="brandVideoPrev" type="button" title="Previous video">‹</button>
      <button id="brandVideoNext" type="button" title="Next video">›</button>
      <button id="brandAudioToggle" type="button">Audio off</button>
      <label class="brand-video-volume">Vol <input id="brandVolumeSlider" type="range" min="0" max="1" step="0.05"></label>
      <span id="brandVideoStatus" class="brand-video-status">Video ready</span>
    `;
    document.body.appendChild(controls);

    const sceneryToggle = document.getElementById('brandSceneryToggle');
    const audioToggle = document.getElementById('brandAudioToggle');
    const volumeSlider = document.getElementById('brandVolumeSlider');

    sceneryToggle.addEventListener('click', () => {
      const next = !document.body.classList.contains('scenery-mode');
      document.body.classList.toggle('scenery-mode', next);
      localStorage.setItem(STORAGE_KEYS.scenery, next ? 'on' : 'off');
      sceneryToggle.textContent = next ? 'Back to portal' : 'Enjoy the scenery';
      sceneryToggle.classList.toggle('active', next);
    });

    document.getElementById('brandVideoPrev').addEventListener('click', playPrevious);
    document.getElementById('brandVideoNext').addEventListener('click', playNext);

    audioToggle.addEventListener('click', () => {
      const nextOn = localStorage.getItem(STORAGE_KEYS.audio) !== 'on';
      localStorage.setItem(STORAGE_KEYS.audio, nextOn ? 'on' : 'off');
      setVideoAudioState(activeVideo);
      if (activeVideo) activeVideo.play().catch(() => {});
      updateControls();
    });

    volumeSlider.value = String(getVolume());
    volumeSlider.addEventListener('input', () => {
      const value = Number(volumeSlider.value);
      localStorage.setItem(STORAGE_KEYS.volume, String(value));
      if (activeVideo) activeVideo.volume = value;
    });

    if (localStorage.getItem(STORAGE_KEYS.scenery) === 'on') {
      document.body.classList.add('scenery-mode');
    }

    updateControls();
  }

  function updateControls() {
    const sceneryToggle = document.getElementById('brandSceneryToggle');
    const audioToggle = document.getElementById('brandAudioToggle');
    const volumeSlider = document.getElementById('brandVolumeSlider');
    if (sceneryToggle) {
      const sceneryOn = document.body.classList.contains('scenery-mode');
      sceneryToggle.textContent = sceneryOn ? 'Back to portal' : 'Enjoy the scenery';
      sceneryToggle.classList.toggle('active', sceneryOn);
    }
    if (audioToggle) {
      const audioOn = localStorage.getItem(STORAGE_KEYS.audio) === 'on';
      audioToggle.textContent = audioOn ? 'Audio on' : 'Audio off';
      audioToggle.classList.toggle('active', audioOn);
    }
    if (volumeSlider) volumeSlider.value = String(getVolume());
  }

  function updateStatus(src) {
    const status = document.getElementById('brandVideoStatus');
    if (!status || !src) return;
    const name = src.split('/').pop();
    status.textContent = name || 'Video playing';
  }

  async function init() {
    if (!document.body || prefersReducedMotion()) return;

    const manifest = await fetchManifest();
    if (!manifest || !manifest.brands) return;

    activeSettings = manifest.settings || {};
    activeSettings.loopPlaylist = activeSettings.loopPlaylist !== false;
    if (activeSettings.mobileVideo === false && isMobileWidth()) {
      createControls();
      return;
    }

    const brandKey = getBrandKey();
    activePlaylist = buildPlaylist(manifest.brands[brandKey]);
    if (!activePlaylist.length) {
      createControls();
      return;
    }

    activeVideo = await waitForVideo();
    if (!activeVideo) {
      createControls();
      return;
    }

    activeQueue = activeSettings.mode === 'random' ? shuffle(activePlaylist) : activePlaylist.slice();
    activeIndex = 0;

    activeVideo.addEventListener('ended', () => {
      if (!activeSettings.loopPlaylist && activeIndex >= activeQueue.length - 1) return;
      playNext();
    });

    activeVideo.addEventListener('error', () => {
      if (activeQueue.length > 1) playNext();
      else activeVideo.style.display = 'none';
    });

    createControls();
    playCurrent();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
