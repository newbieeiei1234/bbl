from fastapi import APIRouter, Depends, HTTPException, status
from db.db_connection import get_db
from sqlalchemy.orm import Session
from db.models.users import Users
from api.auth.auth import get_current_user
from db.models.bookings import Bookings
from sqlalchemy import select
from pydantic import BaseModel, Field

router = APIRouter(prefix="/bookings")

@router.get("")
def getMyBookings(user: Users = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = select(Bookings).filter(Bookings.owner_id == user.id)
    result = db.execute(stmt).scalars().all()
    return {"data": result}

@router.get("/all")
def getAllBooking(user: Users = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user.admin_status:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only.")
    result = db.execute(select(Bookings)).scalars().all()
    return {"data": result}

class CreateNewBookingRequest(BaseModel):
    name: str = Field(min_length=1, max_length=20)
    detail: str = Field(min_length=1, max_length=100)
    start_time: str = Field(min_length=1, max_length=10)
    end_time: str = Field(min_length=1, max_length=10)

@router.post("")
def createNewBooking(req: CreateNewBookingRequest, user: Users = Depends(get_current_user), db: Session = Depends(get_db)):
    booking = Bookings(
        name=req.name,
        detail=req.detail,
        start_time=req.start_time,
        end_time=req.end_time,
        owner_id=user.id
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return {"data": booking}

class EditBookingRequest(BaseModel):
    id: int
    name: str|None = Field(default=None, min_length=1, max_length=20)
    detail: str|None = Field(default=None, min_length=1, max_length=100)
    start_time: str|None = Field(default=None, min_length=1, max_length=10)
    end_time: str|None = Field(default=None, min_length=1, max_length=10)

@router.put("")
def editBooking(req: EditBookingRequest, user: Users = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = select(Bookings).filter(Bookings.id == req.id)
    booking = db.execute(stmt).scalar_one_or_none()
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    if booking.owner_id != user.id and not user.admin_status:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to edit this booking")

    for field, value in req.model_dump(exclude={"id"}, exclude_none=True).items():
        setattr(booking, field, value)

    db.commit()
    db.refresh(booking)
    return {"data": booking}
