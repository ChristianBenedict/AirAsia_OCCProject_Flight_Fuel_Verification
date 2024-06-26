
import re
import gspread
import pandas as pd
from datetime import datetime
from django.contrib import messages
from vendorapp.models import FuelVendor
from occapp.models import FuelIaa
from oauth2client.service_account import ServiceAccountCredentials




def to_dict(instance): # ini berguna untuk mengubah data dari instance menjadi dictionary
    return {
        'Date': str(instance.Date),
        'Flight': instance.Flight,
        'Dep': instance.Dep,
        'Arr': instance.Arr,
        'Reg': instance.Reg,
        'Uplift_in_Lts': instance.Uplift_in_Lts,
        'Invoice': instance.Invoice,
        'Vendor': instance.Vendor,
    }
    

# yang baru


def process_uploaded_file_iaa(uploaded_file_iaa, request):
    try:
        if uploaded_file_iaa.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file_iaa, dtype='str')
        elif uploaded_file_iaa.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file_iaa, dtype='str')
        else:
            raise ValueError("Format file tidak didukung.")
    except Exception as e:
        raise ValueError("Gagal membaca file: " + str(e))
    
    required_columns = ["Date", "Flight", "Dep", "Arr", "Reg", "Uplift_in_Lts", "Invoice"]
    
    # Memeriksa apakah semua kolom yang diperlukan ada dalam dataframe
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        messages.error(request, "Pastikan Semua Atribut Berikut Ada Pada File: " + ', '.join(missing_columns))
        return None
    df = df[required_columns]
    df.columns = ["Date", "Flight", "Dep", "Arr", "Reg", "Uplift_in_Lts", "Invoice"]

    # Cek apakah kolom 'Date' sudah memiliki tipe data datetime
    for index, row in df.iterrows():
        if isinstance(row['Date'], datetime):
            continue
        else:
            # Konversi tanggal ke format yang benar
            date_str = str(row['Date'])
            if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', date_str):
                date_str = date_str.split()[0]
                if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                    date_str = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
                elif re.match(r'\d{2}-\d{2}-\d{4}', date_str):
                    date_str = datetime.strptime(date_str, "%d-%m-%Y").strftime("%d/%m/%Y")
                elif re.match(r'\d{2}/\d{2}/\d{4}', date_str):
                    date_str = date_str
            elif re.match(r'\d{4}/\d{2}/\d{2}', date_str):
                date_str = date_str.replace('/', '-')
            elif re.match(r'\d{2}/\d{2}/\d{4}', date_str):
                date_str = datetime.strptime(date_str, "%d/%m/%Y").strftime("%d/%m/%Y")
            else:
                messages.error(request, f"Format tanggal tidak valid: {date_str}")
                continue
            df.at[index, 'Date'] = date_str

    # Konversi kolom 'Date' ke tipe data datetime
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
    return df


def process_uploaded_file_vendor(uploaded_vendor, request):
    try:
        if uploaded_vendor.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_vendor, dtype='str')
        elif uploaded_vendor.name.endswith('.csv'):
            df = pd.read_csv(uploaded_vendor, dtype='str')
        else:
            raise ValueError("Format file tidak didukung.")
    except Exception as e:
        raise ValueError("Gagal membaca file: " + str(e))
    
    required_columns = ["Date", "Flight", "Dep", "Arr", "Reg", "Uplift_in_Lts", "Invoice"]
    
    # Memeriksa apakah semua kolom yang diperlukan ada dalam dataframe
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        messages.error(request, "Pastikan Semua Atribut Berikut Ada Pada File: " + ', '.join(missing_columns))
        return None
        
    df = df[required_columns]
    df.columns = ["Date", "Flight", "Dep", "Arr", "Reg", "Uplift_in_Lts", "Invoice"]

    # Cek apakah kolom 'Date' sudah memiliki tipe data datetime
    for index, row in df.iterrows():
        if isinstance(row['Date'], datetime):
            continue
        else:
            # Konversi tanggal ke format yang benar
            date_str = str(row['Date'])
            if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', date_str):
                date_str = date_str.split()[0]
                if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                    date_str = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
                elif re.match(r'\d{2}-\d{2}-\d{4}', date_str):
                    date_str = datetime.strptime(date_str, "%d-%m-%Y").strftime("%d/%m/%Y")
                elif re.match(r'\d{2}/\d{2}/\d{4}', date_str):
                    date_str = date_str
            elif re.match(r'\d{4}/\d{2}/\d{2}', date_str):
                date_str = date_str.replace('/', '-')
            elif re.match(r'\d{2}/\d{2}/\d{4}', date_str):
                date_str = datetime.strptime(date_str, "%d/%m/%Y").strftime("%d/%m/%Y")
            else:
                messages.error(request, f"Format tanggal tidak valid: {date_str}")
                continue
            df.at[index, 'Date'] = date_str

    # Konversi kolom 'Date' ke tipe data datetime
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
    return df



