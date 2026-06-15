from pydantic import BaseModel
from typing import Any


class ApiResponse(BaseModel):
    success: bool
    data: Any = None
    message: str | None = None
