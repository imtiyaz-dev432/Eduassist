document.addEventListener("DOMContentLoaded", function() {
    // Check agar user directly is page par aa gaya bina email daale
    const identifier = sessionStorage.getItem("reset_id");
    if (!identifier) {
        alert("Please enter your email/mobile first.");
        window.location.href = "forgot-password.html";
    }
});

document.getElementById("resetForm").addEventListener("submit", async function(event) {
    event.preventDefault(); // Page reload hone se roko

    const otpInput = document.getElementById("otp").value.trim();
    const newPasswordInput = document.getElementById("newPassword").value;
    const messageEl = document.getElementById("message");
    const resetBtn = document.getElementById("resetBtn");
    
    // Purane page se save kiya hua email/mobile nikaalo
    const identifier = sessionStorage.getItem("reset_id");

    // UI Updates
    messageEl.textContent = "Resetting password...";
    messageEl.style.color = "#6b7280"; // Gray color
    resetBtn.disabled = true;

    // Body set karo (Python backend jaisa expect kar raha hai)
    let requestBody = {
        otp: otpInput,
        new_password: newPasswordInput
    };
    
    if (identifier.includes("@")) {
        requestBody.email = identifier;
    } else {
        requestBody.mobile_no = identifier;
    }

    try {
        // Apne Python backend endpoint par request bhejein
        const response = await fetch("http://localhost:5000/auth/reset-password", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(requestBody)
        });

        const data = await response.json();

        if (response.ok) {
            // 200 OK - Password successfully reset
            messageEl.style.color = "#4ade80"; // Green
            messageEl.textContent = data.message || "Password reset successfully!";

            // Security ke liye sessionStorage se email hata do
            sessionStorage.removeItem("reset_id");

            // 2 second baad wapas login page par bhej do
            setTimeout(() => {
                window.location.href = "login.html";
            }, 2000);

        } else {
            // 400/401 - Galat OTP ya koi aur error
            messageEl.style.color = "#f87171"; // Red
            messageEl.textContent = data.message || "Failed to reset password.";
        }

    } catch (error) {
        console.error("Backend connection error:", error);
        messageEl.style.color = "#f87171";
        messageEl.textContent = "Unable to connect to the Python server.";
    } finally {
        // Button wapas chalu karo
        resetBtn.disabled = false;
    }
});