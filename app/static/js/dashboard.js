
// let studyChart, quizChart;

// async function loadStats() {
//   const res = await fetch("/api/stats");
//   const data = await res.json();

//   let hours = Math.floor(data.studyMinutes / 60);
//   let mins = data.studyMinutes % 60;
//   document.getElementById("studyTime").textContent = `${hours}h ${mins}m`;
//   document.getElementById("topics").textContent = data.topicsCompleted;
//   document.getElementById("quiz").textContent = data.quizPerformance + "%";
//   document.getElementById("focus").textContent = data.focusScore + " / 10";

//   if (studyChart) studyChart.destroy();
//   studyChart = new Chart(document.getElementById("studyTrend"), {
//     type: 'line',
//     data: {
//       labels: ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
//       datasets: [{
//         label: 'Study Minutes',
//         data: data.studyHistory,
//         borderColor: "#007bff",
//         backgroundColor: "rgba(0,123,255,0.2)",
//         tension: 0.3,
//         fill: true
//       }]
//     }
//   });

//   if (quizChart) quizChart.destroy();
//   quizChart = new Chart(document.getElementById("quizTrend"), {
//     type: 'bar',
//     data: {
//       labels: ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
//       datasets: [{
//         label: 'Quiz Performance %',
//         data: data.quizHistory,
//         backgroundColor: "#28a745"
//       }]
//     }
//   });
// }

// loadStats();
// setInterval(loadStats, 10000);

function slidbar() {
  document.body.classList.toggle("open");  
  const sliderBtn = document.getElementById("slider-btn");
  if (document.body.classList.contains("open")) {
    sliderBtn.textContent = "✖";
  } else {
    sliderBtn.textContent = "☰";
  }
}




// async function loadUserProgress() {
//   try {
//     // ✅ Call backend API
//     const res = await fetch("/api/user_progress");
//     if (!res.ok) throw new Error("Failed to fetch progress");

//     const data = await res.json();

//     // ✅ If no data (new user)
//     if (!data || Object.keys(data).length === 0) {
//       document.getElementById("studyTime").textContent = "--";
//       document.getElementById("topics").textContent = "--";
//       document.getElementById("quiz").textContent = "--";
//       document.getElementById("focus").textContent = "--";
//       return;
//     }

//     // ✅ Fill Dashboard values
//     let hours = Math.floor((data.studyMinutes || 0) / 60);
//     let mins = (data.studyMinutes || 0) % 60;
//     document.getElementById("studyTime").textContent = `${hours}h ${mins}m`;
//     document.getElementById("topics").textContent = data.topicsCompleted || 0;
//     document.getElementById("quiz").textContent = (data.quizPerformance || 0) + "%";
//     document.getElementById("focus").textContent = (data.focusScore || 0) + " / 10";

//     // ✅ Example additional fields (overall progress)
//     if (data.remindersCount !== undefined) {
//       let reminderCard = document.getElementById("reminderProgress");
//       if (reminderCard) {
//         reminderCard.textContent = data.remindersCount + " reminders";
//       }
//     }

//     // ✅ Update Charts
//     if (window.studyChart) studyChart.destroy();
//     studyChart = new Chart(document.getElementById("studyTrend"), {
//       type: 'line',
//       data: {
//         labels: ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
//         datasets: [{
//           label: 'Study Minutes',
//           data: data.studyHistory || [0,0,0,0,0,0,0],
//           borderColor: "#007bff",
//           backgroundColor: "rgba(0,123,255,0.2)",
//           tension: 0.3,
//           fill: true
//         }]
//       }
//     });

//     if (window.quizChart) quizChart.destroy();
//     quizChart = new Chart(document.getElementById("quizTrend"), {
//       type: 'bar',
//       data: {
//         labels: ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
//         datasets: [{
//           label: 'Quiz Performance %',
//           data: data.quizHistory || [0,0,0,0,0,0,0],
//           backgroundColor: "#28a745"
//         }]
//       }
//     });

//   } catch (err) {
//     console.error("⚠️ Error loading progress:", err);
//   }
// }

// // ⏳ Run when page loads
// loadUserProgress();
// setInterval(loadUserProgress, 15000); // refresh every 15s

let studyChart, quizChart;

async function loadUserProgress() {
    try {
        const res = await fetch("/api/user_progress");
        const data = await res.json();

        if (!data || Object.keys(data).length === 0) return;

        // --- Update Cards ---
        const hours = Math.floor((data.studyMinutes || 0) / 60);
        const mins = (data.studyMinutes || 0) % 60;
        document.getElementById("studyTime").textContent = `${hours}h ${mins}m`;
        document.getElementById("topics").textContent = data.topicsCompleted || 0;
        document.getElementById("quiz").textContent = (data.quizPerformance || 0) + "%";
        document.getElementById("focus").textContent = (data.focusScore || 0) + " / 10";

        // --- Update Study Chart ---
        if (studyChart) studyChart.destroy();
        studyChart = new Chart(document.getElementById("studyTrend"), {
            type: 'line',
            data: {
                labels: ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
                datasets: [{
                    label: 'Study Minutes',
                    data: data.studyHistory || [0,0,0,0,0,0,0],
                    borderColor: "#007bff",
                    backgroundColor: "rgba(0,123,255,0.2)",
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: true },
                    tooltip: { mode: 'index' }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });

        // --- Update Quiz Chart ---
        if (quizChart) quizChart.destroy();
        quizChart = new Chart(document.getElementById("quizTrend"), {
            type: 'bar',
            data: {
                labels: ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
                datasets: [{
                    label: 'Quiz Performance %',
                    data: data.quizHistory || [0,0,0,0,0,0,0],
                    backgroundColor: "#28a745"
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: true },
                    tooltip: { mode: 'index' }
                },
                scales: {
                    y: { beginAtZero: true, max: 100 }
                }
            }
        });

    } catch (err) {
        console.error("Error loading progress:", err);
    }
}

// Load on page load
loadUserProgress();

// Refresh every 15 seconds (optional)
setInterval(loadUserProgress, 15000);

let hours = Math.floor((data.studyMinutes || 0) / 60);
let mins = (data.studyMinutes || 0) % 60;
document.getElementById("studyTime").textContent = `${hours}h ${mins}m`;
document.getElementById("topics").textContent = data.topicsCompleted || 0;
document.getElementById("quiz").textContent = (data.quizPerformance || 0) + "%";
document.getElementById("focus").textContent = (data.focusScore || 0) + " / 10";

