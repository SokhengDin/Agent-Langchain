from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


from app.database.models.booking_model import BookingModel
from app.database.models.guest_model import GuestModel
from app.database.models.hotel_model import HotelModel
from app.database.models.payment_model import PaymentModel
from app.database.models.review_model import ReviewModel
from app.database.models.room_model import RoomModel

from app.core.config import settings


DATABASE_URL    = f"postgresql://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

engine          = create_engine(
    DATABASE_URL,
    echo            = False, 
    pool_pre_ping   = True,
    pool_size       = 5,
    max_overflow    = 10,
    pool_timeout    = 30,
    connect_args    = {
        "connect_timeout": 10
    }
)

SessionLocal    = sessionmaker(
    autocommit  =   False
    , autoflush = False
    , bind      = engine
)

def get_db():
    db  = SessionLocal()
    try:
        yield db
    finally:
        db.close()
