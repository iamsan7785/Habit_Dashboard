const STORAGE_KEY = "habitcheck:lastResult";

const MODEL_CONFIGS = {
  sleep: {
    formId: "sleepForm",
    endpoint: "/predict_sleep",
    resultsTitle: "Sleep Drift Analysis",
    editUrl: "/sleep",
    primaryLabel: "Sleep Score",
    pageLabel: "Sleep",
    icon: "bedtime",
    displayLabels: {
      sleep_hours: "Sleep Hours",
      screen_time_before_sleep: "Screen Time Before Sleep",
      notifications_night: "Notifications Night",
      heart_rate: "Heart Rate",
      steps_today: "Steps Today",
      deep_sleep_hours: "Deep Sleep Hours",
      night_phone_usage: "Night Phone Usage",
      sleep_interruption: "Sleep Interruptions",
      wake_time: "Wake Time",
      noise_level: "Noise Level",
      ambient_light_level: "Ambient Light Level"
    },
    colors: {
      sleep_hours: "#facc15",
      screen_time_before_sleep: "#f472b6",
      notifications_night: "#a78bfa",
      heart_rate: "#22d3ee",
      steps_today: "#34d399",
      deep_sleep_hours: "#10b981",
      night_phone_usage: "#f97316",
      sleep_interruption: "#ef4444",
      wake_time: "#3b82f6",
      noise_level: "#8b5cf6",
      ambient_light_level: "#14b8a6"
    },
    fieldMap: {
      sleep_hours: "sleep_hours",
      total_screen_time: "screen_time_before_sleep",
      notification_count: "notifications_night",
      heart_rate: "heart_rate",
      steps: "steps_today",
      deep_sleep_hours: "deep_sleep_hours",
      night_phone_usage: "night_phone_usage",
      sleep_interruption: "sleep_interruption",
      wake_time: "wake_time",
      noise_level: "noise_level",
      ambient_light_level: "ambient_light_level"
    },
    previewFormatters: {
      sleep_hours: "hoursDecimal",
      screen_time_before_sleep: "durationMinutes",
      notifications_night: "count",
      heart_rate: "bpm",
      steps_today: "steps",
      deep_sleep_hours: "hoursDecimal",
      night_phone_usage: "durationMinutes",
      sleep_interruption: "count",
      wake_time: "hoursDecimal",
      noise_level: "count",
      ambient_light_level: "count"
    },
    quickFacts: [
      { key: "sleep_hours", label: "Sleep Hours", formatter: "hoursDecimal" },
      { key: "screen_time_before_sleep", label: "Screen Before Sleep", formatter: "durationMinutes" },
      { key: "notifications_night", label: "Night Notifications", formatter: "count" },
      { key: "steps_today", label: "Steps Today", formatter: "steps" },
    ],
    resultMeta(result) {
      return {
        scoreText: `${toOneDecimal(result.prediction)}`,
        categoryText: result.category || "Sleep",
        explanation: result.explanation || "Your current sleep pattern has been analyzed across recent lifestyle signals.",
      };
    },
  },
  study: {
    formId: "studyForm",
    endpoint: "/predict_study",
    resultsTitle: "Study Drift Analysis",
    editUrl: "/study",
    primaryLabel: "Study Score",
    pageLabel: "Study",
    icon: "menu_book",
    displayLabels: {
      screen_time: "Screen Time",
      productive_usage: "Productive Usage",
      social_usage: "Social Usage",
      gaming_usage: "Gaming Usage",
      notifications: "Notifications",
      unlock_count: "Unlock Count",
      study_hours: "Study Hours",
      app_switching_frequency: "App Switching Frequency",
      notifications_during_study: "Notifications During Study",
      break_frequency: "Break Frequency",
      phone_usage_during_study: "Phone Usage During Study",
      completed_tasks: "Completed Tasks"
    },
    colors: {
      screen_time: "#22d3ee",
      productive_usage: "#34d399",
      social_usage: "#a78bfa",
      gaming_usage: "#f472b6",
      notifications: "#facc15",
      unlock_count: "#60a5fa",
      study_hours: "#0284c7",
      app_switching_frequency: "#22d3ee",
      notifications_during_study: "#facc15",
      break_frequency: "#a3e635",
      phone_usage_during_study: "#fb7185",
      completed_tasks: "#4ade80"
    },
    fieldMap: {
      total_screen_time: "screen_time",
      productive_usage: "productive_usage",
      social_usage: "social_usage",
      gaming_usage: "gaming_usage",
      notification_count: "notifications",
      study_hours: "study_hours",
      app_switching_frequency: "app_switching_frequency",
      notifications_during_study: "notifications_during_study",
      break_frequency: "break_frequency",
      phone_usage_during_study: "phone_usage_during_study",
      completed_tasks: "completed_tasks"
    },
    previewFormatters: {
      screen_time: "durationMinutes",
      productive_usage: "durationMinutes",
      social_usage: "durationMinutes",
      gaming_usage: "durationMinutes",
      notifications: "count",
      unlock_count: "count",
      study_hours: "hoursDecimal",
      app_switching_frequency: "count",
      notifications_during_study: "count",
      break_frequency: "count",
      phone_usage_during_study: "durationMinutes",
      completed_tasks: "count"
    },
    quickFacts: [
      { key: "screen_time", label: "Screen Time", formatter: "durationMinutes" },
      { key: "productive_usage", label: "Productive Usage", formatter: "durationMinutes" },
      { key: "social_usage", label: "Social Usage", formatter: "durationMinutes" },
      { key: "gaming_usage", label: "Gaming Usage", formatter: "durationMinutes" },
    ],
    resultMeta(result) {
      return {
        scoreText: `${toOneDecimal(result.prediction)}`,
        categoryText: result.category || "Study",
        explanation: result.explanation || "Your study drift score blends focus time, distractions, and unlock behavior.",
      };
    },
  },
  stress: {
    formId: "stressForm",
    endpoint: "/predict_stress",
    resultsTitle: "Stress Analysis",
    editUrl: "/stress",
    primaryLabel: "Stress Level",
    pageLabel: "Stress",
    icon: "psychology_alt",
    displayLabels: {
      screen_time: "Screen Time",
      notifications: "Notifications",
      unlock_count: "Unlock Count",
      sleep_hours: "Sleep Hours",
      steps: "Steps",
      heart_rate: "Heart Rate",
      social_usage: "Social Usage",
      gaming_usage: "Gaming Usage",
    },
    colors: {
      screen_time: "#22d3ee",
      notifications: "#a78bfa",
      unlock_count: "#60a5fa",
      sleep_hours: "#facc15",
      steps: "#34d399",
      heart_rate: "#fb7185",
      social_usage: "#c084fc",
      gaming_usage: "#f472b6",
    },
    fieldMap: {
      total_screen_time: "screen_time",
      notification_count: "notifications",
      sleep_hours: "sleep_hours",
      steps: "steps",
      heart_rate: "heart_rate",
      social_usage: "social_usage",
      gaming_usage: "gaming_usage",
    },
    previewFormatters: {
      screen_time: "durationMinutes",
      notifications: "count",
      unlock_count: "count",
      sleep_hours: "hoursDecimal",
      steps: "steps",
      heart_rate: "bpm",
      social_usage: "durationMinutes",
      gaming_usage: "durationMinutes",
    },
    quickFacts: [
      { key: "screen_time", label: "Screen Time", formatter: "durationMinutes" },
      { key: "sleep_hours", label: "Sleep Hours", formatter: "hoursDecimal" },
      { key: "heart_rate", label: "Heart Rate", formatter: "bpm" },
      { key: "social_usage", label: "Social Usage", formatter: "durationMinutes" },
    ],
    resultMeta(result) {
      return {
        scoreText: result.stress_level || "Unknown",
        categoryText: "Stress Level",
        explanation: result.explanation || "Stress level combines recovery, activity, and digital overload indicators.",
      };
    },
  },
  health: {
    formId: "healthForm",
    endpoint: "/predict_health",
    resultsTitle: "Overall Health Analysis",
    editUrl: "/overall",
    primaryLabel: "Health Score",
    pageLabel: "Health",
    icon: "monitor_heart",
    displayLabels: {
      sleep_hours: "Sleep Hours",
      steps: "Steps",
      calories: "Calories",
      heart_rate: "Heart Rate",
      screen_time: "Screen Time",
      social_usage: "Social Usage",
      gaming_usage: "Gaming Usage",
      productive_usage: "Productive Usage",
      notifications: "Notifications",
      unlock_count: "Unlock Count",
      deep_sleep_hours: "Deep Sleep Hours",
      night_phone_usage: "Night Phone Usage",
      sleep_interruption: "Sleep Interruptions",
      wake_time: "Wake Time",
      noise_level: "Noise Level",
      ambient_light_level: "Ambient Light Level",
      study_hours: "Study Hours",
      app_switching_frequency: "App Switching Frequency",
      notifications_during_study: "Notifications During Study",
      break_frequency: "Break Frequency",
      phone_usage_during_study: "Phone Usage During Study",
      completed_tasks: "Completed Tasks"
    },
    colors: {
      sleep_hours: "#facc15",
      steps: "#34d399",
      calories: "#fb923c",
      heart_rate: "#22d3ee",
      screen_time: "#f472b6",
      social_usage: "#a78bfa",
      gaming_usage: "#fb7185",
      productive_usage: "#00d4ff",
      notifications: "#60a5fa",
      unlock_count: "#c084fc",
      deep_sleep_hours: "#10b981",
      night_phone_usage: "#f97316",
      sleep_interruption: "#ef4444",
      wake_time: "#3b82f6",
      noise_level: "#8b5cf6",
      ambient_light_level: "#14b8a6",
      study_hours: "#0284c7",
      app_switching_frequency: "#22d3ee",
      notifications_during_study: "#facc15",
      break_frequency: "#a3e635",
      phone_usage_during_study: "#fb7185",
      completed_tasks: "#4ade80"
    },
    fieldMap: {
      sleep_hours: "sleep_hours",
      steps: "steps",
      calories_burned: "calories",
      heart_rate: "heart_rate",
      total_screen_time: "screen_time",
      social_usage: "social_usage",
      gaming_usage: "gaming_usage",
      productive_usage: "productive_usage",
      notification_count: "notifications",
      deep_sleep_hours: "deep_sleep_hours",
      night_phone_usage: "night_phone_usage",
      sleep_interruption: "sleep_interruption",
      wake_time: "wake_time",
      noise_level: "noise_level",
      ambient_light_level: "ambient_light_level",
      study_hours: "study_hours",
      app_switching_frequency: "app_switching_frequency",
      notifications_during_study: "notifications_during_study",
      break_frequency: "break_frequency",
      phone_usage_during_study: "phone_usage_during_study",
      completed_tasks: "completed_tasks"
    },
    previewFormatters: {
      sleep_hours: "hoursDecimal",
      steps: "steps",
      calories: "calories",
      heart_rate: "bpm",
      screen_time: "durationMinutes",
      social_usage: "durationMinutes",
      gaming_usage: "durationMinutes",
      productive_usage: "durationMinutes",
      notifications: "count",
      unlock_count: "count",
      deep_sleep_hours: "hoursDecimal",
      night_phone_usage: "durationMinutes",
      sleep_interruption: "count",
      wake_time: "hoursDecimal",
      noise_level: "count",
      ambient_light_level: "count",
      study_hours: "hoursDecimal",
      app_switching_frequency: "count",
      notifications_during_study: "count",
      break_frequency: "count",
      phone_usage_during_study: "durationMinutes",
      completed_tasks: "count"
    },
    quickFacts: [
      { key: "screen_time", label: "Screen Time", formatter: "durationMinutes" },
      { key: "calories", label: "Calories", formatter: "calories" },
      { key: "social_usage", label: "Social Usage", formatter: "durationMinutes" },
      { key: "productive_usage", label: "Productive Usage", formatter: "durationMinutes" },
    ],
    resultMeta(result) {
      return {
        scoreText: `${toOneDecimal(result.prediction)}`,
        categoryText: result.category || "Health",
        explanation: result.explanation || "The overall health score weighs sleep, activity, recovery, and digital balance.",
      };
    },
  },
};

