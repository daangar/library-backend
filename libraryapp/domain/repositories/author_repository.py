from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.author import Author


class AuthorRepository(ABC):
    """Interface para el repositorio de autores"""

    @abstractmethod
    def get_by_id(self, author_id: int) -> Optional[Author]:
        """Obtener autor por ID"""
        pass

    @abstractmethod
    def get_all(self) -> List[Author]:
        """Obtener todos los autores"""
        pass

    @abstractmethod
    def save(self, author: Author) -> Author:
        """Guardar autor (crear o actualizar)"""
        pass

    @abstractmethod
    def delete(self, author_id: int) -> bool:
        """Eliminar autor por ID"""
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> List[Author]:
        """Buscar autores por nombre (búsqueda parcial)"""
        pass