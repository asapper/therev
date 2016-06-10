import datetime

from django.core.urlresolvers import reverse
from django.test import TestCase

from .forms import OrderForm
from .models import Quote
from .tests_quote import QuoteSetUpClass
from .utility import OrderController, QuoteController


class OrderSetUpClass(QuoteSetUpClass, TestCase):
    @classmethod
    def setUpTestData(cls):
        super(OrderSetUpClass, cls).setUpTestData()
        cls.pack_inst = "None."
        cls.delivery_addr = "123 ave"
        cls.notes = "Due soon!"
        # store HTTP response statuses
        cls.OK_STATUS = 200
        cls.NOT_FOUND_STAUS = 404
        cls.NOT_ALLOWED_STATUS = 405


class OrderMethodTests(OrderSetUpClass, TestCase):
    @classmethod
    def setUpTestData(cls):
        super(OrderMethodTests, cls).setUpTestData()
        quote = Quote.objects.get(pk=cls.quote_instance.id)
        QuoteController.authorize_quote(quote)
        cls.order_instance = OrderController.create_order(
            quote, cls.pack_inst, cls.delivery_addr, cls.notes)

    def test_get_quote_id(self):
        """
        Create a Quote, authorize it, create a Quote from it,
        and get its quote id.
        """
        order = self.order_instance
        self.assertEqual(order.get_quote_id(), self.quote_instance.id)

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
        QuoteController.authorize_quote(quote_future)
        # create orders (today order already exists)
        order_today = self.order_instance
        order_future = OrderController.create_order(
            quote_future, self.pack_inst, self.delivery_addr, self.notes)
        # check method: get_quote_due_date()
        self.assertEqual(order_today.get_due_date(), self.due_today)
        self.assertEqual(order_future.get_due_date(), in_seven_days)

    def test_get_client(self):
        """
        Create and authorize a quote, create an order based on
        that quote, and get its client.
        """
        order = self.order_instance
        self.assertEqual(order.get_client(), self.client_instance)

    def test_get_executive(self):
        """
        Create and authorize a quote, create an order based on
        that quote, and get its executive.
        """
        order = self.order_instance
        self.assertEqual(order.get_executive(), self.executive_instance)

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
        QuoteController.authorize_quote(quote)
        # create order
        order = OrderController.create_order(
            quote, self.pack_inst, self.delivery_addr, self.notes)
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
        QuoteController.authorize_quote(quote)
        # create order
        order = OrderController.create_order(
            quote, self.pack_inst, self.delivery_addr, self.notes)
        self.assertSequenceEqual(order.get_materials(), materials)

    def test_get_paper(self):
        """
        Create and authorize a quote, create an order based on
        that quote, and get its paper.
        """
        order = self.order_instance
        self.assertEqual(order.get_paper(), self.paper_instance)


class OrderCreateFormTests(OrderSetUpClass, TestCase):
    @classmethod
    def setUpTestData(cls):
        super(OrderCreateFormTests, cls).setUpTestData()
        cls.REQ_MSG = "This field is required."
        # store data to be used in forms
        cls.order_data = {
            'order_packaging_instructions': 'Pack in groups of 50.',
            'order_delivery_address': '987 ave.',
            'order_notes': 'Due very soon!',
        }

    def test_blank_form(self):
        """Test for a blank form. Expect an error."""
        form = OrderForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['order_packaging_instructions'], [self.REQ_MSG])
        self.assertEqual(
            form.errors['order_delivery_address'], [self.REQ_MSG])
        self.assertEqual(form.errors['order_notes'], [self.REQ_MSG])

    def test_valid_full_form(self):
        """Test that a fully-filled form is valid."""
        form = OrderForm(data=self.order_data)
        self.assertTrue(form.is_valid())

    def test_form_no_pack_inst(self):
        """
        Test a form with no text input for packaging instructions.
        Expect an error.
        """
        temp_data = self.order_data.copy()
        temp_data['order_packaging_instructions'] = ""  # blank
        form = OrderForm(data=temp_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['order_packaging_instructions'], [self.REQ_MSG])
        self.assertNotIn('order_delivery_address', form.errors)
        self.assertNotIn('order_notes', form.errors)

    def test_form_no_delivery_address(self):
        """
        Test a form with no text input for delivery address.
        Expect an error.
        """
        temp_data = self.order_data.copy()
        temp_data['order_delivery_address'] = ""  # blank address
        form = OrderForm(data=temp_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['order_delivery_address'], [self.REQ_MSG])
        self.assertNotIn('order_packaging_instructions', form.errors)
        self.assertNotIn('order_notes', form.errors)

    def test_form_no_notes(self):
        """Test a form with no text input for notes. Expect an error."""
        temp_data = self.order_data.copy()
        temp_data['order_notes'] = ""  # blank notes
        form = OrderForm(data=temp_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['order_notes'], [self.REQ_MSG])
        self.assertNotIn('order_packaging_instructions', form.errors)
        self.assertNotIn('order_delivery_address', form.errors)

    def test_form_too_long_delivery_address(self):
        """
        Test a form with input text too long for delivery address.
        Expect an error.
        """
        LIMIT_CHARS = 255
        ERROR_MSG = (
            "Ensure this value has at most {} characters "
            "(it has {}).").format(LIMIT_CHARS, LIMIT_CHARS+1)
        temp_data = self.order_data.copy()
        temp_data['order_delivery_address'] = 'a' * (LIMIT_CHARS + 1)  # long
        form = OrderForm(data=temp_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['order_delivery_address'], [ERROR_MSG])
        self.assertNotIn('order_packaging_instructions', form.errors)
        self.assertNotIn('order_notes', form.errors)


