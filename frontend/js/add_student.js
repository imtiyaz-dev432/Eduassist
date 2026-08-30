document.addEventListener("DOMContentLoaded", function () {
    const token = localStorage.getItem("access_token");
    if (!token) {
        alert("Please login first!");
        window.location.href = "login.html";
        return;
    }

    // URL se Batch ID nikalna zaroori hai
    const urlParams = new URLSearchParams(window.location.search);
    const batchId = urlParams.get("batch_id");

    if (!batchId) {
        alert("Batch ID missing! Please select a batch first.");
        window.history.back();
        return;
    }

    let isEditMode = false;
    let editStudentId = null;

    const studentForm = document.getElementById("studentForm");
    const msgEl = document.getElementById("formMessage");
    const submitBtn = document.getElementById("saveStudentBtn");
    const cancelEditBtn = document.getElementById("cancelEditBtn");
    const studentsList = document.getElementById("studentsList");

    // --- 1. FETCH & DISPLAY STUDENTS ---
    async function fetchStudents() {
        try {
            const response = await fetch(`http://127.0.0.1:5000/owner/teacher/academics/student/get/${batchId}`, {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });
            const data = await response.json();

            if (response.ok && data.students) {
                studentsList.innerHTML = "";
                if (data.students.length === 0) {
                    studentsList.innerHTML = `<p style="text-align: center; color: #6b7280;">No students enrolled in this batch yet.</p>`;
                    return;
                }
                
                data.students.forEach(student => {
                    const statusColor = student.status === 'Active' ? '#10b981' : (student.status === 'Dropped' ? '#ef4444' : '#f59e0b');
                    
                    const div = document.createElement("div");
                    div.className = "student-item"; 
                    div.innerHTML = `
                        <div class="student-info">
                            <h4>${student.student_name} <span class="badge" style="background-color: ${statusColor}20; color: ${statusColor};">${student.status}</span></h4>
                            <p>📞 ${student.phone} ${student.email ? '| ✉️ ' + student.email : ''}</p>
                            <p style="font-size: 0.85rem; color: #6b7280;">Joined: ${student.admission_date || 'N/A'}</p>
                        </div>
                        <div class="action-buttons">
                            <button class="lock-btn" onclick="enableLogin(${student.id})">🔑 Enable Login</button>
                            <button class="edit-btn" onclick='fillEditForm(${JSON.stringify(student).replace(/'/g, "&#39;")})'>✏️ Edit</button>
                            <button class="del-btn" onclick="deleteStudent(${student.id})">🗑️ Delete</button>
                        </div>
                    `;
                    studentsList.appendChild(div);
                });
            }
        } catch (error) {
            studentsList.innerHTML = `<p style="color:red; text-align:center;">Failed to load students.</p>`;
        }
    }

    fetchStudents(); // Page load hote hi data fetch karo

    // --- 2. ADD OR UPDATE STUDENT ---
    studentForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        submitBtn.disabled = true;
        submitBtn.textContent = isEditMode ? "Updating..." : "Enrolling...";

        const payload = {
            student_name: document.getElementById("studentName").value.trim(),
            email: document.getElementById("studentEmail").value.trim() || null,
            phone: document.getElementById("studentPhone").value.trim(),
            parent_phone: document.getElementById("parentPhone").value.trim() || null,
            admission_date: document.getElementById("admissionDate").value || null,
            status: document.getElementById("studentStatus").value,
            address: document.getElementById("studentAddress").value.trim() || null
        };

        const apiUrl = isEditMode 
            ? `http://127.0.0.1:5000/owner/teacher/academics/student/update/${editStudentId}`
            : `http://127.0.0.1:5000/owner/teacher/academics/student/add/${batchId}`;
        
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
                msgEl.style.color = "#10b981"; // Success Green
                msgEl.textContent = isEditMode ? "Student Updated Successfully!" : "Student Enrolled Successfully!";
                
                studentForm.reset();
                cancelEdit();
                fetchStudents(); 

                setTimeout(() => { msgEl.style.display = "none"; }, 3000);
            } else {
                msgEl.style.color = "#ef4444"; // Error Red
                msgEl.textContent = data.message || "Failed to save student.";
            }
        } catch (error) {
            msgEl.style.color = "#ef4444";
            msgEl.textContent = "Server error!";
        } finally {
            submitBtn.disabled = false;
        }
    });

    // --- 3. FILL EDIT FORM ---
    window.fillEditForm = function(student) {
        isEditMode = true;
        editStudentId = student.id;

        document.getElementById("formTitle").textContent = "Update Student Details";
        document.getElementById("formSubtitle").textContent = "Modifying details for " + student.student_name;
        
        document.getElementById("studentName").value = student.student_name || "";
        document.getElementById("studentEmail").value = student.email || "";
        document.getElementById("studentPhone").value = student.phone || "";
        document.getElementById("parentPhone").value = student.parent_phone || "";
        // date format backend se "YYYY-MM-DD" aana chahiye <input type="date"> ke liye
        document.getElementById("admissionDate").value = student.admission_date || ""; 
        document.getElementById("studentStatus").value = student.status || "Active";
        document.getElementById("studentAddress").value = student.address || "";

        submitBtn.textContent = "Update Student";
        submitBtn.style.background = "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)";
        cancelEditBtn.style.display = "inline-block";
        window.scrollTo(0, 0);
    };

    // --- 4. CANCEL EDIT MODE ---
    window.cancelEdit = function() {
        isEditMode = false;
        editStudentId = null;
        studentForm.reset();
        
        document.getElementById("formTitle").textContent = "Enroll New Student";
        document.getElementById("formSubtitle").textContent = "Fill in the details to add a student to this batch.";
        
        submitBtn.textContent = "Enroll Student";
        submitBtn.style.background = "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)";
        cancelEditBtn.style.display = "none";
    };

    // --- 5. ENABLE LOGIN (PATCH) ---
    window.enableLogin = async function(id) {
        const password = prompt("Enter a strong password for this student (Min 8 chars, 1 special char):");
        if (!password) return; // User pressed cancel or empty

        try {
            const response = await fetch(`http://127.0.0.1:5000/owner/teacher/academics/student/enable-login/${id}`, {
                method: "PATCH",
                headers: { 
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}` 
                },
                body: JSON.stringify({ password: password })
            });
            const data = await response.json();
            
            if (response.ok || data.success) {
                alert(" " + (data.message || "Login enabled successfully!"));
            } else {
                alert("❌ " + (data.message || "Failed to enable login. Check password requirements."));
            }
        } catch (error) {
            alert("❌ Error communicating with the server.");
        }
    };

    // --- 6. DELETE STUDENT ---
    window.deleteStudent = async function(id) {
        if (!confirm("Are you sure you want to completely remove this student?")) return;
        
        try {
            const response = await fetch(`http://127.0.0.1:5000/owner/teacher/academics/student/delete/${id}`, {
                method: "DELETE",
                headers: { "Authorization": `Bearer ${token}` }
            });
            
            if (response.ok) {
                fetchStudents();
            } else {
                const data = await response.json();
                alert("❌ " + (data.message || "Failed to delete student."));
            }
        } catch (error) {
            alert("❌ Error deleting student.");
        }
    };
});