function toNumber(value) {
  const num = Number(value);
  return Number.isFinite(num) ? num : 0;
}

function toOneDecimal(value) {
  return toNumber(value).toFixed(1);
}

function formatNumber(value) {
  return Math.round(toNumber(value)).toLocaleString();
}

function convertMinutesToReadable(value) {
  const totalMinutes = Math.max(0, Math.round(toNumber(value)));
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  if (hours === 0) {
    return `${minutes} min`;
  }
  return `${hours} hr ${minutes} min`;
}

function humanizeMinutes(value) {
  return convertMinutesToReadable(value);
}

function formatFieldValue(value, formatter) {
  const numericValue = toNumber(value);
  switch (formatter) {
    case "durationMinutes":
      return humanizeMinutes(numericValue);
    case "hoursDecimal":
      return `${numericValue.toFixed(1)} hrs`;
    case "steps":
      return `${formatNumber(numericValue)} steps`;
    case "count":
      return formatNumber(numericValue);
    case "bpm":
      return `${formatNumber(numericValue)} bpm`;
    case "calories":
      return `${formatNumber(numericValue)} kcal`;
    default:
      return `${numericValue}`;
  }
}

function refreshFloatingField(input) {
  const wrapper = input.closest(".floating-field");
  if (!wrapper) return;
  wrapper.classList.toggle("is-active", String(input.value).trim() !== "");
}

