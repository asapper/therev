from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import Order, Order_Process, Process


class OrderSetUpClass(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.OK_STATUS = 200
        cls.NOT_FOUND_STATUS = 404
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
    def test_order_view_with_no_orders(self):
        """If no Orders exist, an appropriate message should be displayed."""
        response = self.client.get(reverse('control_produccion:orders'))
        self.assertEqual(response.status_code, self.OK_STATUS)
        self.assertContains(response, "No hay órdenes hábiles.")
        self.assertQuerysetEqual(response.context['latest_order_list'], [])

    def test_order_view_with_an_order(self):
        """If an Order exists, it should be displayed."""
        order = self.create_order(
            op_number='23456-1',
            client='Test Cliente',
            description='Producto 1',
            quantity=200,
            sheets=50,
            processes=[self.p_trim, self.p_print])
        # access detail page
        response = self.client.get(reverse('control_produccion:orders'))
        self.assertQuerysetEqual(
            response.context['latest_order_list'],
            [("<Order: OP: 23456-1; Cliente: Test Cliente; Descripción: Producto 1>")])

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
