from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator



# 1. Custom User Manager. phone_number-di username orina paydalaniw ushin.
class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Phone number required!")
        
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', User.SUPER_ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser is_staff=True is required.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser is_superuser=True is required.")

        return self.create_user(phone_number, password, **extra_fields)



# created_at ham updated_at qayta-qayta jazbaw ushin paydalandim
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True # qosimsha table jaratpaydi tek g'ana basqa modeller ushun. waqitti Qayta-qayta jazbaw ushin 


# Uluwmaliq user-lerdi ushin.
class User(AbstractUser, TimeStampedModel):
    
    ADMIN = 'admin'
    CLIENT = 'client'
    SUPER_ADMIN = 'super_admin'

    ROLE_CHOICES = [
        (SUPER_ADMIN, 'Super_admin'),
        (ADMIN, 'Admin'),
        (CLIENT, 'Client'),
    ]
    
    # Telefon nomerdi validatsiya qiliw ushin
    phone_validator = RegexValidator(
        regex=r'^\d{9}$',
        message="Invalid input: phone number must contain exactly 9 numeric digits without spaces or separators (e.g., 901234567)."
    )

    username = None     # username kerek emes
    email = None
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CLIENT, verbose_name="user role")
    phone_number = models.CharField(max_length=9, unique=True, validators=[phone_validator], verbose_name="user phone number")
    address = models.TextField(max_length=1024, blank=True, verbose_name="user address")
    telegram_id = models.CharField(max_length=255, blank=True, verbose_name="user telegram id")

    USERNAME_FIELD = 'phone_number'     # username ornina phone_number-di belgiledik
    REQUIRED_FIELDS = []

    objects = CustomUserManager()   # joqarda jazgan CustomUserManager-di ozimnin modlime baylanistirdim, sebebi createsuperuser jaratiwda error boldi

    def is_admin(self):
        if self.role and self.role == self.ADMIN:
            return True
        return False
    
    def __str__(self):
        return self.phone_number


