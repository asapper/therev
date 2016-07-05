import datetime

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils import timezone
from django.test import TestCase

from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from .models import Order_Process
from .tests_order import OrderSetUpClass
from .utility import OrderController


class SeleniumTestsSetUpClass(OrderSetUpClass):
    @classmethod
    def setUpClass(cls):
        super(SeleniumTestsSetUpClass, cls).setUpClass()
        cls.driver = WebDriver()
        cls.TIMEOUT = 2
        # create user
        cls.user_password = "00000000"
        cls.user = User.objects.create_user(
            username="tmp2",
            password=cls.user_password)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super(SeleniumTestsSetUpClass, cls).tearDownClass()


class SeleniumOrderTests(SeleniumTestsSetUpClass, StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super(SeleniumOrderTests, cls).setUpClass()
        cls.INDEX_ONE = 1
        cls.START_PROCESS_BTN_ID = "popover-start-process"
        cls.FINISH_PROCESS_BTN_ID = "popover-finish-process"

    def setUp(self):
        self.order = self.create_order(
            op_number='12345-1',
            client='Test Cliente',
            description='Producto 1',
            quantity=200,
            sheets=50,
            processes=[self.p_trim, self.p_print])

    def test_start_process(self):
        """
        Test starting a process of an order. Verify buttons are
        displayed correctly.
        """
        # access order detail page
        self.driver.get('{}{}'.format(
            self.live_server_url,
            reverse('control_produccion:order_detail',
                    kwargs={'pk': self.order.id})))
        # wait for page to load
        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda driver: self.driver.find_element_by_tag_name('body'))
        # assert Start Process 1 button is enabled
        start_proc_btn = self.driver.find_element_by_xpath(
            '//a[@id="{}-{}"]'.format(
                self.START_PROCESS_BTN_ID, self.INDEX_ONE))
        # Start Process 1
        start_proc_btn.click()
        # wait for form to load
        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda driver: self.driver.find_element_by_tag_name('form'))
        # fill in user credentials
        username = self.driver.find_element_by_xpath("//input[@name='username']")
        username.send_keys(self.user.username)
        password = self.driver.find_element_by_xpath("//input[@name='password']")
        password.send_keys(self.user_password)
        # submit form
        submit_btn = self.driver.find_element_by_xpath("//button[@type='submit']")
        submit_btn.click()
        # assert redirected to same page
        self.assertEqual(self.driver.current_url, '{}{}'.format(
            self.live_server_url,
            reverse('control_produccion:order_detail',
                    kwargs={'pk': self.order.id})))
        # wait for page to load
        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda driver: self.driver.find_element_by_tag_name('body'))
        # assert Finish Process 1 button is enabled
        finish_proc_btn = self.driver.find_element_by_xpath(
            '//a[@id="{}-{}"]'.format(
                self.FINISH_PROCESS_BTN_ID, self.INDEX_ONE))


class SeleniumAnalyticsStatsTests(
        SeleniumTestsSetUpClass, StaticLiveServerTestCase):
    def test_avg_process_times(self):
        """Test that the average time shown is per unit of quantity."""
        # create two identical orders
        order_one = self.create_order(
            '12345', 'Test Client', 'Prueba', 100, 100,
            [self.p_trim, self.p_print])
        order_two = self.create_order(
            '67890', 'Test Client', 'Prueba', 10, 100, [self.p_trim])
        # store times
        now = timezone.now()
        fifteen_min_ago = now - datetime.timedelta(minutes=15)
        thirty_min_ago = now - datetime.timedelta(minutes=30)
        hour_ago = now - datetime.timedelta(minutes=60)
        # set start of process one (order one) to one hour ago
        o_proc_one = Order_Process.objects.get(
            order=order_one, process=self.p_trim)
        o_proc_one.order_process_datetime_started = hour_ago
        o_proc_one.order_process_is_started = True
        # set finish of process one (order one) to now
        o_proc_one.order_process_datetime_finished = now
        o_proc_one.order_process_is_finished = True
        o_proc_one.save()
        # set start of process two (order one) to 30min ago
        o_proc_two = Order_Process.objects.get(
            order=order_one, process=self.p_print)
        o_proc_two.order_process_datetime_started = thirty_min_ago
        o_proc_two.order_process_is_started = True
        # set finish of process two (order one) to now
        o_proc_two.order_process_datetime_finished = now
        o_proc_two.order_process_is_finished = True
        o_proc_two.save()
        # set start of process one (order two) to 15min ago
        o_proc_three = Order_Process.objects.get(
            order=order_two, process=self.p_trim)
        o_proc_three.order_process_datetime_started = fifteen_min_ago
        o_proc_three.order_process_is_started = True
        # set finish of process one (order two) to now
        o_proc_three.order_process_datetime_finished = now
        o_proc_three.order_process_is_finished = True
        o_proc_three.save()
        # go to analytics page
        self.driver.get('{}{}'.format(
            self.live_server_url, reverse('control_produccion:analytics')))
        # wait for page to load
        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda driver: self.driver.find_element_by_tag_name('body'))
        # get elements in table
        table = self.driver.find_element_by_id('avgProcessTimes')
        cells = table.find_elements_by_tag_name('td')
        # assert time/unit for process one is X
        for index, cell in enumerate(cells):
            if index == 0:
                self.assertEqual(cell.text, self.p_trim.process_name)
            elif index == 1:
                self.assertEqual(cell.text, '1.05')
            elif index == 2:
                self.assertEqual(cell.text, self.p_print.process_name)
            else:
                self.assertEqual(cell.text, '0.30')
