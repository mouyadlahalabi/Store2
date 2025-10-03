from django.urls import path
from . import views

app_name = "stores"

urlpatterns = [
    path("my-store/", views.store_front, name="store_front"),
    path("category/<int:id>/", views.category_detail, name="category_detail"),
    path("product/<int:id>/", views.product_detail, name="product_detail"),
    path("product/<int:id>/edit/", views.product_edit, name="product_edit"),
    path("product/<int:id>/delete/", views.product_delete, name="product_delete"),
    path("add-category/", views.add_category, name="add_category"),
    path("category/delete/<int:id>/", views.delete_category, name="delete_category"),
]
