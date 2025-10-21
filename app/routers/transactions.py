from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, models, schemas, security
from ..database import get_db

router = APIRouter(
    prefix="/api/transactions",
    tags=["Giao Dịch Người Dùng"],
    dependencies=[Depends(security.get_current_user)],
)

@router.post("/request", response_model=schemas.Transaction)
def request_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    # Validate transaction type based on user role
    if current_user.role == "agent" and transaction.type != "agent_deposit":
        raise HTTPException(status_code=400, detail="Đại lý chỉ có thể tạo yêu cầu nạp tiền")
    if current_user.role == "customer" and transaction.type != "customer_withdraw":
        raise HTTPException(status_code=400, detail="Khách thẻ chỉ có thể tạo yêu cầu rút tiền")

    return crud.create_transaction(db=db, transaction=transaction, user_id=current_user.id)
