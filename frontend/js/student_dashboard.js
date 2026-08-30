// document.addEventListener("DOMContentLoaded", function () {
//     const token = localStorage.getItem("access_token");
//     const role = localStorage.getItem("user_role");

//     // 1. Security Check 🔥
//     if (!token) {
//         alert("Please login first!");
//         window.location.href = "student_login.html";
//         return;
//     }
    
//     if (role !== "student") {
//         alert("Access Denied! Only students can view this dashboard.");
//         window.location.href = "login.html"; // Owner/Teacher ko bahar nikalo
//         return;
//     }

//     const msgEl = document.getElementById("dashboardMessage");

//     // 2. Fetch Dashboard Data
//     async function fetchDashboard() {
//         try {
//             const response = await fetch("http://127.0.0.1:5000/student/dashboard", {
//                 method: "GET",
//                 headers: { 
//                     "Authorization": `Bearer ${token}` 
//                 }
//             });
//             const result = await response.json();

//             if (response.ok && result.success) {
//                 const data = result;

//                 // --- A. Profile & Header ---
//                 document.getElementById("welcomeName").textContent = `Welcome, ${data.student.student_name.split(" ")[0]}`;
//                 document.getElementById("studentName").textContent = data.student.student_name;
//                 document.getElementById("instituteName").textContent = data.institution.name ? `Institute: ${data.institution.name}` : "Institute: Not Assigned";
//                 document.getElementById("courseName").textContent = data.course.course_name ? `Course: ${data.course.course_name}` : "Course: N/A";
//                 document.getElementById("batchName").textContent = data.batch.batch_name ? `Batch: ${data.batch.batch_name}` : "Batch: N/A";

//                 // --- B. Attendance Summary ---
//                 const att = data.attendance_summary;
//                 document.getElementById("attPercentage").textContent = `${att.attendance_percentage}%`;
//                 document.getElementById("attPresent").textContent = att.present;
//                 document.getElementById("attAbsent").textContent = att.absent;
//                 document.getElementById("attLate").textContent = att.late;

//                 // --- C. Fee Summary ---
//                 const fee = data.fee_summary;
//                 document.getElementById("feeDue").textContent = `₹${fee.due_amount}`;
//                 document.getElementById("feeTotal").textContent = `₹${fee.total_fee}`;
//                 document.getElementById("feePaid").textContent = `₹${fee.paid_amount}`;
//                 document.getElementById("feeStatus").textContent = fee.status;
                
//                 // Smart Alert for Due Fees
//                 if (fee.is_due) {
//                     document.getElementById("feeAlert").style.display = "inline-block";
//                     document.getElementById("feeDue").style.color = "#ef4444"; // Red text if due
//                 } else {
//                     document.getElementById("feeDue").style.color = "#10b981"; // Green text if cleared
//                 }

//                 // --- D. Assignments Summary ---
//                 const assign = data.assignment_summary;
//                 document.getElementById("assignPending").textContent = assign.pending_assignments;
//                 document.getElementById("assignTotal").textContent = assign.total_assignments;
//                 document.getElementById("assignSubmitted").textContent = assign.submitted_assignments;

//                 // Smart Alert for Pending Assignments
//                 if (assign.has_pending) {
//                     document.getElementById("assignmentAlert").style.display = "inline-block";
//                 }

//             } else {
//                 msgEl.style.display = "block";
//                 msgEl.style.color = "#ef4444";
//                 msgEl.textContent = result.message || "Failed to load dashboard data.";
//             }
//         } catch (error) {
//             console.error("Dashboard Fetch Error:", error);
//             msgEl.style.display = "block";
//             msgEl.style.color = "#ef4444";
//             msgEl.textContent = "Server error! Cannot connect to backend.";
//         }
//     }

//     fetchDashboard();

//     // 3. Logout Function
//     window.logoutStudent = async function() {
//         if (confirm("Are you sure you want to log out?")) {
//             try {
//                 // Call backend logout route
//                 await fetch("http://127.0.0.1:5000/student_auth/logout", {
//                     method: "POST",
//                     headers: { "Authorization": `Bearer ${token}` }
//                 });
//             } catch (e) {
//                 console.log("Logout API failed, but clearing local storage.");
//             }
//             // Clear local storage and redirect
//             localStorage.removeItem("access_token");
//             localStorage.removeItem("user_role");
//             localStorage.removeItem("student_data");
//             window.location.href = "student_login.html";
//         }
//     };
// });




