document.addEventListener("DOMContentLoaded", function () {
    const resendBtn = document.getElementById("resendBtn");
    const resendTimerDisplay = document.getElementById("resendTimer");
    const messageEl = document.getElementById("messageBox");
    
    const verifyForm = document.getElementById("verifyForm");
    const verifyBtn = document.getElementById("verifyBtn");
    
    // Dono Input fields (HTML mein inki ID yahi honi chahiye)
    const identifierInput = document.getElementById("identifierInput");
    const otpInput = document.getElementById("otpInput");

    

    // ==========================================
    // 1. VERIFY OTP LOGIC (Form Submit)
    // ==========================================
    if (verifyForm) {
        verifyForm.addEventListener("submit", async function (e) {
            e.preventDefault(); // Page reload hone se roko

            // Form se user ka input uthao
            const userInput = identifierInput.value.trim();
            const otpCode = otpInput.value.trim();

            if (!userInput) {
                showMessage("Please enter your email or phone.", "#ef4444");
                return;
            }

            if (otpCode.length !== 6) {
                showMessage("Please enter a valid 6-digit OTP.", "#ef4444");
                return;
            }

            // Button disable karo taaki double-click na ho
            verifyBtn.disabled = true;
            verifyBtn.textContent = "Verifying...";
            showMessage("Verifying OTP...", "#6b7280");

            // 🔥 SMART PAYLOAD LOGIC 🔥
            // Backend Verify OTP ke liye ya toh 'email' mangta hai ya 'mobile_no'
            const isEmail = userInput.includes("@");
            const requestData = { otp: otpCode };
            
            if (isEmail) {
                requestData.email = userInput;
            } else {
                requestData.mobile_no = userInput;
            }

            try {
                // Apna Verify OTP ka backend API URL call karo
                const response = await fetch("http://127.0.0.1:5000/otp/verify-otp", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(requestData) 
                });

                let data;
                try {
                    data = await response.json();
                } catch (parseError) {
                    if (response.status === 429) {
                        showMessage("Too many attempts! Please wait 10 minutes.", "#ef4444");
                    } else if (response.status === 500) {
                        showMessage("Backend Error (500). Please check server logs.", "#ef4444");
                    } else {
                        showMessage(`Server Error: ${response.status}`, "#ef4444");
                    }
                    verifyBtn.disabled = false;
                    verifyBtn.textContent = "Verify OTP";
                    return; 
                }

                // Agar Verify Success ho gaya
                if (response.ok || data.success === true) {
                    showMessage("Verified successfully! Redirecting to login...", "#4ade80");
                    sessionStorage.removeItem("verify_id"); // Kaam khatam, memory clear karo
                    
                    // 2 second baad automatically Login page par bhej do
                    setTimeout(() => {
                        window.location.href = "login.html";
                    }, 2000);

                } else {
                    showMessage(data.message || "Invalid OTP or User Details.", "#ef4444");
                    verifyBtn.disabled = false;
                    verifyBtn.textContent = "Verify OTP";
                }
            } catch (error) {
                console.error("Verify Error:", error);
                showMessage("Server connection failed. Please check backend.", "#ef4444");
                verifyBtn.disabled = false;
                verifyBtn.textContent = "Verify OTP";
            }
        });
    }

    // ==========================================
    // 2. RESEND OTP LOGIC
    // ==========================================
    if (resendBtn) {
        resendBtn.addEventListener("click", async function (e) {
            e.preventDefault();

            // Agar user ne bina email/phone dale "Resend" daba diya
            const userInput = identifierInput.value.trim();
            if (!userInput) {
                showMessage("Please enter your email or phone first to resend OTP.", "#ef4444");
                identifierInput.focus();
                return;
            }

            resendBtn.classList.add("disabled-link");
            resendBtn.textContent = "Sending...";
            showMessage("Sending new OTP...", "#6b7280");

            try {
                // Backend Resend OTP ke liye strictly 'identifier' mangta hai
                const response = await fetch("http://127.0.0.1:5000/otp/resend-otp", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ identifier: userInput }) 
                });

                let data;
                try {
                    data = await response.json();
                } catch (err) {
                    showMessage(response.status === 429 ? "Too many attempts!" : "Server Error", "#ef4444");
                    resetResendButton();
                    return;
                }

                if (response.ok || data.success === true) {
                    showMessage("New OTP sent successfully!", "#4ade80");
                    startCooldownTimer(); 
                } else {
                    showMessage(data.message || "Failed to resend OTP.", "#ef4444");
                    resetResendButton();
                }
            } catch (error) {
                console.error("Resend Error:", error);
                showMessage("Server is down. Please try again later.", "#ef4444");
                resetResendButton();
            }
        });
    }

    // --- COOLDOWN TIMER FUNCTION ---
    // Resend dabane ke baad 60 seconds ka timer
    function startCooldownTimer() {
        let timeLeft = 60;
        resendBtn.style.display = "none"; 
        resendTimerDisplay.style.display = "inline"; 
        
        const timerInterval = setInterval(() => {
            resendTimerDisplay.textContent = `(Wait ${timeLeft}s)`;
            timeLeft--;

            if (timeLeft < 0) {
                clearInterval(timerInterval); 
                resetResendButton(); 
            }
        }, 1000); 
    }

    // --- RESET BUTTON UI ---
    function resetResendButton() {
        resendBtn.style.display = "inline";
        resendBtn.classList.remove("disabled-link");
        resendBtn.textContent = "Resend OTP";
        resendTimerDisplay.style.display = "none";
    }

    // --- MESSAGE HELPER ---
    // Screen par error ya success message dikhane ke liye
    function showMessage(text, color) {
        messageEl.style.display = "block";
        messageEl.textContent = text;
        messageEl.style.color = color;
    }
});