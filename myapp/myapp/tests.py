import os
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import User
from myapp.utils import reconcile_data_occ_equal_vendor, get_data_from_sheet
from vendorapp.models import AgentName
from reconapp.models import DetailResult, MissingInvoiceInVendor, Result
from  vendorapp.models import FuelVendor

class MyAppTests(TestCase):
    def setUp(self):
        # Membuat user dan login
        self.client = Client()
        self.user = User.objects.create_user(username='user05', password='Django123')
        self.client.login(username='user05', password='Django123')

        # Membuat data FuelAgentName
        AgentName.objects.create(fuel_agent_name="Test Vendor")

    @patch('myapp.views.process_uploaded_file')
    @patch('myapp.views.saveVendorToDatabase')
    @patch('myapp.views.get_data_occ')
    @patch('myapp.views.change_data_fuel')
    @patch('myapp.views.reconcile_data_occ_equal_vendor')
    def test_index_post(self, mock_reconcile, mock_change_data_fuel, mock_get_data_occ, mock_saveVendorToDatabase, mock_process_uploaded_file):
        # Mocking functions
        mock_process_uploaded_file.return_value = MagicMock()
        mock_saveVendorToDatabase.return_value = MagicMock()
        mock_get_data_occ.return_value = MagicMock()
        mock_change_data_fuel.return_value = (100, 80)
        mock_reconcile.return_value = ([], [], [], [])

        # Path to your test file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, 'static', 'file', 'pertamina_februari.xlsx')

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('index'), {
                'file': file,
                'date_of_data': '2024-02-01',
                'end_date_data': '2024-02-29',
                'vendor': 'Pertamina'
            })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('result'))

    def test_index_get(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertContains(response, 'Home')

    @patch('myapp.utils.get_data_from_sheet')
    def test_get_data_from_google_sheet(self, mock_get_data):
        mock_get_data.return_value = [
            {"Invoice": "INV001", "Uplift_in_Lts": 100.0, "Date": "01/01/2024", "Flight": "FL001", "Dep": "DEP1", "Arr": "ARR1", "Reg": "REG1", "Fuel_Agent": "AgentA"},
        ]
        data = mock_get_data('VendorA', '2024-01-01', '2024-01-31')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['Invoice'], 'INV001')


    def test_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'user05',
            'password': 'Django123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))

    def test_logout(self):
        # Login terlebih dahulu
        self.client.login(username='user05', password='Django123')

        # Pastikan user sudah login
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

        # Logout menggunakan metode POST
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))


