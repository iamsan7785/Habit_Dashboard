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
  const hasAnySeries = Array.isArray(weekly?.screen_time)
    || Array.isArray(weekly?.sleep_hours)
    || Array.isArray(weekly?.steps)
    || Array.isArray(weekly?.stress);

  if (!weekly || !hasAnySeries) {
    setText('weeklyAvgScreen', 'Not enough data');
    setText('weeklyAvgSleep', 'Not enough data');
    setText('weeklyAvgSteps', 'Not enough data');
    setText('weeklyAvgStress', 'Not enough data');
    return;
  }

  const screenHoursSeries = Array.isArray(weekly.screen_time)
    ? weekly.screen_time
        .map((value) => normalizeRawTimeToHours(value))
        .filter((value) => value !== null && value >= 0 && value <= MAX_DAY_HOURS)
    : [];

  const sleepHoursSeries = Array.isArray(weekly.sleep_hours)
    ? weekly.sleep_hours
        .map((value) => normalizeRawTimeToHours(value))
        .filter((value) => value !== null && value >= 0 && value <= MAX_DAY_HOURS)
    : [];

  const stepsSeries = Array.isArray(weekly.steps)
    ? weekly.steps
        .map((value) => toFiniteNumber(value))
        .filter((value) => value !== null && value >= 0)
    : [];

  const stressSeries = Array.isArray(weekly.stress)
    ? weekly.stress
        .map((value) => toFiniteNumber(value))
        .filter((value) => value !== null)
    : [];

  const strictWeeklyAverage = (values) => {
    if (!values.length) return null;
    const total = values.reduce((sum, value) => sum + value, 0);
    return total / 7;
  };

  const avgScreenHours = strictWeeklyAverage(screenHoursSeries);
  const avgSleepHours = strictWeeklyAverage(sleepHoursSeries);
  const avgSteps = strictWeeklyAverage(stepsSeries);
  const avgStress = strictWeeklyAverage(stressSeries);

  setText('weeklyAvgScreen', avgScreenHours === null ? 'Not enough data' : `${roundToOne(clamp(avgScreenHours, 0, MAX_DAY_HOURS)).toFixed(1)} hrs`);
  setText('weeklyAvgSleep', avgSleepHours === null ? 'Not enough data' : `${roundToOne(avgSleepHours).toFixed(1)} hrs`);
  setText('weeklyAvgSteps', avgSteps === null ? 'Not enough data' : `${Math.round(avgSteps).toLocaleString()} steps`);
  setText('weeklyAvgStress', avgStress === null ? 'Not enough data' : roundToOne(avgStress).toFixed(1));
}

function toReadableTrend(trend) {
  if (!trend || typeof trend !== 'string') return '—';
  return trend.charAt(0).toUpperCase() + trend.slice(1);
}

function renderWeeklyComparisonCards(weeklyComparison) {
  const comparison = weeklyComparison || {};
  setText('highestScreenDay', comparison.highest_screen_day || '—');
  setText('lowestSleepDay', comparison.lowest_sleep_day || '—');
  setText('mostActiveDay', comparison.most_active_day || '—');
  setText('stressTrendSummary', toReadableTrend(comparison.stress_trend));
}

function formatWeekdayLabels(dates) {
  if (!Array.isArray(dates)) return [];
  return dates.map((date) => {
    if (typeof date !== 'string' || !date) return '—';
    const parsed = new Date(date);
    if (Number.isNaN(parsed.getTime())) return date;
    return parsed.toLocaleDateString(undefined, { weekday: 'short' });
  });
}

const MAX_DAY_HOURS = 24;
const MAX_DAY_MINUTES = 24 * 60;
let latestDashboardPayload = null;