document.addEventListener("DOMContentLoaded", function () {
    const token = localStorage.getItem("access_token");
    const role = localStorage.getItem("user_role");

    // 1. Security Check 🔥
    if (!token) {
        alert("Please login first!");
        window.location.href = "student_login.html";
        return;
    }
    
    if (role !== "student") {
        alert("Access Denied! Only students can view this dashboard.");
        window.location.href = "login.html"; // Owner/Teacher ko bahar nikalo
        return;
    }

    const msgEl = document.getElementById("dashboardMessage");

    // Helper safe updater to avoid 'TypeError: Cannot set properties of null'
    function safeSetText(elementId, text) {
        const el = document.getElementById(elementId);
        if (el) el.textContent = text;
    }

    function safeSetDisplay(elementId, displayValue) {
        const el = document.getElementById(elementId);
        if (el) el.style.display = displayValue;
    }

    function safeSetColor(elementId, colorValue) {
        const el = document.getElementById(elementId);
        if (el) el.style.color = colorValue;
    }

    // 2. Fetch Dashboard Data
    async function fetchDashboard() {
        try {
            const response = await fetch("http://127.0.0.1:5000/student/dashboard", {
                method: "GET",
                headers: { 
                    "Authorization": `Bearer ${token}` 
                }
            });
            const result = await response.json();

            if (response.ok && result.success) {
                const data = result;

                // --- A. Profile & Header ---
                const firstName = data.student && data.student.student_name ? data.student.student_name.split(" ")[0] : "Student";
                safeSetText("welcomeName", `Welcome, ${firstName}`);
                safeSetText("studentName", data.student && data.student.student_name ? data.student.student_name : "N/A");
                safeSetText("instituteName", data.institution && data.institution.name ? `Institute: ${data.institution.name}` : "Institute: Not Assigned");
                safeSetText("courseName", data.course && data.course.course_name ? `Course: ${data.course.course_name}` : "Course: N/A");
                safeSetText("batchName", data.batch && data.batch.batch_name ? `Batch: ${data.batch.batch_name}` : "Batch: N/A");

                // --- B. Attendance Summary ---
                const att = data.attendance_summary || {};
                safeSetText("attPercentage", `${att.attendance_percentage || 0}%`);
                safeSetText("attPresent", att.present || 0);
                safeSetText("attAbsent", att.absent || 0);
                safeSetText("attLate", att.late || 0);

                // --- C. Fee Summary ---
                const fee = data.fee_summary || {};
                safeSetText("feeDue", `₹${fee.due_amount || 0}`);
                safeSetText("feeTotal", `₹${fee.total_fee || 0}`);
                safeSetText("feePaid", `₹${fee.paid_amount || 0}`);
                safeSetText("feeStatus", fee.status || "N/A");
                
                // Smart Alert for Due Fees
                if (fee.is_due) {
                    safeSetDisplay("feeAlert", "inline-block");
                    safeSetColor("feeDue", "#ef4444"); // Red text if due
                } else {
                    safeSetColor("feeDue", "#10b981"); // Green text if cleared
                }

                // --- D. Assignments Summary ---
                const assign = data.assignment_summary || {};
                safeSetText("assignPending", assign.pending_assignments || 0);
                safeSetText("assignTotal", assign.total_assignments || 0);
                safeSetText("assignSubmitted", assign.submitted_assignments || 0);

                // Smart Alert for Pending Assignments
                if (assign.has_pending) {
                    safeSetDisplay("assignmentAlert", "inline-block");
                }

            } else {
                if (msgEl) {
                    msgEl.style.display = "block";
                    msgEl.style.color = "#ef4444";
                    msgEl.textContent = result.message || "Failed to load dashboard data.";
                }
            }
        } catch (error) {
            console.error("Dashboard Fetch Error:", error);
            if (msgEl) {
                msgEl.style.display = "block";
                msgEl.style.color = "#ef4444";
                msgEl.textContent = "Server error! Cannot connect to backend.";
            }
        }
    }

    fetchDashboard();

    // 3. Logout Function
    window.logoutStudent = async function() {
        if (confirm("Are you sure you want to log out?")) {
            try {
                await fetch("http://127.0.0.1:5000/student_auth/logout", {
                    method: "POST",
                    headers: { "Authorization": `Bearer ${token}` }
                });
            } catch (e) {
                console.log("Logout API failed, but clearing local storage.");
            }
            localStorage.removeItem("access_token");
            localStorage.removeItem("user_role");
            localStorage.removeItem("student_data");
            window.location.href = "student_login.html";
        }
    };
});