from .models import FuelIaa
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def index(request):
    try:
        fuel_iaas = FuelIaa.objects.all()
        total_uplift_in_lts = sum(fuel_iaa.Uplift_in_Lts for fuel_iaa in fuel_iaas)
        
        page_title = 'Fuel by IAA'

        context = {
            'fuel_iaas': fuel_iaas,
            'page_title': page_title,
            'total_uplift_in_lts': total_uplift_in_lts,
        }
    except Exception as e:
        return render(request, 'error/error.html', {'error_message': str(e)})
    
    return render(request, 'occapp/fuel_iaa_list.html', context)



