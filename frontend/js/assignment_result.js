document.addEventListener("DOMContentLoaded", function () {
    const token = localStorage.getItem("access_token");
    const role = localStorage.getItem("user_role") || localStorage.getItem("role");

    // Security Check
    if (!token || role !== "student") {
        alert("Please login as a student first!");
        window.location.href = "login.html";
        return;
    }

    // Get Assignment ID from URL (e.g., ?assignment_id=5)
    const urlParams = new URLSearchParams(window.location.search);
    const ASSIGNMENT_ID = urlParams.get('assignment_id');

    const API_URL = `http://127.0.0.1:5000/student/result/${ASSIGNMENT_ID}`;

    // UI Elements
    const loadingState = document.getElementById('loadingState');
    const pendingState = document.getElementById('pendingState');
    const errorState = document.getElementById('errorState');
    const resultCard = document.getElementById('resultCard');

    // Hide all states function
    function hideAllStates() {
        loadingState.style.display = 'none';
        pendingState.style.display = 'none';
        errorState.style.display = 'none';
        resultCard.style.display = 'none';
    }

    async function fetchResult() {
        if (!ASSIGNMENT_ID) {
            hideAllStates();
            document.getElementById('errorTitle').textContent = "Invalid Link";
            document.getElementById('errorMessage').textContent = "Assignment ID is missing.";
            errorState.style.display = 'block';
            return;
        }

        try {
            const response = await fetch(API_URL, {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            });

            const data = await response.json();
            hideAllStates();

            if (response.ok && data.success) {
                // Assignment is Checked! Show the Result Card
                document.getElementById('assignTitle').textContent = data.result.assignment_title;
                document.getElementById('assignMarks').textContent = data.result.marks;
                
                // Handle empty feedback
                if (data.result.feedback && data.result.feedback.trim() !== "") {
                    document.getElementById('assignFeedback').textContent = data.result.feedback;
                    document.getElementById('assignFeedback').style.fontStyle = "normal";
                    document.getElementById('assignFeedback').style.color = "#4b5563";
                } else {
                    document.getElementById('assignFeedback').textContent = "No specific feedback provided by the teacher.";
                    document.getElementById('assignFeedback').style.fontStyle = "italic";
                    document.getElementById('assignFeedback').style.color = "#9ca3af";
                }
                
                resultCard.style.display = 'block';

            } else if (response.status === 400 && data.message.includes("not been checked")) {
                // Assignment not checked yet
                pendingState.style.display = 'block';

            } else {
                // Other errors (Not found, Unauthorized, etc.)
                document.getElementById('errorTitle').textContent = "Access Denied";
                document.getElementById('errorMessage').textContent = data.message;
                errorState.style.display = 'block';
            }

        } catch (error) {
            console.error("Fetch error:", error);
            hideAllStates();
            document.getElementById('errorTitle').textContent = "Network Error";
            document.getElementById('errorMessage').textContent = "Failed to connect to the server. Please try again.";
            errorState.style.display = 'block';
        }
    }

    // Call the function
    fetchResult();
});