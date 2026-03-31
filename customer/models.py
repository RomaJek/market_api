from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

from accounts.models import TimeStampedModel, User
from warehouse.models import Product



class Cart(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} cart"



class CartItem(TimeStampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="item")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],  # en keminde 1 dana boliw kerek
        verbose_name="product quantity in cartitem"
    )
    def __str__(self):
        return f"{self.quantity} {self.product.name}"
    


class Order(TimeStampedModel):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"          # Kutilmekte
        PAID = "paid", "Paid"                   # Tolendi
        SHIPPED = "shipped", "Shipped"          # Jiberildi
        CANCELED = "canceled", "Canceled"       # Biykar etildi

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders"   # User oshse zakazlarda oship betedi null bolip qalmaydi
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],     # minimal 0 yamasa joqari boliw ushin
        verbose_name="order total price"
        )
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING,
        verbose_name="order status"
    )
    address = models.TextField(max_length=512, verbose_name="delivery address")

    def __str__(self):
        return f"{self.user.username} order"



class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, 
        related_name="orderitems", 
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],  # 1 yamasa odan ulken 
        verbose_name="orderitem quantity"
        )
    price = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="orderitem price"
    )

    def __str__(self):
        return f"{self.order.id}"



class Review(TimeStampedModel):

    class Status(models.TextChoices):
        ONE = "1", "one"
        TWO = "2", "two"
        THREE = "3", "three"
        FOUR = "4", "four"
        FIVE = "5", "five"

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="reviews",
        verbose_name="review by user"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews", verbose_name="review for product")
    text = models.TextField(blank=True, null=True)
    rating = models.CharField(
        max_length=10,
        choices=Status.choices,
        verbose_name="product rating"
    )

    class Meta:
        unique_together = (
            "user",
            "product",
        )

    def __str__(self):
        return f"{self.user.username}'s rating for {self.product.name}: {self.rating}"


