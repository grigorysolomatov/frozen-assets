// ── Content ──
// Add a tab by appending here. `cards` may be a number (that many blank cards)
// or an array of { title, text } once real content exists.
const TABS = [
  { id: 'investments', label: 'Investments', cards: 6 },
];

// ── Rendering ──
const tabsEl = document.getElementById('tabs');
const gridEl = document.getElementById('card-grid');

function cardList(cards) {
  return typeof cards === 'number'
    ? Array.from({ length: cards }, () => null)
    : cards;
}

function renderCards(tab) {
  gridEl.innerHTML = '';
  cardList(tab.cards).forEach(card => {
    const el = document.createElement('article');
    el.className = 'card' + (card ? '' : ' card-blank');
    el.innerHTML = card
      ? `<div class="card-inner">
           <h3>${card.title}</h3>
           <p>${card.text}</p>
         </div>`
      : `<div class="card-inner"><span class="card-mark">❄</span></div>`;
    gridEl.appendChild(el);
  });
}

function selectTab(id) {
  const tab = TABS.find(t => t.id === id) || TABS[0];
  [...tabsEl.children].forEach(b => {
    const on = b.dataset.id === tab.id;
    b.classList.toggle('active', on);
    b.setAttribute('aria-selected', on);
  });
  renderCards(tab);
}

TABS.forEach(tab => {
  const b = document.createElement('button');
  b.className = 'tab';
  b.textContent = tab.label;
  b.dataset.id = tab.id;
  b.setAttribute('role', 'tab');
  b.addEventListener('click', () => selectTab(tab.id));
  tabsEl.appendChild(b);
});

selectTab(TABS[0].id);

// ── Snowfall ──
const canvas = document.getElementById('snow');
const ctx = canvas.getContext('2d');
let W, H, flakes;

function resize() {
  W = canvas.width  = window.innerWidth;
  H = canvas.height = window.innerHeight;
}

function initFlakes() {
  flakes = Array.from({ length: 140 }, () => ({
    x: Math.random() * W,
    y: Math.random() * H,
    r: Math.random() * 2.5 + 0.5,
    d: Math.random() * 0.6 + 0.2,
    drift: (Math.random() - 0.5) * 0.3,
  }));
}

function tick() {
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = 'rgba(220, 240, 255, 0.85)';
  flakes.forEach(f => {
    ctx.beginPath();
    ctx.arc(f.x, f.y, f.r, 0, Math.PI * 2);
    ctx.fill();

    f.y += f.d;
    f.x += f.drift;
    if (f.y > H + 4) { f.y = -4; f.x = Math.random() * W; }
    if (f.x > W + 4) { f.x = -4; }
    if (f.x < -4)    { f.x = W + 4; }
  });
  requestAnimationFrame(tick);
}

resize();
initFlakes();
tick();
window.addEventListener('resize', () => { resize(); initFlakes(); });
