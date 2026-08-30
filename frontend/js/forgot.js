document.addEventListener("DOMContentLoaded", function () {
    const forgotForm = document.getElementById("forgotForm");
    const messageEl = document.getElementById("messageBox");
    
    forgotForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        const emailInput = document.getElementById("forgotEmail").value.trim();
        const sendOtpBtn = document.getElementById("sendOtpBtn");

        showMessage("Sending OTP...", "#6b7280");
        sendOtpBtn.disabled = true;

        try {
            const response = await fetch("http://127.0.0.1:5000/auth/forgot-password", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: emailInput })
            });

            const data = await response.json();

            if (response.ok) {
                // ⚠️ SABSE ZAROORI STEP: Naye page ke liye email save karo
                sessionStorage.setItem("reset_email", emailInput);
                
                showMessage("OTP Sent! Redirecting...", "#4ade80");
                
                // Naye page (reset-password.html) par bhej do!
                setTimeout(() => {
                    window.location.href = "reset-password.html";
                }, 1000);
            } else {
                showMessage(data.message || "Failed to send OTP.", "#f87171");
                sendOtpBtn.disabled = false;
            }
        } catch (error) {
            showMessage("Server error. Please try again.", "#f87171");
            sendOtpBtn.disabled = false;
        }
    });

    function showMessage(text, color) {
        messageEl.style.display = "block";
        messageEl.textContent = text;
        messageEl.style.color = color;
    }
});