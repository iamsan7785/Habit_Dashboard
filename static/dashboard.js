/* Dashboard data binding and chart rendering for HabitCheck AI */

async function fetchDashboardData() {
  try {
    const res = await fetch('/api/dashboard');
    return await res.json();
  } catch (err) {
    console.error('Dashboard fetch failed', err);
    return { error: err.message || 'Network error' };
  }
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = value ?? '';
}

function setClassByThreshold(id, value, { goodMin = null, warnMin = null, inverse = false } = {}) {
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.remove('highlight-good', 'highlight-warn', 'highlight-risk');

  const num = Number(value);
  if (!Number.isFinite(num)) return;

  let cls = 'highlight-warn';
  if (!inverse) {
    if (goodMin !== null && num >= goodMin) cls = 'highlight-good';
    else if (warnMin !== null && num < warnMin) cls = 'highlight-risk';
  } else {
    if (warnMin !== null && num >= warnMin) cls = 'highlight-risk';
    else if (goodMin !== null && num <= goodMin) cls = 'highlight-good';
  }
  el.classList.add(cls);
}

function setToneByThreshold(cardId, value, { low = 30, high = 70, inverse = false } = {}) {
  const card = document.getElementById(cardId);
  if (!card) return;
  card.classList.remove('tone-good', 'tone-warn', 'tone-risk');

  const num = Number(value);
  if (!Number.isFinite(num)) return;

  let cls = 'tone-warn';
  if (!inverse) {
    if (num >= high) cls = 'tone-good';
    else if (num < low) cls = 'tone-risk';
  } else {
    if (num >= high) cls = 'tone-risk';
    else if (num <= low) cls = 'tone-good';
  }
  card.classList.add(cls);
}

function formatHours(value) {
  const num = Number(value);
  if (!Number.isFinite(num)) return '—';
  return `${num.toFixed(1)} hrs`;
}

function formatSteps(value) {
  const num = Number(value);
  if (!Number.isFinite(num)) return '—';
  return `${Math.round(num).toLocaleString()} steps`;
}

function formatPercent(value) {
  const num = Number(value);
  if (!Number.isFinite(num)) return '—';
  return `${Math.round(num)}%`;
}

function setProgressRing(element, percent) {
  if (!element) return;
  const pct = Math.max(0, Math.min(100, Number(percent) || 0));
  element.style.background = `conic-gradient(var(--cyan) ${pct}%, rgba(255,255,255,0.1) ${pct}% 100%)`;
  element.setAttribute('aria-valuenow', String(pct));
}

function renderList(id, items) {
  const list = document.getElementById(id);
  if (!list) return;
  list.innerHTML = '';
  if (!Array.isArray(items) || items.length === 0) {
    const li = document.createElement('li');
    li.textContent = 'No items to show yet.';
    list.appendChild(li);
    return;
  }
  items.forEach((item) => {
    const li = document.createElement('li');
    li.textContent = item;
    list.appendChild(li);
  });
}

function renderWeeklyAverages(weekly) {
  if (!weekly || !weekly.averages) return;
  setText('weeklyAvgScreen', formatHours(weekly.averages.screen_time));
  setText('weeklyAvgSleep', formatHours(weekly.averages.sleep_hours));
  setText('weeklyAvgSteps', formatSteps(weekly.averages.steps));
  setText('weeklyAvgStress', `${weekly.averages.stress.toFixed(1)}`);
}

function renderChart(canvasId, labels, data, label, color, type = 'line', options = {}) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || typeof Chart === 'undefined') return;

  if (canvas._habitCheckChart) {
    canvas._habitCheckChart.destroy();
  }

  const defaultOpts = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: { grid: { display: false }, ticks: { color: 'rgba(255,255,255,0.7)' } },
      y: {
        grid: { color: 'rgba(255,255,255,0.08)' },
        ticks: { color: 'rgba(255,255,255,0.7)' },
      },
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label(context) {
            const val = context.parsed.y;
            return `${label}: ${val}`;
          },
        },
      },
    },
  };

  canvas._habitCheckChart = new Chart(canvas, {
    type: type,
    data: {
      labels: labels,
      datasets: [
        {
          label: label,
          data: data,
          borderColor: color,
          backgroundColor: color.replace('0.9', '0.18') || 'rgba(0,212,255,0.18)',
          fill: type === 'line',
          tension: 0.35,
          pointRadius: 3,
          pointHoverRadius: 5,
        },
      ],
    },
    options: Object.assign(defaultOpts, options),
  });
}

