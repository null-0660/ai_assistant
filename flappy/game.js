// Flappy Bird — v4: красивая графика, облака, анимация

const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');

const W = canvas.width;
const H = canvas.height;

const bird = { x: 80, y: H / 2, w: 34, h: 24, vy: 0, rot: 0 };

const GRAVITY = 0.5;
const JUMP = -8;
const PIPE_W = 60;
const PIPE_GAP = 150;
const PIPE_SPEED = 2.5;

let pipes = [];
let clouds = [];
let frame = 0;
let score = 0;
let best = parseInt(localStorage.getItem('flappyBest') || '0');
let gameOver = false;
let groundOffset = 0;

const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

function beep(freq, duration) {
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.connect(gain);
  gain.connect(audioCtx.destination);
  osc.frequency.value = freq;
  gain.gain.value = 0.05;
  osc.start();
  osc.stop(audioCtx.currentTime + duration);
}

// Облака
function createClouds() {
  clouds = [];
  for (let i = 0; i < 5; i++) {
    clouds.push({
      x: Math.random() * W,
      y: 50 + Math.random() * 200,
      size: 30 + Math.random() * 40,
      speed: 0.3 + Math.random() * 0.5,
    });
  }
}

function resetGame() {
  bird.y = H / 2;
  bird.vy = 0;
  bird.rot = 0;
  pipes = [];
  frame = 0;
  score = 0;
  gameOver = false;
  createClouds();
}

function jump() {
  if (gameOver) { resetGame(); return; }
  bird.vy = JUMP;
  beep(600, 0.05);
}

document.addEventListener('keydown', (e) => {
  if (e.code === 'Space') { e.preventDefault(); jump(); }
});
canvas.addEventListener('click', jump);

function spawnPipe() {
  const minTop = 60;
  const maxTop = H - 40 - PIPE_GAP - 60;
  const topH = minTop + Math.random() * (maxTop - minTop);
  pipes.push({ x: W, topH, bottomY: topH + PIPE_GAP, scored: false });
}

function collides(px, py, pw, ph, rx, ry, rw, rh) {
  return px < rx + rw && px + pw > rx && py < ry + rh && py + ph > ry;
}

function update() {
  bird.vy += GRAVITY;
  bird.y += bird.vy;

  // Наклон
  bird.rot = Math.max(-0.5, Math.min(1.5, bird.vy * 0.08));

  if (bird.y - bird.h / 2 < 0) {
    bird.y = bird.h / 2;
    bird.vy = 0;
  }

  if (bird.y + bird.h / 2 > H - 40) {
    if (!gameOver) {
      beep(200, 0.3);
      if (score > best) { best = score; localStorage.setItem('flappyBest', best); }
    }
    gameOver = true;
  }

  // Облака
  for (let c of clouds) {
    c.x -= c.speed;
    if (c.x + c.size < 0) {
      c.x = W + c.size;
      c.y = 50 + Math.random() * 200;
    }
  }

  // Земля
  groundOffset = (groundOffset + PIPE_SPEED) % 40;

  frame++;
  if (frame % 90 === 0) spawnPipe();

  for (let p of pipes) {
    p.x -= PIPE_SPEED;

    const bx = bird.x - bird.w / 2;
    const by = bird.y - bird.h / 2;

    if (collides(bx, by, bird.w, bird.h, p.x, 0, PIPE_W, p.topH)) {
      if (!gameOver) beep(200, 0.3);
      gameOver = true;
    }
    if (collides(bx, by, bird.w, bird.h, p.x, p.bottomY, PIPE_W, H - p.bottomY)) {
      if (!gameOver) beep(200, 0.3);
      gameOver = true;
    }

    if (!p.scored && p.x + PIPE_W < bird.x) {
      p.scored = true;
      score++;
      beep(900, 0.1);
      if (score > best) { best = score; localStorage.setItem('flappyBest', best); }
    }
  }

  pipes = pipes.filter(p => p.x + PIPE_W > 0);
}

function drawCloud(c) {
  ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
  ctx.beginPath();
  ctx.arc(c.x, c.y, c.size * 0.6, 0, Math.PI * 2);
  ctx.arc(c.x + c.size * 0.5, c.y, c.size * 0.5, 0, Math.PI * 2);
  ctx.arc(c.x - c.size * 0.5, c.y, c.size * 0.5, 0, Math.PI * 2);
  ctx.arc(c.x + c.size * 0.2, c.y - c.size * 0.3, c.size * 0.4, 0, Math.PI * 2);
  ctx.fill();
}

