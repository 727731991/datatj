from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    role: str = "user"

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class DataRecordBase(BaseModel):
    category: str
    title: str
    value: float = Field(..., ge=0)
    unit: Optional[str] = None
    date: date
    remark: Optional[str] = None

class DataRecordCreate(DataRecordBase):
    pass

class DataRecordUpdate(DataRecordBase):
    pass

class DataRecordResponse(DataRecordBase):
    id: int
    created_by: Optional[int]
    created_at: datetime
    
    class Config:
        orm_mode = True

class ReportTemplateBase(BaseModel):
    name: str
    config: str

class ReportTemplateCreate(ReportTemplateBase):
    pass

class ReportTemplateResponse(ReportTemplateBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class ReportRequest(BaseModel):
    template_id: Optional[int] = None
    category: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
