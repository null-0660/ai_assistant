// Flappy Bird — v14: Монеты, Магазин и Скины

(function () {
  'use strict';

  const canvas = document.getElementById('game');
  const ctx = canvas.getContext('2d');
  const W = canvas.width;
  const H = canvas.height;

  const GRAVITY = 0.28;
  const JUMP = -5.5;
  const MAX_FALL = 8;
  const PIPE_W = 60;
  const PIPE_GAP = 150;
  const BASE_SPEED = 2.0;
  const PIPE_SPAWN = 110;
  const GROUND_H = 60;

  const bird = { x: 80, y: H / 2, w: 34, h: 24, vy: 0, rot: 0 };
  let pipes = [];
  let coins = [];
  let clouds = [];
  let particles = [];
  let frame = 0;
  let score = 0;
  let best = parseInt(localStorage.getItem('flappyBest') || '0', 10);
  let state = 'ready'; // ready | playing | gameover | shop
  let groundOffset = 0;
  let shake = 0;
  let time = 0;

  let audioCtx = null;
  let muted = localStorage.getItem('flappyMuted') === 'true';

  function initAudio() {
    try {
      if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      if (audioCtx.state === 'suspended') audioCtx.resume();
    } catch (e) {}
  }

  function beep(freq, dur, vol = 0.05) {
    if (muted || !audioCtx) return;
    try {
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'square';
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(vol, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + dur);
      osc.connect(gain); gain.connect(audioCtx.destination);
      osc.start(); osc.stop(audioCtx.currentTime + dur);
    } catch (e) {}
  }

  function spawnParticles(x, y, color, count) {
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 1 + Math.random() * 4;
      particles.push({
        x, y, vx: Math.cos(angle) * speed, vy: Math.sin(angle) * speed - 1,
        color, life: 30, maxLife: 30, size: 2 + Math.random() * 4
      });
    }
  }

  function updateParticles() {
    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i];
      p.x += p.vx; p.y += p.vy; p.vy += 0.2; p.vx *= 0.95; p.life--;
      if (p.life <= 0) particles.splice(i, 1);
    }
  }

  function drawParticles() {
    for (let p of particles) {
      ctx.globalAlpha = p.life / p.maxLife;
      ctx.fillStyle = p.color;
      ctx.beginPath(); ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2); ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  function createClouds() {
    clouds = [];
    for (let i = 0; i < 4; i++) {
      clouds.push({ x: Math.random() * W, y: 40 + Math.random() * 150, size: 30 + Math.random() * 40, speed: 0.2 + Math.random() * 0.3 });
    }
  }

  function spawnPipe() {
    const minTop = 60;
    const maxTop = H - GROUND_H - PIPE_GAP - 60;
    const topH = minTop + Math.random() * (maxTop - minTop);
    
    // Шанс 30% заспавнить монету в проеме между трубами
    if (Math.random() < 0.3) {
      const coinY = topH + PIPE_GAP / 2;
      coins.push({ x: W + PIPE_W / 2, y: coinY, collected: false });
    }

    pipes.push({ x: W, topH, bottomY: topH + PIPE_GAP, scored: false });
  }

  function resetGame() {
    bird.y = H / 2; bird.vy = 0; bird.rot = 0;
    pipes = []; coins = []; particles = [];
    frame = 0; score = 0; state = 'ready';
    shake = 0; createClouds();
  }

  function jump() {
    if (state === 'shop') return; // В магазине не прыгаем
    
    initAudio();
    if (state === 'ready') {
      state = 'playing'; bird.vy = JUMP; beep(600, 0.08);
    } else if (state === 'playing') {
      bird.vy = JUMP; beep(600, 0.08);
    } else if (state === 'gameover') {
      resetGame(); state = 'playing'; bird.vy = JUMP; beep(600, 0.08);
    }
  }

  document.addEventListener('keydown', (e) => {
    if (e.code === 'Space' || e.code === 'ArrowUp') { e.preventDefault(); jump(); }
    if (e.code === 'KeyM') { muted = !muted; localStorage.setItem('flappyMuted', muted); }
  });

  canvas.addEventListener('click', (e) => {
    const rect = canvas.getBoundingClientRect();
    const mx = (e.clientX - rect.left) * (W / rect.width);
    const my = (e.clientY - rect.top) * (H / rect.height);

    // Кнопка звука
    if (mx > W - 50 && my < 50) { muted = !muted; localStorage.setItem('flappyMuted', muted); return; }

    // Меню (Главный экран)
    if (state === 'ready' && my > H/2 + 80 && my < H/2 + 130 && mx > W/2 - 60 && mx < W/2 + 60) {
      state = 'shop'; return;
    }
    if (state === 'ready' && my > H/2 + 140 && my < H/2 + 190 && mx > W/2 - 60 && mx < W/2 + 60) {
      resetGame(); return;
    }

    // Магазин (Клик по скинам)
    if (state === 'shop') {
      const skinsArr = Object.keys(Shop.skins);
      const boxW = 150, boxH = 60;
      const startY = 150;
      
      // Кнопка "Назад"
      if (mx > W/2 - 60 && mx < W/2 + 60 && my > H - 80 && my < H - 40) {
        state = 'ready'; return;
      }

      // Покупка
      for (let i = 0; i < skinsArr.length; i++) {
        const bx = W/2 - boxW/2;
        const by = startY + i * (boxH + 15);
        if (mx > bx && mx < bx + boxW && my > by && my < by + boxH) {
          const id = skinsArr[i];
          if (Shop.currentSkin === id) return; // Уже надет
          
          const isBought = Shop.currentSkin === id || parseInt(localStorage.getItem('skin_'+id) || '0');
          if (isBought) {
            Shop.currentSkin = id; localStorage.setItem('flappySkin', id); beep(800, 0.1);
          } else {
            if (Shop.buySkin(id)) {
              localStorage.setItem('skin_'+id, '1');
              beep(1200, 0.2); // Звук покупки
            } else {
              beep(200, 0.2); // Не хватает денег
            }
          }
          return;
        }
      }
      return;
    }

    jump();
  });

  function collides(px, py, pw, ph, rx, ry, rw, rh) {
    return px < rx + rw && px + pw > rx && py < ry + rh && py + ph > ry;
  }

  function update() {
    time++;
    updateParticles();

    for (let c of clouds) {
      c.x -= c.speed;
      if (c.x + c.size < 0) { c.x = W + c.size; c.y = 40 + Math.random() * 150; }
    }

    if (state !== 'playing') return;

    bird.vy = Math.min(bird.vy + GRAVITY, MAX_FALL);
    bird.y += bird.vy;
    bird.rot = Math.max(-0.4, Math.min(1.2, bird.vy * 0.1));

    if (bird.y - bird.h / 2 < 0) { bird.y = bird.h / 2; bird.vy = 0; }
    
    if (bird.y + bird.h / 2 > H - GROUND_H) {
      bird.y = H - GROUND_H - bird.h / 2;
      endGame(); return;
    }

    groundOffset = (groundOffset + BASE_SPEED) % 40;
    frame++;
    if (frame % PIPE_SPAWN === 0) spawnPipe();

    const bx = bird.x - bird.w / 2 + 4;
    const by = bird.y - bird.h / 2 + 4;
    const bw = bird.w - 8;
    const bh = bird.h - 8;

    // Столкновение с трубами
    for (let p of pipes) {
      p.x -= BASE_SPEED;
      if (collides(bx, by, bw, bh, p.x, 0, PIPE_W, p.topH) ||
          collides(bx, by, bw, bh, p.x, p.bottomY, PIPE_W, H - p.bottomY)) {
        endGame(); return;
      }
      if (!p.scored && p.x + PIPE_W < bird.x) {
        p.scored = true; score++; beep(900, 0.1);
        if (score > best) { best = score; localStorage.setItem('flappyBest', best); }
      }
    }

    // Столкновение с монетами
    for (let c of coins) {
      c.x -= BASE_SPEED;
      if (!c.collected && collides(bx, by, bw, bh, c.x - 10, c.y - 10, 20, 20)) {
        c.collected = true;
        Shop.addCoin();
        beep(1500, 0.1); // Звук монетки
        spawnParticles(c.x, c.y, '#ffd700', 10);
      }
    }

    pipes = pipes.filter((p) => p.x + PIPE_W > 0);
    coins = coins.filter((c) => c.x > -20 && !c.collected);

    if (shake > 0) shake -= 1;
  }

  function endGame() {
    if (state === 'gameover') return;
    state = 'gameover'; shake = 12;
    spawnParticles(bird.x, bird.y, Shop.skins[Shop.currentSkin].color, 25);
    beep(200, 0.3, 0.08);
  }

  function drawCloud(c) {
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.beginPath();
    ctx.arc(c.x, c.y, c.size * 0.6, 0, Math.PI * 2);
    ctx.arc(c.x + c.size * 0.5, c.y, c.size * 0.5, 0, Math.PI * 2);
    ctx.arc(c.x - c.size * 0.5, c.y, c.size * 0.5, 0, Math.PI * 2);
    ctx.fill();
  }

  function drawPipe(p) {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
    ctx.fillRect(p.x + 4, 0, PIPE_W, p.topH);
    ctx.fillRect(p.x + 4, p.bottomY, PIPE_W, H - p.bottomY);

    const grad = ctx.createLinearGradient(p.x, 0, p.x + PIPE_W, 0);
    grad.addColorStop(0, '#4a8f1e'); grad.addColorStop(0.3, '#8fdc4a'); grad.addColorStop(0.7, '#73bf2e'); grad.addColorStop(1, '#3d6b14');
    ctx.fillStyle = grad;
    ctx.fillRect(p.x, 0, PIPE_W, p.topH);
    ctx.fillRect(p.x, p.bottomY, PIPE_W, H - p.bottomY);

    ctx.fillStyle = '#5a9e1f';
    ctx.fillRect(p.x - 4, p.topH - 20, PIPE_W + 8, 20);
    ctx.strokeStyle = '#2d5b0e'; ctx.lineWidth = 2;
    ctx.strokeRect(p.x - 4, p.topH - 20, PIPE_W + 8, 20);

    ctx.fillStyle = '#5a9e1f';
    ctx.fillRect(p.x - 4, p.bottomY, PIPE_W + 8, 20);
    ctx.strokeRect(p.x - 4, p.bottomY, PIPE_W + 8, 20);

    ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.fillRect(p.x + 4, 0, 6, p.topH - 20);
    ctx.fillRect(p.x + 4, p.bottomY + 20, 6, H - p.bottomY - 20);
  }

  function drawBird() {
    const skin = Shop.skins[Shop.currentSkin];
    ctx.save();
    ctx.translate(bird.x, bird.y); ctx.rotate(bird.rot);

    ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
    ctx.beginPath(); ctx.ellipse(3, 3, bird.w / 2, bird.h / 2, 0, 0, Math.PI * 2); ctx.fill();

    // Тело (цвет из скина)
    ctx.fillStyle = skin.color;
    ctx.beginPath(); ctx.ellipse(0, 0, bird.w / 2, bird.h / 2, 0, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = '#333'; ctx.lineWidth = 2; ctx.stroke();

    // Крыло
    const wing = state === 'playing' ? Math.sin(frame * 0.3) * 0.4 : 0;
    ctx.save(); ctx.translate(-4, 0); ctx.rotate(wing);
    ctx.fillStyle = 'rgba(0,0,0,0.2)';
    ctx.beginPath(); ctx.ellipse(0, 0, 10, 6, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
    ctx.restore();

    // Глаз
    ctx.fillStyle = skin.eye; ctx.beginPath(); ctx.arc(8, -5, 5, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
    ctx.fillStyle = '#000'; ctx.beginPath(); ctx.arc(9, -5, 2, 0, Math.PI * 2); ctx.fill();

    // Клюв
    ctx.fillStyle = '#f39c12'; ctx.beginPath(); ctx.moveTo(14, 0); ctx.lineTo(22, 3); ctx.lineTo(14, 6); ctx.closePath(); ctx.fill();

    ctx.restore();
  }

  function drawGround() {
    ctx.fillStyle = '#ded895'; ctx.fillRect(0, H - GROUND_H, W, GROUND_H);
    ctx.fillStyle = '#73bf2e'; ctx.fillRect(0, H - GROUND_H, W, 8);
    ctx.fillStyle = '#c9c06a';
    for (let x = -groundOffset; x < W; x += 20) {
      ctx.fillRect(x, H - GROUND_H + 12, 10, 4);
      ctx.fillRect(x + 10, H - GROUND_H + 20, 10, 4);
    }
  }

  function drawCoin(x, y) {
    // Вращающаяся монета
    const scaleX = Math.cos(time * 0.1);
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(scaleX, 1);
    ctx.fillStyle = '#ffd700';
    ctx.beginPath(); ctx.arc(0, 0, 10, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = '#b8860b'; ctx.lineWidth = 2; ctx.stroke();
    ctx.fillStyle = '#fff';
    ctx.beginPath(); ctx.arc(0, 0, 4, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  }

  function drawHUD() {
    ctx.fillStyle = '#fff'; ctx.strokeStyle = '#000'; ctx.lineWidth = 4;
    ctx.font = 'bold 48px Courier New'; ctx.textAlign = 'center';
    ctx.strokeText(score, W / 2, 70); ctx.fillText(score, W / 2, 70);

    ctx.font = 'bold 16px Courier New'; ctx.lineWidth = 3;
    ctx.strokeText('Рекорд: ' + best, W / 2, 100); ctx.fillText('Рекорд: ' + best, W / 2, 100);

    // Баланс монет
    ctx.textAlign = 'left'; ctx.font = 'bold 20px Courier New';
    ctx.fillStyle = '#ffd700'; ctx.strokeStyle = '#000'; ctx.lineWidth = 3;
    ctx.strokeText('🪙 ' + Shop.coins, 20, 40); ctx.fillText('🪙 ' + Shop.coins, 20, 40);

    // Кнопка Mute
    ctx.textAlign = 'right'; ctx.font = 'bold 24px Courier New';
    ctx.fillStyle = muted ? '#ff4d6d' : '#fff';
    ctx.fillText(muted ? '🔇' : '🔊', W - 20, 40);
  }

  function drawMenu() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)'; ctx.fillRect(0, 0, W, H);
    
    ctx.fillStyle = '#f7d51d'; ctx.strokeStyle = '#000'; ctx.lineWidth = 6;
    ctx.font = 'bold 42px Courier New'; ctx.textAlign = 'center';
    ctx.strokeText('FLAPPY', W / 2, H / 2 - 80); ctx.fillText('FLAPPY', W / 2, H / 2 - 80);
    ctx.strokeText('BIRD', W / 2, H / 2 - 30); ctx.fillText('BIRD', W / 2, H / 2 - 30);

    // Кнопка ИГРАТЬ
    ctx.fillStyle = '#73bf2e'; ctx.strokeStyle = '#3d6b14'; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.roundRect(W/2 - 60, H/2 + 80, 120, 40, 10); ctx.fill(); ctx.stroke();
    ctx.fillStyle = '#fff'; ctx.font = 'bold 20px Courier New';
    ctx.fillText('ИГРАТЬ', W / 2, H/2 + 107);

    // Кнопка МАГАЗИН
    ctx.fillStyle = '#ffd700'; ctx.strokeStyle = '#b8860b'; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.roundRect(W/2 - 60, H/2 + 140, 120, 40, 10); ctx.fill(); ctx.stroke();
    ctx.fillStyle = '#333'; ctx.font = 'bold 20px Courier New';
    ctx.fillText('МАГАЗИН', W / 2, H/2 + 167);

    ctx.fillStyle = '#fff'; ctx.font = 'bold 14px Courier New'; ctx.lineWidth = 3;
    ctx.strokeText('Space / Клик — играть', W / 2, H - 40); ctx.fillText('Space / Клик — играть', W / 2, H - 40);
  }

  function drawShop() {
    ctx.fillStyle = 'rgba(15, 20, 30, 0.95)'; ctx.fillRect(0, 0, W, H);

    ctx.fillStyle = '#f7d51d'; ctx.strokeStyle = '#000'; ctx.lineWidth = 5;
    ctx.font = 'bold 32px Courier New'; ctx.textAlign = 'center';
    ctx.strokeText('МАГАЗИН', W / 2, 70); ctx.fillText('МАГАЗИН', W / 2, 70);

    // Баланс
    ctx.font = 'bold 24px Courier New'; ctx.fillStyle = '#ffd700';
    ctx.strokeText('🪙 ' + Shop.coins, W / 2, 110); ctx.fillText('🪙 ' + Shop.coins, W / 2, 110);

    const skinsArr = Object.keys(Shop.skins);
    const boxW = 150, boxH = 60;
    const startY = 150;

    for (let i = 0; i < skinsArr.length; i++) {
      const id = skinsArr[i];
      const skin = Shop.skins[id];
      const bx = W/2 - boxW/2;
      const by = startY + i * (boxH + 15);
      
      const isSelected = Shop.currentSkin === id;
      const isBought = isSelected || parseInt(localStorage.getItem('skin_'+id) || '0');

      // Фон карточки
      ctx.fillStyle = isSelected ? 'rgba(115, 191, 46, 0.8)' : (isBought ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.5)');
      ctx.strokeStyle = isSelected ? '#fff' : '#555';
      ctx.lineWidth = 2;
      ctx.beginPath(); ctx.roundRect(bx, by, boxW, boxH, 8); ctx.fill(); ctx.stroke();

      // Превью птицы
      ctx.fillStyle = skin.color;
      ctx.beginPath(); ctx.ellipse(bx + 30, by + boxH/2, 15, 11, 0, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = '#333'; ctx.stroke();
      ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(bx + 35, by + boxH/2 - 3, 4, 0, Math.PI*2); ctx.fill();
      ctx.fillStyle = '#000'; ctx.beginPath(); ctx.arc(bx + 36, by + boxH/2 - 3, 1.5, 0, Math.PI*2); ctx.fill();

      // Название
      ctx.fillStyle = '#fff'; ctx.font = 'bold 16px Courier New'; ctx.textAlign = 'left';
      ctx.fillText(skin.name, bx + 60, by + 25);

      // Цена или Статус
      ctx.font = 'bold 14px Courier New';
      if (isSelected) {
        ctx.fillStyle = '#73bf2e'; ctx.fillText('НАДЕТО', bx + 60, by + 45);
      } else if (isBought) {
        ctx.fillStyle = '#fff'; ctx.fillText('КУПЛЕНО', bx + 60, by + 45);
      } else {
        ctx.fillStyle = '#ffd700'; ctx.fillText('🪙 ' + skin.price, bx + 60, by + 45);
      }
    }

    // Кнопка Назад
    ctx.fillStyle = '#ff4d4d'; ctx.strokeStyle = '#b30000'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.roundRect(W/2 - 60, H - 80, 120, 40, 8); ctx.fill(); ctx.stroke();
    ctx.fillStyle = '#fff'; ctx.font = 'bold 18px Courier New'; ctx.textAlign = 'center';
    ctx.fillText('НАЗАД', W / 2, H - 54);
  }

  function draw() {
    ctx.save();
    if (shake > 0) ctx.translate((Math.random() - 0.5) * shake, (Math.random() - 0.5) * shake);

    // Небо
    const sky = ctx.createLinearGradient(0, 0, 0, H);
    sky.addColorStop(0, '#4ec0ca'); sky.addColorStop(1, '#8fd8e0');
    ctx.fillStyle = sky; ctx.fillRect(0, 0, W, H);

    for (let c of clouds) drawCloud(c);
    for (let p of pipes) drawPipe(p);
    for (let c of coins) if (!c.collected) drawCoin(c.x, c.y);
    
    drawGround();
    drawBird();
    drawParticles();

    if (state === 'playing' || state === 'gameover') drawHUD();
    if (state === 'ready') drawMenu();
    if (state === 'shop') drawShop();

    if (state === 'gameover') {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.6)'; ctx.fillRect(0, 0, W, H);
      const pw = 260, ph = 220;
      const px = (W - pw) / 2, py = (H - ph) / 2;
      ctx.fillStyle = '#ded895'; ctx.strokeStyle = '#3d6b14'; ctx.lineWidth = 4;
      ctx.fillRect(px, py, pw, ph); ctx.strokeRect(px, py, pw, ph);

      ctx.fillStyle = '#3d6b14'; ctx.font = 'bold 28px Courier New'; ctx.textAlign = 'center';
      ctx.fillText('GAME OVER', W / 2, py + 45);
      ctx.fillStyle = '#333'; ctx.font = 'bold 20px Courier New';
      ctx.fillText('Счёт: ' + score, W / 2, py + 90);
      ctx.fillStyle = '#c9a227'; ctx.font = 'bold 16px Courier New';
      ctx.fillText('Рекорд: ' + best, W / 2, py + 130);
      ctx.fillStyle = '#4ec0ca'; ctx.font = 'bold 16px Courier New';
      ctx.fillText('Space — заново', W / 2, py + 180);
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