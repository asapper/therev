from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import Order, Order_Process, Process
from .utility import OrderController


class OrderSetUpClass(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.OK_STATUS = 200
        cls.NOT_FOUND_STATUS = 404
        cls.NOT_ALLOWED_STATUS = 405
        cls.ENCODING = "utf-8"
        # process instances
        cls.p_trim = Process.objects.create(
            process_name="Trim")
        cls.p_print = Process.objects.create(
            process_name="Print")

    @classmethod
    def create_order(cls, op_number, client, description, quantity,
                     sheets, processes, machine="CP1000"):
        """Create an Order with the given information."""
        order = Order.objects.create(
            order_op_number=op_number,
            order_client=client,
            order_description=description,
            order_machine=machine,
            order_quantity=quantity,
            order_total_sheets=sheets)
        # create Order_Process
        for process in processes:
            Order_Process.objects.create(
                order=order,
                process=process)
        return order


class OrderViewTests(OrderSetUpClass):
    @classmethod
    def setUpTestData(cls):
        super(OrderViewTests, cls).setUpTestData()
        cls.INDEX_ONE = 1
        cls.BAD_INDEX = 100
        # messages
        cls.PROCESS_ALREADY_STARTED_MSG = "Process already started"
        cls.PROCESS_NOT_STARTED_MSG = "Process not started"
        cls.PROCESS_ALREADY_FINISHED_MSG = "Process already finished"

    def setUp(self):
        self.order = self.create_order(
            op_number='23456-1',
            client='Test Cliente',
            description='Producto 1',
            quantity=200,
            sheets=50,
            processes=[self.p_trim, self.p_print])

    def test_order_view_with_no_orders(self):
        """If no Orders exist, an appropriate message should be displayed."""
        self.order.delete()  # clear db
        response = self.client.get(reverse('control_produccion:orders'))
        self.assertEqual(response.status_code, self.OK_STATUS)
        self.assertContains(response, "No hay órdenes hábiles.")
        self.assertQuerysetEqual(response.context['latest_order_list'], [])

    def test_order_view_with_an_order(self):
        """If an Order exists, it should be displayed."""
        # access detail page
        response = self.client.get(reverse('control_produccion:orders'))
        self.assertQuerysetEqual(
            response.context['latest_order_list'],
            [("<Order: OP: 23456-1; Cliente: Test Cliente; Descripción: Producto 1>")])

    def test_cannot_access_start_process_page(self):
        """
        If accessing Start Process page through a GET request
        a 405 error should be returned.
        """
        response = self.client.get(reverse(
            'control_produccion:order_start_process',
            kwargs={'pk': self.order.id, 'process_id': self.INDEX_ONE}))
        self.assertEqual(response.status_code, self.NOT_ALLOWED_STATUS)

    def test_access_start_process_page_of_nonexisting_order(self):
        """
        Attempt to access the Start Process page of an Order
        that does not exist.
        """
        response = self.client.post(reverse(
            'control_produccion:order_start_process',
            kwargs={'pk': self.BAD_INDEX, 'process_id': self.INDEX_ONE}))
        self.assertEqual(response.status_code, self.NOT_FOUND_STATUS)

    def test_access_start_process_page_of_nonexisting_process(self):
        """
        Attempt to access the Start Process page of a valid Order
        with a Process that does not exist.
        """
        response = self.client.post(reverse(
            'control_produccion:order_start_process',
            kwargs={'pk': self.order.id, 'process_id': self.BAD_INDEX}))
        self.assertEqual(response.status_code, self.NOT_FOUND_STATUS)

    def test_access_start_process_page_of_process_already_started(self):
        """
        Attempt to access the Start Process page of a Process
        already started.
        """
        # get first process
        process = self.order.get_processes()[0]
        # get OrderProcess
        o_proc = Order_Process.objects.get(
            order_id=self.order.id,
            process_id=process.id)
        # start process
        OrderController.start_process(o_proc)
        # acces start process page
        response = self.client.post(reverse(
            'control_produccion:order_start_process',
            kwargs={'pk': self.order.id, 'process_id': process.id}),
            follow=True)  # follow redirection
        self.assertEqual(response.status_code, self.OK_STATUS)
        self.assertIn(
            self.PROCESS_ALREADY_STARTED_MSG,
            response.content.decode(self.ENCODING))

    def test_cannot_access_finish_process_page(self):
        """
        If accessing Finish Process page through a GET request
        a 405 error should be returned.
        """
        response = self.client.get(reverse(
            'control_produccion:order_finish_process',
            kwargs={'pk': self.order.id, 'process_id': self.INDEX_ONE}))
        self.assertEqual(response.status_code, self.NOT_ALLOWED_STATUS)

    def test_access_finish_process_page_of_nonexisting_order(self):
        """
        Attempt to access the Finish Process page of an Order
        that does not exist.
        """
        response = self.client.post(reverse(
            'control_produccion:order_finish_process',
            kwargs={'pk': self.BAD_INDEX, 'process_id': self.INDEX_ONE}))
        self.assertEqual(response.status_code, self.NOT_FOUND_STATUS)

    def test_access_finish_process_page_of_nonexisting_process(self):
        """
        Attempt to access the Finish Process page of a valid Order
        with a Process that does not exist.
        """
        response = self.client.post(reverse(
            'control_produccion:order_finish_process',
            kwargs={'pk': self.order.id, 'process_id': self.BAD_INDEX}))
        self.assertEqual(response.status_code, self.NOT_FOUND_STATUS)

    def test_access_finish_process_page_of_process_not_started(self):
        """
        Attempt to access the Finish Process page of a Process
        not started.
        """
        # get first process
        process = self.order.get_processes()[0]
        # acces finish process page
        response = self.client.post(reverse(
            'control_produccion:order_finish_process',
            kwargs={'pk': self.order.id, 'process_id': process.id}),
            follow=True)  # follow redirection
        self.assertEqual(response.status_code, self.OK_STATUS)
        self.assertIn(
            self.PROCESS_NOT_STARTED_MSG,
            response.content.decode(self.ENCODING))

    def test_access_finish_process_page_of_process_already_finished(self):
        """
        Attempt to access the Finish Process page of a Process
        already finished.
        """
        # get first process
        process = self.order.get_processes()[0]
        # get OrderProcess
        o_proc = Order_Process.objects.get(
            order_id=self.order.id,
            process_id=process.id)
        # start process
        OrderController.start_process(o_proc)
        # finish process
        OrderController.finish_process(o_proc)
        # acces start process page
        response = self.client.post(reverse(
            'control_produccion:order_finish_process',
            kwargs={'pk': self.order.id, 'process_id': process.id}),
            follow=True)  # follow redirection
        self.assertEqual(response.status_code, self.OK_STATUS)
        self.assertIn(
            self.PROCESS_ALREADY_FINISHED_MSG,
            response.content.decode(self.ENCODING))


class OrderDetailViewTests(OrderSetUpClass):
    def test_correct_order_detail_view(self):
        """Test that page is loaded correctly."""
        order = self.create_order(
            op_number='23456-1',
            client='Test Cliente',
            description='Producto 1',
            quantity=200,
            sheets=50,
            processes=[self.p_trim, self.p_print])
        # access detail page
        response = self.client.get(
            reverse('control_produccion:order_detail',
                    kwargs={'pk': order.id}))
        self.assertEqual(response.status_code, self.OK_STATUS)

    def test_not_existent_order_detail_page(self):
        """
        Test that a 404 is returned when accessing the detail page
        of an order that does not exist.
        """
        BAD_ORDER_ID = 100
        response = self.client.get(
            reverse('control_produccion:order_detail',
                    kwargs={'pk': BAD_ORDER_ID}))
        self.assertEqual(response.status_code, self.NOT_FOUND_STATUS)
