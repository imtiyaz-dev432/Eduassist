document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("loginForm");
    const loginBtn = document.getElementById("loginBtn");
    
    // Message dikhane ke liye (Iska HTML mein hona zaroori hai)
    const messageEl = document.getElementById("messageBox"); 

    if (loginForm) {
        loginForm.addEventListener("submit", async function (e) {
            e.preventDefault(); // Page reload hone se roko

            // Button ko disable karo aur text change karo
            loginBtn.disabled = true;
            loginBtn.textContent = "Logging in...";
            showMessage("Checking credentials...", "#6b7280");

            // Form se value nikalna (Aapke HTML mein inputs ki ID yahi honi chahiye)
            // Note: HTML mein email input ki id="identifier" aur password ki id="password" honi chahiye
            const identifierVal = document.getElementById("identifier").value.trim();
            const passwordVal = document.getElementById("password").value.trim();

            if (!identifierVal || !passwordVal) {
                showMessage("Please enter both email/phone and password.", "#ef4444");
                resetButton();
                return;
            }

            // SMART PAYLOAD: Decide karo ki email hai ya mobile number
            const isEmail = identifierVal.includes("@");
            const payload = { password: passwordVal };

            if (isEmail) {
                payload.email = identifierVal;
            } else {
                payload.mobile_no = identifierVal;
            }

            try {
                // Backend API call
                const response = await fetch("http://127.0.0.1:5000/auth/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();

                if (response.ok || data.success) {
                    // 🎉 BINGO! JWT Token Browser mein save karein
                    if (data.access_token) {
                        localStorage.setItem("access_token", data.access_token);
                        localStorage.setItem("role", "owner"); 
                    }
                    
                    showMessage("Login successful! Redirecting...", "#4ade80");
                    
                    // 1.5 seconds ke baad add_institute page par jump karein
                    setTimeout(() => {
                        window.location.href = "add_institute.html";
                    }, 1500);

                } else {
                    // Agar password galat hua ya verify nahi hua
                    showMessage(data.message || "Invalid credentials.", "#ef4444");
                    resetButton();
                }

            } catch (error) {
                console.error("Login Error:", error);
                showMessage("Server error. Please check your backend.", "#ef4444");
                resetButton();
            }
        });
    }

    // Helper Functions
    function showMessage(text, color) {
        if (messageEl) {
            messageEl.style.display = "block";
            messageEl.textContent = text;
            messageEl.style.color = color;
        }
    }

    function resetButton() {
        if (loginBtn) {
            loginBtn.disabled = false;
            loginBtn.textContent = "Login";
        }
    }
});