document.addEventListener("DOMContentLoaded", () => {
    // Gắn header
    document.getElementById("header").innerHTML = `
        <header class="main-header">
        <div class="logo">
            <img src="/src/assets/image/logo.jpg" alt="Logo" height="40" />
        </div>
        <nav class="nav-bar">
            <a href="/index.html">Trang chủ</a>
            <div class="dropdown">
            <a href="#" class="dropbtn">Gói cước ▾</a>
            <div class="dropdown-content">
                <a href="/public/packages.html?category=1">Internet</a>
                <a href="/public/packages.html?category=2">Truyền hình</a>
                <a href="/public/packages.html?category=3">Combo</a>
            </div>
            </div>
            <a href="about.html">Giới thiệu</a>
            <a href="#">Liên hệ</a>
            <a href="#">Hỗ trợ</a>
            <a href="#">My Service</a>
            <button class="login-btn">Đăng nhập</button>
            <button class="resig-btn">Đăng kí</button>
        </nav>
        </header>
    `;

    // Gắn footer
    document.getElementById("footer").innerHTML = `
      <footer class="main-footer">
        <p>&copy; 2025 Công ty XYZ. All rights reserved.</p>
      </footer>
    `;

    // ✅ Gắn modal đăng nhập vào cuối <body>
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
});
