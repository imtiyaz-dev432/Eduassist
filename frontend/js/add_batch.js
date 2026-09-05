// ==========================================================================
// Global Scope Functions (Edit & Delete handlers)
// ==========================================================================
let isEditMode = false;
let editBatchId = null;

window.fillEditForm = function (batch) {
    isEditMode = true;
    editBatchId = batch.id;

    const formTitle = document.querySelector(".form-card h3");
    const formSub = document.querySelector(".form-card .subtitle");
    const submitBtn = document.getElementById("saveBatchBtn");
    const cancelEditBtn = document.getElementById("cancelEditBtn");

    if (formTitle) formTitle.textContent = "Update Batch";
    if (formSub) formSub.textContent = "Modify details for " + batch.batch_name;

    document.getElementById("batchName").value = batch.batch_name || "";
    document.getElementById("courseSelect").value = batch.course_id || "";
    document.getElementById("teacherSelect").value = batch.teacher_id || "";
    document.getElementById("startTime").value = batch.start_time || "";
    document.getElementById("endTime").value = batch.end_time || "";

    if (submitBtn) {
        submitBtn.textContent = "Update Batch";
        submitBtn.style.background = "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)";
    }
    if (cancelEditBtn) cancelEditBtn.style.display = "inline-block";
    window.scrollTo({ top: 0, behavior: "smooth" });
};

window.cancelEdit = function () {
    isEditMode = false;
    editBatchId = null;
    const batchForm = document.getElementById("batchForm");
    const submitBtn = document.getElementById("saveBatchBtn");
    const cancelEditBtn = document.getElementById("cancelEditBtn");

    if (batchForm) batchForm.reset();

    const formTitle = document.querySelector(".form-card h3");
    const formSub = document.querySelector(".form-card .subtitle");
    if (formTitle) formTitle.textContent = "Step 4: Create Batches";
    if (formSub) formSub.textContent = "Assign a Teacher and a Course to create a new Batch.";

    if (submitBtn) {
        submitBtn.textContent = "Create Batch";
        submitBtn.style.background = "linear-gradient(135deg, #1e3a8a, #0ea5e9)";
    }
    if (cancelEditBtn) cancelEditBtn.style.display = "none";
};

