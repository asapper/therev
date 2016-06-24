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
    hasHours = False  # used to format minutes
    # hours in time calculated?
    if hours > 0:
        hasHours = True  # for use in formatting minutes
        tmpStr= "horas"
        if hours == 1:  # singular form
            tmpStr = "hora"
        finalStr += "{} {}".format(hours, tmpStr)
    # minutes in time calculated?
    if minutes >= 0:
        if seconds >= 30:  # round minutes
            minutes += 1
        if hasHours is True:  # format correctly
            finalStr += ", "
        tmpStr = "minutos"
        if minutes == 1:  # singular form
            tmpStr = "minuto"
        finalStr += "{} {}".format(int(minutes), tmpStr)
    return finalStr
