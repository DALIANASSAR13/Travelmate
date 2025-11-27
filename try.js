document.addEventListener('DOMContentLoaded', function() {
    // -------- Smooth scroll (لو استخدمت anchors في المستقبل) --------
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href && href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // -------- Animation للـfeature cards --------
    const featureCards = document.querySelectorAll('.feature-card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });
    
    featureCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(card);
    });

    // -------- Navbar background on scroll --------
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.style.backgroundColor = 'rgba(245, 247, 248, 0.95)';
        } else {
            navbar.style.backgroundColor = 'rgba(245, 247, 248, 0.8)';
        }
    });

    // -------- عناصر الـAuth --------
    const myBookingBtn = document.getElementById("myBookingBtn");
    const navSignUpBtn = document.getElementById("navSignUpBtn");
    const logoutBtn = document.getElementById("logoutBtn");

    const signInForm = document.getElementById("signInForm");
    const signUpForm = document.getElementById("signUpForm");

    const loginEmailInput = document.getElementById("loginEmail");
    const loginPasswordInput = document.getElementById("loginPassword");
    const loginError = document.getElementById("loginError");

    const signupFirstNameInput = document.getElementById("signupFirstName");
    const signupLastNameInput = document.getElementById("signupLastName");
    const signupEmailInput = document.getElementById("signupEmail");
    const signupPasswordInput = document.getElementById("signupPassword");
    const signupError = document.getElementById("signupError");

    // -------- Switch بين المودالين --------
    document.getElementById('goToSignUp').addEventListener('click', function(){
      const signInModal = bootstrap.Modal.getInstance(document.getElementById('signInModal'));
      signInModal.hide();
      const signUpModal = new bootstrap.Modal(document.getElementById('signUpModal'));
      signUpModal.show();
    });

    document.getElementById('goToSignIn').addEventListener('click', function(){
      const signUpModal = bootstrap.Modal.getInstance(document.getElementById('signUpModal'));
      signUpModal.hide();
      const signInModal = new bootstrap.Modal(document.getElementById('signInModal'));
      signInModal.show();
    });

    // -------- إعداد الـAPI --------
    const API_BASE = "/api/auth";
    let currentUser = null;

    function setLoading(form, isLoading) {
        const btn = form.querySelector("button[type='submit'], .custom-btn");
        if (!btn) return;
        if (isLoading) {
            btn.disabled = true;
            btn.dataset.originalText = btn.innerHTML;
            btn.innerHTML = "Please wait...";
        } else {
            btn.disabled = false;
            if (btn.dataset.originalText) {
                btn.innerHTML = btn.dataset.originalText;
            }
        }
    }

    function closeModal(id) {
        const modalEl = document.getElementById(id);
        const instance = bootstrap.Modal.getInstance(modalEl);
        if (instance) instance.hide();
    }

    function updateUIAfterLogin(user) {
        currentUser = user;
        closeModal("signInModal");
        closeModal("signUpModal");

        if (myBookingBtn) {
            myBookingBtn.dataset.loggedIn = "true";
            myBookingBtn.textContent = "My Booking";
        }
        if (navSignUpBtn) {
            navSignUpBtn.style.display = "none";
        }
        if (logoutBtn) {
            logoutBtn.style.display = "inline-block";
        }

        console.log("Logged in as:", user);
    }

    function updateUIAfterLogout() {
        currentUser = null;
        if (myBookingBtn) {
            myBookingBtn.dataset.loggedIn = "false";
        }
        if (navSignUpBtn) {
            navSignUpBtn.style.display = "inline-block";
        }
        if (logoutBtn) {
            logoutBtn.style.display = "none";
        }
    }

    async function callApi(url, data) {
        const res = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "include",
            body: JSON.stringify(data)
        });

        let json;
        try {
            json = await res.json();
        } catch (_) {
            json = { success: false, message: "Unexpected server response." };
        }

        if (!res.ok || json.success === false) {
            throw new Error(json.message || "Request failed");
        }
        return json;
    }

    // -------- Sign In --------
    signInForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        loginError.textContent = "";

        const email = loginEmailInput.value.trim();
        const password = loginPasswordInput.value.trim();

        if (!email || !password) {
            loginError.textContent = "Please enter email and password.";
            return;
        }

        setLoading(signInForm, true);
        try {
            const result = await callApi(`${API_BASE}/login`, { email, password });
            updateUIAfterLogin(result.user);
        } catch (err) {
            loginError.textContent = err.message || "Login failed.";
        } finally {
            setLoading(signInForm, false);
        }
    });

    // -------- Sign Up --------
    signUpForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        signupError.textContent = "";

        const first_name = signupFirstNameInput.value.trim();
        const last_name = signupLastNameInput.value.trim();
        const email = signupEmailInput.value.trim();
        const password = signupPasswordInput.value.trim();

        if (!first_name || !last_name || !email || !password) {
            signupError.textContent = "All fields are required.";
            return;
        }

        setLoading(signUpForm, true);
        try {
            const result = await callApi(`${API_BASE}/signup`, {
                first_name,
                last_name,
                email,
                password
            });
            updateUIAfterLogin(result.user);
        } catch (err) {
            signupError.textContent = err.message || "Sign up failed.";
        } finally {
            setLoading(signUpForm, false);
        }
    });

    // -------- My Booking behaviour --------
    if (myBookingBtn) {
        myBookingBtn.addEventListener("click", (e) => {
            const loggedIn = myBookingBtn.dataset.loggedIn === "true";
            if (!loggedIn) {
                // يفتح Modal الـSign In (السلوك الافتراضي للـdata-bs)
                return;
            } else {
                e.preventDefault();
                window.location.href = "mybooking.html";
            }
        });
    }

    // -------- Logout --------
    if (logoutBtn) {
        logoutBtn.addEventListener("click", async () => {
            try {
                await callApi(`${API_BASE}/logout`, {});
            } catch (err) {
                console.log("Logout error (ignored):", err.message);
            }
            updateUIAfterLogout();
            window.location.href = "/";
        });
    }

    // -------- تحقق من السيشن عند تحميل الصفحة --------
    (async () => {
        try {
            const res = await fetch(`${API_BASE}/me`, {
                credentials: "include"
            });
            const data = await res.json();
            if (data.authenticated && data.user) {
                updateUIAfterLogin(data.user);
            } else {
                updateUIAfterLogout();
            }
        } catch (err) {
            console.log("Not logged in");
            updateUIAfterLogout();
        }
    })();
});
