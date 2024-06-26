import django
from datetime import datetime
from django.shortcuts import render, redirect
from .utils import  save_vendor_to_database, process_uploaded_file_iaa,process_uploaded_file_vendor, change_to_float_uplift
from .utils import  reconcile_data_occ_less_than_vendor
from .utils import reconcile_data_occ_equal_vendor, reconcile_data_occ_greater_than_vendor
from reconapp.models import  Result, DetailResult,MissingInvoiceInVendor
from django.contrib.auth.decorators import login_required
from vendorapp.models import AgentName
import pandas as pd


# Create your views here.
@login_required
def index(request):
    missing_data_vendor=[]
    missing_data_iaa=[]
    missing_invoice_vendor=[]
    missing_invoice_iaa=[]
    fuel_iaa=None
    fuel_vendor=None
    total_iaa=0
    total_vendor=0
    total_selisih=0
    
    
    if request.method == 'POST' and request.FILES['file_iaa'] and request.FILES['file_vendor']:
        file_iaa = request.FILES['file_iaa']
        file_vendor = request.FILES['file_vendor']
        data_start_date = request.POST.get("date_of_data")  
        data_end_date=request.POST.get("end_date_data")  
        vendor = request.POST.get("vendor")

        
        # ambil nama file yang diupload
        file_iaa_name = file_iaa.name
        file_vendor_name = file_vendor.name
        
        #proses file yang diupload
        df_iaa= process_uploaded_file_iaa(file_iaa, request)
        df_vendor=process_uploaded_file_vendor(file_vendor, request)
        
        if df_iaa is None or df_vendor is None:
            return redirect('index')
        
        #simpan data dari DataFrame ke database
        fuel_iaa=save_vendor_to_database(df_iaa, request)
        fuel_vendor=save_vendor_to_database(df_vendor, request)
        
        # ubah tipe data dan cari total uplift dari data fuel_iaa dan fuel_vendor
        total_iaa, total_vendor = change_to_float_uplift(fuel_iaa, fuel_vendor)
        # cari selisih total uplift dari data fuel_iaa dan fuel_vendor
        total_selisih = total_iaa - total_vendor
        
        if fuel_iaa is not None and fuel_vendor is not None:
            # cari panjang data fuel_iaa dan fuel_vendor
            len_fuel_iaa = len(fuel_iaa)
            len_fuel_vendor = len(fuel_vendor)
            #jika panjang data fuel_iaa dan fuel_vendor sama
            if len_fuel_iaa == len_fuel_vendor:
                # panggil fungsi reconcile_data_occ_equal_vendor
                missing_data_vendor, missing_data_iaa, missing_invoice_vendor, missing_invoice_iaa = reconcile_data_occ_equal_vendor(fuel_iaa, fuel_vendor,missing_data_vendor, missing_data_iaa, missing_invoice_vendor, missing_invoice_iaa)
            elif len_fuel_iaa > len_fuel_vendor:
                # panggil fungsi reconcile_data_occ_greater_than_vendor
                missing_data_vendor, missing_data_iaa,  missing_invoice_vendor,missing_invoice_iaa = reconcile_data_occ_greater_than_vendor(fuel_iaa, fuel_vendor, missing_data_vendor, missing_data_iaa,  missing_invoice_vendor,missing_invoice_iaa)
            elif len_fuel_iaa < len_fuel_vendor:
                missing_data_vendor, missing_data_iaa, missing_invoice_vendor,missing_invoice_iaa = reconcile_data_occ_less_than_vendor(fuel_iaa, fuel_vendor, missing_data_vendor, missing_data_iaa, missing_invoice_vendor,missing_invoice_iaa)
        
        result_obj = Result.objects.create(
            time_of_event=datetime.now(),  
            data_start_date=data_start_date,
            data_end_date=data_end_date,
            total_uplift_in_lts_occ=total_iaa,
            total_uplift_in_lts_ven=total_vendor,
            total_selisih=total_selisih,
            fuel_agent=vendor,
        )
        
        detail_result_objects=[]
        if missing_data_vendor and missing_data_iaa:
            for i in range(len(missing_data_vendor)):
                # Konversi format tanggal dari DD/MM/YYYY ke YYYY-MM-DD untuk tanggal occ
                date_iaa_formatted = datetime.strptime(missing_data_iaa[i]["Date"], "%d/%m/%Y").strftime("%Y-%m-%d")
                # Konversi format tanggal dari YYYY-MM-DD ke YYYY-MM-DD untuk tanggal vendor (jika belum dalam format yang benar)
                date_ven_formatted = (
                    missing_data_vendor[i].Date.strftime("%Y-%m-%d")
                    if isinstance(missing_data_vendor[i].Date, datetime)
                    else missing_data_vendor[i].Date
                )
                # Membuat objek DetailResult dan menghubungkannya dengan Result
                detail_result_obj = DetailResult(
                    result=result_obj,
                    date_occ=date_iaa_formatted,
                    flight_occ=missing_data_iaa[i]["Flight"],
                    departure_occ=missing_data_iaa[i]["Dep"],
                    arrival_occ=missing_data_iaa[i]["Arr"],
                    registration_occ=missing_data_iaa[i]["Reg"],
                    uplift_in_lts_occ=missing_data_iaa[i]["Uplift_in_Lts"],
                    date_ven=date_ven_formatted,
                    flight_ven=missing_data_vendor[i].Flight,
                    departure_ven=missing_data_vendor[i].Dep,
                    arrival_ven=missing_data_vendor[i].Arr,
                    registration_ven=missing_data_vendor[i].Reg,
                    uplift_in_lts_ven=missing_data_vendor[i].Uplift_in_Lts,
                    invoice_no=missing_data_vendor[i].Invoice,
                    fuel_agent=missing_data_vendor[i].Vendor,
                    selisih=missing_data_iaa[i]["Uplift_in_Lts"] - missing_data_vendor[i].Uplift_in_Lts,
                )
                detail_result_objects.append(detail_result_obj)
                # Menyimpan semua objek DetailResult ke database
            DetailResult.objects.bulk_create(detail_result_objects)
            
        missing_invoice_in_vendor_objects=[]
        if missing_invoice_vendor:
            for i in range(len(missing_invoice_vendor)):
                date_formated = (
                    missing_invoice_vendor[i].Date.strftime("%Y-%m-%d")
                    if isinstance(missing_invoice_vendor[i].Date, datetime)
                    else missing_invoice_vendor[i].Date
                )
                # Membuat objek MissingInvoice dan menyimpannya ke database
                missing_invoice_obj = MissingInvoiceInVendor(
                    result=result_obj,
                    date=date_formated,
                    flight=missing_invoice_vendor[i].Flight,
                    departure=missing_invoice_vendor[i].Dep,
                    arrival=missing_invoice_vendor[i].Arr,
                    registration=missing_invoice_vendor[i].Reg,
                    uplift_in_lts=missing_invoice_vendor[i].Uplift_in_Lts,
                    invoice_no=missing_invoice_vendor[i].Invoice,  
                    fuel_agent=missing_invoice_vendor[i].Vendor,
                )
                missing_invoice_in_vendor_objects.append(missing_invoice_obj)
            MissingInvoiceInVendor.objects.bulk_create(missing_invoice_in_vendor_objects)

        return redirect('result',)

    user = request.user
    fuel_agent_name=AgentName.objects.all()
    context = {
        "page_title": "Home",
        "user": user,
        "fuel_agent_names": fuel_agent_name,
    }
    return render(request, "index.html", context)




