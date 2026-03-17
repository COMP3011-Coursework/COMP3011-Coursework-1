from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "jane_doe",
                "email": "jane@example.com",
                "password": "securepassword123",
            }
        }
    )

    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "username": "jane_doe",
                "email": "jane@example.com",
                "is_active": True,
                "created_at": "2024-01-15T10:30:00Z",
            }
        },
    )

    id: int
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqYW5lX2RvZSIsImV4cCI6MTcwNTMyMDYwMH0.abc123",
                "token_type": "bearer",
            }
        }
    )

    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