def save_vendor_to_database(df, request):
    new_invoices=[]
    """Menyimpan data dari DataFrame ke database."""
    fuel_vendor_list = []
    # Menyimpan data ke database
    for index, row in df.iterrows():
        # ambil vendor dari request.POST
        vendor = request.POST.get("vendor")
        fuel_vendor = FuelVendor(
            Date=row["Date"],
            Flight=row["Flight"],
            Dep=row["Dep"],
            Arr=row["Arr"],
            Reg=row["Reg"],
            Uplift_in_Lts=float(row["Uplift_in_Lts"]),
            Invoice=str(row["Invoice"]),
            Vendor=vendor,
        )  # Membuat objek FuelVendor
        # sebelum menyimpan data, cek apakah data sudah ada di database, cek berdasarkan Invoice
        if FuelVendor.objects.filter(Invoice=row["Invoice"]).exists():
            new_invoices.append(fuel_vendor)
        else:
            fuel_vendor_list.append(fuel_vendor)
            new_invoices.append(fuel_vendor)
    # Menyimpan semua objek fuel_vendor dalam satu transaksi
    FuelVendor.objects.bulk_create(fuel_vendor_list)
    return new_invoices



def save_iaa_to_database(df, request):
    new_invoices=[]
    """Menyimpan data dari DataFrame ke database."""
    fuel_iaa_list = []
    # Menyimpan data ke database
    for index, row in df.iterrows():
        # ambil vendor dari request.POST
        vendor = request.POST.get("vendor")
        fuel_iaa = FuelIaa(
            Date=row["Date"],
            Flight=row["Flight"],
            Dep=row["Dep"],
            Arr=row["Arr"],
            Reg=row["Reg"],
            Uplift_in_Lts=float(row["Uplift_in_Lts"]),
            Invoice=str(row["Invoice"]),
            Vendor=vendor,
        )  # Membuat objek FuelIaa

        # sebelum menyimpan data, cek apakah data sudah ada di database, cek berdasarkan Invoice
        if FuelIaa.objects.filter(Invoice=row["Invoice"]).exists():
            new_invoices.append(fuel_iaa)
        else:
            fuel_iaa_list.append(fuel_iaa)
            new_invoices.append(fuel_iaa)
    # Menyimpan semua objek fuel_vendor dalam satu transaksi
    FuelIaa.objects.bulk_create(fuel_iaa_list)
    return new_invoices


def change_to_float_uplift(fuel_iaa, fuel_vendor):
    total_iaa = 0
    total_vendor = 0
    # Ubah tipe data Uplift_in_Lts menjadi float dan jumlahkan semua Uplift_in_Lts dari fuel_vendor
    for i in range(len(fuel_vendor)):
        fuel_vendor[i].Invoice = fuel_vendor[i].Invoice.strip()
        fuel_vendor[i].Uplift_in_Lts = float(fuel_vendor[i].Uplift_in_Lts)
        total_vendor += fuel_vendor[i].Uplift_in_Lts
        
    # Ubah tipe data Uplift_in_Lts menjadi float dan jumlahkan semua Uplift_in_Lts dari fuel_iaa
    for i in range(len(fuel_iaa)):
        fuel_iaa[i].Invoice = fuel_iaa[i].Invoice.strip()
        fuel_iaa[i].Uplift_in_Lts = float(fuel_iaa[i].Uplift_in_Lts)
        total_iaa += fuel_iaa[i].Uplift_in_Lts
    return total_iaa, total_vendor


