from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, models, schemas, security
from ..database import get_db

router = APIRouter(
    prefix="/api/bills",
    tags=["Hóa Đơn Điện"],
    dependencies=[Depends(security.get_current_user)],
)

@router.post("/import", response_model=schemas.Bill)
def import_new_bill(bill: schemas.BillImport, db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    if current_user.role not in ["agent", "admin"]:
        raise HTTPException(status_code=403, detail="Không có quyền thực hiện hành động này")
    return crud.import_bill(db=db, bill=bill, importer_id=current_user.id)

@router.get("/warehouse", response_model=List[schemas.Bill])
def read_bills_in_warehouse(db: Session = Depends(get_db)):
    return crud.get_bills_by_status(db, status="in_stock")

@router.put("/{bill_id}/export", response_model=schemas.Bill)
def export_bill_to_customer(bill_id: int, buyer_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_active_admin)):
    db_bill = crud.export_bill(db=db, bill_id=bill_id, buyer_id=buyer_id)
    if db_bill is None:
        raise HTTPException(status_code=404, detail="Hóa đơn không tồn tại hoặc đã được bán")
    return db_bill
