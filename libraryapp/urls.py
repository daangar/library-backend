from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .presentation.views.api_views import BookViewSet, LoanViewSet, UserViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'loans', LoanViewSet, basename='loan')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('api/', include(router.urls)),
]