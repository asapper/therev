import datetime

from django.core.urlresolvers import reverse
from django.test import TestCase

from . import utility
from .forms import QuoteForm
from .models import Quote
from .models import Quote_Finishing
from personal.models import Client
from personal.models import Executive
from personal.models import Person
from recursos.models import Finishing
from recursos.models import Material
from recursos.models import Paper


class QuoteSetUpClass(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.due_today = datetime.date.today()
        person = Person.objects.create(
            person_name='Andy',
            person_lastname='Sapper')
        cls.client_instance = Client.objects.create(
            client_name='Test_Client',
            client_receipt_name='Test_Client',
            client_receipt_address='123 ave',
            client_nit=123456)
        cls.executive_instance = Executive.objects.create(
            person=person,
            executive_comssn=10)
        cls.f_trim = Finishing.objects.create(
            finishing_name='Trim',
            finishing_price=3)
        cls.f_fold = Finishing.objects.create(
            finishing_name='Fold',
            finishing_price=1)
        cls.f_blunt = Finishing.objects.create(
            finishing_name='Blunt',
            finishing_price=3)
        cls.m_print = Material.objects.create(
            material_name='Printing',
            material_price=8)
        cls.m_varnish = Material.objects.create(
            material_name='Varnish',
            material_price=5)
        cls.m_foil = Material.objects.create(
            material_name='Foil',
            material_price=10)
        cls.paper_instance = Paper.objects.create(
            paper_name='Test_Paper',
            paper_width=10,
            paper_length=10,
            paper_price=5)
        cls.quote_instance = cls.create_quote(
            name="TestQuote", due_date=cls.due_today, copies=10,
            product_name="Prueba", width=10, length=18, bleed=0.1, sides=2,
            colors_front=4, colors_back=4, materials=[cls.m_print],
            finishings=[cls.f_trim])

    @classmethod
    def create_quote(cls, name, due_date, copies, product_name,
                     width, length, bleed, sides, colors_front, colors_back,
                     materials, finishings, quires=1):
        """Create a Quote with the given information."""
        quote = Quote.objects.create(
            quote_name=name,
            quote_due_date=due_date,
            quote_copies=copies,
            quote_quires=quires,
            quote_product_name=product_name,
            quote_dimention_width=width,
            quote_dimention_length=length,
            quote_printing_bleed=bleed,
            quote_printing_sides=sides,
            quote_printing_colors_front=colors_front,
            quote_printing_colors_back=colors_back,
            client=cls.client_instance,
            executive=cls.executive_instance,
            paper=cls.paper_instance)
        # store materials
        quote.materials.set(materials)
        # store finishigns
        for finishing in finishings:
            Quote_Finishing.objects.create(
                quote=quote,
                finishing=finishing)
        imposing, sheets = utility.get_imposing(quote)
        quote.quote_imposing_per_sheet = imposing
        quote.quote_total_sheets = sheets
        quote.quote_total_price = utility.get_total_price(quote)
        quote.save()
        return quote


class QuoteViewTests(QuoteSetUpClass, TestCase):
    def test_quote_view_with_no_quotes(self):
        """If no Quotes exist, an appropriate message should be displayed."""
        # clear database for test
        Quote.objects.get(pk=self.quote_instance.id).delete()
        response = self.client.get(reverse('ventas:quotes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No quotes are available.")
        self.assertQuerysetEqual(response.context['latest_quote_list'], [])

    def test_quote_view_with_a_quote(self):
        """If a Quote exists, it should be displayed."""
        # a quote is already in db
        response = self.client.get(reverse('ventas:quotes'))
        self.assertQuerysetEqual(
            response.context['latest_quote_list'],
            [("<Quote: Id: 1; Name: TestQuote; Product: Prueba; "
                "Dimentions: 10.00\" x 18.00\"; Due: {}; Copies: 10; "
                "Printing sides: 2.>").format(datetime.date.today())]
        )

    def test_quote_view_with_two_quotes(self):
        """If two or more Quotes exist, they should be displayed."""
        # quote #1 (test quote) is already in db
        # create quote #2
        self.create_quote(name="Quote2", due_date=self.due_today,
                          copies=20, product_name="Prueba2", width=11,
                          length=19, bleed=0.1, sides=1, colors_front=0,
                          colors_back=4, materials=[self.m_print],
                          finishings=[self.f_trim])
        # get response
        response = self.client.get(reverse('ventas:quotes'))
        self.assertQuerysetEqual(
            response.context['latest_quote_list'].order_by('id'),
            [("<Quote: Id: 1; Name: TestQuote; Product: Prueba; "
                "Dimentions: 10.00\" x 18.00\"; Due: {}; Copies: 10; "
                "Printing sides: 2.>").format(
                    datetime.date.today()),
             ("<Quote: Id: 2; Name: Quote2; Product: Prueba2; "
                "Dimentions: 11.00\" x 19.00\"; Due: {}; Copies: 20; "
                "Printing sides: 1.>").format(
                    datetime.date.today())]
        )


class QuoteDetailViewTests(QuoteSetUpClass, TestCase):
    def test_quote_detail_view(self):
        """Test that data is displayed correctly."""
        # a quote is already in db
        quote = self.quote_instance
        response = self.client.get(
            reverse('ventas:quote_detail', kwargs={'pk': quote.id}))
        self.assertContains(response, quote.quote_name, status_code=200)

    def test_not_existent_quote_detail_view(self):
        """
        Test that a 404 is returned when accessing the detail page of a
        quote that does not exist.
        """
        BAD_QUOTE_ID = 100
        response = self.client.get(
            reverse('ventas:quote_detail', kwargs={'pk': BAD_QUOTE_ID}))
        self.assertEqual(response.status_code, 404)


class QuoteMethodTests(QuoteSetUpClass, TestCase):
    def test_get_quote_price(self):
        """Create a quote and verify its price is accurate."""
        quote = self.create_quote(
            name='Quote1',
            due_date=self.due_today,
            copies=250,
            product_name='invitations',
            width=8.5,
            length=5.5,
            bleed=0.1,
            sides=1,
            colors_front=4,
            colors_back=0,
            materials=[self.m_print, self.m_varnish, self.m_foil],
            finishings=[self.f_trim, self.f_fold, self.f_blunt])
        # expected price
        sheets = quote.quote_total_sheets
        exp_price = sheets * self.m_print.material_price
        exp_price += sheets * self.m_varnish.material_price
        exp_price += sheets * self.m_foil.material_price
        exp_price += sheets * self.f_trim.finishing_price
        exp_price += sheets * self.f_fold.finishing_price
        exp_price += sheets * self.f_blunt.finishing_price
        exp_price += sheets * quote.paper.paper_price
        # assert price if accurate
        self.assertEqual(quote.quote_total_price, exp_price)

    def test_get_quote_price_many_quires(self):
        """Create a quote with many quires and verify its price is accurate."""
        quote = self.create_quote(
            name='Quote1',
            due_date=self.due_today,
            copies=1,
            product_name='invitations',
            width=8.5,
            length=5.5,
            bleed=0.1,
            sides=1,
            colors_front=4,
            colors_back=0,
            materials=[self.m_print, self.m_varnish, self.m_foil],
            finishings=[self.f_trim, self.f_fold, self.f_blunt],
            quires=250)
        # expected price
        sheets = quote.quote_total_sheets
        exp_price = sheets * self.m_print.material_price
        exp_price += sheets * self.m_varnish.material_price
        exp_price += sheets * self.m_foil.material_price
        exp_price += sheets * self.f_trim.finishing_price
        exp_price += sheets * self.f_fold.finishing_price
        exp_price += sheets * self.f_blunt.finishing_price
        exp_price += sheets * quote.paper.paper_price
        # assert price if accurate
        self.assertEqual(quote.quote_total_price, exp_price)

    def test_get_quote_imposing_and_sheets(self):
        """Create a quote and verify its imposing is accurate."""
        bleed = 0.1
        dimentions = int(self.paper_instance.paper_width / 2)
        dimentions -= (2 * bleed)

        quote = self.create_quote(
            name='Quote1',
            due_date=self.due_today,
            copies=100,
            product_name='tarjetas',
            width=dimentions,
            length=dimentions,
            bleed=bleed,
            sides=1,
            colors_front=4,
            colors_back=0,
            materials=[self.m_print],
            finishings=[self.f_trim])
        # best imposing
        exp_imposing = 4  # expected since dimentions == 1/4 of paper
        exp_sheets = 25  # expected since 4 fit per sheet for 100 copies
        # assert imposing and sheets is accurate
        self.assertEqual(quote.quote_imposing_per_sheet, exp_imposing)
        self.assertEqual(quote.quote_total_sheets, exp_sheets)

    def test_get_imposing_job_bigger_than_paper(self):
        """
        Create a quote with dimentions greater than the paper.
        Testing that job is not imposable.
        """
        dimentions = self.paper_instance.paper_width * 2

        quote = self.create_quote(
            name='Quote1',
            due_date=self.due_today,
            copies=100,
            product_name='tarjetas',
            width=dimentions,
            length=dimentions,
            bleed=0.1,
            sides=1,
            colors_front=4,
            colors_back=0,
            materials=[self.m_print],
            finishings=[self.f_trim])
        # assert no imposing or sheets given (error)
        self.assertEqual(quote.quote_imposing_per_sheet, 0)
        self.assertEqual(quote.quote_total_sheets, 0)

    def test_get_quote_id(self):
        """Create a quote, and get its id."""
        # create quote with id: 1
        quote = self.quote_instance
        # check method: get_quote_id()
        self.assertEqual(quote.get_quote_id(), quote.id)

    def test_get_due_date(self):
        """Create a quote and get its due date."""
        # create quote with due date: today
        quote_today = self.quote_instance
        # create quote with due date: today
        in_seven_days = self.due_today + datetime.timedelta(days=7)
        quote_future = self.create_quote(
            name="Quote2", due_date=in_seven_days, copies=20,
            product_name="Prueba2", width=10, length=18, bleed=0.1, sides=1,
            colors_front=4, colors_back=4, materials=[self.m_print],
            finishings=[self.f_trim])
        # check method: get_quote_due_date()
        self.assertEqual(quote_today.get_due_date(), self.due_today)
        self.assertEqual(quote_future.get_due_date(), in_seven_days)

    def test_get_client(self):
        """Create a quote and get its client."""
        # create quote with given client instance
        quote = self.quote_instance
        self.assertEqual(quote.get_client(), self.client_instance)

    def test_get_executive(self):
        """Create a quote and get its executive."""
        # create quote with given executive instance
        quote = self.quote_instance
        self.assertEqual(quote.get_executive(), self.executive_instance)

    def test_get_finishings(self):
        """Create a quote and get its finishings."""
        # list of finishings to use
        finishings = [self.f_trim, self.f_fold, self.f_blunt]
        # create quote with many finishings
        quote = self.create_quote(
            name="Quote1", due_date=self.due_today, copies=10,
            product_name="Prueba", width=10, length=18, bleed=0.1, sides=2,
            colors_front=4, colors_back=4, materials=[self.m_print],
            finishings=finishings)
        self.assertSequenceEqual(quote.get_finishings(), finishings)

    def test_get_materials(self):
        """Create a quote and get its materials."""
        # list of materials to use
        materials = [self.m_print, self.m_varnish, self.m_foil]
        # create quote with many materials
        quote = self.create_quote(
            name="Quote1", due_date=self.due_today, copies=10,
            product_name="Prueba", width=10, length=18, bleed=0.1, sides=2,
            colors_front=4, colors_back=4, materials=materials,
            finishings=[self.f_trim])
        self.assertSequenceEqual(quote.get_materials(), materials)

    def test_get_paper(self):
        """Create a quote and get its paper."""
        # create quote with given paper instance
        quote = self.quote_instance
        self.assertEqual(quote.get_paper(), self.paper_instance)


class QuoteCreateFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.REQ_MSG = "This field is required."
        cls.MIN_VAL_0_MSG = "Ensure this value is greater than or equal to 0."
        FIRST_INDEX = 1
        person = Person.objects.create(  # create a Person
            person_name='Andy',
            person_lastname='Sapper')
        Client.objects.create(  # create a Client
            client_name='Test_Client',
            client_receipt_name='Test_Client',
            client_receipt_address='123 ave',
            client_nit=123456)
        Executive.objects.create(  # create an Executive
            person=person,
            executive_comssn=10)
        Finishing.objects.create(  # create a Finishing
            finishing_name='Trim',
            finishing_price=3)
        Material.objects.create(  # create a Material
            material_name='Printing',
            material_price=8)
        Paper.objects.create(  # create a Paper
            paper_name='Test_Paper',
            paper_width=10,
            paper_length=10,
            paper_price=5)
        # store data to be used in forms
        cls.quote_data = {
            'quote_name': 'TestQuote1',
            'quote_due_date': datetime.date.today(),
            'quote_copies':  100,
            'quote_quires': 1,
            'quote_product_name': 'Test product',
            'quote_dimention_width': 2,
            'quote_dimention_length': 3.5,
            'quote_printing_bleed': 0.1,
            'quote_printing_sides': 1,
            'quote_printing_colors_front': 4,
            'quote_printing_colors_back': 0,
            'client': FIRST_INDEX,
            'executive': FIRST_INDEX,
            'paper': FIRST_INDEX,
            'materials': [FIRST_INDEX],
            'finishings': [FIRST_INDEX],
            'quote_imposing_per_sheet': 10,
            'quote_total_sheets': 10,
            'quote_total_price': 50,
        }

    def test_blank_form(self):
        """Test for a blank form. Expect an error."""
        form = QuoteForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['quote_name'], [self.REQ_MSG])
        self.assertEqual(form.errors['quote_due_date'], [self.REQ_MSG])
        self.assertEqual(form.errors['quote_copies'], [self.REQ_MSG])
        self.assertEqual(form.errors['quote_product_name'], [self.REQ_MSG])
        self.assertEqual(form.errors['quote_dimention_width'], [self.REQ_MSG])
        self.assertEqual(
            form.errors['quote_dimention_length'], [self.REQ_MSG])
        self.assertEqual(form.errors['quote_printing_bleed'], [self.REQ_MSG])
        self.assertEqual(form.errors['quote_printing_sides'], [self.REQ_MSG])
        self.assertEqual(
            form.errors['quote_printing_colors_front'], [self.REQ_MSG])
        self.assertEqual(
            form.errors['quote_printing_colors_back'], [self.REQ_MSG])
        self.assertEqual(form.errors['client'], [self.REQ_MSG])
        self.assertEqual(form.errors['finishings'], [self.REQ_MSG])
        self.assertEqual(form.errors['materials'], [self.REQ_MSG])
        self.assertEqual(form.errors['paper'], [self.REQ_MSG])

    def test_valid_full_form(self):
        """Test that a fully-filled form is valid."""
        form = QuoteForm(data=self.quote_data)
        form.is_valid()
        self.assertTrue(form.is_valid())

    def test_blank_quote_name(self):
        """Test a form missing quote name. Expect an error."""
        temp_data = self.quote_data.copy()
        temp_data['quote_name'] = ""  # blank quote name
        form = QuoteForm(data=temp_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['quote_name'], [self.REQ_MSG])
        self.assertEqual(len(form.errors), 1)

    def test_due_date_in_past(self):
        """Test a form with an invalid due date. Expect an error."""
        temp_data = self.quote_data.copy()
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        temp_data['quote_due_date'] = yesterday
        form = QuoteForm(data=temp_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['quote_due_date'],
            ['Date must be greater than or equal to today.'])
        self.assertEqual(len(form.errors), 1)

    def test_negative_copies(self):
        """Test a form with negative number of copies. Expect an error."""
        temp_data = self.quote_data.copy()
        temp_data['quote_copies'] = -1
        form = QuoteForm(data=temp_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['quote_copies'], [self.MIN_VAL_0_MSG])
        self.assertEqual(len(form.errors), 1)

    def test_zero_copies(self):
        """Test a form with zero copies. Expect no error."""
        temp_data = self.quote_data.copy()
        temp_data['quote_copies'] = 0
        form = QuoteForm(data=temp_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.errors), 0)

    def test_negative_quires(self):
        """Test a form with a negative number of quires. Expect an error."""
        temp_data = self.quote_data.copy()
        temp_data['quote_quires'] = -1
        form = QuoteForm(data=temp_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['quote_quires'], [self.MIN_VAL_0_MSG])
        self.assertEqual(len(form.errors), 1)

    def test_zero_quires(self):
        """Test a form with zero quires. Expect no error."""
        temp_data = self.quote_data.copy()
        temp_data['quote_quires'] = 0
        form = QuoteForm(data=temp_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.errors), 0)

    def test_blank_product_name(self):
        """Test a form missing product name. Expect an error."""
        temp_data = self.quote_data.copy()
        temp_data['quote_product_name'] = ""  # blank product name
        form = QuoteForm(data=temp_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['quote_product_name'], [self.REQ_MSG])
        self.assertEqual(len(form.errors), 1)

    def test_negative_job_width(self):
        """
        Test a form with a negative number for job width.
        Expect an error.
        """
        temp_data = self.quote_data.copy()
        temp_data['quote_dimention_width'] = -1
        form = QuoteForm(data=temp_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['quote_dimention_width'],
            ['This value must be greater than 0.'])
        self.assertEqual(len(form.errors), 1)

    def test_zero_job_width(self):
        """Test a form with zero for job width. Expect an error."""
        pass
        temp_data = self.quote_data.copy()
        temp_data['quote_dimention_width'] = 0
        form = QuoteForm(data=temp_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['quote_dimention_width'],
            ['This value must be greater than 0.'])
        self.assertEqual(len(form.errors), 1)

    def test_negative_job_length(self):
        """
        Test a form with a negativ number for job length.
        Expect an error.
        """
        temp_data = self.quote_data.copy()
        temp_data['quote_dimention_length'] = -1
        form = QuoteForm(data=temp_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['quote_dimention_length'],
            ['This value must be greater than 0.'])
        self.assertEqual(len(form.errors), 1)

    def test_zero_job_length(self):
        """Test a form with zero for job length. Expect an error."""
        temp_data = self.quote_data.copy()
        temp_data['quote_dimention_length'] = 0
        form = QuoteForm(data=temp_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['quote_dimention_length'],
            ['This value must be greater than 0.'])
        self.assertEqual(len(form.errors), 1)

    def test_negative_job_bleed(self):
        """
        Test a form with a negative number for job bleed.
        Expect an error.
        """
        temp_data = self.quote_data.copy()
        temp_data['quote_printing_bleed'] = -1
        form = QuoteForm(data=temp_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['quote_printing_bleed'],
            [self.MIN_VAL_0_MSG])
        self.assertEqual(len(form.errors), 1)

    def test_zero_job_bleed(self):
        """Test a form with zero for job bleed."""
        temp_data = self.quote_data.copy()
        temp_data['quote_printing_bleed'] = 0
        form = QuoteForm(data=temp_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.errors), 0)

    def test_negative_printing_sides(self):
        """Test a form with a negative number for printing sides.
        Expect an error.
        """
        temp_data = self.quote_data.copy()
        temp_data['quote_printing_sides'] = -1
        form = QuoteForm(data=temp_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['quote_printing_sides'],
            [self.MIN_VAL_0_MSG])
        self.assertEqual(len(form.errors), 1)

    def test_zero_printing_sides(self):
        """Test a form with zero for printing sides."""
        temp_data = self.quote_data.copy()
        temp_data['quote_printing_sides'] = 0
        form = QuoteForm(data=temp_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.errors), 0)

    def test_too_many_printing_sides(self):
        """
        Test a form with more than two (2) printing sides. Expect an error.
        """
        temp_data = self.quote_data.copy()
        temp_data['quote_printing_sides'] = 3
        form = QuoteForm(data=temp_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['quote_printing_sides'],
            ['Ensure this value is less than or equal to 2.'])
        self.assertEqual(len(form.errors), 1)

    def test_negative_colors_front(self):
        """
        Test a form with a negative number for printing colors front.
        Expect an error.
        """
        temp_data = self.quote_data.copy()
        temp_data['quote_printing_colors_front'] = -1
        form = QuoteForm(data=temp_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['quote_printing_colors_front'],
            [self.MIN_VAL_0_MSG])
        self.assertEqual(len(form.errors), 1)

    def test_negative_colors_back(self):
        """
        Test a form with a negative number for printing colors back.
        Expect an error.
        """
        temp_data = self.quote_data.copy()
        temp_data['quote_printing_colors_back'] = -1
        form = QuoteForm(data=temp_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['quote_printing_colors_back'],
            [self.MIN_VAL_0_MSG])
        self.assertEqual(len(form.errors), 1)

    def test_no_client_chosen(self):
        """Test a form with no client chosen. Expect an error."""
        temp_data = self.quote_data.copy()
        del temp_data['client']  # no client chosen
        form = QuoteForm(data=temp_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['client'], [self.REQ_MSG])
        self.assertEqual(len(form.errors), 1)

    def test_no_finishings_chosen(self):
        """Test a form with no finishings chosen. Expect an error."""
        temp_data = self.quote_data.copy()
        del temp_data['finishings']  # no finishings chosen
        form = QuoteForm(data=temp_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['finishings'], [self.REQ_MSG])
        self.assertEqual(len(form.errors), 1)

    def test_no_materials_chosen(self):
        """Test a form with no materials chosen. Expect an error."""
        temp_data = self.quote_data.copy()
        del temp_data['materials']  # no materials chosen
        form = QuoteForm(data=temp_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['materials'], [self.REQ_MSG])
        self.assertEqual(len(form.errors), 1)

    def test_no_paper_chosen(self):
        """Test a form with no paper chosen. Expect an error."""
        temp_data = self.quote_data.copy()
        del temp_data['paper']  # no paper chosen
        form = QuoteForm(data=temp_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['paper'], [self.REQ_MSG])
        self.assertEqual(len(form.errors), 1)
