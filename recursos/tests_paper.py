from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import Paper


def create_paper(name, width, length, price):
    """Create a Paper with the given information."""
    return Paper.objects.create(
        paper_name=name,
        paper_width=width,
        paper_length=length,
        paper_price=price)


class PaperViewTests(TestCase):
    def test_paper_view_with_no_papers(self):
        """
        If no Papers exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('recursos:papers'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No papers are available.")
        self.assertQuerysetEqual(
            response.context['latest_paper_list'], [])

    def test_paper_view_with_a_paper(self):
        """If a Paper exists, it should be displayed."""
        create_paper(name="Temp", width=13, length=19, price=2)
        response = self.client.get(reverse('recursos:papers'))
        self.assertQuerysetEqual(
            response.context['latest_paper_list'],
            ['<Paper: Temp (13.00\" x 19.00\")>']
        )

    def test_paper_view_with_two_papers(self):
        """If two or more Papers exist, they should be displayed."""
        create_paper(name="Temp1", width=13, length=19, price=2)
        create_paper(name="Temp2", width=12.5, length=18.75, price=4)
        response = self.client.get(reverse('recursos:papers'))
        self.assertQuerysetEqual(
            response.context['latest_paper_list'].order_by('paper_name'),
            ['<Paper: Temp1 (13.00\" x 19.00\")>',
                '<Paper: Temp2 (12.50\" x 18.75\")>']
        )
