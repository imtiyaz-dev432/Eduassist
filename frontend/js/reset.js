document.addEventListener("DOMContentLoaded", function () {
    const resetForm = document.getElementById("resetForm");
    const messageEl = document.getElementById("messageBox");
    const emailDisplay = document.getElementById("userEmailDisplay");

    // 1. Check karo ki pichle page se konsa email aaya hai
    const savedEmail = sessionStorage.getItem("reset_email");

    // Agar koi direct is page par aa gaya bina OTP bheje, wapas bhej do
    if (!savedEmail) {
        alert("Session expired. Please request OTP again.");
        window.location.href = "forgot-password.html";
        return;
    }

    // UI mein email dikhao
    emailDisplay.textContent = `Enter the OTP sent to ${savedEmail}`;

    // 2. Submit form to Backend
    resetForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        const otpInput = document.getElementById("resetOtp").value.trim();
        const passwordInput = document.getElementById("newPassword").value;
        const resetBtn = document.getElementById("resetBtn");

        showMessage("Updating password...", "#6b7280");
        resetBtn.disabled = true;

        try {
            const response = await fetch("http://127.0.0.1:5000/auth/reset-password", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    email: savedEmail,      // Pichle page se liya hua email
                    otp: otpInput,
                    new_password: passwordInput
                })
            });

            const data = await response.json();

            if (response.ok) {
                showMessage("Password updated successfully! Redirecting to login...", "#4ade80");
                
                // Kaam hone ke baad email ko memory se delete kardo
                sessionStorage.removeItem("reset_email");

                // Login page par bhej do
                setTimeout(() => {
                    window.location.href = "login.html";
                }, 2000);
            } else {
                showMessage(data.message || "Invalid OTP or Password.", "#f87171");
                resetBtn.disabled = false;
            }
        } catch (error) {
            showMessage("Server error. Please try again.", "#f87171");
            resetBtn.disabled = false;
        }
    });

    function showMessage(text, color) {
        messageEl.style.display = "block";
        messageEl.textContent = text;
        messageEl.style.color = color;
    }
});