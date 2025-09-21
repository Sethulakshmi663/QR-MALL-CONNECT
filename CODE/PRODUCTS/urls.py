from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
    path('<int:pk>/qr/', views.generate_product_qr, name='product_qr'),
    path('api/search-suggestions/', views.search_suggestions, name='search_suggestions'),
    path('admin/batch-qr/', views.batch_qr_generation, name='batch_qr'),
]
