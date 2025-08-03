"""Implementación concreta del repositorio de usuarios usando Django ORM"""
from typing import List, Optional
from django.contrib.auth.models import User as DjangoUser, Group

from ...domain.entities.user import User, UserRole
from ...domain.repositories.user_repository import UserRepository
from .mappers import UserMapper


class DjangoUserRepository(UserRepository):
    """Implementación del repositorio de usuarios usando Django ORM"""

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Obtener usuario por ID"""
        try:
            django_user = DjangoUser.objects.prefetch_related('groups').get(id=user_id)
            return UserMapper.to_domain(django_user)
        except DjangoUser.DoesNotExist:
            return None

    def get_by_username(self, username: str) -> Optional[User]:
        """Obtener usuario por nombre de usuario"""
        try:
            django_user = DjangoUser.objects.prefetch_related('groups').get(username=username)
            return UserMapper.to_domain(django_user)
        except DjangoUser.DoesNotExist:
            return None

    def get_all(self) -> List[User]:
        """Obtener todos los usuarios"""
        django_users = DjangoUser.objects.prefetch_related('groups').all()
        return [UserMapper.to_domain(django_user) for django_user in django_users]

    def save(self, user: User, password: Optional[str] = None) -> User:
        """Guardar usuario (crear o actualizar)"""
        is_new_user = user.id is None
        
        if user.id:
            try:
                django_user = DjangoUser.objects.get(id=user.id)
            except DjangoUser.DoesNotExist:
                django_user = DjangoUser()
                is_new_user = True
        else:
            django_user = DjangoUser()

        # Mapear campos básicos
        django_user.username = user.username
        django_user.email = user.email
        django_user.first_name = user.first_name or ""
        django_user.last_name = user.last_name or ""
        
        # Establecer password si se proporciona
        if password:
            django_user.set_password(password)
        
        django_user.save()
        
        # Asignar grupo según el rol (solo para nuevos usuarios)
        if is_new_user:
            # Eliminar de todos los grupos primero
            django_user.groups.clear()
            
            # Asignar grupo según rol
            if user.role == UserRole.LIBRARIAN:
                librarian_group, _ = Group.objects.get_or_create(name='Librarians')
                django_user.groups.add(librarian_group)
            else:  # UserRole.STUDENT (default)
                student_group, _ = Group.objects.get_or_create(name='Students') 
                django_user.groups.add(student_group)
        
        # Actualizar ID en la entidad de dominio si es nueva
        user.id = django_user.id
        
        return user

    def delete(self, user_id: int) -> bool:
        """Eliminar usuario por ID"""
        try:
            django_user = DjangoUser.objects.get(id=user_id)
            django_user.delete()
            return True
        except DjangoUser.DoesNotExist:
            return False

    def find_by_role(self, role: UserRole) -> List[User]:
        """Buscar usuarios por rol"""
        if role == UserRole.LIBRARIAN:
            django_users = DjangoUser.objects.prefetch_related('groups').filter(
                groups__name='Librarians'
            )
        else:  # UserRole.STUDENT
            django_users = DjangoUser.objects.prefetch_related('groups').filter(
                groups__name='Students'
            )
        
        return [UserMapper.to_domain(django_user) for django_user in django_users]