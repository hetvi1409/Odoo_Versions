function togglePasswordVisibility() {
    var passwordInput = document.getElementById("password");
    console.log('Password input element:', passwordInput);
    var passwordToggleIcon = document.getElementById("passwordToggleIcon");
    console.log("togglePasswordVisibility called");
    console.log("passwordInput:", passwordInput);
    console.log("passwordToggleIcon:", passwordToggleIcon);
    if (!passwordInput) {
        console.error("Password input not found");
        return;
    }
    if (!passwordToggleIcon) {
        console.error("Password toggle icon not found");
        return;
    }
    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        passwordToggleIcon.classList.remove("fa-eye-slash");
        passwordToggleIcon.classList.add("fa-eye");
        console.log("Password shown");
    } else {
        passwordInput.type = "password";
        passwordToggleIcon.classList.remove("fa-eye");
        passwordToggleIcon.classList.add("fa-eye-slash");
        console.log("Password hidden");
    }
}

window.togglePasswordVisibility = togglePasswordVisibility;