"""Mappers para convertir entre entidades de dominio y modelos de Django"""
from typing import Optional
from django.contrib.auth.models import User as DjangoUser

from ...domain.entities.book import Book
from ...domain.entities.user import User, UserRole
from ...domain.entities.loan import Loan

from ..models.django_models import (
    DjangoBook, DjangoLoan
)


class UserMapper:
    """Mapper para User"""
    
    @staticmethod
    def to_domain(django_user: DjangoUser) -> User:
        """Convertir modelo Django a entidad de dominio"""
        # Determinar rol basado en grupos
        role = UserRole.STUDENT
        if django_user.groups.filter(name='Librarians').exists():
            role = UserRole.LIBRARIAN
        
        return User(
            id=django_user.id,
            username=django_user.username,
            email=django_user.email,
            first_name=django_user.first_name or None,
            last_name=django_user.last_name or None,
            role=role
        )


class BookMapper:
    """Mapper para Book"""
    
    @staticmethod
    def to_domain(django_book: DjangoBook) -> Book:
        """Convertir modelo Django a entidad de dominio"""
        return Book(
            id=django_book.id,
            title=django_book.title,
            author_name=django_book.author_name,
            published_year=django_book.published_year,
            genre_name=django_book.genre_name,
            stock=django_book.stock
        )
    
    @staticmethod
    def to_django(book: Book, django_book: Optional[DjangoBook] = None) -> DjangoBook:
        """Convertir entidad de dominio a modelo Django"""
        if django_book is None:
            django_book = DjangoBook()
        
        django_book.title = book.title
        django_book.author_name = book.author_name
        django_book.published_year = book.published_year
        django_book.genre_name = book.genre_name
        django_book.stock = book.stock
        
        return django_book


class LoanMapper:
    """Mapper para Loan"""
    
    @staticmethod
    def to_domain(django_loan: DjangoLoan) -> Loan:
        """Convertir modelo Django a entidad de dominio"""
        return Loan(
            id=django_loan.id,
            student=UserMapper.to_domain(django_loan.student),
            book=BookMapper.to_domain(django_loan.book),
            borrowed_at=django_loan.borrowed_at,
            returned_at=django_loan.returned_at
        )
    
    @staticmethod
    def to_django(loan: Loan, django_loan: Optional[DjangoLoan] = None) -> DjangoLoan:
        """Convertir entidad de dominio a modelo Django"""
        if django_loan is None:
            django_loan = DjangoLoan()
        
        django_loan.borrowed_at = loan.borrowed_at
        django_loan.returned_at = loan.returned_at
        
        # Las relaciones se manejan por separado
        return django_loan