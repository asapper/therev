from django.core.urlresolvers import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase

from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from .models import Order, Quote
from .tests_quote import QuoteSetUpClass
from .utility import OrderController, QuoteController


class SeleniumSetUpClass(QuoteSetUpClass, TestCase):
    @classmethod
    def setUpClass(cls):
        super(SeleniumSetUpClass, cls).setUpClass()
        cls.driver = WebDriver()
        cls.FIRST_VALUE = '1'
        cls.INDEX_ONE = 1
        cls.INDEX_TWO = 2
        cls.TIMEOUT = 2
        cls.CREATE_QUOTE_TEXT = 'CREATE NEW QUOTE'
        cls.EDIT_TEXT = 'EDIT QUOTE'
        cls.CREATE_ORDER_TEXT = 'CREATE ORDER'
        cls.START_ORDER_BTN_ID = 'btn-start-order'
        cls.FINISH_ORDER_BTN_ID = 'btn-finish-order'
        cls.START_FINISHING_BTN_ID = 'btn-start-finishing'
        cls.FINISH_FINISHING_BTN_ID = 'btn-finish-finishing'
        cls.pack_inst = "Pack in 20s."
        cls.delivery_addr = "123 ave."
        cls.notes = "None."

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super(SeleniumSetUpClass, cls).tearDownClass()


