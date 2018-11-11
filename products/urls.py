from django.urls import path,re_path, include
from products.views import (
                            ProductListView, ProductDetailView,
                            ProductFeaturedListView, ProductFeaturedDetailView
                            )

app_name = 'products'

urlpatterns = [
    re_path(r'^$', ProductListView.as_view() , name='productlist'),
    re_path(r'^(?P<slug>[\w-]+)/$', ProductDetailView.as_view() , name='productdetail')    
    # path('featured/', ProductFeaturedListView.as_view() , name='featuredproductlist'),
    # path('featured/detail-<slug:slug>/', ProductFeaturedDetailView.as_view() , name='featuredproductdetail')

]
