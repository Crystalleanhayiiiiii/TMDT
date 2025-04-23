document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("token");
    if (!token) {
        alert("Bạn chưa đăng nhập. Vui lòng đăng nhập lại.");
        window.location.href = "/index.html";
        return;
    }

    try {
        const res = await fetch("http://127.0.0.1:7777/myinfo/", {
            method: "GET",
            headers: {
                Authorization: `Bearer ${token}`
            }
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.msg || "Lỗi khi lấy thông tin");

        // Gán vào chế độ xem
        const fullName = `${data.FirstName || ""} ${data.LastName || ""}`;
        document.getElementById("fullname").textContent = fullName;
        document.getElementById("email").textContent = data.Email || "Chưa cập nhật";
        document.getElementById("phone").textContent = data.Phone || "Chưa cập nhật";
        document.getElementById("birthdate").textContent = data.BirthDate || "Chưa cập nhật";
        document.getElementById("gender").textContent = data.Gender || "Không rõ";
        document.getElementById("address").textContent = data.Address || "Chưa cập nhật";

        // Gán sẵn vào chế độ chỉnh sửa
        document.getElementById("input-fullname").value = fullName;
        document.getElementById("input-email").value = data.Email || "";
        document.getElementById("input-phone").value = data.Phone || "";
        document.getElementById("input-gender").value = data.Gender || "Nam";
        document.getElementById("input-dob").value = data.BirthDate || "";
        document.getElementById("input-address").value = data.Address || "";

    } catch (err) {
        console.error("❌ Lỗi khi tải thông tin:", err);
        alert("Không thể tải thông tin cá nhân. Vui lòng thử lại sau.");
    }
});

// 👉 Chuyển sang chế độ chỉnh sửa
document.getElementById("edit-profile-btn").addEventListener("click", () => {
    document.getElementById("profile-view").style.display = "none";
    document.getElementById("profile-edit").style.display = "block";
});

// 👉 Hủy chỉnh sửa
document.getElementById("cancel-profile-btn").addEventListener("click", () => {
    document.getElementById("profile-edit").style.display = "none";
    document.getElementById("profile-view").style.display = "block";
});

// 👉 Lưu thông tin mới
document.getElementById("save-profile-btn").addEventListener("click", async () => {
    const token = localStorage.getItem("token");
    const fullName = document.getElementById("input-fullname").value.trim();
    const nameParts = fullName.split(" ");
    const lastName = nameParts.pop();
    const firstName = nameParts.join(" ");

    const data = {
        firstName,
        lastName,
        phone: document.getElementById("input-phone").value.trim(),
        email: document.getElementById("input-email").value.trim(),
        address: document.getElementById("input-address").value.trim(),
        birthDate: document.getElementById("input-dob").value,
        gender: document.getElementById("input-gender").value === "Nam" ? 1 : 0
    };

    try {
        const res = await fetch("http://127.0.0.1:7777/edit_myinfo", {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });

        const result = await res.json();
        if (!res.ok) throw new Error(result.msg || "Lỗi cập nhật");

        alert("✅ Cập nhật thành công!");

        // Cập nhật giao diện hiển thị
        document.getElementById("fullname").textContent = fullName;
        document.getElementById("email").textContent = data.email;
        document.getElementById("phone").textContent = data.phone;
        document.getElementById("birthdate").textContent = data.birthDate;
        document.getElementById("gender").textContent = document.getElementById("input-gender").value;
        document.getElementById("address").textContent = data.address;

        // ✅ Cập nhật localStorage
        localStorage.setItem("fullName", fullName);
        localStorage.setItem("phone", data.phone);
        document.getElementById("profile-edit").style.display = "none";
        document.getElementById("profile-view").style.display = "block";

    } catch (err) {
        console.error("❌ Lỗi cập nhật:", err);
        alert("❌ Không thể cập nhật thông tin.");
    }
});