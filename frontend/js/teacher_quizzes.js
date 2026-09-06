const urlParams = new URLSearchParams(window.location.search);
const BATCH_ID = urlParams.get('batch_id') || localStorage.getItem('current_batch_id');
const API_BASE = 'http://127.0.0.1:5000/quiz';
let quizzes = [];

window.authFetch = function(url, options = {}) {
    const token = localStorage.getItem('access_token');
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
    if (token) headers['Authorization'] = 'Bearer ' + token;
    return fetch(API_BASE + url, { ...options, headers });
};

window.showToast = function(msg, isSuccess=true) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.style.borderLeftColor = isSuccess ? '#10b981' : '#ef4444';
    toast.innerHTML = `<i class="fas ${isSuccess ? 'fa-check' : 'fa-times'}" style="color:${isSuccess ? '#10b981' : '#ef4444'}"></i> ${msg}`;
    document.getElementById('toastContainer').appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
};

window.fetchQuizzes = async function() {
    if(!BATCH_ID || BATCH_ID === 'null') {
        document.getElementById('quizTableBody').innerHTML = '<tr><td colspan="6" style="text-align:center; color:red;">Error: Batch ID missing in URL. Please open this page from the Dashboard.</td></tr>';
        return showToast('Batch ID missing', false);
    }
    
    try {
        const res = await authFetch(`/get/${BATCH_ID}`);
        const data = await res.json();
        if(data.success) {
            quizzes = data["quiz list"] || [];
            renderQuizzes();
        } else showToast(data.message, false);
    } catch(e) { 
        showToast('Network Error', false); 
    }
};

window.renderQuizzes = function() {
    const tbody = document.getElementById('quizTableBody');
    if(quizzes.length === 0) return tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No quizzes found.</td></tr>';
    
    tbody.innerHTML = quizzes.map(q => `
        <tr>
            <td><strong>${q.title}</strong></td>
            <td>${q.topic || '-'}</td>
            <td><span style="background:#f3f4f6; padding:4px 8px; border-radius:4px; font-size:12px;">${q.difficulty}</span></td>
            <td>${q.total_marks}</td>
            <td><span style="color:${q.status==='Active'?'#10b981':(q.status==='Draft'?'#f59e0b':'#ef4444')}; font-weight:bold;">${q.status}</span></td>
            <td>
                <div class="action-icons">
                    <button class="icon-btn" title="Manage Questions" style="color:#8b5cf6; border-color:#8b5cf6;" onclick="window.location.href='teacher_quiz_questions.html?quiz_id=${q.id}'"><i class="fas fa-list-ol"></i></button>
                    <button class="icon-btn" title="Edit" onclick="openEditModal(${q.id})"><i class="fas fa-pen"></i></button>
                    <button class="icon-btn" title="Delete" style="color:#ef4444;" onclick="deleteQuiz(${q.id})"><i class="fas fa-trash"></i></button>
                </div>
            </td>
        </tr>
    `).join('');
};

window.addQuiz = async function(e) {
    e.preventDefault();
    
    if(!BATCH_ID || BATCH_ID === 'null') {
        showToast('Error: Batch ID is missing!', false);
        return;
    }

    const payload = {
        title: document.getElementById('a_title').value,
        topic: document.getElementById('a_topic').value,
        difficulty: document.getElementById('a_diff').value,
        total_marks: parseInt(document.getElementById('a_marks').value),
        status: document.getElementById('a_status').value
    };

    try {
        const res = await authFetch(`/add/${BATCH_ID}`, { method: 'POST', body: JSON.stringify(payload) });
        
        if (!res.ok && res.status === 404) {
            return showToast('API route not found. Check backend URL.', false);
        }

        const data = await res.json();
        if(data.success) { 
            showToast('Quiz Added!'); 
            closeModal('addModal'); 
            fetchQuizzes(); 
        } else { 
            showToast(data.message, false); 
        }
    } catch (err) {
        console.error(err);
        showToast('Something went wrong!', false);
    }
};

window.openEditModal = function(id) {
    const q = quizzes.find(x => x.id === id);
    document.getElementById('e_id').value = q.id;
    document.getElementById('e_title').value = q.title;
    document.getElementById('e_topic').value = q.topic;
    document.getElementById('e_diff').value = q.difficulty;
    document.getElementById('e_marks').value = q.total_marks;
    document.getElementById('e_status').value = q.status;
    openModal('editModal');
};

window.editQuiz = async function(e) {
    e.preventDefault();
    const id = document.getElementById('e_id').value;
    const payload = {
        title: document.getElementById('e_title').value,
        topic: document.getElementById('e_topic').value,
        difficulty: document.getElementById('e_diff').value,
        total_marks: parseInt(document.getElementById('e_marks').value),
        status: document.getElementById('e_status').value
    };
    const res = await authFetch(`/update/${id}`, { method: 'PATCH', body: JSON.stringify(payload) });
    const data = await res.json();
    if(data.success) { 
        showToast('Updated!'); 
        closeModal('editModal'); 
        fetchQuizzes(); 
    } else { 
        showToast(data.message, false); 
    }
};

window.deleteQuiz = async function(id) {
    if(!confirm('Delete this quiz?')) return;
    const res = await authFetch(`/delete/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if(data.success) { 
        showToast('Deleted!'); 
        fetchQuizzes(); 
    } else { 
        showToast(data.message, false); 
    }
};

window.openModal = function(id) { 
    document.getElementById(id).classList.add('open'); 
};
window.closeModal = function(id) { 
    document.getElementById(id).classList.remove('open'); 
    document.getElementById(id).querySelector('form').reset(); 
};

document.addEventListener('DOMContentLoaded', () => {
    // Auth Check
    const token = localStorage.getItem('access_token');
    if(!token) {
        alert("Please login first!");
        window.location.href = "teacher_.html";
        return;
    }
    fetchQuizzes();
});