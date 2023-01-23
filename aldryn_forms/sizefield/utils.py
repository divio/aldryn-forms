import operator
import re
import sys

from django.conf import settings
from django.utils import formats
from django.utils.translation import ugettext as _


if sys.version_info >= (3, 0):
    xrange = range

SIZEFIELD_FORMAT = getattr(settings, 'SIZEFIELD_FORMAT', '{value}{unit}')

file_size_re = re.compile(r'^(?P<value>[0-9\.,]+?)\s*(?P<unit>[KMGTPEZY]?B?)$', re.IGNORECASE)
FILESIZE_UNITS = {
    'B': 1,
    'KB': 1 << 10,
    'MB': 1 << 20,
    'GB': 1 << 30,
    'TB': 1 << 40,
    'PB': 1 << 50,
    'EB': 1 << 60,
    'ZB': 1 << 70,
    'YB': 1 << 80,
}


def filesizeformat(bytes, decimals=1):
    """
    Formats the value like a 'human-readable' file size (i.e. 13 KB, 4.1 MB,
    102 bytes, etc).
    Based on django.template.defaultfilters.filesizeformat
    """

    try:
        bytes = float(bytes)
    except (TypeError, ValueError, UnicodeDecodeError):
        raise ValueError

    def filesize_number_format(value):
        return formats.number_format(round(value, decimals), decimals)

    units_list = sorted(FILESIZE_UNITS.items(), key=operator.itemgetter(1))

    value = unit = None
    len_unints_list = len(units_list)
    for i in xrange(1, len_unints_list):
        if bytes < units_list[i][1]:
            prev_unit = units_list[i - 1]
            value = filesize_number_format(bytes / prev_unit[1])
            unit = prev_unit[0]
            break

    if value is None:
        value = filesize_number_format(bytes / units_list[-1][1])
        unit = units_list[-1][0]

    return SIZEFIELD_FORMAT.format(value=value, unit=unit)


def parse_size(size):
    """
    @rtype int
    """
    if isinstance(size, int):
        return size

    r = file_size_re.match(size.strip())
    if r:
        clean_value = r.group("value").replace(",", ".")
        value = float(clean_value)
        unit = r.group('unit').upper()
        if not unit.endswith('B'):
            unit += 'B'
        return int(value * FILESIZE_UNITS[unit])

    # Regex pattern was not matched
    raise ValueError(_("Size '%s' has incorrect format") % size)
