"""Views refactorizadas usando Clean Architecture"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ...infrastructure.models.django_models import DjangoBook
from ..serializers.clean_serializers import BookSerializer, LoanSerializer, UserSerializer
from ..permissions.permissions import IsStudent, IsLibrarian
from ...shared.exceptions.business_exceptions import (
    NotFoundException, ValidationException, BusinessRuleException
)

# Dependency Injection - En una aplicación real usarías un container
from ...infrastructure.repositories.django_book_repository import DjangoBookRepository
from ...infrastructure.repositories.django_loan_repository import DjangoLoanRepository
from ...infrastructure.repositories.django_user_repository import DjangoUserRepository

from ...application.use_cases.book_use_cases import (
    GetBookUseCase, ListBooksUseCase, CreateBookUseCase, 
    UpdateBookUseCase, DeleteBookUseCase
)
from ...application.use_cases.loan_use_cases import (
    GetLoanUseCase, ListLoansUseCase, CreateLoanUseCase, 
    ReturnLoanUseCase, DeleteLoanUseCase
)
from ...application.use_cases.user_use_cases import (
    GetUserUseCase, ListUsersUseCase, CreateUserUseCase,
    UpdateUserUseCase, DeleteUserUseCase, GetUserByUsernameUseCase
)


class BookFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    author_name = django_filters.CharFilter(lookup_expr='icontains')
    genre_name = django_filters.CharFilter(lookup_expr='icontains')
    published_year_min = django_filters.NumberFilter(field_name='published_year', lookup_expr='gte')
    published_year_max = django_filters.NumberFilter(field_name='published_year', lookup_expr='lte')
    available = django_filters.BooleanFilter(method='filter_available')

    class Meta:
        model = DjangoBook
        fields = ['author_name', 'genre_name', 'published_year', 'stock']

    def filter_available(self, queryset, name, value):
        if value:
            return queryset.filter(stock__gt=0)
        return queryset.filter(stock=0)


class BookViewSet(viewsets.ViewSet):
    """
    ViewSet para gestión de libros usando Clean Architecture.
    
    Permite operaciones CRUD sobre libros:
    - list: Listar todos los libros (con filtros disponibles)
    - create: Crear nuevo libro (solo bibliotecarios)
    - retrieve: Ver detalles de un libro específico
    - update: Actualizar libro completo (solo bibliotecarios)
    - partial_update: Actualizar libro parcialmente (solo bibliotecarios)
    - destroy: Eliminar libro (solo bibliotecarios)
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookFilter

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dependency Injection
        self.book_repository = DjangoBookRepository()
        
        # Use Cases
        self.get_book_use_case = GetBookUseCase(self.book_repository)
        self.list_books_use_case = ListBooksUseCase(self.book_repository)
        self.create_book_use_case = CreateBookUseCase(self.book_repository)
        self.update_book_use_case = UpdateBookUseCase(self.book_repository)
        self.delete_book_use_case = DeleteBookUseCase(self.book_repository)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsLibrarian()]
        return [IsAuthenticated()]

    def list(self, request):
        """Listar libros con filtros"""
        try:
            # Extraer filtros de query parameters
            filters = {}
            for key, value in request.GET.items():
                if value:
                    filters[key] = value
            
            books = self.list_books_use_case.execute(filters if filters else None)
            serializer = BookSerializer(books, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None):
        """Obtener libro específico"""
        try:
            book = self.get_book_use_case.execute(int(pk))
            serializer = BookSerializer(book)
            return Response(serializer.data)
        except NotFoundException as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Crear un nuevo libro con autor y género como campos de texto",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['title', 'author_name', 'genre_name', 'published_year'],
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Título del libro (min 2 caracteres)'),
                'author_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre del autor (min 2 caracteres)'),
                'genre_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre del género (min 2 caracteres)'),
                'published_year': openapi.Schema(type=openapi.TYPE_INTEGER, description='Año de publicación (1-2024)'),
                'stock': openapi.Schema(type=openapi.TYPE_INTEGER, description='Stock inicial (opcional, default 0)'),
            },
        ),
        responses={
            201: BookSerializer,
            400: 'Error de validación',
            403: 'Permisos insuficientes (solo bibliotecarios)',
        }
    )
    def create(self, request):
        """Crear nuevo libro"""
        try:
            data = request.data
            book = self.create_book_use_case.execute(
                title=data['title'],
                author_name=data['author_name'],
                genre_name=data['genre_name'],
                published_year=data['published_year'],
                stock=data.get('stock', 0)
            )
            serializer = BookSerializer(book)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (ValidationException, ValueError) as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Actualizar libro completo - todos los campos requeridos",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['title', 'author_name', 'genre_name', 'published_year', 'stock'],
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Título del libro'),
                'author_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre del autor'),
                'genre_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre del género'),
                'published_year': openapi.Schema(type=openapi.TYPE_INTEGER, description='Año de publicación'),
                'stock': openapi.Schema(type=openapi.TYPE_INTEGER, description='Stock del libro'),
            },
        ),
        responses={200: BookSerializer, 400: 'Error de validación', 404: 'Libro no encontrado'}
    )
    def update(self, request, pk=None):
        """Actualizar libro completo"""
        try:
            data = request.data
            book = self.update_book_use_case.execute(
                book_id=int(pk),
                title=data.get('title'),
                author_name=data.get('author_name'),
                genre_name=data.get('genre_name'),
                published_year=data.get('published_year'),
                stock=data.get('stock')
            )
            serializer = BookSerializer(book)
            return Response(serializer.data)
        except NotFoundException as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except (ValidationException, ValueError) as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def partial_update(self, request, pk=None):
        """Actualizar libro parcialmente"""
        return self.update(request, pk)

    def destroy(self, request, pk=None):
        """Eliminar libro"""
        try:
            success = self.delete_book_use_case.execute(int(pk))
            if success:
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'error': 'No se pudo eliminar el libro'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except NotFoundException as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoanViewSet(viewsets.ViewSet):
    """
    ViewSet para gestión de préstamos usando Clean Architecture.
    
    Operaciones disponibles:
    - list: Listar préstamos (estudiantes ven solo los suyos, bibliotecarios ven todos)
    - create: Crear nuevo préstamo (solo estudiantes, valida stock disponible)
    - retrieve: Ver detalles de un préstamo específico
    - return: Devolver libro (solo bibliotecarios, endpoint personalizado)
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dependency Injection
        self.loan_repository = DjangoLoanRepository()
        self.book_repository = DjangoBookRepository()
        self.user_repository = DjangoUserRepository()
        
        # Use Cases
        self.get_loan_use_case = GetLoanUseCase(self.loan_repository)
        self.list_loans_use_case = ListLoansUseCase(self.loan_repository)
        self.create_loan_use_case = CreateLoanUseCase(
            self.loan_repository, self.book_repository, self.user_repository
        )
        self.return_loan_use_case = ReturnLoanUseCase(
            self.loan_repository, self.book_repository
        )
        self.delete_loan_use_case = DeleteLoanUseCase(self.loan_repository)

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsStudent()]
        if self.action == 'return_loan':
            return [IsAuthenticated(), IsLibrarian()]
        return [IsAuthenticated()]

    def list(self, request):
        """Listar préstamos"""
        try:
            # Prevenir error en generación de schema de Swagger
            if getattr(self, 'swagger_fake_view', False):
                return Response([])
            
            # Determinar si es bibliotecario
            is_librarian = request.user.groups.filter(name='Librarians').exists()
            user_id = request.user.id if not is_librarian else None
            
            loans = self.list_loans_use_case.execute(
                user_id=user_id, 
                is_librarian=is_librarian
            )
            serializer = LoanSerializer(loans, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None):
        """Obtener préstamo específico"""
        try:
            loan = self.get_loan_use_case.execute(int(pk))
            
            # Verificar permisos: solo el estudiante o bibliotecarios pueden ver el préstamo
            if (loan.student.id != request.user.id and 
                not request.user.groups.filter(name='Librarians').exists()):
                return Response(
                    {'error': 'No tienes permisos para ver este préstamo'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = LoanSerializer(loan)
            return Response(serializer.data)
        except NotFoundException as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request):
        """Crear nuevo préstamo"""
        try:
            data = request.data
            loan = self.create_loan_use_case.execute(
                student_id=request.user.id,
                book_id=data['book_id']
            )
            serializer = LoanSerializer(loan)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (ValidationException, BusinessRuleException) as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except NotFoundException as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['patch'], url_path='return')
    def return_loan(self, request, pk=None):
        """
        Devolver un libro prestado.
        
        Marca el préstamo como devuelto estableciendo la fecha de devolución
        e incrementa automáticamente el stock del libro.
        
        Solo los bibliotecarios pueden usar este endpoint.
        """
        try:
            loan = self.return_loan_use_case.execute(int(pk))
            serializer = LoanSerializer(loan)
            return Response(serializer.data)
        except NotFoundException as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except BusinessRuleException as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserViewSet(viewsets.ViewSet):
    """
    ViewSet para gestión de usuarios usando Clean Architecture.
    
    Operaciones disponibles:
    - list: Listar usuarios (solo bibliotecarios pueden ver todos)
    - create: Crear nuevo usuario (solo bibliotecarios)
    - retrieve: Ver detalles de un usuario específico
    - update: Actualizar usuario completo (solo bibliotecarios)
    - partial_update: Actualizar usuario parcialmente (solo bibliotecarios)
    - destroy: Eliminar usuario (solo bibliotecarios)
    - me: Ver información del usuario actual (endpoint personalizado)
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dependency Injection
        self.user_repository = DjangoUserRepository()
        
        # Use Cases
        self.get_user_use_case = GetUserUseCase(self.user_repository)
        self.list_users_use_case = ListUsersUseCase(self.user_repository)
        self.create_user_use_case = CreateUserUseCase(self.user_repository)
        self.update_user_use_case = UpdateUserUseCase(self.user_repository)
        self.delete_user_use_case = DeleteUserUseCase(self.user_repository)
        self.get_user_by_username_use_case = GetUserByUsernameUseCase(self.user_repository)

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated()]
        # Solo bibliotecarios pueden hacer operaciones CRUD sobre usuarios
        return [IsAuthenticated(), IsLibrarian()]

    def list(self, request):
        """Listar usuarios (solo bibliotecarios)"""
        try:
            # Filtro opcional por rol
            role_filter = request.GET.get('role')
            role = None
            if role_filter:
                from ...domain.entities.user import UserRole
                if role_filter == 'student':
                    role = UserRole.STUDENT
                elif role_filter == 'librarian':
                    role = UserRole.LIBRARIAN
            
            users = self.list_users_use_case.execute(role=role)
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None):
        """Obtener usuario específico (solo bibliotecarios)"""
        try:
            user = self.get_user_use_case.execute(int(pk))
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except NotFoundException as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request):
        """Crear nuevo usuario (solo bibliotecarios)"""
        try:
            data = request.data
            from ...domain.entities.user import UserRole
            
            # Convertir string de rol a enum
            role = UserRole.STUDENT  # default
            if data.get('role') == 'librarian':
                role = UserRole.LIBRARIAN
            elif data.get('role') == 'student':
                role = UserRole.STUDENT
            
            user = self.create_user_use_case.execute(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                role=role
            )
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (ValidationException, ValueError) as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, pk=None):
        """Actualizar usuario completo (solo bibliotecarios)"""
        try:
            data = request.data
            from ...domain.entities.user import UserRole
            
            # Convertir string de rol a enum si se proporciona
            role = None
            if 'role' in data:
                if data['role'] == 'librarian':
                    role = UserRole.LIBRARIAN
                elif data['role'] == 'student':
                    role = UserRole.STUDENT
            
            user = self.update_user_use_case.execute(
                user_id=int(pk),
                username=data.get('username'),
                email=data.get('email'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                role=role
            )
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except NotFoundException as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except (ValidationException, ValueError) as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def partial_update(self, request, pk=None):
        """Actualizar usuario parcialmente (solo bibliotecarios)"""
        return self.update(request, pk)

    def destroy(self, request, pk=None):
        """Eliminar usuario (solo bibliotecarios)"""
        try:
            success = self.delete_user_use_case.execute(int(pk))
            if success:
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'error': 'No se pudo eliminar el usuario'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except NotFoundException as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """
        Obtener información del usuario actual.
        
        Endpoint que permite a cualquier usuario autenticado ver su propia información.
        """
        try:
            # Prevenir error en generación de schema de Swagger
            if getattr(self, 'swagger_fake_view', False):
                return Response({})
            
            user = self.get_user_use_case.execute(request.user.id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except NotFoundException as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )