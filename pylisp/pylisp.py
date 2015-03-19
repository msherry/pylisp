from __future__ import unicode_literals


def tokenize(chars):
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()
