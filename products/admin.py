from django.contrib import admin
from products.models import Product

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'slug']
    class Meta:
        model = Product


admin.site.register(Product, ProductAdmin)
