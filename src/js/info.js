//api get info
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

        if (!res.ok) {
            throw new Error(data.msg || "Lỗi khi lấy thông tin");
        }

        const fullName = `${data.FirstName || ""} ${data.LastName || ""}`;
        document.getElementById("fullname").textContent = fullName;
        document.getElementById("email").textContent = data.Email || "Chưa cập nhật";
        document.getElementById("phone").textContent = data.Phone || "Chưa cập nhật";
        document.getElementById("birthdate").textContent = data.BirthDate || "Chưa cập nhật";
        document.getElementById("gender").textContent = data.Gender || "Không rõ";
        document.getElementById("address").textContent = data.Address || "Chưa cập nhật";
    } catch (err) {
        console.error("❌ Lỗi khi tải thông tin:", err);
        alert("Không thể tải thông tin cá nhân. Vui lòng thử lại sau.");
    }
});

document.getElementById("edit-profile-btn").addEventListener("click", () => {
    document.getElementById("input-fullname").value = document.getElementById("fullname").textContent;
    document.getElementById("input-email").value = document.getElementById("email").textContent;
    document.getElementById("input-phone").value = document.getElementById("phone").textContent;
    document.getElementById("input-gender").value = document.getElementById("gender").textContent;
    document.getElementById("input-dob").value = document.getElementById("birthdate").textContent;
    document.getElementById("input-address").value = document.getElementById("address").textContent;

    document.getElementById("profile-view").style.display = "none";
    document.getElementById("profile-edit").style.display = "block";
});

