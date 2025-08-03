from dataclasses import dataclass
from typing import Optional


@dataclass
class Author:
    """Entidad de dominio para Autor"""
    id: Optional[int]
    name: str
    birth_year: Optional[int] = None
    nationality: Optional[str] = None

    def __str__(self) -> str:
        return self.name

    def validate(self) -> None:
        """Validaciones de negocio"""
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("El nombre del autor debe tener al menos 2 caracteres")
        
        if self.birth_year and (self.birth_year < 1 or self.birth_year > 2024):
            raise ValueError("El año de nacimiento debe estar entre 1 y 2024")