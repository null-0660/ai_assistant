// ============================================================
// FLAPPY BIRD — полная рабочая игра
// ============================================================

(function () {
  'use strict';

  // ===== Canvas =====
  const canvas = document.getElementById('game');
  const ctx = canvas.getContext('2d');
  const W = canvas.width;
  const H = canvas.height;

  // ===== Константы =====
  const GRAVITY = 0.35;
  const JUMP = -6.5;
  const MAX_FALL = 10;
  const PIPE_W = 60;
  const PIPE_GAP = 160;
  const PIPE_SPEED = 2.2;
  const PIPE_SPAWN = 100;
  const GROUND_H = 60;

  // ===== Состояние =====
  const bird = { x: 100, y: H / 2, w: 34, h: 24, vy: 0, rot: 0 };
  let pipes = [];
  let clouds = [];
  let frame = 0;
  let score = 0;
  let best = parseInt(localStorage.getItem('flappyBest') || '0', 10);
  let state = 'ready'; // ready | playing | gameover
  let groundOffset = 0;
  let shake = 0;

  // ===== Аудио =====
  let audioCtx = null;

  function initAudio() {
    try {
      if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      }
      if (audioCtx.state === 'suspended') {
        audioCtx.resume();
      }
    } catch (e) {
      console.warn('Audio init failed:', e);
    }
  }

  function beep(freq, dur, vol = 0.06, type = 'square') {
    if (!audioCtx) return;
    try {
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = type;
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(vol, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + dur);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + dur);
    } catch (e) {}
  }

  // ===== Облака =====
  function createClouds() {
    clouds = [];
    for (let i = 0; i < 5; i++) {
      clouds.push({
        x: Math.random() * W,
        y: 40 + Math.random() * 180,
        size: 30 + Math.random() * 40,
        speed: 0.3 + Math.random() * 0.5,
      });
    }
  }

  // ===== Сброс =====
  function resetGame() {
    bird.y = H / 2;
    bird.vy = 0;
    bird.rot = 0;
    pipes = [];
    frame = 0;
    score = 0;
    state = 'ready';
    shake = 0;
    createClouds();
  }

  // ===== Прыжок =====
  function jump() {
    initAudio();

    if (state === 'ready') {
      state = 'playing';
      bird.vy = JUMP;
      beep(600, 0.08);
      return;
    }
    if (state === 'playing') {
      bird.vy = JUMP;
      beep(600, 0.08);
      return;
    }
    if (state === 'gameover') {
      resetGame();
      state = 'playing';
      bird.vy = JUMP;
      beep(600, 0.08);
    }
  }

  // ===== Управление =====
  document.addEventListener('keydown', (e) => {
    if (e.code === 'Space' || e.code === 'ArrowUp') {
      e.preventDefault();
      jump();
    }
  });

  canvas.addEventListener('click', jump);
  canvas.addEventListener('touchstart', (e) => {
    e.preventDefault();
    jump();
  }, { passive: false });

  // ===== Трубы =====
  function spawnPipe() {
    const minTop = 60;
    const maxTop = H - GROUND_H - PIPE_GAP - 60;
    const topH = minTop + Math.random() * (maxTop - minTop);
    pipes.push({
      x: W,
      topH,
      bottomY: topH + PIPE_GAP,
      scored: false,
    });
  }

  function collides(px, py, pw, ph, rx, ry, rw, rh) {
    return px < rx + rw && px + pw > rx && py < ry + rh && py + ph > ry;
  }

  // ===== Обновление =====
  function update() {
    if (state !== 'playing') {
      // Облака двигаются всегда
      for (let c of clouds) {
        c.x -= c.speed;
        if (c.x + c.size < 0) {
          c.x = W + c.size;
          c.y = 40 + Math.random() * 180;
        }
      }
      return;
    }

    // Гравитация
    bird.vy = Math.min(bird.vy + GRAVITY, MAX_FALL);
    bird.y += bird.vy;

    // Наклон
    bird.rot = Math.max(-0.5, Math.min(1.4, bird.vy * 0.1));

    // Потолок
    if (bird.y - bird.h / 2 < 0) {
      bird.y = bird.h / 2;
      bird.vy = 0;
    }

    // Земля
    if (bird.y + bird.h / 2 > H - GROUND_H) {
      bird.y = H - GROUND_H - bird.h / 2;
      endGame();
      return;
    }

    // Облака
    for (let c of clouds) {
      c.x -= c.speed;
      if (c.x + c.size < 0) {
        c.x = W + c.size;
        c.y = 40 + Math.random() * 180;
      }
    }

    // Земля
    groundOffset = (groundOffset + PIPE_SPEED) % 40;

    // Трубы
    frame++;
    if (frame % PIPE_SPAWN === 0) spawnPipe();

    for (let p of pipes) {
      p.x -= PIPE_SPEED;

      const bx = bird.x - bird.w / 2 + 4;
      const by = bird.y - bird.h / 2 + 4;
      const bw = bird.w - 8;
      const bh = bird.h - 8;

      if (collides(bx, by, bw, bh, p.x, 0, PIPE_W, p.topH)) {
        endGame();
        return;
      }
      if (collides(bx, by, bw, bh, p.x, p.bottomY, PIPE_W, H - p.bottomY)) {
        endGame();
        return;
      }

      if (!p.scored && p.x + PIPE_W < bird.x) {
        p.scored = true;
        score++;
        beep(900, 0.1);
        if (score > best) {
          best = score;
          localStorage.setItem('flappyBest', best);
        }
      }
    }

    pipes = pipes.filter((p) => p.x + PIPE_W > 0);

    if (shake > 0) shake -= 1;
  }

  function endGame() {
    if (state === 'gameover') return;
    state = 'gameover';
    shake = 15;
    beep(200, 0.4, 0.08, 'sawtooth');
    if (score > best) {
      best = score;
      localStorage.setItem('flappyBest', best);
    }
  }

  // ===== Рисование =====
  function drawCloud(c) {
    ctx.fillStyle = 'rgba(255, 255, 255, 0.75)';
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

    // Крыло
    const wingAngle = state === 'playing' ? Math.sin(frame * 0.3) * 0.4 : 0;
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
    ctx.save();

    // Тряска
    if (shake > 0) {
      ctx.translate(
        (Math.random() - 0.5) * shake,
        (Math.random() - 0.5) * shake
      );
    }

    // Небо
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
    ctx.fillRect(0, H - GROUND_H, W, GROUND_H);
    ctx.fillStyle = '#73bf2e';
    ctx.fillRect(0, H - GROUND_H, W, 8);

    ctx.fillStyle = '#c9c06a';
    for (let x = -groundOffset; x < W; x += 20) {
      ctx.fillRect(x, H - GROUND_H + 12, 10, 4);
      ctx.fillRect(x + 10, H - GROUND_H + 20, 10, 4);
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
    ctx.lineWidth = 3;
    ctx.strokeText('Рекорд: ' + best, W / 2, 100);
    ctx.fillText('Рекорд: ' + best, W / 2, 100);

    // Ready
    if (state === 'ready') {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.35)';
      ctx.fillRect(0, 0, W, H);

      ctx.fillStyle = '#f7d51d';
      ctx.strokeStyle = '#000';
      ctx.lineWidth = 6;
      ctx.font = 'bold 42px Courier New';
      ctx.strokeText('FLAPPY', W / 2, H / 2 - 80);
      ctx.fillText('FLAPPY', W / 2, H / 2 - 80);

      ctx.font = 'bold 42px Courier New';
      ctx.strokeText('BIRD', W / 2, H / 2 - 30);
      ctx.fillText('BIRD', W / 2, H / 2 - 30);

      ctx.fillStyle = '#fff';
      ctx.font = 'bold 20px Courier New';
      ctx.lineWidth = 4;
      ctx.strokeText('Нажми Space', W / 2, H / 2 + 60);
      ctx.fillText('Нажми Space', W / 2, H / 2 + 60);
      ctx.font = 'bold 16px Courier New';
      ctx.strokeText('или кликни', W / 2, H / 2 + 90);
      ctx.fillText('или кликни', W / 2, H / 2 + 90);

      ctx.font = 'bold 18px Courier New';
      ctx.fillStyle = '#fff';
      ctx.strokeText('Рекорд: ' + best, W / 2, H / 2 + 140);
      ctx.fillText('Рекорд: ' + best, W / 2, H / 2 + 140);
    }

    // Game Over
    if (state === 'gameover') {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.55)';
      ctx.fillRect(0, 0, W, H);

      // Панель
      ctx.fillStyle = '#ded895';
      ctx.strokeStyle = '#3d6b14';
      ctx.lineWidth = 4;
      const pw = 280;
      const ph = 260;
      const px = (W - pw) / 2;
      const py = (H - ph) / 2;
      ctx.fillRect(px, py, pw, ph);
      ctx.strokeRect(px, py, pw, ph);

      ctx.fillStyle = '#3d6b14';
      ctx.font = 'bold 32px Courier New';
      ctx.fillText('GAME OVER', W / 2, py + 50);

      ctx.fillStyle = '#333';
      ctx.font = 'bold 24px Courier New';
      ctx.fillText('Счёт: ' + score, W / 2, py + 110);

      ctx.fillStyle = '#c9a227';
      ctx.font = 'bold 18px Courier New';
      ctx.fillText('Рекорд: ' + best, W / 2, py + 150);

      ctx.fillStyle = '#4ec0ca';
      ctx.font = 'bold 16px Courier New';
      ctx.fillText('Space — заново', W / 2, py + 210);
    }

    ctx.restore();
  }

  // ===== Цикл =====
  function loop() {
    update();
    draw();
    requestAnimationFrame(loop);
  }

  // ===== Старт =====
  createClouds();
  loop();
})();