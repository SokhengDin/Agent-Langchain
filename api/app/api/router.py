from fastapi import APIRouter

from app.api.v1.handlers import (
    booking_handler
    , guest_handler
    , hotel_handler
    , payment_handler
    , review_handler
    , room_handler
    , invoice_handler
    , auth_handler
)

router  = APIRouter()

router.include_router(auth_handler.router       , prefix="/auth"            , tags=["Authentication"])
router.include_router(hotel_handler.router      , prefix="/hotel"           , tags=["Hotel Handlers"])
router.include_router(guest_handler.router      , prefix="/guest"           , tags=["Guest Handlers"])

router.include_router(invoice_handler.router    , prefix="/invoice"         , tags=["INVOICE"])

router.include_router(room_handler.router       , prefix="/room"            , tags=["Room Handlers"])

router.include_router(booking_handler.router    , prefix="/booking"         , tags=["Booking Handlers"])
router.include_router(payment_handler.router    , prefix="/payment"         , tags=["Payment Handlers"])
router.include_router(review_handler.router     , prefix="/review"          , tags=["Review Handlers"])