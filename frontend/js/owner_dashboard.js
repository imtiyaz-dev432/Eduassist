document.addEventListener("DOMContentLoaded", function () {
    const token = localStorage.getItem("access_token");
    const role = localStorage.getItem("role");
    
    // Security Check
    if (!token || role !== "owner") {
        alert("Access Denied! Owner login required.");
        window.location.href = "login.html";
        return;
    }

    async function fetchDashboardData() {
        const errorEl = document.getElementById("dashboardError");
        
        try {
            const response = await fetch("http://127.0.0.1:5000/owner/dashboard/", {
                method: "GET",
                headers: { 
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}` 
                }
            });
            const result = await response.json();

            if (response.ok && result.success) {
                const data = result.data;

                // 🔥 SMART ID FINDER: Data mein kisi bhi naam se ID aaye, pakad lega
                const actualInstId = data.institution_id || data.institute_id || data.id || (data.institute && data.institute.id) || "1";
                localStorage.setItem("institution_id", actualInstId);

                // Update Action Links with correct ID
                document.getElementById("navCourseLink").href = `add_course.html?institution_id=${actualInstId}`;
                document.getElementById("navBatchLink").href = `add_batch.html?institution_id=${actualInstId}`;
                document.getElementById("actionCourseBtn").href = `add_course.html?institution_id=${actualInstId}`;
                document.getElementById("actionBatchBtn").href = `add_batch.html?institution_id=${actualInstId}`;
                
                // Add FAQ Link Update
                const faqLink = document.getElementById("navFaqLink");
                if(faqLink) faqLink.href = `add_faq.html?institution_id=${actualInstId}`;

                // Public Link Generate
                generatePublicLink(actualInstId);

                // Update Header Info
                document.getElementById("topbarInstName").textContent = data.institution_name || "Institute Portal";
                document.getElementById("welcomeText").textContent = `Welcome to ${data.institution_name || 'your Institute'}!`;

                // Update Metrics Numbers
                document.getElementById("totalTeachers").textContent = data.metrics?.total_teachers || 0;
                document.getElementById("totalStudents").textContent = data.metrics?.total_students || 0;
                document.getElementById("totalCourses").textContent = data.metrics?.total_courses || 0;
                document.getElementById("totalBatches").textContent = data.metrics?.total_batches || 0;
                document.getElementById("activeBatches").textContent = data.metrics?.active_batches || 0;

                // Populate Recent Batches Table
                const tbody = document.getElementById("recentBatchesBody");
                tbody.innerHTML = ""; 
                
                if (!data.recent_batches || data.recent_batches.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="3" style="text-align:center; color:#6b7280;">No batches created yet.</td></tr>`;
                } else {
                    data.recent_batches.forEach(batch => {
                        let statusColor = batch.status === 'Active' ? '#10b981' : '#f59e0b';
                        let seatsDisplay = (batch.total_seats && batch.total_seats > 0) ? batch.total_seats : 'N/A';
                        const tr = document.createElement("tr");
                        tr.innerHTML = `
                            <td><b>${batch.batch_name}</b></td>
                            <td>${seatsDisplay}</td>
                            <td><span style="background:${statusColor}20; color:${statusColor}; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:bold;">${batch.status || 'Active'}</span></td>
                        `;
                        tbody.appendChild(tr);
                    });
                }
            } else {
                if (errorEl) {
                    errorEl.style.display = "block";
                    errorEl.textContent = result.message || "Failed to load dashboard data.";
                }
            }
        } catch (error) {
            console.error("Dashboard Fetch Error:", error);
            if (errorEl) {
                errorEl.style.display = "block";
                errorEl.textContent = "Unable to connect to the server. Please check your backend.";
            }
        }
    }

    fetchDashboardData();

    // PUBLIC LINK GENERATION & COPY LOGIC
    function generatePublicLink(institutionId) {
        const baseUrl = window.location.origin; 
        const finalUrl = `${baseUrl}/frontend/html/institute_profile.html?id=${institutionId}`;
        const linkInput = document.getElementById("publicLinkInput");
        if (linkInput) {
            linkInput.value = finalUrl;
        }
    }

    window.copyPublicLink = function() {
        const copyText = document.getElementById("publicLinkInput");
        if (!copyText) return;
        copyText.select();
        copyText.setSelectionRange(0, 99999); 
        navigator.clipboard.writeText(copyText.value).then(() => {
            alert("✅ Link Copied! Ab ise WhatsApp ya Instagram par share karein.");
        }).catch(err => {
            alert("❌ Copy failed!");
        });
    };

    // Logout Action
    document.getElementById("globalLogoutBtn").addEventListener("click", function() {
        if (confirm("Are you sure you want to log out?")) {
            localStorage.clear(); 
            window.location.href = "login.html";
        }
    });
});