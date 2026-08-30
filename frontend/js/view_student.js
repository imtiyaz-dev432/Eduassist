document.addEventListener("DOMContentLoaded", function () {
    const token = localStorage.getItem("access_token");
    const role = localStorage.getItem("user_role");

    // 1. Auth Check
    if (!token || role !== "teacher") {
        alert("Access Denied! Please login as a teacher.");
        window.location.href = "teacher_login.html";
        return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    const batchId = urlParams.get("batch_id");

    if (!batchId || batchId === "undefined" || batchId === "null") {
        alert("Batch ID missing! Going back to dashboard.");
        window.location.href = "teacher_dashboard.html";
        return;
    }

    // Set today's date default
    document.getElementById("attendanceDate").value = new Date().toISOString().split('T')[0];

    // 2. Fetch Students list
    async function fetchBatchStudents() {
        try {
            // URL MATCH: GET /teacher/batch/<batch_id>/students
            const response = await fetch(`http://127.0.0.1:5000/teacher/batch/${batchId}/students`, {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });
            
            const data = await response.json();
            const tbody = document.getElementById("studentBody");
            tbody.innerHTML = ""; 

            document.getElementById("batchNameDisplay").textContent = data.batch_name || `Batch #${batchId}`;

            if (!data.students || data.students.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #ef4444; padding: 20px;">No students enrolled in this batch yet.</td></tr>`;
                document.getElementById("saveBtn").style.display = "none";
                return;
            }

            data.students.forEach(student => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td><b>${student.id}</b></td>
                    <td style="color: #1f2937; font-weight: 600;">${student.name}</td>
                    <td>${student.mobile_no || 'N/A'}</td>
                    <td>
                        <div class="att-options">
                            <label class="att-p">
                                <input type="radio" name="att_${student.id}" value="Present" checked> (P) Present
                            </label>
                            <label class="att-a">
                                <input type="radio" name="att_${student.id}" value="Absent"> (A) Absent
                            </label>
                        </div>
                    </td>
                    <td>
                        <button class="btn-sm btn-history" onclick="viewHistory(${student.id}, '${student.name}')">🕒 History & Edit</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });

        } catch (error) {
            console.error("Error fetching students:", error);
            document.getElementById("studentBody").innerHTML = `<tr><td colspan="5" style="text-align: center; color: red;">Failed to connect to backend server.</td></tr>`;
        }
    }

    fetchBatchStudents();

    // 3. Mark Bulk Attendance (POST)
    document.getElementById("saveBtn").addEventListener("click", async () => {
        const date = document.getElementById("attendanceDate").value;
        if (!date) return alert("Please select a date!");

        const rows = document.querySelectorAll("#studentBody tr");
        const fetchPromises = []; 
        let totalStudents = 0;
        
        rows.forEach(row => {
            const studentIdNode = row.querySelector("td:first-child b");
            if (!studentIdNode) return;
            
            const sId = parseInt(studentIdNode.textContent);
            const statusNode = row.querySelector(`input[name="att_${sId}"]:checked`);
            
            if (statusNode) {
                totalStudents++;
                // Backend requirements: attendance_date, status
                const payload = { attendance_date: date, status: statusNode.value };

                // URL MATCH: POST /teacher/operation/attendance/mark/<student_id>
                const request = fetch(`http://127.0.0.1:5000/teacher/operation/attendance/mark/${sId}`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`
                    },
                    body: JSON.stringify(payload)
                }).then(res => res.json()); 

                fetchPromises.push(request);
            }
        });

        if (fetchPromises.length === 0) return alert("No student data found to save!");

        const saveBtn = document.getElementById("saveBtn");
        const msgBox = document.getElementById("msgBox");
        saveBtn.textContent = "Saving...";
        saveBtn.disabled = true;

        try {
            const results = await Promise.all(fetchPromises);
            let successCount = 0, alreadyMarkedCount = 0, errorCount = 0;

            results.forEach(result => {
                if (result.message === "Attendance marked successfully") successCount++;
                else if (result.message === "Attendance already marked for this student on this date") alreadyMarkedCount++;
                else errorCount++;
            });

            msgBox.style.display = "block";
            if (successCount > 0 && errorCount === 0) {
                msgBox.style.background = "#dcfce7";
                msgBox.style.color = "#16a34a";
                msgBox.textContent = `✅ Success! Saved for ${successCount} students.` + (alreadyMarkedCount > 0 ? ` (${alreadyMarkedCount} were already marked)` : "");
                setTimeout(() => { msgBox.style.display = "none"; }, 4000);
            } else if (alreadyMarkedCount === totalStudents) {
                msgBox.style.background = "#fef9c3";
                msgBox.style.color = "#ca8a04";
                msgBox.textContent = "⚠️ Attendance is already marked for all students on this date!";
            } else {
                msgBox.style.background = "#fee2e2";
                msgBox.style.color = "#dc2626";
                msgBox.textContent = `❌ Saved: ${successCount} | Failed: ${errorCount} | Already Marked: ${alreadyMarkedCount}`;
            }
        } catch (error) {
            alert("Server error! Cannot connect to backend.");
        } finally {
            saveBtn.textContent = "💾 Save Attendance";
            saveBtn.disabled = false;
        }
    });

    // ==========================================
    // HISTORY, EDIT (PATCH), DELETE LOGIC
    // ==========================================

    let currentStudentId = null; 

    // Open Modal and Fetch Data
    window.viewHistory = async function(studentId, studentName) {
        currentStudentId = studentId;
        document.getElementById("modalStudentName").textContent = `History: ${studentName}`;
        document.getElementById("historyModal").style.display = "block";
        await loadStudentHistory(studentId);
    };

    // Close Modal
    window.closeModal = function() {
        document.getElementById("historyModal").style.display = "none";
    };

    // Fetch History (GET)
    async function loadStudentHistory(studentId) {
        const tbody = document.getElementById("historyBody");
        tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;">Loading records...</td></tr>`;

        try {
            // URL MATCH: GET /teacher/operation/attendance/get/<student_id>
            const response = await fetch(`http://127.0.0.1:5000/teacher/operation/attendance/get/${studentId}`, {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });
            const data = await response.json();

            tbody.innerHTML = "";
            if (!data.records || data.records.length === 0) {
                tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color: #6b7280;">No attendance records found.</td></tr>`;
                return;
            }

            data.records.forEach(record => {
                let statusColor = record.status === "Present" ? "#16a34a" : (record.status === "Absent" ? "#dc2626" : "#ca8a04");
                
                tbody.innerHTML += `
                    <tr>
                        <td><b>${record.attendance_date}</b></td>
                        <td style="color: ${statusColor}; font-weight: bold;">${record.status}</td>
                        <td style="color: #6b7280; font-size: 13px;">${record.remarks || "-"}</td>
                        <td>
                            <button class="btn-sm btn-edit" onclick="editAttendance(${record.id}, '${record.status}')">✏️ Edit</button>
                            <button class="btn-sm btn-delete" onclick="deleteAttendance(${record.id})">🗑️ Delete</button>
                        </td>
                    </tr>
                `;
            });
        } catch (error) {
            tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color: red;">Error fetching history.</td></tr>`;
        }
    }

    // Edit Attendance (PATCH)
    window.editAttendance = async function(attendanceId, currentStatus) {
        const newStatus = prompt(`Enter new status (Present, Absent, Late, Leave):`, currentStatus);
        if (!newStatus || newStatus === currentStatus) return;

        try {
            // URL MATCH: PATCH /teacher/operation/attendance/update/<attendance_id>
            const response = await fetch(`http://127.0.0.1:5000/teacher/operation/attendance/update/${attendanceId}`, {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({ status: newStatus }) // Backend allows just updating status
            });

            const result = await response.json();
            if (response.ok || result.success) {
                loadStudentHistory(currentStudentId); // Refresh table silently
            } else {
                alert("❌ Update failed: " + result.message);
            }
        } catch (error) {
            alert("❌ Server error during update.");
        }
    };

    // Delete Attendance (DELETE)
    window.deleteAttendance = async function(attendanceId) {
        if (!confirm("Are you sure you want to delete this record?")) return;

        try {
            // URL MATCH: DELETE /teacher/operation/attendance/delete/<attendance_id>
            const response = await fetch(`http://127.0.0.1:5000/teacher/operation/attendance/delete/${attendanceId}`, {
                method: "DELETE",
                headers: { "Authorization": `Bearer ${token}` }
            });

            const result = await response.json();
            if (response.ok || result.success) {
                loadStudentHistory(currentStudentId); // Refresh table silently
            } else {
                alert("❌ Delete failed: " + result.message);
            }
        } catch (error) {
            alert("❌ Server error during deletion.");
        }
    };
});