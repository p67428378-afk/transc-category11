from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.kyc import KycCreate, Kyc
from app.services import kyc_service
from app.db.session import get_db

router = APIRouter()


@router.post("/kyc/submit", response_model=Kyc, status_code=status.HTTP_200_OK)
def submit_kyc(
    kyc_data: KycCreate,
    db: Session = Depends(get_db)
):
    try:
        db_kyc = kyc_service.create_kyc_record(db, kyc_data)
        return db_kyc
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
