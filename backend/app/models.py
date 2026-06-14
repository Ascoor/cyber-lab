"""Pydantic models for the Cyber Lab Control Panel API."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class TargetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    target: str = Field(..., min_length=1, max_length=500)
    target_type: Optional[str] = Field(default=None, max_length=20)
    authorized: bool = False
    scope_notes: Optional[str] = Field(default=None, max_length=1000)


class TargetAuthorizationUpdate(BaseModel):
    authorized: bool
