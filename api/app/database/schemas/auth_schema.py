from pydantic import BaseModel, EmailStr, Field

class RegisterSchema(BaseModel):
    first_name      : str = Field(min_length=2, max_length=50)
    last_name       : str = Field(min_length=2, max_length=50)
    email           : EmailStr
    phone_number    : str = Field(min_length=8, max_length=15)
    password        : str = Field(min_length=8, max_length=100)

class LoginSchema(BaseModel):
    email           : EmailStr
    password        : str

class TokenSchema(BaseModel):
    access_token    : str
    token_type      : str = "bearer"
