// MoodPlay — Yuletide Holiday Edition Frontend Logic

let currentAudio = null;
let currentAudioBtn = null;
let currentRpm = 33;
let isCued = false;

// Web Audio API Analog Simulator
let audioCtx = null;

// Vinyl Crackle State
let crackleNode = null;
let crackleGain = null;
let isCracklePlaying = false;

// Hearth / Fireplace Crackle State
let hearthSource = null;
let hearthFilter = null;
let hearthGain = null;
let isHearthPlaying = false;
let hearthPopInterval = null;

// Canvas Snowfall State
let snowCanvas = null;
let snowCtx = null;
let snowflakes = [];
let isSnowing = true;
let snowAnimId = null;

document.addEventListener('DOMContentLoaded', () => {
  initSystemStatus();
  initListeningHistory();
  setupDeckControls();
  setupCrateChips();
  setupForm();
  initSnowfall();
});

// System Status Check
async function initSystemStatus() {
  const engineLabel = document.getElementById('engineLabel');
  const spotifyLabel = document.getElementById('spotifyLabel');

  try {
    const res = await fetch('/api/status');
    const data = await res.json();

    if (data.ollama && data.ollama.online) {
      engineLabel.textContent = 'Gemma 3 Yuletide Engine';
    } else {
      engineLabel.textContent = 'Holiday Vault Active';
    }

    if (data.spotify && data.spotify.configured) {
      spotifyLabel.textContent = 'Spotify API Connected';
    } else {
      spotifyLabel.textContent = 'Direct Stream Links';
    }
  } catch (err) {
    console.warn('Status check warning:', err);
  }
}

// Listening History
async function initListeningHistory() {
  const container = document.getElementById('historyChips');
  try {
    const res = await fetch('/api/history');
    const data = await res.json();
    if (data.history && data.history.length > 0) {
      container.innerHTML = '';
      data.history.forEach(mood => {
        const chip = document.createElement('button');
        chip.className = 'history-chip';
        chip.textContent = mood;
        chip.addEventListener('click', () => {
          document.getElementById('moodInput').value = mood;
          triggerCuration(mood);
        });
        container.appendChild(chip);
      });
    }
  } catch (err) {
    console.warn('History fetch error:', err);
  }
}

// Setup Hardware Deck Controls
function setupDeckControls() {
  const rpmToggle = document.getElementById('rpmToggle');
  const crackleToggle = document.getElementById('crackleToggle');
  const hearthToggle = document.getElementById('hearthToggle');
  const snowToggle = document.getElementById('snowToggle');
  const cueLever = document.getElementById('cueLever');
  const mainPlatter = document.getElementById('mainPlatter');
  const tonearmAssembly = document.getElementById('tonearmAssembly');

  // RPM Switch: 33 1/3 vs 45
  rpmToggle.addEventListener('click', () => {
    if (currentRpm === 33) {
      currentRpm = 45;
      rpmToggle.querySelector('.toggle-text').textContent = '45';
      document.getElementById('rpmDisplay').textContent = '45 RPM';
      rpmToggle.classList.add('active');
    } else {
      currentRpm = 33;
      rpmToggle.querySelector('.toggle-text').textContent = '33⅓';
      document.getElementById('rpmDisplay').textContent = '33⅓ RPM';
      rpmToggle.classList.remove('active');
    }

    if (isCued) {
      mainPlatter.className = `vinyl-disc spinning-${currentRpm}`;
    }
  });

  // Vinyl Crackle Noise Toggle
  crackleToggle.addEventListener('click', () => {
    toggleVinylCrackle(crackleToggle);
  });

  // Fireside Hearth Crackle Toggle
  if (hearthToggle) {
    hearthToggle.addEventListener('click', () => {
      toggleHearthAudio(hearthToggle);
    });
  }

  // Snowfall Toggle
  if (snowToggle) {
    snowToggle.addEventListener('click', () => {
      isSnowing = !isSnowing;
      if (isSnowing) {
        snowToggle.classList.add('active');
        snowToggle.querySelector('.toggle-text').textContent = 'ON';
        if (snowCanvas) snowCanvas.classList.remove('disabled');
      } else {
        snowToggle.classList.remove('active');
        snowToggle.querySelector('.toggle-text').textContent = 'OFF';
        if (snowCanvas) snowCanvas.classList.add('disabled');
      }
    });
  }

  // Cue Lever Drop/Lift
  cueLever.addEventListener('click', () => {
    toggleCue();
  });

  // Clicking platter directly also toggles cue
  mainPlatter.addEventListener('click', () => {
    toggleCue();
  });
}

