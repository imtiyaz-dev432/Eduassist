// document.addEventListener("DOMContentLoaded", function () {
//     const token = localStorage.getItem("access_token");
//     const role = localStorage.getItem("user_role");

//     // 1. Role-Based Security Check 🔥
//     if (!token) {
//         alert("Please login first!");
//         window.location.href = "teacher_login.html";
//         return;
//     }
    
//     if (role !== "teacher") {
//         alert("Access Denied! Only teachers can view this dashboard.");
//         window.location.href = "login.html"; // Redirect Owner back to admin login
//         return;
//     }

//     // Set Teacher Name if saved during login
//     const teacherData = JSON.parse(localStorage.getItem("teacher_data") || "{}");
//     if (teacherData.name) {
//         document.getElementById("welcomeName").textContent = `Welcome, ${teacherData.name}`;
//     }

//     const msgEl = document.getElementById("dashboardMessage");

//     // 2. Fetch Dashboard Data
//     async function fetchDashboard() {
//         try {
//             const response = await fetch("http://127.0.0.1:5000/teacher/dashboard/", {
//                 method: "GET",
//                 headers: { "Authorization": `Bearer ${token}` }
//             });
//             const result = await response.json();

//             if (response.ok && result.success) {
//                 const data = result.data;
                
//                 // Update Metrics
//                 document.getElementById("totalBatches").textContent = data.metrics.total_batches;
//                 document.getElementById("totalStudents").textContent = data.metrics.total_students;
//                 document.getElementById("pendingGrading").textContent = data.metrics.pending_grading;

//                 // Update Batches List
//                 const batchesList = document.getElementById("batchesList");
//                 batchesList.innerHTML = "";

//                 if (data.my_batches.length === 0) {
//                     batchesList.innerHTML = `<p style="text-align: center; color: #6b7280; width: 100%; padding: 20px;">${result.message}</p>`;
//                     return;
//                 }

//                 data.my_batches.forEach(batch => {
//                     const statusColor = batch.status === 'Active' ? '#10b981' : '#f59e0b';
                    
//                     // 🔥 FIX: Backend se aane wali exact ID ko handle karne ke liye
//                     const correctBatchId = batch.batch_id || batch.id;

//                     const div = document.createElement("div");
//                     div.className = "batch-card";
//                     div.innerHTML = `
//                         <div class="batch-header">
//                             <h4>${batch.batch_name}</h4>
//                             <span class="status-badge" style="background: ${statusColor}20; color: ${statusColor};">${batch.status || 'Active'}</span>
//                         </div>
//                         <p class="batch-details">🪑 Total Seats: ${batch.total_seats || 'N/A'}</p>
                        
//                         <div class="batch-actions" style="margin-top: 15px;">
//                             <!-- 🔥 YAHAN URL KO THEEK KIYA HAI (${correctBatchId} LAGAYA HAI) -->
//                             <button onclick="window.location.href='view_students.html?batch_id=${batch.batch_id}'" 
//         style="background: #4facfe; color: white; padding: 10px; width: 100%; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 14px;">
//     👥 View Students & Mark Attendance
// </button>    
//                      <!-- 🔥 DUSRA NAYA BUTTON: Assignments Ke Liye 🔥 -->
//     <button onclick="window.location.href='batch_assignments.html?batch_id=${correctBatchId}'" 
//             style="background: #10b981; color: white; padding: 10px; width: 100%; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 14px;">
//         📝 Manage Assignments
//     </button>
                         
                 
//                         </div>
//                     `;
//                     batchesList.appendChild(div);
//                 });

//             } else {
//                 msgEl.style.display = "block";
//                 msgEl.textContent = result.message || "Failed to load dashboard.";
//             }
//         } catch (error) {
//             console.error("Dashboard Fetch Error:", error);
//             msgEl.style.display = "block";
//             msgEl.textContent = "Server error! Cannot connect to backend.";
//         }
//     }

//     fetchDashboard();

//     // 3. Logout Function
//     window.logoutTeacher = function() {
//         if (confirm("Are you sure you want to log out?")) {
//             localStorage.removeItem("access_token");
//             localStorage.removeItem("user_role");
//             localStorage.removeItem("teacher_data");
//             window.location.href = "teacher_login.html";
//         }
//     };
// });




