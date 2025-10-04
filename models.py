from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    ip_addresses = relationship("IPAddress", back_populates="user")

class IPAddress(Base):
    __tablename__ = 'ip_addresses'
    
    id = Column(Integer, primary_key=True)
    address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="ip_addresses")

class DataType(Base):
    __tablename__ = 'data_types'
    
    id = Column(Integer, primary_key=True)
    type_name = Column(String, unique=True, nullable=False)
    description = Column(String)