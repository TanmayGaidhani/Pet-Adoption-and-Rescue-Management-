document.addEventListener("DOMContentLoaded", () => {

    // ===== PREVENT AUTOFILL & CLEAR OTP FIELDS =====
    const otpBoxes = document.querySelectorAll(".otp-box");
    
    // Clear OTP fields on page load
    otpBoxes.forEach(box => {
        box.value = "";
    });

    // Prevent autofill on all form fields
    const allInputs = document.querySelectorAll("input");
    allInputs.forEach(input => {
        input.setAttribute("readonly", "readonly");
        setTimeout(() => {
            input.removeAttribute("readonly");
        }, 500);
    });

    // ===== SEND OTP BUTTON =====
    const sendOtpBtn = document.getElementById("sendOtpBtn");
    sendOtpBtn.addEventListener("click", function () {
        const email = document.getElementById("email").value;

        if (!email) {
            alert("Please enter your email first!");
            return;
        }

        fetch("/send-otp/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            },
            body: JSON.stringify({ email: email })
        })
        .then(res => res.json())
        .then(data => {
            const msg = document.getElementById("otpMessage");
            msg.style.display = "block";
            msg.textContent = data.message;

            if (data.success) {
                msg.style.color = "green";
                document.querySelector(".otp-box").focus(); // Focus on first input
            } else {
                msg.style.color = "red";
            }
        });
    });

    // ===== OTP AUTO-MOVE BETWEEN BOXES =====

    otpBoxes.forEach((box, index) => {

        box.addEventListener("input", (e) => {
            e.target.value = e.target.value.replace(/[^0-9]/g, "");

            if (e.target.value && index < otpBoxes.length - 1) {
                otpBoxes[index + 1].focus();
            }
        });

        box.addEventListener("keydown", (e) => {
            if (e.key === "Backspace" && index > 0 && !box.value) {
                otpBoxes[index - 1].focus();
            }
        });
    });

});
