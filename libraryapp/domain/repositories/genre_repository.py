from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.genre import Genre


class GenreRepository(ABC):
    """Interface para el repositorio de géneros"""

    @abstractmethod
    def get_by_id(self, genre_id: int) -> Optional[Genre]:
        """Obtener género por ID"""
        pass

    @abstractmethod
    def get_all(self) -> List[Genre]:
        """Obtener todos los géneros"""
        pass

    @abstractmethod
    def save(self, genre: Genre) -> Genre:
        """Guardar género (crear o actualizar)"""
        pass

    @abstractmethod
    def delete(self, genre_id: int) -> bool:
        """Eliminar género por ID"""
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> List[Genre]:
        """Buscar géneros por nombre (búsqueda parcial)"""
        pass