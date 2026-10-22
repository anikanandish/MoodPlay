// MoodPlay — Audiophile Companion Frontend Logic

let currentAudio = null;
let currentAudioBtn = null;
let currentRpm = 33;
let isCued = false;

// Web Audio API Vinyl Crackle Simulator
let audioCtx = null;
let crackleNode = null;
let crackleGain = null;
let isCracklePlaying = false;

document.addEventListener('DOMContentLoaded', () => {
  initSystemStatus();
  initListeningHistory();
  setupDeckControls();
  setupCrateChips();
  setupForm();
});

// System Status Check
async function initSystemStatus() {
  const engineLabel = document.getElementById('engineLabel');
  const spotifyLabel = document.getElementById('spotifyLabel');

  try {
    const res = await fetch('/api/status');
    const data = await res.json();

    if (data.ollama && data.ollama.online) {
      engineLabel.textContent = 'Gemma 3 Analog Engine';
    } else {
      engineLabel.textContent = 'Acoustic Vault Active';
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

  // Vinyl Crackle Noise Toggle (Web Audio API)
  crackleToggle.addEventListener('click', () => {
    toggleVinylCrackle(crackleToggle);
  });

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
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!audioCtx) audioCtx = new AudioContext();
    if (audioCtx.state === 'suspended') audioCtx.resume();

    // Create a buffer with soft vinyl noise and periodic microscopic pops
    const bufferSize = audioCtx.sampleRate * 2;
    const noiseBuffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
    const output = noiseBuffer.getChannelData(0);

    for (let i = 0; i < bufferSize; i++) {
      let white = Math.random() * 2 - 1;
      let crackle = 0;
      if (Math.random() < 0.0012) {
        crackle = (Math.random() * 2 - 1) * 0.45;
      }
      output[i] = white * 0.015 + crackle;
    }

    crackleNode = audioCtx.createBufferSource();
    crackleNode.buffer = noiseBuffer;
    crackleNode.loop = true;

    // Filter to warm analog low-pass
    const filter = audioCtx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = 1800;

    crackleGain = audioCtx.createGain();
    crackleGain.gain.setValueAtTime(0.001, audioCtx.currentTime);
    crackleGain.gain.exponentialRampToValueAtTime(0.28, audioCtx.currentTime + 0.5);

    crackleNode.connect(filter);
    filter.connect(crackleGain);
    crackleGain.connect(audioCtx.destination);

    crackleNode.start(0);
    isCracklePlaying = true;
    btn.classList.add('active');
    btn.querySelector('.toggle-text').textContent = 'ON';
  } catch (e) {
    console.warn('Web Audio not allowed or failed:', e);
  }
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

  // Rotating atmospheric cue messages
  const titles = [
    'Selecting master recordings from the archive...',
    'Tuning tube saturation and acoustic resonance...',
    'Reviewing warm vinyl liner notes...',
    'Dropping needle onto curated grooves...'
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
    document.getElementById('vibeTitle').textContent = 'Archive Curations';
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

  vibeTitle.textContent = data.vibe_headline || `Selection for: ${data.mood}`;
  vibeAnalysis.textContent = data.vibe_analysis || 'Curated with unhurried analog warmth and genuine acoustic presence.';
  trackCount.textContent = `${data.tracks.length} Master Cuts`;

  tracksGrid.innerHTML = '';

  data.tracks.forEach((track, index) => {
    const card = document.createElement('div');
    card.className = 'sleeve-card';
    card.style.animationDelay = `${index * 0.08}s`;

    // Texture tags
    const textures = track.textures || ['Analog Warmth', 'Acoustic Resonance', 'Vinyl Texture'];
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
            <span class="fallback-glyph">◈</span>
            <span class="fallback-sub">VINYL</span>
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
          <span class="track-album">• ${escapeHtml(track.album || 'Master Recording')}</span>
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
