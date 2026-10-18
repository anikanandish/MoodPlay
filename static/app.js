// MoodPlay Frontend Application Logic

let currentAudio = null;
let currentAudioBtn = null;

document.addEventListener('DOMContentLoaded', () => {
  initStatus();
  initHistory();
  setupEventListeners();
});

// Check Ollama & Spotify health
async function initStatus() {
  const ollamaPill = document.getElementById('ollamaPill');
  const spotifyPill = document.getElementById('spotifyPill');

  try {
    const res = await fetch('/api/status');
    const data = await res.json();

    if (data.ollama && data.ollama.online) {
      ollamaPill.querySelector('.status-dot').classList.remove('offline');
      ollamaPill.querySelector('.status-text').textContent = 'Ollama (Gemma 3) Online';
    } else {
      ollamaPill.querySelector('.status-dot').classList.add('offline');
      ollamaPill.querySelector('.status-text').textContent = 'Ollama Connecting...';
    }

    if (data.spotify && data.spotify.configured) {
      spotifyPill.querySelector('.status-dot').classList.remove('offline');
      spotifyPill.querySelector('.status-text').textContent = 'Spotify API Active';
    } else {
      spotifyPill.querySelector('.status-dot').classList.add('offline');
      spotifyPill.querySelector('.status-text').textContent = 'Spotify Web Mode';
    }
  } catch (err) {
    console.warn('Status check warning:', err);
  }
}

// Fetch recent mood history
async function initHistory() {
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
          triggerCurate(mood);
        });
        container.appendChild(chip);
      });
    }
  } catch (err) {
    console.warn('History fetch error:', err);
  }
}

function setupEventListeners() {
  const form = document.getElementById('moodForm');
  const input = document.getElementById('moodInput');

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const mood = input.value.trim();
    if (mood) {
      triggerCurate(mood);
    }
  });

  // Preset chips click handler
  document.querySelectorAll('.preset-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const vibe = chip.getAttribute('data-vibe');
      input.value = vibe;
      triggerCurate(vibe);
    });
  });
}

// Trigger Curate Request
async function triggerCurate(mood) {
  const submitBtn = document.getElementById('submitBtn');
  const mainVinyl = document.getElementById('mainVinyl');
  const toneArm = document.getElementById('toneArm');
  const loadingState = document.getElementById('loadingState');
  const resultsSection = document.getElementById('resultsSection');

  // Start visual turntable animation
  mainVinyl.classList.add('spinning');
  toneArm.classList.add('playing');
  submitBtn.disabled = true;

  // Show loading state
  loadingState.style.display = 'block';
  resultsSection.style.display = 'none';
  loadingState.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

  // Rotate fun loader messages
  const titles = [
    'Gemma 3 is analyzing acoustic textures...',
    'Matching emotional frequencies to artists...',
    'Spinning local neural weights on Ollama...',
    'Curating your high-fidelity tracklist...'
  ];
  let msgIdx = 0;
  const interval = setInterval(() => {
    msgIdx = (msgIdx + 1) % titles.length;
    const titleEl = document.getElementById('loaderTitle');
    if (titleEl) titleEl.textContent = titles[msgIdx];
  }, 2500);

  try {
    const res = await fetch('/api/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mood: mood, count: 5 })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to curate playlist');
    }

    const data = await res.json();
    renderResults(data);
    initHistory(); // Refresh history
  } catch (err) {
    alert(`Could not generate playlist: ${err.message}`);
  } finally {
    clearInterval(interval);
    loadingState.style.display = 'none';
    submitBtn.disabled = false;
  }
}

// Render Tracks & Vibe Summary
function renderResults(data) {
  const resultsSection = document.getElementById('resultsSection');
  const vibeTitle = document.getElementById('vibeTitle');
  const vibeAnalysis = document.getElementById('vibeAnalysis');
  const trackCount = document.getElementById('trackCount');
  const tracksGrid = document.getElementById('tracksGrid');

  vibeTitle.textContent = data.vibe_headline || `Vibe: ${data.mood}`;
  vibeAnalysis.textContent = data.vibe_analysis || 'Gemma 3 tailored this acoustic journey for your mood.';
  trackCount.textContent = `${data.tracks.length} Tracks`;

  tracksGrid.innerHTML = '';

  data.tracks.forEach((track, index) => {
    const card = document.createElement('div');
    card.className = 'song-card';
    card.style.animationDelay = `${index * 0.08}s`;

    // Album art or vinyl fallback
    let artHtml = '';
    if (track.image_url) {
      artHtml = `
        <div class="album-art-container">
          <img src="${track.image_url}" alt="${track.title}" class="album-cover" loading="lazy">
          <div class="vinyl-peek"></div>
        </div>
      `;
    } else {
      artHtml = `
        <div class="album-art-container">
          <div class="vinyl-fallback-art">💿</div>
          <div class="vinyl-peek"></div>
        </div>
      `;
    }

    // Audio preview button if available
    let previewHtml = '';
    if (track.preview_url) {
      previewHtml = `
        <button class="preview-audio-btn" title="Play 30s Preview" onclick="toggleAudioPreview(this, '${track.preview_url}')">
          ▶
        </button>
      `;
    }

    card.innerHTML = `
      ${artHtml}
      <div class="song-details">
        <div class="song-title-row">
          <h4 class="song-title">${escapeHtml(track.title)}</h4>
        </div>
        <p class="song-artist">${escapeHtml(track.artist)} • <span style="color: #64748b">${escapeHtml(track.album || '')}</span></p>
        <p class="song-reason">💡 ${escapeHtml(track.reason || '')}</p>
      </div>
      <div class="song-actions">
        ${previewHtml}
        <a href="${track.spotify_url}" target="_blank" rel="noopener noreferrer" class="spotify-play-btn">
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
