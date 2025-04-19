window.addEventListener("DOMContentLoaded", () => {
  includeComponent("header", "/src/layout/header.html", handleAuthDisplay);
  includeComponent("footer", "/src/layout/footer.html");
});

function includeComponent(id, filePath, callback) {
  fetch(filePath)
    .then(res => res.text())
    .then(html => {
      document.getElementById(id).innerHTML = html;
      if (typeof callback === "function") {
        callback();
      }
    })
    .catch(err => console.error(`Không thể load ${filePath}:`, err));
}

// Xử lý hiển thị người dùng sau khi header đã được chèn
function handleAuthDisplay() {

  const token = localStorage.getItem("token");
  const fullName = localStorage.getItem("fullName");
  console.log("🔐 Token:", token);

  const authSection = document.getElementById("auth-section");
  const userDropdown = document.getElementById("user-dropdown");

  if (token && fullName && authSection && userDropdown) {
    authSection.style.display = "none";
    userDropdown.style.display = "inline";

    document.getElementById("user-name").innerText = `Xin chào, ${fullName}`;
    document.getElementById("user-phone").innerText = localStorage.getItem("phone") || "";

    const logoutBtn = document.getElementById("logout-btn");
    logoutBtn?.addEventListener("click", () => {
      localStorage.clear();
      location.reload();
    });
  } else {
    console.warn("❌ Thiếu phần tử HTML hoặc chưa có token");
  }
}

// Gắn modal đăng nhập vào cuối <body>
document.body.insertAdjacentHTML("beforeend", `
  <div id="login-modal" class="modal-overlay" style="display: none;">
    <div class="modal-box">
      <span class="close-btn" id="close-login">&times;</span>
      <h2>Đăng nhập</h2>
      <form id="login-form">
        <input type="text" id="username" placeholder="Tên đăng nhập" required />
        <input type="password" id="password" placeholder="Mật khẩu" required />
        <button type="submit" id="btn-login">Đăng nhập</button>
        <p id="login-message" class="error-message"></p>
      </form>
    </div>
  </div>
`);
