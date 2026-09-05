window.goToCourse = function () {
    const urlParams = new URLSearchParams(window.location.search);

    const instId =
        urlParams.get("inst_id") ||
        urlParams.get("institution_id") ||
        localStorage.getItem("institution_id") ||
        localStorage.getItem("coaching_id");

    if (!instId || instId === "null" || instId === "undefined") {
        alert("Institution ID not found. Please select your institute first.");
        window.location.href = "add_institute.html";
        return;
    }

    window.location.href = `add_course.html?institution_id=${instId}`;
};



window.enableLogin = async function (id, button) {

    const token = localStorage.getItem("access_token");

    if (!token || token === "null") {
        alert("Please login first!");
        window.location.href = "login.html";
        return;
    }

    // Password prompt
    const password = prompt(
        "Enter a strong password for this teacher (Min 8 chars, 1 special char):"
    );

    if (!password) {
        return;
    }

    // Button ko temporary disabled karo
    if (button) {
        button.disabled = true;
        button.textContent = "Enabling...";
    }

    try {

        const response = await fetch(
            `http://127.0.0.1:5000/teacher/enable-teacher-login/${id}`,
            {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({
                    password: password
                })
            }
        );

        const data = await response.json();

        if (response.ok && data.success !== false) {

           

            if (button) {

                button.textContent = "✅ Login Enabled";

                button.disabled = true;

                button.style.backgroundColor = "#dcfce7";
                button.style.color = "#16a34a";
                button.style.border = "1px solid #86efac";
                button.style.cursor = "default";
                button.style.fontWeight = "bold";
                button.style.opacity = "1";
            }

        } else {

            
            if (button) {
                button.disabled = false;
                button.textContent = "🔑 Enable Login";
            }

            alert(
                "❌ " +
                (
                    data.message ||
                    "Failed to enable login. Check password requirements."
                )
            );
        }

    } catch (error) {

        console.error("Enable login error:", error);

        // Error par button normal state mein lao
        if (button) {
            button.disabled = false;
            button.textContent = "🔑 Enable Login";
        }

        alert("❌ Error communicating with the server.");
    }
};


