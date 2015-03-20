from __future__ import unicode_literals

RED = '\x1b[31m{}\x1b[0m'
GREEN = '\x1b[32m{}\x1b[0m'
BLUE = '\x1b[34m{}\x1b[0m'


class Colors(object):

    @staticmethod
    def red(s):
        return RED.format(s)

    @staticmethod
    def green(s):
        return GREEN.format(s)

    @staticmethod
    def blue(s):
        return BLUE.format(s)


def parens_balanced(lines):
    text = ' '.join(lines)
    count = 0
    for c in text:
        if c == '(':
            count += 1
        elif c == ')':
            count -= 1
            if count < 0:
                raise SyntaxError('Unexpected ")"')
    return count == 0
