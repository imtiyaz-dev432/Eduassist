// ==========================================
// AI CHAT WIDGET LOGIC
// ==========================================
let chatOpen = false;

// UI Toggle Function (Open/Close Chat)
window.toggleChat = function() {
    const chatBox = document.getElementById("chatBox");
    chatOpen = !chatOpen;
    chatBox.style.display = chatOpen ? "flex" : "none";
};

// Enter key press handler
window.handleKeyPress = function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
};

window.sendMessage = async function() {
    const inputField = document.getElementById("userInput");
    const messageText = inputField.value.trim();
    
    if (messageText === "") return;

    // 1. Show User Message
    appendMessage("user-message", messageText);
    inputField.value = "";
    
    // 2. Show Loading state
    const loadingId = appendMessage("ai-message loading", "AI is typing...");

    try {
        // 🔥 UPDATE THIS URL ONCE YOUR PYTHON FLASK ROUTE IS READY 🔥
        const response = await fetch("http://127.0.0.1:5000/public/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: messageText })
        });

        const data = await response.json();

        // 3. Remove Loading message
        document.getElementById(loadingId).remove();

        if (response.ok && data.success) {
            // 4. Show AI reply
            appendMessage("ai-message", data.reply);
        } else {
            appendMessage("ai-message", "Sorry, kuch error aa gaya. " + (data.message || ""));
        }
    } catch (error) {
        document.getElementById(loadingId).remove();
        appendMessage("ai-message", "Network error! Server se connect nahi ho paaya.");
    }
};

// Helper function to append message to chat box
function appendMessage(className, text) {
    const chatMessages = document.getElementById("chatMessages");
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${className}`;
    msgDiv.textContent = text;
    
    // Create a unique ID for removing loading messages later
    const id = "msg-" + Math.random().toString(36).substr(2, 9);
    msgDiv.id = id;

    chatMessages.appendChild(msgDiv);
    
    // Smooth auto-scroll to the newest message
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 10);
    
    return id;
}