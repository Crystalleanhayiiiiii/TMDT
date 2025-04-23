
window.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("token");

    if (!token) {
        document.getElementById("mysub").innerText = "Bạn chưa đăng nhập.";
        return;
    }

    fetch("http://127.0.0.1:7777/my_subcriptions", {
        method: "GET",
        headers: {
            "Authorization": "Bearer " + token
        }
    })
        .then(response => response.json())
        .then(data => renderSubscriptions(data))
        .catch(error => {
            console.error("Lỗi khi tải dữ liệu:", error);
            document.getElementById("mysub").innerText = "Không thể tải dữ liệu.";
        });
});

function renderSubscriptions(subs) {
    const container = document.getElementById("mysub");
    container.innerHTML = "";

    if (subs.length === 0) {
        container.innerHTML = "<p>Bạn chưa đăng ký gói nào.</p>";
        return;
    }

    subs.forEach(sub => {
        const card = `
        <div class="package-card">
            <h2> ${sub.ServiceName}</h2>
            <ul>
                <li><strong>Bắt đầu:</strong> ${sub.StartDate}</li>
                <li><strong>Kết thúc:</strong> ${sub.EndDate}</li>
                <li><strong>Tốc độ:</strong> ${sub.SpeedLimit || "Không rõ"}</li>
                <li><strong>Trạng thái:</strong> ${sub.Status}</li>
            </ul>
            <a href="packages_detail.html?id=${sub.ServiceID}" class="btn-register">Đăng kí thêm</a>
            <a href="packages_detail.html?id=${sub.ServiceID}" class="btn-register_white">Xem chi tiết</a>
            <a href="packages_detail.html?id=${sub.ServiceID}" class="btn-register_white">Hủy gói cước</a>
        </div>
        `;
        container.insertAdjacentHTML("beforeend", card);
    });
}



document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("token");
    if (!token) {
        alert("Vui lòng đăng nhập để xem đơn hàng.");
        return;
    }

    try {
        const res = await fetch("http://127.0.0.1:7777/my_orders", {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });

        const orders = await res.json();

        if (!res.ok) {
            throw new Error(orders.msg || "Lỗi khi tải đơn hàng");
        }

        const container = document.getElementById("order-list");
        container.innerHTML = "";

        if (orders.length === 0) {
            container.innerHTML = "<p class='text-center text-muted'>Bạn chưa có đơn hàng nào.</p>";
            return;
        }

        orders.forEach(order => {
            const badgeClass = getStatusBadgeClass(order.Status);
            const bonusText = order.BonusMonths > 0 ? `<span class="text-success">(Tặng ${order.BonusMonths} tháng)</span>` : "";

            // Tùy theo loại gói, hiển thị khác nhau
            let typeContent = "";
            if (order.Type === "Internet") {
                typeContent = `<li><i class="bi bi-download"></i> Tốc độ: <strong>${order.Speed}</strong></li>`;
            } else if (order.Type === "Truyền hình") {
                typeContent = `<li><i class="bi bi-tv"></i> Số kênh: <strong>${order.Channels} kênh</strong></li>`;
            } else if (order.Type === "Combo") {
                typeContent = `
                <li><i class="bi bi-download"></i> Tốc độ: <strong>${order.Speed}</strong></li>
                <li><i class="bi bi-tv"></i> Số kênh: <strong>${order.Channels} kênh</strong></li>`;
            }

            const card = `
              <div class="col">
                <div class="card h-100 shadow-sm border-0">
                  <div class="card-body d-flex flex-column justify-content-between">
                    <!-- Header -->
                    <div class="d-flex justify-content-between align-items-start mb-3">
                      <div>
                        <h5 class="card-title mb-1 text-primary">${order.ServiceName}</h5>
                        <p class="mb-1 text-muted" style="font-size: 14px;">
                          Đơn hàng #${order.OrderID} • Đặt ngày ${order.OrderDate}
                        </p>
                      </div>
                      <span class="badge rounded-pill ${badgeClass} mt-1">${getStatusText(order.Status)}</span>
                    </div>
            
                    <!-- Nội dung gói -->
                    <ul class="list-unstyled mb-3" style="font-size: 15px;">
                      <li><i class="bi bi-clock"></i> Thời lượng: <strong>${order.Duration} tháng</strong> ${bonusText}</li>
                      <li><i class="bi bi-geo-alt"></i> Khu vực: <strong>${order.Area}</strong></li>
                      <li><i class="bi bi-cash-coin"></i> Tổng cộng: <strong>${formatCurrency(order.PriceAmount, order.Currency)}</strong></li>
                      ${typeContent}
                    </ul>
            
                    <!-- Nút hành động -->
                    <div class="d-flex justify-content-end flex-wrap gap-2">
                      <a href="packages_detail.html?id=${order.ServiceID}"class="btn btn-sm btn-outline-primary">Xem chi tiết</a>
                    <!-- gửi data vào nút thanh toán -->  
                    <button 
                    class="btn btn-sm btn-success btn-pay"
                    data-bs-toggle="modal" 
                    data-bs-target="#paymentModal"
                    data-order-id="${order.OrderID}"
                    data-service-name="${order.ServiceName}"
                    data-duration="${order.Duration}"
                    data-bonus="${order.BonusMonths}"
                    data-price="${order.PriceAmount}"
                    data-currency="${order.Currency}"
                    data-area="${order.Area}"
                    data-status="${order.Status}"
                    >
                    Thanh toán
                    </button>

                    <button class="btn btn-sm btn-outline-danger cancel-order-btn" data-order-id="${order.OrderID}">Hủy đơn hàng</button>

                    </div>
                  </div>
                </div>
              </div>
            `;

            container.insertAdjacentHTML("beforeend", card);
        });

    } catch (err) {
        console.error("❌ Lỗi khi tải đơn hàng:", err);
        alert("Không thể tải đơn hàng. Vui lòng thử lại sau.");
    }
});
// xử lý hiện modal thanh toán 
const methodSelect = document.getElementById("payment-method");
const walletFields = document.getElementById("e-wallet-fields");
const bankFields = document.getElementById("bank-fields");
const msgBox = document.getElementById("payment-msg");

