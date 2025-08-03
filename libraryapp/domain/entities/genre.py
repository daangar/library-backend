from dataclasses import dataclass
from typing import Optional


@dataclass
class Genre:
    """Entidad de dominio para Género"""
    id: Optional[int]
    name: str
    description: Optional[str] = None

    def __str__(self) -> str:
        return self.name

    def validate(self) -> None:
        """Validaciones de negocio"""
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("El nombre del género debe tener al menos 2 caracteres")