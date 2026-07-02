/* Pleiades brand video playlist controller
   Static GitHub Pages cannot automatically list a folder, so this uses:
   /assets/video/brand-playlists.json
*/
(function () {
  'use strict';

  const MANIFEST_PATH = '/Pleiades/assets/video/brand-playlists.json';

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

  function setVideoSource(video, src) {
    if (!video || !src) return;
    video.pause();
    video.removeAttribute('loop');
    video.innerHTML = '';
    const source = document.createElement('source');
    source.src = src;
    source.type = 'video/mp4';
    video.appendChild(source);
    video.load();
    const playAttempt = video.play();
    if (playAttempt && typeof playAttempt.catch === 'function') playAttempt.catch(() => {});
  }

  async function init() {
    if (!document.body || prefersReducedMotion()) return;

    const manifest = await fetchManifest();
    if (!manifest || !manifest.brands) return;

    const settings = manifest.settings || {};
    if (settings.mobileVideo === false && isMobileWidth()) return;

    const brandKey = getBrandKey();
    const playlist = buildPlaylist(manifest.brands[brandKey]);
    if (!playlist.length) return;

    const video = await waitForVideo();
    if (!video) return;

    let queue = settings.mode === 'random' ? shuffle(playlist) : playlist.slice();
    let index = 0;

    function playCurrent() {
      if (!queue.length) return;
      setVideoSource(video, queue[index]);
    }

    video.addEventListener('ended', () => {
      if (!settings.loopPlaylist && index >= queue.length - 1) return;
      index += 1;
      if (index >= queue.length) {
        index = 0;
        if (settings.mode === 'random') queue = shuffle(playlist);
      }
      playCurrent();
    });

    video.addEventListener('error', () => {
      index += 1;
      if (index >= queue.length) index = 0;
      if (queue.length > 1) playCurrent();
      else video.style.display = 'none';
    });

    playCurrent();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
