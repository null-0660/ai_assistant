// Flappy Bird — v2: трубы и столкновения

const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');

const W = canvas.width;
const H = canvas.height;

const bird = {
  x: 80, y: H / 2, w: 34, h: 24, vy: 0,
};

const GRAVITY = 0.5;
const JUMP = -8;
const PIPE_W = 60;
const PIPE_GAP = 150;
const PIPE_SPEED = 2.5;

let pipes = [];
let frame = 0;
let gameOver = false;

function resetGame() {
  bird.y = H / 2;
  bird.vy = 0;
  pipes = [];
  frame = 0;
  gameOver = false;
}

function jump() {
  if (gameOver) {
    resetGame();
    return;
  }
  bird.vy = JUMP;
}

document.addEventListener('keydown', (e) => {
  if (e.code === 'Space') { e.preventDefault(); jump(); }
});
canvas.addEventListener('click', jump);

// Создание трубы
function spawnPipe() {
  const minTop = 60;
  const maxTop = H - 40 - PIPE_GAP - 60;
  const topH = minTop + Math.random() * (maxTop - minTop);
  pipes.push({
    x: W,
    topH: topH,
    bottomY: topH + PIPE_GAP,
    scored: false,
  });
}

// Столкновения
function collides(px, py, pw, ph, rx, ry, rw, rh) {
  return px < rx + rw && px + pw > rx && py < ry + rh && py + ph > ry;
}

function update() {
  bird.vy += GRAVITY;
  bird.y += bird.vy;

  // Потолок
  if (bird.y - bird.h / 2 < 0) {
    bird.y = bird.h / 2;
    bird.vy = 0;
  }

  // Земля
  if (bird.y + bird.h / 2 > H - 40) {
    gameOver = true;
  }

  // Трубы
  frame++;
  if (frame % 90 === 0) spawnPipe();

  for (let p of pipes) {
    p.x -= PIPE_SPEED;

    // Верхняя труба
    const bx = bird.x - bird.w / 2;
    const by = bird.y - bird.h / 2;

    if (collides(bx, by, bird.w, bird.h, p.x, 0, PIPE_W, p.topH)) {
      gameOver = true;
    }
    if (collides(bx, by, bird.w, bird.h, p.x, p.bottomY, PIPE_W, H - p.bottomY)) {
      gameOver = true;
    }
  }

  // Удаляем ушедшие трубы
  pipes = pipes.filter(p => p.x + PIPE_W > 0);
}

function drawPipe(p) {
  // Верхняя
  ctx.fillStyle = '#73bf2e';
  ctx.fillRect(p.x, 0, PIPE_W, p.topH);
  ctx.fillStyle = '#5a9e1f';
  ctx.fillRect(p.x - 4, p.topH - 20, PIPE_W + 8, 20);
  ctx.strokeStyle = '#3d6b14';
  ctx.lineWidth = 2;
  ctx.strokeRect(p.x - 4, p.topH - 20, PIPE_W + 8, 20);

  // Нижняя
  ctx.fillStyle = '#73bf2e';
  ctx.fillRect(p.x, p.bottomY, PIPE_W, H - p.bottomY);
  ctx.fillStyle = '#5a9e1f';
  ctx.fillRect(p.x - 4, p.bottomY, PIPE_W + 8, 20);
  ctx.strokeStyle = '#3d6b14';
  ctx.strokeRect(p.x - 4, p.bottomY, PIPE_W + 8, 20);
}

function draw() {
  ctx.fillStyle = '#4ec0ca';
  ctx.fillRect(0, 0, W, H);

  // Трубы
  for (let p of pipes) drawPipe(p);

  // Земля
  ctx.fillStyle = '#ded895';
  ctx.fillRect(0, H - 40, W, 40);
  ctx.fillStyle = '#c9c06a';
  ctx.fillRect(0, H - 40, W, 8);

  // Птица
  ctx.fillStyle = '#f7d51d';
  ctx.beginPath();
  ctx.ellipse(bird.x, bird.y, bird.w / 2, bird.h / 2, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = '#333';
  ctx.lineWidth = 2;
  ctx.stroke();

  // Глаз
  ctx.fillStyle = '#fff';
  ctx.beginPath();
  ctx.arc(bird.x + 8, bird.y - 5, 5, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = '#000';
  ctx.beginPath();
  ctx.arc(bird.x + 9, bird.y - 5, 2, 0, Math.PI * 2);
  ctx.fill();

  // Клюв
  ctx.fillStyle = '#f39c12';
  ctx.beginPath();
  ctx.moveTo(bird.x + 14, bird.y);
  ctx.lineTo(bird.x + 22, bird.y + 3);
  ctx.lineTo(bird.x + 14, bird.y + 6);
  ctx.closePath();
  ctx.fill();

  if (gameOver) {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 32px Courier New';
    ctx.textAlign = 'center';
    ctx.fillText('GAME OVER', W / 2, H / 2 - 20);
    ctx.font = 'bold 18px Courier New';
    ctx.fillText('Нажми Space', W / 2, H / 2 + 20);
  }
}

function loop() {
  if (!gameOver) update();
  draw();
  requestAnimationFrame(loop);
}

loop();