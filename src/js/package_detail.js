window.addEventListener("DOMContentLoaded", () => {
    // Lấy id từ URL
    const id = new URLSearchParams(window.location.search).get("id");

    if (!id) {
        document.getElementById("service-detail").innerText = "Không tìm thấy gói cần hiển thị.";
        return;
    }

    // Gọi API lấy thông tin gói
    fetch(`http://127.0.0.1:7777/service_detail/${id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Không tìm thấy dịch vụ");
            }
            return response.json();
        })
        .then(data => {
            const html = `
          <h2>${data.ServiceName}</h2>
          <p><strong>Tốc độ:</strong> ${data.Speed}</p>
          <p><strong>Kênh:</strong> ${data.Channels}</p>
          <p><strong>Khu vực:</strong> ${data.Area}</p>
          <p><strong>Tính năng:</strong> ${data.Features}</p>
          <hr/>
          <h3>Giá:</h3>
        <ul>
        <li>
            <label>
            <input type="radio" name="duration" value="${data.PriceID_1_month}" checked>
            1 tháng: ${formatCurrency(data.Price_1_month)} (Tặng ${data.Bonus_1_month} tháng)
            </label>
        </li>
        <li>
            <label>
            <input type="radio" name="duration" value="${data.PriceID_6_months}">
            6 tháng: ${formatCurrency(data.Price_6_months)} (Tặng ${data.Bonus_6_months} tháng)
            </label>
        </li>
        <li>
            <label>
            <input type="radio" name="duration" value="${data.PriceID_12_months}">
            12 tháng: ${formatCurrency(data.Price_12_months)} (Tặng ${data.Bonus_12_months} tháng)
            </label>
        </li>
        </ul>

        <a href="#" class="btn-register" id="order-link">Đăng ký ngay</a>
  `;
            document.getElementById("service-detail").innerHTML = html;
            // ✅ GẮN SỰ KIỆN SAU KHI GIAO DIỆN ĐÃ CÓ NÚT
            // ✅ GỌI API khi xác nhận
            document.getElementById("order-link").addEventListener("click", async function (e) {
                e.preventDefault();

                const selected = document.querySelector('input[name="duration"]:checked');
                if (!selected) {
                    alert("Vui lòng chọn gói đăng ký.");
                    return;
                }

                const priceID = selected.value;

                const confirmed = confirm("Bạn có chắc chắn muốn đăng ký gói này?");
                if (!confirmed) return;

                const token = localStorage.getItem("token");

                try {
                    const response = await fetch("http://127.0.0.1:7777/order_service", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "Authorization": "Bearer " + token
                        },
                        body: JSON.stringify({
                            price_id: priceID
                        })
                    });

                    const result = await response.json();

                    if (response.ok) {
                        alert("✅ " + result.msg);
                        // 👉 Chuyển trang sau khi thành công 
                        window.location.href = "/public/packages.html?category=1";
                    } else {
                        alert("❌ " + "Bạn chưa đăng nhập , vui lòng đăng nhập !");
                        window.location.href = "/index.html";
                    }

                } catch (error) {
                    console.error("Lỗi khi gửi yêu cầu:", error);
                    alert("❌ Lỗi kết nối đến máy chủ.");
                }
            });

        })
        .catch(error => {
            console.error(error);
            document.getElementById("service-detail").innerText = "Lỗi khi tải chi tiết dịch vụ.";
        });
});



function formatCurrency(amount) {
    const number = parseFloat(amount);
    return number.toLocaleString("vi-VN", {
        style: "currency",
        currency: "VND"
    });
}