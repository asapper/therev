from django import template


register = template.Library()

@register.filter
def humanize_seconds(value):
    """
    Returns the given seconds in hours, minutes humanized.
    """
    hours, remainder = divmod(value, 3600)
    minutes, seconds = divmod(remainder, 60)
    finalStr = ""  # store final sentence
    tmpStr = ""  # store singular/plural of hour/minute
    # hours in time calculated?
    if hours > 0:
        # include days
        days = int(hours / 24)
        hours -= days * 24
        if days > 0:
            if days == 1:
                tmpStr = "día"
            else:
                tmpStr = "días"
            finalStr += "{} {}, ".format(days, tmpStr)
        if hours > 0:
            # include hours
            tmpStr= "horas"
            if hours == 1:  # singular form
                tmpStr = "hora"
            finalStr += "{} {}, ".format(int(hours), tmpStr)
    # minutes in time calculated?
    if minutes >= 0:
        if seconds >= 30:  # round minutes
            minutes += 1
        tmpStr = "minutos"
        if minutes == 1:  # singular form
            tmpStr = "minuto"
        finalStr += "{} {}".format(int(minutes), tmpStr)
    return finalStr
