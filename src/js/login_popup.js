const waitForLoginBtn = setInterval(() => {
  const loginBtn = document.querySelector(".login-btn");
  const modal = document.getElementById("login-modal");
  const closeBtn = document.getElementById("close-login");

  if (loginBtn && modal && closeBtn) {
    console.log("✅ Đã tìm thấy .login-btn");

    loginBtn.addEventListener("click", () => {
      console.log("✅ Click vào nút Đăng nhập");
      modal.style.display = "flex";
    });

    closeBtn.addEventListener("click", () => {
      modal.style.display = "none";
    });

    clearInterval(waitForLoginBtn); // Dừng đợi
  }
}, 100); // kiểm tra mỗi 100ms