function toggleCue() {
  const mainPlatter = document.getElementById('mainPlatter');
  const tonearmAssembly = document.getElementById('tonearmAssembly');
  const cueLever = document.getElementById('cueLever');

  isCued = !isCued;
  if (isCued) {
    mainPlatter.className = `vinyl-disc spinning-${currentRpm}`;
    tonearmAssembly.classList.add('cued');
    cueLever.textContent = 'LIFT ⏸';
    cueLever.style.borderColor = 'var(--lavender-mist)';
  } else {
    mainPlatter.className = 'vinyl-disc';
    tonearmAssembly.classList.remove('cued');
    cueLever.textContent = 'DROP ▶';
    cueLever.style.borderColor = 'var(--silver-mid)';
  }
}

// Web Audio Context Helper
function getOrCreateAudioContext() {
  if (!audioCtx) {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    audioCtx = new AudioContext();
  }
  if (audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
  return audioCtx;
}

// Web Audio API Analog Vinyl Crackle Generator
function toggleVinylCrackle(btn) {
  if (isCracklePlaying) {
    if (crackleGain && audioCtx) {
      crackleGain.gain.setValueAtTime(crackleGain.gain.value, audioCtx.currentTime);
      crackleGain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.3);
      setTimeout(() => {
        if (crackleNode) crackleNode.disconnect();
      }, 350);
    }
    isCracklePlaying = false;
    btn.classList.remove('active');
    btn.querySelector('.toggle-text').textContent = 'OFF';
    return;
  }

  try {
    const ctx = getOrCreateAudioContext();

    const bufferSize = ctx.sampleRate * 2;
    const noiseBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const output = noiseBuffer.getChannelData(0);

    for (let i = 0; i < bufferSize; i++) {
      let white = Math.random() * 2 - 1;
      let crackle = 0;
      if (Math.random() < 0.0012) {
        crackle = (Math.random() * 2 - 1) * 0.45;
      }
      output[i] = white * 0.015 + crackle;
    }

    crackleNode = ctx.createBufferSource();
    crackleNode.buffer = noiseBuffer;
    crackleNode.loop = true;

    const filter = ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = 1800;

    crackleGain = ctx.createGain();
    crackleGain.gain.setValueAtTime(0.001, ctx.currentTime);
    crackleGain.gain.exponentialRampToValueAtTime(0.28, ctx.currentTime + 0.5);

    crackleNode.connect(filter);
    filter.connect(crackleGain);
    crackleGain.connect(ctx.destination);

    crackleNode.start(0);
    isCracklePlaying = true;
    btn.classList.add('active');
    btn.querySelector('.toggle-text').textContent = 'ON';
  } catch (e) {
    console.warn('Web Audio crackle failed:', e);
  }
}

// Web Audio API Fireside Hearth & Wood Crackle Synthesizer
function toggleHearthAudio(btn) {
  if (isHearthPlaying) {
    if (hearthGain && audioCtx) {
      hearthGain.gain.setValueAtTime(hearthGain.gain.value, audioCtx.currentTime);
      hearthGain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.4);
      setTimeout(() => {
        if (hearthSource) hearthSource.disconnect();
        clearInterval(hearthPopInterval);
      }, 450);
    }
    isHearthPlaying = false;
    btn.classList.remove('active');
    btn.querySelector('.toggle-text').textContent = 'OFF';
    return;
  }

  try {
    const ctx = getOrCreateAudioContext();

    // 1. Warm rumble of a living fireplace (brown noise)
    const bufferSize = ctx.sampleRate * 3;
    const noiseBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const data = noiseBuffer.getChannelData(0);
    let lastOut = 0.0;

    for (let i = 0; i < bufferSize; i++) {
      let white = Math.random() * 2 - 1;
      // Brown noise integration
      lastOut = (lastOut + (0.02 * white)) / 1.02;
      data[i] = lastOut * 3.5;
    }

    hearthSource = ctx.createBufferSource();
    hearthSource.buffer = noiseBuffer;
    hearthSource.loop = true;

    // Warm hearth lowpass
    hearthFilter = ctx.createBiquadFilter();
    hearthFilter.type = 'lowpass';
    hearthFilter.frequency.value = 450;
    hearthFilter.Q.value = 1.2;

    hearthGain = ctx.createGain();
    hearthGain.gain.setValueAtTime(0.001, ctx.currentTime);
    hearthGain.gain.exponentialRampToValueAtTime(0.25, ctx.currentTime + 0.6);

    hearthSource.connect(hearthFilter);
    hearthFilter.connect(hearthGain);
    hearthGain.connect(ctx.destination);

    hearthSource.start(0);

    // 2. Periodic natural wood snap/pop bursts
    hearthPopInterval = setInterval(() => {
      if (!isHearthPlaying || !audioCtx) return;
      if (Math.random() < 0.65) {
        triggerHearthPop(ctx);
      }
    }, 400);

    isHearthPlaying = true;
    btn.classList.add('active');
    btn.querySelector('.toggle-text').textContent = 'ON';
  } catch (e) {
    console.warn('Web Audio hearth failed:', e);
  }
}

