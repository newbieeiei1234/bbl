from fastapi import APIRouter, Depends, HTTPException, status
from db.db_connection import get_db
from sqlalchemy.orm import Session
from db.models.users import Users
from api.auth.auth import get_current_user
from db.models.bookings import Bookings
from sqlalchemy import select
from pydantic import BaseModel, Field

router = APIRouter("/bookings")

@router.get("/all")
def getAllBooking(user: Users = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = None
    if not user.admin_status:
        stmt = select(Bookings).filter(Bookings.owner_id == user.id)
    else:
        stmt = select(Bookings)
    result = db.execute(stmt).all()
    return {"data": result}

class CreateNewBookingRequest(BaseModel):
    name: str = Field(min_length=1, max_length=20)
    detail: str = Field(min_length=1, max_length=100)
    start_time: str = Field(min_length=1, max_length=10)
    end_time: str = Field(min_length=1, max_length=10)

@router.post("/new")
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

    if req.name is not None:
        booking.name = req.name
    if req.detail is not None:
        booking.detail = req.detail
    if req.start_time is not None:
        booking.start_time = req.start_time
    if req.end_time is not None:
        booking.end_time = req.end_time

    db.commit()
    db.refresh(booking)
    return {"data": booking}