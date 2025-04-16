from datetime import datetime
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
    username = Column('username', String(50), nullable=False, unique=True)
    password = Column(String(20), nullable=False)
    RoleID = Column(Integer, ForeignKey('Role.RoleID'), nullable=False)

    # Mối quan hệ với bảng Role
    role = relationship("Role", back_populates="accounts")

    # Quan hệ 1:1 với Customer và Employee
    customer = relationship(
        "Customer", back_populates="account", uselist=False)
    employee = relationship(
        "Employee", back_populates="account", uselist=False)

    def __repr__(self):
        return f'<Account {self.AccountID}, RoleID {self.RoleID}>'
# Model Customer


class Customer(Base):
    __tablename__ = 'Customer'

    CustomerID = Column(Integer, primary_key=True, autoincrement=True)
    FirstName = Column(String(50), nullable=False)
    LastName = Column(String(50), nullable=False)
    BirthDate = Column(Date)
    Gender = Column(Boolean, nullable=False, default=True)  # BIT → Boolean
    Address = Column(String(200))
    Phone = Column(String(11), nullable=False, unique=True)
    Email = Column(String(100))
    Status = Column(Boolean, nullable=False, default=True)
    AccountID = Column(Integer, ForeignKey('Account.AccountID'), unique=True)

  # Quan hệ với bảng account,order
    account = relationship("Account", back_populates="customer")
    orders = relationship("Order", back_populates="customer")

# Model Employee


class Employee(Base):
    __tablename__ = 'Employee'

    EmployeeID = Column(Integer, primary_key=True, autoincrement=True)
    FirstName = Column(String(50), nullable=False)
    LastName = Column(String(50), nullable=False)
    BirthDate = Column(Date)
    Gender = Column(Boolean, nullable=False, default=True)
    Address = Column(String(200))
    Phone = Column(String(11), nullable=False, unique=True)
    Email = Column(String(100))
    Status = Column(Boolean, nullable=False, default=True)
    AccountID = Column(Integer, ForeignKey('Account.AccountID'), unique=True)
    # Quan hệ với bảng account
    account = relationship("Account", back_populates="employee")
    orders = relationship("Order", back_populates="employee")


# Model Service
class Service(Base):
    __tablename__ = 'Service'

    ServiceID = Column(Integer, primary_key=True, autoincrement=True)
    CategoryID = Column(Integer, ForeignKey(
        'Category.CategoryID'), nullable=False)
    ManagementID = Column(Integer, ForeignKey(
        'Management.ManagementID'), nullable=True)
    Name = Column(VARCHAR(255), nullable=True)
    Speed = Column(VARCHAR(50), nullable=True)
    Channels = Column(Integer, nullable=True)
    Area = Column(VARCHAR(255), nullable=True)
    Features = Column(Text, nullable=True)

    # Mối quan hệ với bảng Price
    prices = relationship("Price", back_populates="service")
    # Mối quan hệ với bảng category
    category = relationship("Category", back_populates="services")

# Model Category


class Category(Base):
    __tablename__ = 'Category'

    CategoryID = Column(Integer, primary_key=True, autoincrement=True)
    CategoryName = Column(String(255), nullable=False)

    # Mối quan hệ với Service
    services = relationship("Service", back_populates="category")

# Model Price (nếu muốn)


class Price(Base):
    __tablename__ = 'Price'

    PriceID = Column(Integer, primary_key=True, autoincrement=True)
    ServiceID = Column(Integer, ForeignKey(
        'Service.ServiceID'), nullable=False)
    ManagementID = Column(Integer, ForeignKey(
        'Management.ManagementID'), nullable=True)
    # Giả định sẽ kiểm tra trong ứng dụng
    Duration = Column(Integer, nullable=False)
    BonusMonths = Column(Integer, default=0, nullable=False)
    PriceAmount = Column(DECIMAL(10, 2), nullable=False)
    Currency = Column(VARCHAR(10), default='VND', nullable=True)
    Status = Column(Enum('active', 'inactive'), nullable=True)

    # Quan hệ ngược với Service
    service = relationship("Service", back_populates="prices")
    orders = relationship("Order", back_populates="price")


# Model Order
class Order(Base):
    __tablename__ = 'Order'

    OrderID = Column(Integer, primary_key=True, autoincrement=True)
    CustomerID = Column(Integer, ForeignKey(
        'Customer.CustomerID'), nullable=False)
    EmployeeID = Column(Integer, ForeignKey(
        'Employee.EmployeeID'), nullable=True)
    PriceID = Column(Integer, ForeignKey('Price.PriceID'), nullable=False)
    OrderDate = Column(DateTime, default=datetime.utcnow)
    Status = Column(Enum('pending', 'approved', 'canceled'), default='pending')

    # Quan hệ ngược
    customer = relationship("Customer", back_populates="orders")
    employee = relationship("Employee", back_populates="orders")
    price = relationship("Price", back_populates="orders")
    subscription = relationship(
        "Subscription", back_populates="order", uselist=False)
#  Model Subcription


class Subscription(Base):
    __tablename__ = 'Subscription'

    SubscriptionID = Column(Integer, primary_key=True, autoincrement=True)
    OrderID = Column(Integer, ForeignKey('Order.OrderID'), nullable=False)
    StartDate = Column(Date, nullable=False)
    EndDate = Column(Date, nullable=False)
    SpeedLimit = Column(String(50))
    Status = Column(Enum('active', 'expired', 'suspended'), default='active')

    # Quan hệ ngược
    order = relationship("Order", back_populates="subscription")