window.deleteTeacher = async function (id) {

    const token = localStorage.getItem("access_token");

    if (!token || token === "null") {
        alert("Please login first!");
        window.location.href = "login.html";
        return;
    }

    if (!confirm("Are you sure you want to completely remove this teacher?")) {
        return;
    }

    try {

        const response = await fetch(
            `http://127.0.0.1:5000/teacher/delete/${id}`,
            {
                method: "DELETE",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const data = await response.json().catch(() => ({}));

        if (response.ok) {

            if (typeof window.reloadTeachers === "function") {
                await window.reloadTeachers();
            } else {
                window.location.reload();
            }

        } else {

            alert(
                "❌ " +
                (data.message || "Failed to delete teacher.")
            );
        }

    } catch (error) {

        console.error("Delete teacher error:", error);

        alert("❌ Error deleting teacher.");
    }
};



document.addEventListener("DOMContentLoaded", function () {

    

    const token = localStorage.getItem("access_token");

    if (!token || token === "null") {

        alert("Please login first!");
        window.location.href = "login.html";
        return;
    }

    const urlParams =
        new URLSearchParams(window.location.search);

    let instituteId =
        urlParams.get("inst_id") ||
        urlParams.get("institution_id") ||
        localStorage.getItem("institution_id") ||
        localStorage.getItem("coaching_id");


  
    if (
        !instituteId ||
        instituteId === "null" ||
        instituteId === "undefined" ||
        isNaN(instituteId)
    ) {

        console.error(
            "Invalid Institute ID detected:",
            instituteId
        );

        localStorage.removeItem("institution_id");

        alert(
            "Invalid Institute ID! Please select your Coaching again."
        );

        window.location.href =
            "add_institute.html";

        return;
    }


    // Convert to string
    instituteId = String(instituteId);


    // Save institution ID
    localStorage.setItem(
        "institution_id",
        instituteId
    );


    const courseLink =
        document.getElementById("navCourseLink");

    const batchLink =
        document.getElementById("navBatchLink");


    if (courseLink) {

        courseLink.href =
            `add_course.html?institution_id=${instituteId}`;
    }


    if (batchLink) {

        batchLink.href =
            `add_batch.html?institution_id=${instituteId}`;
    }


    const logoutBtn =
        document.getElementById("globalLogoutBtn");


    if (logoutBtn) {

        logoutBtn.addEventListener(
            "click",
            () => {

                if (
                    confirm(
                        "Are you sure you want to log out?"
                    )
                ) {

                    localStorage.clear();

                    window.location.href =
                        "login.html";
                }
            }
        );
    }

    const nextBtn =
        document.querySelector(".next-step-btn");


    if (nextBtn) {

        nextBtn.addEventListener(
            "click",
            window.goToCourse
        );
    }

    const teacherForm =
        document.getElementById("teacherForm");

    const msgEl =
        document.getElementById("formMessage");

    const submitBtn =
        document.getElementById("saveTeacherBtn");

    const teachersList =
        document.getElementById("teachersList");


    function showMsg(text, type) {

        if (!msgEl) return;

        msgEl.textContent =
            text;

        msgEl.className =
            `message ${type}`;

        msgEl.style.display =
            "block";


        setTimeout(() => {

            msgEl.style.display =
                "none";

            msgEl.className =
                "message";

        }, 4000);
    }

    async function fetchTeachers() {

        try {

            const response = await fetch(
                `http://127.0.0.1:5000/teacher/get/${instituteId}`,
                {
                    method: "GET",
                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );


            const data =
                await response.json();


            if (!teachersList) {
                return;
            }


            if (
                response.ok &&
                Array.isArray(data.teacher_list)
            ) {

                teachersList.innerHTML =
                    "";



                if (
                    data.teacher_list.length === 0
                ) {

                    teachersList.innerHTML = `
                        <p class="loading-text">
                            No teachers added yet.
                            Start by adding one above.
                        </p>
                    `;

                    return;
                }


                // ----------------------------------------------------------
                // Render Every Teacher
                // ----------------------------------------------------------

                data.teacher_list.forEach(
                    (teacher) => {

                        const div =
                            document.createElement(
                                "div"
                            );

                        div.className =
                            "teacher-item";


                        // --------------------------------------------------
                        // LOGIN BUTTON
                        // --------------------------------------------------

                        let loginButton;


                        if (
                            teacher.is_login_enabled === true
                        ) {

                            // =================================================
                            // Already enabled
                            // =================================================

                            loginButton = `
                                <button
                                    type="button"
                                    disabled
                                    style="
                                        background-color: #dcfce7;
                                        color: #16a34a;
                                        border: 1px solid #86efac;
                                        padding: 8px 14px;
                                        border-radius: 6px;
                                        font-weight: bold;
                                        cursor: default;
                                        opacity: 1;
                                    "
                                >
                                    ✅ Login Enabled
                                </button>
                            `;

                        } else {

                            // =================================================
                            // Login not enabled
                            // =================================================

                            loginButton = `
                                <button
                                    type="button"
                                    class="lock-btn"
                                    onclick="enableLogin(${teacher.id}, this)"
                                >
                                    🔑 Enable Login
                                </button>
                            `;
                        }


                        // --------------------------------------------------
                        // Teacher Card
                        // --------------------------------------------------

                        div.innerHTML = `

                            <div class="teacher-info">

                                <h4>
                                    👨‍🏫 ${teacher.name}
                                </h4>

                                <p>
                                    📞 ${teacher.phone}
                                    ${
                                        teacher.email
                                            ? `| ✉️ ${teacher.email}`
                                            : ""
                                    }
                                </p>

                            </div>


                            <div class="item-actions">

                                ${loginButton}

                                <button
                                    type="button"
                                    class="del-btn"
                                    onclick="deleteTeacher(${teacher.id})"
                                >
                                    🗑️ Delete
                                </button>

                            </div>

                        `;


                        teachersList.appendChild(
                            div
                        );

                    }
                );

            } else {

                teachersList.innerHTML = `

                    <p
                        style="
                            color: #ef4444;
                            text-align: center;
                        "
                    >
                        ${
                            data.message ||
                            "Failed to load teachers."
                        }
                    </p>
                `;
            }

        } catch (error) {

            console.error(
                "Fetch teachers error:",
                error
            );


            if (teachersList) {

                teachersList.innerHTML = `

                    <p
                        style="
                            color: #ef4444;
                            text-align: center;
                        "
                    >
                        Server error fetching teachers.
                    </p>

                `;
            }
        }
    }


    // ----------------------------------------------------------------------
    // Expose fetch function globally
    // ----------------------------------------------------------------------

    window.reloadTeachers =
        fetchTeachers;


    // ----------------------------------------------------------------------
    // Initial Load
    // ----------------------------------------------------------------------

    fetchTeachers();


    // ----------------------------------------------------------------------
    // 8. Add Teacher
    // ----------------------------------------------------------------------

    if (teacherForm) {

        teacherForm.addEventListener(
            "submit",
            async (e) => {

                e.preventDefault();


                // ----------------------------------------------------------
                // Disable Save Button
                // ----------------------------------------------------------

                if (submitBtn) {

                    submitBtn.disabled =
                        true;

                    submitBtn.textContent =
                        "Saving...";
                }


                // ----------------------------------------------------------
                // Get Form Data
                // ----------------------------------------------------------

                const payload = {

                    name:
                        document
                            .getElementById(
                                "teacherName"
                            )
                            .value
                            .trim(),

                    mobile_no:
                        document
                            .getElementById(
                                "teacherPhone"
                            )
                            .value
                            .trim(),

                    email:
                        document
                            .getElementById(
                                "teacherEmail"
                            )
                            .value
                            .trim() || null
                };


                try {

                    const response =
                        await fetch(
                            `http://127.0.0.1:5000/teacher/add/${instituteId}`,
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json",

                                    "Authorization":
                                        `Bearer ${token}`
                                },

                                body:
                                    JSON.stringify(
                                        payload
                                    )
                            }
                        );


                    const data =
                        await response.json();


                    if (
                        response.ok &&
                        data.success !== false
                    ) {

                        showMsg(
                            "Teacher Added Successfully!",
                            "success"
                        );

                        teacherForm.reset();

                        await fetchTeachers();

                    } else {

                        showMsg(
                            data.message ||
                                "Failed to add teacher.",
                            "error"
                        );
                    }

                } catch (error) {

                    console.error(
                        "Add teacher error:",
                        error
                    );

                    showMsg(
                        "Server connection error!",
                        "error"
                    );

                } finally {

                    if (submitBtn) {

                        submitBtn.disabled =
                            false;

                        submitBtn.textContent =
                            "💾 Save Teacher";
                    }
                }
            }
        );
    }

});

