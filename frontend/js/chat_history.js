document.addEventListener("DOMContentLoaded", function () {
    const token = localStorage.getItem("access_token");
    const role = localStorage.getItem("role");
    
    // Get Institution ID
    const institutionId = localStorage.getItem("institution_id") || new URLSearchParams(window.location.search).get("institution_id");

    // Security Check
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
    const API_BASE = "http://127.0.0.1:5000/owner/chat_history";

    function showAlert(message, isSuccess) {
        msgBox.style.display = "block";
        msgBox.style.background = isSuccess ? "#dcfce7" : "#fee2e2";
        msgBox.style.color = isSuccess ? "#16a34a" : "#dc2626";
        msgBox.textContent = message;
        setTimeout(() => msgBox.style.display = "none", 4000);
    }

    // ==========================================
    // FETCH CHAT HISTORY
    // ==========================================
    async function fetchChatHistory() {
        const tableBody = document.getElementById("chatTableBody");
        try {
            const response = await fetch(`${API_BASE}/get/${institutionId}`, {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });
            const data = await response.json();

            if (response.ok && data.success) {
                if (!data.chats || data.chats.length === 0) {
                    tableBody.innerHTML = `<tr><td colspan="4" style="text-align:center; color:#6b7280; padding: 20px;">No chat history found yet.</td></tr>`;
                    return;
                }
                
                tableBody.innerHTML = "";
                data.chats.forEach(chat => {
                    
                    // 🔥 TIMEZONE FIX (GMT TO IST) 🔥
                    let rawDate = chat.created_at;
                    // Agar date ke end mein 'Z' nahi hai, toh 'Z' lagao jisse browser ko pata chale ye UTC hai
                    if (rawDate && !rawDate.endsWith("Z")) {
                        rawDate = rawDate.replace(" ", "T") + "Z";
                    }
                    
                    const dateObj = new Date(rawDate || new Date());
                    
                    // Date Formatting (Make it look nice: DD/MM/YYYY, HH:MM AM/PM)
                    const formattedDate = dateObj.toLocaleDateString('en-IN', { 
                        day: '2-digit', month: 'short', year: 'numeric' 
                    });
                    const formattedTime = dateObj.toLocaleTimeString('en-IN', { 
                        hour: '2-digit', minute: '2-digit'
                    });

                    // Lead Status Badge
                    // Agar chat mein lead_id save hui hai, matlab student ne proper details di thin.
                    const isLead = chat.lead_id ? true : false;
                    const badgeClass = isLead ? "badge-lead" : "badge-anon";
                    const badgeText = isLead ? "👤 Lead Saved" : "👻 Anonymous";

                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td>
                            <div class="date-text">${formattedDate}</div>
                            <div class="date-text" style="color: #0ea5e9; font-weight: bold;">${formattedTime}</div>
                        </td>
                        <td>
                            <span class="badge ${badgeClass}">${badgeText}</span>
                        </td>
                        <td>
                            <div class="visitor-msg">${chat.message || '-'}</div>
                        </td>
                        <td>
                            <div class="ai-msg">${chat.response || '-'}</div>
                        </td>
                    `;
                    tableBody.appendChild(tr);
                });
            } else {
                tableBody.innerHTML = `<tr><td colspan="4" style="color:red; text-align:center;">Failed to load data: ${data.message}</td></tr>`;
            }
        } catch (error) {
            tableBody.innerHTML = `<tr><td colspan="4" style="color:red; text-align:center;">Network error while fetching chats!</td></tr>`;
        }
    }

    // Logout Functionality
    document.getElementById("globalLogoutBtn").addEventListener("click", function() {
        if (confirm("Are you sure you want to log out?")) {
            localStorage.clear(); 
            window.location.href = "login.html";
        }
    });

    // Load Data on Page Load
    fetchChatHistory();
});