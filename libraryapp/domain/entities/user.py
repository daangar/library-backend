from dataclasses import dataclass
from typing import Optional
from enum import Enum


class UserRole(Enum):
    STUDENT = "student"
    LIBRARIAN = "librarian"


@dataclass
class User:
    id: Optional[int]
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole = UserRole.STUDENT

    def __str__(self) -> str:
        return f"{self.username} ({self.role.value})"

    def is_student(self) -> bool:
        return self.role == UserRole.STUDENT

    def is_librarian(self) -> bool:
        return self.role == UserRole.LIBRARIAN

    def validate(self) -> None:
        if not self.username or len(self.username.strip()) < 3:
            raise ValueError("Username too short")
        
        if not self.email or "@" not in self.email:
            raise ValueError("Invalid email")