
// Store tasks temporarily (from backend or newly added)
let tasks = [];

async function loadReminders() {
  const tbody = document.getElementById("reminderTableBody");
  tbody.innerHTML = ""; // clear old content
  try {
    const res = await fetch("/reminders/api"); // backend API
    const reminders = await res.json();
    const now = new Date();

    const activeTasks = reminders.filter(r => new Date(r.time) > now); // only active

    if (!activeTasks.length) {
      tbody.innerHTML = `<tr><td colspan="3" id="no-tasks-msg">No reminders yet</td></tr>`;
      return;
    }

    activeTasks.forEach(renderTask);
  } catch (err) {
    console.error(err);
    tbody.innerHTML = `<tr><td colspan="3">Error loading reminders</td></tr>`;
  }
}

// Render a single task in the table
function renderTask(task) {
  const tbody = document.getElementById("reminderTableBody");
  const tr = document.createElement("tr");
  tr.id = "task-" + task._id;
  tr.innerHTML = `
    <td>${task.title}</td>
    <td>${new Date(task.time).toLocaleString()}</td>

    <td>
      <button class="delete-btn" onclick="deleteReminder('${task._id}')">✖ Delete</button>
    </td>
  `;
  tbody.appendChild(tr);
}

// Add new task
async function addTask() {
  const title = document.getElementById("task-title").value;
  const time = document.getElementById("task-deadline").value;
  if (!title || !time) { alert("Please enter title and deadline"); return; }

  const res = await fetch("/reminders/add", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, time })
  });

  if (res.ok) {
    const newTask = await res.json(); // backend returns added task
    document.getElementById("no-tasks-msg")?.remove();
    renderTask(newTask); // render immediately
    document.getElementById("task-title").value = "";
    document.getElementById("task-deadline").value = "";
  } else {
    alert("Failed to add reminder");
  }
}

// Delete task
async function deleteReminder(id) {
  const res = await fetch(`/reminders/${id}`, { method: "DELETE" });
  if (res.ok) {
    document.getElementById("task-" + id).remove();
    // If no tasks left, show "No reminders yet"
    if (document.getElementById("reminderTableBody").children.length === 0) {
      document.getElementById("reminderTableBody").innerHTML = `<tr><td colspan="3" id="no-tasks-msg">No reminders yet</td></tr>`;
    }
  }
}

// Load reminders when page loads
window.onload = loadReminders;

// Sidebar toggle (unchanged)
function slidbar() {
  document.body.classList.toggle("open");  
  const sliderBtn = document.getElementById("slider-btn");
  if (document.body.classList.contains("open")) {
    sliderBtn.textContent = "✖";
  } else {
    sliderBtn.textContent = "☰";
  }
}
// ---------- Real-time updates & auto-expiry ----------

// Auto-refresh reminders every 5 seconds and remove expired tasks from table
setInterval(() => {
  const now = new Date();
  const tbody = document.getElementById("reminderTableBody");
  
  Array.from(tbody.children).forEach(row => {
    const deadlineCell = row.children[1];
    if (deadlineCell) {
      const deadline = new Date(deadlineCell.textContent);
      if (deadline <= now) row.remove();
    }
  });

  // Fetch new active reminders from backend
  loadReminders();
}, 5000);

// Auto-clean expired reminders in MongoDB every 1 minute
async function cleanupExpiredReminders() {
  try {
    await fetch("/reminders/cleanup", { method: "POST" });
  } catch (err) {
    console.error("Failed to cleanup expired reminders:", err);
  }
}
setInterval(cleanupExpiredReminders, 5000);

