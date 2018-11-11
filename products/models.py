import os, random
from django.db import models
from django.db.models import Q
from django.urls import reverse
from ecommerce.utils import unique_slug_generator
from django.db.models.signals import pre_save

def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext

def upload_image_path(instance, filename):
    new_filename = random.randint(1,1223424234)
    name, ext = get_filename_ext(filename)
    final_name = f'{new_filename}{ext}'
    return 'products/'f'{new_filename}/{final_name}'

# *** This is to Custom QuerySet ***
class ProductQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(featured=True)

    def search(self, query):
        lookups = ( Q(title__icontains=query) |
                    Q(description__icontains=query) |
                    Q(price__icontains=query) |
                    Q(tag__title__icontains=query)
                  )
        return self.filter(lookups).distinct() # distinct is to remove redundant records from the result


# *** This is Custom Model Manager ***
class ProductManager(models.Manager):
# *** Customize all built-in methods here ***
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active()

    def featured(self):
        return self.get_queryset().featured()

    def get_by_slug(self, slug):
        qs = self.get_queryset().filter(slug=slug)
        if qs.count() >= 1:
            return qs.first()
        return None

    def search(self, query):
        return self.get_queryset().active().search(query)

# Create your models here.
class Product(models.Model):
    title       = models.CharField(max_length=20)
    slug        = models.SlugField(blank=True, unique=True)
    description = models.CharField(max_length=30)
    price       = models.DecimalField(decimal_places=2, max_digits=5, default=1.0)
    image       = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
    featured    = models.BooleanField(default=False)
    active      = models.BooleanField(default=True)

    objects = ProductManager()

    def get_absolute_url(self):        
        # return f'/products/{self.slug}/'
        return reverse('products:productdetail',kwargs={"slug": self.slug})

    def __str__(self):
        return self.title

    # class Meta:
    #     verbose_name_plural = "products"

def product_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(product_pre_save_receiver, sender=Product)
