# Hotel Agent API Documentation

## Base Configuration

- **Base URL**: `http://localhost:8000`
- **API Version**: `/api/v1`
- **Full Base URL**: `http://localhost:8000/api/v1`

## Main Application

The application is configured in [main.py](main.py) with the following features:
- FastAPI application with lifespan management
- Automatic database table creation on startup
- API router mounted at `/api/v1` prefix
- Development server runs on `0.0.0.0:8000` with hot reload

---

## API Endpoints

### 1. Hotel Handlers (`/api/v1/hotel`)

#### 1.1 Create Hotel
- **Endpoint**: `POST /api/v1/hotel/`
- **Status Code**: `201 Created`
- **Request Body**:
```json
{
  "name": "string (2-100 chars)",
  "address": "string (max 200 chars)",
  "city": "string (max 100 chars)",
  "postal_code": "string (max 20 chars, optional)",
  "phone_number": "string (max 20 chars, optional)",
  "email": "valid email (optional)",
  "total_rooms": "integer (> 0)",
  "star_rating": "decimal (optional)",
  "description": "string (optional)"
}
```
- **Response**:
```json
{
  "id": "uuid",
  "name": "string",
  "address": "string",
  "city": "string",
  "postal_code": "string or null",
  "phone_number": "string or null",
  "email": "string or null",
  "total_rooms": "integer",
  "star_rating": "decimal or null",
  "description": "string or null",
  "created_at": "datetime (ISO format)",
  "updated_at": "datetime or null",
  "deleted_at": "datetime or null",
  "is_active": "boolean"
}
```

#### 1.2 Search Hotels
- **Endpoint**: `GET /api/v1/hotel/search`
- **Query Parameters**:
  - `search_term` (optional): Search by name
  - `min_rating` (optional): Minimum star rating
  - `city` (optional): Filter by city
  - `skip` (default: 0): Pagination offset
  - `limit` (default: 100): Pagination limit
- **Response**: Array of HotelSchemaOut objects

#### 1.3 Get Hotel by ID
- **Endpoint**: `GET /api/v1/hotel/{hotel_id}`
- **Path Parameters**: `hotel_id` (UUID)
- **Response**: HotelSchemaOut object

#### 1.4 List All Hotels
- **Endpoint**: `GET /api/v1/hotel/`
- **Query Parameters**:
  - `skip` (default: 0)
  - `limit` (default: 100)
- **Response**: Array of HotelSchemaOut objects

#### 1.5 Update Hotel
- **Endpoint**: `PUT /api/v1/hotel/{hotel_id}`
- **Path Parameters**: `hotel_id` (UUID)
- **Request Body**: HotelSchemaIn (same as Create Hotel)
- **Response**: HotelSchemaOut object

#### 1.6 Delete Hotel
- **Endpoint**: `DELETE /api/v1/hotel/{hotel_id}`
- **Path Parameters**: `hotel_id` (UUID)
- **Status Code**: `204 No Content`

#### 1.7 Get Hotel Rooms
- **Endpoint**: `GET /api/v1/hotel/{hotel_id}/rooms`
- **Path Parameters**: `hotel_id` (UUID)
- **Query Parameters**:
  - `skip` (default: 0)
  - `limit` (default: 100)
- **Response**: Array of RoomSchemaOut objects

---

### 2. Guest Handlers (`/api/v1/guest`)

#### 2.1 Create Guest
- **Endpoint**: `POST /api/v1/guest`
- **Status Code**: `201 Created`
- **Request Body**:
```json
{
  "first_name": "string (2-50 chars)",
  "last_name": "string (2-50 chars)",
  "email": "valid email",
  "phone_number": "string (8-15 chars, digits/+/-)",
  "address": "string (max 200 chars, optional)",
  "nationality": "string (max 50 chars, optional)",
  "passport_number": "string (max 50 chars, optional)"
}
```
- **Response**:
```json
{
  "id": "uuid",
  "first_name": "string",
  "last_name": "string",
  "email": "email",
  "phone_number": "string",
  "address": "string or null",
  "nationality": "string or null",
  "passport_number": "string or null",
  "created_at": "datetime",
  "updated_at": "datetime or null",
  "deleted_at": "datetime or null",
  "is_active": "boolean"
}
```

#### 2.2 Search Guests
- **Endpoint**: `GET /api/v1/guest/search`
- **Query Parameters**:
  - `search_term` (required): Search by name/email
  - `skip` (default: 0)
  - `limit` (default: 100)
- **Response**: Array of GuestSchemaOut objects

#### 2.3 Get Guest by ID
- **Endpoint**: `GET /api/v1/guest/{guest_id}`
- **Path Parameters**: `guest_id` (UUID)
- **Response**: GuestSchemaOut object