class OrderViewTests(OrderSetUpClass, TestCase):
    @classmethod
    def setUpTestData(cls):
        super(OrderViewTests, cls).setUpTestData()
        cls.INDEX_ONE = 1
        cls.BAD_INDEX = 100

    def test_order_view_with_no_orders(self):
        """If no Orders exist, an appropriate message should be displayed."""
        response = self.client.get(reverse('ventas:orders'))
        self.assertEqual(response.status_code, self.OK_STATUS)
        self.assertContains(response, "No orders are available.")
        self.assertQuerysetEqual(response.context['latest_order_list'], [])

    def test_order_view_with_an_order(self):
        """If an Order exists, it should be displayed."""
        # create an order
        quote = Quote.objects.get(pk=self.quote_instance.id)
        QuoteController.authorize_quote(quote)
        OrderController.create_order(
            quote, self.pack_inst, self.delivery_addr, self.notes)
        # access orders list view
        response = self.client.get(reverse('ventas:orders'))
        self.assertQuerysetEqual(
            response.context['latest_order_list'],
            [("<Order: Id: 1; Started: False; Finished: False>")])

    def test_cannot_access_start_order_page(self):
        """
        If accessing /ventas/orders/X/start a 405 error should be returned.
        """
        # create an order
        quote = Quote.objects.get(pk=self.quote_instance.id)
        QuoteController.authorize_quote(quote)
        order = OrderController.create_order(
            quote, self.pack_inst, self.delivery_addr, self.notes)
        # attempt to access start page
        response = self.client.get(reverse(
            'ventas:order_start', kwargs={'pk': order.id}))
        self.assertEqual(response.status_code, self.NOT_ALLOWED_STATUS)

    def test_access_start_order_page_of_nonexisting_order(self):
        """
        Attempt to access the Start Order page of an order that does not exist.
        """
        # attempt to access start page
        response = self.client.post(reverse(
            'ventas:order_start', kwargs={'pk': self.BAD_INDEX}))
        self.assertEqual(response.status_code, self.NOT_FOUND_STAUS)

    def test_cannot_access_start_finishing_page(self):
        """
        If accessing /ventas/orders/X/start_finishing/Y/ a
        405 error should be returned.
        """
        # create an order
        quote = Quote.objects.get(pk=self.quote_instance.id)
        QuoteController.authorize_quote(quote)
        order = OrderController.create_order(
            quote, self.pack_inst, self.delivery_addr, self.notes)
        OrderController.start_order(order)  # start order
        # attemp to access start finishing page
        response = self.client.get(reverse(
            'ventas:order_start_finishing',
            kwargs={'pk': order.id, 'finishing_id': self.INDEX_ONE}))
        self.assertEqual(response.status_code, self.NOT_ALLOWED_STATUS)

    def test_access_start_finishing_of_unstarted_order(self):
        """
        Attempt to access the Start Finishing page of an order
        that has not been started.
        """
        quote = Quote.objects.get(pk=self.quote_instance.id)
        QuoteController.authorize_quote(quote)
        order = OrderController.create_order(
            quote, self.pack_inst, self.delivery_addr, self.notes)
        # attemp to access start finishing page
        response = self.client.post(reverse(
            'ventas:order_start_finishing',
            kwargs={'pk': order.id, 'finishing_id': self.BAD_INDEX}))
        self.assertEqual(response.status_code, self.NOT_FOUND_STAUS)

    def test_access_start_finishing_of_nonexisting_order(self):
        """
        Attempt to access the Start Finishing page of an
        order that does not exist.
        """
        # attempt to access start page
        response = self.client.post(reverse(
            'ventas:order_start_finishing',
            kwargs={'pk': self.BAD_INDEX, 'finishing_id': self.INDEX_ONE}))
        self.assertEqual(response.status_code, self.NOT_FOUND_STAUS)

    def test_access_start_finishing_of_nonexisting_finishing(self):
        """
        Attempt to access the Start Finishing page of an order
        that exists but where the desired Finishing does not exist.
        """
        # create an order
        quote = Quote.objects.get(pk=self.quote_instance.id)
        QuoteController.authorize_quote(quote)
        order = OrderController.create_order(
            quote, self.pack_inst, self.delivery_addr, self.notes)
        OrderController.start_order(order)  # start order
        # attemp to access start finishing page
        response = self.client.post(reverse(
            'ventas:order_start_finishing',
            kwargs={'pk': order.id, 'finishing_id': self.BAD_INDEX}))
        self.assertEqual(response.status_code, self.NOT_FOUND_STAUS)

    def test_cannot_access_finish_finishing_page(self):
        """
        If accessing /ventas/orders/X/finish_finishing/Y/ a
        405 error should be returned.
        """
        # create an order
        quote = Quote.objects.get(pk=self.quote_instance.id)
        QuoteController.authorize_quote(quote)
        order = OrderController.create_order(
            quote, self.pack_inst, self.delivery_addr, self.notes)
        OrderController.start_order(order)  # start order
        # attemp to access start finishing page
        response = self.client.get(reverse(
            'ventas:order_finish_finishing',
            kwargs={'pk': order.id, 'finishing_id': self.INDEX_ONE}))
        self.assertEqual(response.status_code, self.NOT_ALLOWED_STATUS)

    def test_access_finish_finishing_of_unstarted_order(self):
        """
        Attempt to access the Finish Finishing page of an order
        that has not been started.
        """
        quote = Quote.objects.get(pk=self.quote_instance.id)
        QuoteController.authorize_quote(quote)
        order = OrderController.create_order(
            quote, self.pack_inst, self.delivery_addr, self.notes)
        # attemp to access start finishing page
        response = self.client.post(reverse(
            'ventas:order_finish_finishing',
            kwargs={'pk': order.id, 'finishing_id': self.BAD_INDEX}))
        self.assertEqual(response.status_code, self.NOT_FOUND_STAUS)

    def test_access_finish_finishing_of_nonexisting_order(self):
        """
        Attempt to access the Finish Finishing page of an
        order that does not exist.
        """
        # attempt to access start page
        response = self.client.post(reverse(
            'ventas:order_finish_finishing',
            kwargs={'pk': self.BAD_INDEX, 'finishing_id': self.INDEX_ONE}))
        self.assertEqual(response.status_code, self.NOT_FOUND_STAUS)

    def test_access_finish_finishing_of_nonexisting_finishing(self):
        """
        Attempt to access the Finish Finishing page of an order
        that exists but where the desired Finishing does not exist.
        """
        # create an order
        quote = Quote.objects.get(pk=self.quote_instance.id)
        QuoteController.authorize_quote(quote)
        order = OrderController.create_order(
            quote, self.pack_inst, self.delivery_addr, self.notes)
        OrderController.start_order(order)  # start order
        # attemp to access start finishing page
        response = self.client.post(reverse(
            'ventas:order_finish_finishing',
            kwargs={'pk': order.id, 'finishing_id': self.BAD_INDEX}))
        self.assertEqual(response.status_code, self.NOT_FOUND_STAUS)


