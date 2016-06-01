import datetime

from django.test import TestCase

from .models import Quote
from .models import AuthorizedQuote
from .tests_quote import QuoteSetUpClass


class OrderMethodTests(QuoteSetUpClass, TestCase):
    @classmethod
    def setUpTestData(cls):
        super(OrderMethodTests, cls).setUpTestData()
        cls.pack_inst = "None."
        cls.delivery_addr = "123 ave"
        cls.notes = "Due soon!"
        quote = Quote.objects.get(pk=cls.quote_instance.id)
        quote.authorize_quote()
        auth_quote = AuthorizedQuote.objects.get(quote_id=quote.id)
        cls.order_instance = auth_quote.create_order(
            cls.pack_inst, cls.delivery_addr, cls.notes)

    def test_get_quote_id(self):
        """
        Create a Quote, authorize it, create a Quote from it,
        and get its quote id.
        """
        order = self.order_instance
        self.assertEquals(order.get_quote_id(), self.quote_instance.id)

    def test_get_due_date(self):
        """
        Create and authorize a Quote, create an Order based on
        that Quote, and get its due date.
        """
        # create quote with due date: future
        in_seven_days = self.due_today + datetime.timedelta(days=7)
        quote_future = self.create_quote(
            name="Quote2", due_date=in_seven_days, copies=20,
            product_name="Prueba2", width=10, length=18, bleed=0.1, sides=1,
            colors_front=4, colors_back=4, materials=[self.m_print],
            finishings=[self.f_trim])
        # authorize quotes and retrieve authorized quotes
        auth_quote_future = quote_future.authorize_quote()
        # create orders (today order already exists)
        order_today = self.order_instance
        order_future = auth_quote_future.create_order(
            self.pack_inst, self.delivery_addr, self.notes)
        # check method: get_quote_due_date()
        self.assertEqual(order_today.get_due_date(), self.due_today)
        self.assertEqual(order_future.get_due_date(), in_seven_days)

    def test_get_client(self):
        """
        Create and authorize a quote, create an order based on
        that quote, and get its client.
        """
        order = self.order_instance
        self.assertEquals(order.get_client(), self.client_instance)

    def test_get_executive(self):
        """
        Create and authorize a quote, create an order based on
        that quote, and get its executive.
        """
        order = self.order_instance
        self.assertEquals(order.get_executive(), self.executive_instance)

    def test_get_finishings(self):
        """
        Create and authorize a quote, create an order based on
        that quote, and get its finishings.
        """
        # store finishings to use in quote
        finishings = [self.f_trim, self.f_fold, self.f_blunt]
        # create quote
        quote = self.create_quote(
            name="Quote1", due_date=self.due_today, copies=10,
            product_name="Prueba", width=10, length=18, bleed=0.1, sides=2,
            colors_front=4, colors_back=4, materials=[self.m_print],
            finishings=finishings)
        # authorize quote
        auth_quote = quote.authorize_quote()
        # create order
        order = auth_quote.create_order(
            self.pack_inst, self.delivery_addr, self.notes)
        self.assertSequenceEqual(order.get_finishings(), finishings)

    def test_get_materials(self):
        """
        Create and authorize a quote, create an order based on
        that quote, and get its materials.
        """
        # store materials to use in quote
        materials = [self.m_print, self.m_varnish, self.m_foil]
        # create quote
        quote = self.create_quote(
            name="Quote1", due_date=self.due_today, copies=10,
            product_name="Prueba", width=10, length=18, bleed=0.1, sides=2,
            colors_front=4, colors_back=4, materials=materials,
            finishings=[self.f_trim])
        # authorize quote
        auth_quote = quote.authorize_quote()
        # create order
        order = auth_quote.create_order(
            self.pack_inst, self.delivery_addr, self.notes)
        self.assertSequenceEqual(order.get_materials(), materials)

    def test_get_paper(self):
        """
        Create and authorize a quote, create an order based on
        that quote, and get its paper.
        """
        order = self.order_instance
        self.assertEquals(order.get_paper(), self.paper_instance)
