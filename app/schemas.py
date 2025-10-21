from pydantic import BaseModel
from typing import Optional, List

# User Schemas
class UserCreate(BaseModel):
    phone_number: str
    password: str
    full_name: str
    role: str

class User(BaseModel):
    id: int
    phone_number: str
    full_name: str
    role: str
    status: str
    class Config:
        orm_mode = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    phone_number: Optional[str] = None

# Credit Card Schemas
class CreditCardCreate(BaseModel):
    card_number_suffix: str
    bank_name: str

class CreditCard(BaseModel):
    id: int
    card_number_suffix: str
    bank_name: str
    class Config:
        orm_mode = True

# Bill Schemas
class BillImport(BaseModel):
    customer_code: str
    total_amount: float

class Bill(BaseModel):
    id: int
    customer_code: str
    total_amount: float
    status: str
    importer_id: int
    buyer_id: Optional[int] = None
    class Config:
        orm_mode = True

# Transaction Schemas
class TransactionCreate(BaseModel):
    amount: float
    type: str

class Transaction(BaseModel):
    id: int
    user_id: int
    amount: float
    type: str
    status: str
    class Config:
        orm_mode = True
