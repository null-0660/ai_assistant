// Flappy Bird — v1: птица падает и прыгает

const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');

const W = canvas.width;
const H = canvas.height;

// Птица
const bird = {
  x: 80,
  y: H / 2,
  w: 34,
  h: 24,
  vy: 0,
};

const GRAVITY = 0.5;
const JUMP = -8;

let gameOver = false;

// Прыжок
function jump() {
  if (gameOver) return;
  bird.vy = JUMP;
}

// Управление
document.addEventListener('keydown', (e) => {
  if (e.code === 'Space') {
    e.preventDefault();
    jump();
  }
});
canvas.addEventListener('click', jump);

// Обновление физики
function update() {
  bird.vy += GRAVITY;
  bird.y += bird.vy;

  // Земля
  if (bird.y + bird.h / 2 > H) {
    bird.y = H - bird.h / 2;
    gameOver = true;
  }

  // Потолок
  if (bird.y - bird.h / 2 < 0) {
    bird.y = bird.h / 2;
    bird.vy = 0;
  }
}

// Рисование
function draw() {
  // Небо
  ctx.fillStyle = '#4ec0ca';
  ctx.fillRect(0, 0, W, H);

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

  // Game Over
  if (gameOver) {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 32px Courier New';
    ctx.textAlign = 'center';
    ctx.fillText('GAME OVER', W / 2, H / 2);
  }
}

// Игровой цикл
function loop() {
  if (!gameOver) {
    update();
  }
  draw();
  requestAnimationFrame(loop);
}

loop();