#### 2.4 Get Guest by Email
- **Endpoint**: `GET /api/v1/guest/email/{email}`
- **Path Parameters**: `email` (string)
- **Response**: GuestSchemaOut object

#### 2.5 List All Guests
- **Endpoint**: `GET /api/v1/guest/`
- **Query Parameters**:
  - `skip` (default: 0)
  - `limit` (default: 100)
- **Response**: Array of GuestSchemaOut objects

#### 2.6 Update Guest
- **Endpoint**: `PUT /api/v1/guest/{guest_id}`
- **Path Parameters**: `guest_id` (UUID)
- **Request Body**: GuestSchemaIn (same as Create Guest)
- **Response**: GuestSchemaOut object

#### 2.7 Delete Guest
- **Endpoint**: `DELETE /api/v1/guest/{guest_id}`
- **Path Parameters**: `guest_id` (UUID)
- **Status Code**: `204 No Content`

---

### 3. Room Handlers (`/api/v1/room`)

#### 3.1 Create Room
- **Endpoint**: `POST /api/v1/room`
- **Status Code**: `201 Created`
- **Request Body**:
```json
{
  "hotel_id": "uuid",
  "room_number": "string (max 20 chars)",
  "room_type": "RoomType enum (SINGLE_ROOM, DOUBLE_ROOM, TWIN_ROOM, FAMILY_ROOM, SUITE_ROOM)",
  "floor": "integer (optional)",
  "status": "string (max 20 chars)",
  "price_per_night": "float",
  "additional_notes": "string (optional)"
}
```
- **Response**:
```json
{
  "id": "uuid",
  "hotel_id": "uuid",
  "room_number": "string",
  "room_type": "RoomType enum",
  "floor": "integer or null",
  "status": "string",
  "additional_notes": "string or null",
  "price_per_night": "float",
  "created_at": "datetime",
  "updated_at": "datetime or null",
  "deleted_at": "datetime or null",
  "is_active": "boolean"
}
```

#### 3.2 Get All Rooms
- **Endpoint**: `GET /api/v1/room/all`
- **Query Parameters**:
  - `skip` (default: 0)
  - `limit` (default: 100)
- **Response**: Array of RoomSchemaOut objects

#### 3.3 Get Room by ID
- **Endpoint**: `GET /api/v1/room/{room_id}`
- **Path Parameters**: `room_id` (UUID)
- **Response**: RoomSchemaOut object

#### 3.4 Get Rooms by Hotel
- **Endpoint**: `GET /api/v1/room/hotel/{hotel_id}`
- **Path Parameters**: `hotel_id` (UUID)
- **Query Parameters**:
  - `room_type` (optional): Filter by RoomType enum
  - `floor` (optional): Filter by floor number
  - `status` (optional): Filter by status
  - `skip` (default: 0)
  - `limit` (default: 100)
- **Response**: Array of RoomSchemaOut objects

#### 3.5 Update Room
- **Endpoint**: `PUT /api/v1/room/{room_id}`
- **Path Parameters**: `room_id` (UUID)
- **Request Body**: RoomSchemaIn (same as Create Room)
- **Response**: RoomSchemaOut object

#### 3.6 Delete Room
- **Endpoint**: `DELETE /api/v1/room/{room_id}`
- **Path Parameters**: `room_id` (UUID)
- **Status Code**: `204 No Content`

---

### 4. Booking Handlers (`/api/v1/booking`)

#### 4.1 Create Booking
- **Endpoint**: `POST /api/v1/booking`
- **Status Code**: `201 Created`
- **Request Body**:
```json
{
  "guest_id": "uuid",
  "hotel_id": "uuid",
  "room_id": "uuid",
  "check_in_date": "datetime or date string (YYYY-MM-DD)",
  "check_out_date": "datetime or date string (YYYY-MM-DD)",
  "num_guests": "integer (> 0)",
  "special_requests": "string (optional)"
}
```
- **Validation**:
  - Check-out date must be after check-in date
  - Guest, hotel, and room must exist and be active
  - Room must belong to the specified hotel
- **Response**:
```json
{
  "id": "uuid",
  "guest_id": "uuid",
  "hotel_id": "uuid",
  "room_id": "uuid",
  "check_in_date": "datetime",
  "check_out_date": "datetime",
  "total_price": "decimal (auto-calculated)",
  "booking_status": "BookingStatus enum (PENDING, CONFIRMED, CHECKED_IN, CHECKED_OUT, CANCELLED)",
  "num_guests": "integer",
  "special_requests": "string or null",
  "created_at": "datetime",
  "updated_at": "datetime or null",
  "is_active": "boolean"
}
```
- **Business Logic**:
  - Total price is calculated as: `(check_out_date - check_in_date) * room.price_per_night`
  - Initial status is set to `PENDING`

