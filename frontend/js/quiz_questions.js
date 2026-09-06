// URL Parameter Setup
const urlParams = new URLSearchParams(window.location.search);
const QUIZ_ID = urlParams.get('quiz_id');
const API_BASE = 'http://127.0.0.1:5000/quiz_question'; // Backend API
let questionsList = [];

// Authentication Header setup
function authFetch(url, options = {}) {
    const token = localStorage.getItem('access_token');
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
    if (token) headers['Authorization'] = 'Bearer ' + token;
    return fetch(API_BASE + url, { ...options, headers });
}

// Beautiful Toast Notifications
window.showToast = function(msg, isSuccess=true) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.style.borderLeftColor = isSuccess ? '#10b981' : '#ef4444';
    toast.innerHTML = `<i class="fas ${isSuccess ? 'fa-check-circle' : 'fa-exclamation-circle'}" style="color:${isSuccess ? '#10b981' : '#ef4444'}; font-size: 18px;"></i> <span style="color:#374151;">${msg}</span>`;
    document.getElementById('toastContainer').appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
}

// ==========================================
// 1. GET ALL QUESTIONS API
// ==========================================
async function fetchQuestions() {
    if(!QUIZ_ID || QUIZ_ID === 'null') {
        document.getElementById('questionsContainer').innerHTML = `
            <div style="text-align:center; padding: 40px; background: white; border-radius: 12px; color: #ef4444;">
                <i class="fas fa-exclamation-triangle" style="font-size:30px; margin-bottom:10px;"></i>
                <h3>Error: Quiz ID is missing in URL!</h3>
                <p style="color:#6b7280; margin-top:5px;">Please navigate here from the Manage Quizzes page.</p>
            </div>`;
        return;
    }

    try {
        const res = await authFetch(`/get/${QUIZ_ID}`);
        const data = await res.json();
        if(data.success) {
            questionsList = data.question_list || [];
            renderQuestions();
        } else {
            showToast(data.message, false);
        }
    } catch(e) {
        console.error(e);
        showToast('Network Error: Cannot connect to server', false);
    }
}

// Render Questions to HTML
function renderQuestions() {
    const container = document.getElementById('questionsContainer');
    
    if(questionsList.length === 0) {
        container.innerHTML = `
            <div style="text-align:center; padding: 50px 20px; background: white; border-radius: 12px; border: 1px dashed #d1d5db;">
                <i class="fas fa-clipboard-question" style="font-size: 40px; color: #d1d5db; margin-bottom: 15px;"></i>
                <h3 style="color: #374151;">No questions added yet</h3>
                <p style="color: #6b7280; margin-top: 5px;">Click on the 'Add New Question' button to get started.</p>
            </div>`;
        return;
    }
    
    container.innerHTML = questionsList.map((q, index) => `
        <div class="question-card">
            <div class="q-header">
                <div class="q-title">Q${index + 1}. ${q.question}</div>
                <div class="action-badges">
                    <span class="badge">Marks: ${q.marks}</span>
                    <button class="icon-btn edit" title="Edit Question" onclick="openEditModal(${q.id})"><i class="fas fa-pen"></i></button>
                    <button class="icon-btn delete" title="Delete Question" onclick="deleteQuestion(${q.id})"><i class="fas fa-trash"></i></button>
                </div>
            </div>
            
            <div class="options-grid">
                <div class="opt ${q.correct_answer === 'A' ? 'correct' : ''}">
                    <span class="opt-label">A</span> ${q.option_a}
                </div>
                <div class="opt ${q.correct_answer === 'B' ? 'correct' : ''}">
                    <span class="opt-label">B</span> ${q.option_b}
                </div>
                <div class="opt ${q.correct_answer === 'C' ? 'correct' : ''}">
                    <span class="opt-label">C</span> ${q.option_c}
                </div>
                <div class="opt ${q.correct_answer === 'D' ? 'correct' : ''}">
                    <span class="opt-label">D</span> ${q.option_d}
                </div>
            </div>
            
            ${q.explanation ? `
            <div class="explanation-box">
                <strong><i class="fas fa-lightbulb" style="color:#eab308; margin-right:5px;"></i> Explanation:</strong> 
                ${q.explanation}
            </div>` : ''}
        </div>
    `).join('');
}

