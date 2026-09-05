document.addEventListener("DOMContentLoaded", function () {
    const token = localStorage.getItem("access_token");
    const role = localStorage.getItem("role");

    // 1. Security Check
    if (!token || token === "null" || role !== "owner") {
        alert("Access Denied! Owner login required.");
        window.location.href = "login.html";
        return;
    }

    // 2. Get Institution ID (from URL query parameter or localStorage)
    const urlParams = new URLSearchParams(window.location.search);
    let institutionId = urlParams.get("institution_id") || localStorage.getItem("institution_id") || localStorage.getItem("coaching_id");

    if (!institutionId) {
        alert("Institution ID is missing! Please select or create a coaching first.");
        window.location.href = "add_institute.html"; 
        return;
    }

    // Save it back to localStorage for consistency
    localStorage.setItem("institution_id", institutionId);

    // ==========================================
    // Navbar Logic & Link Fixing
    // ==========================================
    const courseLink = document.getElementById("navCourseLink");
    const batchLink = document.getElementById("navBatchLink");
    
    if (courseLink) courseLink.href = `add_course.html?institution_id=${institutionId}`;
    if (batchLink) batchLink.href = `add_batch.html?institution_id=${institutionId}`;
    
    // Global Logout Action
    const logoutBtn = document.getElementById("globalLogoutBtn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            if (confirm("Are you sure you want to log out?")) {
                localStorage.clear();
                window.location.href = "login.html";
            }
        });
    }

    // ==========================================
    // Course Logic
    // ==========================================
    const courseForm = document.getElementById("courseForm");
    const coursesList = document.getElementById("coursesList");
    const formMessage = document.getElementById("formMessage");
    const formTitle = document.getElementById("formTitle");
    const saveCourseBtn = document.getElementById("saveCourseBtn");
    const cancelEditBtn = document.getElementById("cancelEditBtn");

    let isEditMode = false;
    let editCourseId = null;

    // 3. Fetch & Render Courses (GET API)
    async function fetchCourses() {
        try {
            const response = await fetch(`http://127.0.0.1:5000/owner/academics/courses/get/${institutionId}`, {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });
            const data = await response.json();

            if (response.ok && data.success !== false) {
                renderCourses(data.courses);
            } else {
                coursesList.innerHTML = `<p style="text-align:center; color:#ef4444;">${data.message || "Failed to load courses."}</p>`;
            }
        } catch (error) {
            console.error("Fetch error:", error);
            coursesList.innerHTML = `<p style="text-align:center; color:#ef4444;">Server error while loading courses.</p>`;
        }
    }

    function renderCourses(courses) {
        coursesList.innerHTML = "";
        if (!courses || courses.length === 0) {
            coursesList.innerHTML = `<p style="text-align: center; color: #6b7280;">No courses added yet. Use the form above to add one!</p>`;
            return;
        }

        courses.forEach(c => {
            const card = document.createElement("div");
            card.className = "course-item-card"; 
            card.style.cssText = "background: #f9fafb; border: 1px solid #e5e7eb; padding: 15px; border-radius: 8px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;";
            
            card.innerHTML = `
                <div>
                    <h4 style="color: #1f2937; font-size: 16px; margin-bottom: 4px;">${c.course_name} <span style="font-size:12px; background:#e0f2fe; color:#0284c7; padding:2px 8px; border-radius:10px;">${c.mode || 'N/A'}</span></h4>
                    <p style="font-size: 13px; color: #6b7280;">Category: ${c.category || 'General'} | Fee: ₹${c.course_fee} | Duration: ${c.duration || 'N/A'}</p>
                </div>
                <div style="display: flex; gap: 8px;">
                    <button onclick='setupEdit(${JSON.stringify(c)})' style="background: #e0f2fe; color: #0284c7; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-weight: bold;">Edit</button>
                    <button onclick="deleteCourse(${c.id})" style="background: #fee2e2; color: #ef4444; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-weight: bold;">Delete</button>
                </div>
            `;
            coursesList.appendChild(card);
        });
    }

    // 4. Handle Add & Update (POST / PATCH API)
    courseForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        saveCourseBtn.disabled = true;
        saveCourseBtn.textContent = "Saving...";

        const payload = {
            course_name: document.getElementById("courseName").value,
            category: document.getElementById("courseCategory").value,
            course_fee: document.getElementById("courseFee").value,
            duration: document.getElementById("courseDuration").value,
            mode: document.getElementById("courseMode").value,
            level: document.getElementById("courseLevel").value,
            eligibility: document.getElementById("courseEligibility").value,
            description: document.getElementById("courseDescription").value,
            syllabus: document.getElementById("courseSyllabus").value,
            certificate_available: document.getElementById("certAvailable").checked,
            placement_support: document.getElementById("placementSupport").checked
        };

        const url = isEditMode
            ? `http://127.0.0.1:5000/owner/academics/courses/update/${editCourseId}`
            : `http://127.0.0.1:5000/owner/academics/courses/add/${institutionId}`;
        
        const method = isEditMode ? "PATCH" : "POST";

        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });
            const result = await response.json();

            if (response.ok && result.success !== false) {
                showMsg(result.message || "Saved successfully!", "success");
                courseForm.reset();
                resetEditMode();
                fetchCourses(); // Reload list
            } else {
                showMsg(result.message || "Failed to save course.", "error");
            }
        } catch (error) {
            showMsg("Server connection error!", "error");
        } finally {
            saveCourseBtn.disabled = false;
            saveCourseBtn.textContent = "Save Course";
        }
    });

    // 5. Setup Edit Mode
    window.setupEdit = function (c) {
        isEditMode = true;
        editCourseId = c.id;
        
        formTitle.textContent = "Edit Course / Program";
        saveCourseBtn.textContent = "Update Course";
        cancelEditBtn.style.display = "inline-block";

        document.getElementById("courseName").value = c.course_name || "";
        document.getElementById("courseCategory").value = c.category || "";
        document.getElementById("courseFee").value = c.course_fee || "";
        document.getElementById("courseDuration").value = c.duration || "";
        document.getElementById("courseMode").value = c.mode || "Offline";
        document.getElementById("courseLevel").value = c.level || "Beginner";
        document.getElementById("courseEligibility").value = c.eligibility || "";
        document.getElementById("courseDescription").value = c.description || "";
        document.getElementById("courseSyllabus").value = c.syllabus || "";
        document.getElementById("certAvailable").checked = c.certificate_available || false;
        document.getElementById("placementSupport").checked = c.placement_support || false;

        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    // 6. Cancel Edit
    window.cancelEdit = function () {
        resetEditMode();
        courseForm.reset();
    };

    function resetEditMode() {
        isEditMode = false;
        editCourseId = null;
        formTitle.textContent = "Add New Course / Program";
        saveCourseBtn.textContent = "Save Course";
        cancelEditBtn.style.display = "none";
    }

    // 7. Delete Course (DELETE API)
    window.deleteCourse = async function (courseId) {
        if (!confirm("Are you sure you want to delete this course?")) return;

        try {
            const response = await fetch(`http://127.0.0.1:5000/owner/academics/courses/delete/${courseId}`, {
                method: "DELETE",
                headers: { "Authorization": `Bearer ${token}` }
            });

            if (response.ok) {
                fetchCourses(); // Reload table
            } else {
                const data = await response.json();
                alert("❌ " + (data.message || "Failed to delete course"));
            }
        } catch (error) {
            alert("❌ Server error while deleting.");
        }
    };

    // 8. Navigation to Batches
    window.goToBatches = function () {
        window.location.href = `add_batch.html?institution_id=${institutionId}`;
    };

    function showMsg(text, type) {
        formMessage.style.display = "block";
        formMessage.textContent = text;
        formMessage.style.color = type === "error" ? "#ef4444" : "#10b981";
        formMessage.style.backgroundColor = type === "error" ? "#fee2e2" : "#d1fae5";
        formMessage.style.padding = "10px";
        formMessage.style.borderRadius = "6px";
        formMessage.style.textAlign = "center";
        formMessage.style.marginBottom = "15px";

        setTimeout(() => {
            formMessage.style.display = "none";
        }, 4000);
    }

    // Initial load
    fetchCourses();
});