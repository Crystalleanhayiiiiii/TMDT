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
            <h2>Gói đang sử dụng</h2>
            <ul>
                <li><strong>Mã Subscription:</strong> ${sub.ServiceName}</li>
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