# def index2(request):
#     context = {}
#     missing_data_vendor = [] # List untuk menyimpan data yang tidak sama antara vendor dan occ
#     missing_data_occ = [] # List untuk menyimpan data yang tidak sama antara vendor dan occ
#     missing_invoice_vendor = [] # List untuk menyimpan invoice yang tidak ada di data occ
#     missing_invoice_occ = [] # List untuk menyimpan invoice yang tidak ada di data vendor padahal di occ ada
#     successful_invoices = [] # List untuk menyimpan invoice yang berhasil diinputkan ke database
#     failed_invoices = [] # List untuk menyimpan invoice yang sudah ada di database
#     fuel_vendor = None
#     fuel_occ = None
#     total_occ = 0
#     total_vendor = 0
#     total_selisih = 0
#     data_start_date = None
#     data_end_date = None
    
#     if request.method == "POST" :
#         # memeriksa validate form
#         if 'file' in request.FILES and (request.FILES['file'].name.endswith('.xlsx') or request.FILES['file'].name.endswith('.csv')) and request.POST.get("date_of_data") is not None:
#             # Mendapatkan file yang diunggah dari form
#             uploaded_file = request.FILES["file"]
#             # Proses file yang diunggah
#             df = process_uploaded_file(uploaded_file, request)
#             if df is None:
#                 return redirect('index')
#             # Menyimpan data dari DataFrame ke database
#             fuel_vendor=saveVendorToDatabase(df, request, failed_invoices, successful_invoices)
#             data_start_date = request.POST.get("date_of_data")  
#             data_end_date=request.POST.get("end_date_data")  
#             vendor = request.POST.get("vendor")
#             fuel_occ = get_data_occ(data_start_date, data_end_date, vendor)
#             total_occ, total_vendor = change_data_fuel(fuel_occ, fuel_vendor)
#             total_selisih =   total_occ - total_vendor

#             if fuel_occ is not None and fuel_vendor is not None:
#                 # cari panjang data fuel_occ dan fuel_vendor
#                 len_fuel_occ = len(fuel_occ)
#                 len_fuel_vendor = len(fuel_vendor)

#                 # jika panjang data fuel_occ dan fuel_vendor sama,
#                 if len_fuel_occ == len_fuel_vendor:
#                     # panggil fungsi reconcile_data_occ_equal_vendor
#                     missing_data_vendor, missing_data_occ, missing_invoice_vendor, missing_invoice_occ = reconcile_data_occ_equal_vendor(fuel_occ, fuel_vendor, missing_data_vendor, missing_data_occ, missing_invoice_vendor, missing_invoice_occ)
                        
