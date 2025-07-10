// Show success alert when redirected to /success
if (window.location.href.includes("success")) {
    alert("Helper registered successfully!");
}

// Basic login form validation
const loginForm = document.querySelector('.login-form');
if (loginForm) {
    loginForm.addEventListener('submit', function (e) {
        const email = loginForm.email.value;
        const password = loginForm.password.value;

        if (!email.includes('@') || password.length < 5) {
            e.preventDefault();
            alert(" Please enter a valid email and password (min 5 characters).");
        }
    });
}
