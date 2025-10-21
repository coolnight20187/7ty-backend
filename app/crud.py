from sqlalchemy.orm import Session
from . import models, schemas, security

# User CRUD
def get_user_by_phone(db: Session, phone_number: str):
    return db.query(models.User).filter(models.User.phone_number == phone_number).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        phone_number=user.phone_number,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users_by_status_and_role(db: Session, status: str, role: str):
    return db.query(models.User).filter(models.User.status == status, models.User.role == role).all()

def approve_user(db: Session, user_id: int, role: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None
    db_user.status = "active"
    
    if role == "agent":
        agent_profile = models.AgentProfile(user_id=user_id, agent_name=f"Đại lý {db_user.full_name}")
        db.add(agent_profile)
    elif role == "customer":
        customer_profile = models.CustomerProfile(user_id=user_id)
        db.add(customer_profile)
        
    db.commit()
    db.refresh(db_user)
    return db_user

# Card CRUD
def create_customer_card(db: Session, card: schemas.CreditCardCreate, customer_id: int):
    db_card = models.CreditCard(**card.dict(), customer_id=customer_id)
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card

def get_customer_cards(db: Session, customer_id: int):
    return db.query(models.CreditCard).filter(models.CreditCard.customer_id == customer_id).all()

# Bill CRUD
def import_bill(db: Session, bill: schemas.BillImport, importer_id: int):
    db_bill = models.ElectricityBill(**bill.dict(), importer_id=importer_id)
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    return db_bill

def get_bills_by_status(db: Session, status: str):
    return db.query(models.ElectricityBill).filter(models.ElectricityBill.status == status).all()

def export_bill(db: Session, bill_id: int, buyer_id: int):
    db_bill = db.query(models.ElectricityBill).filter(models.ElectricityBill.id == bill_id).first()
    if not db_bill or db_bill.status != 'in_stock':
        return None
    db_bill.status = 'sold'
    db_bill.buyer_id = buyer_id
    db.commit()
    db.refresh(db_bill)
    return db_bill

# Transaction CRUD
def create_transaction(db: Session, transaction: schemas.TransactionCreate, user_id: int):
    db_transaction = models.Transaction(**transaction.dict(), user_id=user_id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transactions_by_status(db: Session, status: str):
    return db.query(models.Transaction).filter(models.Transaction.status == status).all()

def process_transaction(db: Session, transaction_id: int, new_status: str):
    db_transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not db_transaction or db_transaction.status != 'pending':
        return None

    db_transaction.status = new_status
    if new_status == 'approved':
        user_profile = None
        if db_transaction.type == 'agent_deposit':
            user_profile = db.query(models.AgentProfile).filter(models.AgentProfile.user_id == db_transaction.user_id).first()
        elif db_transaction.type == 'customer_withdraw':
             user_profile = db.query(models.CustomerProfile).filter(models.CustomerProfile.user_id == db_transaction.user_id).first()
        
        if user_profile:
            if db_transaction.type == 'agent_deposit':
                user_profile.wallet_balance += db_transaction.amount
            elif db_transaction.type == 'customer_withdraw':
                if user_profile.wallet_balance >= db_transaction.amount:
                    user_profile.wallet_balance -= db_transaction.amount
                else: # Rollback
                    db.rollback()
                    return "insufficient_funds"

    db.commit()
    db.refresh(db_transaction)
    return db_transaction