// ==========================================
// 2. ADD QUESTION API
// ==========================================
window.addQuestion = async function(e) {
    e.preventDefault();
    
    if(!QUIZ_ID || QUIZ_ID === 'null') return showToast('Quiz ID Missing!', false);

    const payload = {
        question: document.getElementById('a_q').value,
        option_a: document.getElementById('a_a').value,
        option_b: document.getElementById('a_b').value,
        option_c: document.getElementById('a_c').value,
        option_d: document.getElementById('a_d').value,
        correct_answer: document.getElementById('a_correct').value,
        marks: parseInt(document.getElementById('a_marks').value),
        explanation: document.getElementById('a_exp').value
    };

    try {
        const res = await authFetch(`/add/${QUIZ_ID}`, { method: 'POST', body: JSON.stringify(payload) });
        const data = await res.json();
        
        if(data.success) { 
            showToast('Question successfully added!'); 
            closeModal('addModal'); 
            fetchQuestions(); 
        } else { 
            showToast(data.message, false); 
        }
    } catch (err) {
        showToast('Something went wrong!', false);
    }
}

// ==========================================
// 3. EDIT QUESTION API
// ==========================================
window.openEditModal = function(id) {
    const q = questionsList.find(x => x.id === id);
    if(!q) return;

    document.getElementById('e_id').value = q.id;
    document.getElementById('e_q').value = q.question;
    document.getElementById('e_a').value = q.option_a;
    document.getElementById('e_b').value = q.option_b;
    document.getElementById('e_c').value = q.option_c;
    document.getElementById('e_d').value = q.option_d;
    document.getElementById('e_correct').value = q.correct_answer;
    document.getElementById('e_marks').value = q.marks;
    document.getElementById('e_exp').value = q.explanation || '';
    
    openModal('editModal');
}

window.editQuestion = async function(e) {
    e.preventDefault();
    const id = document.getElementById('e_id').value;
    
    const payload = {
        question: document.getElementById('e_q').value,
        option_a: document.getElementById('e_a').value,
        option_b: document.getElementById('e_b').value,
        option_c: document.getElementById('e_c').value,
        option_d: document.getElementById('e_d').value,
        correct_answer: document.getElementById('e_correct').value,
        marks: parseInt(document.getElementById('e_marks').value),
        explanation: document.getElementById('e_exp').value
    };

    try {
        const res = await authFetch(`/update/${id}`, { method: 'PATCH', body: JSON.stringify(payload) });
        const data = await res.json();
        
        if(data.success) { 
            showToast('Question updated successfully!'); 
            closeModal('editModal'); 
            fetchQuestions(); 
        } else { 
            showToast(data.message, false); 
        }
    } catch (err) {
        showToast('Something went wrong!', false);
    }
}

// ==========================================
// 4. DELETE QUESTION API
// ==========================================
window.deleteQuestion = async function(id) {
    if(!confirm('Are you sure you want to delete this question? This action cannot be undone.')) return;
    
    try {
        const res = await authFetch(`/delete/${id}`, { method: 'DELETE' });
        const data = await res.json();
        
        if(data.success) { 
            showToast('Question deleted!'); 
            fetchQuestions(); 
        } else { 
            showToast(data.message, false); 
        }
    } catch (err) {
        showToast('Something went wrong!', false);
    }
}

// UI Helpers
window.openModal = function(id) { 
    document.getElementById(id).classList.add('open'); 
}
window.closeModal = function(id) { 
    document.getElementById(id).classList.remove('open'); 
    document.getElementById(id).querySelector('form').reset(); 
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Check auth token before loading anything
    const token = localStorage.getItem("access_token");
    if (!token) {
        alert("Please login first!");
        window.location.href = "login.html"; // Redirect to login
        return;
    }
    fetchQuestions();
});