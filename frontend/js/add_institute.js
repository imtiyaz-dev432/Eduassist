document.addEventListener("DOMContentLoaded", function () {
    // 1. Security Check: Token hai ya nahi?
    const token = localStorage.getItem("access_token");
    if (!token) {
        alert("Please login first!");
        window.location.href = "login.html";
        return;
    }

    const form = document.getElementById("instituteForm");
    const msgEl = document.getElementById("formMessage");
    const listContainer = document.getElementById("institutesList");
    const logoutBtn = document.getElementById("logoutBtn");

    const BASE_URL = "http://127.0.0.1:5000/teacher/institution";

    // --- PAGE LOAD HOTE HI INSTITUTES LEKAR AAYO ---
    fetchInstitutes();

    // --- FORM SUBMIT (ADD INSTITUTE) ---
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        // Data ikkatha karo
        const payload = {
            institution_name: document.getElementById("instName").value.trim(),
            institution_type: document.getElementById("instType").value,
            city: document.getElementById("instCity").value.trim(),
            state: document.getElementById("instState").value.trim(),
            country: document.getElementById("instCountry").value.trim(),
            phone: document.getElementById("instPhone").value.trim(),
            address: document.getElementById("instAddress").value.trim()
        };

        msgEl.style.display = "block";
        msgEl.style.color = "#6b7280";
        msgEl.textContent = "Saving institute...";

        try {
            const response = await fetch(`${BASE_URL}/register`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}` // JWT token yahan jata hai
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (response.ok) {
                msgEl.style.color = "#4ade80";
                msgEl.textContent = "Institute Added Successfully!";
                form.reset(); // Form khali karo
                fetchInstitutes(); // List ko refresh karo
            } else {
                msgEl.style.color = "#ef4444";
                msgEl.textContent = data.message || "Failed to add institute.";
            }
        } catch (error) {
            msgEl.style.color = "#ef4444";
            msgEl.textContent = "Server error!";
        }
    });

    // --- GET ALL INSTITUTES ---
    async function fetchInstitutes() {
        try {
            const response = await fetch(`${BASE_URL}/get`, {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}` // Backend ko dikhao ki hum owner hain
                }
            });
            const data = await response.json();

            if (response.ok && data.institutions) {
                listContainer.innerHTML = ""; // Purana data hatao
                
                if(data.institutions.length === 0){
                    listContainer.innerHTML = "<p>No coachings added yet.</p>";
                    return;
                }

                // Har ek institute ke liye HTML element banao
                data.institutions.forEach(inst => {
                    const div = document.createElement("div");
                    div.className = "inst-item";
                    
                    // 🔥 YAHAN NAYA BUTTON ADD KIYA HAI 🔥
                    div.innerHTML = `
                        <h4>${inst.institute_name}</h4>
                        <p><strong>Type:</strong> ${inst.institute_type}</p>
                        <p><strong>Location:</strong> ${inst.city}, ${inst.state}</p>
                        
                        <div class="action-buttons">
                            <button class="add-btn" onclick="window.location.href='add_teacher.html?inst_id=${inst.id}'">
                                + Add Teacher
                            </button>
                            <button class="del-btn" onclick="deleteInstitute(${inst.id})">
                                Delete
                            </button>
                        </div>
                    `;
                    listContainer.appendChild(div);
                });
            }
        } catch (error) {
            listContainer.innerHTML = "<p style='color:red;'>Failed to load data.</p>";
        }
    }

    // --- LOGOUT BUTTON ---
    // --- LOGOUT BUTTON (Safe Code) ---
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            localStorage.removeItem("access_token");
            window.location.href = "login.html";
        });
    }
});

// --- DELETE INSTITUTE ---
// Ise global rakhna padega kyunki HTML mein onclick lagaya hai
async function deleteInstitute(id) {
    if (!confirm("Are you sure you want to delete this coaching?")) return;

    const token = localStorage.getItem("access_token");
    try {
        const response = await fetch(`http://127.0.0.1:5000/teacher/institution/delete/${id}`, {
            method: "DELETE",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (response.ok) {
            alert("Deleted successfully!");
            location.reload(); // Page reload to refresh list
        } else {
            alert("Failed to delete.");
        }
    } catch (error) {
        alert("Server error.");
    }
}