#### 4.2 Get Guest Bookings
- **Endpoint**: `GET /api/v1/booking/guest/{guest_id}/bookings`
- **Path Parameters**: `guest_id` (UUID)
- **Query Parameters**:
  - `skip` (default: 0)
  - `limit` (default: 100)
- **Response**:
```json
[
  {
    "booking_id": "uuid",
    "guest_info": {
      "first_name": "string",
      "last_name": "string",
      "email": "string",
      "phone_number": "string"
    },
    "booking_details": {
      "check_in_date": "datetime",
      "check_out_date": "datetime",
      "total_price": "string",
      "booking_status": "BookingStatus enum",
      "num_guests": "integer"
    }
  }
]
```

#### 4.3 Cancel Guest Booking
- **Endpoint**: `POST /api/v1/booking/guest/{guest_id}/cancel`
- **Path Parameters**: `guest_id` (UUID)
- **Response**: `boolean` (true if cancelled successfully)
- **Business Logic**: Updates booking status to `CANCELLED`

#### 4.4 List All Bookings
- **Endpoint**: `GET /api/v1/booking/`
- **Query Parameters**:
  - `skip` (default: 0)
  - `limit` (default: 100)
- **Response**: Array of BookingSchemaOut objects

#### 4.5 Get Booking Info by Guest ID
- **Endpoint**: `GET /api/v1/booking/{guest_id}`
- **Path Parameters**: `guest_id` (UUID)
- **Response**:
```json
{
  "guest_id": "string (uuid)",
  "guest_name": "string (full name)",
  "total_bookings": "integer",
  "bookings": [
    {
      "booking_id": "string (uuid)",
      "hotel_name": "string",
      "hotel_address": "string",
      "room_number": "string",
      "room_type": "string",
      "check_in_date": "date (ISO format)",
      "check_out_date": "date (ISO format)",
      "stay_duration": "integer (days)",
      "price_per_night": "float",
      "total_price": "float",
      "booking_status": "BookingStatus enum",
      "num_guests": "integer",
      "created_at": "datetime (ISO format)",
      "special_requests": "string or null"
    }
  ]
}
```
- **Note**: This endpoint joins booking data with hotel and room information

---

### 5. Payment Handlers (`/api/v1/payment`)

#### 5.1 Create Payment
- **Endpoint**: `POST /api/v1/payment`
- **Status Code**: `201 Created`
- **Request Body**:
```json
{
  "booking_id": "uuid",
  "amount": "decimal (> 0, 2 decimal places)",
  "payment_method": "string (max 50 chars)",
  "transaction_date": "datetime",
  "transaction_reference": "string (max 100 chars, optional)"
}
```
- **Response**:
```json
{
  "id": "uuid",
  "booking_id": "uuid",
  "amount": "decimal",
  "payment_method": "string",
  "transaction_date": "datetime",
  "payment_status": "PaymentStatus enum (PENDING, COMPLETED, FAILED, REFUNDED)",
  "transaction_reference": "string or null",
  "created_at": "datetime",
  "updated_at": "datetime or null",
  "deleted_at": "datetime or null",
  "is_active": "boolean"
}
```

#### 5.2 Get Payment by ID
- **Endpoint**: `GET /api/v1/payment/{payment_id}`
- **Path Parameters**: `payment_id` (UUID)
- **Response**: PaymentSchemaOut object

#### 5.3 Get Booking Payments
- **Endpoint**: `GET /api/v1/payment/booking/{booking_id}`
- **Path Parameters**: `booking_id` (UUID)
- **Query Parameters**:
  - `skip` (default: 0)
  - `limit` (default: 100)
- **Response**: Array of PaymentSchemaOut objects

#### 5.4 Update Payment Status
- **Endpoint**: `PUT /api/v1/payment/{payment_id}/status`
- **Path Parameters**: `payment_id` (UUID)
- **Query Parameters**: `status` (PaymentStatus enum)
- **Response**: PaymentSchemaOut object

#### 5.5 Void Payment
- **Endpoint**: `DELETE /api/v1/payment/{payment_id}`
- **Path Parameters**: `payment_id` (UUID)
- **Status Code**: `204 No Content`

#### 5.6 List All Payments
- **Endpoint**: `GET /api/v1/payment/`
- **Query Parameters**:
  - `skip` (default: 0)
  - `limit` (default: 100)
- **Response**: Array of PaymentSchemaOut objects

---

### 6. Review Handlers (`/api/v1/review`)

#### 6.1 Create Review
- **Endpoint**: `POST /api/v1/review/`
- **Status Code**: `201 Created`
- **Request Body**:
```json
{
  "hotel_id": "uuid",
  "rating": "integer (1-5, optional)",
  "review_text": "string (optional)",
  "review_date": "datetime (optional)"
}
```
- **Response**:
```json
{
  "id": "uuid",
  "hotel_id": "uuid",
  "rating": "integer or null",
  "review_text": "string or null",
  "review_date": "datetime or null",
  "created_at": "datetime",
  "updated_at": "datetime or null",
  "deleted_at": "datetime or null",
  "is_active": "boolean"
}
```

