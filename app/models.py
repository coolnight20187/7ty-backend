from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base

class UserRole(str, enum.Enum):
    admin = "admin"
    staff = "staff"
    agent = "agent"
    customer = "customer"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    
    agent_profile = relationship("AgentProfile", back_populates="user", uselist=False)
    customer_profile = relationship("CustomerProfile", back_populates="user", uselist=False)

class AgentProfile(Base):
    __tablename__ = "agent_profiles"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    agent_name = Column(String, nullable=False)
    wallet_balance = Column(Float, default=0.0)
    user = relationship("User", back_populates="agent_profile")

class CustomerProfile(Base):
    __tablename__ = "customer_profiles"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    wallet_balance = Column(Float, default=0.0)
    user = relationship("User", back_populates="customer_profile")