from __future__ import unicode_literals

RED = '\x1b[31m{}\x1b[0m'
GREEN = '\x1b[32m{}\x1b[0m'


def red(s):
    return RED.format(s)


def green(s):
    return GREEN.format(s)
