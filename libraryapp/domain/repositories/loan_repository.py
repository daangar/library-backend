from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.loan import Loan


class LoanRepository(ABC):
    """Interface para el repositorio de préstamos"""

    @abstractmethod
    def get_by_id(self, loan_id: int) -> Optional[Loan]:
        """Obtener préstamo por ID"""
        pass

    @abstractmethod
    def get_all(self) -> List[Loan]:
        """Obtener todos los préstamos"""
        pass

    @abstractmethod
    def save(self, loan: Loan) -> Loan:
        """Guardar préstamo (crear o actualizar)"""
        pass

    @abstractmethod
    def delete(self, loan_id: int) -> bool:
        """Eliminar préstamo por ID"""
        pass

    @abstractmethod
    def find_by_student_id(self, student_id: int) -> List[Loan]:
        """Buscar préstamos por ID de estudiante"""
        pass

    @abstractmethod
    def find_by_book_id(self, book_id: int) -> List[Loan]:
        """Buscar préstamos por ID de libro"""
        pass

    @abstractmethod
    def find_active_loans(self) -> List[Loan]:
        """Obtener préstamos activos (no devueltos)"""
        pass

    @abstractmethod
    def find_returned_loans(self) -> List[Loan]:
        """Obtener préstamos devueltos"""
        pass