function updateFieldPreview(input, modelName) {
  const wrapper = input.closest(".floating-field");
  if (!wrapper) return;
  const preview = wrapper.querySelector(".input-preview");
  if (!preview) return;

  const formatter = MODEL_CONFIGS[modelName]?.previewFormatters?.[input.name];
  const value = String(input.value).trim();
  if (!formatter || value === "") {
    preview.textContent = "";
    preview.classList.remove("active");
    return;
  }

  preview.textContent = formatFieldValue(value, formatter);
  preview.classList.add("active");
}

function updateCalculations(formEl, modelName) {
  if (!formEl) return;
  formEl.querySelectorAll("input").forEach((input) => {
    refreshFloatingField(input);
    updateFieldPreview(input, modelName);
  });
}

function bindLiveInputUpdates(formEl, modelName) {
  if (!formEl) return;
  formEl.querySelectorAll("input").forEach((input) => {
    input.addEventListener("input", () => updateCalculations(formEl, modelName));
    input.addEventListener("change", () => updateCalculations(formEl, modelName));
  });
  updateCalculations(formEl, modelName);
}

function setVal(id, value) {
  const el = document.getElementById(id);
  if (!el) return;
  el.value = value ?? "";
  refreshFloatingField(el);
}

function collectFormData(formId) {
  const form = document.getElementById(formId);
  if (!form) return {};
  const data = {};
  form.querySelectorAll("input").forEach((el) => {
    if (el.name) data[el.name] = toNumber(el.value);
  });
  return data;
}

