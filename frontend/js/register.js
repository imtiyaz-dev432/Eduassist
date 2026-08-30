// Safety Lock: HTML poora load hone ka wait karega
document.addEventListener("DOMContentLoaded", function () {
    
    // 1. Form aur elements ko pakdo
    const form = document.getElementById("registerForm");
    const messageEl = document.getElementById("messageBox"); 
    const registerBtn = document.querySelector(".submit-btn");

    // 2. Agar form mil gaya, toh aage ka kaam karo
    if (form) {
        form.addEventListener("submit", async function (event) {
            event.preventDefault(); // Page reload hone se roko

            // Data uthao
            const nameInput = document.getElementById("regName").value.trim();
            const emailInput = document.getElementById("regEmail").value.trim();
            const mobileInput = document.getElementById("regMobile").value.trim();
            const passwordInput = document.getElementById("regPassword").value;
            
            // Loading UI dikhao
            messageEl.style.display = "block";
            messageEl.textContent = "Checking details...";
            messageEl.style.color = "#6b7280";
            registerBtn.disabled = true;

            try {
                // PYTHON API KO DATA BHEJO 
                // (Agar codespace public URL use karna hai toh localhost ki jagah wo daal dena)
                // Sahi wala code (Ek hi quote rahega end mein):
             const response = await fetch("http://127.0.0.1:5000/auth/register", {
    method: "POST",
    // baki ka code same rahega...
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        name: nameInput,
                        email: emailInput,
                        mobile_no: mobileInput,
                        password: passwordInput
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    // Success!
                    messageEl.style.color = "#4ade80"; 
                    messageEl.textContent = data.message || "Registration successful!";
                    sessionStorage.setItem("verify_id", emailInput); 
                    
                    // 2 second baad otp page par jao
                    setTimeout(() => {
                        window.location.href = "verify-otp.html";
                    }, 2000);
                } else {
                    // Backend ne error diya (jaise: Password too short)
                    messageEl.style.color = "#f87171"; 
                    messageEl.textContent = data.message; 
                }

            } catch (error) {
                console.error("Backend connection error:", error);
                messageEl.style.color = "#f87171";
                messageEl.textContent = "Server is down or not responding.";
            } finally {
                // Button wapas enable karo
                registerBtn.disabled = false; 
            }
        });
    } else {
        console.error("HTML mein registerForm nahi mila!");
    }
});