document.addEventListener("DOMContentLoaded", function () {
    const token = localStorage.getItem("access_token");
    const role = localStorage.getItem("user_role");

    // 1. Role-Based Security Check 🔥
    if (!token) {
        alert("Please login first!");
        window.location.href = "teacher_login.html";
        return;
    }
    
    if (role !== "teacher") {
        alert("Access Denied! Only teachers can view this dashboard.");
        window.location.href = "login.html"; // Redirect Owner back to admin login
        return;
    }

    // Set Teacher Name if saved during login
    const teacherData = JSON.parse(localStorage.getItem("teacher_data") || "{}");
    if (teacherData.name) {
        document.getElementById("welcomeName").textContent = `Welcome, ${teacherData.name}`;
    }

    const msgEl = document.getElementById("dashboardMessage");

    // 2. Fetch Dashboard Data
    async function fetchDashboard() {
        try {
            const response = await fetch("http://127.0.0.1:5000/teacher/dashboard/", {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });
            const result = await response.json();

            if (response.ok && result.success) {
                const data = result.data;
                
                // Update Metrics
                document.getElementById("totalBatches").textContent = data.metrics.total_batches;
                document.getElementById("totalStudents").textContent = data.metrics.total_students;
                document.getElementById("pendingGrading").textContent = data.metrics.pending_grading;

                // Update Batches List
                const batchesList = document.getElementById("batchesList");
                batchesList.innerHTML = "";

                if (data.my_batches.length === 0) {
                    batchesList.innerHTML = `<p style="text-align: center; color: #6b7280; width: 100%; padding: 20px;">${result.message}</p>`;
                    return;
                }

                data.my_batches.forEach(batch => {
                    const statusColor = batch.status === 'Active' ? '#10b981' : '#f59e0b';
                    
                    // 🔥 FIX: Backend se aane wali exact ID (batch_id ya id) ko secure karna
                    const correctBatchId = batch.batch_id || batch.id;

                    const div = document.createElement("div");
                    div.className = "batch-card";
                    div.innerHTML = `
                        <div class="batch-header">
                            <h4>${batch.batch_name}</h4>
                            <span class="status-badge" style="background: ${statusColor}20; color: ${statusColor};">${batch.status || 'Active'}</span>
                        </div>
                        <p class="batch-details">🪑 Total Seats: ${batch.total_seats || 'N/A'}</p>
                        
                        <div class="batch-actions" style="margin-top: 15px; display: flex; flex-direction: column; gap: 8px;">
                            
                            <!-- 1. View Students & Attendance Button -->
                            <button onclick="window.location.href='view_students.html?batch_id=${correctBatchId}'" 
                                style="background: #4facfe; color: white; padding: 10px; width: 100%; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 14px;">
                                👥 View Students & Mark Attendance
                            </button>    
                            
                            <!-- 2. Manage Assignments Button -->
                            <button onclick="window.location.href='batch_assignment.html?batch_id=${correctBatchId}'" 
                                style="background: #10b981; color: white; padding: 10px; width: 100%; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 14px;">
                                📝 Manage Assignments
                            </button>

                            <!-- 🔥 3. NAYA BUTTON: Manage Quizzes Ke Liye 🔥 -->
                            <button onclick="window.location.href='teacher_quizzes.html?batch_id=${correctBatchId}'" 
                                style="background: #8b5cf6; color: white; padding: 10px; width: 100%; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 14px;">
                                ⏱️ Manage Quizzes
                            </button>
                             
                        </div>
                    `;
                    batchesList.appendChild(div);
                });

            } else {
                msgEl.style.display = "block";
                msgEl.textContent = result.message || "Failed to load dashboard.";
            }
        } catch (error) {
            console.error("Dashboard Fetch Error:", error);
            msgEl.style.display = "block";
            msgEl.textContent = "Server error! Cannot connect to backend.";
        }
    }

    fetchDashboard();

    // 3. Logout Function
    window.logoutTeacher = function() {
        if (confirm("Are you sure you want to log out?")) {
            localStorage.removeItem("access_token");
            localStorage.removeItem("user_role");
            localStorage.removeItem("teacher_data");
            window.location.href = "teacher_login.html";
        }
    };
});