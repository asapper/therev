from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import Client

def create_client(name, address, nit):
    """Create a client with the given information."""
    return Client.objects.create(
        client_name=name,
        client_receipt_name=name,
        client_receipt_address=address,
        client_nit=nit)


class ClientViewTests(TestCase):
    def test_client_view_with_no_clients(self):
        """If no Clients exist, an appropriate message should be displayed."""
        response = self.client.get(reverse('personal:clients'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No clients are available.")
        self.assertQuerysetEqual(response.context['latest_client_list'], [])

    def test_client_view_with_a_client(self):
        """If a Client exists, it should be displayed."""
        create_client(name="Temp", address="123 ave", nit=1234)
        response = self.client.get(reverse('personal:clients'))
        self.assertQuerysetEqual(
            response.context['latest_client_list'],
            ['<Client: Temp>']
        )

    def test_client_view_with_two_clients(self):
        """If two or more Clients exists, they should be displayed."""
        create_client(name="Temp1", address="123 ave", nit=1234)
        create_client(name="Temp2", address="456 ave", nit=5678)
        response = self.client.get(reverse('personal:clients'))
        self.assertQuerysetEqual(
            response.context['latest_client_list'].order_by('client_name'),
            ['<Client: Temp1>', '<Client: Temp2>']
        )
