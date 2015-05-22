import urllib

from itertools import chain


def format_range(values):
    """Attempts to present the given range in a human-readable format

    >>> format_range([1])
    '1'
    >>> format_range([1,2,3])
    '1:3'
    >>> format_range([1,2,3,5,6])
    '1:3,5:6'
    >>> format_range([1,2,3,5,6,8,10])
    '1:3,5:6,8,10'
    """

    if hasattr(values, "values_list"):
        # We need iter here because values_list returns a special QuerySet
        # object, not a list.
        return format_range(iter(values.values_list("number", flat=True)))

    values = iter(values)
    beginning = end = None

    def _iter(values):
        # We use _iter here to mutate values
        prev = values.next()
        while True:
            try:
                current = values.next()
            except StopIteration, e:
                yield prev, None
                raise e
            yield prev, current
            prev = current

    for prev, current in _iter(values):
        if not beginning:
            beginning = end = prev
        if current:
            if prev == current - 1:
                end = current
            else:
                break
    if beginning is not None:
        if beginning == end:
            this_range = str(beginning)
        else:
            this_range = "{}:{}".format(beginning, end)
        extra = format_range(chain([current], values))
        if extra:
            return "{},{}".format(this_range, extra)
        else:
            return this_range


QR_CODE_URL_TEMPLATE = ("https://chart.googleapis.com/chart?cht=qr"
                        "&chs={size}x{size}&chl={data}")


def qr_code_from_url(relative_url, request=None, size=500):
    if request:
        url = request.build_absolute_uri(relative_url)
    else:
        url = relative_url
    return QR_CODE_URL_TEMPLATE.format(size=size, data=urllib.quote_plus(url))