// Single wood ember snap/pop sound
function triggerHearthPop(ctx) {
  try {
    const popOsc = ctx.createOscillator();
    const popGain = ctx.createGain();
    const popFilter = ctx.createBiquadFilter();

    popFilter.type = 'bandpass';
    popFilter.frequency.value = 600 + Math.random() * 900;
    popFilter.Q.value = 3.0;

    const startFreq = 250 + Math.random() * 400;
    popOsc.frequency.setValueAtTime(startFreq, ctx.currentTime);
    popOsc.frequency.exponentialRampToValueAtTime(50, ctx.currentTime + 0.04);

    const amp = 0.08 + Math.random() * 0.12;
    popGain.gain.setValueAtTime(amp, ctx.currentTime);
    popGain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.05);

    popOsc.connect(popFilter);
    popFilter.connect(popGain);
    popGain.connect(ctx.destination);

    popOsc.start(ctx.currentTime);
    popOsc.stop(ctx.currentTime + 0.06);
  } catch (err) {
    // Graceful fallback
  }
}

// Ambient Snowfall Simulation
function initSnowfall() {
  snowCanvas = document.getElementById('snowCanvas');
  if (!snowCanvas) return;
  snowCtx = snowCanvas.getContext('2d');

  function resize() {
    snowCanvas.width = window.innerWidth;
    snowCanvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resize);
  resize();

  // Create gentle snowflakes
  const flakeCount = Math.min(window.innerWidth < 768 ? 40 : 75, 90);
  snowflakes = [];
  for (let i = 0; i < flakeCount; i++) {
    snowflakes.push({
      x: Math.random() * snowCanvas.width,
      y: Math.random() * snowCanvas.height,
      radius: Math.random() * 2.2 + 0.8,
      density: Math.random() * flakeCount,
      speedY: Math.random() * 0.8 + 0.4,
      speedX: Math.random() * 0.6 - 0.3,
      opacity: Math.random() * 0.5 + 0.25,
      swayStep: Math.random() * Math.PI * 2
    });
  }

  function renderSnow() {
    if (!snowCtx) return;
    snowCtx.clearRect(0, 0, snowCanvas.width, snowCanvas.height);

    if (isSnowing) {
      snowCtx.fillStyle = '#ffffff';
      for (let i = 0; i < snowflakes.length; i++) {
        const f = snowflakes[i];
        f.swayStep += 0.015;
        f.x += Math.sin(f.swayStep) * 0.6 + f.speedX;
        f.y += f.speedY;

        // Wrap around boundaries
        if (f.y > snowCanvas.height) {
          f.y = -10;
          f.x = Math.random() * snowCanvas.width;
        }
        if (f.x > snowCanvas.width) f.x = 0;
        if (f.x < 0) f.x = snowCanvas.width;

        snowCtx.beginPath();
        snowCtx.arc(f.x, f.y, f.radius, 0, Math.PI * 2);
        snowCtx.fillStyle = `rgba(240, 244, 255, ${f.opacity})`;
        snowCtx.fill();
      }
    }
    snowAnimId = requestAnimationFrame(renderSnow);
  }
  renderSnow();
}

// Curated Crate Chips
function setupCrateChips() {
  document.querySelectorAll('.crate-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const vibe = chip.getAttribute('data-vibe');
      document.getElementById('moodInput').value = vibe;
      triggerCuration(vibe);
    });
  });
}

// Form Submission
function setupForm() {
  const form = document.getElementById('moodForm');
  const input = document.getElementById('moodInput');

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const mood = input.value.trim();
    if (mood) {
      triggerCuration(mood);
    }
  });
}