function toFiniteNumber(value) {
  const num = Number(value);
  return Number.isFinite(num) ? num : null;
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function roundToOne(value) {
  return Math.round(value * 10) / 10;
}

function normalizeRawTimeToHours(value) {
  const numeric = toFiniteNumber(value);
  if (numeric === null || numeric < 0) return null;
  if (numeric > MAX_DAY_MINUTES) return null;
  if (numeric > MAX_DAY_HOURS) return numeric / 60;
  return numeric;
}

function normalizeRawTimeToMinutes(value) {
  const numeric = toFiniteNumber(value);
  if (numeric === null || numeric < 0) return null;
  if (numeric > MAX_DAY_MINUTES) return null;
  if (numeric > MAX_DAY_HOURS) return numeric;
  return numeric * 60;
}

function toValidHours(value, { assumeMinutes = false } = {}) {
  const numeric = toFiniteNumber(value);
  if (numeric === null || numeric < 0) return null;

  let hours;
  if (assumeMinutes || numeric > MAX_DAY_HOURS) {
    if (numeric > MAX_DAY_MINUTES) return null;
    hours = numeric / 60;
  } else {
    hours = numeric;
  }

  if (hours < 0 || hours > MAX_DAY_HOURS) return null;
  return roundToOne(clamp(hours, 0, MAX_DAY_HOURS));
}

function toValidSteps(value) {
  const numeric = toFiniteNumber(value);
  if (numeric === null || numeric < 0) return null;
  return Math.round(numeric);
}

function trendDirection(values) {
  if (!Array.isArray(values) || values.length < 2) return 'stable';
  const first = toFiniteNumber(values[0]);
  const last = toFiniteNumber(values[values.length - 1]);
  if (first === null || last === null) return 'stable';
  if (last > first) return 'increased';
  if (last < first) return 'decreased';
  return 'stable';
}

function average(values) {
  if (!Array.isArray(values) || !values.length) return null;
  const cleaned = values.map((v) => toFiniteNumber(v)).filter((v) => v !== null);
  if (!cleaned.length) return null;
  return cleaned.reduce((sum, v) => sum + v, 0) / cleaned.length;
}

function findIndexOfMax(values) {
  if (!Array.isArray(values) || !values.length) return -1;
  let maxIndex = -1;
  let maxValue = -Infinity;
  values.forEach((value, index) => {
    const numeric = toFiniteNumber(value);
    if (numeric === null) return;
    if (numeric > maxValue) {
      maxValue = numeric;
      maxIndex = index;
    }
  });
  return maxIndex;
}

function findIndexOfMin(values) {
  if (!Array.isArray(values) || !values.length) return -1;
  let minIndex = -1;
  let minValue = Infinity;
  values.forEach((value, index) => {
    const numeric = toFiniteNumber(value);
    if (numeric === null) return;
    if (numeric < minValue) {
      minValue = numeric;
      minIndex = index;
    }
  });
  return minIndex;
}

function toWeekdayLabelAtIndex(dates, index) {
  if (!Array.isArray(dates) || index < 0 || index >= dates.length) return 'N/A';
  const labels = formatWeekdayLabels(dates);
  return labels[index] || 'N/A';
}

function getLiveInputValue(nameOrId) {
  const byName = document.querySelector(`input[name='${nameOrId}']`);
  const byId = document.getElementById(nameOrId);
  const input = byName || byId;
  if (!input) return null;
  return toFiniteNumber(input.value);
}

function getCurrentSummaryData(weekly) {
  const weeklyScreen = Array.isArray(weekly?.screen_time) ? weekly.screen_time : [];
  const weeklySleep = Array.isArray(weekly?.sleep_hours) ? weekly.sleep_hours : [];
  const weeklySteps = Array.isArray(weekly?.steps) ? weekly.steps : [];
  const weeklyStress = Array.isArray(weekly?.stress) ? weekly.stress : [];

  const fallbackScreenRaw = weeklyScreen.length ? toFiniteNumber(weeklyScreen[weeklyScreen.length - 1]) : null;
  const fallbackScreenMinutes = normalizeRawTimeToMinutes(fallbackScreenRaw);
  const fallbackSleepHours = weeklySleep.length ? toFiniteNumber(weeklySleep[weeklySleep.length - 1]) : null;
  const fallbackSteps = weeklySteps.length ? toFiniteNumber(weeklySteps[weeklySteps.length - 1]) : null;
  const fallbackStress = weeklyStress.length ? toFiniteNumber(weeklyStress[weeklyStress.length - 1]) : null;

  return {
    screen_time: getLiveInputValue('screen_time') ?? fallbackScreenMinutes,
    steps: getLiveInputValue('steps') ?? getLiveInputValue('steps_today') ?? fallbackSteps,
    sleep_hours: getLiveInputValue('sleep_hours') ?? fallbackSleepHours,
    stress_score: getLiveInputValue('stress_score') ?? getLiveInputValue('stress') ?? fallbackStress,
  };
}

function generateDailySummary(data) {
  const screenHours = toValidHours(data?.screen_time, { assumeMinutes: true });
  const sleepHours = toValidHours(data?.sleep_hours, { assumeMinutes: false });
  const steps = toValidSteps(data?.steps);
  const stressScore = toFiniteNumber(data?.stress_score);

  const detailParts = [];
  const insightParts = [];

  if (screenHours !== null) {
    detailParts.push(`used your phone for ${screenHours.toFixed(1)} hrs`);
    if (screenHours > 6) {
      insightParts.push('You had high screen usage today which may affect focus and sleep.');
    } else if (screenHours < 3) {
      insightParts.push('Your screen usage was well controlled today.');
    }
  }

  if (steps !== null) {
    detailParts.push(`walked ${steps.toLocaleString()} steps`);
    if (steps < 3000) {
      insightParts.push('Low physical activity detected.');
    } else if (steps <= 8000) {
      insightParts.push('Moderate activity level maintained.');
    } else {
      insightParts.push('Great job staying active today.');
    }
  }

  if (sleepHours !== null) {
    detailParts.push(`slept ${sleepHours.toFixed(1)} hrs`);
    if (sleepHours < 6) {
      insightParts.push('Sleep duration was below recommended levels.');
    } else if (sleepHours <= 8) {
      insightParts.push('You maintained a decent sleep schedule.');
    } else {
      insightParts.push('Good recovery with sufficient sleep.');
    }
  }

  if (stressScore !== null) {
    const clampedStress = clamp(stressScore, 0, 100);
    if (clampedStress >= 70) {
      insightParts.push('Stress signals are elevated, so recovery routines may help.');
    } else if (clampedStress <= 35) {
      insightParts.push('Stress indicators look stable today.');
    }
  }

  const details = detailParts.length
    ? `Today you ${detailParts.join(', and ')}.`
    : 'Today\'s tracked values were not available.';

  const insights = insightParts.length
    ? ` ${insightParts.join(' ')}`
    : ' Keep logging your habits for a more detailed AI summary.';

  return `${details}${insights}`;
}

function generateWeeklySummary(weeklyData) {
  const dates = Array.isArray(weeklyData?.dates) ? weeklyData.dates : [];
  const screenSeries = Array.isArray(weeklyData?.screen_time)
    ? weeklyData.screen_time
        .map((value) => normalizeRawTimeToHours(value))
        .filter((value) => value !== null)
    : [];
  const sleepSeries = Array.isArray(weeklyData?.sleep_hours)
    ? weeklyData.sleep_hours
        .map((value) => normalizeRawTimeToHours(value))
        .filter((value) => value !== null)
    : [];
  const stepsSeries = Array.isArray(weeklyData?.steps) ? weeklyData.steps : [];

  const avgScreen = average(screenSeries);
  const avgSleep = average(sleepSeries);
  const avgSteps = average(stepsSeries);

  const highestStepsIndex = findIndexOfMax(stepsSeries);
  const lowestSleepIndex = findIndexOfMin(sleepSeries);
  const highestStepsDay = toWeekdayLabelAtIndex(dates, highestStepsIndex);
  const lowestSleepDay = toWeekdayLabelAtIndex(dates, lowestSleepIndex);

  const screenTrend = trendDirection(screenSeries);
  const screenTrendText = screenTrend === 'decreased'
    ? 'slightly decreased this week'
    : screenTrend === 'increased'
      ? 'increased this week'
      : 'remained fairly stable this week';

  let sleepConsistency = 'steady';
  if (sleepSeries.length > 1) {
    const maxSleep = Math.max(...sleepSeries.map((v) => Number(v) || 0));
    const minSleep = Math.min(...sleepSeries.map((v) => Number(v) || 0));
    if (maxSleep - minSleep > 2) {
      sleepConsistency = 'inconsistent';
    }
  }

  let lifestyleSummary = 'balanced';
  const stepsTrend = trendDirection(stepsSeries);
  if (stepsTrend === 'increased') {
    lifestyleSummary = 'improving activity momentum';
  } else if (sleepConsistency === 'inconsistent') {
    lifestyleSummary = 'mixed recovery consistency';
  }

  const avgContextParts = [];
  if (avgScreen !== null) avgContextParts.push(`average screen time was ${roundToOne(avgScreen).toFixed(1)} hrs`);
  if (avgSleep !== null) avgContextParts.push(`average sleep was ${roundToOne(avgSleep).toFixed(1)} hrs`);
  if (avgSteps !== null) avgContextParts.push(`average steps were ${Math.round(avgSteps).toLocaleString()}`);
  const avgContext = avgContextParts.length ? ` This week, your ${avgContextParts.join(', and ')}.` : '';

  const sleepSentence = sleepConsistency === 'inconsistent'
    ? 'Sleep was inconsistent this week.'
    : 'Sleep pattern looked fairly consistent this week.';

  return `This week your activity peaked on ${highestStepsDay}. Sleep was lowest on ${lowestSleepDay}. Overall, your screen usage ${screenTrendText}, and your lifestyle shows ${lifestyleSummary}. ${sleepSentence}${avgContext}`;
}

function renderDynamicSummaries(payload) {
  const weekly = payload?.weekly || {};
  const dailyData = getCurrentSummaryData(weekly);
  setText('dailySummary', generateDailySummary(dailyData));
  setText('whaInsightText', generateWeeklySummary(weekly));
}

function bindLiveSummaryUpdates() {
  const seen = new Set();
  document.querySelectorAll('input').forEach((input) => {
    if (seen.has(input)) return;
    seen.add(input);

    const rerender = () => {
      if (!latestDashboardPayload) return;
      renderDynamicSummaries(latestDashboardPayload);
    };
    input.addEventListener('input', rerender);
    input.addEventListener('change', rerender);
  });
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
    animation: {
      duration: 1100,
      easing: 'easeOutQuart',
    },
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

  const mergedOptions = {
    ...defaultOpts,
    ...options,
    scales: {
      ...defaultOpts.scales,
      ...(options.scales || {}),
    },
    plugins: {
      ...defaultOpts.plugins,
      ...(options.plugins || {}),
      tooltip: {
        ...defaultOpts.plugins.tooltip,
        ...((options.plugins && options.plugins.tooltip) || {}),
      },
      legend: {
        ...defaultOpts.plugins.legend,
        ...((options.plugins && options.plugins.legend) || {}),
      },
    },
  };

  if (type === 'bar') {
    mergedOptions.scales = {
      ...mergedOptions.scales,
      y: {
        ...mergedOptions.scales.y,
        beginAtZero: true,
      },
    };
  }

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
    options: mergedOptions,
  });
}

