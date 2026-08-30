document.addEventListener("DOMContentLoaded", function () {
    const token = localStorage.getItem("access_token");
    const role = localStorage.getItem("user_role") || localStorage.getItem("role");

    // Strictly check for Teacher role
    if (!token || role !== "teacher") {
        alert("Access Denied! Teacher login required.");
        window.location.href = "login.html";
        return;
    }

    const API_BASE = "http://127.0.0.1:5000/teacher/owner/assessments/assignment";
    
    const msgBox = document.getElementById("msgBox");
    const batchSelect = document.getElementById("batchSelect");
    const grid = document.getElementById("assignmentsGrid");
    const addBtn = document.getElementById("openAddModalBtn");

    function showAlert(message, isSuccess) {
        msgBox.style.display = "block";
        msgBox.style.background = isSuccess ? "#dcfce7" : "#fee2e2";
        msgBox.style.color = isSuccess ? "#16a34a" : "#dc2626";
        msgBox.textContent = message;
        setTimeout(() => msgBox.style.display = "none", 4000);
    }

    // ==========================================
    // 1. FETCH ONLY ASSIGNED BATCHES FOR TEACHER
    // ==========================================
    async function fetchBatches() {
        try {
            // Yahan wahi secure route use hoga jo sirf is teacher ke batches laayega
            const BATCH_API_URL = "http://127.0.0.1:5000/owner/academics/batch/teacher/my-batches";
            
            const response = await fetch(BATCH_API_URL, {
                headers: { "Authorization": `Bearer ${token}` }
            });
            const data = await response.json();
            
            if (response.ok && data.success) {
                batchSelect.innerHTML = '<option value="">-- Select Your Assigned Batch --</option>';
                
                if (data.batches.length === 0) {
                    batchSelect.innerHTML = '<option value="">No batches assigned to you yet.</option>';
                    return;
                }

                data.batches.forEach(b => {
                    batchSelect.innerHTML += `<option value="${b.id}">${b.batch_name} (${b.batch_code || 'N/A'})</option>`;
                });
            } else {
                batchSelect.innerHTML = '<option value="">❌ Failed to load your batches</option>';
            }
        } catch (e) {
            console.error("Batch API Error: ", e);
            batchSelect.innerHTML = '<option value="">❌ Network error loading batches</option>';
        }
    }

    // ==========================================
    // 2. LIST ASSIGNMENTS (GET /list/<batch_id>)
    // ==========================================
    window.loadAssignments = async function() {
        const batchId = batchSelect.value;
        if (!batchId) {
            addBtn.style.display = "none";
            grid.innerHTML = '<p style="text-align: center; width: 100%; grid-column: 1/-1;">Please select a batch.</p>';
            return;
        }

        addBtn.style.display = "block"; 
        grid.innerHTML = '<p style="text-align: center; width: 100%; grid-column: 1/-1;">Loading assignments...</p>';

        try {
            const response = await fetch(`${API_BASE}/list/${batchId}`, {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });
            const data = await response.json();

            if (response.ok && data.success) {
                if (data.assignments.length === 0) {
                    grid.innerHTML = '<p style="text-align: center; width: 100%; grid-column: 1/-1;">No assignments found for this batch.</p>';
                    return;
                }
                
                grid.innerHTML = "";
                data.assignments.forEach(a => {
                    grid.innerHTML += `
                        <div class="card">
                            <span class="badge">${a.status}</span>
                            <h3 class="card-title">${a.title}</h3>
                            <div class="card-meta">
                                <strong>Due:</strong> ${a.due_date || 'No Date'}<br>
                                <strong>Marks:</strong> ${a.max_marks}
                            </div>
                            <div class="card-actions">
                                <button class="btn-view" onclick="viewPDF(${a.id})">📄 View File</button>
                                <button class="btn-replace" onclick="openReplaceModal(${a.id}, '${a.title.replace(/'/g, "\\'")}')">🔄 Replace PDF</button>
                            </div>
                        </div>
                    `;
                });
            } else {
                grid.innerHTML = `<p style="color:red; text-align: center; width: 100%; grid-column: 1/-1;">${data.message}</p>`;
            }
        } catch (error) {
            grid.innerHTML = '<p style="color:red; text-align: center; width: 100%; grid-column: 1/-1;">Network Error while fetching assignments!</p>';
        }
    };

    // ==========================================
    // 3. ADD ASSIGNMENT (POST /add/<batch_id>)
    // ==========================================
    document.getElementById("addAssignmentForm").addEventListener("submit", async function(e) {
        e.preventDefault();
        const batchId = batchSelect.value;
        const btn = document.getElementById("submitAddBtn");
        
        const formData = new FormData();
        formData.append("title", document.getElementById("addTitle").value);
        formData.append("description", document.getElementById("addDesc").value);
        formData.append("due_date", document.getElementById("addDate").value); 
        formData.append("max_marks", document.getElementById("addMarks").value);
        formData.append("status", "Active");
        formData.append("file", document.getElementById("addFile").files[0]);

        btn.textContent = "Publishing...";
        btn.disabled = true;

        try {
            const response = await fetch(`${API_BASE}/add/${batchId}`, {
                method: "POST",
                headers: { "Authorization": `Bearer ${token}` },
                body: formData 
            });
            const data = await response.json();

            if (response.ok && data.success) {
                showAlert("✅ Assignment Created Successfully!", true);
                closeAddModal();
                loadAssignments(); 
            } else {
                showAlert("❌ Error: " + data.message, false);
            }
        } catch (error) {
            showAlert("❌ Network error while creating assignment!", false);
        } finally {
            btn.textContent = "Publish";
            btn.disabled = false;
        }
    });

    // ==========================================
    // 4. VIEW PDF (GET /file/<assignment_id>)
    // ==========================================
    window.viewPDF = async function(assignmentId) {
        try {
            const response = await fetch(`${API_BASE}/file/${assignmentId}`, {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });
            if (response.ok) {
                const blob = await response.blob();
                window.open(window.URL.createObjectURL(blob), '_blank');
            } else {
                const data = await response.json();
                showAlert("Error: " + data.message, false);
            }
        } catch (error) {
            showAlert("Network Error opening PDF.", false);
        }
    };

    // ==========================================
    // 5. REPLACE PDF (PATCH /file/replace/<assignment_id>)
    // ==========================================
    document.getElementById("replaceFileForm").addEventListener("submit", async function(e) {
        e.preventDefault();
        const assignId = document.getElementById("replaceAssignId").value;
        const fileInput = document.getElementById("replaceFile").files[0];
        const btn = document.getElementById("submitReplaceBtn");

        const formData = new FormData();
        formData.append("file", fileInput);

        btn.textContent = "Updating...";
        btn.disabled = true;

        try {
            const response = await fetch(`${API_BASE}/file/replace/${assignId}`, {
                method: "PATCH", 
                headers: { "Authorization": `Bearer ${token}` },
                body: formData
            });
            const data = await response.json();

            if (response.ok && data.success) {
                showAlert("✅ PDF Replaced Successfully!", true);
                closeReplaceModal();
            } else {
                showAlert("❌ Error: " + data.message, false);
            }
        } catch (error) {
            showAlert("❌ Network error!", false);
        } finally {
            btn.textContent = "Update File";
            btn.disabled = false;
        }
    });

    // Modal Controls
    window.openAddModal = () => document.getElementById("addModal").style.display = "flex";
    window.closeAddModal = () => {
        document.getElementById("addModal").style.display = "none";
        document.getElementById("addAssignmentForm").reset();
    };

    window.openReplaceModal = (id, title) => {
        document.getElementById("replaceAssignId").value = id;
        document.getElementById("replaceAssignTitle").textContent = "Assignment: " + title;
        document.getElementById("replaceModal").style.display = "flex";
    };
    window.closeReplaceModal = () => {
        document.getElementById("replaceModal").style.display = "none";
        document.getElementById("replaceFileForm").reset();
    };

    // Logout
    document.getElementById("logoutBtn").addEventListener("click", () => {
        if(confirm("Are you sure you want to logout?")) {
            localStorage.clear();
            window.location.href = "teacher_login.html";
        }
    });

    fetchBatches();
});