class SeleniumQuoteTests(SeleniumSetUpClass, StaticLiveServerTestCase):
    def test_create_quote(self):
        """
        Test accessing the Ventas module and creating a Quote.
        Fill-in the input fields and submit a valid Quote. Check that
        it redirects to quote's detail page.
        """
        # access ventas module
        self.driver.get('{}{}'.format(
            self.live_server_url,
            reverse('ventas:index')))
        # wait for page to load
        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda driver: self.driver.find_element_by_tag_name('body'))
        # click Create New Quote button
        self.driver.find_element_by_link_text(self.CREATE_QUOTE_TEXT).click()
        # fill form
        name_field = self.driver.find_element_by_name('quote_name')
        name_field.send_keys('Test Quote 1')
        due_date_field = self.driver.find_element_by_name('quote_due_date')
        due_date_field.send_keys('12/12/2016')
        copies_field = self.driver.find_element_by_name('quote_copies')
        copies_field.send_keys('100')
        product_name_field = self.driver.find_element_by_name(
            'quote_product_name')
        product_name_field.send_keys('Test Product')
        dimention_field = self.driver.find_element_by_name(
            'quote_dimention_width')
        dimention_field.send_keys('2')
        length_field = self.driver.find_element_by_name(
            'quote_dimention_length')
        length_field.send_keys('3.5')
        bleed_field = self.driver.find_element_by_name('quote_printing_bleed')
        bleed_field.send_keys('0.1')
        sides_field = self.driver.find_element_by_name('quote_printing_sides')
        sides_field.send_keys('2')
        colors_front_field = self.driver.find_element_by_name(
            'quote_printing_colors_front')
        colors_front_field.send_keys('4')
        colors_back_field = self.driver.find_element_by_name(
            'quote_printing_colors_back')
        colors_back_field.send_keys('4')
        client_field = Select(self.driver.find_element_by_name('client'))
        client_field.select_by_value(self.FIRST_VALUE)
        finishings_field = Select(
            self.driver.find_element_by_name('finishings'))
        finishings_field.select_by_value(self.FIRST_VALUE)
        materials_field = Select(self.driver.find_element_by_name('materials'))
        materials_field.select_by_value(self.FIRST_VALUE)
        paper_field = Select(self.driver.find_element_by_name('paper'))
        paper_field.select_by_value(self.FIRST_VALUE)
        # submit form
        self.driver.find_element_by_xpath('//button[@type="submit"]').click()
        # wait for page to load
        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda driver: self.driver.find_element_by_tag_name('body'))
        # assert in detail page
        self.assertEqual(self.driver.current_url, "{}{}".format(
            self.live_server_url,
            reverse('ventas:quote_detail', kwargs={'pk': self.INDEX_TWO})))

    def test_unauthorized_quote_detail_page_buttons(self):
        """
        Test accessing the detail page of an unauthorized quote, and verify
        the buttons are correctly enabled/disabled.
        """
        # access detail page of quote in db (through set up class)
        self.driver.get('{}{}'.format(
            self.live_server_url,
            reverse('ventas:quote_detail', kwargs={'pk': self.INDEX_ONE})))
        # wait for page to load
        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda driver: self.driver.find_element_by_tag_name('body'))
        # assert Edit button is enabled
        edit_button = self.driver.find_element_by_link_text(self.EDIT_TEXT)
        self.assertTrue('disabled' not in edit_button.get_attribute('class'))
        # assert Authorize button is enabled
        auth_button = self.driver.find_element_by_xpath(
            '//button[@data-toggle="modal"]')
        self.assertTrue('disabled' not in auth_button.get_attribute('class'))
        # assert Create Order button is disabled
        create_order_button = self.driver.find_element_by_link_text(
            self.CREATE_ORDER_TEXT)
        self.assertTrue(
            'disabled' in create_order_button.get_attribute('class'))

    def test_authorized_quote_detail_page_buttons(self):
        """
        Test accessing the detail page of an authorized quote, and verify
        the buttons are correctly enabled/disabled.
        """
        quote = Quote.objects.get(pk=self.quote_instance.id)
        QuoteController.authorize_quote(quote)
        # access detail page of quote in db (through set up class)
        self.driver.get('{}{}'.format(
            self.live_server_url,
            reverse('ventas:quote_detail', kwargs={'pk': self.INDEX_ONE})))
        # wait for page to load
        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda driver: self.driver.find_element_by_tag_name('body'))
        # assert Edit button is disabled
        edit_button = self.driver.find_element_by_link_text(self.EDIT_TEXT)
        self.assertTrue('disabled' in edit_button.get_attribute('class'))
        # assert Authorize button is disabled
        auth_button = self.driver.find_element_by_css_selector('button.btn')
        self.assertTrue('disabled' in auth_button.get_attribute('class'))
        # assert Create Order button is enabled
        create_order_button = self.driver.find_element_by_link_text(
            self.CREATE_ORDER_TEXT)
        self.assertTrue(
            'disabled' not in create_order_button.get_attribute('class'))

    def test_approved_quote_detail_page_buttons(self):
        """
        Test accessing the detail page of an approved quote, and verify
        the buttons are correctly enabled/disabled.
        """
        # authorize and approve quote (create order)
        quote = Quote.objects.get(pk=self.quote_instance.id)
        QuoteController.authorize_quote(quote)
        OrderController.create_order(
            quote, self.pack_inst, self.delivery_addr, self.notes)
        # access detail page of quote in db (through set up class)
        self.driver.get('{}{}'.format(
            self.live_server_url,
            reverse('ventas:quote_detail', kwargs={'pk': self.INDEX_ONE})))
        # wait for page to load
        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda driver: self.driver.find_element_by_tag_name('body'))
        # assert Edit button is disabled
        edit_button = self.driver.find_element_by_link_text(self.EDIT_TEXT)
        self.assertTrue('disabled' in edit_button.get_attribute('class'))
        # assert Authorize button is disabled
        auth_button = self.driver.find_element_by_css_selector('button.btn')
        self.assertTrue('disabled' in auth_button.get_attribute('class'))
        # assert Create Order button is disabled
        create_order_button = self.driver.find_element_by_link_text(
            self.CREATE_ORDER_TEXT)
        self.assertTrue(
            'disabled' in create_order_button.get_attribute('class'))

    def test_edit_quote(self):
        """
        Test accessing the detail page of a quote and editing it.
        Verify the buttons are correctly enabled/disabled.
        Save edited quote, check it redirects to detail page.
        """
        # access detail page of quote in db (through set up class)
        self.driver.get('{}{}'.format(
            self.live_server_url,
            reverse('ventas:quote_detail', kwargs={'pk': self.INDEX_ONE})))
        # wait for page to load
        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda driver: self.driver.find_element_by_tag_name('body'))
        # assert Edit button is enabled
        edit_button = self.driver.find_element_by_link_text(self.EDIT_TEXT)
        self.assertTrue('disabled' not in edit_button.get_attribute('class'))
        edit_button.click()
        # assert in quote edit page
        self.assertEqual(self.driver.current_url, "{}{}".format(
            self.live_server_url,
            reverse('ventas:quote_edit', kwargs={'pk': self.INDEX_ONE})))
        # edit form
        name_field = self.driver.find_element_by_name('quote_name')
        name_field.send_keys('Test Quote ABC')
        # submit form
        self.driver.find_element_by_xpath('//button[@type="submit"]').click()
        # assert in detail page
        self.assertEqual(self.driver.current_url, "{}{}".format(
            self.live_server_url,
            reverse('ventas:quote_detail', kwargs={'pk': self.INDEX_ONE})))

    def test_edit_quote_badly(self):
        """
        Test accessing the detail page of a quote and editing it.
        Unselect all finishings and materials.
        An error should occur when saving quote.
        """
        # access detail page of quote in db (through set up class)
        self.driver.get('{}{}'.format(
            self.live_server_url,
            reverse('ventas:quote_detail', kwargs={'pk': self.INDEX_ONE})))
        # wait for page to load
        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda driver: self.driver.find_element_by_tag_name('body'))
        # assert Edit button is enabled
        edit_button = self.driver.find_element_by_link_text(self.EDIT_TEXT)
        self.assertTrue('disabled' not in edit_button.get_attribute('class'))
        edit_button.click()
        # assert in quote edit page
        self.assertEqual(self.driver.current_url, "{}{}".format(
            self.live_server_url,
            reverse('ventas:quote_edit', kwargs={'pk': self.INDEX_ONE})))
        # edit form
        finishings_field = Select(
            self.driver.find_element_by_name('finishings'))
        finishings_field.deselect_all()  # clear selections
        materials_field = Select(self.driver.find_element_by_name('materials'))
        materials_field.deselect_all()  # clear selections
        # submit form
        self.driver.find_element_by_xpath('//button[@type="submit"]').click()
        # assert in edit page still
        self.assertEqual(self.driver.current_url, "{}{}".format(
            self.live_server_url,
            reverse('ventas:quote_edit', kwargs={'pk': self.INDEX_ONE})))

    def test_edit_quote_leave_blank(self):
        """
        Test accessing the detail page of a quote and editing it.
        Blank all input fields. An error should occur when saving quote.
        """
        # access detail page of quote in db (through set up class)
        self.driver.get('{}{}'.format(
            self.live_server_url,
            reverse('ventas:quote_detail', kwargs={'pk': self.INDEX_ONE})))
        # wait for page to load
        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda driver: self.driver.find_element_by_tag_name('body'))
        # assert Edit button is enabled
        edit_button = self.driver.find_element_by_link_text(self.EDIT_TEXT)
        self.assertTrue('disabled' not in edit_button.get_attribute('class'))
        edit_button.click()
        # assert in quote edit page
        self.assertEqual(self.driver.current_url, "{}{}".format(
            self.live_server_url,
            reverse('ventas:quote_edit', kwargs={'pk': self.INDEX_ONE})))
        # edit form
        self.driver.find_element_by_name('quote_name').clear()  # clear field
        self.driver.find_element_by_name(
            'quote_due_date').clear()  # clear field
        self.driver.find_element_by_name('quote_quires').clear()  # clear field
        self.driver.find_element_by_name('quote_copies').clear()  # clear field
        self.driver.find_element_by_name(
            'quote_product_name').clear()  # clear field
        self.driver.find_element_by_name(
            'quote_dimention_width').clear()  # clear field
        self.driver.find_element_by_name(
            'quote_dimention_length').clear()  # clear field
        self.driver.find_element_by_name(
            'quote_printing_bleed').clear()  # clear field
        self.driver.find_element_by_name(
            'quote_printing_sides').clear()  # clear field
        self.driver.find_element_by_name(
            'quote_printing_colors_front').clear()  # clear field
        self.driver.find_element_by_name(
            'quote_printing_colors_back').clear()  # clear field
        Select(self.driver.find_element_by_name(
            'finishings')).deselect_all()  # clear field
        Select(self.driver.find_element_by_name(
            'materials')).deselect_all()  # clear field
        # submit form
        self.driver.find_element_by_xpath('//button[@type="submit"]').click()
        # assert in edit page still
        self.assertEqual(self.driver.current_url, "{}{}".format(
            self.live_server_url,
            reverse('ventas:quote_edit', kwargs={'pk': self.INDEX_ONE})))

    def test_create_order(self):
        """
        Test accessing the detail page of a quote and creating an order
        by clicking Create Order. Verify that it redirects to the approve
        page. Verify the buttons are correctly enabled/disabled before
        and after creating the order. Fill out Order form and submit.
        Verify it redirects to order detail page.
        """
        # authorize quote
        quote = Quote.objects.get(pk=self.quote_instance.id)
        QuoteController.authorize_quote(quote)
        # access detail page of quote in db (through set up class)
        self.driver.get('{}{}'.format(
            self.live_server_url,
            reverse('ventas:quote_detail', kwargs={'pk': self.INDEX_ONE})))
        # wait for page to load
        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda driver: self.driver.find_element_by_tag_name('body'))
        # assert Edit button is disabled
        edit_button = self.driver.find_element_by_link_text(self.EDIT_TEXT)
        self.assertTrue('disabled' in edit_button.get_attribute('class'))
        # assert Authorize button is disabled
        auth_button = self.driver.find_element_by_css_selector('button.btn')
        self.assertTrue('disabled' in auth_button.get_attribute('class'))
        # assert Create Order button is enabled
        create_order_button = self.driver.find_element_by_link_text(
            self.CREATE_ORDER_TEXT)
        self.assertTrue(
            'disabled' not in create_order_button.get_attribute('class'))
        create_order_button.click()
        # assert redirects to approve page
        self.assertEqual(self.driver.current_url, "{}{}".format(
            self.live_server_url,
            reverse('ventas:quote_approve', kwargs={'pk': self.INDEX_ONE})))
        # fill in form
        pack_inst_field = self.driver.find_element_by_name(
            'order_packaging_instructions')
        pack_inst_field.send_keys(self.pack_inst)
        delivery_addr_field = self.driver.find_element_by_name(
            'order_delivery_address')
        delivery_addr_field.send_keys(self.delivery_addr)
        notes_field = self.driver.find_element_by_name('order_notes')
        notes_field.send_keys(self.notes)
        # submit form
        self.driver.find_element_by_xpath('//button[@type="submit"]').click()
        # wait for page to load
        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda driver: self.driver.find_element_by_tag_name('body'))
        # assert in order detail page
        self.assertEqual(self.driver.current_url, "{}{}".format(
            self.live_server_url,
            reverse('ventas:order_detail', kwargs={'pk': self.INDEX_ONE})))

    def test_create_order_with_different_id_than_its_quote(self):
        """
        Test accessing the detail page of a quote and creating an order
        by clicking Create Order, while there exist a few quotes already
        in the database. Verify that it redirects to the approve
        page. Verify the buttons are correctly enabled/disabled before
        and after creating the order. Fill out Order form and submit.
        Verify it redirects to order detail page of order's id and
        not of quote's id.
        """
        # create one quote
        self.create_quote(
            name="Test quote ABC", due_date=self.due_today, copies=100,
            product_name="test", width=8.5, length=5.5, bleed=0.1, sides=1,
            colors_front=4, colors_back=0, materials=[self.m_print],
            finishings=[self.f_trim])
        # create another quote (three in system now)
        third_quote = self.create_quote(
            name="Test quote DEF", due_date=self.due_today, copies=100,
            product_name="test", width=8.5, length=5.5, bleed=0.1, sides=1,
            colors_front=4, colors_back=0, materials=[self.m_print],
            finishings=[self.f_trim])
        # authorize third quote
        QuoteController.authorize_quote(third_quote)
        # authorize and create order for first quote in db
        first_quote = self.quote_instance
        QuoteController.authorize_quote(first_quote)
        OrderController.create_order(
            first_quote, self.pack_inst, self.delivery_addr, self.notes)
        # access detail page of last quote created
        self.driver.get('{}{}'.format(
            self.live_server_url,
            reverse('ventas:quote_detail', kwargs={'pk': third_quote.id})))
        # wait for page to load
        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda driver: self.driver.find_element_by_tag_name('body'))
        # assert Edit button is disabled
        edit_button = self.driver.find_element_by_link_text(self.EDIT_TEXT)
        self.assertTrue('disabled' in edit_button.get_attribute('class'))
        # assert Authorize button is disabled
        auth_button = self.driver.find_element_by_css_selector('button.btn')
        self.assertTrue('disabled' in auth_button.get_attribute('class'))
        # assert Create Order button is enabled
        create_order_button = self.driver.find_element_by_link_text(
            self.CREATE_ORDER_TEXT)
        self.assertTrue(
            'disabled' not in create_order_button.get_attribute('class'))
        create_order_button.click()
        # assert redirects to approve page
        self.assertEqual(self.driver.current_url, "{}{}".format(
            self.live_server_url,
            reverse('ventas:quote_approve', kwargs={'pk': third_quote.id})))
        # fill in form
        pack_inst_field = self.driver.find_element_by_name(
            'order_packaging_instructions')
        pack_inst_field.send_keys(self.pack_inst)
        delivery_addr_field = self.driver.find_element_by_name(
            'order_delivery_address')
        delivery_addr_field.send_keys(self.delivery_addr)
        notes_field = self.driver.find_element_by_name('order_notes')
        notes_field.send_keys(self.notes)
        # submit form
        self.driver.find_element_by_xpath('//button[@type="submit"]').click()
        # wait for page to load
        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda driver: self.driver.find_element_by_tag_name('body'))
        # assert in order detail page
        self.assertEqual(self.driver.current_url, "{}{}".format(
            self.live_server_url,
            reverse('ventas:order_detail', kwargs={'pk': self.INDEX_TWO})))