methodSelect.addEventListener("change", () => {
    walletFields.classList.add("d-none");
    bankFields.classList.add("d-none");

    if (methodSelect.value === "Ví điện tử") {
        walletFields.classList.remove("d-none");
    } else if (methodSelect.value === "Thẻ ngân hàng") {
        bankFields.classList.remove("d-none");
    }
});
document.addEventListener("DOMContentLoaded", () => {
    const paymentModal = document.getElementById("paymentModal");

    paymentModal.addEventListener("show.bs.modal", (event) => {
        const button = event.relatedTarget;
        const orderId = button.getAttribute("data-order-id");
        const serviceName = button.getAttribute("data-service-name");
        const duration = button.getAttribute("data-duration");
        const bonus = button.getAttribute("data-bonus");
        const price = button.getAttribute("data-price");
        const currency = button.getAttribute("data-currency");
        const area = button.getAttribute("data-area");
        // nếu pending , success không hiển thị modal thanh toán 
        const status = button.getAttribute("data-status");
        if (status === "pending") {
            alert("❗ Đơn hàng phải được duyệt trước khi thanh toán.");
            event.preventDefault(); // ❌ Ngăn modal hiển thị
            return;
        }
        if (status === "canceled") {
            alert("❌ Đơn hàng này đã được hủy,tạo order mới");
            event.preventDefault(); // ❌ Ngăn modal hiển thị
            return;
        }
        if (status === "success") {
            alert("✅ Đơn hàng này đã được thanh toán.");
            event.preventDefault(); // ❌ Ngăn modal hiển thị
            return;
        }

        // Gán giá trị vào modal
        document.getElementById("order-id").value = orderId;
        document.getElementById("payment-service-name").innerText = serviceName;
        document.getElementById("payment-duration").innerText = `${duration} tháng`;
        document.getElementById("payment-bonus").innerText = bonus > 0 ? `(Tặng ${bonus} tháng)` : "";
        document.getElementById("payment-price").innerText = formatCurrency(price, currency);
        document.getElementById("payment-area").innerText = area;
        // Reset form thanh toán
        document.getElementById("payment-method").value = "";
        document.getElementById("e-wallet-fields").classList.add("d-none");
        document.getElementById("bank-fields").classList.add("d-none");
        document.getElementById("payment-msg").classList.add("d-none");
        document.getElementById("payment-msg").innerText = "";
    });

});
document.getElementById("payment-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const token = localStorage.getItem("token"); // ✅ Lấy JWT
    if (!token) {
        alert("Vui lòng đăng nhập trước khi thanh toán.");
        return;
    }

    const orderId = document.getElementById("order-id").value;
    const method = document.getElementById("payment-method").value;

    let accountNumber = "";
    let password = "";
    let bankName = null;

    if (method === "Ví điện tử") {
        accountNumber = document.getElementById("wallet-phone").value.trim();
        password = document.getElementById("wallet-password").value.trim();
    } else if (method === "Thẻ ngân hàng") {
        bankName = document.getElementById("bank-name").value.trim();
        accountNumber = document.getElementById("bank-account").value.trim();
        password = document.getElementById("bank-password").value.trim();
    } else if (method === "Tiền mặt") {
        accountNumber = "cash"; // ví dụ placeholder
        password = "cash";
    }

    // Validate cơ bản
    if (!orderId || !method || !accountNumber || !password) {
        alert("Vui lòng điền đầy đủ thông tin thanh toán.");
        return;
    }

    const payload = {
        order_id: orderId,
        method: method,
        accountNumber: accountNumber,
        password: password,
        bankName: bankName // null nếu không cần
    };

    const msgBox = document.getElementById("payment-msg");
    msgBox.classList.remove("alert-success", "alert-danger", "d-none");

    try {
        const res = await fetch("http://127.0.0.1:7777/pay_order", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (res.ok) {
            msgBox.classList.add("alert-success");
            msgBox.innerText = data.msg || "Thanh toán thành công!";

            setTimeout(() => {
                const modal = bootstrap.Modal.getInstance(document.getElementById("paymentModal"));
                modal.hide();
                location.reload(); // hoặc bạn chỉ reload danh sách đơn hàng
            }, 1500);
        } else {
            msgBox.classList.add("alert-danger");
            msgBox.innerText = data.msg || "Thanh toán thất bại.";
        }
    } catch (error) {
        msgBox.classList.add("alert-danger");
        msgBox.innerText = "Lỗi kết nối máy chủ. Vui lòng thử lại.";
        console.error("❌ Payment error:", error);
    }
});
// NÚT HỦY
//Modal chọn lý do hủy 
let selectedOrderId = null;