# fungsi rekonsiliasi data jika len_fuel_iaa dan len_fuel_vendor sama
def reconcile_data_occ_equal_vendor(fuel_iaa, fuel_vendor, missing_data_vendor, missing_data_iaa, missing_invoice_vendor, missing_invoice_iaa):
    # Ambil set invoice untuk fuel_iaa dan fuel_vendor
    fuel_iaa_invoices = set(item.Invoice for item in fuel_iaa)
    fuel_vendor_invoices = set(item.Invoice for item in fuel_vendor)

    # Temukan invoice yang ada di fuel_iaa tetapi tidak ada di fuel_vendor
    missing_invoices_vendor = fuel_iaa_invoices - fuel_vendor_invoices

    # Temukan invoice yang ada di fuel_vendor tetapi tidak ada di fuel_iaa
    missing_invoices_iaa = fuel_vendor_invoices - fuel_iaa_invoices

    # Masukkan missing invoices ke dalam list masing-masing
    missing_invoice_iaa = [item for item in fuel_iaa if item.Invoice in missing_invoices_iaa]
    missing_invoice_vendor = [item for item in fuel_vendor if item.Invoice in missing_invoices_vendor]

    # Lakukan iterasi melalui set invoice yang ada di fuel_iaa_invoices
    for invoice in fuel_iaa_invoices:
        # Jika invoice ada di fuel_vendor_invoices
        if invoice in fuel_vendor_invoices:
            # Bandingkan data
            occ_item = next((item for item in fuel_iaa if item.Invoice == invoice), None)
            vendor_item = next((item for item in fuel_vendor if item.Invoice == invoice), None)
            if occ_item and vendor_item and occ_item.Uplift_in_Lts != vendor_item.Uplift_in_Lts:
                # Jika data tidak sama, masukkan ke dalam list missing_data
                missing_data_vendor.append(vendor_item)
                missing_data_iaa.append(occ_item)
        else:
            # Jika invoice tidak ada di fuel_vendor, masukkan ke dalam list missing_invoice
            missing_invoice_iaa.append(next((item for item in fuel_iaa if item.Invoice == invoice), None))

    # Jika ada invoice yang ada di fuel_vendor tetapi tidak ada di fuel_iaa
    for invoice in missing_invoices_iaa:
        missing_invoice_vendor.append(next((item for item in fuel_vendor if item.Invoice == invoice), None))
    
    return missing_data_vendor, missing_data_iaa, missing_invoice_vendor, missing_invoice_iaa

# Fungsi rekonsiliasi data jika len_fuel_iaa > len_fuel_vendor
def reconcile_data_occ_greater_than_vendor(fuel_iaa, fuel_vendor, missing_data_vendor, missing_data_iaa, missing_invoice_vendor,missing_invoices_iaa):
    # Mengambil set Invoice dari fuel_vendor
    fuel_vendor_invoices = set(item.Invoice for item in fuel_vendor)
    
    for iaa_item in fuel_iaa:
        if iaa_item.Invoice in fuel_vendor_invoices:
            # Jika Invoice ada di fuel_vendor, bandingkan data
            vendor_item = next((item for item in fuel_vendor if item.Invoice == iaa_item.Invoice), None)
            if vendor_item and iaa_item.Uplift_in_Lts != vendor_item.Uplift_in_Lts:
                missing_data_vendor.append(vendor_item)
                missing_data_iaa.append(iaa_item)
        else:
            # Jika Invoice tidak ada di fuel_vendor, tambahkan ke missing_invoices_iaa
            missing_invoices_iaa.append(iaa_item)

    # Temukan invoice yang ada di fuel_vendor tetapi tidak ada di fuel_iaa
    missing_invoices_vendor = fuel_vendor_invoices - set(item.Invoice for item in fuel_iaa)
    # Ambil detail invoice yang hilang dari fuel_vendor
    missing_invoice_vendor.extend(item for item in fuel_vendor if item.Invoice in missing_invoices_vendor)

    return missing_data_vendor, missing_data_iaa,  missing_invoice_vendor,missing_invoices_iaa,

# Fungsi rekonsiliasi data jika len_fuel_iaa < len_fuel_vendor
def reconcile_data_occ_less_than_vendor(fuel_iaa, fuel_vendor, missing_data_vendor, missing_data_iaa, missing_invoice_vendor, missing_invoice_iaa):
    # Mengambil set Invoice dari fuel_iaa
    fuel_iaa_invoices = set(item.Invoice for item in fuel_iaa)

    for vendor_item in fuel_vendor:
        if vendor_item.Invoice in fuel_iaa_invoices:
            # Jika Invoice ada di fuel_iaa, bandingkan data
            occ_item = next((item for item in fuel_iaa if item.Invoice == vendor_item.Invoice), None)
            if occ_item and occ_item.Uplift_in_Lts != vendor_item.Uplift_in_Lts:
                missing_data_vendor.append(vendor_item)
                missing_data_iaa.append(occ_item)
        else:
            # Jika Invoice tidak ada di fuel_iaa, tambahkan ke missing_invoice_vendor
            missing_invoice_vendor.append(vendor_item)

    # Temukan invoice yang ada di fuel_iaa tetapi tidak ada di fuel_vendor
    missing_invoices_occ = fuel_iaa_invoices - set(item.Invoice for item in fuel_vendor)
    # Ambil detail invoice yang hilang dari fuel_iaa
    missing_invoice_iaa.extend(item for item in fuel_iaa if item.Invoice in missing_invoices_occ)

    return missing_data_vendor, missing_data_iaa, missing_invoice_vendor, missing_invoice_iaa     
   
