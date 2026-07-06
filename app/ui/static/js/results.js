const analysisId = document.body.dataset.analysisId;
const scoreValue = document.getElementById('scoreValue');
const scoreCircle = document.getElementById('scoreCircle');
const summaryText = document.getElementById('summaryText');
const matchedSkills = document.getElementById('matchedSkills');
const missingSkills = document.getElementById('missingSkills');
const recommendationsList = document.getElementById('recommendationsList');
const strengthsList = document.getElementById('strengthsList');
const explanations = document.getElementById('explanations');
const matchedBar = document.getElementById('matchedBar');
const missingBar = document.getElementById('missingBar');

// Defensive reset: remove any stale inline style from previously cached scripts
if (scoreCircle) {
  scoreCircle.style.background = 'none';
}

// SVG icons (inline, visual only)
const ICON_CHECK = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`;
const ICON_X     = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`;
const ICON_DOT_V = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>`;
const ICON_STAR  = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>`;
const ICON_ALERT = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`;

function chip(label, kind) {
  const icon = kind === 'good' ? ICON_CHECK : kind === 'bad' ? ICON_X : '';
  return `<span class="chip ${kind}">${icon}${label}</span>`;
}

function listItem(text, bulletClass, icon) {
  return `<li><span class="list-bullet ${bulletClass}">${icon}</span>${text}</li>`;
}

function explanationCard(skill, reason) {
  return `<article class="explanation">
    <div class="explanation-skill">${ICON_ALERT}${skill}</div>
    <p class="explanation-reason">${reason}</p>
  </article>`;
}

function animateScore(target) {
  const start = performance.now();
  const duration = 1200;
  function frame(now) {
    const p = Math.min((now - start) / duration, 1);
    const current = Math.round(target * p);
    scoreValue.textContent = String(current);
    if (p < 1) requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}

function setCircle(score) {
  // Drive the SVG stroke-dashoffset animation
  const fill = scoreCircle ? scoreCircle.querySelector('.fill') : null;
  if (fill) {
    const pct = Math.max(0, Math.min(100, score)) / 100;
    const circumference = fill.getTotalLength();

    // Ensure dash metrics are always synced with real SVG geometry
    fill.style.strokeDasharray = `${circumference} ${circumference}`;
    fill.style.strokeDashoffset = `${circumference}`;

    // Force layout so the browser applies the initial state before transition
    fill.getBoundingClientRect();

    fill.style.strokeDashoffset = String(Math.round(circumference * (1 - pct)));
  }

  // Score label
  const label = document.getElementById('scoreLabel');
  if (label) {
    let text, color;
    if (score >= 80)      { text = 'Excellent'; color = '#34d399'; }
    else if (score >= 60) { text = 'Good';      color = '#67e8f9'; }
    else if (score >= 40) { text = 'Fair';      color = '#fbbf24'; }
    else                  { text = 'Low';       color = '#fb7185'; }
    label.textContent = text;
    label.style.color = color;
    label.style.borderColor = color + '55';
  }
}

fetch(`/results/${analysisId}`)
  .then((r) => r.json().then((d) => ({ ok: r.ok, data: d })))
  .then(({ ok, data }) => {
    if (!ok) throw new Error(data.detail || 'Failed to load results');

    animateScore(data.score);
    setCircle(data.score);
    summaryText.textContent = data.summary || 'No summary.';

    const matched = data.matched_skills || [];
    const missing = data.missing_skills || [];

    // Skill chips
    matchedSkills.innerHTML = matched.length
      ? matched.map((x) => chip(x, 'good')).join('')
      : `<span class="chip-empty">No matched skills found.</span>`;
    missingSkills.innerHTML = missing.length
      ? missing.map((x) => chip(x, 'bad')).join('')
      : `<span class="chip-empty">All required skills matched!</span>`;

    // Counts in metric headers
    const matchedCountEl = document.getElementById('matchedCount');
    const missingCountEl = document.getElementById('missingCount');
    if (matchedCountEl) matchedCountEl.textContent = matched.length;
    if (missingCountEl) missingCountEl.textContent = missing.length;

    // Recommendations & Strengths with styled list items
    recommendationsList.innerHTML = (data.recommendations || [])
      .map((x) => listItem(x, 'violet', ICON_DOT_V))
      .join('') || listItem('No recommendations at this time.', 'violet', ICON_DOT_V);
    strengthsList.innerHTML = (data.strengths || [])
      .map((x) => listItem(x, 'amber', ICON_STAR))
      .join('') || listItem('No strengths listed.', 'amber', ICON_STAR);

    // Explainability cards
    explanations.innerHTML = (data.missing_skill_explanations || [])
      .map((x) => explanationCard(x.skill, x.reason))
      .join('') || '<p class="muted">No missing skill explanations.</p>';

    // Progress bars
    const requiredCount = matched.length + missing.length;
    const matchedPct = requiredCount ? Math.round((matched.length / requiredCount) * 100) : 0;
    const missingPct = requiredCount ? 100 - matchedPct : 0;
    matchedBar.style.width = `${matchedPct}%`;
    missingBar.style.width = `${missingPct}%`;
  })
  .catch((err) => {
    summaryText.textContent = err.message;
  });