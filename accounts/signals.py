from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User as CustomUser
from customer.models import Cart


@receiver(post_save, sender=CustomUser)
def create_user_cart(sender, instance, created, **kwargs):
    """ User jaratilsa avtomat ogan tiyisli Cart jaratiladi"""
    if created:
        Cart.objects.create(user=instance)





