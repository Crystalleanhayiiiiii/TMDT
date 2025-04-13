from sqlalchemy import Column, Enum, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, Text, SmallInteger, DECIMAL, CHAR, DateTime, VARCHAR, Boolean

# Định nghĩa lớp cơ sở
Base = declarative_base()

# Model Role
class Role(Base):
    __tablename__ = 'Role'

    RoleID = Column(Integer, primary_key=True, autoincrement=True)
    RoleName = Column(String(100), nullable=False, unique=True)

    # Mối quan hệ với bảng Account
    accounts = relationship("Account", back_populates="role")

    def __repr__(self):
        return f'<Role {self.RoleName}>'

# Model Account
class Account(Base):
    __tablename__ = 'Account'

    AccountID = Column(Integer, primary_key=True, autoincrement=True)
    username = Column('username',String(50), nullable=False, unique=True) 
    password = Column(String(20), nullable=False)
    RoleID = Column(Integer, ForeignKey('Role.RoleID'), nullable=False)

    # Mối quan hệ với bảng Role
    role = relationship("Role", back_populates="accounts")

    def __repr__(self):
        return f'<Account {self.AccountID}, RoleID {self.RoleID}>'
# Model Service
class Service(Base):
    __tablename__ = 'Service'

    ServiceID = Column(Integer, primary_key=True, autoincrement=True)
    CategoryID = Column(Integer, ForeignKey('Category.CategoryID'), nullable=False)
    ManagementID = Column(Integer, ForeignKey('Management.ManagementID'), nullable=True)
    Name = Column(VARCHAR(255), nullable=True)
    Speed = Column(VARCHAR(50), nullable=True)
    Channels = Column(Integer, nullable=True)
    Area = Column(VARCHAR(255), nullable=True)
    Features = Column(Text, nullable=True)

    # Mối quan hệ với bảng Price
    prices = relationship("Price", back_populates="service")

# Model Price
class Price(Base):
    __tablename__ = 'Price'

    PriceID = Column(Integer, primary_key=True, autoincrement=True)
    ServiceID = Column(Integer, ForeignKey('Service.ServiceID'), nullable=False)
    ManagementID = Column(Integer, ForeignKey('Management.ManagementID'), nullable=True)
    Duration = Column(Integer, nullable=False)  # Giả định sẽ kiểm tra trong ứng dụng
    BonusMonths = Column(Integer, default=0, nullable=False)
    PriceAmount = Column(DECIMAL(10, 2), nullable=False)
    Currency = Column(VARCHAR(10), default='VND', nullable=True)
    Status = Column(Enum('active', 'inactive'), nullable=True)

    # Quan hệ ngược với Service
    service = relationship("Service", back_populates="prices")
