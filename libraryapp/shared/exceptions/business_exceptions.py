"""Excepciones específicas del dominio de negocio"""


class BusinessException(Exception):
    """Excepción base para errores de negocio"""
    pass


class ValidationException(BusinessException):
    """Excepción para errores de validación"""
    pass


class BusinessRuleException(BusinessException):
    """Excepción para violaciones de reglas de negocio"""
    pass


class NotFoundException(BusinessException):
    """Excepción base para entidades no encontradas"""
    pass


class BookNotFoundException(NotFoundException):
    """Excepción cuando no se encuentra un libro"""
    pass


class LoanNotFoundException(NotFoundException):
    """Excepción cuando no se encuentra un préstamo"""
    pass


class UserNotFoundException(NotFoundException):
    """Excepción cuando no se encuentra un usuario"""
    pass


class AuthorNotFoundException(NotFoundException):
    """Excepción cuando no se encuentra un autor"""
    pass


class GenreNotFoundException(NotFoundException):
    """Excepción cuando no se encuentra un género"""
    pass