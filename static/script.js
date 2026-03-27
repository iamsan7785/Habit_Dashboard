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
    defaults: {
      sleep_hours: 7,
      screen_time_before_sleep: 120,
      notifications_night: 10,
      heart_rate: 70,
      steps_today: 5000,
      deep_sleep_hours: 2,
      night_phone_usage: 30,
      sleep_interruption: 2,
      wake_time: 7,
      noise_level: 3,
      ambient_light_level: 2
    },
    ranges: {
      sleep_hours: { min: 6, max: 9, decimals: 1 },
      screen_time_before_sleep: { min: 30, max: 240 },
      notifications_night: { min: 20, max: 120 },
      heart_rate: { min: 65, max: 95 },
      steps_today: { min: 2000, max: 10000 },
      deep_sleep_hours: { min: 1, max: 3 },
      night_phone_usage: { min: 0, max: 60 },
      sleep_interruption: { min: 0, max: 5 },
      wake_time: { min: 5, max: 9 },
      noise_level: { min: 0, max: 6 },
      ambient_light_level: { min: 0, max: 5 }
    },
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
    defaults: {
      screen_time: 180,
      productive_usage: 60,
      social_usage: 45,
      gaming_usage: 30,
      notifications: 5,
      unlock_count: 25,
      study_hours: 2,
      app_switching_frequency: 8,
      notifications_during_study: 3,
      break_frequency: 4,
      phone_usage_during_study: 90,
      completed_tasks: 6
    },
    ranges: {
      screen_time: { min: 120, max: 360 },
      productive_usage: { min: 30, max: 150 },
      social_usage: { min: 60, max: 240 },
      gaming_usage: { min: 0, max: 120 },
      notifications: { min: 20, max: 120 },
      unlock_count: { min: 10, max: 100 },
      study_hours: { min: 0.5, max: 8, decimals: 1 },
      app_switching_frequency: { min: 0, max: 20 },
      notifications_during_study: { min: 0, max: 10 },
      break_frequency: { min: 1, max: 10 },
      phone_usage_during_study: { min: 0, max: 180 },
      completed_tasks: { min: 0, max: 15 }
    },
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
    defaults: {
      screen_time: 240,
      notifications: 15,
      unlock_count: 40,
      sleep_hours: 7,
      steps: 6000,
      heart_rate: 75,
      social_usage: 60,
      gaming_usage: 45
    },
    ranges: {
      screen_time: { min: 120, max: 360 },
      notifications: { min: 20, max: 120 },
      unlock_count: { min: 10, max: 150 },
      sleep_hours: { min: 6, max: 9, decimals: 1 },
      steps: { min: 2000, max: 10000 },
      heart_rate: { min: 65, max: 95 },
      social_usage: { min: 60, max: 240 },
      gaming_usage: { min: 0, max: 120 }
    },
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
    defaults: {
      sleep_hours: 7,
      steps: 7000,
      calories: 2000,
      heart_rate: 68,
      screen_time: 300,
      social_usage: 90,
      gaming_usage: 60,
      productive_usage: 120,
      notifications: 20,
      unlock_count: 35
    },
    ranges: {
      sleep_hours: { min: 6, max: 9, decimals: 1 },
      steps: { min: 2000, max: 10000 },
      calories: { min: 1500, max: 3000 },
      heart_rate: { min: 65, max: 95 },
      screen_time: { min: 120, max: 360 },
      social_usage: { min: 60, max: 240 },
      gaming_usage: { min: 0, max: 120 },
      productive_usage: { min: 30, max: 150 },
      notifications: { min: 20, max: 120 },
      unlock_count: { min: 10, max: 150 }
    },
    resultMeta(result) {
      return {
        scoreText: `${toOneDecimal(result.prediction)}`,
        categoryText: result.category || "Health",
        explanation: result.explanation || "The overall health score weighs sleep, activity, recovery, and digital balance.",
      };
    },
  },
};

