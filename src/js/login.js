document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("login-form");
  const message = document.getElementById("login-message");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    try {
      const response = await fetch("http://127.0.0.1:7777/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();

      if (response.ok) {
        // ✅ Đăng nhập thành công
        localStorage.setItem("token", data.token);
        localStorage.setItem("role", data.role);
        localStorage.setItem("userID", data.userID);
        localStorage.setItem("username", data.username);
        localStorage.setItem("fullName", data.FirstName + " " + data.LastName);
        localStorage.setItem("phone", data.Phone);
        message.style.color = "green";
        message.textContent = data.msg || "Đăng nhập thành công";

        // 👉 Chuyển hướng sau 1 giây (nếu cần)
        setTimeout(() => {
          window.location.href = "/index.html";
        }, 500);
      } else {
        // ❌ Đăng nhập sai
        message.style.color = "red";
        message.textContent = data.msg || "Đăng nhập thất bại!";
      }

    } catch (error) {
      console.error("Lỗi kết nối:", error);
      message.style.color = "red";
      message.textContent = "Không thể kết nối đến máy chủ.";
    }
  });
});
