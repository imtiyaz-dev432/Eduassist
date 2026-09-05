// UI function for styling selected radio buttons
window.selectOption = function(labelElement) {
    // Remove 'selected' class from all sibling labels
    const siblings = labelElement.parentElement.querySelectorAll('.option-label');
    siblings.forEach(sib => sib.classList.remove('selected'));
    
    // Add 'selected' class to clicked label
    labelElement.classList.add('selected');
};

// Handle Form Submit (Send to Backend)
window.submitQuiz = async function(event) {
    event.preventDefault(); // Stop page reload
    
    if(!confirm("Are you sure you want to submit the quiz? You cannot change answers after this.")) return;

    const submitBtn = document.getElementById("finalSubmitBtn");
    submitBtn.innerHTML = "Submitting... <i class='fas fa-spinner fa-spin'></i>";
    submitBtn.disabled = true;

    const form = document.getElementById("questionsForm");
    const formData = new FormData(form);
    
    const answersArray = [];

    // Get selected answer for each question
    for (let [name, value] of formData.entries()) {
        let question_id = parseInt(name.split("_")[1]); 
        answersArray.push({
            "question_id": question_id,
            "student_answer": value  // Matched exactly with your backend
        });
    }

    const payload = {
        "answers": answersArray
    };

    const urlParams = new URLSearchParams(window.location.search);
    const QUIZ_ID = urlParams.get('quiz_id');
    
    // URL for Backend Submit Route
    const SUBMIT_API_URL = `http://127.0.0.1:5000/student/quiz/my/${QUIZ_ID}`;
    const token = localStorage.getItem("access_token");

    try {
        const response = await fetch(SUBMIT_API_URL, {
            method: "POST",
            headers: { 
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // Hide Questions and Header
            document.getElementById("questionsForm").style.display = "none";
            document.getElementById("quizHeaderInfo").style.display = "none";
            
            // Show Result Box
            const msgBox = document.getElementById("msgBox");
            msgBox.style.display = "block";
            msgBox.innerHTML = `
                <i class="fas fa-check-circle" style="font-size: 60px; color: #10b981; margin-bottom: 20px;"></i>
                <h2 style="color: #1f2937; margin-bottom: 10px;">Quiz Submitted Successfully!</h2>
                <div style="background: #ecfdf5; border: 1px solid #10b981; padding: 25px; border-radius: 12px; display: inline-block; margin-top: 15px;">
                    <h1 style="color: #065f46; font-size: 42px; margin: 0;">
                        ${data.data.obtained_marks} <span style="font-size:24px; color:#10b981;">/ ${data.data.total_marks}</span>
                    </h1>
                    <p style="color: #047857; margin-top: 5px; font-weight: 600; font-size: 16px;">Total Score</p>
                </div>
                <br>
                <button onclick="window.location.href='student_quizzes.html'" style="margin-top: 30px; background: #8b5cf6; color: white; border: none; padding: 12px 25px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: 0.2s;">
                    Go Back to Quizzes ➔
                </button>
            `;
        } else {
            alert("Error: " + data.message);
            submitBtn.innerHTML = "Submit Quiz <i class='fas fa-paper-plane'></i>";
            submitBtn.disabled = false;
        }
    } catch (error) {
        console.error(error);
        alert("Network error! Failed to submit quiz.");
        submitBtn.innerHTML = "Submit Quiz <i class='fas fa-paper-plane'></i>";
        submitBtn.disabled = false;
    }
};

document.addEventListener("DOMContentLoaded", function () {
    const token = localStorage.getItem("access_token");
    const role = localStorage.getItem("user_role") || localStorage.getItem("role");

    if (!token || role !== "student") {
        alert("Please login as a student!");
        window.location.href = "login.html";
        return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    const QUIZ_ID = urlParams.get('quiz_id');
    const msgBox = document.getElementById("msgBox");

    if (!QUIZ_ID) {
        msgBox.innerHTML = `<h3 style="color:red;"><i class="fas fa-exclamation-triangle"></i> Invalid Link</h3><p>Quiz ID is missing.</p>`;
        return;
    }

    // API TO FETCH QUESTIONS
    const API_URL = `http://127.0.0.1:5000/student/quiz/questions/${QUIZ_ID}`;

    async function loadQuiz() {
        try {
            const response = await fetch(API_URL, {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });
            
            const data = await response.json();

            if (response.ok && data.success) {
                msgBox.style.display = "none";
                
                // Set Header Info
                document.getElementById("quizHeaderInfo").style.display = "block";
                document.getElementById("quizTitle").innerText = data.quiz.title;
                document.getElementById("quizTopic").innerHTML = `<i class="fas fa-book"></i> Topic: ${data.quiz.topic || 'N/A'}`;
                document.getElementById("quizDifficulty").innerHTML = `<i class="fas fa-layer-group"></i> Difficulty: ${data.quiz.difficulty || 'N/A'}`;

                // Render Questions
                const qList = document.getElementById("questionsList");
                document.getElementById("questionsForm").style.display = "block";

                if (data.questions.length === 0) {
                    qList.innerHTML = `<div class="message-box"><h3>No questions available in this quiz.</h3></div>`;
                    document.getElementById("finalSubmitBtn").style.display = "none";
                    return;
                }

                data.questions.forEach((q, index) => {
                    const qCard = document.createElement('div');
                    qCard.className = "question-card";
                    qCard.innerHTML = `
                        <div class="q-text">
                            <span>${index + 1}. ${q.question}</span>
                            <span class="q-marks">${q.marks} Marks</span>
                        </div>
                        <div class="options-container">
                            <label class="option-label" onclick="selectOption(this)">
                                <input type="radio" name="q_${q.id}" value="A" required> 
                                <span>A. ${q.option_a}</span>
                            </label>
                            <label class="option-label" onclick="selectOption(this)">
                                <input type="radio" name="q_${q.id}" value="B"> 
                                <span>B. ${q.option_b}</span>
                            </label>
                            <label class="option-label" onclick="selectOption(this)">
                                <input type="radio" name="q_${q.id}" value="C"> 
                                <span>C. ${q.option_c}</span>
                            </label>
                            <label class="option-label" onclick="selectOption(this)">
                                <input type="radio" name="q_${q.id}" value="D"> 
                                <span>D. ${q.option_d}</span>
                            </label>
                        </div>
                    `;
                    qList.appendChild(qCard);
                });

            } else {
                msgBox.innerHTML = `<h3 style="color:red;"><i class="fas fa-ban"></i> Access Denied</h3><p>${data.message}</p>`;
            }
        } catch (error) {
            msgBox.innerHTML = `<h3 style="color:red;"><i class="fas fa-wifi"></i> Network Error</h3><p>Could not connect to the server.</p>`;
        }
    }

    loadQuiz();
});