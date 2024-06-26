# Register your models here.
from django.contrib import admin
from .models import FuelVendor, AgentName

@admin.register(FuelVendor)
class FuelVendorAdmin(admin.ModelAdmin):
    list_display = ('Date', 'Flight', 'Dep', 'Arr', 'Reg', 'Uplift_in_Lts', 'Invoice', 'Vendor')
    search_fields = ('Date', 'Flight', 'Dep', 'Arr', 'Reg', 'Uplift_in_Lts', 'Invoice', 'Vendor')
    ordering = ['Date', 'Flight', 'Dep', 'Arr', 'Reg', 'Uplift_in_Lts', 'Invoice', 'Vendor']
    
@admin.register(AgentName)  
class FuelAgentAdmin(admin.ModelAdmin):
    list_display = ('fuel_agent_name',)
    search_fields = ('fuel_agent_name',)
    ordering = ['fuel_agent_name']



