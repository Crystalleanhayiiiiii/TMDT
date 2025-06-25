# Hệ thống quản lý dịch vụ Internet và Truyền hình

Dự án này là hệ thống quản lý dịch vụ Internet và truyền hình với các chức năng như đăng ký, thanh toán, quản lý đơn hàng, hỗ trợ khách hàng và nhiều tính năng khác. Hệ thống được xây dựng với Flask (Python) cho backend và sử dụng cơ sở dữ liệu MySQL.

## Cấu trúc dự án

### Backend
- **Flask**
- **SQLAlchemy**
- **JWT Authentication**

### Frontend
- **HTML**
- **CSS**
- **JavaScript**
- **Fetch API**

## Các tính năng chính

### Giao diện khách hàng

1. **Đăng ký tài khoản:**
   - Tạo tài khoản cho khách hàng với thông tin: tên đăng nhập, mật khẩu, họ tên, số điện thoại, email, địa chỉ.
   - Xử lý đăng ký tài khoản qua API.

2. **Đăng nhập:**
   - Khách hàng có thể đăng nhập qua API với tên đăng nhập và mật khẩu.
   - API trả về token JWT để xác thực các yêu cầu tiếp theo.

3. **Đăng ký gói dịch vụ:**
   - **Bước 1:** Người dùng có thể chọn gói dịch vụ qua API.
   - Hệ thống tạo đơn hàng với trạng thái "pending" chờ thanh toán.
   
   - **Bước 2:** Sau khi kiểm tra đảm bảo đủ điều kiện cung cấp dịch vụ, nhân viên xác nhận đơn hàng và thay đổi trạng thái thành "approved."
   
   - **Bước 3:** **Thanh toán và tạo Subscription:**
     - Thanh toán qua các phương thức như thẻ ngân hàng, MoMo, v.v.
     - Khi thanh toán thành công, trạng thái đơn hàng thay đổi thành "success" và hệ thống tạo một subscription cho khách hàng để theo dõi thông tin gói dịch vụ, thời hạn, gia hạn hoặc hủy gói.

4. **Cập nhật thông tin cá nhân:**
   - Khách hàng có thể thay đổi mật khẩu và cập nhật thông tin cá nhân qua API, bao gồm tên, địa chỉ, số điện thoại, email.

5. **Hỗ trợ khách hàng:**
   - Khách hàng có thể tạo ticket hỗ trợ cho các vấn đề liên quan đến dịch vụ.

### Giao diện quản lý

1. **Quản lý dịch vụ:**
   - Thêm, sửa, xóa và hiển thị thông tin dịch vụ. Xem thông tin các gói dịch vụ đang sử dụng.

2. **Quản lý đơn hàng:**
   - Thêm, duyệt và hiển thị đơn hàng.

3. **Quản lý khách hàng:**
   - Xem thông tin khách hàng và lịch sử đơn hàng của họ.

4. **Báo cáo:**
   - Tổng hợp thống kê doanh thu và đơn hàng theo tháng và trạng thái.

## Một số API chính

### 1. Đăng nhập

- **Endpoint:** `/login`
- **Method:** `POST`
- **Dữ liệu yêu cầu:**
  ```
  {
    "username": "your_username",
    "password": "your_password"
  }
```
Dữ liệu trả về:
 ```
{
  "msg": "Đăng nhập thành công",
  "token": "JWT_TOKEN",
  "userID": 1,
  "role": "customer",
  "username": "your_username"
}
 ```
2. Đặt gói dịch vụ
Endpoint: /order_service

Method: POST

Dữ liệu yêu cầu:

 ```
{
  "price_id": 1
}
 ```
Dữ liệu trả về:

 ```
{
  "msg": "Đơn hàng đã được tạo với trạng thái: pending",
  "OrderID": 1
}
 ```
3. Thanh toán và tạo Subscription
Endpoint: /pay_order

Method: POST

Dữ liệu yêu cầu:

 ```
{
  "order_id": 1,
  "method": "Thẻ Ngân Hàng",
  "accountNumber": "1234567890",
  "password": "bank_password",
  "bankName": "Vietcombank"
}
 ```
Dữ liệu trả về:

 ```
{
  "msg": "Thanh toán thành công, gia hạn Subscription",
  "SubscriptionID": 1,
  "NewEndDate": "2025-10-20",
  "ServiceName": "Fiber Super 100"
}
 ```
4. Cập nhật thông tin cá nhân
Endpoint: /edit_myinfo

Method: PUT

Dữ liệu yêu cầu:

 ```
{
  "firstName": "Nguyễn",
  "lastName": "Văn A",
  "phone": "0912345678",
  "email": "vana@gmail.com",
  "address": "123 Đường ABC, Quận 1, TP.HCM",
  "birthDate": "1998-05-12",
  "gender": "1"
}
 ```
Dữ liệu trả về:

 ```
{
  "msg": "Cập nhật thông tin thành công"
}
 ```
Một số hình ảnh minh họa 
