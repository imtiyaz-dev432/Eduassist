document.addEventListener("DOMContentLoaded", function () {
    const token = localStorage.getItem("access_token");
    const role = localStorage.getItem("role");
    const institutionId = localStorage.getItem("institution_id");

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
    const API_BASE = "http://127.0.0.1:5000/owner/faq";

    // Helper: Show Alert
    function showAlert(message, isSuccess) {
        msgBox.style.display = "block";
        msgBox.className = isSuccess ? "alert-box alert-success" : "alert-box alert-error";
        msgBox.textContent = message;
        setTimeout(() => msgBox.style.display = "none", 5000); // Hide after 5 seconds
    }

    // ==========================================
    // 1. ADD NEW FAQ
    // ==========================================
    document.getElementById("faqForm").addEventListener("submit", async function (e) {
        e.preventDefault();
        const submitBtn = document.getElementById("submitBtn");
        submitBtn.disabled = true;
        submitBtn.textContent = "Saving...";

        const payload = {
            category: document.getElementById("faqCategory").value,
            question: document.getElementById("faqQuestion").value,
            answer: document.getElementById("faqAnswer").value
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
                showAlert("✅ " + data.message, true);
                document.getElementById("faqForm").reset();
                fetchFAQs(); // Naya data aane par table update karo
            } else {
                showAlert("❌ " + data.message, false);
            }
        } catch (error) {
            showAlert("❌ Network Error! Cannot connect to server.", false);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = "➕ Save FAQ to AI";
        }
    });

    // ==========================================
    // 2. FETCH EXISTING FAQS
    // ==========================================
    window.fetchFAQs = async function() {
        const listBody = document.getElementById("faqListBody");
        try {
            const response = await fetch(`${API_BASE}/view/${institutionId}`, {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });
            
            const data = await response.json();

            if (response.ok && data.success) {
                if (!data.faqs || data.faqs.length === 0) {
                    listBody.innerHTML = `<tr><td colspan="4" style="text-align:center; color:#6b7280;">No FAQs added yet. AI is currently empty.</td></tr>`;
                    return;
                }
                
                listBody.innerHTML = "";
                data.faqs.forEach(faq => {
                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td><span style="background: #e0f2fe; color: #0284c7; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">${faq.category || 'General'}</span></td>
                        <td><b>${faq.question}</b></td>
                        <td>${faq.answer}</td>
                        <td>
                            <button class="delete-btn" onclick="deleteFaq(${faq.id})">🗑️ Delete</button>
                        </td>
                    `;
                    listBody.appendChild(tr);
                });
            }
        } catch (error) {
            listBody.innerHTML = `<tr><td colspan="4" style="color:red; text-align:center;">Failed to load FAQs.</td></tr>`;
        }
    }

    // ==========================================
    // 3. DELETE FAQ
    // ==========================================
    window.deleteFaq = async function(faqId) {
        if (!confirm("Are you sure? This will remove the answer from AI's brain.")) {
            return;
        }

        try {
            const response = await fetch(`${API_BASE}/delete/${faqId}`, {
                method: "DELETE",
                headers: { "Authorization": `Bearer ${token}` }
            });
            const data = await response.json();

            if (response.ok && data.success) {
                showAlert("✅ FAQ Deleted Successfully!", true);
                fetchFAQs(); // Refresh Table
            } else {
                showAlert("❌ Error: " + data.message, false);
            }
        } catch (error) {
            showAlert("❌ Network Error!", false);
        }
    };

    // Logout Logic
    document.getElementById("globalLogoutBtn").addEventListener("click", function() {
        if (confirm("Are you sure you want to log out?")) {
            localStorage.clear(); 
            window.location.href = "login.html";
        }
    });

    // Page Load hote hi data fetch karo
    fetchFAQs();
});