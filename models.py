from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated, Any

class Book(BaseModel):
    title: str
    chapter_no: int | None = Field(default=1, gt = 0)
    pg_no: int | None = Field(default=1, gt=0)

class OutputSchema(BaseModel):
    message: str
    book_id: int
    title: str

class AllBooksOutputSchema(BaseModel):
    book_id: int
    title: str
