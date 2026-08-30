// document.addEventListener("DOMContentLoaded", function () {
//     const token = localStorage.getItem("access_token");
//     if (!token) {
//         alert("Please login first!");
//         window.location.href = "login.html";
//         return;
//     }

//     const urlParams = new URLSearchParams(window.location.search);
//     const instituteId = urlParams.get("inst_id");

//     if (!instituteId) {
//         alert("Coaching ID missing!");
//         window.location.href = "add_institute.html";
//         return;
//     }

//     let isEditMode = false;
//     let editBatchId = null;

//     const batchForm = document.getElementById("batchForm");
//     const msgEl = document.getElementById("formMessage");
//     const submitBtn = document.getElementById("saveBatchBtn");
//     const cancelEditBtn = document.getElementById("cancelEditBtn");
//     const batchesList = document.getElementById("batchesList");
//     const courseSelect = document.getElementById("courseSelect");
//     const teacherSelect = document.getElementById("teacherSelect");

//     // --- 1. LOAD COURSES & TEACHERS FOR DROPDOWN ---
//     async function loadDropdowns() {
//         try {
//             // A. Load Courses
//             const courseRes = await fetch(`http://127.0.0.1:5000/owner/academics/courses/get/${instituteId}`, { 
//                 headers: { "Authorization": `Bearer ${token}` } 
//             });
//             const courseData = await courseRes.json();
//             courseSelect.innerHTML = '<option value="">-- Select Course --</option>';
//             if (courseRes.ok && courseData.courses) {
//                 courseData.courses.forEach(c => {
//                     courseSelect.innerHTML += `<option value="${c.id}">${c.course_name}</option>`;
//                 });
//             }

//             // B. Load Teachers
//             const teacherRes = await fetch(`http://127.0.0.1:5000/teacher/get/${instituteId}`, { 
//                 headers: { "Authorization": `Bearer ${token}` } 
//             });
//             const teacherData = await teacherRes.json();
//             teacherSelect.innerHTML = '<option value="">-- Assign Teacher --</option>';
            
//             if (teacherRes.ok && teacherData.teacher_list) {
//                 if (teacherData.teacher_list.length === 0) {
//                     teacherSelect.innerHTML += '<option value="" disabled>No teachers found. Add a teacher first!</option>';
//                 } else {
//                     teacherData.teacher_list.forEach(t => {
//                         teacherSelect.innerHTML += `<option value="${t.id}">${t.name}</option>`;
//                     });
//                 }
//             }
//         } catch (error) {
//             console.error("Error loading dropdowns:", error);
//         }
//     }

//     // --- 2. FETCH & DISPLAY BATCHES ---
//     async function fetchBatches() {
//         try {
//             const response = await fetch(`http://127.0.0.1:5000/owner/academics/batch/get/${instituteId}`, {
//                 method: "GET",
//                 headers: { "Authorization": `Bearer ${token}` }
//             });
//             const data = await response.json();

//             if (response.ok && data.batches) {
//                 batchesList.innerHTML = "";
//                 if (data.batches.length === 0) {
//                     batchesList.innerHTML = `<p style="text-align: center; color: #6b7280;">No batches created yet.</p>`;
//                     return;
//                 }
                
//                 data.batches.forEach(batch => {
//                     const div = document.createElement("div");
//                     div.className = "course-item"; 
                    
//                     // 🔥 Yahan par Batch details ke sath naya button add kiya gaya hai 🔥
//                     div.innerHTML = `
//                         <div class="course-info">
//                             <h4>${batch.batch_name} <span class="badge">🕒 ${batch.start_time || 'N/A'} - ${batch.end_time || 'N/A'}</span></h4>
//                             <p>Course ID: ${batch.course_id} | Teacher ID: ${batch.teacher_id}</p>
//                         </div>
//                         <div class="action-buttons">
//                             <!-- NAYA ADD STUDENT BUTTON -->
//                             <button style="background: #10b981; color: white; padding: 6px 12px; border: none; border-radius: 6px; cursor: pointer; font-weight: 500;" 
//                                     onclick="window.location.href='add_student.html?batch_id=${batch.id}'">
//                                 👨‍🎓 Add/View Students
//                             </button>
                            
