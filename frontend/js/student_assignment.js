// document.addEventListener("DOMContentLoaded", function () {
//     const token = localStorage.getItem("access_token");
//     const role = localStorage.getItem("user_role") || localStorage.getItem("role");

//     // Security check: Only students allowed
//     if (!token || role !== "student") {
//         alert("Access Denied! Student login required.");
//         window.location.href = "login.html";
//         return;
//     }

//     const msgBox = document.getElementById("msgBox");
//     const grid = document.getElementById("assignmentsGrid");
    
//     // Backend Base URLs
//     const API_BASE = "http://127.0.0.1:5000/student/assessments/assignment"; 
//     const SUBMIT_API_BASE = "http://127.0.0.1:5000/student/assessments/assignment_submission"; 

//     function showAlert(message, isSuccess) {
//         msgBox.style.display = "block";
//         msgBox.style.background = isSuccess ? "#dcfce7" : "#fee2e2";
//         msgBox.style.color = isSuccess ? "#16a34a" : "#dc2626";
//         msgBox.textContent = message;
//         setTimeout(() => msgBox.style.display = "none", 4000);
//     }

//     // ==========================================
//     // 1. FETCH ALL ASSIGNMENTS FOR STUDENT
//     // ==========================================
//     async function loadAssignments() {
//         try {
//             const response = await fetch(`${API_BASE}/my`, {
//                 method: "GET",
//                 headers: { "Authorization": `Bearer ${token}` }
//             });
//             const data = await response.json();

//             if (response.ok && data.success) {
//                 if (!data.assignments || data.assignments.length === 0) {
//                     grid.innerHTML = `<p class="loading-text">No active assignments from your teachers right now! 🎉</p>`;
//                     return;
//                 }

//                 grid.innerHTML = ""; // Clear the loading text

//                 data.assignments.forEach(assign => {
//                     // Fix timezone for Indian Standard Time (IST)
//                     let formattedDate = "No Deadline";
//                     if (assign.due_date) {
//                         let rawDate = assign.due_date;
//                         if (!rawDate.endsWith("Z")) rawDate = rawDate.replace(" ", "T") + "Z";
//                         const dateObj = new Date(rawDate);
//                         formattedDate = dateObj.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
//                     }

//                     // Check if student has already submitted
//                     let badgeClass = assign.is_submitted ? "badge-submitted" : "badge-pending";
//                     let badgeText = assign.is_submitted ? "✅ Submitted" : "⏳ Pending";

//                     // ==============================================
//                     // 🔥 NEW: Action Buttons with 'View Result' Logic 🔥
//                     // ==============================================
//                     let actionButtonsHtml = `
//                         <div style="margin-top: 15px; display: flex; flex-direction: column; gap: 10px;">
//                             ${assign.is_submitted 
//                                 ? `
//                                    <!-- Agar submit ho gaya hai, toh View Result ka button dikhao -->
//                                    <div style="display: flex; gap: 10px;">
//                                        <button class="btn-view" onclick="viewAssignmentPDF(${assign.assignment_id})" style="flex: 1; padding: 8px; border-radius: 5px; border: 1px solid #d1d5db; background: white; cursor: pointer; font-weight:bold; color: #374151;">📄 Question</button>
                                       
