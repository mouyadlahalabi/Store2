# store/urls.py
from django.urls import path
from . import views

app_name = "stores"

urlpatterns = [
    path("my-store/", views.store_front, name="store_front"),
    path("category/<int:pk>/", views.category_detail, name="category_detail"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
]
