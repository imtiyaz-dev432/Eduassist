document.addEventListener("DOMContentLoaded", function () {
    const token = localStorage.getItem("access_token");
    if (!token) {
        alert("Please login first!");
        window.location.href = "login.html";
        return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    const instituteId = urlParams.get("inst_id");

    if (!instituteId) {
        alert("Coaching ID missing!");
        window.location.href = "add_institute.html";
        return;
    }

    // 🔥 EDIT MODE VARIABLES 🔥
    let isEditMode = false;
    let editTeacherId = null;
    let allTeachers = []; // Safe storage for teacher data

    const teacherForm = document.getElementById("teacherForm");
    const msgEl = document.getElementById("formMessage");
    const submitBtn = document.getElementById("saveTeacherBtn");
    const teachersList = document.getElementById("teachersList");
    const cancelEditBtn = document.getElementById("cancelEditBtn");

    // --- 1. FETCH & DISPLAY TEACHERS ---
    async function fetchTeachers() {
        try {
            const response = await fetch(`http://127.0.0.1:5000/teacher/get/${instituteId}`, {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });
            
            if (!response.ok) throw new Error("Failed to fetch");

            const data = await response.json();

            if (data.teacher_list) {
                allTeachers = data.teacher_list; // Save to array
                teachersList.innerHTML = "";
                
                if (allTeachers.length === 0) {
                    teachersList.innerHTML = `<p style="text-align: center; color: #6b7280;">No teachers added yet.</p>`;
                    return;
                }
                
                allTeachers.forEach(t => {
                    const div = document.createElement("div");
                    div.className = "student-item";
                    
                    // Optional: Hide button if login is already enabled based on backend data
                    const showEnableBtn = t.login_enabled ? 
                        `<button class="lock-btn" style="background: #ecfdf5; color: #16a34a; padding: 6px 12px; border: none; border-radius: 6px; cursor: default;" disabled>✅ Login Active</button>` :
                        `<button class="lock-btn" style="background: #f3e8ff; color: #7e22ce; padding: 6px 12px; border: none; border-radius: 6px; cursor: pointer; font-weight: 500;" onclick="enableTeacherLogin(${t.id})">🔑 Enable Login</button>`;

                    div.innerHTML = `
                        <div class="student-info">
                            <h4>👨‍🏫 ${t.name}</h4>
                            <p>📞 ${t.mobile_no || t.phone || 'N/A'} | ✉️ ${t.email || 'N/A'}</p>
                        </div>
                        <div class="action-buttons">
                            ${showEnableBtn}
                            
                            <button class="edit-btn" style="background: #e0f2fe; color: #0284c7; padding: 6px 12px; border: none; border-radius: 6px; cursor: pointer;" 
                                    onclick="fillEditForm(${t.id})">✏️ Edit</button>
                        
                            <button class="del-btn" style="background: #fee2e2; color: #b91c1c; padding: 6px 12px; border: none; border-radius: 6px; cursor: pointer;" 
                                    onclick="deleteTeacher(${t.id})">🗑️ Delete</button>
                        </div>
                    `;
                    teachersList.appendChild(div);
                });
            }
        } catch (error) {
            console.error(error);
            teachersList.innerHTML = `<p style="color:red; text-align:center;">Failed to load teachers.</p>`;
        }
    }

    fetchTeachers(); 

    // --- 2. ADD OR UPDATE TEACHER FORM SUBMIT ---
    if (teacherForm) {
        teacherForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            submitBtn.disabled = true;
            submitBtn.textContent = isEditMode ? "Updating Teacher..." : "Saving Teacher...";

            const payload = {
                name: document.getElementById("teacherName").value.trim(),
                mobile_no: document.getElementById("teacherPhone").value.trim(),
                email: document.getElementById("teacherEmail").value.trim(),
              
            };

            const apiUrl = isEditMode 
                ? `http://127.0.0.1:5000/teacher/update/${editTeacherId}`
                : `http://127.0.0.1:5000/teacher/add/${instituteId}`;
            
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
                msgEl.style.display = "block";

                if (response.ok || data.success) {
                    msgEl.style.color = "#10b981";
                    msgEl.textContent = isEditMode ? "Teacher Updated Successfully!" : "Teacher Added Successfully!";
                    teacherForm.reset();
                    if (isEditMode) cancelEdit(); 
                    fetchTeachers(); 
                    setTimeout(() => { msgEl.style.display = "none"; }, 3000);
                } else {
                    msgEl.style.color = "#ef4444";
                    msgEl.textContent = data.message || "Failed to save teacher.";
                }
            } catch (error) {
                msgEl.style.color = "#ef4444";
                msgEl.textContent = "Server error!";
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = isEditMode ? "Update Teacher" : "💾 Save Teacher";
            }
        });
    }

    // --- 3. FILL FORM FOR EDITING 🔥 ---
    window.fillEditForm = function(id) {
        const teacher = allTeachers.find(t => t.id === id);
        if (!teacher) return alert("Teacher data not found!");

        isEditMode = true;
        editTeacherId = teacher.id;

        document.getElementById("teacherName").value = teacher.name || "";
        document.getElementById("teacherPhone").value = teacher.mobile_no || teacher.phone || "";
        document.getElementById("teacherEmail").value = teacher.email || "";

        submitBtn.textContent = "Update Teacher";
        submitBtn.style.background = "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)";
        
        if (cancelEditBtn) cancelEditBtn.style.display = "inline-block";
        window.scrollTo({ top: 0, behavior: 'smooth' }); 
    };

    // --- 4. CANCEL EDIT MODE 🔥 ---
    window.cancelEdit = function() {
        isEditMode = false;
        editTeacherId = null;
        teacherForm.reset();
        
        submitBtn.textContent = "💾 Save Teacher";
        submitBtn.style.background = "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)";
        if (cancelEditBtn) cancelEditBtn.style.display = "none";
    };

    // --- 5. ENABLE TEACHER LOGIN (PATCH) ---
    window.enableTeacherLogin = async function(teacher_id) {
        const password = prompt("Enter a strong password for this Teacher:\n(Min 8 chars, 1 special char, 1 letter, 1 digit)");
        if (!password) return; 

        try {
            // 🔥 FIXED URL: Added "-teacher" to match your backend exactly
            const response = await fetch(`http://127.0.0.1:5000/teacher/enable-teacher-login/${teacher_id}`, {
                method: "PATCH",
                headers: { 
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}` 
                },
                body: JSON.stringify({ password: password })
            });
            
            // Your backend always returns JSON, so this is safe
            const data = await response.json();
            
            if (data.success) {
                alert("✅ " + data.message);
                fetchTeachers(); // Refresh list to change button to "Login Active"
            } else {
                // This will catch your 400, 403, 404, and 500 backend errors perfectly
                alert("❌ " + (data.message || "Failed to enable login."));
            }
            
        } catch (error) {
            console.error("Network Error:", error);
            alert("❌ Error communicating with the server.");
        }
    };

    // --- 6. DELETE TEACHER ---
    window.deleteTeacher = async function(teacher_id) {
        if (!confirm("Are you sure you want to remove this teacher?")) return;
        try {
            const response = await fetch(`http://127.0.0.1:5000/teacher/delete/${teacher_id}`, {
                method: "DELETE",
                headers: { "Authorization": `Bearer ${token}` }
            });
            if (response.ok) fetchTeachers();
            else alert("Failed to delete.");
        } catch (error) {
            console.error("Error:", error);
            alert("Error deleting teacher.");
        }
    };

    // --- 7. GO TO NEXT STEP ---
    window.goToCourse = function() {
        window.location.href = `add_course.html?inst_id=${instituteId}`;
    };
});