//                                        <button onclick="window.location.href='student_assignment_result.html?assignment_id=${assign.assignment_id}'" 
//                                             style="flex: 1; background: #10b981; color: white; padding: 8px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 6px rgba(16,185,129,0.2);">
//                                             📊 View Result
//                                        </button>
//                                    </div>
//                                    <div style="text-align: center; margin-top: 5px;">
//                                         <span style="color: #16a34a; font-weight: bold; font-size: 13px;">✅ Answer Successfully Submitted</span>
//                                    </div>
//                                   ` 
//                                 : `
//                                    <!-- Agar submit nahi hua hai, toh Upload ka button dikhao -->
//                                    <div style="display: flex; justify-content: space-between; align-items: center;">
//                                        <button class="btn-view" onclick="viewAssignmentPDF(${assign.assignment_id})" style="padding: 8px 12px; border-radius: 5px; border: 1px solid #d1d5db; background: white; cursor: pointer; font-weight:bold; color: #374151;">📄 View Question</button>
//                                        <button onclick="openSubmitModal(${assign.assignment_id})" style="background: #2563eb; color: white; padding: 8px 12px; border-radius: 5px; border: none; cursor: pointer; font-weight:bold;">📤 Upload Answer</button>
//                                    </div>
//                                   `
//                             }
//                         </div>
//                     `;

//                     // Create Card HTML
//                     const card = document.createElement("div");
//                     card.className = "card";
//                     // Dynamic styling based on submission status
//                     if(assign.is_submitted) {
//                         card.style.borderLeft = "4px solid #10b981"; // Green border for submitted
//                     }

//                     card.innerHTML = `
//                         <h3 class="card-title">${assign.title}</h3>
//                         <span class="badge ${badgeClass}" style="${assign.is_submitted ? 'background:#dcfce7; color:#16a34a;' : 'background:#fef3c7; color:#d97706;'} padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">${badgeText}</span>
//                         <p class="card-desc" style="margin-top: 10px;">${assign.description || "No description provided."}</p>
                        
//                         <div class="meta-info" style="margin-top: 10px;">
//                             <span>Max Marks:</span>
//                             <strong>${assign.max_marks}</strong>
//                         </div>
//                         <div class="meta-info">
//                             <span>Due Date:</span>
//                             <span class="date-text">⏳ ${formattedDate}</span>
//                         </div>

//                         ${actionButtonsHtml}
//                     `;
//                     grid.appendChild(card);
//                 });
//             } else {
//                 grid.innerHTML = `<p style="color:red; text-align:center;">${data.message}</p>`;
//             }
//         } catch (error) {
//             console.error("Fetch error: ", error);
//             grid.innerHTML = `<p style="color:red; text-align:center;">Network error while loading assignments!</p>`;
//         }
//     }

//     // ==========================================
//     // 2. SECURE PDF VIEWER (WITH JWT TOKEN)
//     // ==========================================
//     window.viewAssignmentPDF = async function(assignmentId) {
//         const btn = event.target;
//         const originalText = btn.textContent;
//         btn.textContent = "Loading...";
//         btn.disabled = true;

//         try {
//             const response = await fetch(`${API_BASE}/file/${assignmentId}`, {
//                 method: "GET",
//                 headers: { "Authorization": `Bearer ${token}` }
//             });

//             if (response.ok) {
//                 const blob = await response.blob();
//                 const fileUrl = window.URL.createObjectURL(blob);
//                 window.open(fileUrl, '_blank');
//             } else {
//                 const data = await response.json();
//                 showAlert(data.message || "Failed to open PDF.", false);
//             }
//         } catch (error) {
//             showAlert("Network error while trying to fetch the PDF.", false);
//         } finally {
//             btn.textContent = originalText;
//             btn.disabled = false;
//         }
//     };

//     // ==========================================
//     // 3. SUBMIT ASSIGNMENT (MODAL & UPLOAD LOGIC)
//     // ==========================================
    
//     // Open Modal
//     window.openSubmitModal = function(assignmentId) {
//         document.getElementById("uploadAssignmentId").value = assignmentId;
//         document.getElementById("assignmentPdf").value = ""; 
        
//         let msgDiv = document.getElementById("uploadMessage");
//         msgDiv.classList.add("hidden");
//         msgDiv.innerText = "";
//         msgDiv.className = "upload-msg hidden";

//         document.getElementById("submitModal").classList.remove("hidden");
//     };

//     // Close Modal
//     window.closeSubmitModal = function() {
//         document.getElementById("submitModal").classList.add("hidden");
//     };

