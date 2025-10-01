function slidbar() {
  document.body.classList.toggle("open");  
  const sliderBtn = document.getElementById("slider-btn");
  if (document.body.classList.contains("open")) {
    sliderBtn.style.display = "none";
  } else {
    sliderBtn.style.display = "inline-block";
  }
}

document.addEventListener("DOMContentLoaded", function() {
  const menuHeading = document.querySelector(".slider h2");
  menuHeading.addEventListener("click", function() {
    document.body.classList.remove("open");
    document.getElementById("slider-btn").style.display = "inline-block";
  });
});

// Toggle button logic
const localBtn = document.getElementById('localBtn');
const ytBtn = document.getElementById('ytBtn');
const localPanel = document.getElementById('localPanel');
const ytPanel = document.getElementById('ytPanel');
const localInput = document.getElementById('localVideo');
const processLocalBtn = document.getElementById('processLocalBtn');
const ytUrl = document.getElementById('ytUrl');
const ytError = document.getElementById('ytError');
const processYtBtn = document.getElementById('processYtBtn');
const summary = document.getElementById('summary');


const ytRegex = /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)[\w-]+/;

function switchMode(isYouTube) {
  if (isYouTube) {
    ytBtn.classList.add('active');
    localBtn.classList.remove('active');
    ytPanel.classList.add('active');
    localPanel.classList.remove('active');
  } else {
    localBtn.classList.add('active');
    ytBtn.classList.remove('active');
    localPanel.classList.add('active');
    ytPanel.classList.remove('active');
  }
  localInput.value = "";
  processLocalBtn.disabled = true;
  ytUrl.value = "";
  processYtBtn.disabled = true;
  ytError.style.display = "none";
  summary.value = "";
}

localBtn.addEventListener('click', () => switchMode(false));
ytBtn.addEventListener('click', () => switchMode(true));
switchMode(false);

localInput.addEventListener("change", () => {
  processLocalBtn.disabled = !localInput.files || localInput.files.length === 0;
});

function validateYouTube(url) {
  return ytRegex.test(url.trim());
}

ytUrl.addEventListener("input", () => {
  const value = ytUrl.value;
  const valid = validateYouTube(value);
  ytError.style.display = value && !valid ? "inline" : "none";
  processYtBtn.disabled = !valid;
});

// Process local video
processLocalBtn.addEventListener("click", async () => {
  const file = localInput.files[0];
  if (!file) return;
  summary.value = "Processing local file, please wait...";

  const formData = new FormData();
  formData.append("video", file);

  try {
    const res = await fetch("/notes_sumariser/summarise_local", {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    summary.value = data.summary || data.error || "No summary generated.";
  } catch (err) {
    summary.value = "Error processing video.";
  }
});

// Process YouTube link
processYtBtn.addEventListener("click", async () => {
  const link = ytUrl.value.trim();
  if (!validateYouTube(link)) return;
  summary.value = "Processing YouTube link, please wait...";

  try {
    const res = await fetch("/notes_sumariser/summarise_youtube", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: link })
    });
    const data = await res.json();
    summary.value = data.summary || data.error || "No summary generated.";
  } catch (err) {
    summary.value = "Error processing YouTube link.";
  }
});