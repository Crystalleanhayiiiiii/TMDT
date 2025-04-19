
window.addEventListener("DOMContentLoaded", () => {
    console.log("📦 DOM đã load xong. Bắt đầu kiểm tra username...");
    const savedUsername = localStorage.getItem("username");

    if (savedUsername) {
        document.getElementById("username_new").value = savedUsername;
    }
    document.getElementById("change-account-form").addEventListener("submit", async function (e) {
        e.preventDefault();

        const username = document.getElementById("username_new").value.trim();
        const newPassword = document.getElementById("new-password").value;
        const confirmPassword = document.getElementById("confirm-password").value;
        const resultMsg = document.getElementById("result-message");

        if (newPassword !== confirmPassword) {
            resultMsg.innerText = "⚠️ Mật khẩu không khớp!";
            resultMsg.style.color = "#d9534f"; // đỏ
            return;
        }

        const token = localStorage.getItem("token");
        console.log("🔑 Token hiện tại:", token)

        try {
            const response = await fetch("http://127.0.0.1:7777/change_account", {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + token
                },
                body: JSON.stringify({
                    username: username,
                    password: newPassword
                })
            });

            const result = await response.json();

            if (response.ok) {
                resultMsg.innerText = "✅ Đã cập nhật tài khoản mật khẩu!, Vui lòng đăng nhập lại";
                resultMsg.style.color = "green";

                // Chuyển về index.html sau 2 giây
                setTimeout(() => {
                    localStorage.clear();
                    location.reload();
                    window.location.href = "/index.html";
                }, 2000);
            } else {
                resultMsg.innerText = "❌ " + result.msg;
                resultMsg.style.color = "#d9534f"; // đỏ
            }

        } catch (error) {
            resultMsg.innerText = "❌ Lỗi gửi yêu cầu";
            resultMsg.style.color = "#d9534f";
            console.error(error);
        }
    });

    // Nút Hủy → quay lại index.html ngay
    document.getElementById("cancel-btn").addEventListener("click", function () {
        window.location.href = "/index.html";
    });
});