function generateRandomValue(min, max, decimals) {
  const rand = Math.random() * (max - min) + min;

  // If a specific decimal precision is requested, use it.
  if (typeof decimals === "number" && decimals > 0) {
    return Number(rand.toFixed(decimals));
  }

  // Preserve existing behavior: if either boundary is non-integer, return one decimal.
  if (!Number.isInteger(min) || !Number.isInteger(max)) {
    return Number(rand.toFixed(1));
  }

  // Otherwise return an integer.
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function fillEmptyFieldsWithRandom(modelName) {
  const config = MODEL_CONFIGS[modelName];
  if (!config || !config.ranges) return;

  Object.entries(config.ranges).forEach(([key, range]) => {
    const input = document.getElementById(key);
    if (!input) return;

    const currentValue = String(input.value).trim();
    if (currentValue !== "") return;

    const decimals = range.decimals ?? 0;
    const value = generateRandomValue(range.min, range.max, decimals);
    setVal(key, value);
  });
}

function toNumber(value) {
  const num = Number(value);
  return Number.isFinite(num) ? num : 0;
}

const TIME_MINUTES_MIN = 0;
const TIME_MINUTES_MAX = 1440;
const HEART_RATE_MIN = 0;
const HEART_RATE_MAX = 250;

const TIME_FIELDS_IN_MINUTES = new Set([
  "screen_time",
  "screen_time_before_sleep",
  "night_phone_usage",
  "wake_time",
  "phone_usage_during_study",
]);

const HOUR_BASED_FIELDS = new Set([
  "sleep_hours",
  "study_hours",
  "deep_sleep_hours",
]);

const SCREEN_DISTRIBUTION_FIELDS = ["social_usage", "gaming_usage", "productive_usage"];
const HIGHLIGHT_TIME_FIELDS_MINUTES = new Set([
  "sleep_hours",
  "screen_time_before_sleep",
  "night_phone_usage",
  "phone_usage_during_study",
  "screen_time",
]);

function roundToTwoDecimals(value) {
  return Math.round(toNumber(value) * 100) / 100;
}

function formatInputValue(value) {
  const numericValue = roundToTwoDecimals(value);
  if (Number.isInteger(numericValue)) {
    return String(numericValue);
  }
  return String(numericValue);
}

function ensureInlineErrorElement(input) {
  const wrapper = input.closest(".floating-field");
  if (!wrapper) return null;

  let errorEl = wrapper.querySelector(".input-error-text");
  if (errorEl) return errorEl;

  errorEl = document.createElement("p");
  errorEl.className = "form-note input-error-text";

  const meta = wrapper.querySelector(".input-meta");
  if (meta && meta.parentNode) {
    meta.parentNode.insertBefore(errorEl, meta.nextSibling);
  } else {
    wrapper.appendChild(errorEl);
  }

  return errorEl;
}

function setFieldError(input, message) {
  const wrapper = input.closest(".floating-field");
  if (wrapper) wrapper.classList.add("has-error");

  const errorEl = ensureInlineErrorElement(input);
  if (!errorEl) return;
  errorEl.textContent = message;
}

function clearFieldError(input) {
  const wrapper = input.closest(".floating-field");
  if (wrapper) wrapper.classList.remove("has-error");

  const errorEl = ensureInlineErrorElement(input);
  if (!errorEl) return;
  errorEl.textContent = "";
}

function normalizeScreenTimeDistribution(payload) {
  if (!("screen_time" in payload)) return;
  if (!SCREEN_DISTRIBUTION_FIELDS.every((field) => field in payload)) return;

  const totalScreenTime = Math.max(0, toNumber(payload.screen_time));
  const existingValues = SCREEN_DISTRIBUTION_FIELDS.map((field) => Math.max(0, toNumber(payload[field])));
  const totalUsage = existingValues.reduce((sum, value) => sum + value, 0);

  if (totalScreenTime === 0) {
    SCREEN_DISTRIBUTION_FIELDS.forEach((field) => {
      payload[field] = 0;
    });
    return;
  }

  if (totalUsage === 0) {
    const equalShare = roundToTwoDecimals(totalScreenTime / SCREEN_DISTRIBUTION_FIELDS.length);
    let runningTotal = 0;
    SCREEN_DISTRIBUTION_FIELDS.forEach((field, index) => {
      const isLast = index === SCREEN_DISTRIBUTION_FIELDS.length - 1;
      const value = isLast ? roundToTwoDecimals(totalScreenTime - runningTotal) : equalShare;
      payload[field] = value;
      runningTotal += value;
    });
    return;
  }

  const scaleFactor = totalScreenTime / totalUsage;
  let scaledRunningTotal = 0;
  SCREEN_DISTRIBUTION_FIELDS.forEach((field, index) => {
    const isLast = index === SCREEN_DISTRIBUTION_FIELDS.length - 1;
    const scaledValue = isLast
      ? roundToTwoDecimals(totalScreenTime - scaledRunningTotal)
      : roundToTwoDecimals(toNumber(payload[field]) * scaleFactor);

    payload[field] = scaledValue;
    scaledRunningTotal += scaledValue;
  });
}

function validateAndPreparePayload(modelName, formEl, options = {}) {
  if (!formEl || !MODEL_CONFIGS[modelName]) {
    return { isValid: false, payload: {}, validationErrors: { form: "Form unavailable" } };
  }

  const shouldShowErrors = options.showErrors === true;
  const applyNormalization = options.applyNormalization === true;
  const syncNormalizedValuesToForm = options.syncNormalizedValuesToForm === true;

  const payload = collectFormData(MODEL_CONFIGS[modelName].formId);
  const validationErrors = {};

  formEl.querySelectorAll("input").forEach((input) => {
    const fieldName = input.name;
    if (!fieldName) return;

    const rawValue = toNumber(input.value);
    const minutesValue = HOUR_BASED_FIELDS.has(fieldName) ? rawValue * 60 : rawValue;

    if (HOUR_BASED_FIELDS.has(fieldName)) {
      payload[fieldName] = minutesValue;
    }

    if (TIME_FIELDS_IN_MINUTES.has(fieldName) || HOUR_BASED_FIELDS.has(fieldName)) {
      if (minutesValue < TIME_MINUTES_MIN || minutesValue > TIME_MINUTES_MAX) {
        validationErrors[fieldName] = "Invalid input (must be between 0-1440 minutes)";
      }
    }

    if (fieldName === "heart_rate") {
      if (rawValue < HEART_RATE_MIN || rawValue > HEART_RATE_MAX) {
        validationErrors[fieldName] = "Heart rate must be between 0-250 bpm";
      }
    }

    if (shouldShowErrors && validationErrors[fieldName]) {
      setFieldError(input, validationErrors[fieldName]);
    } else if (shouldShowErrors) {
      clearFieldError(input);
    }
  });

  const isValid = Object.keys(validationErrors).length === 0;

  if (isValid && applyNormalization) {
    normalizeScreenTimeDistribution(payload);

    if (syncNormalizedValuesToForm) {
      SCREEN_DISTRIBUTION_FIELDS.forEach((fieldName) => {
        if (!(fieldName in payload)) return;
        const fieldInput = formEl.querySelector(`input[name='${fieldName}']`);
        if (!fieldInput) return;
        fieldInput.value = formatInputValue(payload[fieldName]);
      });
      updateCalculations(formEl, modelName);
    }
  }

  return { isValid, payload, validationErrors };
}

function syncSubmitButtonState(formEl, modelName) {
  if (!formEl) return;
  const button = formEl.querySelector("button[type='button']");
  if (!button) return;

  const validation = validateAndPreparePayload(modelName, formEl, { showErrors: true });
  button.disabled = !validation.isValid;
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

function sanitizeMinutesForDisplay(value) {
  return Math.max(TIME_MINUTES_MIN, Math.min(TIME_MINUTES_MAX, Math.round(toNumber(value))));
}

function formatMinutesForDisplay(value) {
  const totalMinutes = sanitizeMinutesForDisplay(value);
  if (totalMinutes < 60) {
    return `${totalMinutes} min`;
  }

  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  if (minutes === 0) {
    return `${(hours).toFixed(1)} hrs`;
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

function formatHighlightFieldValue(fieldKey, value, formatter) {
  const numericValue = toNumber(value);

  if (HIGHLIGHT_TIME_FIELDS_MINUTES.has(fieldKey) || HOUR_BASED_FIELDS.has(fieldKey)) {
    return formatMinutesForDisplay(numericValue);
  }

  switch (formatter) {
    case "steps":
      return `${Math.round(Math.max(0, numericValue)).toLocaleString()} steps`;
    case "count":
      return `${Math.round(Math.max(0, numericValue)).toLocaleString()}`;
    default:
      return formatFieldValue(numericValue, formatter);
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
    input.addEventListener("input", () => {
      updateCalculations(formEl, modelName);
      syncSubmitButtonState(formEl, modelName);
    });
    input.addEventListener("change", () => {
      updateCalculations(formEl, modelName);
      syncSubmitButtonState(formEl, modelName);
    });
  });
  updateCalculations(formEl, modelName);
  syncSubmitButtonState(formEl, modelName);
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

function collectStudyFormData() {
  return {
    screen_time: toNumber(document.getElementById("screen_time")?.value),
    productive_usage: toNumber(document.getElementById("productive_usage")?.value),
    social_usage: toNumber(document.getElementById("social_usage")?.value),
    gaming_usage: toNumber(document.getElementById("gaming_usage")?.value),
    notifications: toNumber(document.getElementById("notifications")?.value),
    unlock_count: toNumber(document.getElementById("unlock_count")?.value),
    study_hours: toNumber(document.getElementById("study_hours")?.value),
    app_switching_frequency: toNumber(document.getElementById("app_switching_frequency")?.value),
    notifications_during_study: toNumber(document.getElementById("notifications_during_study")?.value),
    break_frequency: toNumber(document.getElementById("break_frequency")?.value),
    phone_usage_during_study: toNumber(document.getElementById("phone_usage_during_study")?.value),
    completed_tasks: toNumber(document.getElementById("completed_tasks")?.value),
  };
}

async function postPredict(endpoint, data) {
  const res = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    cache: "no-store",
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
      // If no data, use stored defaults or generate new
      const storedDefaults = localStorage.getItem(`habitcheck_defaults_${modelName}`);
      let defaults = config.defaults;
      if (storedDefaults) {
        defaults = JSON.parse(storedDefaults);
      }
      Object.entries(defaults).forEach(([key, value]) => {
        setVal(key, value);
      });
      if (loadingEl) loadingEl.textContent = `Using default values.`;
    } else {
      Object.entries(config.fieldMap || {}).forEach(([sourceKey, inputId]) => {
        if (data[sourceKey] !== undefined) {
          setVal(inputId, data[sourceKey]);
        }
      });
    }

    if (document.getElementById("unlock_count") && !document.getElementById("unlock_count").value) {
      setVal("unlock_count", 0);
    }

    // Populate any remaining empty inputs with realistic random defaults.
    fillEmptyFieldsWithRandom(modelName);

    if (loadingEl) loadingEl.classList.add("hidden");
    if (formEl) formEl.classList.remove("hidden");
    updateCalculations(formEl, modelName);
  } catch (err) {
    // Fallback to defaults
    const storedDefaults = localStorage.getItem(`habitcheck_defaults_${modelName}`);
    let defaults = config.defaults;
    if (storedDefaults) {
      defaults = JSON.parse(storedDefaults);
    }
    Object.entries(defaults).forEach(([key, value]) => {
      setVal(key, value);
    });
    if (loadingEl) {
      loadingEl.textContent = `Using default values.`;
      loadingEl.classList.add("hidden");
    }
    if (formEl) formEl.classList.remove("hidden");

    // Populate any remaining empty inputs with realistic random defaults.
    fillEmptyFieldsWithRandom(modelName);

    updateCalculations(formEl, modelName);
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

  const validation = validateAndPreparePayload(modelName, formEl, {
    showErrors: true,
    applyNormalization: true,
    syncNormalizedValuesToForm: true,
  });

  if (!validation.isValid) {
    if (statusEl) statusEl.textContent = "Please fix the highlighted fields before submitting.";
    syncSubmitButtonState(formEl, modelName);
    return;
  }

  if (button) button.disabled = true;
  if (statusEl) statusEl.textContent = "Running prediction...";

  try {
    const inputs = validation.payload;

    console.info(`[HabitCheck] ${modelName} request payload`, inputs);
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
    if (button) {
      syncSubmitButtonState(formEl, modelName);
    }
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

function getChartData(modelName, result, inputs = {}) {
  const contributions = result?.contributions || {};
  const labels = Object.keys(contributions);
  const values = Object.values(contributions).map((value) => roundToTwoDecimals(value));
  const colors = labels.map((key) => MODEL_CONFIGS[modelName]?.colors?.[key] || "#00d4ff");

  const stepsInput = toNumber(inputs.steps ?? inputs.steps_today);
  const stepsPresent = labels.includes("steps") || labels.includes("steps_today");
  if (stepsInput > 0 && !stepsPresent) {
    labels.push("steps");
    values.push(roundToTwoDecimals(stepsInput / 100));
    colors.push(
      MODEL_CONFIGS[modelName]?.colors?.steps ||
      MODEL_CONFIGS[modelName]?.colors?.steps_today ||
      "#34d399"
    );
  }

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
      <div class="metric-value">${formatHighlightFieldValue(fact.key, inputs[fact.key], fact.formatter)}</div>
    `;
    wrap.appendChild(card);
  });
}

function generateRecommendations(data) {
  const recommendations = [];

  const addUnique = (text) => {
    if (!recommendations.includes(text)) {
      recommendations.push(text);
    }
  };

  const screenBeforeSleep = sanitizeMinutesForDisplay(data?.screen_time_before_sleep);
  const nightNotifications = Math.max(0, Math.round(toNumber(data?.notifications_night ?? data?.night_notifications)));
  const sleepMinutes = sanitizeMinutesForDisplay(data?.sleep_hours);
  const steps = Math.max(0, Math.round(toNumber(data?.steps ?? data?.steps_today)));

  if (screenBeforeSleep > 60) {
    addUnique("Reduce screen time before bed to improve sleep quality.");
  }

  if (nightNotifications > 50) {
    addUnique("Consider silencing notifications at night to avoid sleep disruption.");
  }

  if ((sleepMinutes / 60) < 6) {
    addUnique("Increase sleep duration to at least 6–8 hours for better recovery.");
  }

  if (steps > 0 && steps < 3000) {
    addUnique("Try to increase daily movement for better health.");
  }

  if (!recommendations.length) {
    addUnique("Your habits are balanced. Keep maintaining this routine.");
  }

  return recommendations.slice(0, 4);
}

function renderRecommendations(result, inputs = {}) {
  const list = document.getElementById("recommendationList");
  if (!list) return;
  list.innerHTML = "";

  const items = generateRecommendations(inputs);
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    list.appendChild(li);
  });
}

function renderListItems(targetId, items, fallbackText) {
  const list = document.getElementById(targetId);
  if (!list) return;
  list.innerHTML = "";
  const values = Array.isArray(items) && items.length ? items : [fallbackText];
  values.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    list.appendChild(li);
  });
}

function renderDigitalMindMirror(result) {
  const mirror = result?.digital_mind_mirror || {};
  const points = mirror?.points || [];
  renderListItems("digitalMindMirrorList", points, "Behavior reflection is being generated from your latest inputs.");

  const patternEl = document.getElementById("digitalMindMirrorPattern");
  if (!patternEl) return;
  const possiblePattern = mirror?.possible_pattern || "No dominant behavioral pattern was detected for this snapshot.";
  patternEl.textContent = `Possible pattern detected: ${possiblePattern}`;
}

function renderBehaviorInsights(result) {
  renderListItems(
    "behaviorInsightsList",
    result?.behavior_insights || [],
    "No strong drift marker detected; behavior appears relatively balanced."
  );
}

function renderHabitDetection(result) {
  renderListItems(
    "habitDetectionList",
    result?.habit_detection || [],
    "No high-risk habit signal detected from current inputs."
  );
}

function getRiskBadgeClass(riskLevel) {
  const label = String(riskLevel || "").toLowerCase();
  if (label.includes("low")) return "status-low";
  if (label.includes("high")) return "status-high";
  if (label.includes("elevated")) return "status-moderate";
  if (label.includes("moderate")) return "status-moderate";
  return "status-normal";
}

function renderRiskIndicator(result) {
  const risk = result?.risk_indicator || {};
  const level = risk?.risk_level || "Moderate Risk";
  const score = toNumber(risk?.risk_score);

  const badge = document.getElementById("riskIndicatorBadge");
  if (badge) {
    badge.className = `status-pill ${getRiskBadgeClass(level)}`;
    badge.textContent = level;
  }

  const scoreEl = document.getElementById("riskScoreText");
  if (scoreEl) {
    scoreEl.textContent = `Risk score: ${toOneDecimal(score)} / 100`;
  }
}

function renderAIExplanation(result) {
  const el = document.getElementById("aiExplanationText");
  if (!el) return;
  el.textContent = result?.ai_explanation || result?.explanation || "Your prediction is influenced by multiple lifestyle factors from this input set.";
}

function renderBehaviorSummary(result) {
  const el = document.getElementById("behaviorSummaryText");
  if (!el) return;
  el.textContent = result?.behavior_summary || "Your current behavior snapshot shows mixed strengths and opportunities for better recovery.";
}

function renderChart(modelName, result, inputs = {}) {
  const canvas = document.getElementById("resultsChart");
  if (!canvas || typeof Chart === "undefined") return;

  if (window.habitCheckChart) {
    window.habitCheckChart.destroy();
  }

  const { labels, values, colors } = getChartData(modelName, result, inputs);
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
        legend: { display: true, position: "bottom", labels: { color: "rgba(255,255,255,0.82)" } },
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

async function fetchWeeklyForResults() {
  try {
    const res = await fetch("/api/dashboard", { cache: "no-store" });
    const data = await res.json();
    if (data?.error) return null;
    return data?.weekly || null;
  } catch (_error) {
    return null;
  }
}

function renderModuleCanvasChart(targetKey, canvasId, config) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || typeof Chart === "undefined") return;

  if (window[targetKey]) {
    window[targetKey].destroy();
  }

  const baseOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: { grid: { display: false }, ticks: { color: "rgba(255,255,255,0.7)" } },
      y: { grid: { color: "rgba(255,255,255,0.08)" }, ticks: { color: "rgba(255,255,255,0.7)" } },
    },
    plugins: {
      legend: { position: "bottom", labels: { color: "rgba(255,255,255,0.82)" } },
      tooltip: {
        callbacks: {
          label(context) {
            const dataset = context.dataset || {};
            const rawData = Array.isArray(dataset.rawData) ? dataset.rawData : null;
            const rawValue = rawData ? rawData[context.dataIndex] : context.parsed?.y;
            const type = dataset.rawType || "value";

            if (type === "hours") {
              return `${dataset.label}: ${toOneDecimal(rawValue)} hrs`;
            }
            if (type === "minutes") {
              return `${dataset.label}: ${Math.round(toNumber(rawValue))} min`;
            }
            if (type === "steps") {
              return `${dataset.label}: ${Math.round(toNumber(rawValue)).toLocaleString()} steps`;
            }
            if (type === "score") {
              return `${dataset.label}: ${toOneDecimal(rawValue)}`;
            }

            return `${dataset.label}: ${toOneDecimal(rawValue)}`;
          },
        },
      },
    },
  };

  const mergedOptions = {
    ...baseOptions,
    ...(config.options || {}),
    scales: {
      ...baseOptions.scales,
      ...((config.options && config.options.scales) || {}),
      y: {
        ...baseOptions.scales.y,
        ...((config.options && config.options.scales && config.options.scales.y) || {}),
      },
      x: {
        ...baseOptions.scales.x,
        ...((config.options && config.options.scales && config.options.scales.x) || {}),
      },
    },
    plugins: {
      ...baseOptions.plugins,
      ...((config.options && config.options.plugins) || {}),
      legend: {
        ...baseOptions.plugins.legend,
        ...((config.options && config.options.plugins && config.options.plugins.legend) || {}),
      },
      tooltip: {
        ...baseOptions.plugins.tooltip,
        ...((config.options && config.options.plugins && config.options.plugins.tooltip) || {}),
      },
    },
  };

  window[targetKey] = new Chart(canvas, {
    type: config.type,
    data: {
      labels: config.labels,
      datasets: config.datasets,
    },
    options: mergedOptions,
  });
}

function normalizeSeriesForComparison(values, maxValue) {
  const safeMax = Math.max(1, toNumber(maxValue));
  const rawData = (values || []).map((value) => Math.max(0, toNumber(value)));
  const normalizedData = rawData.map((value) => roundToTwoDecimals(Math.min(1, value / safeMax)));
  return { rawData, normalizedData };
}

async function renderModelSpecificCharts(modelName) {
  const section = document.getElementById("moduleChartsSection");
  if (!section) return;

  if (!["sleep", "study", "stress"].includes(modelName)) {
    section.classList.add("hidden");
    return;
  }

  const weekly = await fetchWeeklyForResults();
  const labels = weekly?.dates || [];
  if (!labels.length) {
    section.classList.add("hidden");
    return;
  }

  const sleepNormalized = normalizeSeriesForComparison(weekly?.sleep_hours || [], 8);
  const screenNormalized = normalizeSeriesForComparison(weekly?.screen_time || [], 600);
  const stepsNormalized = normalizeSeriesForComparison(weekly?.steps || [], 10000);
  const stressNormalized = normalizeSeriesForComparison(weekly?.stress || [], 100);

  const normalizedAxisOptions = {
    scales: {
      y: {
        min: 0,
        max: 1,
        grid: { color: "rgba(255,255,255,0.08)" },
        ticks: {
          color: "rgba(255,255,255,0.7)",
          stepSize: 0.2,
        },
      },
    },
  };

  const trendTitle = document.getElementById("moduleTrendTitle");
  const trendSubtitle = document.getElementById("moduleTrendSubtitle");
  const analysisTitle = document.getElementById("moduleAnalysisTitle");
  const analysisSubtitle = document.getElementById("moduleAnalysisSubtitle");

  const chartConfigs = {
    sleep: {
      trendTitle: "Sleep trend chart",
      trendSubtitle: "Daily sleep-hour trend across your latest 7-day window.",
      analysisTitle: "Sleep quality graph",
      analysisSubtitle: "Sleep and pre-bed screen load viewed together. Values normalized for comparison.",
      trend: {
        type: "line",
        labels,
        datasets: [
          {
            label: "Sleep hours",
            data: weekly.sleep_hours || [],
            borderColor: "rgba(250, 204, 21, 0.95)",
            backgroundColor: "rgba(250, 204, 21, 0.18)",
            fill: true,
            tension: 0.35,
            pointRadius: 3,
          },
        ],
      },
      analysis: {
        type: "bar",
        labels,
        datasets: [
          {
            label: "Sleep hours",
            data: sleepNormalized.normalizedData,
            rawData: sleepNormalized.rawData,
            rawType: "hours",
            backgroundColor: "rgba(250, 204, 21, 0.55)",
          },
          {
            label: "Screen time",
            data: screenNormalized.normalizedData,
            rawData: screenNormalized.rawData,
            rawType: "minutes",
            backgroundColor: "rgba(244, 114, 182, 0.55)",
          },
          {
            label: "Steps",
            data: stepsNormalized.normalizedData,
            rawData: stepsNormalized.rawData,
            rawType: "steps",
            backgroundColor: "rgba(52, 211, 153, 0.55)",
          },
        ],
        options: normalizedAxisOptions,
      },
    },
    study: {
      trendTitle: "Study contribution chart",
      trendSubtitle: "Focus pressure trend using screen exposure over the week.",
      analysisTitle: "Study breakdown chart",
      analysisSubtitle: "Distraction and activity balance aligned to study outcomes. Values normalized for comparison.",
      trend: {
        type: "line",
        labels,
        datasets: [
          {
            label: "Screen time",
            data: weekly.screen_time || [],
            borderColor: "rgba(34, 211, 238, 0.95)",
            backgroundColor: "rgba(34, 211, 238, 0.18)",
            fill: true,
            tension: 0.35,
            pointRadius: 3,
          },
        ],
      },
      analysis: {
        type: "bar",
        labels,
        datasets: [
          {
            label: "Screen time",
            data: screenNormalized.normalizedData,
            rawData: screenNormalized.rawData,
            rawType: "minutes",
            backgroundColor: "rgba(34, 211, 238, 0.55)",
          },
          {
            label: "Stress",
            data: stressNormalized.normalizedData,
            rawData: stressNormalized.rawData,
            rawType: "score",
            backgroundColor: "rgba(251, 113, 133, 0.55)",
          },
          {
            label: "Steps",
            data: stepsNormalized.normalizedData,
            rawData: stepsNormalized.rawData,
            rawType: "steps",
            backgroundColor: "rgba(52, 211, 153, 0.55)",
          },
        ],
        options: normalizedAxisOptions,
      },
    },
    stress: {
      trendTitle: "Stress trend graph",
      trendSubtitle: "Daily stress progression from your most recent week.",
      analysisTitle: "Stress analysis chart",
      analysisSubtitle: "Stress and sleep relationship for clearer risk context. Values normalized for comparison.",
      trend: {
        type: "line",
        labels,
        datasets: [
          {
            label: "Stress",
            data: weekly.stress || [],
            borderColor: "rgba(251, 113, 133, 0.95)",
            backgroundColor: "rgba(251, 113, 133, 0.18)",
            fill: true,
            tension: 0.35,
            pointRadius: 3,
          },
        ],
      },
      analysis: {
        type: "bar",
        labels,
        datasets: [
          {
            label: "Stress",
            data: stressNormalized.normalizedData,
            rawData: stressNormalized.rawData,
            rawType: "score",
            backgroundColor: "rgba(251, 113, 133, 0.55)",
          },
          {
            label: "Sleep hours",
            data: sleepNormalized.normalizedData,
            rawData: sleepNormalized.rawData,
            rawType: "hours",
            backgroundColor: "rgba(250, 204, 21, 0.55)",
          },
          {
            label: "Steps",
            data: stepsNormalized.normalizedData,
            rawData: stepsNormalized.rawData,
            rawType: "steps",
            backgroundColor: "rgba(52, 211, 153, 0.55)",
          },
        ],
        options: normalizedAxisOptions,
      },
    },
  };

  const config = chartConfigs[modelName];
  if (!config) {
    section.classList.add("hidden");
    return;
  }

  if (trendTitle) trendTitle.textContent = config.trendTitle;
  if (trendSubtitle) trendSubtitle.textContent = config.trendSubtitle;
  if (analysisTitle) analysisTitle.textContent = config.analysisTitle;
  if (analysisSubtitle) analysisSubtitle.textContent = config.analysisSubtitle;

  section.classList.remove("hidden");
  renderModuleCanvasChart("habitCheckModuleTrendChart", "moduleTrendChart", config.trend);
  renderModuleCanvasChart("habitCheckModuleAnalysisChart", "moduleAnalysisChart", config.analysis);
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
  renderRecommendations(result || {}, inputs || {});
  renderChart(modelName, result || {}, inputs || {});
  renderBreakdown(modelName, result || {});
  renderDigitalMindMirror(result || {});
  renderBehaviorInsights(result || {});
  renderHabitDetection(result || {});
  renderRiskIndicator(result || {});
  renderAIExplanation(result || {});
  renderBehaviorSummary(result || {});
  renderModelSpecificCharts(modelName);

  // Generate new randomized defaults for next visit
  const newDefaults = {};
  Object.keys(config.defaults).forEach(key => {
    const range = config.ranges[key];
    if (range) {
      newDefaults[key] = generateRandomValue(range.min, range.max, range.decimals);
    } else {
      newDefaults[key] = config.defaults[key];
    }
  });
  localStorage.setItem(`habitcheck_defaults_${modelName}`, JSON.stringify(newDefaults));

  // Setup WhatsApp button
  const whatsappBtn = document.getElementById("whatsappButton");
  if (whatsappBtn) {
    const riskLevel = result?.risk_indicator?.risk_level || "Moderate Risk";
    const behaviorSummary = result?.behavior_summary || "Behavior summary unavailable.";
    const summary = `${config.resultsTitle}\nScore: ${meta.scoreText}\n${meta.explanation}\nRisk: ${riskLevel}\n\nBehavior Summary:\n${behaviorSummary}\n\nKey Inputs:\n${Object.entries(inputs).map(([k, v]) => `${prettifyKey(modelName, k)}: ${v}`).join('\n')}\n\nRecommendations:\n${(result?.recommendations || []).join('\n')}`;
    const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(summary)}`;
    whatsappBtn.href = whatsappUrl;
  }
}

function initPredictionPage(modelName) {
  const config = MODEL_CONFIGS[modelName];
  const formEl = document.getElementById(config.formId);
  if (!formEl) return;
  bindLiveInputUpdates(formEl, modelName);
  autoFillForm(modelName);
  syncSubmitButtonState(formEl, modelName);
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
