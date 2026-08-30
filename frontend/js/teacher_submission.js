document.addEventListener("DOMContentLoaded", function () {
    const token = localStorage.getItem("access_token") || localStorage.getItem("token");
    const role = localStorage.getItem("user_role") || localStorage.getItem("role");

    // Security check: Teacher or Owner allowed
    if (!token || (role !== "teacher" && role !== "owner")) {
        alert("Access Denied! Teacher/Owner login required.");
        window.location.href = "login.html";
        return;
    }

    const API_BASE = "http://127.0.0.1:5000/teacher/owner/check"; 
    const tableBody = document.getElementById("submissionsTableBody");

    // Extract assignment_id from URL (e.g., page.html?assignment_id=12)
    const urlParams = new URLSearchParams(window.location.search);
    const assignmentId = urlParams.get('assignment_id');

    if (!assignmentId) {
        tableBody.innerHTML = `<tr><td colspan="5" style="color:red; text-align:center;">Error: Assignment ID missing in URL!</td></tr>`;
        return;
    }

    // ==========================================
    // 1. FETCH ALL SUBMISSIONS
    // ==========================================
    async function fetchSubmissions() {
        try {
            const response = await fetch(`${API_BASE}/${assignmentId}`, {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });
            const data = await response.json();

            if (response.ok && data.success) {
                if (data.submission_list.length === 0) {
                    tableBody.innerHTML = `<tr><td colspan="5" class="loading-text">No students have submitted this assignment yet.</td></tr>`;
                    return;
                }
                
                tableBody.innerHTML = ""; // Clear table
                
                data.submission_list.forEach(sub => {
                    // Badge coloring logic
                    let badgeClass = "badge-submitted";
                    if (sub.status === "Late Submitted") badgeClass = "badge-late";
                    if (sub.status === "Checked") badgeClass = "badge-checked";

                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td><strong>Student #${sub.student_id}</strong></td>
                        <td><span class="badge ${badgeClass}">${sub.status}</span></td>
                        <td>${sub.marks !== null ? sub.marks : "-"}</td>
                        <td>${sub.feedback ? sub.feedback : "-"}</td>
                        <td>
                            <button class="btn-view" onclick="viewPDF(${sub.id})">📄 View</button>
                            <button class="btn-grade" onclick="openGradeModal(${sub.id}, '${sub.marks || ''}', '${sub.feedback || ''}')">📝 Grade</button>
                        </td>
                    `;
                    tableBody.appendChild(tr);
                });
            } else {
                tableBody.innerHTML = `<tr><td colspan="5" style="color:red; text-align:center;">${data.message}</td></tr>`;
            }
        } catch (error) {
            console.error(error);
            tableBody.innerHTML = `<tr><td colspan="5" style="color:red; text-align:center;">Network error fetching submissions.</td></tr>`;
        }
    }

    // ==========================================
    // 2. VIEW STUDENT PDF
    // ==========================================
    window.viewPDF = async function(submissionId) {
        try {
            const response = await fetch(`${API_BASE}/file/${submissionId}`, {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });

            if (response.ok) {
                const blob = await response.blob();
                const fileUrl = window.URL.createObjectURL(blob);
                window.open(fileUrl, '_blank');
            } else {
                const data = await response.json();
                alert("Failed to load PDF: " + data.message);
            }
        } catch (error) {
            alert("Network error trying to open PDF.");
        }
    };

    // ==========================================
    // 3. GRADE SUBMISSION LOGIC
    // ==========================================
    window.openGradeModal = function(submissionId, currentMarks, currentFeedback) {
        document.getElementById("gradeSubmissionId").value = submissionId;
        document.getElementById("marksInput").value = currentMarks !== 'null' ? currentMarks : "";
        document.getElementById("feedbackInput").value = currentFeedback !== 'null' ? currentFeedback : "";
        
        let msgDiv = document.getElementById("gradeMessage");
        msgDiv.classList.add("hidden");

        document.getElementById("gradeModal").classList.remove("hidden");
    };

    window.closeGradeModal = function() {
        document.getElementById("gradeModal").classList.add("hidden");
    };

    window.submitGrade = async function() {
        const submissionId = document.getElementById("gradeSubmissionId").value;
        const marks = document.getElementById("marksInput").value;
        const feedback = document.getElementById("feedbackInput").value;
        const msgDiv = document.getElementById("gradeMessage");
        const btn = document.getElementById("submitGradeBtn");

        if (!marks) {
            msgDiv.innerText = "❌ Please enter marks.";
            msgDiv.className = "upload-msg block";
            msgDiv.style.backgroundColor = "#fee2e2";
            msgDiv.style.color = "#991b1b";
            msgDiv.classList.remove("hidden");
            return;
        }

        try {
            btn.innerText = "Saving...";
            btn.disabled = true;

            const response = await fetch(`${API_BASE}/${submissionId}`, {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({ marks: parseInt(marks), feedback: feedback })
            });

            const data = await response.json();

            if (response.ok) {
                msgDiv.innerText = "✅ " + data.message;
                msgDiv.className = "upload-msg block";
                msgDiv.style.backgroundColor = "#dcfce7";
                msgDiv.style.color = "#16a34a";
                msgDiv.classList.remove("hidden");
                
                setTimeout(() => {
                    closeGradeModal();
                    fetchSubmissions(); // Refresh the table
                }, 1000);
            } else {
                msgDiv.innerText = "❌ " + data.message;
                msgDiv.classList.remove("hidden");
            }
        } catch (error) {
            msgDiv.innerText = "❌ Network error.";
            msgDiv.classList.remove("hidden");
        } finally {
            btn.innerText = "Save Grade";
            btn.disabled = false;
        }
    };

    // Logout Function
    document.getElementById("logoutBtn").addEventListener("click", function() {
        if (confirm("Are you sure you want to log out?")) {
            localStorage.clear(); 
            window.location.href = "login.html";
        }
    });

    // Load initial data
    fetchSubmissions();
});