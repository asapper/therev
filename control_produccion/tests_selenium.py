from django.core.urlresolvers import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase

from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from .tests_order import OrderSetUpClass


class SeleniumOrderTests(OrderSetUpClass, StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super(SeleniumOrderTests, cls).setUpClass()
        cls.driver = WebDriver()
        cls.INDEX_ONE = 1
        cls.TIMEOUT = 2
        cls.START_PROCESS_BTN_ID = "btn-start-process"
        cls.FINISH_PROCESS_BTN_ID = "btn-finish-process"

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super(SeleniumOrderTests, cls).tearDownClass()

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
            '//button[@id="{}-{}"]'.format(
                self.START_PROCESS_BTN_ID, self.INDEX_ONE))
        # Start Process 1
        start_proc_btn.click()
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
            '//button[@id="{}-{}"]'.format(
                self.FINISH_PROCESS_BTN_ID, self.INDEX_ONE))

    def test_finish_process(self):
        """
        Test finishing a process of an order. Verify buttons are
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
            '//button[@id="{}-{}"]'.format(
                self.START_PROCESS_BTN_ID, self.INDEX_ONE))
        # Start Process 1
        start_proc_btn.click()
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
            '//button[@id="{}-{}"]'.format(
                self.FINISH_PROCESS_BTN_ID, self.INDEX_ONE))
        # Finish Process 1
        finish_proc_btn.click()
        # assert redirected to same page
        self.assertEqual(self.driver.current_url, '{}{}'.format(
            self.live_server_url,
            reverse('control_produccion:order_detail',
                    kwargs={'pk': self.order.id})))
        # wait for page to load
        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda driver: self.driver.find_element_by_tag_name('body'))
        # assert no buttons are shown
