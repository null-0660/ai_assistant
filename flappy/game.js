// Flappy Bird — v11: 3 режима игры

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

  const MODES = {
    classic: { name: 'Classic', icon: '🎮', desc: 'Классика' },
    time: { name: 'Time Attack', icon: '⏱', desc: '60 секунд' },
    mirror: { name: 'Mirror', icon: '🪞', desc: 'Зеркальные трубы' },
  };

  const bird = { x: 100, y: H / 2, w: 34, h: 24, vy: 0, rot: 0 };
  let pipes = [];
  let clouds = [];
  let particles = [];
  let frame = 0;
  let score = 0;
  let best = parseInt(localStorage.getItem('flappyBest') || '0', 10);
  let state = 'menu';
  let mode = 'classic';
  let groundOffset = 0;
  let shake = 0;
  let time = 0;
  let combo = 0;
  let comboFlash = 0;
  let lives = 1;
  let goldenCount = 0;
  let invincible = 0;
  let trail = [];
  let timeLeft = 60;
  let selectedMode = 0;

  let audioCtx = null;
  let muted = localStorage.getItem('flappyMuted') === 'true';

  function initAudio() {
    try {
      if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      if (audioCtx.state === 'suspended') audioCtx.resume();
    } catch (e) {}
  }

  function beep(freq, dur, vol = 0.06, type = 'square') {
    if (muted || !audioCtx) return;
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

  function spawnParticle(x, y, vx, vy, color, size, life) {
    particles.push({ x, y, vx, vy, color, size, life, maxLife: life });
  }

  function explode(x, y, color, count) {
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 2 + Math.random() * 4;
      spawnParticle(x, y, Math.cos(angle) * speed, Math.sin(angle) * speed,
        color, 2 + Math.random() * 4, 30 + Math.random() * 30);
    }
  }

  function starsBurst(x, y) {
    for (let i = 0; i < 12; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 1 + Math.random() * 3;
      spawnParticle(x, y, Math.cos(angle) * speed, Math.sin(angle) * speed,
        '#ffd700', 3 + Math.random() * 3, 40 + Math.random() * 20);
    }
  }

  function updateParticles() {
    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.vy += 0.15;
      p.vx *= 0.98;
      p.life--;
      if (p.life <= 0) particles.splice(i, 1);
    }
  }

  function drawParticles() {
    for (let p of particles) {
      const alpha = p.life / p.maxLife;
      ctx.globalAlpha = alpha;
      ctx.fillStyle = p.color;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size * alpha, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
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
    particles = [];
    trail = [];
    frame = 0;
    score = 0;
    combo = 0;
    comboFlash = 0;
    lives = 1;
    goldenCount = 0;
    invincible = 0;
    shake = 0;
    timeLeft = 60;
    createClouds();
  }

  function startGame(m) {
    mode = m;
    resetGame();
    state = 'playing';
    bird.vy = JUMP;
    initAudio();
    beep(600, 0.08);
  }

  function jump() {
    if (state === 'playing') {
      bird.vy = JUMP;
      beep(600, 0.08);
    }
  }

  function selectMode(dir) {
    const keys = Object.keys(MODES);
    selectedMode = (selectedMode + dir + keys.length) % keys.length;
    beep(700, 0.05);
  }

  document.addEventListener('keydown', (e) => {
    if (e.code === 'KeyM') {
      muted = !muted;
      localStorage.setItem('flappyMuted', muted);
      return;
    }

    if (state === 'menu') {
      if (e.code === 'ArrowLeft' || e.code === 'KeyA') {
        e.preventDefault();
        selectMode(-1);
      } else if (e.code === 'ArrowRight' || e.code === 'KeyD') {
        e.preventDefault();
        selectMode(1);
      } else if (e.code === 'Space' || e.code === 'Enter') {
        e.preventDefault();
        const keys = Object.keys(MODES);
        startGame(keys[selectedMode]);
      }
      return;
    }

    if (e.code === 'Space' || e.code === 'ArrowUp') {
      e.preventDefault();
      if (state === 'gameover') {
        state = 'menu';
      } else {
        jump();
      }
    }
    if (e.code === 'KeyP' || e.code === 'Escape') {
      if (state === 'playing') state = 'paused';
      else if (state === 'paused') state = 'playing';
    }
  });

  canvas.addEventListener('click', (e) => {
    const rect = canvas.getBoundingClientRect();
    const mx = (e.clientX - rect.left) * (W / rect.width);
    const my = (e.clientY - rect.top) * (H / rect.height);

    if (mx > W - 50 && my < 50) {
      muted = !muted;
      localStorage.setItem('flappyMuted', muted);
      return;
    }

    if (state === 'menu') {
      const keys = Object.keys(MODES);
      const boxW = 220, boxH = 100;
      const totalW = keys.length * boxW + (keys.length - 1) * 20;
      const startX = (W - totalW) / 2;
      const boxY = H / 2 - boxH / 2 + 40;

      for (let i = 0; i < keys.length; i++) {
        const bx = startX + i * (boxW + 20);
        if (mx > bx && mx < bx + boxW && my > boxY && my < boxY + boxH) {
          selectedMode = i;
          startGame(keys[i]);
          return;
        }
      }
      startGame(keys[selectedMode]);
      return;
    }

    if (state === 'gameover') {
      state = 'menu';
      return;
    }
    jump();
  });

  function spawnPipe() {
    const minTop = 60;
    const maxTop = H - GROUND_H - pipeGap() - 60;
    const topH = minTop + Math.random() * (maxTop - minTop);
    const isGolden = Math.random() < 0.15;
    pipes.push({
      x: W,
      topH,
      bottomY: topH + pipeGap(),
      scored: false,
      golden: isGolden,
    });
  }

  function collides(px, py, pw, ph, rx, ry, rw, rh) {
    return px < rx + rw && px + pw > rx && py < ry + rh && py + ph > ry;
  }

  function update() {
    time++;
    updateParticles();

    for (let c of clouds) {
      c.x -= c.speed;
      if (c.x + c.size < 0) {
        c.x = W + c.size;
        c.y = 40 + Math.random() * 180;
      }
    }

    if (state !== 'playing') return;

    if (mode === 'time') {
      timeLeft -= 1 / 60;
      if (timeLeft <= 0) {
        endGame();
        return;
      }
    }

    if (invincible > 0) invincible--;

    if (frame % 3 === 0) {
      trail.push({ x: bird.x, y: bird.y, life: 15, maxLife: 15, rot: bird.rot });
    }
    for (let i = trail.length - 1; i >= 0; i--) {
      trail[i].life--;
      if (trail[i].life <= 0) trail.splice(i, 1);
    }

    bird.vy = Math.min(bird.vy + GRAVITY, MAX_FALL);
    bird.y += bird.vy;
    bird.rot = Math.max(-0.5, Math.min(1.4, bird.vy * 0.1));

    if (bird.y - bird.h / 2 < 0) {
      bird.y = bird.h / 2;
      bird.vy = 0;
    }

    if (bird.y + bird.h / 2 > H - GROUND_H) {
      bird.y = H - GROUND_H - bird.h / 2;
      hit();
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

      if (invincible === 0) {
        if (collides(bx, by, bw, bh, p.x, 0, PIPE_W, p.topH)) {
          explode(bird.x, bird.y, '#f7d51d', 20);
          hit();
          return;
        }
        if (collides(bx, by, bw, bh, p.x, p.bottomY, PIPE_W, H - p.bottomY)) {
          explode(bird.x, bird.y, '#f7d51d', 20);
          hit();
          return;
        }
      }

      if (!p.scored && p.x + PIPE_W < bird.x) {
        p.scored = true;
        combo++;
        comboFlash = 30;

        if (p.golden) {
          score += 3;
          goldenCount++;
          starsBurst(bird.x, bird.y);
          beep(1400, 0.15);
          if (goldenCount >= 5) {
            goldenCount = 0;
            lives++;
            beep(1800, 0.3);
          }
        } else {
          score += 1;
          if (combo === 3) {
            beep(1200, 0.15);
            score += 2;
            explode(bird.x, bird.y, '#f7d51d', 10);
          } else {
            beep(900, 0.1);
          }
        }

        if (score > best && mode === 'classic') {
          best = score;
          localStorage.setItem('flappyBest', best);
        }
      }
    }

    pipes = pipes.filter((p) => p.x + PIPE_W > 0);
    if (shake > 0) shake -= 1;
    if (comboFlash > 0) comboFlash -= 1;
  }

  function hit() {
    if (invincible > 0) return;
    lives--;
    combo = 0;
    shake = 15;
    invincible = 90;
    if (lives <= 0) {
      endGame();
    } else {
      beep(300, 0.2, 0.08, 'sawtooth');
      bird.y = H / 2;
      bird.vy = 0;
      bird.rot = 0;
    }
  }

  function endGame() {
    if (state === 'gameover') return;
    state = 'gameover';
    shake = 15;
    combo = 0;
    explode(bird.x, bird.y, '#f7d51d', 40);
    explode(bird.x, bird.y, '#ff6b9d', 20);
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
    const isGolden = p.golden;
    ctx.fillStyle = 'rgba(0, 0, 0, 0.25)';
    ctx.fillRect(p.x + 6, 0, PIPE_W, p.topH);
    ctx.fillRect(p.x + 6, p.bottomY, PIPE_W, H - p.bottomY);

    const topGrad = ctx.createLinearGradient(p.x, 0, p.x + PIPE_W, 0);
    if (isGolden) {
      topGrad.addColorStop(0, '#b8860b');
      topGrad.addColorStop(0.3, '#ffd700');
      topGrad.addColorStop(0.7, '#ffed4e');
      topGrad.addColorStop(1, '#b8860b');
    } else {
      topGrad.addColorStop(0, '#4a8f1e');
      topGrad.addColorStop(0.3, '#8fdc4a');
      topGrad.addColorStop(0.7, '#73bf2e');
      topGrad.addColorStop(1, '#3d6b14');
    }
    ctx.fillStyle = topGrad;
    ctx.fillRect(p.x, 0, PIPE_W, p.topH);

    const capGrad = ctx.createLinearGradient(p.x - 4, 0, p.x + PIPE_W + 4, 0);
    if (isGolden) {
      capGrad.addColorStop(0, '#b8860b');
      capGrad.addColorStop(0.3, '#ffd700');
      capGrad.addColorStop(0.7, '#ffed4e');
      capGrad.addColorStop(1, '#b8860b');
    } else {
      capGrad.addColorStop(0, '#3d6b14');
      capGrad.addColorStop(0.3, '#8fdc4a');
      capGrad.addColorStop(0.7, '#5a9e1f');
      capGrad.addColorStop(1, '#2d5b0e');
    }
    ctx.fillStyle = capGrad;
    ctx.fillRect(p.x - 4, p.topH - 20, PIPE_W + 8, 20);
    ctx.strokeStyle = isGolden ? '#8b6914' : '#2d5b0e';
    ctx.lineWidth = 2;
    ctx.strokeRect(p.x - 4, p.topH - 20, PIPE_W + 8, 20);

    ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.fillRect(p.x + 6, 0, 6, p.topH - 20);

    const botGrad = ctx.createLinearGradient(p.x, 0, p.x + PIPE_W, 0);
    if (isGolden) {
      botGrad.addColorStop(0, '#b8860b');
      botGrad.addColorStop(0.3, '#ffd700');
      botGrad.addColorStop(0.7, '#ffed4e');
      botGrad.addColorStop(1, '#b8860b');
    } else {
      botGrad.addColorStop(0, '#4a8f1e');
      botGrad.addColorStop(0.3, '#8fdc4a');
      botGrad.addColorStop(0.7, '#73bf2e');
      botGrad.addColorStop(1, '#3d6b14');
    }
    ctx.fillStyle = botGrad;
    ctx.fillRect(p.x, p.bottomY, PIPE_W, H - p.bottomY);

    ctx.fillStyle = capGrad;
    ctx.fillRect(p.x - 4, p.bottomY, PIPE_W + 8, 20);
    ctx.strokeStyle = isGolden ? '#8b6914' : '#2d5b0e';
    ctx.strokeRect(p.x - 4, p.bottomY, PIPE_W + 8, 20);

    ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.fillRect(p.x + 6, p.bottomY + 20, 6, H - p.bottomY - 20);
  }

  function drawTrail() {
    for (let t of trail) {
      const alpha = (t.life / t.maxLife) * 0.3;
      ctx.globalAlpha = alpha;
      ctx.fillStyle = '#f7d51d';
      ctx.save();
      ctx.translate(t.x, t.y);
      ctx.rotate(t.rot);
      ctx.beginPath();
      ctx.ellipse(0, 0, bird.w / 2, bird.h / 2, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }
    ctx.globalAlpha = 1;
  }

  function drawBird() {
    if (invincible > 0 && Math.floor(time / 4) % 2 === 0) {
      ctx.globalAlpha = 0.4;
    }
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
    ctx.globalAlpha = 1;
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

    ctx.font = 'bold 14px Courier New';
    ctx.fillStyle = '#fff';
    ctx.textAlign = 'left';
    ctx.fillText(MODES[mode].icon + ' ' + MODES[mode].name, 15, 30);

    if (mode === 'time') {
      ctx.textAlign = 'center';
      ctx.font = 'bold 20px Courier New';
      ctx.fillStyle = timeLeft < 10 ? '#ff4d6d' : '#f7d51d';
      ctx.strokeStyle = '#000';
      ctx.lineWidth = 3;
      ctx.strokeText('⏱ ' + Math.ceil(timeLeft) + 's', W / 2, 130);
      ctx.fillText('⏱ ' + Math.ceil(timeLeft) + 's', W / 2, 130);
    }

    ctx.font = 'bold 20px Courier New';
    ctx.fillStyle = '#ff4d6d';
    ctx.textAlign = 'left';
    for (let i = 0; i < lives; i++) {
      ctx.fillText('♥', 20 + i * 22, 55);
    }

    ctx.textAlign = 'right';
    ctx.font = 'bold 28px Courier New';
    ctx.fillStyle = muted ? '#ff4d6d' : '#fff';
    ctx.fillText(muted ? '🔇' : '🔊', W - 20, 40);

    ctx.textAlign = 'center';
    if (combo >= 2 && comboFlash > 0) {
      ctx.fillStyle = '#f7d51d';
      ctx.font = 'bold 24px Courier New';
      ctx.fillText('x' + combo + ' COMBO!', W / 2, 170);
    }
  }

  function drawMenu() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
    ctx.fillRect(0, 0, W, H);

    ctx.fillStyle = '#f7d51d';
    ctx.strokeStyle = '#000';
    ctx.lineWidth = 6;
    ctx.font = 'bold 42px Courier New';
    ctx.textAlign = 'center';
    ctx.strokeText('FLAPPY', W / 2, 80);
    ctx.fillText('FLAPPY', W / 2, 80);
    ctx.strokeText('BIRD', W / 2, 130);
    ctx.fillText('BIRD', W / 2, 130);

    ctx.fillStyle = '#fff';
    ctx.font = 'bold 18px Courier New';
    ctx.lineWidth = 4;
    ctx.strokeText('Выбери режим', W / 2, 190);
    ctx.fillText('Выбери режим', W / 2, 190);

    const keys = Object.keys(MODES);
    const boxW = 220, boxH = 100;
    const totalW = keys.length * boxW + (keys.length - 1) * 20;
    const startX = (W - totalW) / 2;
    const boxY = H / 2 - boxH / 2 + 40;

    for (let i = 0; i < keys.length; i++) {
      const bx = startX + i * (boxW + 20);
      const isSelected = i === selectedMode;

      ctx.fillStyle = isSelected ? 'rgba(247, 213, 29, 0.9)' : 'rgba(255, 255, 255, 0.15)';
      ctx.strokeStyle = isSelected ? '#f7d51d' : '#fff';
      ctx.lineWidth = isSelected ? 4 : 2;
      ctx.beginPath();
      ctx.roundRect(bx, boxY, boxW, boxH, 12);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = isSelected ? '#000' : '#fff';
      ctx.font = 'bold 32px Courier New';
      ctx.textAlign = 'center';
      ctx.fillText(MODES[keys[i]].icon, bx + boxW / 2, boxY + 42);

      ctx.font = 'bold 14px Courier New';
      ctx.fillText(MODES[keys[i]].name, bx + boxW / 2, boxY + 70);

      ctx.font = '11px Courier New';
      ctx.fillStyle = isSelected ? '#333' : 'rgba(255, 255, 255, 0.7)';
      ctx.fillText(MODES[keys[i]].desc, bx + boxW / 2, boxY + 90);
    }

    ctx.fillStyle = '#fff';
    ctx.font = 'bold 14px Courier New';
    ctx.textAlign = 'center';
    ctx.lineWidth = 3;
    ctx.strokeText('← → выбрать · Space играть', W / 2, H - 80);
    ctx.fillText('← → выбрать · Space играть', W / 2, H - 80);
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
    drawTrail();
    drawBird();
    drawParticles();

    if (state === 'menu') {
      drawMenu();
    } else {
      drawHUD();
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
      ctx.fillText('Space — в меню', W / 2, py + 210);
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