from django.contrib import admin
from django.urls import path, include
from myapp.views import index
from reconapp.views import result as result
from reconapp.views import history as history 

handler404 = 'myapp.views.handler404'
admin.site.site_header = "Fuel Reconciliation System "
admin.site.site_title = "FRS Administration"


urlpatterns = [

    path('admin/', admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    path("accounts/", include("django.contrib.auth.urls")),  
    
    path('', index, name='index'),
    path('result/', result, name='result'),
    path('history/',history, name='history'),
    path('vendor/', include('vendorapp.urls', namespace='vendorapp')),
    path('iaa/', include('occapp.urls', namespace='occapp')),
    
]