// Curation Request & Needle Drop Execution
async function triggerCuration(mood) {
  const submitBtn = document.getElementById('submitBtn');
  const mainPlatter = document.getElementById('mainPlatter');
  const tonearmAssembly = document.getElementById('tonearmAssembly');
  const cueLever = document.getElementById('cueLever');
  const loadingState = document.getElementById('loadingState');
  const resultsSection = document.getElementById('resultsSection');

  // Trigger Platter & Tonearm Drop
  isCued = true;
  mainPlatter.className = `vinyl-disc spinning-${currentRpm}`;
  tonearmAssembly.classList.add('cued');
  cueLever.textContent = 'LIFT ⏸';
  cueLever.style.borderColor = 'var(--lavender-mist)';
  submitBtn.disabled = true;

  // Show Analog Meter Loading
  loadingState.style.display = 'block';
  resultsSection.style.display = 'none';
  loadingState.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

  // Rotating atmospheric holiday cue messages
  const titles = [
    'Selecting holiday masters from the archive...',
    'Tuning tube saturation and fireside resonance...',
    'Unpacking vintage yuletide vinyl sleeves...',
    'Dropping stylus onto winter grooves...'
  ];
  let msgIdx = 0;
  const interval = setInterval(() => {
    msgIdx = (msgIdx + 1) % titles.length;
    const titleEl = document.getElementById('loaderTitle');
    if (titleEl) titleEl.textContent = titles[msgIdx];
  }, 2400);

  try {
    const res = await fetch('/api/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mood: mood, count: 5 })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to curate selection');
    }

    const data = await res.json();
    renderSelectionResults(data);
    initListeningHistory();
  } catch (err) {
    console.warn("Curation Notice:", err);
    resultsSection.style.display = 'block';
    document.getElementById('vibeTitle').textContent = 'Yuletide Archive Curations';
    document.getElementById('vibeAnalysis').textContent = `Using offline acoustic vault: ${err.message}`;
  } finally {
    clearInterval(interval);
    loadingState.style.display = 'none';
    submitBtn.disabled = false;
  }
}

// Render Results with Sliding Vinyl Record Sleeves
function renderSelectionResults(data) {
  const resultsSection = document.getElementById('resultsSection');
  const vibeTitle = document.getElementById('vibeTitle');
  const vibeAnalysis = document.getElementById('vibeAnalysis');
  const trackCount = document.getElementById('trackCount');
  const tracksGrid = document.getElementById('tracksGrid');

  vibeTitle.textContent = data.vibe_headline || `Yuletide Selection for: ${data.mood}`;
  vibeAnalysis.textContent = data.vibe_analysis || 'Curated with unhurried analog warmth, holiday cheer, and acoustic presence.';
  trackCount.textContent = `${data.tracks.length} Master Cuts`;

  tracksGrid.innerHTML = '';

  data.tracks.forEach((track, index) => {
    const card = document.createElement('div');
    card.className = 'sleeve-card';
    card.style.animationDelay = `${index * 0.08}s`;

    // Texture tags
    const textures = track.textures || ['Holiday Jazz', 'Analog Warmth', 'Winter Vinyl'];
    const tagsHtml = textures.map(t => `<span class="texture-pill">${escapeHtml(t)}</span>`).join('');

    // Album art or physical sleeve fallback
    let artHtml = '';
    if (track.image_url) {
      artHtml = `
        <div class="art-pocket">
          <img src="${track.image_url}" alt="${track.title}" class="jacket-cover" loading="lazy">
          <div class="sliding-vinyl">
            <div class="sliding-label"></div>
          </div>
        </div>
      `;
    } else {
      artHtml = `
        <div class="art-pocket">
          <div class="sleeve-fallback-cover">
            <span class="fallback-glyph">❄</span>
            <span class="fallback-sub">YULETIDE</span>
          </div>
          <div class="sliding-vinyl">
            <div class="sliding-label"></div>
          </div>
        </div>
      `;
    }

    // Audio preview button
    let previewHtml = '';
    if (track.preview_url) {
      previewHtml = `
        <button class="preview-listen-btn" title="Listen to 30s master preview" onclick="toggleAudioPreview(this, '${track.preview_url}')">
          ▶
        </button>
      `;
    }

    card.innerHTML = `
      ${artHtml}
      <div class="sleeve-meta">
        <div class="sleeve-title-row">
          <h4 class="track-heading">${escapeHtml(track.title)}</h4>
          <span class="track-artist">${escapeHtml(track.artist)}</span>
          <span class="track-album">• ${escapeHtml(track.album || 'Holiday Master Recording')}</span>
        </div>
        <div class="texture-tags">
          ${tagsHtml}
        </div>
        <p class="curator-note">◈ ${escapeHtml(track.reason || '')}</p>
      </div>
      <div class="sleeve-actions">
        ${previewHtml}
        <a href="${track.spotify_url}" target="_blank" rel="noopener noreferrer" class="spotify-action-btn">
          <span>Spotify</span>
          <span>↗</span>
        </a>
      </div>
    `;

    tracksGrid.appendChild(card);
  });

  resultsSection.style.display = 'block';
  resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// 30s Audio Preview Controller
function toggleAudioPreview(btn, url) {
  if (currentAudio && !currentAudio.paused && currentAudio.src === url) {
    currentAudio.pause();
    btn.textContent = '▶';
    return;
  }

  if (currentAudio) {
    currentAudio.pause();
    if (currentAudioBtn) currentAudioBtn.textContent = '▶';
  }

  currentAudio = new Audio(url);
  currentAudioBtn = btn;
  btn.textContent = '⏸';

  currentAudio.play();
  currentAudio.onended = () => {
    btn.textContent = '▶';
  };
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
}