function renderWeeklyCharts(weekly) {
  if (!weekly || !Array.isArray(weekly.dates) || !weekly.dates.length) return;

  const labels = formatWeekdayLabels(weekly.dates);

  renderChart(
    'weeklyScreenChart',
    labels,
    weekly.screen_time || [],
    'Screen time (hrs)',
    'rgba(0,212,255,0.92)',
    'line'
  );

  renderChart(
    'weeklySleepChart',
    labels,
    weekly.sleep_hours || [],
    'Sleep hours',
    'rgba(250,204,21,0.92)',
    'line'
  );

  renderChart(
    'weeklyStepsChart',
    labels,
    weekly.steps || [],
    'Steps',
    'rgba(52,211,153,0.92)',
    'bar'
  );

  renderChart(
    'weeklyStressChart',
    labels,
    weekly.stress || [],
    'Stress',
    'rgba(244,114,182,0.92)',
    'line'
  );
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

function renderPieChart(canvasId, labels, data, colors) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || typeof Chart === 'undefined') return;
  if (canvas._habitCheckChart) {
    canvas._habitCheckChart.destroy();
  }
  const total = data.reduce((a, b) => a + b, 0);
  canvas._habitCheckChart = new Chart(canvas, {
    type: 'pie',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: colors,
        borderColor: 'rgba(5,10,20,0.4)',
        borderWidth: 2,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom', labels: { color: 'rgba(255,255,255,0.8)', padding: 16 } },
        tooltip: {
          callbacks: {
            label(context) {
              const value = context.parsed;
              const pct = total > 0 ? ((value / total) * 100).toFixed(1) : '0.0';
              return `${context.label}: ${value} (${pct}%)`;
            },
          },
        },
      },
    },
  });
}

