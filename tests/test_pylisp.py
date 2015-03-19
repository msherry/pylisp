from pylisp import tokenize, parse


class TestEval(object):

    def test_tokenize_addition(self, addition_sexp):
        assert tokenize(addition_sexp) == ['(', '+', '2', '3', ')']
