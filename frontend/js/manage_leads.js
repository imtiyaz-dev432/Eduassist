document.addEventListener("DOMContentLoaded", function () {
    const token = localStorage.getItem("access_token");
    const role = localStorage.getItem("role");
    
    // Smart ID Finder
    const institutionId = localStorage.getItem("institution_id") || new URLSearchParams(window.location.search).get("institution_id");

    if (!token || role !== "owner") {
        alert("Access Denied! Owner login required.");
        window.location.href = "login.html";
        return;
    }

    if (!institutionId) {
        alert("Institute ID missing. Please go to Dashboard first.");
        window.location.href = "owner_dashboard.html";
        return;
    }

    const msgBox = document.getElementById("msgBox");
    const API_BASE = "http://127.0.0.1:5000/owner/leads";

    function showAlert(message, isSuccess) {
        msgBox.style.display = "block";
        msgBox.style.background = isSuccess ? "#dcfce7" : "#fee2e2";
        msgBox.style.color = isSuccess ? "#16a34a" : "#dc2626";
        msgBox.textContent = message;
        setTimeout(() => msgBox.style.display = "none", 4000);
    }

    // ==========================================
    // 1. FETCH & DISPLAY LEADS
    // ==========================================
    window.fetchLeads = async function() {
        const tableBody = document.getElementById("leadsTableBody");
        try {
            const response = await fetch(`${API_BASE}/view/${institutionId}`, {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });
            const data = await response.json();

            if (response.ok && data.success) {
                if (!data.leads || data.leads.length === 0) {
                    tableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:#6b7280;">No leads found yet.</td></tr>`;
                    return;
                }
                
                tableBody.innerHTML = "";
                data.leads.forEach(lead => {
                    // Badge Color Logic
                    let badgeClass = `status-${lead.status}`; // Matches CSS class status-New, status-Contacted etc.

                    // Source styling (Highlight AI Bot vs Manual)
                    let sourceStyle = lead.source === "AI Bot" || lead.source === "AI Chatbot" 
                                      ? "background:#e0e7ff; color:#4f46e5; font-weight:bold;" 
                                      : "background:#f1f5f9; color:#475569;";

                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td><strong>${lead.name}</strong></td>
                        <td>📞 ${lead.phone}<br>✉️ ${lead.email || '-'}</td>
                        <td>${lead.course_interest || '-'}</td>
                        <td><span style="font-size:11px; padding:4px 8px; border-radius:12px; ${sourceStyle}">${lead.source}</span></td>
                        <td><span class="status-badge ${badgeClass}">${lead.status}</span></td>
                        <td>
                            <button class="btn-edit" onclick="openEditModal(${lead.id}, '${lead.name}', '${lead.status}')">✏️ Status</button>
                            <button class="btn-delete" onclick="deleteLead(${lead.id})">🗑️</button>
                        </td>
                    `;
                    tableBody.appendChild(tr);
                });
            }
        } catch (error) {
            tableBody.innerHTML = `<tr><td colspan="6" style="color:red; text-align:center;">Failed to load leads.</td></tr>`;
        }
    }

    // ==========================================
    // 2. ADD MANUAL LEAD LOGIC
    // ==========================================
    window.openAddModal = () => document.getElementById("addModal").style.display = "flex";
    window.closeAddModal = () => document.getElementById("addModal").style.display = "none";

    document.getElementById("addLeadForm").addEventListener("submit", async function(e) {
        e.preventDefault();
        
        const payload = {
            name: document.getElementById("addName").value,
            phone: document.getElementById("addPhone").value,
            email: document.getElementById("addEmail").value,
            course_interest: document.getElementById("addCourse").value,
            message: document.getElementById("addMessage").value,
            source: "Manual Entry" // Yeh highlight karega ki yeh manual hai
        };

        try {
            const response = await fetch(`${API_BASE}/add/${institutionId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });
            const data = await response.json();

            if (response.ok && data.success) {
                showAlert("✅ Lead Added Successfully", true);
                closeAddModal();
                document.getElementById("addLeadForm").reset();
                fetchLeads(); // Refresh Table
            } else {
                showAlert("❌ Error: " + data.message, false);
            }
        } catch (error) {
            showAlert("❌ Network Error!", false);
        }
    });

    // ==========================================
    // 3. EDIT LEAD STATUS LOGIC
    // ==========================================
    window.openEditModal = function(id, name, status) {
        document.getElementById("editLeadId").value = id;
        document.getElementById("editLeadName").textContent = "Student: " + name;
        document.getElementById("editStatus").value = status;
        document.getElementById("editModal").style.display = "flex";
    };
    
    window.closeEditModal = () => document.getElementById("editModal").style.display = "none";

    document.getElementById("editLeadForm").addEventListener("submit", async function(e) {
        e.preventDefault();
        
        const leadId = document.getElementById("editLeadId").value;
        const payload = { status: document.getElementById("editStatus").value };

        try {
            const response = await fetch(`${API_BASE}/update/${leadId}`, {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });
            const data = await response.json();

            if (response.ok && data.success) {
                showAlert("✅ Status Updated Successfully", true);
                closeEditModal();
                fetchLeads(); // Refresh Table
            } else {
                showAlert("❌ Error: " + data.message, false);
            }
        } catch (error) {
            showAlert("❌ Network Error!", false);
        }
    });

    // ==========================================
    // 4. DELETE LEAD
    // ==========================================
    window.deleteLead = async function(leadId) {
        if (!confirm("Are you sure you want to delete this lead permanently?")) return;

        try {
            const response = await fetch(`${API_BASE}/delete/${leadId}`, {
                method: "DELETE",
                headers: { "Authorization": `Bearer ${token}` }
            });
            const data = await response.json();

            if (response.ok && data.success) {
                showAlert("✅ Lead Deleted Successfully", true);
                fetchLeads(); 
            } else {
                showAlert("❌ Error: " + data.message, false);
            }
        } catch (error) {
            showAlert("❌ Network Error!", false);
        }
    };

    // Logout
    document.getElementById("globalLogoutBtn").addEventListener("click", function() {
        if (confirm("Are you sure you want to log out?")) {
            localStorage.clear(); 
            window.location.href = "login.html";
        }
    });

    // Page load hote hi data fetch karo
    fetchLeads();
});