async function postPredict(endpoint, data) {
  const res = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

async function autoFillForm(modelName) {
  const config = MODEL_CONFIGS[modelName];
  const loadingEl = document.getElementById("loadingMsg");
  const formEl = document.getElementById(config.formId);

  try {
    const res = await fetch("/api/user_data");
    const data = await res.json();

    if (data.error) {
      if (loadingEl) loadingEl.textContent = `Error: ${data.error}`;
      return;
    }

    Object.entries(config.fieldMap || {}).forEach(([sourceKey, inputId]) => {
      if (data[sourceKey] !== undefined) {
        setVal(inputId, data[sourceKey]);
      }
    });

    if (document.getElementById("unlock_count") && !document.getElementById("unlock_count").value) {
      setVal("unlock_count", 0);
    }

    if (loadingEl) loadingEl.classList.add("hidden");
    if (formEl) formEl.classList.remove("hidden");
    updateCalculations(formEl, modelName);
  } catch (err) {
    if (loadingEl) {
      loadingEl.textContent = `Failed to load data: ${err.message}`;
      loadingEl.style.color = "#fca5a5";
    }
  }
}

function persistResult(modelName, inputs, result) {
  sessionStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({ modelName, timestamp: new Date().toISOString(), inputs, result })
  );
}

async function submitPrediction(modelName) {
  const config = MODEL_CONFIGS[modelName];
  const formEl = document.getElementById(config.formId);
  const button = formEl?.querySelector("button[type='button']");
  const statusEl = document.getElementById(`${modelName}Status`);

  if (button) button.disabled = true;
  if (statusEl) statusEl.textContent = "Running prediction...";

  try {
    const inputs = collectFormData(config.formId);
    const result = await postPredict(config.endpoint, inputs);
    if (result.error) {
      if (statusEl) statusEl.textContent = `Error: ${result.error}`;
      return;
    }

    persistResult(modelName, inputs, result);
    window.location.href = `/results?model=${encodeURIComponent(modelName)}`;
  } catch (err) {
    if (statusEl) statusEl.textContent = `Request failed: ${err.message}`;
  } finally {
    if (button) button.disabled = false;
  }
}

