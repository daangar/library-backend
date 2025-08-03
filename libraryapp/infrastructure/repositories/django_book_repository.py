"""Implementación concreta del repositorio de libros usando Django ORM"""
from typing import List, Optional, Dict, Any
from django.db.models import Q

from ...domain.entities.book import Book
from ...domain.repositories.book_repository import BookRepository
from ..models.django_models import DjangoBook
from .mappers import BookMapper


class DjangoBookRepository(BookRepository):
    """Implementación del repositorio de libros usando Django ORM"""

    def get_by_id(self, book_id: int) -> Optional[Book]:
        """Obtener libro por ID"""
        try:
            django_book = DjangoBook.objects.get(id=book_id)
            return BookMapper.to_domain(django_book)
        except DjangoBook.DoesNotExist:
            return None

    def get_all(self) -> List[Book]:
        """Obtener todos los libros"""
        django_books = DjangoBook.objects.all()
        return [BookMapper.to_domain(django_book) for django_book in django_books]

    def save(self, book: Book) -> Book:
        """Guardar libro (crear o actualizar)"""
        # Obtener o crear modelo Django
        if book.id:
            try:
                django_book = DjangoBook.objects.get(id=book.id)
            except DjangoBook.DoesNotExist:
                django_book = DjangoBook()
        else:
            django_book = DjangoBook()

        # Mapear todos los datos usando el mapper
        django_book = BookMapper.to_django(book, django_book)
        
        # Guardar
        django_book.save()
        
        # Actualizar ID en la entidad de dominio si es nueva
        book.id = django_book.id
        
        return book

    def delete(self, book_id: int) -> bool:
        """Eliminar libro por ID"""
        try:
            django_book = DjangoBook.objects.get(id=book_id)
            django_book.delete()
            return True
        except DjangoBook.DoesNotExist:
            return False

    def find_with_filters(self, filters: Dict[str, Any]) -> List[Book]:
        """Buscar libros con filtros dinámicos"""
        queryset = DjangoBook.objects.all()
        
        # Aplicar filtros
        if 'title' in filters:
            queryset = queryset.filter(title__icontains=filters['title'])
        
        if 'author_name' in filters:
            queryset = queryset.filter(author_name__icontains=filters['author_name'])
        
        if 'genre_name' in filters:
            queryset = queryset.filter(genre_name__icontains=filters['genre_name'])
        
        if 'published_year_min' in filters:
            queryset = queryset.filter(published_year__gte=filters['published_year_min'])
        
        if 'published_year_max' in filters:
            queryset = queryset.filter(published_year__lte=filters['published_year_max'])
        
        if 'available' in filters:
            if filters['available']:
                queryset = queryset.filter(stock__gt=0)
            else:
                queryset = queryset.filter(stock=0)
        
        if 'published_year' in filters:
            queryset = queryset.filter(published_year=filters['published_year'])
        
        if 'stock' in filters:
            queryset = queryset.filter(stock=filters['stock'])
        
        django_books = queryset.all()
        return [BookMapper.to_domain(django_book) for django_book in django_books]

    def find_available(self) -> List[Book]:
        """Obtener libros disponibles (con stock > 0)"""
        django_books = DjangoBook.objects.filter(stock__gt=0)
        return [BookMapper.to_domain(django_book) for django_book in django_books]

    def find_by_title(self, title: str) -> List[Book]:
        """Buscar libros por título (búsqueda parcial)"""
        django_books = DjangoBook.objects.filter(title__icontains=title)
        return [BookMapper.to_domain(django_book) for django_book in django_books]

    def find_by_author_name(self, author_name: str) -> List[Book]:
        """Buscar libros por nombre de autor"""
        django_books = DjangoBook.objects.filter(author_name__icontains=author_name)
        return [BookMapper.to_domain(django_book) for django_book in django_books]

    def find_by_genre_name(self, genre_name: str) -> List[Book]:
        """Buscar libros por nombre de género"""
        django_books = DjangoBook.objects.filter(genre_name__icontains=genre_name)
        return [BookMapper.to_domain(django_book) for django_book in django_books]