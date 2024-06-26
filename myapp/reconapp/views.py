from django.shortcuts import render
from .models import  Result, DetailResult ,MissingInvoiceInVendor
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required



@login_required
def history(request):
    page_title = 'History'
    total_missing_invoices_in_vendor = 0
    total_missing_invoices_in_occ = 0
    total_selisih_fuel = 0
    start_date = request.GET.get("start-date")
    end_date = request.GET.get("end-date")
    fuel_agent = request.GET.get("fuel-agent")

    try:
        if start_date and end_date and fuel_agent:
            detail_results = DetailResult.objects.filter(
                date_occ__gte=start_date, date_occ__lte=end_date, fuel_agent=fuel_agent
            )
            missing_invoices_in_vendor = MissingInvoiceInVendor.objects.filter(
                date__gte=start_date, date__lte=end_date, fuel_agent=fuel_agent
            )
        elif start_date and end_date:
            detail_results = DetailResult.objects.filter(
                date_occ__gte=start_date, date_occ__lte=end_date
            )
            missing_invoices_in_vendor = MissingInvoiceInVendor.objects.filter(
                date__gte=start_date, date__lte=end_date
            )

        elif start_date:
            detail_results = DetailResult.objects.filter(
                date_occ=start_date
            )
            missing_invoices_in_vendor = MissingInvoiceInVendor.objects.filter(
                date=start_date
            )
        else:
            # ambil data dari detail result
            detail_results = DetailResult.objects.all()
            # ambil data dari missing invoices in vendor
            missing_invoices_in_vendor = MissingInvoiceInVendor.objects.all()

        # ambil total_missing_invoices_in_vendor
        total_missing_invoices_in_vendor = sum(item.uplift_in_lts for item in missing_invoices_in_vendor)
        # buat total selisih dari jumlah kolom selisih pada detail result
        total_selisih_fuel = sum(item.selisih for item in detail_results)
        # ambil total_missing_invoices_in_occ

        context = {
            'page_title': page_title,
            'detail_results': detail_results,
            'total_selisih_fuel': total_selisih_fuel,
            'missing_invoices_in_vendor': missing_invoices_in_vendor,
            'total_missing_invoices_in_vendor': total_missing_invoices_in_vendor,
        }
    except Exception as e:
        return render(request, 'error/error.html', {'error_message': str(e)})
    return render(request, 'recon/history_list.html', context)




@login_required
def result(request):
    try:
        total_selisih=0
        # Mengambil entri terbaru dari model Result
        latest_result = Result.objects.latest('time_of_event')
        # Mengambil detail result yang terkait dengan entri terbaru dari Result
        latest_detail_results = latest_result.detail_results.all()
        # ambil total selisih dari jumlah  kolom selisih pada detail result
        total_selisih = sum(item.selisih for item in latest_detail_results)
        # ambil jumlah detail result
        detail_result_count = get_latest_result_detail_count()
        missing_invoice_vendor_count = get_latest_missing_invoices_in_vendor_count()
        
        try:
            latest_missing_invoices_in_vendor = latest_result.missing_invoices_in_vendor.all()
        except Exception as e:
            latest_missing_invoices_in_vendor = None
        # buat total_missing_invoices_in_vendor
        total_missing_invoices_in_vendor = 0
        if latest_missing_invoices_in_vendor:
            for item in latest_missing_invoices_in_vendor:
                total_missing_invoices_in_vendor += item.uplift_in_lts

        
        if request.method == "POST" and 'export_pdf' in request.POST:  
            template_path = 'recon/topdf.html' 
            context = {
                'latest_result': latest_result,
                'latest_detail_results': latest_detail_results,
                'latest_missing_invoices_in_vendor': latest_missing_invoices_in_vendor,
                'total_missing_invoices_in_vendor': total_missing_invoices_in_vendor,
                'detail_result_count': detail_result_count,
                'missing_invoice_vendor_count': missing_invoice_vendor_count,
            }
            # Render template
            html_string = render_to_string(template_path, context)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="data_export.pdf"'
            # Create PDF
            pisa_status = pisa.CreatePDF(html_string, dest=response)
            if pisa_status.err:
                return HttpResponse('Terjadi kesalahan saat membuat PDF: %s' % pisa_status.err)
            return response
        else:  
            context = {
                'page_title': 'Result',
                'latest_result': latest_result,
                'latest_detail_results': latest_detail_results,
                'total_selisih': total_selisih,
                'latest_missing_invoices_in_vendor': latest_missing_invoices_in_vendor,
                'total_missing_invoices_in_vendor': total_missing_invoices_in_vendor,
                'detail_result_count': detail_result_count,
                'missing_invoice_vendor_count': missing_invoice_vendor_count,
            }
        return render(request, 'recon/result.html', context)
    except Exception as e:
        return render(request, 'error/error.html', {'error_message': str(e)})



def get_latest_result_detail_count():
    try:
        latest_result = Result.objects.latest('time_of_event')
        detail_result_count = DetailResult.objects.filter(result=latest_result).count()
    except Result.DoesNotExist:
        detail_result_count = 0
    return detail_result_count

# untuk mendapatkan jumlah missing invoice in vendor dari entri terbaru dari Result
def get_latest_missing_invoices_in_vendor_count():
    try:
        latest_result = Result.objects.latest('time_of_event')
        missing_invoices_in_vendor_count = MissingInvoiceInVendor.objects.filter(result=latest_result).count()
    except Result.DoesNotExist:
        missing_invoices_in_vendor_count = 0
    return missing_invoices_in_vendor_count
    