function renderWeeklyHabitAnalytics(weekly, comparison, weeklyInsight) {
  const labels = weekly.dates ? formatWeekdayLabels(weekly.dates) : [];

  if (labels.length) {
    const stepsScaled = (weekly.steps || []).map((v) => +(Number(v) / 1000).toFixed(2));
    renderGroupedBarChart('whaBarChart', labels, [
      {
        label: 'Screen Time (hrs)',
        data: weekly.screen_time || [],
        backgroundColor: 'rgba(0,212,255,0.72)',
        borderColor: 'rgba(0,212,255,0.92)',
        borderWidth: 1,
      },
      {
        label: 'Sleep Hours',
        data: weekly.sleep_hours || [],
        backgroundColor: 'rgba(250,204,21,0.72)',
        borderColor: 'rgba(250,204,21,0.92)',
        borderWidth: 1,
      },
      {
        label: 'Steps (\u00d71000)',
        data: stepsScaled,
        backgroundColor: 'rgba(52,211,153,0.72)',
        borderColor: 'rgba(52,211,153,0.92)',
        borderWidth: 1,
      },
      {
        label: 'Stress',
        data: weekly.stress || [],
        backgroundColor: 'rgba(244,114,182,0.72)',
        borderColor: 'rgba(244,114,182,0.92)',
        borderWidth: 1,
      },
    ]);
  }

  const avgs = weekly.averages || {};
  const screenAvg = +(Number(avgs.screen_time) || 0).toFixed(2);
  const sleepAvg = +(Number(avgs.sleep_hours) || 0).toFixed(2);
  const stepsAvg = +((Number(avgs.steps) || 0) / 1000).toFixed(2);
  const stressAvg = +(Number(avgs.stress) || 0).toFixed(2);

  if (screenAvg + sleepAvg + stepsAvg + stressAvg > 0) {
    renderPieChart(
      'whaPieChart',
      ['Screen Time', 'Sleep Hours', 'Steps (\u00d71000)', 'Stress'],
      [screenAvg, sleepAvg, stepsAvg, stressAvg],
      [
        'rgba(0,212,255,0.82)',
        'rgba(250,204,21,0.82)',
        'rgba(52,211,153,0.82)',
        'rgba(244,114,182,0.82)',
      ]
    );
  }

  const comp = comparison || {};
  setText('whaHighestScreenDay', comp.highest_screen_day || '\u2014');
  setText('whaLowestSleepDay', comp.lowest_sleep_day || '\u2014');
  setText('whaMostActiveDay', comp.most_active_day || '\u2014');
  setText('whaStressTrend', toReadableTrend(comp.stress_trend));
  setText('whaInsightText', weeklyInsight || generateWeeklySummary(weekly));
}

