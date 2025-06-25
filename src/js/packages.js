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
// Bắt sự kiện nút Lọc
document.getElementById("filter-btn").addEventListener("click", async () => {
  const minPrice = parseInt(document.getElementById("min-price").value.replace(/\./g, ""), 10);
  const maxPrice = parseInt(document.getElementById("max-price").value.replace(/\./g, ""), 10);

  if (isNaN(minPrice) || isNaN(maxPrice)) {
    alert("Vui lòng nhập khoảng giá hợp lệ.");
    return;
  }

  try {
    const res = await fetch("http://127.0.0.1:7777/filterby_price", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        min_price: minPrice,
        max_price: maxPrice
      })
    });

    const data = await res.json();

    if (!res.ok) {
      alert(data.msg || "Không tìm thấy gói cước.");
      return;
    }

    // Gọi hàm renderPackages để hiển thị kết quả tìm kiếm
    renderPackages(data);
  } catch (err) {
    console.error("Lỗi khi lọc gói cước:", err);
    alert("Lỗi khi gọi API.");
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
    // Xử lý hiển thị chu kỳ nếu có Duration và BonusMonths
    let durationHTML = "";
    if (pkg.Duration && pkg.BonusMonths) {
      durationHTML = `<li><i class="bi bi-geo-alt"></i> Chu Kỳ: <strong>${pkg.Duration}</strong> tháng ${pkg.BonusMonths > 0 ? `(Tặng ${pkg.BonusMonths} tháng)` : ""}</li>`;
    }

    const card = `
      <div class="package-card">
        <h2>${pkg.Name}</h2>
        <p class="price">Giá: ${formatCurrency(pkg.PriceAmount || 0)}</p>
        <ul>
          ${featureHTML}
          <li><i class="bi bi-geo-alt"></i> Khu vực: ${pkg.Area || "Toàn quốc"}</li>
          ${durationHTML}  <!-- Hiển thị chu kỳ nếu có -->
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