//     // Upload API Call
//     window.submitAssignmentFile = async function() {
//         const assignmentId = document.getElementById("uploadAssignmentId").value;
//         const fileInput = document.getElementById("assignmentPdf");
//         const msgDiv = document.getElementById("uploadMessage");
//         const submitBtn = document.getElementById("submitBtn");

//         if (fileInput.files.length === 0) {
//             msgDiv.innerText = "❌ Please select a PDF file first.";
//             msgDiv.className = "upload-msg error block";
//             msgDiv.classList.remove("hidden");
//             msgDiv.style.color = "red";
//             return;
//         }

//         const formData = new FormData();
//         formData.append("file", fileInput.files[0]);

//         try {
//             submitBtn.innerText = "Uploading...";
//             submitBtn.disabled = true;

//             const response = await fetch(`${SUBMIT_API_BASE}/submit/${assignmentId}`, {
//                 method: "POST",
//                 headers: { 
//                     "Authorization": `Bearer ${token}` 
//                     // Content-Type is auto-generated for FormData
//                 },
//                 body: formData
//             });

//             const data = await response.json();

//             if (response.ok) {
//                 msgDiv.innerText = "✅ " + data.message;
//                 msgDiv.className = "upload-msg success block";
//                 msgDiv.style.color = "green";
//                 msgDiv.classList.remove("hidden");
                
//                 // Refresh list automatically after 1.5 seconds
//                 setTimeout(() => {
//                     window.closeSubmitModal();
//                     loadAssignments(); // Recharge grid with updated status
//                 }, 1500);
//             } else {
//                 msgDiv.innerText = "❌ " + data.message;
//                 msgDiv.className = "upload-msg error block";
//                 msgDiv.style.color = "red";
//                 msgDiv.classList.remove("hidden");
//             }
//         } catch (error) {
//             console.error(error);
//             msgDiv.innerText = "❌ Network error connecting to server.";
//             msgDiv.className = "upload-msg error block";
//             msgDiv.style.color = "red";
//             msgDiv.classList.remove("hidden");
//         } finally {
//             submitBtn.innerText = "Submit Answer";
//             submitBtn.disabled = false;
//         }
//     };

//     // Logout Function
//     document.getElementById("logoutBtn").addEventListener("click", function() {
//         if (confirm("Are you sure you want to log out?")) {
//             localStorage.clear(); 
//             window.location.href = "student_login.html";
//         }
//     });

//     // Load data when page opens
//     loadAssignments();
// });


