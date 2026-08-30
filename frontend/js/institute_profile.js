document.addEventListener("DOMContentLoaded", function () {
    // 1. URL SE ID NIKALNA
    const urlParams = new URLSearchParams(window.location.search);
    const institutionId = urlParams.get("id");

    // Agar ID nahi hai, toh page par error dikhao
    if (!institutionId) {
        document.getElementById("instName").textContent = "Error: Institute Not Found";
        document.getElementById("instAddress").textContent = "Invalid or broken link.";
    } else {
        document.getElementById("instName").textContent = "Institute Portal #" + institutionId;
        document.getElementById("instAddress").textContent = "Ask our AI bot for course & fee details!";
    }

    // 2. CHAT WIDGET LOGIC
    let chatOpen = false;

    window.toggleChat = function() {
        const chatBox = document.getElementById("chatBox");
        chatOpen = !chatOpen;
        chatBox.style.display = chatOpen ? "flex" : "none";
    };

    window.handleKeyPress = function(event) {
        if (event.key === "Enter") sendMessage();
    };

    window.sendMessage = async function() {
        if (!institutionId) {
            alert("Institute ID is missing! Cannot chat.");
            return;
        }

        const inputField = document.getElementById("userInput");
        const messageText = inputField.value.trim();
        if (messageText === "") return;

        // 🔥 Yahan hum Student ka Name aur Phone input se nikalenge
        const visitorName = document.getElementById("visitorName").value.trim();
        const visitorPhone = document.getElementById("visitorPhone").value.trim();

        // Show User Message
        appendMessage("user-message", messageText);
        inputField.value = "";
        
        // Show Loading
        const loadingId = appendMessage("ai-message loading", "AI is typing...");

        try {
            // 🔥 BACKEND API CALL 🔥
            const response = await fetch(`http://127.0.0.1:5000/admission-bot/chat/${institutionId}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    message: messageText,
                    name: visitorName !== "" ? visitorName : null,  // Agar fill kiya hai toh bhejo
                    phone: visitorPhone !== "" ? visitorPhone : null // Agar fill kiya hai toh bhejo
                })
            });

            const data = await response.json();
            document.getElementById(loadingId).remove();

            if (response.ok && data.success) {
                appendMessage("ai-message", data.reply);
            } else {
                appendMessage("ai-message", "Error: " + (data.message || "Failed to get reply."));
            }
        } catch (error) {
            document.getElementById(loadingId).remove();
            appendMessage("ai-message", "Network error! Server unreachable.");
        }
    };

    function appendMessage(className, text) {
        const chatMessages = document.getElementById("chatMessages");
        const msgDiv = document.createElement("div");
        msgDiv.className = `message ${className}`;
        msgDiv.textContent = text;
        
        const id = "msg-" + Math.random().toString(36).substr(2, 9);
        msgDiv.id = id;
        chatMessages.appendChild(msgDiv);
        
        // Auto-scroll to bottom
        setTimeout(() => chatMessages.scrollTop = chatMessages.scrollHeight, 10);
        return id;
    }
});