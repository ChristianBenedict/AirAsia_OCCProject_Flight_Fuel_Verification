from django.contrib import admin
from .models import FuelIaa

# Register your models here.
@admin.register(FuelIaa)
class FuelIaaAdmin(admin.ModelAdmin):
    list_display = ('Date', 'Flight', 'Dep', 'Arr', 'Reg', 'Uplift_in_Lts', 'Invoice', 'Vendor')
    search_fields = ('Date', 'Flight', 'Dep', 'Arr', 'Reg', 'Uplift_in_Lts', 'Invoice', 'Vendor')
    ordering = ['Date', 'Flight', 'Dep', 'Arr', 'Reg', 'Uplift_in_Lts', 'Invoice', 'Vendor']