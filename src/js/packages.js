window.addEventListener("DOMContentLoaded", () => {
  const categoryId = new URLSearchParams(window.location.search).get("category");

  if (!categoryId) {
    document.getElementById("internet-packages").innerText = "Không xác định danh mục.";
    return;
  }

  fetch(`http://127.0.0.1:7777/service/${categoryId}`)
    .then(response => response.json())
    .then(data => renderPackages(data))
    .catch(error => {
      console.error("Lỗi khi tải dữ liệu:", error);
      document.getElementById("internet-packages").innerText = "Không thể tải dữ liệu.";
    });
});

function renderPackages(packages) {
  const container = document.getElementById("internet-packages");
  container.innerHTML = "";

  packages.forEach(pkg => {
    const card = `
      <div class="package-card">
        <h2>${pkg.Name}</h2>
        <p class="price">Giá: ${formatCurrency(pkg.PriceAmount)}</p>
        <ul>
          <li>Tốc độ: ${pkg.Speed || "Đang cập nhật"}</li>
          <li>Khu vực: ${pkg.Area || "Toàn quốc"}</li>
          <li>Tặng 1 tháng khi đóng cước trước 12 tháng.</li>
        </ul>
        <a href="packages_detail.html?id=${pkg.ServiceID}" class="btn-register">Đăng kí ngay</a>
        <a href="packages_detail.html?id=${pkg.ServiceID}" class="btn-register_white">Xem chi tiết</a>
      </div>
    `;
    container.insertAdjacentHTML("beforeend", card);
  });
}

function formatCurrency(amount) {
  const number = parseFloat(amount);
  return number.toLocaleString("vi-VN", {
    style: "currency",
    currency: "VND"
  });
}