function getStoredResult() {
  const raw = sessionStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch (_error) {
    return null;
  }
}

function prettifyKey(modelName, key) {
  return MODEL_CONFIGS[modelName]?.displayLabels?.[key] || key.replace(/_/g, " ").replace(/\b\w/g, (m) => m.toUpperCase());
}

function getChartData(modelName, result) {
  const contributions = result?.contributions || {};
  const labels = Object.keys(contributions);
  const values = Object.values(contributions);
  const colors = labels.map((key) => MODEL_CONFIGS[modelName]?.colors?.[key] || "#00d4ff");
  return { labels, values, colors };
}

function renderBreakdown(modelName, result) {
  const list = document.getElementById("breakdownList");
  if (!list) return;
  list.innerHTML = "";

  Object.entries(result?.contributions || {}).forEach(([key, value]) => {
    const color = MODEL_CONFIGS[modelName]?.colors?.[key] || "#00d4ff";
    const item = document.createElement("div");
    item.className = "breakdown-item";
    item.innerHTML = `
      <div class="breakdown-head">
        <div class="breakdown-name">
          <span class="breakdown-dot" style="background:${color}"></span>
          <span>${prettifyKey(modelName, key)}</span>
        </div>
        <strong>${toOneDecimal(value)}%</strong>
      </div>
      <div class="breakdown-bar">
        <div class="breakdown-fill" style="background:${color}; width:0%"></div>
      </div>
    `;
    list.appendChild(item);

    requestAnimationFrame(() => {
      const fill = item.querySelector(".breakdown-fill");
      if (fill) fill.style.width = `${Math.max(0, Math.min(100, toNumber(value)))}%`;
    });
  });
}

function renderQuickFacts(modelName, inputs) {
  const wrap = document.getElementById("quickFacts");
  if (!wrap) return;
  wrap.innerHTML = "";

  (MODEL_CONFIGS[modelName]?.quickFacts || []).forEach((fact) => {
    const card = document.createElement("div");
    card.className = "quick-fact metric-card";
    card.innerHTML = `
      <div class="metric-label">${fact.label}</div>
      <div class="metric-value">${formatFieldValue(inputs[fact.key], fact.formatter)}</div>
    `;
    wrap.appendChild(card);
  });
}

