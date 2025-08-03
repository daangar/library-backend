"""Modelos de Django - Capa de infraestructura"""
from django.conf import settings
from django.db import models


class DjangoBook(models.Model):
    """Modelo Django para Libro"""
    title = models.CharField(max_length=255)
    author_name = models.CharField(max_length=200)
    published_year = models.PositiveIntegerField()
    genre_name = models.CharField(max_length=100)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'libraryapp_book'
        ordering = ['title']

    def __str__(self):
        return f"{self.title} by {self.author_name}"


class DjangoLoan(models.Model):
    """Modelo Django para Préstamo"""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(DjangoBook, on_delete=models.CASCADE)
    borrowed_at = models.DateTimeField(auto_now_add=True)
    returned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'libraryapp_loan'
        ordering = ['-borrowed_at']

    def __str__(self):
        status = "Returned" if self.returned_at else "Active"
        return f"{self.book.title} - {self.student.username} ({status})"


# Alias para compatibilidad con el código existente
Book = DjangoBook
Loan = DjangoLoan