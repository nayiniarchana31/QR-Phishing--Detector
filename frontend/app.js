const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const previewArea = document.getElementById("preview-area");
const previewImg = document.getElementById("preview-img");
const clearBtn = document.getElementById("clear-btn");
const scanBtn = document.getElementById("scan-btn");
const loader = document.getElementById("loader");
const resultSection = document.getElementById("result-section");
const errorBox = document.getElementById("error-box");

let selectedFile = null;

dropZone.addEventListener("click", () => fileInput.click());

dropZone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropZone.classList.add("drag-over");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("drag-over");
});

dropZone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropZone.classList.remove("drag-over");
  const file = event.dataTransfer.files[0];
  if (file) loadFile(file);
});

fileInput.addEventListener("change", () => {
  if (fileInput.files[0]) loadFile(fileInput.files[0]);
});

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
}

function hideError() {
  errorBox.textContent = "";
  errorBox.classList.add("hidden");
}

function loadFile(file) {
  hideError();
  if (!file.type.startsWith("image/")) {
    showError("Please upload an image file.");
    return;
  }

  selectedFile = file;
  const reader = new FileReader();
  reader.onload = (event) => {
    previewImg.src = event.target.result;
    previewArea.classList.remove("hidden");
  };
  reader.readAsDataURL(file);
  scanBtn.disabled = false;
  resultSection.classList.add("hidden");
}

clearBtn.addEventListener("click", () => {
  selectedFile = null;
  fileInput.value = "";
  previewImg.removeAttribute("src");
  previewArea.classList.add("hidden");
  resultSection.classList.add("hidden");
  scanBtn.disabled = true;
  hideError();
});

scanBtn.addEventListener("click", async () => {
  if (!selectedFile) {
    showError("Please select a QR code image first.");
    return;
  }

  hideError();
  loader.classList.remove("hidden");
  scanBtn.disabled = true;

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      body: formData
    });
    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.detail || "Prediction request failed.");
    }
    renderResult(result);
  } catch (error) {
    showError(error.message || "Could not connect to the backend.");
  } finally {
    loader.classList.add("hidden");
    scanBtn.disabled = false;
  }
});

function renderResult(data) {
  const badge = document.getElementById("verdict-badge");
  const isPhishing = Boolean(data.is_phishing);

  badge.className = `verdict-badge ${isPhishing ? "phishing" : "safe"}`;
  document.getElementById("verdict-icon").textContent = isPhishing ? "⚠️" : "✓";
  document.getElementById("verdict-text").textContent =
    isPhishing ? "PHISHING DETECTED" : "LEGITIMATE URL (MODEL PREDICTION)";

  // Use textContent rather than innerHTML for untrusted URL text.
  document.getElementById("decoded-url").textContent = data.url;
  document.getElementById("conf-label").textContent =
    `${(data.confidence * 100).toFixed(1)}%`;
  document.getElementById("safe-prob").textContent =
    `${(data.safe_probability * 100).toFixed(1)}%`;
  document.getElementById("danger-prob").textContent =
    `${(data.phishing_probability * 100).toFixed(1)}%`;

  const bar = document.getElementById("conf-bar");
  bar.style.width = `${data.confidence * 100}%`;
  bar.className = `bar-fill ${isPhishing ? "phishing" : "safe"}`;

  const tbody = document.getElementById("feat-tbody");
  tbody.replaceChildren();
  Object.entries(data.features || {}).forEach(([name, value]) => {
    const row = document.createElement("tr");
    const nameCell = document.createElement("td");
    const valueCell = document.createElement("td");
    nameCell.textContent = name;
    valueCell.textContent = String(value);
    row.append(nameCell, valueCell);
    tbody.appendChild(row);
  });

  resultSection.classList.remove("hidden");
}
