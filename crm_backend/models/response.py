from typing import Any, Dict, List

from pydantic import BaseModel


class CrmResponse(BaseModel):
    data: List[Any] | Dict[str, Any] | None
    msg: str