function drawPipe(p) {
  // Тень
  ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
  ctx.fillRect(p.x + 4, 0, PIPE_W, p.topH);
  ctx.fillRect(p.x + 4, p.bottomY, PIPE_W, H - p.bottomY);

  // Верхняя
  ctx.fillStyle = '#73bf2e';
  ctx.fillRect(p.x, 0, PIPE_W, p.topH);
  ctx.fillStyle = '#5a9e1f';
  ctx.fillRect(p.x - 4, p.topH - 20, PIPE_W + 8, 20);
  ctx.strokeStyle = '#3d6b14';
  ctx.lineWidth = 2;
  ctx.strokeRect(p.x - 4, p.topH - 20, PIPE_W + 8, 20);

  // Блик
  ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
  ctx.fillRect(p.x + 4, 0, 8, p.topH - 20);

  // Нижняя
  ctx.fillStyle = '#73bf2e';
  ctx.fillRect(p.x, p.bottomY, PIPE_W, H - p.bottomY);
  ctx.fillStyle = '#5a9e1f';
  ctx.fillRect(p.x - 4, p.bottomY, PIPE_W + 8, 20);
  ctx.strokeStyle = '#3d6b14';
  ctx.strokeRect(p.x - 4, p.bottomY, PIPE_W + 8, 20);

  ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
  ctx.fillRect(p.x + 4, p.bottomY + 20, 8, H - p.bottomY - 20);
}

function drawBird() {
  ctx.save();
  ctx.translate(bird.x, bird.y);
  ctx.rotate(bird.rot);

  // Тень
  ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
  ctx.beginPath();
  ctx.ellipse(2, 2, bird.w / 2, bird.h / 2, 0, 0, Math.PI * 2);
  ctx.fill();

  // Тело
  ctx.fillStyle = '#f7d51d';
  ctx.beginPath();
  ctx.ellipse(0, 0, bird.w / 2, bird.h / 2, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = '#333';
  ctx.lineWidth = 2;
  ctx.stroke();

  // Крыло (машет)
  const wingAngle = Math.sin(frame * 0.3) * 0.3;
  ctx.save();
  ctx.translate(-4, 0);
  ctx.rotate(wingAngle);
  ctx.fillStyle = '#e6c419';
  ctx.beginPath();
  ctx.ellipse(0, 0, 10, 6, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();
  ctx.restore();

  // Глаз
  ctx.fillStyle = '#fff';
  ctx.beginPath();
  ctx.arc(8, -5, 5, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = '#000';
  ctx.beginPath();
  ctx.arc(9, -5, 2, 0, Math.PI * 2);
  ctx.fill();

  // Клюв
  ctx.fillStyle = '#f39c12';
  ctx.beginPath();
  ctx.moveTo(14, 0);
  ctx.lineTo(22, 3);
  ctx.lineTo(14, 6);
  ctx.closePath();
  ctx.fill();

  ctx.restore();
}

function draw() {
  // Градиентное небо
  const sky = ctx.createLinearGradient(0, 0, 0, H);
  sky.addColorStop(0, '#4ec0ca');
  sky.addColorStop(1, '#8fd8e0');
  ctx.fillStyle = sky;
  ctx.fillRect(0, 0, W, H);

  // Облака
  for (let c of clouds) drawCloud(c);

  // Трубы
  for (let p of pipes) drawPipe(p);

  // Земля
  ctx.fillStyle = '#ded895';
  ctx.fillRect(0, H - 40, W, 40);
  // Трава
  ctx.fillStyle = '#73bf2e';
  ctx.fillRect(0, H - 40, W, 8);
  // Текстура земли
  ctx.fillStyle = '#c9c06a';
  for (let x = -groundOffset; x < W; x += 20) {
    ctx.fillRect(x, H - 32, 10, 4);
    ctx.fillRect(x + 10, H - 24, 10, 4);
  }

  // Птица
  drawBird();

  // Счёт
  ctx.fillStyle = '#fff';
  ctx.strokeStyle = '#000';
  ctx.lineWidth = 4;
  ctx.font = 'bold 48px Courier New';
  ctx.textAlign = 'center';
  ctx.strokeText(score, W / 2, 70);
  ctx.fillText(score, W / 2, 70);

  ctx.font = 'bold 16px Courier New';
  ctx.fillStyle = '#fff';
  ctx.fillText('Рекорд: ' + best, W / 2, 100);

  if (gameOver) {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 32px Courier New';
    ctx.fillText('GAME OVER', W / 2, H / 2 - 40);
    ctx.font = 'bold 24px Courier New';
    ctx.fillText('Счёт: ' + score, W / 2, H / 2);
    ctx.font = 'bold 16px Courier New';
    ctx.fillText('Рекорд: ' + best, W / 2, H / 2 + 30);
    ctx.fillText('Нажми Space', W / 2, H / 2 + 70);
  }
}

function loop() {
  if (!gameOver) update();
  draw();
  requestAnimationFrame(loop);
}

createClouds();
loop();