document.addEventListener("DOMContentLoaded", function () {
    const token = localStorage.getItem("access_token");
    const role = localStorage.getItem("user_role") || localStorage.getItem("role");

    // Security check: Only students allowed
    if (!token || role !== "student") {
        alert("Access Denied! Student login required.");
        window.location.href = "login.html";
        return;
    }

    const msgBox = document.getElementById("msgBox");
    const grid = document.getElementById("assignmentsGrid");
    
    // Backend Base URLs
    const API_BASE = "http://127.0.0.1:5000/student/assessments/assignment"; 
    const SUBMIT_API_BASE = "http://127.0.0.1:5000/student/assessments/assignment_submission"; 

    function showAlert(message, isSuccess) {
        if (!msgBox) return;
        msgBox.style.display = "block";
        msgBox.style.background = isSuccess ? "#dcfce7" : "#fee2e2";
        msgBox.style.color = isSuccess ? "#16a34a" : "#dc2626";
        msgBox.textContent = message;
        setTimeout(() => msgBox.style.display = "none", 4000);
    }

    // ==========================================
    // 1. FETCH ALL ASSIGNMENTS FOR STUDENT
    // ==========================================
    async function loadAssignments() {
        try {
            const response = await fetch(`${API_BASE}/my`, {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });
            const data = await response.json();

            if (response.ok && data.success) {
                if (!data.assignments || data.assignments.length === 0) {
                    grid.innerHTML = `<p class="loading-text">No active assignments from your teachers right now! 🎉</p>`;
                    return;
                }

                grid.innerHTML = ""; // Clear the loading text

                data.assignments.forEach(assign => {
                    // Fix timezone for Indian Standard Time (IST)
                    let formattedDate = "No Deadline";
                    if (assign.due_date) {
                        let rawDate = assign.due_date;
                        if (!rawDate.endsWith("Z")) rawDate = rawDate.replace(" ", "T") + "Z";
                        const dateObj = new Date(rawDate);
                        formattedDate = dateObj.toLocaleDateString('en-IN', { 
                            day: '2-digit', 
                            month: 'short', 
                            year: 'numeric', 
                            hour: '2-digit', 
                            minute: '2-digit' 
                        });
                    }

                    // Check if student has already submitted
                    let badgeClass = assign.is_submitted ? "badge-submitted" : "badge-pending";
                    let badgeText = assign.is_submitted ? "✅ Submitted" : "⏳ Pending";

                    let actionButtonsHtml = `
                        <div style="margin-top: 15px; display: flex; flex-direction: column; gap: 10px;">
                            ${assign.is_submitted 
                                ? `
                                   <div style="display: flex; gap: 10px;">
                                       <button class="btn-view" onclick="viewAssignmentPDF(event, ${assign.assignment_id})" style="flex: 1; padding: 8px; border-radius: 5px; border: 1px solid #d1d5db; background: white; cursor: pointer; font-weight:bold; color: #374151;">📄 Question</button>
                                       
                                       <button onclick="window.location.href='student_assignment_result.html?assignment_id=${assign.assignment_id}'" 
                                           style="flex: 1; background: #10b981; color: white; padding: 8px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 6px rgba(16,185,129,0.2);">
                                           📊 View Result
                                       </button>
                                   </div>
                                   <div style="text-align: center; margin-top: 5px;">
                                        <span style="color: #16a34a; font-weight: bold; font-size: 13px;">✅ Answer Successfully Submitted</span>
                                   </div>
                                  ` 
                                : `
                                   <div style="display: flex; justify-content: space-between; align-items: center;">
                                       <button class="btn-view" onclick="viewAssignmentPDF(event, ${assign.assignment_id})" style="padding: 8px 12px; border-radius: 5px; border: 1px solid #d1d5db; background: white; cursor: pointer; font-weight:bold; color: #374151;">📄 View Question</button>
                                       <button onclick="openSubmitModal(${assign.assignment_id})" style="background: #2563eb; color: white; padding: 8px 12px; border-radius: 5px; border: none; cursor: pointer; font-weight:bold;">📤 Upload Answer</button>
                                   </div>
                                  `
                            }
                        </div>
                    `;

                    // Create Card HTML
                    const card = document.createElement("div");
                    card.className = "card";
                    if (assign.is_submitted) {
                        card.style.borderLeft = "4px solid #10b981";
                    }

                    card.innerHTML = `
                        <h3 class="card-title">${assign.title}</h3>
                        <span class="badge ${badgeClass}" style="${assign.is_submitted ? 'background:#dcfce7; color:#16a34a;' : 'background:#fef3c7; color:#d97706;'} padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">${badgeText}</span>
                        <p class="card-desc" style="margin-top: 10px;">${assign.description || "No description provided."}</p>
                        
                        <div class="meta-info" style="margin-top: 10px;">
                            <span>Max Marks:</span>
                            <strong>${assign.max_marks}</strong>
                        </div>
                        <div class="meta-info">
                            <span>Due Date:</span>
                            <span class="date-text">⏳ ${formattedDate}</span>
                        </div>

                        ${actionButtonsHtml}
                    `;
                    grid.appendChild(card);
                });
            } else {
                grid.innerHTML = `<p style="color:red; text-align:center;">${data.message || "Failed to load assignments."}</p>`;
            }
        } catch (error) {
            console.error("Fetch error: ", error);
            grid.innerHTML = `<p style="color:red; text-align:center;">Network error while loading assignments!</p>`;
        }
    }

    // ==========================================
    // 2. SECURE PDF VIEWER (WITH JWT TOKEN)
    // ==========================================
    window.viewAssignmentPDF = async function(e, assignmentId) {
        const btn = e ? e.target : event.target;
        const originalText = btn.textContent;
        btn.textContent = "Loading...";
        btn.disabled = true;

        try {
            const response = await fetch(`${API_BASE}/file/${assignmentId}`, {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });

            if (response.ok) {
                const blob = await response.blob();
                const fileUrl = window.URL.createObjectURL(blob);
                window.open(fileUrl, '_blank');
            } else {
                const data = await response.json();
                showAlert(data.message || "Failed to open PDF.", false);
            }
        } catch (error) {
            showAlert("Network error while trying to fetch the PDF.", false);
        } finally {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    };

    // ==========================================
    // 3. SUBMIT ASSIGNMENT (MODAL & UPLOAD LOGIC)
    // ==========================================
    window.openSubmitModal = function(assignmentId) {
        document.getElementById("uploadAssignmentId").value = assignmentId;
        document.getElementById("assignmentPdf").value = ""; 
        
        let msgDiv = document.getElementById("uploadMessage");
        msgDiv.classList.add("hidden");
        msgDiv.innerText = "";
        msgDiv.className = "upload-msg hidden";

        document.getElementById("submitModal").classList.remove("hidden");
    };

    window.closeSubmitModal = function() {
        document.getElementById("submitModal").classList.add("hidden");
    };

    window.submitAssignmentFile = async function() {
        const assignmentId = document.getElementById("uploadAssignmentId").value;
        const fileInput = document.getElementById("assignmentPdf");
        const msgDiv = document.getElementById("uploadMessage");
        const submitBtn = document.getElementById("submitBtn");

        if (fileInput.files.length === 0) {
            msgDiv.innerText = "❌ Please select a PDF file first.";
            msgDiv.className = "upload-msg error block";
            msgDiv.classList.remove("hidden");
            msgDiv.style.color = "red";
            return;
        }

        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        try {
            submitBtn.innerText = "Uploading...";
            submitBtn.disabled = true;

            const response = await fetch(`${SUBMIT_API_BASE}/submit/${assignmentId}`, {
                method: "POST",
                headers: { 
                    "Authorization": `Bearer ${token}` 
                },
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                msgDiv.innerText = "✅ " + data.message;
                msgDiv.className = "upload-msg success block";
                msgDiv.style.color = "green";
                msgDiv.classList.remove("hidden");
                
                setTimeout(() => {
                    window.closeSubmitModal();
                    loadAssignments();
                }, 1500);
            } else {
                msgDiv.innerText = "❌ " + data.message;
                msgDiv.className = "upload-msg error block";
                msgDiv.style.color = "red";
                msgDiv.classList.remove("hidden");
            }
        } catch (error) {
            console.error(error);
            msgDiv.innerText = "❌ Network error connecting to server.";
            msgDiv.className = "upload-msg error block";
            msgDiv.style.color = "red";
            msgDiv.classList.remove("hidden");
        } finally {
            submitBtn.innerText = "Submit Answer";
            submitBtn.disabled = false;
        }
    };

    // ==========================================
    // 4. LOGOUT LOGIC (GLOBAL & SAFE LISTENER)
    // ==========================================
    window.logoutStudent = function() {
        if (confirm("Are you sure you want to log out?")) {
            localStorage.clear(); 
            window.location.href = "student_login.html";
        }
    };

    // Agar kisi page par id="logoutBtn" wala button ho toh bhi chalega (Optional check)
    const logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", window.logoutStudent);
    }

    // Load data when page opens
    loadAssignments();
});