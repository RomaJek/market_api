from django.db import models
from django.db.models import Q, F
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from decimal import Decimal

from accounts.models import TimeStampedModel

# Create your models here.


class Category(TimeStampedModel):
    name = models.CharField(max_length=255, verbose_name="category name")
    slug = models.SlugField(unique=True, verbose_name="category URL slug")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,   # parent oshirilse childlarda oship ketedi
        null=True,
        blank=True,
        related_name="child",
        verbose_name="father category",
    )

    def clean(self):

        # ozin ozi parent boliwdi tekseriw 
        if self.parent == self:
            raise ValidationError("A category cannot be its own parent.")  # ozine ozi paret bolalmaydi
        
        # cycle tekseriw. Misali: A->B->C->D->E->A qate. admin panelden A-ni change qilgan waqtitta ogan C-ni parnet qilip bere almaymiz.
        # Misali: Aqliqti Ulken ataga ake qilip qoya almaymiz. Awladlar baslanadi ham bir siziq boylap dalawam etedi
        """
        Misali:
        self - D
        self,parent-C
        endi D - baslap A ga deyin parentler boyinsha tekseredi

        """

        parent = self.parent
        while parent:
            if parent == self:
                raise ValidationError("Cyclic relationship detected. This parent assignment is invalid.")   # kalso bolip qaliw aniqlandi
            parent = parent.parent
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)





    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="category",
    )
    name = models.CharField(max_length=255, verbose_name="product name")
    slug = models.SlugField(unique=True, verbose_name="product URL slug")
    description = models.TextField(blank=True, null=True, verbose_name="product description")
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],    # minimal 0,00 yamasa joqari boliw ushin
        verbose_name="product price"
    )

    discount_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),    # Decimal- putin sanlardin aniqligi ushin. misal 0.0002 bul pul esap sanaq anaq boliwi ushin
        validators=[MinValueValidator(Decimal('0.00'))],    # minimal 0 yamasa 0 den joqari boliw ushin
        blank=True,
        verbose_name="product discount price",
    )
    stock = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],   # minus san kiritiwden qorgaw, error xabar koriniw ushin
        verbose_name="product stock",
        )
    is_active = models.BooleanField(default=True, verbose_name="product is active")
    image = models.ImageField(upload_to="products_image/", blank=True, null=True, verbose_name="product image")


    def clean(self):
        # Bulda discount_price > price dan joqari boliwdan qorgaydi
        if self.discount_price and self.price and self.discount_price > self.price:
            raise ValidationError({
                'discount_price': "Discount must be less than the price"    # discount < price boliwi kerek
            })   
        
        super().clean()
    
    class Meta:
        # __lt - Less than <         __lte - Less Than or Equal <=
        # discount_price < price.  magluwmatlar bazasi darejesinde qorgan
        # en kushli qorganiw
        constraints = [
            models.CheckConstraint(
                condition=Q(discount_price__lt=F('price')),
                name='discount_price_must_be_less_than_price'
            )
        ]
    
    def __str__(self):
        return self.name

    def get_price_or_discount_price(self):
        if self.discount_price > 0:
            return self.discount_price
        return self.price
    
    








