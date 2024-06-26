from .models import FuelVendor
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    try:
        fuel_vendors = FuelVendor.objects.all()
        total_uplift_in_lts = sum(fuel_vendor.Uplift_in_Lts for fuel_vendor in fuel_vendors)
        
        page_title = 'Fuel by vendor'

        context = {
            'fuel_vendors': fuel_vendors,
            'page_title': page_title,
            'total_uplift_in_lts': total_uplift_in_lts,
        }
    except Exception as e:
        return render(request, 'error/error.html', {'error_message': str(e)})
    
    return render(request, 'vendor/fuel_vendor_list.html', context)
