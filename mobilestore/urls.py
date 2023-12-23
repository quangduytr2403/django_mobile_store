from django.urls import path

from . import views

urlpatterns = [
    path('<int:page_index>', views.product_list, name='product_list'),
    path('search/<int:page_index>', views.product_search, name='product_search'),
    path('detail', views.product_detail, name='product_detail'),
    path('about-us', views.about_us, name='about_us'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('register', views.register, name='register'),
    path('cart/add-to-cart', views.add_to_cart, name='add_to_cart'),
    path('cart/show-cart', views.show_cart, name='show_cart'),
    path('cart/change-quantity', views.change_quantity, name='change_quantity'),
    path('cart/remove-item', views.remove_product, name='remove_product'),
    path('cart/submit-order', views.submit_order, name='submit_order'),
    path('show-history', views.show_history, name='show_history')
]
