from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from books.models import Book, Payment, User, Order, Invoice


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(), source='book', write_only=True
    )

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Order
        fields = ('id', 'user', 'book', 'book_id', 'created_at', 'is_paid')
        read_only_fields = ('id', 'created_at', 'is_paid')


class InvoiceSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)

    class Meta:
        model = Invoice
        fields = ('id', 'order', 'amount', 'issued_at')


class PaymentSerializer(serializers.ModelSerializer):
    invoice_id = serializers.PrimaryKeyRelatedField(
        queryset=Invoice.objects.all(), source='invoice', write_only=True
    )

    class Meta:
        model = Payment
        fields = ('id', 'invoice_id', 'card_number', 'is_successful', 'paid_at')
        read_only_fields = ('id', 'is_successful', 'paid_at')


class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = CharField(write_only=True)
    password = CharField(write_only=True)

    class Meta:
        model = User
        fields = 'username', 'first_name', 'last_name', 'password', 'confirm_password'

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise ValidationError({"message": "Passwords do not match"})

        if User.objects.filter(email=attrs['username'], is_active=True).exists():
            raise ValidationError({"error": ["User with this username already exists"]})

        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        return user


class UserActionSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        data.update({
            'user_id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
        })

        return data