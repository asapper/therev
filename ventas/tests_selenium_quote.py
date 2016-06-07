from django.core.urlresolvers import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from .tests_quote import QuoteSetUpClass
from .models import AuthorizedQuote, Quote


class SeleniumQuoteTests(QuoteSetUpClass, StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super(SeleniumQuoteTests, cls).setUpClass()
        cls.driver = WebDriver()
        cls.FIRST_VALUE = '1'
        cls.INDEX_ONE = 1
        cls.INDEX_TWO = 2
        cls.TIMEOUT = 2
        cls.CREATE_QUOTE_TEXT = 'CREATE NEW QUOTE'
        cls.EDIT_TEXT = 'EDIT QUOTE'
        cls.CREATE_ORDER_TEXT = 'CREATE ORDER'

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super(SeleniumQuoteTests, cls).tearDownClass()

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
        quote.authorize_quote()
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
        quote = Quote.objects.get(pk=self.quote_instance.id)
        auth_quote = quote.authorize_quote()
        pack_inst = "Pack in groups of 100."
        delivery_addr = "123 ave"
        notes = "Due in two days!"
        auth_quote.create_order(pack_inst, delivery_addr, notes)
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
        quote.authorize_quote()
        # store order data
        pack_inst = "Pack in groups of 100."
        delivery_addr = "123 ave"
        notes = "Due in two days!"
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
            'disabled' not in create_order_button.get_attribute('class'))
        create_order_button.click()
        # assert redirects to approve page
        self.assertEqual(self.driver.current_url, "{}{}".format(
            self.live_server_url,
            reverse('ventas:quote_approve', kwargs={'pk': self.INDEX_ONE})))
        # fill in form
        pack_inst_field = self.driver.find_element_by_name(
            'order_packaging_instructions')
        pack_inst_field.send_keys(pack_inst)
        delivery_addr_field = self.driver.find_element_by_name(
            'order_delivery_address')
        delivery_addr_field.send_keys(delivery_addr)
        notes_field = self.driver.find_element_by_name('order_notes')
        notes_field.send_keys(notes)
        # submit form
        self.driver.find_element_by_xpath('//button[@type="submit"]').click()
        # wait for page to load
        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda driver: self.driver.find_element_by_tag_name('body'))
        # assert in order detail page
        self.assertEqual(self.driver.current_url, "{}{}".format(
            self.live_server_url,
            reverse('ventas:order_detail', kwargs={'pk': self.INDEX_ONE})))

    def test_create_order_while_auth_quote_dynamiclly_deleted(self):
        """
        Test creating an order for an existing quote, while the authorized
        quote instance is deleted during the Order form completion.
        """
        # authorize quote
        quote = Quote.objects.get(pk=self.quote_instance.id)
        auth_quote = quote.authorize_quote()
        # store order data
        pack_inst = "Pack in groups of 100."
        delivery_addr = "123 ave"
        notes = "Due in two days!"
        # access create order page
        self.driver.get('{}{}'.format(
            self.live_server_url,
            reverse('ventas:quote_approve', kwargs={'pk': self.INDEX_ONE})))
        # wait for page to load
        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda driver: self.driver.find_element_by_tag_name('body'))
        # fill in form
        pack_inst_field = self.driver.find_element_by_name(
            'order_packaging_instructions')
        pack_inst_field.send_keys(pack_inst)
        delivery_addr_field = self.driver.find_element_by_name(
            'order_delivery_address')
        delivery_addr_field.send_keys(delivery_addr)
        notes_field = self.driver.find_element_by_name('order_notes')
        notes_field.send_keys(notes)
        # delete authorized quote instance
        AuthorizedQuote.objects.get(pk=auth_quote.id).delete()
        # submit form
        self.driver.find_element_by_xpath('//button[@type="submit"]').click()
        # assert not in order detail page
        self.assertNotEqual(self.driver.current_url, "{}{}".format(
            self.live_server_url,
            reverse('ventas:order_detail', kwargs={'pk': quote.id})))
