from django.urls import path
from .views import *

urlpatterns = [
    path('login',LoginView.as_view(),name='login'),
    path('registration',RegistrationView.as_view(),name='registration')
]
