from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import CustomerRegistrationView, VendorRegistrationView, login_redirect_view

urlpatterns = [
    path('register/customer/', CustomerRegistrationView.as_view(), name='register_customer'),
    path('register/vendor/', VendorRegistrationView.as_view(), name='register_vendor'),
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('redirect/', login_redirect_view, name='login_redirect'),
]