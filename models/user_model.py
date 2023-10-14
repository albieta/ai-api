# generated by datamodel-codegen:
#   filename:  user.json
#   timestamp: 2023-10-14T06:34:35+00:00

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    id: str = Field(..., description='id of the user')
    name: str = Field(..., description='Name of the user')
    surname: str = Field(..., description='Surname of the user')
    email: EmailStr = Field(..., description='Email address of the user')
