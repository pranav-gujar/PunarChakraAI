/* PunarChakra AI - Interactive 2D Delta Robot & Conveyor Canvas Visualizer */

document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('deltaCanvas');
  const ctx = canvas.getContext('2d');

  // Telemetry elements
  const teleTh1 = document.getElementById('tele-th1');
  const teleTh2 = document.getElementById('tele-th2');
  const teleTh3 = document.getElementById('tele-th3');
  const teleVac = document.getElementById('tele-vac');
  const streamBody = document.getElementById('stream-table-body');

  const speedSlider = document.getElementById('input-speed');
  const speedVal = document.getElementById('val-speed');
  const btnRunEpisode = document.getElementById('btn-run-episode');
  const btnToggleSim = document.getElementById('btn-toggle-sim');
  const toggleDR = document.getElementById('toggle-dr');

  let isRunning = true;
  let conveyorSpeed = 0.40;
  let items = [];
  let deltaState = {
    x: 0,
    y: 0,
    z: -0.42,
    targetX: 0,
    targetY: 0,
    targetZ: -0.42,
    vacuumActive: false,
    graspedItem: null,
    phase: 'IDLE',
  };

  const materialColors = {
    'PET': '#38bdf8',       // Light Blue
    'HDPE': '#facc15',      // Yellow
    'ALUMINUM': '#e2e8f0',  // Silver
    'CARDBOARD': '#fb923c',  // Orange
    'GLASS': '#4ade80',     // Green
    'EWASTE': '#f43f5e',    // Red
  };

  // Sorting Bins layout on canvas
  const bins = [
    { label: 'PET', color: '#38bdf8', x: 620, y: 70, w: 100, h: 55 },
    { label: 'HDPE', color: '#facc15', x: 620, y: 140, w: 100, h: 55 },
    { label: 'METALS', color: '#e2e8f0', x: 620, y: 210, w: 100, h: 55 },
    { label: 'PAPER', color: '#fb923c', x: 620, y: 280, w: 100, h: 55 },
  ];

  // Fetch initial stream from API
  async function refreshStream() {
    try {
      const res = await fetch('/api/perception/stream?num_items=10');
      if (res.ok) {
        const data = await res.json();
        populateStreamTable(data);
        spawnConveyorItems(data);
      }
    } catch (e) {
      console.warn("Using offline fallback stream", e);
    }
  }

  function populateStreamTable(data) {
    streamBody.innerHTML = '';
    data.forEach(item => {
      const row = document.createElement('tr');
      const matColor = materialColors[item.material] || '#94a3b8';
      row.innerHTML = `
        <td style="font-family: monospace; font-weight: 700;">${item.object_id}</td>
        <td><span style="color: ${matColor}; font-weight: 600;">${item.material}</span></td>
        <td style="font-family: monospace;">${item.spectral_nir_peak_nm.toFixed(0)} nm</td>
        <td><span class="badge ${item.grasp_quality > 0.85 ? 'badge-emerald' : 'badge-cyan'}">${(item.grasp_quality * 100).toFixed(0)}%</span></td>
        <td style="font-size: 0.72rem; color: #94a3b8;">${item.designated_bin.split('_')[2] || item.designated_bin}</td>
      `;
      streamBody.appendChild(row);
    });
  }

  function spawnConveyorItems(data) {
    items = [];
    data.forEach((d, idx) => {
      items.push({
        id: d.object_id,
        material: d.material,
        x: 40 + idx * 75,
        y: 200 + (d.position.x * 250), // Map lateral x to canvas y
        w: 32,
        h: 22,
        picked: false,
        bin: d.designated_bin,
      });
    });
  }

  speedSlider.addEventListener('input', (e) => {
    conveyorSpeed = parseFloat(e.target.value);
    speedVal.textContent = `${conveyorSpeed.toFixed(2)} m/s`;
  });

  btnToggleSim.addEventListener('click', () => {
    isRunning = !isRunning;
    btnToggleSim.textContent = isRunning ? 'Pause Simulation' : 'Resume Simulation';
    btnToggleSim.classList.toggle('btn-primary', !isRunning);
  });

  btnRunEpisode.addEventListener('click', async () => {
    btnRunEpisode.disabled = true;
    btnRunEpisode.textContent = 'Simulating 50 Items...';
    try {
      const res = await fetch(`/api/simulate?num_items=50&conveyor_speed=${conveyorSpeed}&domain_randomization=${toggleDR.checked}`, { method: 'POST' });
      if (res.ok) {
        const ep = await res.json();
        document.getElementById('kpi-pick-rate').textContent = `${ep.pick_success_rate_percent}%`;
        document.getElementById('kpi-throughput').innerHTML = `${ep.throughput_picks_per_min} <span class="kpi-unit">picks/min</span>`;
        document.getElementById('kpi-purity').textContent = `${ep.purity_rate_percent}%`;
        document.getElementById('kpi-cycle-time').innerHTML = `${ep.average_cycle_time_ms} <span class="kpi-unit">ms</span>`;
        refreshStream();
      }
    } catch (e) {
      console.error(e);
    } finally {
      btnRunEpisode.disabled = false;
      btnRunEpisode.textContent = 'Run 50-Item Episode';
    }
  });

  // Main Render Loop
  let lastTime = performance.now();
  function render(now) {
    const dt = (now - lastTime) / 1000.0;
    lastTime = now;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 1. Draw Conveyor Belt (Horizontal belt running across left-to-middle)
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(20, 140, 560, 140);
    ctx.strokeStyle = '#334155';
    ctx.lineWidth = 2;
    ctx.strokeRect(20, 140, 560, 140);

    // Conveyor rollers lines
    ctx.strokeStyle = '#1e293b';
    ctx.lineWidth = 1;
    const rollerOffset = (now * conveyorSpeed * 0.1) % 30;
    for (let rx = 20 + rollerOffset; rx < 580; rx += 30) {
      ctx.beginPath();
      ctx.moveTo(rx, 140);
      ctx.lineTo(rx, 280);
      ctx.stroke();
    }

    // 2. Draw Sorting Bins
    bins.forEach(bin => {
      ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
      ctx.fillRect(bin.x, bin.y, bin.w, bin.h);
      ctx.strokeStyle = bin.color;
      ctx.lineWidth = 2;
      ctx.strokeRect(bin.x, bin.y, bin.w, bin.h);

      ctx.fillStyle = bin.color;
      ctx.font = 'bold 11px JetBrains Mono';
      ctx.fillText(bin.label, bin.x + 10, bin.y + 22);

      ctx.fillStyle = '#94a3b8';
      ctx.font = '9px Plus Jakarta Sans';
      ctx.fillText('RECYCLE BIN', bin.x + 10, bin.y + 40);
    });

    // 3. Update & Draw Items on Conveyor
    if (isRunning) {
      items.forEach(item => {
        if (!item.picked) {
          item.x += conveyorSpeed * dt * 140;
        }
      });
      // Respawn when items exit right
      items = items.filter(item => item.x < 600 || item.picked);
      if (items.length < 5) {
        refreshStream();
      }
    }

    items.forEach(item => {
      if (!item.picked) {
        ctx.fillStyle = materialColors[item.material] || '#94a3b8';
        ctx.beginPath();
        ctx.roundRect(item.x, item.y, item.w, item.h, 4);
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1;
        ctx.stroke();

        ctx.fillStyle = '#000000';
        ctx.font = 'bold 9px JetBrains Mono';
        ctx.fillText(item.material.substring(0, 3), item.x + 4, item.y + 14);
      }
    });

    // 4. Simulate Delta Robot Pick & Place Motion
    const deltaBaseX = 380;
    const deltaBaseY = 210;

    // Target nearest unpicked item near delta workspace center
    const targetItem = items.find(it => !it.picked && it.x > 300 && it.x < 460);
    if (targetItem && deltaState.phase === 'IDLE') {
      deltaState.phase = 'APPROACH';
      deltaState.targetX = targetItem.x + 15;
      deltaState.targetY = targetItem.y + 10;
      deltaState.graspedItem = targetItem;
    }

    // Step Delta End Effector
    const dx = deltaState.targetX - deltaBaseX;
    const dy = deltaState.targetY - deltaBaseY;
    const speed = 12.0;

    if (deltaState.phase === 'APPROACH') {
      deltaState.x += (deltaState.targetX - deltaState.x) * dt * speed;
      deltaState.y += (deltaState.targetY - deltaState.y) * dt * speed;
      if (Math.hypot(deltaState.targetX - deltaState.x, deltaState.targetY - deltaState.y) < 8) {
        deltaState.phase = 'GRASP';
        deltaState.vacuumActive = true;
      }
    } else if (deltaState.phase === 'GRASP') {
      if (deltaState.graspedItem) {
        deltaState.graspedItem.picked = true;
      }
      // Steer to appropriate bin
      const targetBin = bins.find(b => deltaState.graspedItem && deltaState.graspedItem.bin.includes(b.label)) || bins[0];
      deltaState.targetX = targetBin.x + 30;
      deltaState.targetY = targetBin.y + 25;
      deltaState.phase = 'TRANSFER';
    } else if (deltaState.phase === 'TRANSFER') {
      deltaState.x += (deltaState.targetX - deltaState.x) * dt * speed;
      deltaState.y += (deltaState.targetY - deltaState.y) * dt * speed;
      if (Math.hypot(deltaState.targetX - deltaState.x, deltaState.targetY - deltaState.y) < 10) {
        deltaState.phase = 'RELEASE';
        deltaState.vacuumActive = false;
      }
    } else if (deltaState.phase === 'RELEASE') {
      deltaState.targetX = deltaBaseX;
      deltaState.targetY = deltaBaseY;
      deltaState.phase = 'RETURN';
    } else if (deltaState.phase === 'RETURN') {
      deltaState.x += (deltaBaseX - deltaState.x) * dt * speed;
      deltaState.y += (deltaBaseY - deltaState.y) * dt * speed;
      if (Math.hypot(deltaBaseX - deltaState.x, deltaBaseY - deltaState.y) < 8) {
        deltaState.phase = 'IDLE';
        deltaState.graspedItem = null;
      }
    } else {
      deltaState.x = deltaBaseX;
      deltaState.y = deltaBaseY;
    }

    // 5. Draw 3 Delta Arms
    const eeX = deltaState.x;
    const eeY = deltaState.y;

    // Draw Fixed Base Platform Triangle
    ctx.fillStyle = 'rgba(6, 182, 212, 0.2)';
    ctx.strokeStyle = '#06b6d4';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(deltaBaseX, deltaBaseY, 70, 0, Math.PI * 2);
    ctx.stroke();

    const motorAngles = [0, (2 * Math.PI) / 3, (4 * Math.PI) / 3];
    motorAngles.forEach((ang, idx) => {
      const mx = deltaBaseX + Math.cos(ang) * 65;
      const my = deltaBaseY + Math.sin(ang) * 65;

      // Upper arm link (Bicep)
      const elbowX = mx + Math.cos(ang) * 35;
      const elbowY = my + Math.sin(ang) * 35;

      ctx.strokeStyle = '#0284c7';
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.moveTo(mx, my);
      ctx.lineTo(elbowX, elbowY);
      ctx.stroke();

      // Lower parallelogram rods (Forearm)
      ctx.strokeStyle = '#94a3b8';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(elbowX - 4, elbowY - 4);
      ctx.lineTo(eeX - 4, eeY - 4);
      ctx.moveTo(elbowX + 4, elbowY + 4);
      ctx.lineTo(eeX + 4, eeY + 4);
      ctx.stroke();

      // Motor Joint Node
      ctx.fillStyle = '#06b6d4';
      ctx.beginPath();
      ctx.arc(mx, my, 6, 0, Math.PI * 2);
      ctx.fill();
    });

    // Draw Moving End-Effector Platform & Suction Cup
    ctx.fillStyle = deltaState.vacuumActive ? '#10b981' : '#f59e0b';
    ctx.beginPath();
    ctx.arc(eeX, eeY, 12, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Telemetry updates
    const th1Val = (25 + Math.sin(now * 0.005) * 12).toFixed(1);
    const th2Val = (20 + Math.cos(now * 0.004) * 10).toFixed(1);
    const th3Val = (28 - Math.sin(now * 0.006) * 14).toFixed(1);
    teleTh1.textContent = `${th1Val}°`;
    teleTh2.textContent = `${th2Val}°`;
    teleTh3.textContent = `${th3Val}°`;
    teleVac.textContent = deltaState.vacuumActive ? 'P = -82.4 kPa (SEALED)' : 'P = 0.0 kPa (IDLE)';
    teleVac.className = deltaState.vacuumActive ? 'text-emerald' : 'text-muted';

    requestAnimationFrame(render);
  }

  refreshStream();
  requestAnimationFrame(render);
});
