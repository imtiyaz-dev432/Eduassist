const urlParams = new URLSearchParams(window.location.search);
const BATCH_ID = urlParams.get('batch_id') || localStorage.getItem('current_batch_id');
const API_BASE = 'http://127.0.0.1:5000';

let allAssignments = [];

function getToken() { 
    return localStorage.getItem('access_token') || ''; 
}

function authFetch(url, options = {}) {
    const token = getToken();
    const headers = { ...options.headers };
    if (token) headers['Authorization'] = 'Bearer ' + token;
    if (!(options.body instanceof FormData)) headers['Content-Type'] = headers['Content-Type'] || 'application/json';
    return fetch(API_BASE + url, { ...options, headers });
}

function showToast(type, msg) {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}" style="color:${type==='success'?'#10b981':'#ef4444'}"></i> <span>${msg}</span>`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

async function fetchAssignments() {
    if (!BATCH_ID) {
        showToast('error', 'Batch ID not found!');
        return;
    }
    document.getElementById('batchBadge').innerHTML = `<i class="fas fa-layer-group"></i> Batch #${BATCH_ID}`;

    try {
        const res = await authFetch(`/teacher/owner/assessments/assignment/list/${BATCH_ID}`);
        const data = await res.json();
        if (res.ok && data.success) {
            allAssignments = data.assignments || [];
            updateMetrics();
            renderAssignments(allAssignments);
        } else {
            showToast('error', data.message || 'Failed to load assignments');
        }
    } catch (err) {
        showToast('error', 'Network error fetching assignments');
    }
}

