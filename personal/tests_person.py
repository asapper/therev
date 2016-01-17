from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import Person


def create_person(name, lastname):
    """Create a Person with the given information."""
    return Person.objects.create(
        person_name=name,
        person_lastname=lastname)


class PersonViewTests(TestCase):
    def test_person_view_with_no_persons(self):
        """
        If no Persons exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('personal:persons'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No persons available.")
        self.assertQuerysetEqual(response.context['latest_person_list'], [])

    def test_person_view_with_a_person(self):
        """If a Person exists, it should be displayed."""
        create_person(name="John", lastname="Smith")
        response = self.client.get(reverse('personal:persons'))
        self.assertQuerysetEqual(
            response.context['latest_person_list'],
            ['<Person: Smith, John>']
        )

    def test_person_view_with_two_persons(self):
        """If two or more Persons exist, they should be displayed."""
        create_person(name="John", lastname="Smith")
        create_person(name="Mark", lastname="Twain")
        response = self.client.get(reverse('personal:persons'))
        self.assertQuerysetEqual(
            response.context['latest_person_list'].order_by('person_lastname'),
            ['<Person: Smith, John>', '<Person: Twain, Mark>']
        )