//                             <button class="edit-btn" onclick='fillEditForm(${JSON.stringify(batch).replace(/'/g, "&#39;")})'>✏️ Edit</button>
//                             <button class="del-btn" onclick="deleteBatch(${batch.id})">🗑️ Delete</button>
//                         </div>
//                     `;
//                     batchesList.appendChild(div);
//                 });
//             }
//         } catch (error) {
//             batchesList.innerHTML = `<p style="color:red; text-align:center;">Failed to load batches.</p>`;
//         }
//     }

//     // Load initial data
//     loadDropdowns();
//     fetchBatches();

//     // --- 3. CREATE OR UPDATE BATCH ---
//     batchForm.addEventListener("submit", async (e) => {
//         e.preventDefault();
//         submitBtn.disabled = true;
//         submitBtn.textContent = isEditMode ? "Updating Batch..." : "Creating Batch...";

//         const payload = {
//             batch_name: document.getElementById("batchName").value.trim(),
//             teacher_id: document.getElementById("teacherSelect").value,
//             start_time: document.getElementById("startTime").value,
//             end_time: document.getElementById("endTime").value,
//             mode: "Offline" 
//         };

//         const selectedCourseId = document.getElementById("courseSelect").value;
//         if (!selectedCourseId) {
//             alert("Please select a course!");
//             submitBtn.disabled = false;
//             submitBtn.textContent = "Create Batch";
//             return;
//         }

//         const apiUrl = isEditMode 
//             ? `http://127.0.0.1:5000/owner/academics/batch/update/${editBatchId}` 
//             : `http://127.0.0.1:5000/owner/academics/batch/add/${selectedCourseId}`;
        
//         const apiMethod = isEditMode ? "PATCH" : "POST";

//         try {
//             const response = await fetch(apiUrl, {
//                 method: apiMethod,
//                 headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
//                 body: JSON.stringify(payload)
//             });

//             const data = await response.json();
//             msgEl.style.display = "block";

//             if (response.ok || data.success) {
//                 msgEl.style.color = "#4ade80";
//                 msgEl.textContent = isEditMode ? "Batch Updated Successfully!" : "Batch Created Successfully!";
                
//                 batchForm.reset();
//                 cancelEdit();
//                 fetchBatches(); 

//                 setTimeout(() => { msgEl.style.display = "none"; }, 3000);
//             } else {
//                 msgEl.style.color = "#ef4444";
//                 msgEl.textContent = data.message || "Failed to save batch.";
//             }
//         } catch (error) {
//             msgEl.style.color = "#ef4444";
//             msgEl.textContent = "Server error!";
//         } finally {
//             submitBtn.disabled = false;
//             submitBtn.textContent = isEditMode ? "Update Batch" : "Create Batch";
//         }
//     });

//     // --- 4. FILL EDIT FORM ---
//     window.fillEditForm = function(batch) {
//         isEditMode = true;
//         editBatchId = batch.id;

//         document.querySelector(".form-card h3").textContent = "Update Batch";
//         document.querySelector(".form-card .subtitle").textContent = "Modify details for " + batch.batch_name;
        
//         document.getElementById("batchName").value = batch.batch_name;
//         document.getElementById("courseSelect").value = batch.course_id;
//         document.getElementById("teacherSelect").value = batch.teacher_id;
//         document.getElementById("startTime").value = batch.start_time || "";
//         document.getElementById("endTime").value = batch.end_time || "";

//         submitBtn.textContent = "Update Batch";
//         submitBtn.style.background = "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)";
//         cancelEditBtn.style.display = "inline-block";
//         window.scrollTo(0, 0);
//     };

//     // --- 5. CANCEL EDIT MODE ---
//     window.cancelEdit = function() {
//         isEditMode = false;
//         editBatchId = null;
//         batchForm.reset();
        
//         document.querySelector(".form-card h3").textContent = "Step 4: Create Batches";
//         document.querySelector(".form-card .subtitle").textContent = "Assign a Teacher and a Course to create a new Batch.";
        