function renderGroupedBarChart(canvasId, labels, datasets) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || typeof Chart === 'undefined') return;
  if (canvas._habitCheckChart) {
    canvas._habitCheckChart.destroy();
  }
  canvas._habitCheckChart = new Chart(canvas, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: datasets,
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { display: false }, ticks: { color: 'rgba(255,255,255,0.7)' } },
        y: { grid: { color: 'rgba(255,255,255,0.08)' }, ticks: { color: 'rgba(255,255,255,0.7)' } },
      },
      plugins: {
        legend: { position: 'bottom', labels: { color: 'rgba(255,255,255,0.8)' } },
      },
    },
  });
}

function renderDonutChart(canvasId, labels, data, colors) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || typeof Chart === 'undefined') return;
  if (canvas._habitCheckChart) {
    canvas._habitCheckChart.destroy();
  }
  canvas._habitCheckChart = new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{ data: data, backgroundColor: colors }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom', labels: { color: 'rgba(255,255,255,0.8)' } },
        tooltip: {
          callbacks: {
            label(context) {
              const idx = context.dataIndex;
              return `${labels[idx]}: ${data[idx]}`;
            },
          },
        },
      },
    },
  });
}

async function refreshDashboard() {
  const data = await fetchDashboardData();
  if (!data || data.error) {
    setText('wellnessStatus', data?.error || 'Unable to load data');
    return;
  }

  const wellness = data.wellness || {};
  setText('wellnessScore', wellness.score ?? '0');
  setText('wellnessStatus', wellness.status || '—');
  setProgressRing(document.getElementById('wellnessRing'), wellness.score ?? 0);
  setClassByThreshold('wellnessScore', Number(wellness.score), { goodMin: 75, warnMin: 45, inverse: false });
  setToneByThreshold('wellnessCard', Number(wellness.score), { low: 45, high: 75, inverse: false });
  const breakdown = wellness.breakdown || {};
  setText('wellnessBreakdown', `Sleep ${breakdown.sleep_score ?? 0} | Steps ${breakdown.step_score ?? 0} | Screen ${breakdown.screen_score ?? 0} | Stress ${breakdown.stress_score ?? 0}`);

  const future = data.future_prediction || {};
  setText('futureStressLevel', future.stress?.level || '—');
  setText('futureStressProb', future.stress?.probability ? `Confidence: ${formatPercent(future.stress.probability)}` : '');
  setText('futureFocus', Number.isFinite(Number(future.focus?.score)) ? `${Number(future.focus.score).toFixed(1)}` : '—');
  setText('futureSleepRisk', Number.isFinite(Number(future.sleep_quality_risk)) ? formatPercent(future.sleep_quality_risk) : '—');

  const stressLevel = String(future.stress?.level || '').toLowerCase();
  const stressValueEl = document.getElementById('futureStressLevel');
  if (stressValueEl) {
    stressValueEl.classList.remove('highlight-good', 'highlight-warn', 'highlight-risk');
    if (stressLevel.includes('low')) stressValueEl.classList.add('highlight-good');
    else if (stressLevel.includes('high')) stressValueEl.classList.add('highlight-risk');
    else if (stressLevel) stressValueEl.classList.add('highlight-warn');
  }

  const sleepRiskValue = Number(future.sleep_quality_risk);
  setClassByThreshold('futureSleepRisk', sleepRiskValue, { goodMin: 25, warnMin: 65, inverse: true });
  setToneByThreshold('sleepRiskCard', sleepRiskValue, { low: 25, high: 65, inverse: true });

  const personality = data.personality || {};
  setText('personalityType', personality.type || '—');
  setText('personalityDescription', personality.description || '');

  const burnout = data.burnout || {};
  setText('burnoutRisk', Number.isFinite(Number(burnout.risk_percentage)) ? formatPercent(burnout.risk_percentage) : '—');
  setText('burnoutSummary', burnout.summary || '');
  setClassByThreshold('burnoutRisk', Number(burnout.risk_percentage), { goodMin: 25, warnMin: 65, inverse: true });
  setToneByThreshold('burnoutCard', Number(burnout.risk_percentage), { low: 25, high: 65, inverse: true });
  const progressEl = document.getElementById('burnoutProgress');
  if (progressEl) {
    const pct = Math.max(0, Math.min(100, Number(burnout.risk_percentage) || 0));
    progressEl.style.width = `${pct}%`;
  }

  renderList('insightsList', data.insights);
  renderList('patternsList', data.patterns);

  setText('dailySummary', data.daily_summary || '');

  const weekly = data.weekly || {};
  renderWeeklyAverages(weekly);

  // update trend indicators based on first/last values
  function applyTrend(id, arr) {
    const el = document.getElementById(id);
    if (!el) return;
    if (!Array.isArray(arr) || arr.length < 2) {
      el.innerHTML = '';
      return;
    }
    const first = arr[0];
    const last = arr[arr.length - 1];
    let cls = 'trend-flat';
    let icon = 'trending_flat';
    if (last > first) {
      cls = 'trend-up';
      icon = 'trending_up';
    } else if (last < first) {
      cls = 'trend-down';
      icon = 'trending_down';
    }
    el.innerHTML = `<span class="material-icons-round ${cls}">${icon}</span>`;
  }
  applyTrend('trendScreen', weekly.screen_time);
  applyTrend('trendSleep', weekly.sleep_hours);
  applyTrend('trendSteps', weekly.steps);
  applyTrend('trendStress', weekly.stress);

  if (weekly.dates && weekly.dates.length) {
    // individual charts with specified types
    renderChart('weeklyScreenChart', weekly.dates, weekly.screen_time || [], 'Screen time', 'rgba(0, 212, 255, 0.9)', 'bar');
    renderChart('weeklyStepsChart', weekly.dates, weekly.steps || [], 'Steps', 'rgba(52, 211, 153, 0.9)', 'bar');
    renderChart('weeklySleepChart', weekly.dates, weekly.sleep_hours || [], 'Sleep hours', 'rgba(250, 204, 21, 0.9)', 'line');
    renderChart('weeklyStressChart', weekly.dates, weekly.stress || [], 'Stress', 'rgba(251, 113, 133, 0.9)', 'bar');

    // combined grouped bar chart showing all four habits
    renderGroupedBarChart('combinedWeeklyChart', weekly.dates, [
      {
        label: 'Screen time',
        data: weekly.screen_time || [],
        backgroundColor: 'rgba(0, 212, 255, 0.6)',
      },
      {
        label: 'Sleep hours',
        data: weekly.sleep_hours || [],
        backgroundColor: 'rgba(250, 204, 21, 0.6)',
      },
      {
        label: 'Steps',
        data: weekly.steps || [],
        backgroundColor: 'rgba(52, 211, 153, 0.6)',
      },
      {
        label: 'Stress',
        data: weekly.stress || [],
        backgroundColor: 'rgba(251, 113, 133, 0.6)',
      },
    ]);

    // donut for totals
    const totals = weekly.totals || {};
    const donutLabels = ['Screen time', 'Sleep hours', 'Steps'];
    const donutData = [totals.screen_time, totals.sleep_hours, totals.steps];
    renderDonutChart('weeklyDonutChart', donutLabels, donutData, [
      'rgba(0, 212, 255, 0.9)',
      'rgba(250, 204, 21, 0.9)',
      'rgba(52, 211, 153, 0.9)',
    ]);
  }

  // insert weekly AI insight if provided
  setText('weeklyInsight', data.weekly_insight || '');

  // populate comparative highlights if available
  const comp = data.weekly_comparison || {};
  setText('highestScreenDay', comp.highest_screen_day || '–');
  setText('lowestSleepDay', comp.lowest_sleep_day || '–');
  setText('mostActiveDay', comp.most_active_day || '–');
  setText('stressTrend', comp.stress_trend ? comp.stress_trend.charAt(0).toUpperCase() + comp.stress_trend.slice(1) : '–');
}

window.addEventListener('DOMContentLoaded', () => {
  if (document.body.dataset.page !== 'dashboard') return;
  refreshDashboard();
  // refresh every 5 minutes to reflect new incoming data
  setInterval(refreshDashboard, 5 * 60 * 1000);
});
