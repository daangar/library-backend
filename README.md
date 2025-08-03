# Sistema de Gestión de Biblioteca

API REST en Django para gestionar operaciones de biblioteca incluyendo libros, usuarios y préstamos.

## Requisitos

- Python 3.8+
- pip
- Entorno virtual (recomendado)

## Configuración Rápida

1. **Clonar y navegar al proyecto**
   ```bash
   git clone <url-del-repositorio>
   cd backend
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install django djangorestframework djangorestframework-simplejwt django-filter drf-yasg
   ```

4. **Configurar base de datos**
   ```bash
   python manage.py migrate
   ```

5. **Ejecutar servidor de desarrollo**
   ```bash
   python manage.py runserver
   ```

La API estará disponible en `http://localhost:8000`

## Usuarios Predeterminados

Después de la migración, estos usuarios se crean automáticamente:

| Usuario | Contraseña | Rol | Acceso |
|---------|------------|-----|--------|
| admin | Password!! | Bibliotecario | Todas las operaciones + Django admin |
| estudiante1 | PasswordE1!! | Estudiante | Ver libros, gestionar préstamos propios |
| estudiante2 | PasswordE2!! | Estudiante | Ver libros, gestionar préstamos propios |

## Endpoints de la API

### Autenticación
- `POST /api/token/` - Obtener token JWT
- `POST /api/token/refresh/` - Renovar token JWT

### Libros
- `GET /api/books/` - Listar libros (con filtros)
- `POST /api/books/` - Crear libro (solo bibliotecarios)
- `GET /api/books/{id}/` - Obtener detalles del libro
- `PUT/PATCH /api/books/{id}/` - Actualizar libro (solo bibliotecarios)
- `DELETE /api/books/{id}/` - Eliminar libro (solo bibliotecarios)

### Préstamos
- `GET /api/loans/` - Listar préstamos (propios para estudiantes, todos para bibliotecarios)
- `POST /api/loans/` - Crear préstamo (solo estudiantes)
- `GET /api/loans/{id}/` - Obtener detalles del préstamo
- `PATCH /api/loans/{id}/return/` - Devolver libro (solo bibliotecarios)

### Usuarios
- `GET /api/users/` - Listar usuarios (solo bibliotecarios)
- `POST /api/users/` - Crear usuario (solo bibliotecarios)
- `GET /api/users/{id}/` - Obtener detalles del usuario
- `PUT/PATCH /api/users/{id}/` - Actualizar usuario (solo bibliotecarios)

## Documentación

- **Swagger UI**: `http://localhost:8000/swagger/`
- **ReDoc**: `http://localhost:8000/redoc/`
- **Django Admin**: `http://localhost:8000/admin/`

## Ejemplos de Uso

### Obtener Token JWT
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Password!!"}'
```

### Listar Libros
```bash
curl -X GET http://localhost:8000/api/books/ \
  -H "Authorization: Bearer TU_JWT_TOKEN"
```

### Crear Préstamo (como estudiante)
```bash
curl -X POST http://localhost:8000/api/loans/ \
  -H "Authorization: Bearer JWT_TOKEN_ESTUDIANTE" \
  -H "Content-Type: application/json" \
  -d '{"book_id": 1}'
```

## Estructura del Proyecto

```
backend/
├── config/              # Configuración Django y URLs
├── libraryapp/
│   ├── domain/          # Entidades de negocio y repositorios
│   ├── application/     # Casos de uso (lógica de negocio)
│   ├── infrastructure/  # Acceso a datos y servicios externos
│   ├── presentation/    # Vistas API, serializadores, permisos
│   └── migrations/      # Migraciones de base de datos
└── manage.py
```

## Desarrollo

### Ejecutar Pruebas
```bash
python manage.py test
```

### Crear Superusuario
```bash
python manage.py createsuperuser
```

### Verificar Código
```bash
python manage.py check
```

## Características

- Autenticación JWT
- Permisos basados en roles (Estudiantes/Bibliotecarios)
- Implementación de Arquitectura Limpia
- Documentación completa de la API
- Datos de ejemplo incluidos
- Validación de entrada y manejo de errores

## Gestión de Libros
- Agregar/editar/eliminar libros (bibliotecarios)
- Buscar y filtrar libros
- Seguimiento de stock de libros

## Sistema de Préstamos
- Los estudiantes pueden pedir libros prestados
- Los bibliotecarios pueden gestionar todos los préstamos
- Gestión automática de stock
- Seguimiento de fechas de devolución