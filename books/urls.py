from django.urls import path, include
from rest_framework.routers import DefaultRouter

from books.views import BookViewSet, PaymentViewSet, CustomTokenObtainPairView, CustomTokenRefreshView, RegisterView, \
    BlockUnblockUserView, OrderViewSet, InvoiceViewSet

router = DefaultRouter()
router.register('books', BookViewSet, basename='books')
router.register('orders', OrderViewSet, basename='orders')
router.register('invoices', InvoiceViewSet, basename='invoices')
router.register('payments', PaymentViewSet, basename='payments')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),

    path('block-user/', BlockUnblockUserView.as_view(), name='block-user'),
    path('unblock-user/', BlockUnblockUserView.as_view(), name='unblock-user'),
]
