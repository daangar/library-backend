"""Implementación concreta del repositorio de géneros usando Django ORM"""
from typing import List, Optional

from ...domain.entities.genre import Genre
from ...domain.repositories.genre_repository import GenreRepository
from ..models.django_models import DjangoGenre
from .mappers import GenreMapper


class DjangoGenreRepository(GenreRepository):
    """Implementación del repositorio de géneros usando Django ORM"""

    def get_by_id(self, genre_id: int) -> Optional[Genre]:
        """Obtener género por ID"""
        try:
            django_genre = DjangoGenre.objects.get(id=genre_id)
            return GenreMapper.to_domain(django_genre)
        except DjangoGenre.DoesNotExist:
            return None

    def get_all(self) -> List[Genre]:
        """Obtener todos los géneros"""
        django_genres = DjangoGenre.objects.all()
        return [GenreMapper.to_domain(django_genre) for django_genre in django_genres]

    def save(self, genre: Genre) -> Genre:
        """Guardar género (crear o actualizar)"""
        if genre.id:
            try:
                django_genre = DjangoGenre.objects.get(id=genre.id)
            except DjangoGenre.DoesNotExist:
                django_genre = DjangoGenre()
        else:
            django_genre = DjangoGenre()

        django_genre = GenreMapper.to_django(genre, django_genre)
        django_genre.save()
        
        # Actualizar ID en la entidad de dominio si es nueva
        genre.id = django_genre.id
        
        return genre

    def delete(self, genre_id: int) -> bool:
        """Eliminar género por ID"""
        try:
            django_genre = DjangoGenre.objects.get(id=genre_id)
            django_genre.delete()
            return True
        except DjangoGenre.DoesNotExist:
            return False

    def find_by_name(self, name: str) -> List[Genre]:
        """Buscar géneros por nombre (búsqueda parcial)"""
        django_genres = DjangoGenre.objects.filter(name__icontains=name)
        return [GenreMapper.to_domain(django_genre) for django_genre in django_genres]