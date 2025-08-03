from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..entities.book import Book


class BookRepository(ABC):
    """Interface para el repositorio de libros"""

    @abstractmethod
    def get_by_id(self, book_id: int) -> Optional[Book]:
        """Obtener libro por ID"""
        pass

    @abstractmethod
    def get_all(self) -> List[Book]:
        """Obtener todos los libros"""
        pass

    @abstractmethod
    def save(self, book: Book) -> Book:
        """Guardar libro (crear o actualizar)"""
        pass

    @abstractmethod
    def delete(self, book_id: int) -> bool:
        """Eliminar libro por ID"""
        pass

    @abstractmethod
    def find_with_filters(self, filters: Dict[str, Any]) -> List[Book]:
        """Buscar libros con filtros dinámicos"""
        pass

    @abstractmethod
    def find_available(self) -> List[Book]:
        """Obtener libros disponibles (con stock > 0)"""
        pass

    @abstractmethod
    def find_by_title(self, title: str) -> List[Book]:
        """Buscar libros por título (búsqueda parcial)"""
        pass

    @abstractmethod
    def find_by_author_name(self, author_name: str) -> List[Book]:
        """Buscar libros por nombre de autor"""
        pass

    @abstractmethod
    def find_by_genre_name(self, genre_name: str) -> List[Book]:
        """Buscar libros por nombre de género"""
        pass