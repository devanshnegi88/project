// Sidebar toggle
function slidbar() {
  document.body.classList.toggle("open");
  const sliderBtn = document.getElementById("slider-btn");
  sliderBtn.textContent = document.body.classList.contains("open") ? "✖" : "☰";
}

// Mode switching
let manualMode = false;

function switchMode(mode) {
  manualMode = (mode === "manual");
  document.getElementById("manualSection").style.display = manualMode ? "block" : "none";
  document.getElementById("aiSection").style.display = manualMode ? "none" : "block";
  document.getElementById("aiScheduleContainer").style.display = "none";
  if (manualMode) loadManualSchedule();
  else resetTable();
}

// Add manual task
function addTask() {
  if (!manualMode) return;
  let day = document.getElementById("daySelect").value;
  let task = document.getElementById("taskInput").value.trim();
  if (!task) { alert("Please enter a task!"); return; }

  let rows = document.querySelectorAll("#plannerTable tbody tr");
  rows.forEach(row => {
    if (row.cells[0].innerText === day) {
      let tasksCell = row.cells[1];
      if (tasksCell.innerText === "No tasks") {
        tasksCell.innerHTML = createTaskItem(task, day);
      } else {
        tasksCell.innerHTML += " " + createTaskItem(task, day);
      }
    }
  });
  document.getElementById("taskInput").value = "";
  saveManualSchedule(); // Save after adding
}

// Create task item HTML
function createTaskItem(task, day) {
  const taskId = generateTaskId();
  return `<span class="task-item">${task}<button class="delete-task-btn" onclick="deleteTask('${taskId}', '${day}')" title="Delete task">✖</button></span>`;
}

function generateTaskId() {
  return "task_" + Date.now() + "_" + Math.random().toString(36).substr(2, 5);
}

// Delete a single task
function deleteTask(taskId, day) {
  let rows = document.querySelectorAll("#plannerTable tbody tr");
  rows.forEach(row => {
    if (row.cells[0].innerText === day) {
      let tasksCell = row.cells[1];
      let taskItems = tasksCell.querySelectorAll(".task-item");
      taskItems.forEach(item => {
        let deleteBtn = item.querySelector(".delete-task-btn");
        if (deleteBtn && deleteBtn.onclick.toString().includes(taskId)) {
          item.remove();
        }
      });
      if (tasksCell.innerHTML.trim() === "" || tasksCell.querySelectorAll(".task-item").length === 0) {
        tasksCell.innerHTML = "No tasks";
      }
    }
  });
  saveManualSchedule(); // Save after deletion
}

// Delete all tasks for a day
function deleteAllTasks(day) {
  if (confirm(`Are you sure you want to delete all tasks for ${day}?`)) {
    let rows = document.querySelectorAll("#plannerTable tbody tr");
    rows.forEach(row => {
      if (row.cells[0].innerText === day) {
        row.cells[1].innerHTML = "No tasks";
      }
    });
    saveManualSchedule(); // Save after deletion
  }
}

// Save manual schedule to backend
async function saveManualSchedule() {
  let rows = document.querySelectorAll("#plannerTable tbody tr");
  let schedule = {};
  rows.forEach(row => {
    let day = row.cells[0].innerText;
    let tasksCell = row.cells[1];
    let tasks = [];
    if (tasksCell.innerText !== "No tasks") {
      let taskItems = tasksCell.querySelectorAll(".task-item");
      taskItems.forEach(item => {
        let taskText = item.childNodes[0].textContent.trim();
        if (taskText) tasks.push(taskText);
      });
    }
    schedule[day] = tasks;
  });

  try {
    const res = await fetch("/planner/save_manual_schedule", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ schedule })
    });
    const data = await res.json();
    // Optionally show a message: alert(data.message || "✅ Manual schedule saved!");
  } catch (err) {
    alert("Error saving schedule.");
  }
}

async function loadManualSchedule() {
  try {
    const res = await fetch("/planner/get_manual_schedule");
    const data = await res.json();
    resetTable();
    let rows = document.querySelectorAll("#plannerTable tbody tr");
    rows.forEach(row => {
      let day = row.cells[0].innerText;
      if (data[day] && data[day].length > 0) {
        let tasksHtml = "";
        data[day].forEach(task => {
          tasksHtml += createTaskItem(task, day) + " ";
        });
        row.cells[1].innerHTML = tasksHtml.trim();
      }
    });
  } catch (err) {
    // No schedule found
  }
}

// Clear manual schedule from backend
async function clearManualSchedule() {
  if (confirm("Are you sure you want to clear the entire schedule?")) {
    try {
      await fetch("/planner/clear_manual_schedule", { method: "POST" });
      resetTable();
      alert("🗑 Manual schedule cleared!");
    } catch (err) {
      alert("Error clearing schedule.");
    }
  }
}

// Reset planner table
function resetTable() {
  let rows = document.querySelectorAll("#plannerTable tbody tr");
  rows.forEach(row => row.cells[1].innerHTML = "No tasks");
}

// Generate AI schedule using Gemini API via backend
async function generateAISchedule() {
  let subjects = document.getElementById("subjectsInput").value.split(",").map(s => s.trim());
  let hours = parseInt(document.getElementById("timeInput").value);

  if (!subjects[0] || !hours) {
    alert("Please enter subjects and hours per day!");
    return;
  }

  try {
    const res = await fetch("/planner/generate_ai_schedule", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ subjects, hours })
    });
    const data = await res.json();
    if (data.error) {
      alert(data.error);
      return;
    }

    // Parse AI schedule text and fill table
    fillTableWithAISchedule(data.schedule);

    // Optionally show the raw text in the <pre>
    document.getElementById("aiScheduleContainer").style.display = "block";
    document.getElementById("aiScheduleOutput").textContent = data.schedule;

    alert("🤖 AI schedule generated!");
  } catch (err) {
    alert("Error generating AI schedule.");
  }
}

// Helper to parse AI schedule text and fill table
function fillTableWithAISchedule(scheduleText) {
  // Example expected format:
  // Monday: Task1, Task2
  // Tuesday: Task3, Task4
  // ...
  const dayMap = {};
  const lines = scheduleText.split('\n');
  lines.forEach(line => {
    const match = line.match(/^([A-Za-z]+):\s*(.*)$/);
    if (match) {
      const day = match[1];
      const tasks = match[2].split(',').map(t => t.trim()).filter(t => t);
      dayMap[day] = tasks;
    }
  });

  let rows = document.querySelectorAll("#plannerTable tbody tr");
  rows.forEach(row => {
    let day = row.cells[0].innerText;
    if (dayMap[day] && dayMap[day].length > 0) {
      let tasksHtml = "";
      dayMap[day].forEach(task => {
        tasksHtml += createTaskItem(task, day) + " ";
      });
      row.cells[1].innerHTML = tasksHtml.trim();
    } else {
      row.cells[1].innerHTML = "No tasks";
    }
  });
}

// Connect buttons to functions
document.getElementById("manualBtn").onclick = () => switchMode('manual');
document.getElementById("aiBtn").onclick = () => switchMode('ai');
document.querySelector("button[onclick='addTask()']").onclick = addTask;
document.querySelector("button[onclick='saveManualSchedule()']").onclick = saveManualSchedule;
document.querySelector("button[onclick='clearManualSchedule()']").onclick = clearManualSchedule;
document.querySelector("button[onclick='generateAISchedule()']").onclick = generateAISchedule;

// On page load, default to manual mode
window.onload = function() {
  switchMode('manual');
};
