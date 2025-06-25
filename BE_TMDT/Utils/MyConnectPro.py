from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

class MyConnectPro:
    def __init__(self, user, password, database, host, port):
        self.host = host
        self.username = user
        self.password = password
        self.database = database
        self.port = port
        self.engine = None
        self.Session = None
        self.connection = None  # Kết nối duy trì
        self.connect()  # Kết nối ngay khi khởi tạo đối tượng

    def connect(self):
        if self.engine is None:
            try:
                connection_url = f"mysql+mysqlconnector://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

                self.engine = create_engine(
                    connection_url,
                    pool_pre_ping=True,   # Kiểm tra trước khi dùng connection
                    pool_recycle=3600,    # Tránh timeout kết nối
                    pool_size=10,         # Tối ưu pool
                    max_overflow=20,
                    echo=True
                )
                
                self.Session = sessionmaker(bind=self.engine)
                
                # Tạo kết nối duy trì
                self.connection = self.engine.connect()
                print("✅ Kết nối MySQL thành công!")

            except SQLAlchemyError as e:
                print("❌ Kết nối MySQL thất bại:", str(e))

    def get_session(self):
        if not self.engine or not self.Session:
            self.connect()  # Đảm bảo kết nối đã được thiết lập
        return self.Session()

    def execute_query(self, query):
        if not self.engine or not self.Session:
            self.connect()  # Đảm bảo kết nối đã được thiết lập
        session = self.get_session()  # Lấy session từ sessionmaker
        try:
            result = session.execute(text(query))
            return result.fetchall()
        except SQLAlchemyError as e:
            print(f"❌ Lỗi khi thực thi truy vấn: {str(e)}")
            return None
        finally:
            session.close()  # Đảm bảo đóng session sau khi hoàn thành

    def close_connection(self):
        if self.connection:
            self.connection.close()  # Đóng kết nối duy trì khi không cần sử dụng nữa
            print("✅ Đóng kết nối thành công!")

# Ví dụ sử dụng
if __name__ == "__main__":
    db_connection = MyConnectPro(user="root", password="password", database="test_db", host="localhost", port=3306)
    query = "SELECT * FROM your_table"
    result = db_connection.execute_query(query)
    if result:
        print(result)
    db_connection.close_connection()  # Đóng kết nối khi không cần sử dụng
