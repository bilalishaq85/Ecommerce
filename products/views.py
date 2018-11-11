from django.shortcuts import render, Http404, get_object_or_404
from django.views.generic import ListView, DetailView
from products.models import Product

# Create your views here.
from carts.models import Cart

class ProductFeaturedListView(ListView):
    context_object_name = 'featuredproduct'
    template_name = 'products/featuredproductlist.html'

# *** This is to render data from queryset into the template ***
    def get_context_data(self, *args, **kwargs):
        context = super(ProductFeaturedListView, self).get_context_data(*args, **kwargs)
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.all().featured()

class ProductFeaturedDetailView(DetailView):
    #queryset = Product.objects.all()
    context_object_name = 'featuredproductdetail'
    template_name = 'products/featuredproductdetail.html'

# *** This is to render data from queryset into the template ***
    def get_context_data(self, *args, **kwargs):
        context = super(ProductFeaturedDetailView, self).get_context_data(*args, **kwargs)
        #context['abc'] = 'injected' #*** this is to assign data to the context if needed
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.all().featured()

    def get_object(self, *args, **kwargs):
        request = self.request
        slug = self.kwargs.get('slug')
        instance = Product.objects.get_by_slug(slug)
        if instance is None:
            raise Http404 ("Product does not exist")
        return instance


class ProductListView(ListView):
    context_object_name = 'products'
    template_name = 'products/productlist.html'

# *** This is to render data from queryset into the template ***
    def get_context_data(self, *args, **kwargs):
        context = super(ProductListView, self).get_context_data(*args, **kwargs)
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.all()

class ProductDetailView(DetailView):
    #queryset = Product.objects.all()
    context_object_name = 'productdetail'
    template_name = 'products/productdetail.html'

# *** This is to render data from queryset into the template ***
    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.new_or_create(self.request)
        context['cart'] = cart_obj #*** this is to assign data to the context if needed
        return context

# *** This method is to use Custom Model Manager to fetch data *****************
    def get_object(self, *args, **kwargs):
        request = self.request
        slug = self.kwargs.get('slug')
        instance = Product.objects.get_by_slug(slug)
        if instance is None:
            raise Http404 ("Product does not exist")
        return instance

    # def get_queryset(self):
    #     context = Product.objects.all()
    #     return(request, self.template_name, {'context':context})
