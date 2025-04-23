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

// Tìm Kiếm 
document.getElementById("search-btn").addEventListener("click", async () => {
  const keyword = document.getElementById("search-name").value.trim();

  if (!keyword) {
    alert("Vui lòng nhập từ khóa tìm kiếm.");
    return;
  }

  try {
    const res = await fetch(`http://127.0.0.1:7777/search_service?keyword=${encodeURIComponent(keyword)}`);
    const data = await res.json();

    const container = document.getElementById("internet-packages");

    if (!res.ok) {
      container.innerHTML = `<p class="text-danger">${data.msg}</p>`;
      return;
    }

    renderPackages(data); // dùng lại hàm hiển thị card
  } catch (err) {
    console.error("Lỗi khi tìm kiếm:", err);
    document.getElementById("internet-packages").innerHTML = `<p class="text-danger">Không thể kết nối đến máy chủ.</p>`;
  }
});

// hàm render các gói package
function renderPackages(packages) {
  const container = document.getElementById("internet-packages");
  container.innerHTML = "";

  if (!packages || packages.length === 0) {
    container.innerHTML = "<p class='text-muted'>Không có gói nào phù hợp.</p>";
    return;
  }

  packages.forEach(pkg => {
    let featureHTML = "";

    // Xử lý tuỳ theo loại gói
    const category = pkg.CategoryName?.toLowerCase();
    if (category === "internet") {
      featureHTML = `<li><i class="bi bi-download"></i> Tốc độ: ${pkg.Speed || "Đang cập nhật"}</li>`;
    } else if (category === "truyền hình") {
      featureHTML = `<li><i class="bi bi-tv"></i> Số kênh: ${pkg.Channels || "Đang cập nhật"} kênh</li>`;
    } else if (category === "combo") {
      featureHTML = `
        <li><i class="bi bi-download"></i> Tốc độ: ${pkg.Speed || "Đang cập nhật"}</li>
        <li><i class="bi bi-tv"></i> Số kênh: ${pkg.Channels || "Đang cập nhật"} kênh</li>`;
    }

    const card = `
      <div class="package-card">
        <h2>${pkg.Name}</h2>
        <p class="price">Giá: ${formatCurrency(pkg.PriceAmount || 0)}</p>
        <ul>
          ${featureHTML}
          <li><i class="bi bi-geo-alt"></i> Khu vực: ${pkg.Area || "Toàn quốc"}</li>
          <li><i class="bi bi-gift"></i> Tặng 1 tháng khi đóng cước trước 12 tháng.</li>
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

