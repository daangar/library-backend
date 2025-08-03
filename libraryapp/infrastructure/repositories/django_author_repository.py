"""Implementación concreta del repositorio de autores usando Django ORM"""
from typing import List, Optional

from ...domain.entities.author import Author
from ...domain.repositories.author_repository import AuthorRepository
from ..models.django_models import DjangoAuthor
from .mappers import AuthorMapper


class DjangoAuthorRepository(AuthorRepository):
    """Implementación del repositorio de autores usando Django ORM"""

    def get_by_id(self, author_id: int) -> Optional[Author]:
        """Obtener autor por ID"""
        try:
            django_author = DjangoAuthor.objects.get(id=author_id)
            return AuthorMapper.to_domain(django_author)
        except DjangoAuthor.DoesNotExist:
            return None

    def get_all(self) -> List[Author]:
        """Obtener todos los autores"""
        django_authors = DjangoAuthor.objects.all()
        return [AuthorMapper.to_domain(django_author) for django_author in django_authors]

    def save(self, author: Author) -> Author:
        """Guardar autor (crear o actualizar)"""
        if author.id:
            try:
                django_author = DjangoAuthor.objects.get(id=author.id)
            except DjangoAuthor.DoesNotExist:
                django_author = DjangoAuthor()
        else:
            django_author = DjangoAuthor()

        django_author = AuthorMapper.to_django(author, django_author)
        django_author.save()
        
        # Actualizar ID en la entidad de dominio si es nueva
        author.id = django_author.id
        
        return author

    def delete(self, author_id: int) -> bool:
        """Eliminar autor por ID"""
        try:
            django_author = DjangoAuthor.objects.get(id=author_id)
            django_author.delete()
            return True
        except DjangoAuthor.DoesNotExist:
            return False

    def find_by_name(self, name: str) -> List[Author]:
        """Buscar autores por nombre (búsqueda parcial)"""
        django_authors = DjangoAuthor.objects.filter(name__icontains=name)
        return [AuthorMapper.to_domain(django_author) for django_author in django_authors]