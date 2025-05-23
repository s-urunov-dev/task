from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from books.models import Book, Payment, User, Order, Invoice
from books.permissions import IsAdmin
from books.serializers import BookSerializer, PaymentSerializer, RegisterSerializer, \
    UserActionSerializer, OrderSerializer, InvoiceSerializer, CustomTokenObtainPairSerializer


@extend_schema(tags=["Book"])
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


from drf_spectacular.utils import extend_schema, OpenApiExample


@extend_schema(
    tags=['Payment'],
    request=PaymentSerializer,
    examples=[
        OpenApiExample(
            "Oddiy to‘lov",
            value={
                "book": 1,
                "card_number": "1234567812345678"
            }
        )
    ]
)
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        card = request.data.get('card_number')
        book_id = request.data.get('book')

        if not card or len(card) != 16 or not card.isdigit():
            raise ValidationError({'card_number': 'Karta raqami 16 xonali bo‘lishi kerak.'})

        if not book_id:
            raise ValidationError({'book': 'Kitob ID ko‘rsatilmagan.'})

        is_success = int(card[-1]) % 2 == 0

        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            raise ValidationError({'book': 'Bunday IDga ega kitob topilmadi.'})

        payment = Payment.objects.create(
            user=request.user,
            book=book,
            card_number=card,
            is_successful=is_success,
        )

        serializer = self.get_serializer(payment)
        return Response(serializer.data)


@extend_schema(tags=['Stats'])
class AdminStatsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response({
            'total_users': User.objects.count(),
            'blocked_users': User.objects.filter(is_active=True).count(),
            'books': Book.objects.count(),
            'payments': Payment.objects.count(),
            'orders': Order.objects.count(),
            'succes_orders': Order.objects.filter(is_paid=True).count(),
        })


@extend_schema(tags=['Auth'])
class RegisterView(GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": f"Created user successfully."})


@extend_schema(tags=['Token'])
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(tags=['Token'])
class CustomTokenRefreshView(TokenRefreshView):
    pass


@extend_schema(tags=['Block'])
class BlockUnblockUserView(GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserActionSerializer

    def post(self, request, *args, **kwargs):
        path = request.path  # e.g. "/block-user/" or "/unblock-user/"
        action = 'unblock' if 'unblock' in path else 'block'

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data['user_id']

        try:
            user = User.objects.get(id=user_id)
            if action == 'block':
                if not user.is_active:
                    return Response({'message': f'User {user.username} is already blocked'})
                user.is_active = False
                message = f'User {user.username} has been blocked'
            else:
                if user.is_active:
                    return Response({'message': f'User {user.username} is already active'})
                user.is_active = True
                message = f'User {user.username} has been unblocked'

            user.save()
            return Response({'message': message})

        except User.DoesNotExist:
            return Response({'error': 'User not found'})


@extend_schema(tags=['Order'])
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().order_by('-created_at')
        return Order.objects.filter(user=user).order_by('-created_at')

    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        Invoice.objects.create(order=order, amount=order.book.price)


@extend_schema(tags=['Invoice'])
class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Invoice.objects.filter(order__user=self.request.user).order_by('-issued_at')


@extend_schema(tags=['Payment'])
class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(invoice__order__user=self.request.user).order_by('-paid_at')

    def create(self, request, *args, **kwargs):
        invoice_id = request.data.get('invoice_id')
        card_number = request.data.get('card_number')

        if not invoice_id or not card_number:
            return Response({'detail': 'invoice_id va card_number talab qilinadi.'})

        if len(card_number) != 16 or not card_number.isdigit():
            return Response({'detail': 'Card raqami 16 xonali raqam bo‘lishi kerak.'})

        try:
            invoice = Invoice.objects.get(id=invoice_id, order__user=request.user)
        except Invoice.DoesNotExist:
            return Response({'detail': 'Invoice topilmadi yoki sizga tegishli emas.'})

        is_success = int(card_number[-1]) % 2 == 0

        payment = Payment.objects.create(
            invoice=invoice,
            card_number=card_number,
            is_successful=is_success,
        )

        if is_success:
            order = invoice.order
            order.is_paid = True
            order.save()

        serializer = self.get_serializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
