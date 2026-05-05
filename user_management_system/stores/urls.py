from django.urls import path
from . import views

app_name = 'stores'

urlpatterns = [
    path('my-stores/', views.store_list_user, name='store_list_user'),
    path('my-stores/create/', views.create_store, name='create_store'),
    path('my-stores/<int:store_id>/', views.store_detail, name='store_detail'),
    path('my-stores/<int:store_id>/edit/', views.edit_store, name='edit_store'),
    path('my-stores/<int:store_id>/delete/', views.store_delete, name='store_delete'),

    path('manage-stores/', views.manage_stores, name='manage_stores'),
    path('store-requests/', views.store_requests, name='store_requests'),
    path('store/<int:store_id>/approve/', views.approve_store, name='approve_store'),
    path('store/<int:store_id>/reject/', views.reject_store, name='reject_store'),
    path('store/<int:store_id>/admin-detail/', views.store_detail_admin, name='store_detail_admin'),
    path('store/<int:store_id>/verify/', views.verify_store, name='verify_store'),

    path('', views.store_list, name='store_list'),
    path('categories/', views.categories_all, name='categories_all'),
    path('categories/<str:category_name>/', views.category_products_by_name, name='category_products_by_name'),
    path('offers/', views.offers_list, name='offers_list'),
    path('my/', views.my_store_front, name='my_store_front'),
    path('<int:store_id>/', views.store_front, name='store_front'),

    path('<int:store_id>/categories/', views.store_categories, name='store_categories'),
    path('<int:store_id>/category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('<int:store_id>/category/add/', views.add_category, name='add_category'),
    path('<int:store_id>/category/<int:category_id>/delete/', views.delete_category, name='delete_category'),

    path('<int:store_id>/product/add/', views.add_product, name='add_product'),
    path('<int:store_id>/product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('<int:store_id>/product/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('<int:store_id>/product/<int:product_id>/delete/', views.product_delete, name='product_delete'),

    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('store/<int:store_id>/purchase/<int:product_id>/', views.purchase_product, name='purchase_product'),
    path('store/<int:store_id>/add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('my-store/sales/', views.store_sales, name='store_sales'),

    path('favorites/', views.favorite_products, name='favorite_products'),
    path('toggle-favorite-product/<int:product_id>/', views.toggle_favorite_product, name='toggle_favorite_product'),
    path('store/<int:store_id>/rate/', views.rate_store, name='rate_store'),
    path('product/<int:product_id>/rate/', views.rate_product, name='rate_product'),
    path('store/<int:store_id>/offers/', views.store_offers, name='store_offers'),
]
