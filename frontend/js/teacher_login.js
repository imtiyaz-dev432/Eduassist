document.addEventListener("DOMContentLoaded", function () {
    // ==========================================
    // 1. TEACHER LOGIN LOGIC
    // ==========================================
    const loginForm = document.getElementById("teacherLoginForm");
    const loginBtn = document.getElementById("loginBtn");
    const msgEl = document.getElementById("loginMessage");

    if (loginForm) {
        loginForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            
            loginBtn.disabled = true;
            loginBtn.textContent = "Verifying...";

            const loginId = document.getElementById("loginId").value.trim();
            const password = document.getElementById("password").value;

            // SMART LOGIC: Check if input has '@' to decide email vs mobile
            let payload = {
                password: password
            };

            if (loginId.includes("@")) {
                payload.email = loginId;
            } else {
                payload.mobile_no = loginId;
            }

            try {
                const response = await fetch("http://127.0.0.1:5000/teacher/auth/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();
                msgEl.style.display = "block";

                if (response.ok && data.success) {
                    msgEl.style.color = "#10b981"; // Green success text
                    msgEl.style.backgroundColor = "#d1fae5";
                    msgEl.textContent = "Login Successful! Redirecting...";

                    // MAIN STEP: Token aur Role ko LocalStorage mein save karo
                    localStorage.setItem("access_token", data.access_token);
                    localStorage.setItem("user_role", "teacher"); 
                    // Future use ke liye teacher ka data bhi save kar lo
                    localStorage.setItem("teacher_data", JSON.stringify(data.teacher)); 

                    // Redirect to Teacher Dashboard
                    setTimeout(() => {
                        window.location.href = "teacher_dashboard.html";
                    }, 1500);
                } else {
                    msgEl.style.color = "#ef4444";
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
                loginBtn.textContent = "Login to Portal";
            }
        });
    }


    // ==========================================
    // 2. FORGOT PASSWORD MODAL LOGIC
    // ==========================================
    const forgotPwdLink = document.getElementById("forgotPwdLink");
    const forgotPwdModal = document.getElementById("forgotPwdModal");
    const closeBtn = document.querySelector(".close-btn");

    const requestOtpForm = document.getElementById("requestOtpForm");
    const resetPasswordForm = document.getElementById("resetPasswordForm");
    const modalMessage = document.getElementById("modalMessage");

    let resetIdentifierValue = ""; // Email ya Phone ko yaad rakhne ke liye

    // A. Modal Kholna Aur Band Karna
    if (forgotPwdLink) {
        forgotPwdLink.addEventListener("click", function(e) {
            e.preventDefault();
            forgotPwdModal.style.display = "flex";
            requestOtpForm.style.display = "block";
            resetPasswordForm.style.display = "none";
            requestOtpForm.reset();
            resetPasswordForm.reset();
            modalMessage.style.display = "none";
            document.querySelector(".modal-content .subtitle").style.display = "block";
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener("click", () => {
            forgotPwdModal.style.display = "none";
        });
    }

    window.addEventListener("click", (e) => {
        if (e.target === forgotPwdModal) {
            forgotPwdModal.style.display = "none";
        }
    });

    // B. Step 1: Send OTP API Call
    if (requestOtpForm) {
        requestOtpForm.addEventListener("submit", async function(e) {
            e.preventDefault();
            const identifier = document.getElementById("resetIdentifier").value.trim();
            const sendOtpBtn = document.getElementById("sendOtpBtn");
            
            sendOtpBtn.disabled = true;
            sendOtpBtn.textContent = "Sending...";
            
            let payload = identifier.includes("@") ? { email: identifier } : { mobile_no: identifier };

            try {
                const response = await fetch("http://127.0.0.1:5000/teacher/auth/forgot-password", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                const data = await response.json();
                
                modalMessage.style.display = "block";
                if (response.ok || data.success) {
                    modalMessage.style.color = "#10b981";
                    modalMessage.style.backgroundColor = "#d1fae5";
                    modalMessage.textContent = "OTP sent! Please check your email/phone.";
                    
                    resetIdentifierValue = identifier; 
                    
                    // Switch to Step 2 smoothly
                    setTimeout(() => {
                        requestOtpForm.style.display = "none";
                        document.querySelector(".modal-content .subtitle").style.display = "none";
                        resetPasswordForm.style.display = "block";
                        modalMessage.style.display = "none";
                    }, 1500);
                    
                } else {
                    modalMessage.style.color = "#ef4444";
                    modalMessage.style.backgroundColor = "#fee2e2";
                    modalMessage.textContent = data.message || "Failed to send OTP.";
                }
            } catch (error) {
                console.error("Forgot Pwd Error:", error);
                modalMessage.style.color = "#ef4444";
                modalMessage.style.backgroundColor = "#fee2e2";
                modalMessage.textContent = "Server error!";
            } finally {
                sendOtpBtn.disabled = false;
                sendOtpBtn.textContent = "Send OTP";
            }
        });
    }

    // C. Step 2: Verify OTP & Reset Password Call
    if (resetPasswordForm) {
        resetPasswordForm.addEventListener("submit", async function(e) {
            e.preventDefault();
            const otp = document.getElementById("resetOtp").value.trim();
            const newPassword = document.getElementById("newPassword").value;
            const resetPwdBtn = document.getElementById("resetPwdBtn");
            
            resetPwdBtn.disabled = true;
            resetPwdBtn.textContent = "Updating...";
            
            let payload = { otp: otp, password: newPassword };
            if (resetIdentifierValue.includes("@")) {
                payload.email = resetIdentifierValue;
            } else {
                payload.mobile_no = resetIdentifierValue;
            }

            try {
                const response = await fetch("http://127.0.0.1:5000/teacher/auth/reset-password", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                const data = await response.json();
                
                modalMessage.style.display = "block";
                if (response.ok || data.success) {
                    modalMessage.style.color = "#10b981";
                    modalMessage.style.backgroundColor = "#d1fae5";
                    modalMessage.textContent = "Password updated successfully! You can login now.";
                    
                    setTimeout(() => {
                        forgotPwdModal.style.display = "none";
                        modalMessage.style.display = "none";
                    }, 2500);
                } else {
                    modalMessage.style.color = "#ef4444";
                    modalMessage.style.backgroundColor = "#fee2e2";
                    modalMessage.textContent = data.message || "Failed to reset password.";
                }
            } catch (error) {
                console.error("Reset Pwd Error:", error);
                modalMessage.style.color = "#ef4444";
                modalMessage.style.backgroundColor = "#fee2e2";
                modalMessage.textContent = "Server error!";
            } finally {
                resetPwdBtn.disabled = false;
                resetPwdBtn.textContent = "Update Password";
            }
        });
    }
});