# ReconApp/tests.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Result, DetailResult, MissingInvoiceInVendor

class ReconAppModelTests(TestCase):
    def setUp(self):
        self.result = Result.objects.create(
            data_start_date='2024-01-01',
            data_end_date='2024-01-31',
            total_uplift_in_lts_occ=1000,
            total_uplift_in_lts_ven=900,
            total_selisih=100,
            fuel_agent='Pertamina'
        )
    
    def test_result_creation(self):
        self.assertEqual(self.result.fuel_agent, 'Pertamina')
    
    def test_detail_result_creation(self):
        detail_result = DetailResult.objects.create(
            result=self.result,
            date_occ='2024-01-15',
            flight_occ='FL123',
            departure_occ='DEP',
            arrival_occ='ARR',
            registration_occ='REG123',
            uplift_in_lts_occ=500,
            date_ven='2024-01-15',
            flight_ven='FL123',
            departure_ven='DEP',
            arrival_ven='ARR',
            registration_ven='REG123',
            uplift_in_lts_ven=480,
            invoice_no='INV123',
            fuel_agent='Pertamina',
        )
        self.assertEqual(detail_result.flight_occ, 'FL123')
    
    def test_missing_invoice_creation(self):
        missing_invoice = MissingInvoiceInVendor.objects.create(
            result=self.result,
            date='2024-01-15',
            flight='FL123',
            departure='DEP',
            arrival='ARR',
            registration='REG123',
            uplift_in_lts=100,
            invoice_no='INV123',
            fuel_agent='Pertamina'
        )
        self.assertEqual(missing_invoice.flight, 'FL123')

class ReconAppViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='user05', password='Django123')
        self.client.login(username='user05', password='Django123')

        self.result = Result.objects.create(
            data_start_date='2024-01-01',
            data_end_date='2024-01-31',
            total_uplift_in_lts_occ=1000,
            total_uplift_in_lts_ven=900,
            total_selisih=100,
            fuel_agent='Pertamina'
        )

    def test_index_view(self):
        response = self.client.get(reverse('history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recon/history_list.html')
        self.assertContains(response, 'History')

    def test_result_view(self):
        response = self.client.get(reverse('result'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recon/result.html')
    
    