document.addEventListener("click", (e) => {
    if (e.target.classList.contains("cancel-order-btn")) {
        selectedOrderId = e.target.getAttribute("data-order-id");
        document.getElementById("cancel-order-id").textContent = `#${selectedOrderId}`;
        const modal = new bootstrap.Modal(document.getElementById("cancelModal"));
        modal.show();
    }
});

// Bấm nút xác nhận trong modal
document.getElementById("confirm-cancel-btn").addEventListener("click", async () => {
    const token = localStorage.getItem("token");
    const reason = document.getElementById("cancel-reason").value;

    if (!reason) {
        alert("Vui lòng chọn lý do hủy!");
        return;
    }

    try {
        const res = await fetch("http://127.0.0.1:7777/cancel_order", {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + token
            },
            body: JSON.stringify({
                order_id: selectedOrderId,
                reason: reason
            })
        });

        const result = await res.json();
        if (res.ok) {
            alert(result.msg);
            location.reload();
        } else {
            alert("❌ " + (result.msg || "Hủy đơn hàng thất bại"));
        }
    } catch (err) {
        console.error("Lỗi hủy:", err);
        alert("Không thể kết nối đến máy chủ.");
    }
});

function getStatusText(status) {
    const map = {
        pending: "Đang xử lý",
        approved: "Đã xác nhận",
        success: "Thành công",
        canceled: "Đã hủy"
    };
    return map[status] || "Không rõ";
}

function getStatusBadgeClass(status) {
    switch (status) {
        case "pending": return "bg-warning text-dark";
        case "approved": return "bg-info text-white";
        case "success": return "bg-primary";
        case "canceled": return "bg-danger";
        default: return "bg-secondary";
    }
}
function formatCurrency(amount, currency = 'VND') {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: currency
    }).format(amount);
}



