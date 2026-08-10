document.getElementById("forgotForm").addEventListener("submit", async function(event) {
    event.preventDefault(); // Prevents page reload

    const identifierInput = document.getElementById("identifier").value.trim();
    const messageEl = document.getElementById("message");
    const forgotBtn = document.getElementById("forgotBtn");

    // UI Updates during loading
    messageEl.textContent = "Sending OTP...";
    messageEl.style.color = "#6b7280"; // Gray color
    forgotBtn.disabled = true;

    // Logic to determine if user typed an email or a mobile number
    let requestBody = {};
    if (identifierInput.includes("@")) {
        requestBody.email = identifierInput;
    } else {
        requestBody.mobile_no = identifierInput;
    }

    try {
        // Send request to your Python backend
        const response = await fetch("http://localhost:5000/auth/forgot-password", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(requestBody)
        });

        const data = await response.json();

        if (response.ok) {
            // 200 OK - OTP sent successfully
            messageEl.style.color = "#4ade80"; // Green color
            messageEl.textContent = data.message;

            // Save identifier in sessionStorage so the next page knows which user to verify
            sessionStorage.setItem("reset_id", identifierInput);

            // Redirect to OTP verification/Password Reset page after 2 seconds
            setTimeout(() => {
                window.location.href = "reset-password.html"; // Change to your actual reset page name
            }, 2000);

        } else {
            // 400 Bad Request / Invalid Email/Mobile
            messageEl.style.color = "#f87171"; // Red color
            messageEl.textContent = data.message || "Failed to send OTP.";
        }

    } catch (error) {
        console.error("Backend connection error:", error);
        messageEl.style.color = "#f87171";
        messageEl.textContent = "Unable to connect to the Python server.";
    } finally {
        // Re-enable button
        forgotBtn.disabled = false;
    }
});