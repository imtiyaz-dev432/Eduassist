document.addEventListener("DOMContentLoaded", function () {
    const token = localStorage.getItem("access_token");
    if (!token) { 
        alert("Please login first"); 
        window.location.href = "login.html"; 
        return; 
    }

    const quizGrid = document.getElementById("quizGrid");
    
    // Backend API jo bachhe ki quizzes fetch karegi
    const API_URL = "http://127.0.0.1:5000/student/quiz/list"; 

    async function loadQuizzes() {
        try {
            const response = await fetch(API_URL, {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });
            const data = await response.json();

            if (response.ok && data.success) {
                if(data.quizzes.length === 0) {
                    quizGrid.innerHTML = `<p class="status-text">No active quizzes available for your batch right now! 🎉</p>`;
                    return;
                }
                
                quizGrid.innerHTML = "";
                
                data.quizzes.forEach(quiz => {
                    // Agar active hai toh 'Start Quiz' ka button dikhega
                    let btnHtml = "";
                    if(quiz.status === "Active") {
                        // 🔥 YAHAN HAI MAIN LINK JO STUDENT KO LIVE EXAM WALE PAGE PAR BHEJEGA 🔥
                        btnHtml = `<a href="student_take_quiz.html?quiz_id=${quiz.id}" class="start-btn"><i class="fas fa-play-circle"></i> Start Quiz</a>`;
                    } else {
                        btnHtml = `<button class="start-btn disabled" disabled>Currently Unavailable</button>`;
                    }

                    // Dynamically set status color
                    const statusColor = quiz.status === 'Active' ? '#10b981' : '#f59e0b';

                    quizGrid.innerHTML += `
                        <div class="quiz-card">
                            <h3 class="q-title">${quiz.title}</h3>
                            <p class="q-meta"><strong>Topic:</strong> ${quiz.topic || 'N/A'}</p>
                            <p class="q-meta"><strong>Difficulty:</strong> ${quiz.difficulty || 'N/A'}</p>
                            <p class="q-meta"><strong>Total Marks:</strong> ${quiz.total_marks}</p>
                            <p class="q-meta"><strong>Status:</strong> <span style="color:${statusColor}; font-weight:bold;">${quiz.status}</span></p>
                            ${btnHtml}
                        </div>
                    `;
                });
            } else {
                quizGrid.innerHTML = `<p class="status-text error">${data.message}</p>`;
            }
        } catch (e) {
            quizGrid.innerHTML = `<p class="status-text error">Network error fetching quizzes.</p>`;
        }
    }

    // Call the function on load
    loadQuizzes();
});