function renderRecommendations(result) {
  const list = document.getElementById("recommendationList");
  if (!list) return;
  list.innerHTML = "";
  const items = result?.recommendations?.length ? result.recommendations : ["Keep monitoring your routine to maintain balanced habits."];
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    list.appendChild(li);
  });
}

function renderChart(modelName, result) {
  const canvas = document.getElementById("resultsChart");
  if (!canvas || typeof Chart === "undefined") return;

  if (window.habitCheckChart) {
    window.habitCheckChart.destroy();
  }

  const { labels, values, colors } = getChartData(modelName, result);
  window.habitCheckChart = new Chart(canvas, {
    type: "doughnut",
    data: {
      labels: labels.map((key) => prettifyKey(modelName, key)),
      datasets: [{ data: values, backgroundColor: colors, borderWidth: 0, hoverOffset: 12 }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "62%",
      animation: {
        animateScale: true,
        animateRotate: true,
        duration: 1100,
        easing: "easeOutQuart",
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label(context) {
              return `${context.label}: ${toOneDecimal(context.parsed)}%`;
            },
          },
        },
      },
    },
  });
}

function renderResultsPage() {
  const container = document.getElementById("resultsContent");
  const emptyState = document.getElementById("resultsEmptyState");
  if (!container || !emptyState) return;

  const params = new URLSearchParams(window.location.search);
  const requestedModel = params.get("model");
  const payload = getStoredResult();

  if (!payload || !payload.modelName || !MODEL_CONFIGS[payload.modelName] || (requestedModel && requestedModel !== payload.modelName)) {
    emptyState.classList.remove("hidden");
    container.classList.add("hidden");
    return;
  }

  const { modelName, inputs, result, timestamp } = payload;
  const config = MODEL_CONFIGS[modelName];
  const meta = config.resultMeta(result);

  emptyState.classList.add("hidden");
  container.classList.remove("hidden");

  document.getElementById("resultsTitle").textContent = config.resultsTitle;
  document.getElementById("resultsSubtitle").textContent = `${config.primaryLabel} generated from your latest submitted inputs.`;
  document.getElementById("resultsScore").textContent = meta.scoreText;
  document.getElementById("resultsCategory").textContent = meta.categoryText;
  document.getElementById("resultsExplanation").textContent = meta.explanation;
  document.getElementById("editInputsLink").href = config.editUrl;
  document.getElementById("resultsVisualIcon").textContent = config.icon;
  document.getElementById("resultsVisualTitle").textContent = `${config.pageLabel} insights`;
  document.getElementById("resultsVisualCopy").textContent = modelName === "stress"
    ? "Stress is influenced by mental load, screen habits, and recovery quality."
    : modelName === "study"
      ? "Study drift reflects focus time, distractions, and digital balance."
      : modelName === "sleep"
        ? "Sleep quality is shaped by bedtime behavior, notifications, and recovery signals."
        : "Overall health blends sleep, activity, heart rate, and digital habits.";
  document.getElementById("resultsTimestamp").textContent = `Generated ${new Date(timestamp).toLocaleString()}`;

  renderQuickFacts(modelName, inputs || {});
  renderRecommendations(result || {});
  renderChart(modelName, result || {});
  renderBreakdown(modelName, result || {});
}

function initPredictionPage(modelName) {
  const config = MODEL_CONFIGS[modelName];
  const formEl = document.getElementById(config.formId);
  if (!formEl) return;
  bindLiveInputUpdates(formEl, modelName);
  autoFillForm(modelName);
}

function submitSleep() {
  submitPrediction("sleep");
}

function submitStudy() {
  submitPrediction("study");
}

function submitStress() {
  submitPrediction("stress");
}

function submitHealth() {
  submitPrediction("health");
}

window.initPredictionPage = initPredictionPage;
window.autoFillForm = autoFillForm;
window.submitSleep = submitSleep;
window.submitStudy = submitStudy;
window.submitStress = submitStress;
window.submitHealth = submitHealth;

document.addEventListener("DOMContentLoaded", () => {
  if (document.body.dataset.page === "results") {
    renderResultsPage();
  }
});
