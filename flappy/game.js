// Flappy Bird — v7: геймплей - сложность, пауза, прогресс

(function () {
  'use strict';

  const canvas = document.getElementById('game');
  const ctx = canvas.getContext('2d');
  const W = canvas.width;
  const H = canvas.height;

  const GRAVITY = 0.35;
  const JUMP = -6.5;
  const MAX_FALL = 10;
  const PIPE_W = 60;
  const PIPE_GAP = 160;
  const BASE_SPEED = 2.2;
  const PIPE_SPAWN = 100;
  const GROUND_H = 60;
  const HITBOX_PAD = 5;

  const bird = { x: 100, y: H / 2, w: 34, h: 24, vy: 0, rot: 0 };
  let pipes = [];
  let clouds = [];
  let frame = 0;
  let score = 0;
  let best = parseInt(localStorage.getItem('flappyBest') || '0', 10);
  let state = 'ready'; // ready | playing | paused | gameover
  let groundOffset = 0;
  let shake = 0;
  let time = 0;
  let combo = 0;
  let comboFlash = 0;

  let audioCtx = null;

  function initAudio() {
    try {
      if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      if (audioCtx.state === 'suspended') audioCtx.resume();
    } catch (e) {}
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

  function pipeSpeed() {
    return BASE_SPEED + Math.min(score * 0.08, 3);
  }

  function pipeGap() {
    return Math.max(120, PIPE_GAP - score * 2);
  }

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

  function resetGame() {
    bird.y = H / 2;
    bird.vy = 0;
    bird.rot = 0;
    pipes = [];
    frame = 0;
    score = 0;
    combo = 0;
    comboFlash = 0;
    state = 'ready';
    shake = 0;
    createClouds();
  }

  function jump() {
    initAudio();
    if (state === 'ready') {
      state = 'playing';
      bird.vy = JUMP;
      beep(600, 0.08);
    } else if (state === 'playing') {
      bird.vy = JUMP;
      beep(600, 0.08);
    } else if (state === 'paused') {
      state = 'playing';
    } else if (state === 'gameover') {
      resetGame();
      state = 'playing';
      bird.vy = JUMP;
      beep(600, 0.08);
    }
  }

  document.addEventListener('keydown', (e) => {
    if (e.code === 'Space' || e.code === 'ArrowUp') {
      e.preventDefault();
      jump();
    }
    if (e.code === 'KeyP' || e.code === 'Escape') {
      if (state === 'playing') state = 'paused';
      else if (state === 'paused') state = 'playing';
    }
  });
  canvas.addEventListener('click', jump);
  canvas.addEventListener('touchstart', (e) => {
    e.preventDefault();
    jump();
  }, { passive: false });

  function spawnPipe() {
    const minTop = 60;
    const maxTop = H - GROUND_H - pipeGap() - 60;
    const topH = minTop + Math.random() * (maxTop - minTop);
    pipes.push({ x: W, topH, bottomY: topH + pipeGap(), scored: false });
  }

  function collides(px, py, pw, ph, rx, ry, rw, rh) {
    return px < rx + rw && px + pw > rx && py < ry + rh && py + ph > ry;
  }

  function update() {
    time++;

    for (let c of clouds) {
      c.x -= c.speed;
      if (c.x + c.size < 0) {
        c.x = W + c.size;
        c.y = 40 + Math.random() * 180;
      }
    }

    if (state !== 'playing') return;

    bird.vy = Math.min(bird.vy + GRAVITY, MAX_FALL);
    bird.y += bird.vy;
    bird.rot = Math.max(-0.5, Math.min(1.4, bird.vy * 0.1));

    if (bird.y - bird.h / 2 < 0) {
      bird.y = bird.h / 2;
      bird.vy = 0;
    }

    if (bird.y + bird.h / 2 > H - GROUND_H) {
      bird.y = H - GROUND_H - bird.h / 2;
      endGame();
      return;
    }

    groundOffset = (groundOffset + pipeSpeed()) % 40;
    frame++;
    if (frame % PIPE_SPAWN === 0) spawnPipe();

    const bx = bird.x - bird.w / 2 + HITBOX_PAD;
    const by = bird.y - bird.h / 2 + HITBOX_PAD;
    const bw = bird.w - HITBOX_PAD * 2;
    const bh = bird.h - HITBOX_PAD * 2;

    for (let p of pipes) {
      p.x -= pipeSpeed();

      if (collides(bx, by, bw, bh, p.x, 0, PIPE_W, p.topH)) { endGame(); return; }
      if (collides(bx, by, bw, bh, p.x, p.bottomY, PIPE_W, H - p.bottomY)) { endGame(); return; }

      if (!p.scored && p.x + PIPE_W < bird.x) {
        p.scored = true;
        score++;
        combo++;
        comboFlash = 30;
        if (combo === 3) {
          beep(1200, 0.15);
          score += 2; // бонус
        } else {
          beep(900, 0.1);
        }
        if (score > best) {
          best = score;
          localStorage.setItem('flappyBest', best);
        }
      }
    }

    pipes = pipes.filter((p) => p.x + PIPE_W > 0);
    if (shake > 0) shake -= 1;
    if (comboFlash > 0) comboFlash -= 1;
  }

  function endGame() {
    if (state === 'gameover') return;
    state = 'gameover';
    shake = 15;
    combo = 0;
    beep(200, 0.4, 0.08, 'sawtooth');
    if (score > best) {
      best = score;
      localStorage.setItem('flappyBest', best);
    }
  }

  // ===== Рисование =====
  function drawSun() {
    const sx = W - 60, sy = 80, r = 30;
    ctx.save();
    ctx.translate(sx, sy);
    ctx.rotate(time * 0.005);
    ctx.fillStyle = 'rgba(255, 220, 100, 0.4)';
    for (let i = 0; i < 8; i++) {
      ctx.rotate(Math.PI / 4);
      ctx.fillRect(-3, -r - 15, 6, 15);
    }
    ctx.restore();

    const grad = ctx.createRadialGradient(sx, sy, 5, sx, sy, r);
    grad.addColorStop(0, '#fff8b0');
    grad.addColorStop(1, '#f7d51d');
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(sx, sy, r, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#c9a227';
    ctx.lineWidth = 2;
    ctx.stroke();
  }

  function drawCloud(c) {
    ctx.fillStyle = 'rgba(255, 255, 255, 0.85)';
    ctx.beginPath();
    ctx.arc(c.x, c.y, c.size * 0.6, 0, Math.PI * 2);
    ctx.arc(c.x + c.size * 0.5, c.y, c.size * 0.5, 0, Math.PI * 2);
    ctx.arc(c.x - c.size * 0.5, c.y, c.size * 0.5, 0, Math.PI * 2);
    ctx.arc(c.x + c.size * 0.2, c.y - c.size * 0.3, c.size * 0.4, 0, Math.PI * 2);
    ctx.fill();
  }

  function drawPipe(p) {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.25)';
    ctx.fillRect(p.x + 6, 0, PIPE_W, p.topH);
    ctx.fillRect(p.x + 6, p.bottomY, PIPE_W, H - p.bottomY);

    const topGrad = ctx.createLinearGradient(p.x, 0, p.x + PIPE_W, 0);
    topGrad.addColorStop(0, '#4a8f1e');
    topGrad.addColorStop(0.3, '#8fdc4a');
    topGrad.addColorStop(0.7, '#73bf2e');
    topGrad.addColorStop(1, '#3d6b14');
    ctx.fillStyle = topGrad;
    ctx.fillRect(p.x, 0, PIPE_W, p.topH);

    const capGrad = ctx.createLinearGradient(p.x - 4, 0, p.x + PIPE_W + 4, 0);
    capGrad.addColorStop(0, '#3d6b14');
    capGrad.addColorStop(0.3, '#8fdc4a');
    capGrad.addColorStop(0.7, '#5a9e1f');
    capGrad.addColorStop(1, '#2d5b0e');
    ctx.fillStyle = capGrad;
    ctx.fillRect(p.x - 4, p.topH - 20, PIPE_W + 8, 20);
    ctx.strokeStyle = '#2d5b0e';
    ctx.lineWidth = 2;
    ctx.strokeRect(p.x - 4, p.topH - 20, PIPE_W + 8, 20);

    ctx.fillStyle = 'rgba(255, 255, 255, 0.25)';
    ctx.fillRect(p.x + 6, 0, 6, p.topH - 20);

    const botGrad = ctx.createLinearGradient(p.x, 0, p.x + PIPE_W, 0);
    botGrad.addColorStop(0, '#4a8f1e');
    botGrad.addColorStop(0.3, '#8fdc4a');
    botGrad.addColorStop(0.7, '#73bf2e');
    botGrad.addColorStop(1, '#3d6b14');
    ctx.fillStyle = botGrad;
    ctx.fillRect(p.x, p.bottomY, PIPE_W, H - p.bottomY);

    ctx.fillStyle = capGrad;
    ctx.fillRect(p.x - 4, p.bottomY, PIPE_W + 8, 20);
    ctx.strokeStyle = '#2d5b0e';
    ctx.strokeRect(p.x - 4, p.bottomY, PIPE_W + 8, 20);

    ctx.fillStyle = 'rgba(255, 255, 255, 0.25)';
    ctx.fillRect(p.x + 6, p.bottomY + 20, 6, H - p.bottomY - 20);
  }

  function drawBird() {
    ctx.save();
    ctx.translate(bird.x, bird.y);
    ctx.rotate(bird.rot);

    ctx.fillStyle = 'rgba(0, 0, 0, 0.25)';
    ctx.beginPath();
    ctx.ellipse(3, 3, bird.w / 2, bird.h / 2, 0, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#e6c419';
    ctx.beginPath();
    ctx.moveTo(-bird.w / 2 + 2, -4);
    ctx.lineTo(-bird.w / 2 - 8, -8);
    ctx.lineTo(-bird.w / 2 - 6, 0);
    ctx.lineTo(-bird.w / 2 - 8, 8);
    ctx.lineTo(-bird.w / 2 + 2, 4);
    ctx.closePath();
    ctx.fill();
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    const bodyGrad = ctx.createRadialGradient(-4, -6, 4, 0, 0, bird.w / 2 + 4);
    bodyGrad.addColorStop(0, '#fff08a');
    bodyGrad.addColorStop(1, '#f7d51d');
    ctx.fillStyle = bodyGrad;
    ctx.beginPath();
    ctx.ellipse(0, 0, bird.w / 2, bird.h / 2, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 2;
    ctx.stroke();

    const wingAngle = state === 'playing' ? Math.sin(frame * 0.3) * 0.4 : 0;
    ctx.save();
    ctx.translate(-4, 0);
    ctx.rotate(wingAngle);
    ctx.fillStyle = '#e6c419';
    ctx.beginPath();
    ctx.ellipse(0, 0, 11, 7, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    ctx.restore();

    ctx.fillStyle = 'rgba(255, 150, 150, 0.5)';
    ctx.beginPath();
    ctx.arc(4, 4, 4, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#fff';
    ctx.beginPath();
    ctx.arc(9, -6, 6, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    ctx.fillStyle = '#000';
    ctx.beginPath();
    ctx.arc(10, -6, 2.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#fff';
    ctx.beginPath();
    ctx.arc(11, -7, 1, 0, Math.PI * 2);
    ctx.fill();

    const beakGrad = ctx.createLinearGradient(14, 0, 22, 6);
    beakGrad.addColorStop(0, '#ffb347');
    beakGrad.addColorStop(1, '#e67e22');
    ctx.fillStyle = beakGrad;
    ctx.beginPath();
    ctx.moveTo(14, -2);
    ctx.lineTo(23, 3);
    ctx.lineTo(14, 8);
    ctx.closePath();
    ctx.fill();
    ctx.strokeStyle = '#a0522d';
    ctx.lineWidth = 1;
    ctx.stroke();

    ctx.restore();
  }

  function drawGround() {
    ctx.fillStyle = '#ded895';
    ctx.fillRect(0, H - GROUND_H, W, GROUND_H);

    ctx.fillStyle = '#73bf2e';
    ctx.fillRect(0, H - GROUND_H, W, 10);

    ctx.fillStyle = '#5a9e1f';
    for (let x = -groundOffset; x < W; x += 20) {
      ctx.fillRect(x, H - GROUND_H, 4, 10);
    }

    ctx.fillStyle = '#c9c06a';
    for (let x = -groundOffset; x < W; x += 40) {
      ctx.fillRect(x, H - GROUND_H + 20, 20, 4);
      ctx.fillRect(x + 20, H - GROUND_H + 32, 15, 4);
    }

    for (let x = -groundOffset * 2; x < W; x += 80) {
      const fx = x + 30;
      const fy = H - GROUND_H + 6;
      ctx.fillStyle = '#ff6b9d';
      ctx.beginPath();
      ctx.arc(fx, fy, 3, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#fff';
      ctx.beginPath();
      ctx.arc(fx, fy, 1.5, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  function drawHUD() {
    ctx.fillStyle = '#fff';
    ctx.strokeStyle = '#000';
    ctx.lineWidth = 5;
    ctx.font = 'bold 48px Courier New';
    ctx.textAlign = 'center';
    ctx.strokeText(score, W / 2, 70);
    ctx.fillText(score, W / 2, 70);

    ctx.font = 'bold 16px Courier New';
    ctx.lineWidth = 3;
    ctx.strokeText('Рекорд: ' + best, W / 2, 100);
    ctx.fillText('Рекорд: ' + best, W / 2, 100);

    // Комбо
    if (combo >= 2 && comboFlash > 0) {
      ctx.fillStyle = '#f7d51d';
      ctx.font = 'bold 24px Courier New';
      ctx.fillText('x' + combo + ' COMBO!', W / 2, 140);
    }

    // Прогресс до следующей сложности
    const progress = (score % 10) / 10;
    const barW = 200;
    const barX = (W - barW) / 2;
    const barY = H - GROUND_H + 25;
    ctx.fillStyle = 'rgba(0, 0, 0, 0.4)';
    ctx.fillRect(barX, barY, barW, 10);
    ctx.fillStyle = '#f7d51d';
    ctx.fillRect(barX, barY, barW * progress, 10);
    ctx.strokeStyle = '#000';
    ctx.lineWidth = 1;
    ctx.strokeRect(barX, barY, barW, 10);
  }

  function draw() {
    ctx.save();

    if (shake > 0) {
      ctx.translate(
        (Math.random() - 0.5) * shake,
        (Math.random() - 0.5) * shake
      );
    }

    const sky = ctx.createLinearGradient(0, 0, 0, H);
    sky.addColorStop(0, '#4ec0ca');
    sky.addColorStop(0.5, '#8fd8e0');
    sky.addColorStop(1, '#c5e8ed');
    ctx.fillStyle = sky;
    ctx.fillRect(0, 0, W, H);

    drawSun();
    for (let c of clouds) drawCloud(c);
    for (let p of pipes) drawPipe(p);
    drawGround();
    drawBird();
    drawHUD();

    if (state === 'ready') {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.35)';
      ctx.fillRect(0, 0, W, H);

      ctx.fillStyle = '#f7d51d';
      ctx.strokeStyle = '#000';
      ctx.lineWidth = 6;
      ctx.font = 'bold 42px Courier New';
      ctx.textAlign = 'center';
      ctx.strokeText('FLAPPY', W / 2, H / 2 - 80);
      ctx.fillText('FLAPPY', W / 2, H / 2 - 80);
      ctx.strokeText('BIRD', W / 2, H / 2 - 30);
      ctx.fillText('BIRD', W / 2, H / 2 - 30);

      ctx.fillStyle = '#fff';
      ctx.font = 'bold 20px Courier New';
      ctx.lineWidth = 4;
      ctx.strokeText('Нажми Space', W / 2, H / 2 + 60);
      ctx.fillText('Нажми Space', W / 2, H / 2 + 60);
    }

    if (state === 'paused') {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
      ctx.fillRect(0, 0, W, H);

      ctx.fillStyle = '#f7d51d';
      ctx.strokeStyle = '#000';
      ctx.lineWidth = 6;
      ctx.font = 'bold 48px Courier New';
      ctx.textAlign = 'center';
      ctx.strokeText('ПАУЗА', W / 2, H / 2);
      ctx.fillText('ПАУЗА', W / 2, H / 2);

      ctx.fillStyle = '#fff';
      ctx.font = 'bold 18px Courier New';
      ctx.strokeText('P — продолжить', W / 2, H / 2 + 60);
      ctx.fillText('P — продолжить', W / 2, H / 2 + 60);
    }

    if (state === 'gameover') {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.55)';
      ctx.fillRect(0, 0, W, H);

      const pw = 280, ph = 260;
      const px = (W - pw) / 2, py = (H - ph) / 2;

      ctx.fillStyle = '#ded895';
      ctx.strokeStyle = '#3d6b14';
      ctx.lineWidth = 4;
      ctx.fillRect(px, py, pw, ph);
      ctx.strokeRect(px, py, pw, ph);

      ctx.fillStyle = '#3d6b14';
      ctx.font = 'bold 32px Courier New';
      ctx.textAlign = 'center';
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

  function loop() {
    update();
    draw();
    requestAnimationFrame(loop);
  }

  createClouds();
  loop();
})();