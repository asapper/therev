import math

from django.utils import timezone

from .models import Order, Quote_Finishing


class OrderController():
    @classmethod
    def create_order(cls, quote, pack_inst, delivery_addr, notes):
        """Approve given Quote and create an Order based on that quote."""
        if (quote.quote_is_authorized is True and
                quote.quote_is_approved is False):
            error = False
            try:
                order = Order.objects.create(
                    quote=quote,
                    order_packaging_instructions=pack_inst,
                    order_delivery_address=delivery_addr,
                    order_notes=notes)
            except IntegrityError:
                error = True
            if error is False:
                quote.set_approved()
                return order

    @classmethod
    def start_order(cls, order):
        """
        Starts the given order by calling the order's set_started function.
        """
        # verify order is not started already
        if order.order_is_started is False:
            order.set_started()  # function handles assignment
        else:
            # order already started
            return "Order already started"

    @classmethod
    def finish_order(cls, order):
        """
        Finish the given order by calling the order's set_finished function.
        """
        # verify order is already started
        if order.order_is_started is True:
            # verify order is not finished already
            if order.order_is_finished is False:
                # verify all finishings are finished
                quote_id = order.get_quote_id()
                for finishing in order.get_finishings():
                    q_fin_instance = Quote_Finishing.objects.get(
                        quote_id=quote_id,
                        finishing_id=finishing.id)
                    if q_fin_instance.get_is_finished() is False:
                        return "Not all finishings are finished"
                order.set_finished()  # function handles assignment
            else:  # order already finished
                return "Order already finished"
        else:  # order not yet started
            return "Order not started"

    @classmethod
    def start_finishing(cls, quote_finishing_instance):
        """
        Starts the given finishing by calling
        the quote_finishing's set_started function.
        """
        # verify quote finishing is not started
        if quote_finishing_instance.get_is_started() is False:
            # function handles assignment
            quote_finishing_instance.set_started()
        else:
            return "Finishing already started"

    @classmethod
    def finish_finishing(cls, quote_finishing_instance):
        """
        Finish the given finishing by calling
        the quote_finishing's set_finished function.
        """
        # verify quote finishing is started and not finished
        if quote_finishing_instance.get_is_started() is True:
            if quote_finishing_instance.get_is_finished() is False:
                # function handles assignment
                quote_finishing_instance.set_finished()
            else:
                return "Finishing already finished"
        else:
            return "Finishing not started"


class QuoteController():
    @classmethod
    def authorize_quote(cls, quote):
        """Authorize given Quote."""
        if quote.quote_is_authorized is False:
            if quote.quote_is_approved is False:
                quote.set_authorized()  # authorize quote
            else:  # quote approved
                return "Quote already approved"
        else:
            return "Quote already authorized"

    @classmethod
    def get_total_price(cls, quote):
        """Return the total price for all processes in a Quote."""
        # get materials price
        total_materials_price = 0
        for material in quote.materials.all():
            total_materials_price += material.material_price
        # get finishings price
        total_finishings_price = 0
        for finishing in quote.finishings.all():
            total_finishings_price += finishing.finishing_price
        # get paper price
        paper_price = quote.paper.paper_price
        # calculate total price
        sheets = quote.quote_total_sheets
        total_price = sheets * total_materials_price
        total_price += sheets * total_finishings_price
        total_price += sheets * paper_price
        return total_price

    @classmethod
    def get_imposing(cls, quote):
        """Return the number of jobs that can fit in the chosen paper."""
        paper_width = quote.paper.paper_width
        paper_length = quote.paper.paper_length
        job_width = quote.quote_dimention_width
        job_length = quote.quote_dimention_length
        job_bleed = quote.quote_printing_bleed
        num_copies = quote.quote_copies * quote.quote_quires

        results = []
        results = _calculate_impose(paper_width, paper_length, job_width,
                                   job_length, job_bleed)

        results.sort(reverse=True)
        best_result = results[0]
        if best_result == 0:
            best_sheets = 0
        else:
            best_sheets = math.ceil(num_copies / best_result)
        return best_result, best_sheets


def _calculate_impose(paper_width, paper_length, job_width, job_length,
                     job_bleed):
    """
    Calculate ways to impose job in the given paper and call
    helper function to do the imposing.
    """
    results = []  # store results of imposing
    paper_min = min(paper_width, paper_length)
    paper_max = max(paper_width, paper_length)
    job_min = min(job_width, job_length)
    job_max = max(job_width, job_length)

    job_total_min = job_min + (2 * job_bleed)
    job_total_max = job_max + (2 * job_bleed)

    max_side = int(paper_max / job_total_min)
    min_side = int(paper_min / job_total_max)
    max_final = job_total_min * max_side
    min_final = job_total_max * min_side
    max_leftover = paper_max - max_final
    min_leftover = paper_min - min_final

    # call method 1
    total_method_1 = _do_impose(
        paper_min,
        paper_max,
        job_width,
        job_length,
        job_bleed,
        job_total_min,
        job_total_max,
        max_side,
        min_side,
        max_final,
        min_final,
        max_leftover,
        min_leftover)

    # append to results
    results.append(total_method_1)

    max_side = int(paper_max / job_total_max)
    min_side = int(paper_min / job_total_min)
    max_final = job_total_max * max_side
    min_final = job_total_min * min_side
    max_leftover = paper_max - max_final
    min_leftover = paper_min - min_final

    # call method 2
    total_method_2 = _do_impose(
        paper_min,
        paper_max,
        job_width,
        job_length,
        job_bleed,
        job_total_min,
        job_total_max,
        max_side,
        min_side,
        max_final,
        min_final,
        max_leftover,
        min_leftover)

    # append to results
    results.append(total_method_2)
    return results


def _do_impose(paper_min, paper_max, job_width, job_length, job_bleed,
              job_total_min, job_total_max, max_side, min_side, max_final,
              min_final, max_leftover, min_leftover):
    """Do the imposing of the given job in the given paper."""

    # store imposing so far
    imp_total = max_side * min_side

    # imposed in given area
    if max_final > 0 and min_final > 0:
        # Impose in lefotover area
        if ((job_total_max <= max_leftover and job_total_min <= paper_min) or
                ((job_total_min <= max_leftover and
                  job_total_max <= paper_min))):
            # to store leftover imposing
            leftover_imp = []
            # impose on leftover area
            leftover_imp = _calculate_impose(
                paper_min,  # paper width
                max_leftover,  # paper length
                job_width,
                job_length,
                job_bleed)

            # loop over leftover results
            for imp in leftover_imp:
                if imp > 0:
                    imp_total += imp

        elif ((job_total_max <= min_leftover and job_total_min <= paper_max) or
                ((job_total_min <= min_leftover and
                    job_total_max <= paper_max))):
            # store leftover imposing
            leftover_imp = []
            # impose on leftover area
            leftover_imp = _calculate_impose(
                paper_max,  # paper width
                min_leftover,  # paper length
                job_width,
                job_length,
                job_bleed)

            # loop over leftover results
            for imp in leftover_imp:
                if imp > 0:
                    imp_total += imp

    return imp_total
