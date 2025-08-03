from typing import List, Optional
from datetime import datetime
from django.utils import timezone
from ...domain.entities.loan import Loan
from ...domain.repositories.loan_repository import LoanRepository
from ...domain.repositories.book_repository import BookRepository
from ...domain.repositories.user_repository import UserRepository
from ...shared.exceptions.business_exceptions import (
    LoanNotFoundException, 
    BookNotFoundException, 
    UserNotFoundException,
    ValidationException,
    BusinessRuleException
)


class GetLoanUseCase:
    """Caso de uso: Obtener préstamo por ID"""
    
    def __init__(self, loan_repository: LoanRepository):
        self.loan_repository = loan_repository
    
    def execute(self, loan_id: int) -> Loan:
        loan = self.loan_repository.get_by_id(loan_id)
        if not loan:
            raise LoanNotFoundException(f"Préstamo con ID {loan_id} no encontrado")
        return loan


class ListLoansUseCase:
    """Caso de uso: Listar préstamos (filtrados por usuario si es estudiante)"""
    
    def __init__(self, loan_repository: LoanRepository):
        self.loan_repository = loan_repository
    
    def execute(self, user_id: Optional[int] = None, is_librarian: bool = False) -> List[Loan]:
        if is_librarian:
            return self.loan_repository.get_all()
        elif user_id:
            return self.loan_repository.find_by_student_id(user_id)
        else:
            return []


class CreateLoanUseCase:
    """Caso de uso: Crear nuevo préstamo"""
    
    def __init__(
        self,
        loan_repository: LoanRepository,
        book_repository: BookRepository,
        user_repository: UserRepository
    ):
        self.loan_repository = loan_repository
        self.book_repository = book_repository
        self.user_repository = user_repository
    
    def execute(self, student_id: int, book_id: int) -> Loan:
        # Validar que existan estudiante y libro
        student = self.user_repository.get_by_id(student_id)
        if not student:
            raise UserNotFoundException(f"Usuario con ID {student_id} no encontrado")
        
        if not student.is_student():
            raise ValidationException("Solo los estudiantes pueden tomar préstamos")
        
        book = self.book_repository.get_by_id(book_id)
        if not book:
            raise BookNotFoundException(f"Libro con ID {book_id} no encontrado")
        
        # Validar disponibilidad del libro
        if not book.is_available():
            raise BusinessRuleException(f"El libro '{book.title}' no tiene stock disponible")
            
        # Validación adicional: verificar si el estudiante ya tiene este libro prestado
        try:
            from ...infrastructure.models.django_models import DjangoLoan
            existing_loan = DjangoLoan.objects.filter(
                student_id=student_id, 
                book_id=book_id, 
                returned_at__isnull=True
            ).exists()
            if existing_loan:
                raise BusinessRuleException(
                    f"El estudiante '{student.username}' ya tiene el libro '{book.title}' en préstamo"
                )
                
            # Validar límite de préstamos por estudiante (máximo 3 libros activos)
            active_loans_count = DjangoLoan.objects.filter(
                student_id=student_id, 
                returned_at__isnull=True
            ).count()
            if active_loans_count >= 3:
                raise BusinessRuleException(
                    f"El estudiante '{student.username}' ya tiene el máximo de 3 libros en préstamo"
                )
        except ImportError:
            # Si no se puede importar el modelo, continuar sin validación adicional
            pass
        
        # Crear entidad préstamo
        loan = Loan(
            id=None,
            student=student,
            book=book,
            borrowed_at=timezone.now(),
            returned_at=None
        )
        
        # Validar reglas de negocio
        loan.validate()
        
        # Disminuir stock del libro
        book.decrease_stock()
        self.book_repository.save(book)
        
        # Guardar préstamo
        return self.loan_repository.save(loan)


class ReturnLoanUseCase:
    """Caso de uso: Devolver libro prestado"""
    
    def __init__(
        self,
        loan_repository: LoanRepository,
        book_repository: BookRepository
    ):
        self.loan_repository = loan_repository
        self.book_repository = book_repository
    
    def execute(self, loan_id: int) -> Loan:
        # Obtener préstamo
        loan = self.loan_repository.get_by_id(loan_id)
        if not loan:
            raise LoanNotFoundException(f"Préstamo con ID {loan_id} no encontrado")
        
        if loan.is_returned():
            raise BusinessRuleException("Este préstamo ya ha sido devuelto")
        
        # Devolver libro (regla de negocio en la entidad)
        return_date = timezone.now()
        loan.return_book(return_date)
        
        # Guardar cambios en libro y préstamo
        self.book_repository.save(loan.book)
        return self.loan_repository.save(loan)


class DeleteLoanUseCase:
    """Caso de uso: Eliminar préstamo"""
    
    def __init__(self, loan_repository: LoanRepository):
        self.loan_repository = loan_repository
    
    def execute(self, loan_id: int) -> bool:
        loan = self.loan_repository.get_by_id(loan_id)
        if not loan:
            raise LoanNotFoundException(f"Préstamo con ID {loan_id} no encontrado")
        
        return self.loan_repository.delete(loan_id)