class SeleniumOrderTests(SeleniumSetUpClass, StaticLiveServerTestCase):
    def setUp(self):
        quote_instance = self.create_quote(
            name="Test quote ABC", due_date=self.due_today, copies=100,
            product_name="test", width=8.5, length=5.5, bleed=0.1, sides=1,
            colors_front=4, colors_back=0, materials=[self.m_print],
            finishings=[self.f_trim])
        # authorize and create order for first quote in db
        first_quote = quote_instance
        QuoteController.authorize_quote(first_quote)
        self.order = OrderController.create_order(
            first_quote, self.pack_inst, self.delivery_addr, self.notes)

    def test_start_order(self):
        """Test starting an order."""
        # access order detail page
        self.driver.get('{}{}'.format(
            self.live_server_url,
            reverse('ventas:order_detail', kwargs={'pk': self.order.id})))
        # wait for page to load
        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda driver: self.driver.find_element_by_tag_name('body'))
        # assert Start Order button enabled
        start_order_button = self.driver.find_element_by_xpath(
            '//button[@type="submit"]')
        self.assertTrue(
            'disabled' not in start_order_button.get_attribute('class'))
        # assert Finish Order button disabled
        finish_order_button = self.driver.find_element_by_xpath(
            '//a[@id="{}"]'.format(self.FINISH_ORDER_BTN_ID))
        self.assertTrue(
            'disabled' in finish_order_button.get_attribute('class'))
        # start order
        start_order_button.click()
        # assert page redirects to order detail page
        self.assertEqual(self.driver.current_url, '{}{}'.format(
            self.live_server_url,
            reverse('ventas:order_detail', kwargs={'pk': self.order.id})))
        # assert order is started
        tmp_order = Order.objects.get(pk=self.order.id)  # refresh instance
        self.assertTrue(tmp_order.order_is_started)
        # assert Start Order button disabled
        start_order_button = self.driver.find_element_by_xpath(
            '//a[@id="{}"]'.format(self.START_ORDER_BTN_ID))
        self.assertTrue(
            'disabled' in start_order_button.get_attribute('class'))
        # assert Finish Order button enabled
        finish_order_button = self.driver.find_element_by_xpath(
            '//button[@id="{}"]'.format(self.FINISH_ORDER_BTN_ID))
        self.assertTrue(
            'disabled' not in finish_order_button.get_attribute('class'))

    def test_start_order_already_started(self):
        """Test trying to start an order already started."""
        OrderController.start_order(self.order)  # start order
        # access order detail page
        self.driver.get('{}{}'.format(
            self.live_server_url,
            reverse('ventas:order_detail', kwargs={'pk': self.order.id})))
        # wait for page to load
        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda driver: self.driver.find_element_by_tag_name('body'))
        # assert Start Order button disabled
        start_order_button = self.driver.find_element_by_xpath(
            '//a[@id="{}"]'.format(self.START_ORDER_BTN_ID))
        self.assertTrue(
            'disabled' in start_order_button.get_attribute('class'))
        # assert Finish Order button enabled
        finish_order_button = self.driver.find_element_by_xpath(
            '//button[@id="{}"]'.format(self.FINISH_ORDER_BTN_ID))
        self.assertTrue(
            'disabled' not in finish_order_button.get_attribute('class'))

    def test_start_finishing(self):
        """
        Test starting a finishing of an order already started.
        Verify buttons are enabled/disabled correctly.
        """
        OrderController.start_order(self.order)  # start order
        # access order detail page
        self.driver.get('{}{}'.format(
            self.live_server_url,
            reverse('ventas:order_detail', kwargs={'pk': self.order.id})))
        # wait for page to load
        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda driver: self.driver.find_element_by_tag_name('body'))
        # assert Start Finishing 1 button is enabled
        start_fin_button = self.driver.find_element_by_xpath(
            '//button[@id="{}-{}"]'.format(
                self.START_FINISHING_BTN_ID, self.INDEX_ONE))
        self.assertTrue(
            'disabled' not in start_fin_button.get_attribute('class'))
        # assert Finish Finishing 1 button is disabled
        finish_fin_button = self.driver.find_element_by_xpath(
            '//a[@id="{}-{}"]'.format(
                self.FINISH_FINISHING_BTN_ID, self.INDEX_ONE))
        self.assertTrue(
            'disabled' in finish_fin_button.get_attribute('class'))
        # start finishing 1
        start_fin_button.click()
        # assert redirected to same page
        self.driver.get('{}{}'.format(
            self.live_server_url,
            reverse('ventas:order_detail', kwargs={'pk': self.order.id})))
        # wait for page to load
        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda driver: self.driver.find_element_by_tag_name('body'))
        # assert Start Finishing 1 button is disabled
        start_fin_button = self.driver.find_element_by_xpath(
            '//a[@id="{}-{}"]'.format(
            self.START_FINISHING_BTN_ID, self.INDEX_ONE))
        self.assertTrue(
            'disabled' in start_fin_button.get_attribute('class'))
        # assert Finish Finishing 1 button is enabled
        finish_fin_button = self.driver.find_element_by_xpath(
            '//button[@id="{}-{}"]'.format(
                self.FINISH_FINISHING_BTN_ID, self.INDEX_ONE))
        self.assertTrue(
            'disabled' not in finish_fin_button.get_attribute('class'))

    def test_start_finishing_with_order_not_started(self):
        """
        Test starting a finishing of an order not yet started.
        Verify no changes are made to finishing and order.
        """
        # access order detail page
        self.driver.get('{}{}'.format(
            self.live_server_url,
            reverse('ventas:order_detail', kwargs={'pk': self.order.id})))
        # wait for page to load
        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda driver: self.driver.find_element_by_tag_name('body'))
        # assert Start Finishing 1 button is disabled
        start_fin_button = self.driver.find_element_by_xpath(
            '//a[@id="{}-{}"]'.format(
                self.START_FINISHING_BTN_ID, self.INDEX_ONE))
        self.assertTrue(
            'disabled' in start_fin_button.get_attribute('class'))
        # assert Finish Finishing 1 button is disabled
        finish_fin_button = self.driver.find_element_by_xpath(
            '//a[@id="{}-{}"]'.format(
                self.FINISH_FINISHING_BTN_ID, self.INDEX_ONE))
        self.assertTrue(
            'disabled' in finish_fin_button.get_attribute('class'))

    def test_finish_finishing(self):
        """
        Test finishing a finishing of an order already started.
        Verify buttons are enabled/disabled correctly.
        """
        OrderController.start_order(self.order)  # start order
        # access order detail page
        self.driver.get('{}{}'.format(
            self.live_server_url,
            reverse('ventas:order_detail', kwargs={'pk': self.order.id})))
        # wait for page to load
        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda driver: self.driver.find_element_by_tag_name('body'))
        # get start and finish buttons
        start_fin_button = self.driver.find_element_by_xpath(
            '//button[@id="{}-{}"]'.format(
                self.START_FINISHING_BTN_ID, self.INDEX_ONE))
        finish_fin_button = self.driver.find_element_by_xpath(
            '//a[@id="{}-{}"]'.format(
                self.FINISH_FINISHING_BTN_ID, self.INDEX_ONE))
        # start finishing 1
        start_fin_button.click()
        # assert redirected to same page
        self.driver.get('{}{}'.format(
            self.live_server_url,
            reverse('ventas:order_detail', kwargs={'pk': self.order.id})))
        # wait for page to load
        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda driver: self.driver.find_element_by_tag_name('body'))
        # get start and finish buttons
        start_fin_button = self.driver.find_element_by_xpath(
            '//a[@id="{}-{}"]'.format(
            self.START_FINISHING_BTN_ID, self.INDEX_ONE))
        self.assertTrue(
            'disabled' in start_fin_button.get_attribute('class'))
        finish_fin_button = self.driver.find_element_by_xpath(
            '//button[@id="{}-{}"]'.format(
                self.FINISH_FINISHING_BTN_ID, self.INDEX_ONE))
        self.assertTrue(
            'disabled' not in finish_fin_button.get_attribute('class'))
        # finish finishing
        finish_fin_button.click()
        # assert Start Finishing button is disabled
        start_fin_button = self.driver.find_element_by_xpath(
            '//a[@id="{}-{}"]'.format(
            self.START_FINISHING_BTN_ID, self.INDEX_ONE))
        self.assertTrue(
            'disabled' in start_fin_button.get_attribute('class'))
        # assert Finish Finishing button is disabled
        finish_fin_button = self.driver.find_element_by_xpath(
            '//a[@id="{}-{}"]'.format(
                self.FINISH_FINISHING_BTN_ID, self.INDEX_ONE))
        self.assertTrue(
            'disabled' in finish_fin_button.get_attribute('class'))