window.deleteBatch = async function (id) {
    const token = localStorage.getItem("access_token");
    if (!confirm("Are you sure you want to delete this batch?")) return;

    try {
        const response = await fetch(`http://127.0.0.1:5000/owner/academics/batch/delete/${id}`, {
            method: "DELETE",
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (response.ok) {
            if (typeof window.reloadBatches === "function") {
                window.reloadBatches();
            } else {
                window.location.reload();
            }
        } else {
            alert("Failed to delete batch.");
        }
    } catch (error) {
        alert("Error deleting batch.");
    }
};

// ==========================================================================
// DOM Initialization & Main Flow
// ==========================================================================
document.addEventListener("DOMContentLoaded", function () {
    // 1. Security Check
    const token = localStorage.getItem("access_token");
    if (!token || token === "null") {
        alert("Please login first!");
        window.location.href = "login.html";
        return;
    }

    // 2. Strict ID Resolution (URL priority, phir localStorage. NO '|| 1')
    const urlParams = new URLSearchParams(window.location.search);
    let instituteId = urlParams.get("institution_id") || urlParams.get("inst_id") || localStorage.getItem("institution_id") || localStorage.getItem("coaching_id");

    // Strict Validation: ID agar invalid/missing ho toh redirection
    if (!instituteId || instituteId === "null" || instituteId === "undefined" || isNaN(instituteId)) {
        console.error("Invalid Institute ID:", instituteId);
        localStorage.removeItem("institution_id");
        alert("Institute ID missing! Please select your coaching institute.");
        window.location.href = "add_institute.html";
        return;
    }

    // ID ko clean state mein lock karein
    localStorage.setItem("institution_id", instituteId);

    // 🔥 URL AUTO-SYNC: Agar URL mein ID nahi hai ya galat key hai, toh URL bar ko automatically correct karein bina page reload kiye
    if (urlParams.get("institution_id") !== instituteId) {
        const cleanUrl = `${window.location.pathname}?institution_id=${instituteId}`;
        window.history.replaceState(null, "", cleanUrl);
    }

    // 3. Navbar Links Dynamic Injection
    const courseLink = document.getElementById("navCourseLink");
    const batchLink = document.getElementById("navBatchLink");
    const faqLink = document.getElementById("navFaqLink");

    if (courseLink) courseLink.href = `add_course.html?institution_id=${instituteId}`;
    if (batchLink) batchLink.href = `add_batch.html?institution_id=${instituteId}`;
    if (faqLink) faqLink.href = `add_faq.html?institution_id=${instituteId}`;

    // 4. Safe Global Logout
    const logoutBtn = document.getElementById("globalLogoutBtn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            if (confirm("Are you sure you want to log out?")) {
                localStorage.clear();
                window.location.href = "login.html";
            }
        });
    }

    // 5. Elements Reference
    const batchForm = document.getElementById("batchForm");
    const msgEl = document.getElementById("formMessage");
    const submitBtn = document.getElementById("saveBatchBtn");
    const batchesList = document.getElementById("batchesList");
    const courseSelect = document.getElementById("courseSelect");
    const teacherSelect = document.getElementById("teacherSelect");

    function showMsg(text, type) {
        if (!msgEl) return;
        msgEl.textContent = text;
        msgEl.className = `message ${type}`;
        msgEl.style.display = "block";
        setTimeout(() => {
            msgEl.style.display = "none";
            msgEl.className = "message";
        }, 4000);
    }

    // 6. Load Courses & Teachers for Dropdowns
    async function loadDropdowns() {
        try {
            // A. Load Courses
            const courseRes = await fetch(`http://127.0.0.1:5000/owner/academics/courses/get/${instituteId}`, {
                headers: { "Authorization": `Bearer ${token}` }
            });
            const courseData = await courseRes.json();
            if (courseSelect) {
                courseSelect.innerHTML = '<option value="">-- Select Course --</option>';
                if (courseRes.ok && courseData.courses) {
                    courseData.courses.forEach(c => {
                        courseSelect.innerHTML += `<option value="${c.id}">${c.course_name}</option>`;
                    });
                }
            }

            // B. Load Teachers
            const teacherRes = await fetch(`http://127.0.0.1:5000/teacher/get/${instituteId}`, {
                headers: { "Authorization": `Bearer ${token}` }
            });
            const teacherData = await teacherRes.json();
            if (teacherSelect) {
                teacherSelect.innerHTML = '<option value="">-- Assign Teacher --</option>';
                if (teacherRes.ok && teacherData.teacher_list) {
                    if (teacherData.teacher_list.length === 0) {
                        teacherSelect.innerHTML += '<option value="" disabled>No teachers found. Add a teacher first!</option>';
                    } else {
                        teacherData.teacher_list.forEach(t => {
                            teacherSelect.innerHTML += `<option value="${t.id}">${t.name}</option>`;
                        });
                    }
                }
            }
        } catch (error) {
            console.error("Error loading dropdowns:", error);
        }
    }

    // 7. Fetch & Display Active Batches
    async function fetchBatches() {
        try {
            const response = await fetch(`http://127.0.0.1:5000/owner/academics/batch/get/${instituteId}`, {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });
            const data = await response.json();

            if (!batchesList) return;

            if (response.ok && data.batches) {
                batchesList.innerHTML = "";
                if (data.batches.length === 0) {
                    batchesList.innerHTML = `<p class="loading-text">No batches created yet. Create your first batch above.</p>`;
                    return;
                }

                data.batches.forEach(batch => {
                    const div = document.createElement("div");
                    div.className = "batch-item";

                    div.innerHTML = `
                        <div class="batch-info">
                            <h4>${batch.batch_name} <span style="font-size:12px; background:#e0f2fe; color:#0284c7; padding:2px 8px; border-radius:8px; margin-left:8px;">🕒 ${batch.start_time || 'N/A'} - ${batch.end_time || 'N/A'}</span></h4>
                            <p>Course ID: ${batch.course_id} | Teacher ID: ${batch.teacher_id}</p>
                        </div>
                        <div style="display: flex; gap: 8px; align-items: center;">
                            <button style="background: #10b981; color: white; padding: 8px 14px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 13px;" 
                                    onclick="window.location.href='add_student.html?batch_id=${batch.id}&institution_id=${instituteId}'">
                                👨‍🎓 Students
                            </button>
                            <button class="lock-btn" onclick='fillEditForm(${JSON.stringify(batch).replace(/'/g, "&#39;")})'>✏️ Edit</button>
                            <button class="del-btn" onclick="deleteBatch(${batch.id})">🗑️ Delete</button>
                        </div>
                    `;
                    batchesList.appendChild(div);
                });
            } else {
                batchesList.innerHTML = `<p style="color:#ef4444; text-align:center;">Failed to load batches.</p>`;
            }
        } catch (error) {
            if (batchesList) {
                batchesList.innerHTML = `<p style="color:#ef4444; text-align:center;">Server error fetching batches.</p>`;
            }
        }
    }

    window.reloadBatches = fetchBatches;

    loadDropdowns();
    fetchBatches();

    // 8. Create or Update Batch Form Submission
    if (batchForm) {
        batchForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = isEditMode ? "Updating Batch..." : "Creating Batch...";
            }

            const selectedCourseId = document.getElementById("courseSelect").value;
            if (!selectedCourseId) {
                alert("Please select a course!");
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = isEditMode ? "Update Batch" : "Create Batch";
                }
                return;
            }

            const payload = {
                batch_name: document.getElementById("batchName").value.trim(),
                teacher_id: document.getElementById("teacherSelect").value,
                start_time: document.getElementById("startTime").value,
                end_time: document.getElementById("endTime").value,
                mode: "Offline"
            };

            const apiUrl = isEditMode
                ? `http://127.0.0.1:5000/owner/academics/batch/update/${editBatchId}`
                : `http://127.0.0.1:5000/owner/academics/batch/add/${selectedCourseId}`;

            const apiMethod = isEditMode ? "PATCH" : "POST";

            try {
                const response = await fetch(apiUrl, {
                    method: apiMethod,
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`
                    },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();

                if (response.ok || data.success) {
                    showMsg(isEditMode ? "Batch Updated Successfully!" : "Batch Created Successfully!", "success");
                    batchForm.reset();
                    window.cancelEdit();
                    fetchBatches();
                } else {
                    showMsg(data.message || "Failed to save batch.", "error");
                }
            } catch (error) {
                showMsg("Server connection error!", "error");
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = isEditMode ? "Update Batch" : "Create Batch";
                }
            }
        });
    }
});