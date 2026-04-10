document.addEventListener("DOMContentLoaded", () => {

    const otpBoxes = document.querySelectorAll(".otp-box");
    otpBoxes.forEach(box => { box.value = ""; });

    // Enforce input rules live
    const fullname = document.getElementById("fullname");
    const phone = document.getElementById("phone");
    const email = document.getElementById("email");
    const password = document.getElementById("password");
    const confirmPassword = document.getElementById("confirmPassword");

    enforceNameInput(fullname);
    enforcePhoneInput(phone);

    // Live validation on blur
    fullname.addEventListener('blur', () => validateName(fullname));
    phone.addEventListener('blur', () => validatePhone(phone));
    email.addEventListener('blur', () => validateEmail(email));
    password.addEventListener('blur', () => validatePassword(password));
    confirmPassword.addEventListener('blur', () => {
        if (confirmPassword.value !== password.value) {
            showError(confirmPassword, 'Passwords do not match');
        } else {
            clearError(confirmPassword);
        }
    });

    // ===== SEND OTP =====
    document.getElementById("sendOtpBtn").addEventListener("click", function () {
        if (!validateEmail(email)) { email.focus(); return; }

        fetch("/send-otp/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            },
            body: JSON.stringify({ email: email.value })
        })
        .then(res => res.json())
        .then(data => {
            const msg = document.getElementById("otpMessage");
            msg.style.display = "block";
            msg.textContent = data.message;
            msg.style.color = data.success ? "green" : "red";
            if (data.success) otpBoxes[0].focus();
        });
    });

    // ===== OTP AUTO-MOVE =====
    otpBoxes.forEach((box, index) => {
        box.addEventListener("input", (e) => {
            e.target.value = e.target.value.replace(/[^0-9]/g, "");
            if (e.target.value && index < otpBoxes.length - 1) otpBoxes[index + 1].focus();
        });
        box.addEventListener("keydown", (e) => {
            if (e.key === "Backspace" && index > 0 && !box.value) otpBoxes[index - 1].focus();
        });
    });

    // ===== FORM SUBMIT VALIDATION =====
    document.getElementById("signupForm").addEventListener("submit", function (e) {
        let valid = true;
        if (!validateName(fullname)) valid = false;
        if (!validateEmail(email)) valid = false;
        if (!validatePhone(phone)) valid = false;
        if (!validatePassword(password)) valid = false;

        if (confirmPassword.value !== password.value) {
            showError(confirmPassword, 'Passwords do not match');
            valid = false;
        } else {
            clearError(confirmPassword);
        }

        const otpFilled = [...otpBoxes].every(b => b.value.trim() !== '');
        if (!otpFilled) {
            alert('Please enter the OTP sent to your email');
            valid = false;
        }

        if (!valid) e.preventDefault();
    });
});
