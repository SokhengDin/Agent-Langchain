from enum import Enum


class RoomType(str, Enum):

    SINGLE_ROOM     = "SINGLE_ROOM"
    DOUBLE_ROOM     = "DOUBLE_ROOM"
    TWIN_ROOM       = "TWIN_ROOM"
    FAMILY_ROOM     = "FAMILY_ROOM"
    SUITE_ROOM      = "SUITE_ROOM"


class BookingStatus(str, Enum):
    PENDING         = "PENDING"
    CONFIRMED       = "CONFIRMED"
    CHECKED_IN      = "CHECKED_IN"
    CHECKED_OUT     = "CHECKED_OUT"
    CANCELLED       = "CANCELLED"


class PaymentStatus(str, Enum):
    PENDING         = "PENDING"
    COMPLETED       = "COMPLETED"
    FAILED          = "FAILED"
    REFUNDED        = "REFUNDED"