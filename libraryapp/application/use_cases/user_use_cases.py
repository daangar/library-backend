
from typing import List, Optional
from datetime import datetime

from ...domain.entities.user import User, UserRole
from ...domain.repositories.user_repository import UserRepository
from ...shared.exceptions.business_exceptions import (
    NotFoundException, ValidationException, BusinessRuleException
)


class UserNotFoundException(NotFoundException):
    pass


class GetUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def execute(self, user_id: int) -> User:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID {user_id} not found")
        return user


class ListUsersUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def execute(self, role: Optional[UserRole] = None) -> List[User]:
        if role:
            return self.user_repository.find_by_role(role)
        return self.user_repository.get_all()


class CreateUserUseCase:
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def execute(
        self, 
        username: str, 
        email: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        role: UserRole = UserRole.STUDENT
    ) -> User:
        if not username or len(username.strip()) < 3:
            raise ValidationException("Username too short")
            
        if not email or '@' not in email:
            raise ValidationException("Invalid email")
            
        if not password or len(password) < 8:
            raise ValidationException("Password too short")
            
        existing_user = self.user_repository.get_by_username(username)
        if existing_user:
            raise ValidationException(f"Username '{username}' already exists")
            
        try:
            from django.contrib.auth.models import User as DjangoUser
            if DjangoUser.objects.filter(email=email).exists():
                raise ValidationException(f"Email '{email}' already exists")
        except ImportError:
            pass
        
        user = User(
            id=None,
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        user.validate()
        return self.user_repository.save(user, password=password)


class UpdateUserUseCase:
    """Caso de uso: Actualizar usuario existente"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def execute(
        self, 
        user_id: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        role: Optional[UserRole] = None
    ) -> User:
        # Obtener usuario existente
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"Usuario con ID {user_id} no encontrado")
        
        # Validar que el nuevo username no exista (si se está cambiando)
        if username and username != user.username:
            existing_user = self.user_repository.get_by_username(username)
            if existing_user:
                raise ValidationException(f"Ya existe un usuario con username '{username}'")
        
        # Actualizar campos si se proporcionan
        if username is not None:
            user.username = username
        if email is not None:
            user.email = email
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if role is not None:
            user.role = role
        
        # Validar reglas de negocio
        user.validate()
        
        # Guardar cambios
        return self.user_repository.save(user)


class DeleteUserUseCase:
    """Caso de uso: Eliminar usuario"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def execute(self, user_id: int) -> bool:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"Usuario con ID {user_id} no encontrado")
        
        # Validación de negocio: verificar si el usuario tiene préstamos activos
        try:
            from django.contrib.auth.models import User as DjangoUser
            from ...infrastructure.models.django_models import DjangoLoan
            
            active_loans = DjangoLoan.objects.filter(student_id=user_id, returned_at__isnull=True).count()
            if active_loans > 0:
                raise BusinessRuleException(
                    f"No se puede eliminar el usuario '{user.username}' porque tiene {active_loans} préstamo(s) activo(s)"
                )
                
            # Verificar si es el último bibliotecario
            if user.is_librarian():
                total_librarians = DjangoUser.objects.filter(groups__name='Librarians').count()
                if total_librarians <= 1:
                    raise BusinessRuleException(
                        "No se puede eliminar el último bibliotecario del sistema"
                    )
        except ImportError:
            # Si no se puede importar el modelo, continuar sin validación adicional
            pass
        
        return self.user_repository.delete(user_id)


class GetUserByUsernameUseCase:
    """Caso de uso: Obtener usuario por username"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def execute(self, username: str) -> User:
        user = self.user_repository.get_by_username(username)
        if not user:
            raise UserNotFoundException(f"Usuario con username '{username}' no encontrado")
        return user