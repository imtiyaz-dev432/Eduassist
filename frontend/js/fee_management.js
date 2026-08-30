document.addEventListener("DOMContentLoaded", function () {
    const token = localStorage.getItem("access_token");
    const role = localStorage.getItem("user_role");

    // Security Check
    if (!token || role !== "owner") {
        alert("Owner access only!");
        window.location.href = "login.html";
        return;
    }

    const searchBtn = document.getElementById("searchBtn");
    const searchStudentIdInput = document.getElementById("searchStudentId");
    const feeSection = document.getElementById("feeSection");
    const displayStudentId = document.getElementById("displayStudentId");
    const feeTableBody = document.getElementById("feeTableBody");
    const globalMessage = document.getElementById("globalMessage");

    // Modal Elements
    const feeModal = document.getElementById("feeModal");
    const closeBtn = document.querySelector(".close-btn");
    const addFeeBtn = document.getElementById("addFeeBtn");
    const feeForm = document.getElementById("feeForm");
    const modalTitle = document.getElementById("modalTitle");
    const modalMessage = document.getElementById("modalMessage");

    let currentStudentId = null;
    let isEditMode = false;
    let editFeeId = null;

    // --- 1. LOAD FEES (GET) ---
    searchBtn.addEventListener("click", async () => {
        const studentId = searchStudentIdInput.value.trim();
        if (!studentId) {
            showMsg("Please enter a Student ID", "error", globalMessage);
            return;
        }

        searchBtn.textContent = "Loading...";
        try {
            const response = await fetch(`http://127.0.0.1:5000/owner/fees/find/${studentId}`, {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });
            const data = await response.json();

            if (response.ok && data.success) {
                currentStudentId = studentId;
                displayStudentId.textContent = studentId;
                feeSection.style.display = "block";
                globalMessage.style.display = "none";
                renderFeeTable(data.fees);
            } else {
                feeSection.style.display = "none";
                showMsg(data.message || "Student not found.", "error", globalMessage);
            }
        } catch (error) {
            showMsg("Server error! Could not load fees.", "error", globalMessage);
        } finally {
            searchBtn.textContent = "🔍 Load Fees";
        }
    });

    // Render Table Helper
    function renderFeeTable(fees) {
        feeTableBody.innerHTML = "";
        if (fees.length === 0) {
            feeTableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:#6b7280;">No fee records found for this student.</td></tr>`;
            return;
        }

        fees.forEach(fee => {
            // Determine Badge Color
            let badgeClass = "badge-red";
            if (fee.status === "Paid") badgeClass = "badge-green";
            if (fee.status === "Partially Paid") badgeClass = "badge-yellow";

            // Format Date safely
            let formattedDate = fee.due_date ? new Date(fee.due_date).toLocaleDateString() : "N/A";

            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><b>₹${fee.total_fee}</b></td>
                <td>₹${fee.paid_amount}</td>
                <td style="color: #ef4444; font-weight: 600;">₹${fee.due_amount}</td>
                <td>${formattedDate}</td>
                <td><span class="status-badge ${badgeClass}">${fee.status}</span></td>
                <td>
                    <button class="action-btn edit-btn" onclick='openEditModal(${JSON.stringify(fee)})'>✏️ Edit</button>
                    <button class="action-btn delete-btn" onclick="deleteFee(${fee.id})">🗑️ Delete</button>
                </td>
            `;
            feeTableBody.appendChild(tr);
        });
    }

    // --- MODAL CONTROLS ---
    addFeeBtn.addEventListener("click", () => {
        isEditMode = false;
        editFeeId = null;
        modalTitle.textContent = "Add New Fee Record";
        feeForm.reset();
        modalMessage.style.display = "none";
        feeModal.style.display = "flex";
    });

    closeBtn.addEventListener("click", () => feeModal.style.display = "none");
    window.addEventListener("click", (e) => { if (e.target === feeModal) feeModal.style.display = "none"; });

    // Open Edit Modal Helper
    window.openEditModal = function(fee) {
        isEditMode = true;
        editFeeId = fee.id;
        modalTitle.textContent = "Edit Fee Record";
        modalMessage.style.display = "none";

        document.getElementById("totalFee").value = fee.total_fee;
        document.getElementById("paidAmount").value = fee.paid_amount;
        
        // Format Date for HTML Input
        if (fee.due_date) {
            const d = new Date(fee.due_date);
            document.getElementById("dueDate").value = d.toISOString().split('T')[0];
        } else {
            document.getElementById("dueDate").value = "";
        }

        feeModal.style.display = "flex";
    };

    // --- 2. CREATE & UPDATE FEE (POST / PATCH) ---
    feeForm.addEventListener("submit", async function(e) {
        e.preventDefault();
        const submitBtn = document.getElementById("saveFeeBtn");
        submitBtn.disabled = true;
        submitBtn.textContent = "Saving...";

        const payload = {
            total_fee: document.getElementById("totalFee").value,
            paid_amount: document.getElementById("paidAmount").value,
            due_date: document.getElementById("dueDate").value || null
        };

        const url = isEditMode 
            ? `http://127.0.0.1:5000/owner/fees/update/${editFeeId}` 
            : `http://127.0.0.1:5000/owner/fees/create/${currentStudentId}`;
        
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
            const data = await response.json();

            if (response.ok && data.success !== false) { // Backend returns 201/200
                feeModal.style.display = "none";
                searchBtn.click(); // Reload the table automatically
                alert("✅ " + (data.message || "Saved successfully!"));
            } else {
                showMsg(data.message || "Failed to save fee.", "error", modalMessage);
            }
        } catch (error) {
            showMsg("Server Error!", "error", modalMessage);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = "Save Fee Record";
        }
    });

    // --- 3. DELETE FEE (DELETE) ---
    window.deleteFee = async function(feeId) {
        if (!confirm("Are you sure you want to delete this fee record? This cannot be undone.")) return;

        try {
            const response = await fetch(`http://127.0.0.1:5000/owner/fees/delete/${feeId}`, {
                method: "DELETE",
                headers: { "Authorization": `Bearer ${token}` }
            });
            const data = await response.json();

            if (response.ok && data.success !== false) {
                searchBtn.click(); // Reload table
            } else {
                alert("❌ " + (data.message || "Failed to delete fee."));
            }
        } catch (error) {
            alert("❌ Server Error!");
        }
    };

    // --- UI Helper Function ---
    function showMsg(text, type, element) {
        element.style.display = "block";
        element.textContent = text;
        if (type === "error") {
            element.style.color = "#ef4444";
            element.style.backgroundColor = "#fee2e2";
        } else {
            element.style.color = "#10b981";
            element.style.backgroundColor = "#d1fae5";
        }
    }
});