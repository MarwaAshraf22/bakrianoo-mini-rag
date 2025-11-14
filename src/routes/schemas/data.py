# from typing import Optional

from pydantic import BaseModel


class ProcessRequest(BaseModel):
    file_id: str
    # chunk_size: Optional[int] = 100
    # overlap_size: Optional[int] = 20
    chunk_size: int | None = 100
    overlap_size: int | None = 20
    do_reset: int | None = 0
