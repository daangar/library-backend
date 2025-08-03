from typing import List, Optional, Dict, Any
from ...domain.entities.book import Book
from ...domain.repositories.book_repository import BookRepository
from ...shared.exceptions.business_exceptions import BookNotFoundException, ValidationException, BusinessRuleException


class GetBookUseCase:
    def __init__(self, book_repository: BookRepository):
        self.book_repository = book_repository
    
    def execute(self, book_id: int) -> Book:
        book = self.book_repository.get_by_id(book_id)
        if not book:
            raise BookNotFoundException(f"Book with ID {book_id} not found")
        return book


class ListBooksUseCase:
    def __init__(self, book_repository: BookRepository):
        self.book_repository = book_repository
    
    def execute(self, filters: Optional[Dict[str, Any]] = None) -> List[Book]:
        if filters:
            return self.book_repository.find_with_filters(filters)
        return self.book_repository.get_all()


class CreateBookUseCase:
    
    def __init__(self, book_repository: BookRepository):
        self.book_repository = book_repository
    
    def execute(
        self, 
        title: str, 
        author_name: str, 
        genre_name: str, 
        published_year: int, 
        stock: int = 0
    ) -> Book:
        if not title or len(title.strip()) < 2:
            raise ValidationException("Title too short")
            
        if published_year < 1 or published_year > 2024:
            raise ValidationException("Invalid publication year")
            
        if stock < 0:
            raise ValidationException("Stock cannot be negative")
            
        if not author_name or len(author_name.strip()) < 2:
            raise ValidationException("Author name too short")
            
        if not genre_name or len(genre_name.strip()) < 2:
            raise ValidationException("Genre name too short")
            
        # Verificar si ya existe un libro con el mismo título y autor
        try:
            from ...infrastructure.models.django_models import DjangoBook
            existing_book = DjangoBook.objects.filter(
                title__iexact=title.strip(),
                author_name__iexact=author_name.strip()
            ).exists()
            if existing_book:
                raise ValidationException(
                    f"Ya existe un libro titulado '{title}' del autor '{author_name}'"
                )
        except ImportError:
            pass
        
        book = Book(
            id=None,
            title=title.strip(),
            author_name=author_name.strip(),
            genre_name=genre_name.strip(),
            published_year=published_year,
            stock=stock
        )
        
        book.validate()
        return self.book_repository.save(book)


class UpdateBookUseCase:
    
    def __init__(self, book_repository: BookRepository):
        self.book_repository = book_repository
    
    def execute(
        self, 
        book_id: int,
        title: Optional[str] = None,
        author_name: Optional[str] = None,
        genre_name: Optional[str] = None,
        published_year: Optional[int] = None,
        stock: Optional[int] = None
    ) -> Book:
        book = self.book_repository.get_by_id(book_id)
        if not book:
            raise BookNotFoundException(f"Book with ID {book_id} not found")
        if title is not None:
            if not title or len(title.strip()) < 2:
                raise ValidationException("Title too short")
            book.title = title.strip()
        
        if author_name is not None:
            if not author_name or len(author_name.strip()) < 2:
                raise ValidationException("Author name too short")
            book.author_name = author_name.strip()
        
        if genre_name is not None:
            if not genre_name or len(genre_name.strip()) < 2:
                raise ValidationException("Genre name too short")
            book.genre_name = genre_name.strip()
        
        if published_year is not None:
            if published_year < 1 or published_year > 2024:
                raise ValidationException("Invalid publication year")
            book.published_year = published_year
        
        if stock is not None:
            if stock < 0:
                raise ValidationException("Stock cannot be negative")
            book.stock = stock
        
        book.validate()
        return self.book_repository.save(book)


class DeleteBookUseCase:
    
    def __init__(self, book_repository: BookRepository):
        self.book_repository = book_repository
    
    def execute(self, book_id: int) -> bool:
        book = self.book_repository.get_by_id(book_id)
        if not book:
            raise BookNotFoundException(f"Book with ID {book_id} not found")
        try:
            from ...infrastructure.models.django_models import DjangoLoan
            active_loans = DjangoLoan.objects.filter(book_id=book_id, returned_at__isnull=True).count()
            if active_loans > 0:
                raise BusinessRuleException(
                    f"Cannot delete book '{book.title}' - has {active_loans} active loan(s)"
                )
        except ImportError:
            pass
        
        return self.book_repository.delete(book_id)