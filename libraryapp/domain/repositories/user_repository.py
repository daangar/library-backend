from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.user import User, UserRole


class UserRepository(ABC):
    """Interface para el repositorio de usuarios"""

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Obtener usuario por ID"""
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """Obtener usuario por nombre de usuario"""
        pass

    @abstractmethod
    def get_all(self) -> List[User]:
        """Obtener todos los usuarios"""
        pass

    @abstractmethod
    def save(self, user: User, password: Optional[str] = None) -> User:
        """Guardar usuario (crear o actualizar)"""
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """Eliminar usuario por ID"""
        pass

    @abstractmethod
    def find_by_role(self, role: UserRole) -> List[User]:
        """Buscar usuarios por rol"""
        pass