#### 6.2 Get Review by ID
- **Endpoint**: `GET /api/v1/review/{review_id}`
- **Path Parameters**: `review_id` (UUID)
- **Response**: ReviewSchemaOut object

#### 6.3 Get Hotel Reviews
- **Endpoint**: `GET /api/v1/review/hotel/{hotel_id}`
- **Path Parameters**: `hotel_id` (UUID)
- **Query Parameters**:
  - `skip` (default: 0)
  - `limit` (default: 100)
- **Response**: Array of ReviewSchemaOut objects

#### 6.4 Update Review
- **Endpoint**: `PUT /api/v1/review/{review_id}`
- **Path Parameters**: `review_id` (UUID)
- **Request Body**: ReviewSchemaIn (same as Create Review)
- **Response**: ReviewSchemaOut object

#### 6.5 Delete Review
- **Endpoint**: `DELETE /api/v1/review/{review_id}`
- **Path Parameters**: `review_id` (UUID)
- **Status Code**: `204 No Content`

---

### 7. Invoice Handlers (`/api/v1/invoice`)

#### 7.1 Get Invoice (Generate PDF)
- **Endpoint**: `GET /api/v1/invoice/{booking_id}`
- **Path Parameters**: `booking_id` (UUID)
- **Response**: PDF file (`application/pdf`)
- **Response Headers**:
  - `Content-Type`: `application/pdf`
  - `Content-Disposition`: `inline; filename=invoice_{booking_id}.pdf`
- **Invoice Contents**:
  - Invoice number (format: `INV-YYYYMMDD-{last 8 chars of booking_id}`)
  - Invoice date
  - Guest information (name, email)
  - Hotel information (name, address)
  - Room details (number, type)
  - Booking details (check-in, check-out, duration)
  - Pricing (price per night, total price)
  - Booking status
  - QR code for payment (links to: `https://llm_agent.dev/pay/{booking_id}`)
- **Business Logic**:
  - Joins booking, guest, hotel, and room data
  - Generates QR code with payment URL
  - Renders HTML template and converts to PDF using WeasyPrint

---

## Enums Reference

### RoomType
- `SINGLE_ROOM`
- `DOUBLE_ROOM`
- `TWIN_ROOM`
- `FAMILY_ROOM`
- `SUITE_ROOM`

### BookingStatus
- `PENDING` - Initial status when booking is created
- `CONFIRMED` - Booking confirmed
- `CHECKED_IN` - Guest has checked in
- `CHECKED_OUT` - Guest has checked out
- `CANCELLED` - Booking cancelled

### PaymentStatus
- `PENDING` - Payment initiated
- `COMPLETED` - Payment successful
- `FAILED` - Payment failed
- `REFUNDED` - Payment refunded

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Error message describing validation failure"
}
```

### 404 Not Found
```json
{
  "detail": "Resource with id {id} not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error message describing server error"
}
```

---

## Database Configuration

Database connection is configured via environment variables (see [app/core/config.py](app/core/config.py:10-14)):
- `DB_USER` - Database username
- `DB_PASS` - Database password
- `DB_NAME` - Database name
- `DB_HOST` - Database host
- `DB_PORT` - Database port

---

## Key Business Logic & Services

### Booking Service ([app/services/booking_service.py](app/services/booking_service.py))

1. **Create Booking** (line 27-109):
   - Validates guest, hotel, and room existence
   - Calculates total price based on stay duration
   - Sets initial status to `PENDING`

2. **Check Room Availability** (line 350-380):
   - Checks for overlapping bookings
   - Validates against cancelled bookings

3. **Get Booking Info** (line 385-463):
   - Retrieves comprehensive booking information
   - Joins with hotel and room data
   - Calculates stay duration

### Invoice Service ([app/services/invoice_service.py](app/services/invoice_service.py))

1. **Generate QR Code** (line 22-39):
   - Creates QR code for payment URL
   - Returns base64-encoded image

2. **Generate Invoice PDF** (line 42-72):
   - Renders HTML template with booking info
   - Includes QR code for payment
   - Converts to PDF using WeasyPrint

3. **Get Invoice** (line 75-120):
   - Retrieves booking with related data (guest, hotel, room)
   - Generates formatted booking information
   - Returns PDF document

---

## Running the Application

### Development Mode
```bash
python main.py
```
The server will start on `http://0.0.0.0:8000` with auto-reload enabled for the `app` directory.

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## API Documentation Access

When the server is running, interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
