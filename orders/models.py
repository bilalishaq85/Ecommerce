from django.db import models
from django.db.models.signals import pre_save, post_save
from carts.models import Cart
from addresses.models import Address
from billingprofile.models import BillingProfile
from ecommerce.utils import unique_order_id_generator
import math

# Create your models here.
ORDER_STATUS_CHOICES = [
    ('created', 'Created'),
    ('paid', 'Paid'),
    ('shipped', 'Shipped'),
    ('refunded', 'Refunded')
]

class OrderManager(models.Manager):
    def new_or_get(self, billing_profile, cart_obj):
        created = False
        qs = self.get_queryset().filter(
                                        billing_profile=billing_profile,
                                        cart=cart_obj,
                                        active=True,
                                        status='created')
        if qs.count() == 1:
            obj = qs.first()
        else:
            obj = self.model.objects.create(billing_profile=billing_profile, cart=cart_obj)
            created = True
        return obj, created

class Order(models.Model):
    billing_profile     = models.ForeignKey(BillingProfile, null=True, blank=True, on_delete=models.CASCADE)
    order_id            = models.CharField(max_length=120, blank=True)
    shipping_address    = models.ForeignKey(Address, null=True, blank=True, on_delete=models.CASCADE, related_name="shipping_address")
    billing_address     = models.ForeignKey(Address, null=True, blank=True, on_delete=models.CASCADE, related_name="billing_address")
    cart                = models.ForeignKey(Cart, on_delete=models.CASCADE)
    status              = models.CharField(max_length=120, default='created', choices=ORDER_STATUS_CHOICES)
    shipping_total      = models.DecimalField(default=5.99, decimal_places=2, max_digits=5)
    order_total         = models.DecimalField(default=0.00, decimal_places=2, max_digits=5)
    active              = models.BooleanField(default=True)

    def __str__(self):
        return self.order_id

    objects = OrderManager()

    class Meta:
        verbose_name_plural = "Orders"

    def update_total(self):
        cart_total = self.cart.total
        shipping_total = self.shipping_total
        new_order_total = math.fsum([cart_total, shipping_total])
        formatted_total = format(new_order_total, '.2f')
        self.order_total = formatted_total
        self.save()
        return new_order_total

    def check_order_done(self):
        billing_profile = self.billing_profile
        shipping_address = self.shipping_address
        billing_address = self.billing_address
        total = self.order_total
        if billing_profile and shipping_address and billing_address and total > 0:
            return True
        return False

    def mark_paid(self):
        if self.check_order_done():
            self.status = "paid"
            self.save()
        return self.status

def pre_save_orderid_receiver(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)
    qs = Order.objects.filter(cart=instance.cart).exclude(billing_profile=instance.billing_profile)
    if qs.exists():
        qs.update(active=False)

pre_save.connect(pre_save_orderid_receiver, sender=Order)


def post_save_ordertotal_receiver(sender, instance, created, *args, **kwargs):
    if not created:
        qs = Order.objects.filter(cart__id=instance.id)
        if qs.exists() and qs.count() == 1:
            order_obj = qs.first()
            order_obj.update_total()

post_save.connect(post_save_ordertotal_receiver, sender=Cart)


def post_save_order_receiver(sender, instance, created, *args, **kwargs):
    if created:
        instance.update_total()

post_save.connect(post_save_order_receiver, sender=Order)
