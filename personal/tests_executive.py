from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import Executive, Person


def create_person(name, lastname):
    """Create a Person with the given information."""
    return Person.objects.create(
        person_name=name,
        person_lastname=lastname)


def create_executive(name, lastname, comssn):
    """
    Create a Person with the given information, then creae Executive
    with reference to just created Person.
    """
    person = create_person(name, lastname)
    return Executive.objects.create(
        person=person,
        executive_comssn=comssn)


class ExecutiveViewTests(TestCase):
    def test_executive_view_with_no_executives(self):
        """
        If no Executives exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('personal:executives'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No executives are available.")
        self.assertQuerysetEqual(response.context['latest_executive_list'], [])

    def test_executive_view_with_an_executive(self):
        """If an Executive exists, it should be displayed."""
        create_executive(name="John", lastname="Smith", comssn=10)
        response = self.client.get(reverse('personal:executives'))
        self.assertQuerysetEqual(
            response.context['latest_executive_list'],
            ['<Executive: Smith, John>']
        )

    def test_executive_view_with_two_executives(self):
        """If two or more Executives exist, they should be displayed."""
        create_executive(name="John", lastname="Smith", comssn=10)
        create_executive(name="Mark", lastname="Twain", comssn=20)
        response = self.client.get(reverse('personal:executives'))
        self.assertQuerysetEqual(
            response.context['latest_executive_list'].order_by('executive_comssn'),
            ['<Executive: Smith, John>', '<Executive: Twain, Mark>']
        )
