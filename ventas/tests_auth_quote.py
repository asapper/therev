import datetime

from django.test import TestCase
from .tests_quote import QuoteSetUpClass

from .models import AuthorizedQuote, Quote


class AuthorizedQuoteMethodTests(QuoteSetUpClass, TestCase):
    @classmethod
    def setUpTestData(cls):
        super(AuthorizedQuoteMethodTests, cls).setUpTestData()
        quote = Quote.objects.get(pk=cls.quote_instance.id)
        cls.auth_quote_instance = quote.authorize_quote()

    def test_get_quote_id(self):
        """Create and authorize a Quote, and get its id."""
        quote = Quote.objects.get(pk=self.quote_instance.id)
        auth_quote = self.auth_quote_instance
        self.assertEquals(auth_quote.get_quote_id(), quote.id)

    def test_get_due_date(self):
        """Create and authorize a Quote, and get its due date."""
        # create quote with due date: today
        in_seven_days = self.due_today + datetime.timedelta(days=7)
        quote_future = self.create_quote(
            name="Quote2", due_date=in_seven_days, copies=20,
            product_name="Prueba2", width=10, length=18, bleed=0.1, sides=1,
            colors_front=4, colors_back=4, materials=[self.m_print],
            finishings=[self.f_trim])
        # authorized quote already exists in db
        auth_quote_today = self.auth_quote_instance
        # authorize quotes and retrieve authorized quotes
        auth_quote_future = quote_future.authorize_quote()
        # check method: get_quote_due_date()
        self.assertEqual(auth_quote_today.get_due_date(), self.due_today)
        self.assertTrue(quote_future.quote_is_authorized)
        self.assertEqual(auth_quote_future.get_due_date(), in_seven_days)

    def test_get_client(self):
        """Create and authorize a quote, and get its client."""
        auth_quote = self.auth_quote_instance
        self.assertEquals(auth_quote.get_client(), self.client_instance)

    def test_get_executive(self):
        """Create and authorize a quote, and get its executive."""
        auth_quote = self.auth_quote_instance
        self.assertEquals(auth_quote.get_executive(), self.executive_instance)

    def test_get_finishings(self):
        """Create and authorize a quote, and get its finishings."""
        # store finishings to use
        finishings = [self.f_trim, self.f_fold, self.f_blunt]
        # create quote
        quote = self.create_quote(
            name="Quote2", due_date=self.due_today, copies=20,
            product_name="Prueba2", width=10, length=18, bleed=0.1, sides=1,
            colors_front=4, colors_back=4, materials=[self.m_print],
            finishings=finishings)
        # authorize quote
        auth_quote = quote.authorize_quote()
        self.assertSequenceEqual(auth_quote.get_finishings(), finishings)

    def test_get_materials(self):
        """Create and authorize a quote, and get its materials."""
        # store materials to use
        materials = [self.m_print, self.m_varnish, self.m_foil]
        # create quote
        quote = self.create_quote(
            name="Quote2", due_date=self.due_today, copies=20,
            product_name="Prueba2", width=10, length=18, bleed=0.1, sides=1,
            colors_front=4, colors_back=4, materials=materials,
            finishings=[self.f_trim])
        # authorize quote
        auth_quote = quote.authorize_quote()
        self.assertSequenceEqual(auth_quote.get_materials(), materials)

    def test_get_paper(self):
        """Create and authorize a quote, and get its paper."""
        auth_quote = self.auth_quote_instance
        self.assertEquals(auth_quote.get_paper(), self.paper_instance)

    def test_create_order(self):
        """
        Create and authorize a Quote, as well as an Order based on that Quote.
        """
        quote = Quote.objects.get(pk=self.quote_instance.id)
        # data used for creating an Order
        pack_inst = "None"
        delivery_addr = "123 ave"
        notes = "Due soon!"
        # authorize quote and create Order
        quote.authorize_quote()
        auth_quote = AuthorizedQuote.objects.get(quote_id=quote.id)
        auth_quote.create_order(pack_inst, delivery_addr, notes)
        quote = Quote.objects.get(pk=quote.id)  # refresh instance
        self.assertTrue(quote.quote_is_authorized)
        self.assertTrue(quote.quote_is_approved)
