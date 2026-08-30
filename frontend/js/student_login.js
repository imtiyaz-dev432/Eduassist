document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("studentLoginForm");
    const loginBtn = document.getElementById("loginBtn");
    const msgEl = document.getElementById("loginMessage");

    if (loginForm) {
        loginForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            
            loginBtn.disabled = true;
            loginBtn.textContent = "Verifying...";

            const loginId = document.getElementById("loginId").value.trim();
            const password = document.getElementById("password").value;

            // 🔥 SMART LOGIC: Email vs Phone Check
            let payload = {
                password: password
            };

            if (loginId.includes("@")) {
                payload.email = loginId;
            } else {
                // Backend me variable ka naam 'phone' hai
                payload.phone = loginId;
            }

            try {
                // Aapke backend ka exact route: /student_auth/login
                const response = await fetch("http://127.0.0.1:5000/student_auth/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();
                msgEl.style.display = "block";

                if (response.ok && data.success) {
                    msgEl.style.color = "#10b981"; // Green Success
                    msgEl.style.backgroundColor = "#d1fae5";
                    msgEl.textContent = "Login Successful! Redirecting...";

                    // LocalStorage mein save karein
                    localStorage.setItem("access_token", data.access_token);
                    localStorage.setItem("user_role", "student"); 
                    localStorage.setItem("student_data", JSON.stringify(data.student)); 

                    // Student Dashboard par bhej dein
                    setTimeout(() => {
                        window.location.href = "student_dashboard.html";
                    }, 1500);
                } else {
                    msgEl.style.color = "#ef4444"; // Red Error
                    msgEl.style.backgroundColor = "#fee2e2";
                    msgEl.textContent = data.message || "Login failed. Please check your details.";
                }
            } catch (error) {
                console.error("Login Error:", error);
                msgEl.style.color = "#ef4444";
                msgEl.style.backgroundColor = "#fee2e2";
                msgEl.textContent = "Server error! Cannot connect to backend.";
            } finally {
                loginBtn.disabled = false;
                loginBtn.textContent = "Login as Student";
            }
        });
    }
});