from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import Material


def create_material(name, price):
    """Create a Material with the given information."""
    return Material.objects.create(
        material_name=name,
        material_price=price)


class MaterialViewTests(TestCase):
    def test_material_view_with_no_materials(self):
        """
        If no Materials exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('recursos:materials'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No materials are available.")
        self.assertQuerysetEqual(
            response.context['latest_material_list'], [])

    def test_material_view_with_a_material(self):
        """If a Material exists, it should be displayed."""
        create_material(name="Temp", price=2)
        response = self.client.get(reverse('recursos:materials'))
        self.assertQuerysetEqual(
            response.context['latest_material_list'],
            ['<Material: Temp>']
        )

    def test_material_view_with_two_materials(self):
        """If two or more Materials exist, they should be displayed."""
        create_material(name="Temp1", price=2)
        create_material(name="Temp2", price=4)
        response = self.client.get(reverse('recursos:materials'))
        self.assertQuerysetEqual(
            response.context['latest_material_list'].order_by('material_name'),
            ['<Material: Temp1>', '<Material: Temp2>']
        )
