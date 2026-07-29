// Snowfall
const canvas = document.getElementById('snow');
const ctx = canvas.getContext('2d');

let W, H, flakes;

function resize() {
  W = canvas.width  = window.innerWidth;
  H = canvas.height = window.innerHeight;
}

function mkFlake() {
  return {
    x: Math.random() * W,
    y: Math.random() * H,
    r: Math.random() * 2.5 + 0.5,
    d: Math.random() * 0.6 + 0.2,
    drift: (Math.random() - 0.5) * 0.3,
  };
}

function initFlakes() {
  flakes = Array.from({ length: 140 }, mkFlake);
}

function drawSnow() {
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = 'rgba(220, 240, 255, 0.85)';
  flakes.forEach(f => {
    ctx.beginPath();
    ctx.arc(f.x, f.y, f.r, 0, Math.PI * 2);
    ctx.fill();
  });
}

function updateSnow() {
  flakes.forEach(f => {
    f.y += f.d;
    f.x += f.drift;
    if (f.y > H + 4) { f.y = -4; f.x = Math.random() * W; }
    if (f.x > W + 4) { f.x = -4; }
    if (f.x < -4)    { f.x = W + 4; }
  });
}

function tick() {
  drawSnow();
  updateSnow();
  requestAnimationFrame(tick);
}

resize();
initFlakes();
tick();
window.addEventListener('resize', () => { resize(); initFlakes(); });

// Smooth scroll offset for fixed header
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (!target) return;
    e.preventDefault();
    const top = target.getBoundingClientRect().top + window.scrollY - 72;
    window.scrollTo({ top, behavior: 'smooth' });
  });
});
