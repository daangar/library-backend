from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from .book import Book
from .user import User


@dataclass
class Loan:
    id: Optional[int]
    student: User
    book: Book
    borrowed_at: datetime
    returned_at: Optional[datetime] = None

    def __str__(self) -> str:
        status = "Returned" if self.is_returned() else "Active"
        return f"{self.book.title} - {self.student.username} ({status})"

    def is_returned(self) -> bool:
        return self.returned_at is not None

    def validate(self) -> None:
        if not self.student.is_student():
            raise ValueError("Only students can have loans")
        
        if not self.book.is_available() and not self.is_returned():
            raise ValueError(f"Book '{self.book.title}' not available")
        
        if self.returned_at and self.returned_at < self.borrowed_at:
            raise ValueError("Invalid return date")
        
        self.student.validate()
        self.book.validate()

    def return_book(self, return_date: datetime) -> None:
        if self.is_returned():
            raise ValueError("Loan already returned")
        
        if return_date < self.borrowed_at:
            raise ValueError("Invalid return date")
        
        self.returned_at = return_date
        self.book.increase_stock()