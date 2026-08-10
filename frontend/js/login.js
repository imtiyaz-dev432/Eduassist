document.getElementById("loginForm").addEventListener("submit", async function(event) {
    event.preventDefault(); // Prevents the page from reloading

    const identifierInput = document.getElementById("identifier").value.trim();
    const passwordInput = document.getElementById("password").value;
    const messageEl = document.getElementById("message");
    const loginBtn = document.getElementById("loginBtn");

    // Clear previous messages
    messageEl.textContent = "Logging in...";
    messageEl.style.color = "#6b7280"; // Gray color
    loginBtn.disabled = true;

    // Logic to determine if user typed an email or a mobile number
    let requestBody = { password: passwordInput };
    
    if (identifierInput.includes("@")) {
        // It's an email
        requestBody.email = identifierInput;
    } else {
        // It's a mobile number
        requestBody.mobile_no = identifierInput;
    }

    try {
        // Sending data to your PYTHON backend
        const response = await fetch("http://localhost:5000/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(requestBody)
        });

        const data = await response.json();

        if (response.ok) {
            // 200 OK - Login successful
            messageEl.style.color = "#4ade80"; // Green
            messageEl.textContent = data.message;

            // Save the JWT access token and user info to LocalStorage
            localStorage.setItem("access_token", data.access_token);
            localStorage.setItem("user_id", data.user.id);
            localStorage.setItem("user_role", "owner");

            // Redirect to dashboard (change this to your actual dashboard page)
            setTimeout(() => {
                window.location.href = "dashboard.html"; 
            }, 1000);

        } else {
            // Handle specific backend errors (400, 401, 403)
            messageEl.style.color = "#f87171"; // Red
            messageEl.textContent = data.message;

            // If OTP is required (Status 403 from your Python code)
            if (response.status === 403) {
                // Save the identifier so the verify page knows who to verify
                sessionStorage.setItem("verify_id", identifierInput); 
                setTimeout(() => {
                    window.location.href = "verify-otp.html";
                }, 1500);
            }
        }

    } catch (error) {
        console.error("Backend connection error:", error);
        messageEl.style.color = "#f87171";
        messageEl.textContent = "Unable to connect to the Python server.";
    } finally {
        // Re-enable the button
        loginBtn.disabled = false;
    }
});