function renderAssignments(list) {
    const tbody = document.getElementById('assignmentTableBody');
    if (list.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:30px; color:#6b7280;">No assignments found.</td></tr>';
        return;
    }

    tbody.innerHTML = list.map((a, idx) => {
        const statusClass = a.status === 'Active' ? 'status-active' : a.status === 'Closed' ? 'status-closed' : 'status-draft';
        const fileHtml = a.file_url ? `<span style="color:#10b981;font-weight:600;"><i class="fas fa-file-pdf"></i> Attached</span>` : `<span style="color:#9ca3af;">No file</span>`;

        return `
            <tr>
                <td>${idx + 1}</td>
                <td style="font-weight:600; color:#1f2937;">${a.title}</td>
                <td>${a.due_date || '--'}</td>
                <td>${a.max_marks ?? '--'}</td>
                <td><span class="status-badge ${statusClass}"><span class="dot"></span>${a.status}</span></td>
                <td>${fileHtml}</td>
                <td>
                    <div class="action-icons">
                        <button class="icon-btn" style="color: #10b981; border-color: #10b981; background: #ecfdf5;" title="Check Submissions & Grade" onclick="window.location.href='teacher_submission.html?assignment_id=${a.id}'">
                            <i class="fas fa-clipboard-check"></i>
                        </button>
                        <button class="icon-btn" title="Download Question PDF" ${!a.file_url ? 'disabled' : ''} onclick="downloadFile(${a.id})"><i class="fas fa-download"></i></button>
                        <button class="icon-btn" title="Edit Details" onclick="openEditModal(${a.id})"><i class="fas fa-pen"></i></button>
                        <button class="icon-btn replace" title="Replace PDF" onclick="openReplaceModal(${a.id})"><i class="fas fa-arrows-rotate"></i></button>
                        <button class="icon-btn danger" title="Delete" onclick="handleDelete(${a.id}, '${a.title.replace(/'/g, "\\'")}')"><i class="fas fa-trash"></i></button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function updateMetrics() {
    document.getElementById('metricTotal').textContent = allAssignments.length;
    document.getElementById('metricActive').textContent = allAssignments.filter(a => a.status === 'Active').length;
    document.getElementById('metricDraft').textContent = allAssignments.filter(a => a.status === 'Draft').length;
    document.getElementById('metricClosed').textContent = allAssignments.filter(a => a.status === 'Closed').length;
}

function filterAssignments() {
    const q = document.getElementById('searchInput').value.toLowerCase();
    renderAssignments(allAssignments.filter(a => a.title.toLowerCase().includes(q)));
}

async function handleAddAssignment(e) {
    e.preventDefault();
    const formData = new FormData();
    formData.append('title', document.getElementById('addTitle').value);
    formData.append('description', document.getElementById('addDescription').value);
    formData.append('due_date', document.getElementById('addDueDate').value);
    formData.append('max_marks', document.getElementById('addMaxMarks').value);
    formData.append('status', document.getElementById('addStatus').value);
    const file = document.getElementById('addFileInput').files[0];
    if (file) formData.append('file', file);

    try {
        const res = await authFetch(`/teacher/owner/assessments/assignment/add/${BATCH_ID}`, { method: 'POST', body: formData });
        const data = await res.json();
        if (res.ok && data.success) {
            showToast('success', 'Assignment created successfully!');
            closeAddModal();
            fetchAssignments();
        } else { 
            showToast('error', data.message || 'Failed'); 
        }
    } catch (err) { 
        showToast('error', 'Network error'); 
    }
}

function openEditModal(id) {
    const a = allAssignments.find(x => x.id === id);
    if (!a) return;
    document.getElementById('editAssignId').value = a.id;
    document.getElementById('editTitle').value = a.title;
    document.getElementById('editDescription').value = a.description || '';
    document.getElementById('editDueDate').value = a.due_date || '';
    document.getElementById('editMaxMarks').value = a.max_marks ?? '';
    document.getElementById('editStatus').value = a.status;
    document.getElementById('editModal').classList.add('open');
}

function closeEditModal() { 
    document.getElementById('editModal').classList.remove('open'); 
}

async function handleEditAssignment(e) {
    e.preventDefault();
    const id = document.getElementById('editAssignId').value;
    const payload = {
        title: document.getElementById('editTitle').value,
        description: document.getElementById('editDescription').value,
        due_date: document.getElementById('editDueDate').value,
        max_marks: document.getElementById('editMaxMarks').value,
        status: document.getElementById('editStatus').value
    };

    try {
        const res = await authFetch(`/teacher/owner/assessments/assignment/update/${id}`, {
            method: 'PATCH',
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok && data.success) {
            showToast('success', 'Assignment updated successfully!');
            closeEditModal();
            fetchAssignments();
        } else { 
            showToast('error', data.message || 'Update failed'); 
        }
    } catch (err) { 
        showToast('error', 'Network error'); 
    }
}

function openReplaceModal(id) {
    document.getElementById('replaceAssignId').value = id;
    document.getElementById('replaceFileInput').value = '';
    document.getElementById('replaceModal').classList.add('open');
}

function closeReplaceModal() { 
    document.getElementById('replaceModal').classList.remove('open'); 
}

async function handleReplaceFile() {
    const id = document.getElementById('replaceAssignId').value;
    const file = document.getElementById('replaceFileInput').files[0];
    if (!file) { showToast('error', 'Select a PDF file'); return; }

    const formData = new FormData();
    formData.append('file', file);

    try {
        const res = await authFetch(`/teacher/owner/assessments/assignment/file/replace/${id}`, { method: 'PATCH', body: formData });
        const data = await res.json();
        if (res.ok && data.success) {
            showToast('success', 'PDF replaced successfully!');
            closeReplaceModal();
            fetchAssignments();
        } else { 
            showToast('error', data.message || 'Failed'); 
        }
    } catch (err) { 
        showToast('error', 'Network error'); 
    }
}

async function handleDelete(id, title) {
    if (!confirm(`Delete assignment "${title}"?`)) return;
    try {
        const res = await authFetch(`/teacher/owner/assessments/assignment/delete/${id}`, { method: 'DELETE' });
        const data = await res.json();
        if (res.ok && data.success) {
            showToast('success', 'Assignment deleted!');
            fetchAssignments();
        } else { 
            showToast('error', data.message || 'Failed'); 
        }
    } catch (err) { 
        showToast('error', 'Network error'); 
    }
}

async function downloadFile(id) {
    const token = getToken();
    try {
        const res = await fetch(`${API_BASE}/teacher/owner/assessments/assignment/file/${id}`, { headers: { 'Authorization': 'Bearer ' + token } });
        if (res.ok) {
            const blob = await res.blob();
            window.open(window.URL.createObjectURL(blob), '_blank');
        } else { 
            showToast('error', 'Unable to open PDF'); 
        }
    } catch (err) { 
        showToast('error', 'Network error'); 
    }
}

function openAddModal() { 
    document.getElementById('addAssignmentForm').reset(); 
    document.getElementById('addModal').classList.add('open'); 
}

function closeAddModal() { 
    document.getElementById('addModal').classList.remove('open'); 
}

function handleLogout() { 
    if (confirm("Are you sure you want to log out?")) {
        // 2. Data clear karega
        localStorage.clear();
        sessionStorage.clear();
        
        // 3. Logout success alert dikhayega
        alert("Logged out successfully! Redirecting to login page...");
        
        // 4. Alert par 'OK' dabane ke baad redirect karega
        window.location.href = "teacher_login.html";
     
}

// Call on Load
document.addEventListener('DOMContentLoaded', fetchAssignments);}