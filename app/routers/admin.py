from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, models, schemas, security
from ..database import get_db

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin Panel"],
    dependencies=[Depends(security.get_current_active_admin)],
)

@router.post("/staff", response_model=schemas.User)
def create_staff(user: schemas.UserCreate, db: Session = Depends(get_db)):
    user.role = "staff"
    return crud.create_user(db=db, user=user)

@router.get("/pending/agents", response_model=List[schemas.User])
def read_pending_agents(db: Session = Depends(get_db)):
    return crud.get_users_by_status_and_role(db, status="pending_approval", role="agent")

@router.put("/approve/agent/{user_id}", response_model=schemas.User)
def approve_agent(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.approve_user(db, user_id=user_id, role="agent")
    if db_user is None:
        raise HTTPException(status_code=404, detail="Đại lý không tồn tại")
    return db_user

@router.get("/pending/customers", response_model=List[schemas.User])
def read_pending_customers(db: Session = Depends(get_db)):
    return crud.get_users_by_status_and_role(db, status="pending_approval", role="customer")

@router.put("/approve/customer/{user_id}", response_model=schemas.User)
def approve_customer(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.approve_user(db, user_id=user_id, role="customer")
    if db_user is None:
        raise HTTPException(status_code=404, detail="Khách thẻ không tồn tại")
    return db_user

@router.post("/customers/{customer_id}/cards", response_model=schemas.CreditCard)
def create_card_for_customer(customer_id: int, card: schemas.CreditCardCreate, db: Session = Depends(get_db)):
    return crud.create_customer_card(db=db, card=card, customer_id=customer_id)

@router.get("/customers/{customer_id}/cards", response_model=List[schemas.CreditCard])
def read_customer_cards(customer_id: int, db: Session = Depends(get_db)):
    return crud.get_customer_cards(db=db, customer_id=customer_id)

@router.get("/pending/transactions", response_model=List[schemas.Transaction])
def read_pending_transactions(db: Session = Depends(get_db)):
    return crud.get_transactions_by_status(db, status="pending")

@router.put("/transactions/{transaction_id}/approve", response_model=schemas.Transaction)
def approve_transaction(transaction_id: int, db: Session = Depends(get_db)):
    result = crud.process_transaction(db, transaction_id, "approved")
    if result is None:
        raise HTTPException(status_code=404, detail="Giao dịch không tồn tại hoặc đã được xử lý")
    if result == "insufficient_funds":
        raise HTTPException(status_code=400, detail="Số dư không đủ")
    return result

@router.put("/transactions/{transaction_id}/reject", response_model=schemas.Transaction)
def reject_transaction(transaction_id: int, db: Session = Depends(get_db)):
    result = crud.process_transaction(db, transaction_id, "rejected")
    if result is None:
        raise HTTPException(status_code=404, detail="Giao dịch không tồn tại hoặc đã được xử lý")
    return result
