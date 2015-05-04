from __future__ import unicode_literals


def atom(x):
    from environments import Symbol
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            return Symbol(x)


def tokenize(chars):
    special = '()"\''
    for s in special:
        chars = chars.replace(s, ' {} '.format(s))
    return chars.split()


def parse(expr):
    return read_from_tokens(tokenize(expr))


def read_from_tokens(tokens, level=0):
    if not tokens:
        raise SyntaxError('No input')
    ret = None
    t = tokens.pop(0)
    quote = False
    if t == "'":
        quote = True
        t = tokens.pop(0)
    if t == '"':
        L = []
        while tokens[0] != '"':
            L.append(tokens.pop(0))
        # Pop off final '"'
        tokens.pop(0)
        ret = ' '.join(L)
    elif t == '(':
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens, level=level + 1))
        # Pop off final ')'
        tokens.pop(0)
        if level == 0 and tokens:
            raise SyntaxError('Unexpected data after parse: {}'.format(
                ' '.join(tokens)))
        ret = L
    elif t == ')':
        raise SyntaxError('Unexpected ")"')
    else:
        ret = atom(t)

    if quote:
        ret = ['quote', ret]
    return ret
