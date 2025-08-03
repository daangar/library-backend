"""Implementación concreta del repositorio de préstamos usando Django ORM"""
from typing import List, Optional
from django.contrib.auth.models import User as DjangoUser

from ...domain.entities.loan import Loan
from ...domain.repositories.loan_repository import LoanRepository
from ..models.django_models import DjangoLoan, DjangoBook
from .mappers import LoanMapper


class DjangoLoanRepository(LoanRepository):
    """Implementación del repositorio de préstamos usando Django ORM"""

    def get_by_id(self, loan_id: int) -> Optional[Loan]:
        """Obtener préstamo por ID"""
        try:
            django_loan = DjangoLoan.objects.select_related(
                'student', 'book'
            ).get(id=loan_id)
            return LoanMapper.to_domain(django_loan)
        except DjangoLoan.DoesNotExist:
            return None

    def get_all(self) -> List[Loan]:
        """Obtener todos los préstamos"""
        django_loans = DjangoLoan.objects.select_related(
            'student', 'book'
        ).all()
        return [LoanMapper.to_domain(django_loan) for django_loan in django_loans]

    def save(self, loan: Loan) -> Loan:
        """Guardar préstamo (crear o actualizar)"""
        # Obtener o crear modelo Django
        if loan.id:
            try:
                django_loan = DjangoLoan.objects.get(id=loan.id)
            except DjangoLoan.DoesNotExist:
                django_loan = DjangoLoan()
        else:
            django_loan = DjangoLoan()

        # Mapear datos básicos
        django_loan = LoanMapper.to_django(loan, django_loan)
        
        # Obtener relaciones desde la base de datos
        try:
            django_student = DjangoUser.objects.get(id=loan.student.id)
            django_book = DjangoBook.objects.get(id=loan.book.id)
        except (DjangoUser.DoesNotExist, DjangoBook.DoesNotExist) as e:
            raise ValueError(f"Estudiante o libro no encontrado: {e}")
        
        django_loan.student = django_student
        django_loan.book = django_book
        
        # Guardar
        django_loan.save()
        
        # Actualizar ID en la entidad de dominio si es nueva
        loan.id = django_loan.id
        
        return loan

    def delete(self, loan_id: int) -> bool:
        """Eliminar préstamo por ID"""
        try:
            django_loan = DjangoLoan.objects.get(id=loan_id)
            django_loan.delete()
            return True
        except DjangoLoan.DoesNotExist:
            return False

    def find_by_student_id(self, student_id: int) -> List[Loan]:
        """Buscar préstamos por ID de estudiante"""
        django_loans = DjangoLoan.objects.select_related(
            'student', 'book'
        ).filter(student_id=student_id)
        return [LoanMapper.to_domain(django_loan) for django_loan in django_loans]

    def find_by_book_id(self, book_id: int) -> List[Loan]:
        """Buscar préstamos por ID de libro"""
        django_loans = DjangoLoan.objects.select_related(
            'student', 'book'
        ).filter(book_id=book_id)
        return [LoanMapper.to_domain(django_loan) for django_loan in django_loans]

    def find_active_loans(self) -> List[Loan]:
        """Obtener préstamos activos (no devueltos)"""
        django_loans = DjangoLoan.objects.select_related(
            'student', 'book'
        ).filter(returned_at__isnull=True)
        return [LoanMapper.to_domain(django_loan) for django_loan in django_loans]

    def find_returned_loans(self) -> List[Loan]:
        """Obtener préstamos devueltos"""
        django_loans = DjangoLoan.objects.select_related(
            'student', 'book'
        ).filter(returned_at__isnull=False)
        return [LoanMapper.to_domain(django_loan) for django_loan in django_loans]