from django.urls import path
from . import views as vendor_views

app_name = 'vendorapp'

urlpatterns = [
    path('', vendor_views.index, name='index'),
    
]