class OrderDetailViewTests(OrderSetUpClass, TestCase):
    def test_order_detail_view(self):
        """Test that data is displayed correctly."""
        # authorize and approve quote in db
        quote = Quote.objects.get(pk=self.quote_instance.id)
        QuoteController.authorize_quote(quote)
        OrderController.create_order(
            quote, self.pack_inst, self.delivery_addr, self.notes)
        # access order detail page
        response = self.client.get(
            reverse('ventas:order_detail', kwargs={'pk': quote.id}))
        self.assertEqual(response.status_code, self.OK_STATUS)

    def test_not_existent_order_detail_page(self):
        """
        Test that a 404 is returned when accessing the detail page of an
        order that does not exist.
        """
        BAD_QUOTE_ID = 100
        response = self.client.get(
            reverse('ventas:order_detail', kwargs={'pk': BAD_QUOTE_ID}))
        self.assertEqual(response.status_code, self.NOT_FOUND_STAUS)


class OrderCreateViewTests(OrderSetUpClass, TestCase):
    def test_not_existent_order_create_page(self):
        """
        Test that a 404 is returned when accessing the create page
        of an order that does not exist.
        """
        BAD_QUOTE_ID = 100
        response = self.client.get(
            reverse('ventas:quote_approve', kwargs={'pk': BAD_QUOTE_ID}))
        self.assertEqual(response.status_code, self.NOT_FOUND_STAUS)
