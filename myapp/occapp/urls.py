from django.urls import path
from . import views as occ_views

app_name = 'occapp'

urlpatterns = [
    path('', occ_views.index, name='index'),
    
]