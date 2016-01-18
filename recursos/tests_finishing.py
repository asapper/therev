from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import Finishing


def create_finishing(name, price):
    """Create a Finishing with the given information."""
    return Finishing.objects.create(
        finishing_name=name,
        finishing_price=price)


class FinishingViewTests(TestCase):
    def test_finishing_view_with_no_finishings(self):
        """
        If no Finishings exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('recursos:finishings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No finishings are available.")
        self.assertQuerysetEqual(
            response.context['latest_finishing_list'], [])

    def test_finishing_view_with_a_finishing(self):
        """If a Finishing exists, it should be displayed."""
        create_finishing(name="Temp", price=2)
        response = self.client.get(reverse('recursos:finishings'))
        self.assertQuerysetEqual(
            response.context['latest_finishing_list'],
            ['<Finishing: Temp>']
        )

    def test_finishing_view_with_two_finishings(self):
        """If two or more Finishings exist, they should be displayed."""
        create_finishing(name="Temp1", price=2)
        create_finishing(name="Temp2", price=4)
        response = self.client.get(reverse('recursos:finishings'))
        self.assertQuerysetEqual(
            response.context['latest_finishing_list'].order_by(
                'finishing_name'),
            ['<Finishing: Temp1>', '<Finishing: Temp2>']
        )