//         submitBtn.textContent = "Create Batch";
//         submitBtn.style.background = "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)";
//         cancelEditBtn.style.display = "none";
//     };

//     // --- 6. DELETE BATCH ---
//     window.deleteBatch = async function(id) {
//         if (!confirm("Are you sure you want to delete this batch?")) return;
        
//         try {
//             const response = await fetch(`http://127.0.0.1:5000/owner/academics/batch/delete/${id}`, {
//                 method: "DELETE",
//                 headers: { "Authorization": `Bearer ${token}` }
//             });
//             if (response.ok) {
//                 fetchBatches();
//             } else {
//                 alert("Failed to delete batch.");
//             }
//         } catch (error) {
//             alert("Error deleting batch.");
//         }
//     };
// });



document.addEventListener("DOMContentLoaded", function () {
    const token = localStorage.getItem("access_token");
    if (!token || token === "null") {
        alert("Please login first!");
        window.location.href = "login.html";
        return;
    }

    // 🔥 1. Safe tarike se ID nikalein (chahe inst_id ho ya institution_id)
    const urlParams = new URLSearchParams(window.location.search);
    let instituteId = urlParams.get("inst_id") || urlParams.get("institution_id") || localStorage.getItem("institution_id") || localStorage.getItem("coaching_id") || 1;

    // Isko localStorage mein save bhi kar lo taaki aage problem na aaye
    localStorage.setItem("institution_id", instituteId);

    let isEditMode = false;
    let editBatchId = null;

    const batchForm = document.getElementById("batchForm");
    const msgEl = document.getElementById("formMessage");
    const submitBtn = document.getElementById("saveBatchBtn");
    const cancelEditBtn = document.getElementById("cancelEditBtn");
    const batchesList = document.getElementById("batchesList");
    const courseSelect = document.getElementById("courseSelect");
    const teacherSelect = document.getElementById("teacherSelect");

    // --- 1. LOAD COURSES & TEACHERS FOR DROPDOWN ---
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

    // --- 2. FETCH & DISPLAY BATCHES ---
    async function fetchBatches() {
        try {
            const response = await fetch(`http://127.0.0.1:5000/owner/academics/batch/get/${instituteId}`, {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });
            const data = await response.json();

            if (batchesList) {
                if (response.ok && data.batches) {
                    batchesList.innerHTML = "";
                    if (data.batches.length === 0) {
                        batchesList.innerHTML = `<p style="text-align: center; color: #6b7280;">No batches created yet.</p>`;
                        return;
                    }
                    
                    data.batches.forEach(batch => {
                        const div = document.createElement("div");
                        div.className = "course-item"; 
                        
                        div.innerHTML = `
                            <div class="course-info">
                                <h4>${batch.batch_name} <span class="badge">🕒 ${batch.start_time || 'N/A'} - ${batch.end_time || 'N/A'}</span></h4>
                                <p>Course ID: ${batch.course_id} | Teacher ID: ${batch.teacher_id}</p>
                            </div>
                            <div class="action-buttons">
                                <button style="background: #10b981; color: white; padding: 6px 12px; border: none; border-radius: 6px; cursor: pointer; font-weight: 500;" 
                                        onclick="window.location.href='add_student.html?batch_id=${batch.id}'">
                                    👨‍🎓 Add/View Students
                                </button>
                                
                                <button class="edit-btn" onclick='fillEditForm(${JSON.stringify(batch).replace(/'/g, "&#39;")})'>✏️ Edit</button>
                                <button class="del-btn" onclick="deleteBatch(${batch.id})">🗑️ Delete</button>
                            </div>
                        `;
                        batchesList.appendChild(div);
                    });
                }
            }
        } catch (error) {
            if (batchesList) {
                batchesList.innerHTML = `<p style="color:red; text-align:center;">Failed to load batches.</p>`;
            }
        }
    }

    // Load initial data
    loadDropdowns();
    fetchBatches();

    // --- 3. CREATE OR UPDATE BATCH ---
    if (batchForm) {
        batchForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = isEditMode ? "Updating Batch..." : "Creating Batch...";
            }

            const payload = {
                batch_name: document.getElementById("batchName").value.trim(),
                teacher_id: document.getElementById("teacherSelect").value,
                start_time: document.getElementById("startTime").value,
                end_time: document.getElementById("endTime").value,
                mode: "Offline" 
            };

            const selectedCourseId = document.getElementById("courseSelect").value;
            if (!selectedCourseId) {
                alert("Please select a course!");
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = "Create Batch";
                }
                return;
            }

            const apiUrl = isEditMode 
                ? `http://127.0.0.1:5000/owner/academics/batch/update/${editBatchId}` 
                : `http://127.0.0.1:5000/owner/academics/batch/add/${selectedCourseId}`;
            
            const apiMethod = isEditMode ? "PATCH" : "POST";

            try {
                const response = await fetch(apiUrl, {
                    method: apiMethod,
                    headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();
                if (msgEl) msgEl.style.display = "block";

                if (response.ok || data.success) {
                    if (msgEl) {
                        msgEl.style.color = "#4ade80";
                        msgEl.textContent = isEditMode ? "Batch Updated Successfully!" : "Batch Created Successfully!";
                    }
                    
                    batchForm.reset();
                    cancelEdit();
                    fetchBatches(); 

                    if (msgEl) setTimeout(() => { msgEl.style.display = "none"; }, 3000);
                } else {
                    if (msgEl) {
                        msgEl.style.color = "#ef4444";
                        msgEl.textContent = data.message || "Failed to save batch.";
                    }
                }
            } catch (error) {
                if (msgEl) {
                    msgEl.style.color = "#ef4444";
                    msgEl.textContent = "Server error!";
                }
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = isEditMode ? "Update Batch" : "Create Batch";
                }
            }
        });
    }

    // --- 4. FILL EDIT FORM ---
    window.fillEditForm = function(batch) {
        isEditMode = true;
        editBatchId = batch.id;

        const formTitle = document.querySelector(".form-card h3");
        const formSub = document.querySelector(".form-card .subtitle");
        if (formTitle) formTitle.textContent = "Update Batch";
        if (formSub) formSub.textContent = "Modify details for " + batch.batch_name;
        
        document.getElementById("batchName").value = batch.batch_name;
        document.getElementById("courseSelect").value = batch.course_id;
        document.getElementById("teacherSelect").value = batch.teacher_id;
        document.getElementById("startTime").value = batch.start_time || "";
        document.getElementById("endTime").value = batch.end_time || "";

        if (submitBtn) {
            submitBtn.textContent = "Update Batch";
            submitBtn.style.background = "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)";
        }
        if (cancelEditBtn) cancelEditBtn.style.display = "inline-block";
        window.scrollTo(0, 0);
    };

    // --- 5. CANCEL EDIT MODE ---
    window.cancelEdit = function() {
        isEditMode = false;
        editBatchId = null;
        if (batchForm) batchForm.reset();
        
        const formTitle = document.querySelector(".form-card h3");
        const formSub = document.querySelector(".form-card .subtitle");
        if (formTitle) formTitle.textContent = "Step 4: Create Batches";
        if (formSub) formSub.textContent = "Assign a Teacher and a Course to create a new Batch.";
        
        if (submitBtn) {
            submitBtn.textContent = "Create Batch";
            submitBtn.style.background = "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)";
        }
        if (cancelEditBtn) cancelEditBtn.style.display = "none";
    };

    // --- 6. DELETE BATCH ---
    window.deleteBatch = async function(id) {
        if (!confirm("Are you sure you want to delete this batch?")) return;
        
        try {
            const response = await fetch(`http://127.0.0.1:5000/owner/academics/batch/delete/${id}`, {
                method: "DELETE",
                headers: { "Authorization": `Bearer ${token}` }
            });
            if (response.ok) {
                fetchBatches();
            } else {
                alert("Failed to delete batch.");
            }
        } catch (error) {
            alert("Error deleting batch.");
        }
    };
});