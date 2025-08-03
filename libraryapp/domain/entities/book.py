from dataclasses import dataclass
from typing import Optional


@dataclass
class Book:
    id: Optional[int]
    title: str
    author_name: str
    published_year: int
    genre_name: str
    stock: int = 0

    def __str__(self) -> str:
        return f"{self.title} by {self.author_name}"

    def is_available(self) -> bool:
        return self.stock > 0

    def validate(self) -> None:
        if not self.title or len(self.title.strip()) < 2:
            raise ValueError("Title too short")
        
        if self.published_year < 1 or self.published_year > 2024:
            raise ValueError("Invalid publication year")
        
        if self.stock < 0:
            raise ValueError("Stock cannot be negative")
        
        if not self.author_name or len(self.author_name.strip()) < 2:
            raise ValueError("Author name too short")
            
        if not self.genre_name or len(self.genre_name.strip()) < 2:
            raise ValueError("Genre name too short")

    def decrease_stock(self) -> None:
        if not self.is_available():
            raise ValueError(f"Book '{self.title}' not available")
        self.stock -= 1

    def increase_stock(self) -> None:
        self.stock += 1