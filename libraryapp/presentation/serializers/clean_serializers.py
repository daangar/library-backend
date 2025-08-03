
from rest_framework import serializers
from typing import Dict, Any

from ...domain.entities.book import Book
from ...domain.entities.user import User
from ...domain.entities.loan import Loan


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    role = serializers.CharField(read_only=True)

    def to_representation(self, instance: User) -> Dict[str, Any]:
        return {
            'id': instance.id,
            'username': instance.username,
            'email': instance.email,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'role': instance.role.value if instance.role else None
        }


class BookSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=255)
    author_name = serializers.CharField(max_length=200)
    published_year = serializers.IntegerField()
    genre_name = serializers.CharField(max_length=100)
    stock = serializers.IntegerField(min_value=0)
    is_available = serializers.SerializerMethodField()

    def get_is_available(self, instance: Book) -> bool:
        return instance.is_available()

    def to_representation(self, instance: Book) -> Dict[str, Any]:
        return {
            'id': instance.id,
            'title': instance.title,
            'author_name': instance.author_name,
            'published_year': instance.published_year,
            'genre_name': instance.genre_name,
            'stock': instance.stock,
            'is_available': instance.is_available()
        }


class LoanSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    student = UserSerializer(read_only=True)
    book = BookSerializer(read_only=True)
    book_id = serializers.IntegerField(write_only=True, required=False)
    borrowed_at = serializers.DateTimeField(read_only=True)
    returned_at = serializers.DateTimeField(read_only=True, allow_null=True)
    is_returned = serializers.SerializerMethodField()

    def get_is_returned(self, instance: Loan) -> bool:
        return instance.is_returned()

    def to_representation(self, instance: Loan) -> Dict[str, Any]:
        return {
            'id': instance.id,
            'student': UserSerializer().to_representation(instance.student),
            'book': BookSerializer().to_representation(instance.book),
            'borrowed_at': instance.borrowed_at.isoformat() if instance.borrowed_at else None,
            'returned_at': instance.returned_at.isoformat() if instance.returned_at else None,
            'is_returned': instance.is_returned()
        }