async function refreshDashboard() {
  const data = await fetchDashboardData();
  if (!data || data.error) {
    setText('wellnessStatus', data?.error || 'Unable to load data');
    return;
  }

  latestDashboardPayload = data;

  const wellness = data.wellness || {};
  setText('wellnessScore', wellness.score ?? '0');
  setText('wellnessStatus', wellness.status || '—');
  setProgressRing(document.getElementById('wellnessRing'), wellness.score ?? 0);
  const breakdown = wellness.breakdown || {};
  setText(
    'wellnessBreakdown',
    `Sleep ${breakdown.sleep_hours ?? 0} | Steps ${breakdown.steps ?? 0} | Screen ${breakdown.screen_time ?? 0} | Notifications ${breakdown.notifications ?? 0} | Heart Rate ${breakdown.heart_rate ?? 0}`
  );

  const future = data.future_prediction || {};
  setText('futureStressLevel', future.stress?.level || '—');
  setText('futureStressProb', future.stress?.probability ? `Confidence: ${formatPercent(future.stress.probability)}` : '');
  setText('futureFocus', future.focus?.score ? `${future.focus.score.toFixed(1)}` : '—');
  setText('futureSleepRisk', future.sleep_quality_risk ? formatPercent(future.sleep_quality_risk) : '—');

  const personality = data.personality || {};
  setText('personalityType', personality.type || '—');
  setText('personalityDescription', personality.description || '');

  const burnout = data.burnout || {};
  setText('burnoutRisk', burnout.risk_percentage ? formatPercent(burnout.risk_percentage) : '—');
  setText('burnoutSummary', burnout.summary || '');
  const progressEl = document.getElementById('burnoutProgress');
  if (progressEl) {
    const pct = Math.max(0, Math.min(100, Number(burnout.risk_percentage) || 0));
    progressEl.style.width = `${pct}%`;
  }

  renderList('insightsList', data.insights);
  renderList('patternsList', data.patterns);

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
    const previous = Number(arr[arr.length - 2]);
    const current = Number(arr[arr.length - 1]);
    if (!Number.isFinite(previous) || !Number.isFinite(current)) {
      el.innerHTML = '';
      return;
    }
    let cls = 'trend-flat';
    let icon = 'trending_flat';
    if (current > previous) {
      cls = 'trend-up';
      icon = 'trending_up';
    } else if (current < previous) {
      cls = 'trend-down';
      icon = 'trending_down';
    }
    el.innerHTML = `<span class="material-icons-round ${cls}">${icon}</span>`;
  }
  applyTrend('trendScreen', weekly.screen_time);
  applyTrend('trendSleep', weekly.sleep_hours);
  applyTrend('trendSteps', weekly.steps);
  applyTrend('trendStress', weekly.stress);

  renderWeeklyHabitAnalytics(weekly, data.weekly_comparison || {}, '');
  renderDynamicSummaries(data);
}

window.addEventListener('DOMContentLoaded', () => {
  if (document.body.dataset.page !== 'dashboard') return;
  bindLiveSummaryUpdates();
  refreshDashboard();
  // refresh every 5 minutes to reflect new incoming data
  setInterval(refreshDashboard, 5 * 60 * 1000);
});
