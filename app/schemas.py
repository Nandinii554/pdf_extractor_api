from pydantic import BaseModel
from typing import List

class WordBase(BaseModel):
    content: str

class LineBase(BaseModel):
    content: str
    words: List[WordBase]

class PageBase(BaseModel):
    page_number: int
    lines: List[LineBase]

class DocumentCreate(BaseModel):
    filename: str
    pages: List[PageBase]

class DocumentResponse(BaseModel):
    id: int
    filename: str

    class Config:
        orm_mode = True