#                 elif len_fuel_occ > len_fuel_vendor:
#                     # panggil fungsi reconcile_data_occ_greater_than_vendor
#                     missing_data_vendor, missing_data_occ, missing_invoice_occ,missing_invoice_vendor = reconcile_data_occ_greater_than_vendor(fuel_occ, fuel_vendor, missing_data_vendor, missing_data_occ, missing_invoice_occ,missing_invoice_vendor)

#                 elif len_fuel_occ < len_fuel_vendor:                            
#                     missing_data_vendor, missing_data_occ, missing_invoice_vendor,missing_invoice_occ = reconcile_data_occ_less_than_vendor(fuel_occ, fuel_vendor, missing_data_vendor, missing_data_occ, missing_invoice_vendor,missing_invoice_occ)                            
                            
#             result_obj = Result.objects.create(
#                 time_of_event=datetime.now(),  
#                 data_start_date=data_start_date,
#                 data_end_date=data_end_date,
#                 total_uplift_in_lts_occ=total_occ,
#                 total_uplift_in_lts_ven=total_vendor,
#                 total_selisih=total_selisih,
#                 fuel_agent=vendor,
#             )

#             detail_result_objects = []

#             if missing_data_vendor and missing_data_occ:
#                 for i in range(len(missing_data_vendor)):
#                     # Konversi format tanggal dari DD/MM/YYYY ke YYYY-MM-DD untuk tanggal occ
#                     date_occ_formatted = datetime.strptime(missing_data_occ[i]["Date"], "%d/%m/%Y").strftime("%Y-%m-%d")

#                         # Konversi format tanggal dari YYYY-MM-DD ke YYYY-MM-DD untuk tanggal vendor (jika belum dalam format yang benar)
#                     date_ven_formatted = (
#                         missing_data_vendor[i].Date.strftime("%Y-%m-%d")
#                         if isinstance(missing_data_vendor[i].Date, datetime)
#                         else missing_data_vendor[i].Date
#                     )

#                         # Membuat objek DetailResult dan menghubungkannya dengan Result
#                     detail_result_obj = DetailResult(
#                         result=result_obj,
#                         date_occ=date_occ_formatted,
#                         flight_occ=missing_data_occ[i]["Flight"],
#                         departure_occ=missing_data_occ[i]["Dep"],
#                         arrival_occ=missing_data_occ[i]["Arr"],
#                         registration_occ=missing_data_occ[i]["Reg"],
#                         uplift_in_lts_occ=missing_data_occ[i]["Uplift_in_Lts"],
#                         date_ven=date_ven_formatted,
#                         flight_ven=missing_data_vendor[i].Flight,
#                         departure_ven=missing_data_vendor[i].Dep,
#                         arrival_ven=missing_data_vendor[i].Arr,
#                         registration_ven=missing_data_vendor[i].Reg,
#                         uplift_in_lts_ven=missing_data_vendor[i].Uplift_in_Lts,
#                         invoice_no=missing_data_vendor[i].Invoice,
#                         fuel_agent=missing_data_vendor[i].Vendor,
#                         selisih=missing_data_occ[i]["Uplift_in_Lts"] - missing_data_vendor[i].Uplift_in_Lts,
#                     )
#                     detail_result_objects.append(detail_result_obj)

#                     # Menyimpan semua objek DetailResult ke database
#                 DetailResult.objects.bulk_create(detail_result_objects)                

#             missing_invoice_in_vendor_objects=[]
            
#             if missing_invoice_vendor:
#                 for i in range(len(missing_invoice_vendor)):
#                     date_formated = (
#                         missing_invoice_vendor[i].Date.strftime("%Y-%m-%d")
#                         if isinstance(missing_invoice_vendor[i].Date, datetime)
#                         else missing_invoice_vendor[i].Date
#                     )
                    
#                     # Membuat objek MissingInvoice dan menyimpannya ke database
#                     missing_invoice_obj = MissingInvoiceInVendor(
#                         result=result_obj,
#                         date=date_formated,
#                         flight=missing_invoice_vendor[i].Flight,
#                         departure=missing_invoice_vendor[i].Dep,
#                         arrival=missing_invoice_vendor[i].Arr,
#                         registration=missing_invoice_vendor[i].Reg,
#                         uplift_in_lts=missing_invoice_vendor[i].Uplift_in_Lts,
#                         invoice_no=missing_invoice_vendor[i].Invoice,  
#                         fuel_agent=missing_invoice_vendor[i].Vendor,
#                     )
#                     missing_invoice_in_vendor_objects.append(missing_invoice_obj)                    
#                 MissingInvoiceInVendor.objects.bulk_create(missing_invoice_in_vendor_objects)
                        
#         return redirect('result') 

#     # ambil user yang login
#     user = request.user
#     #ambil data FuelAgentName dari database
#     fuel_agent_name = AgentName.objects.all()
    
#     context = {
#         "page_title": "Home",
#         "user": user,
#         "fuel_agent_names": fuel_agent_name,
#     }
#     return render(request, "index.html", context)





def handler404(request, exception):
    return render(request, 'error/404.html', status=404)


