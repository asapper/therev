import math

def get_imposing(quote):
    """Return the number of jobs that can fit in the chosen paper."""
    paper_width = quote.paper.paper_width
    paper_length = quote.paper.paper_length
    job_width = quote.quote_dimention_width
    job_length = quote.quote_dimention_length
    job_bleed = quote.quote_printing_bleed
    num_copies = quote.quote_copies

    results = []
    results = calculate_impose(paper_width, paper_length, job_width,
            job_length, job_bleed)
    results.sort(reverse=True)
    best_result = results[0]
    # display results
    for imposing in results:
        sheets = math.ceil(num_copies / imposing)
        print(">>> Fit: {}; Sheets: {}".format(imposing, sheets))

    return best_result


def calculate_impose(paper_width, paper_length, job_width, job_length,
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
    total_method_1 = do_impose(
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
    total_method_2 = do_impose(
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


def do_impose(paper_min, paper_max, job_width, job_length, job_bleed,
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
            leftover_imp = calculate_impose(
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
            leftover_imp = calculate_impose(
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
