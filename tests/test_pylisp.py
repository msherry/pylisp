from pylisp import tokenize, l_eval


class TestEval(object):

    def test_tokenize_addition(self, addition_sexp):
        assert tokenize(addition_sexp) == ['(', '+', '2', '3', ')']

    def test_tokenize_subtraction(self, subtraction_sexp):
        assert tokenize(subtraction_sexp) == ['(', '-', '3', '2', ')']

    def test_eval_addition(self, addition_sexp):
        assert l_eval(addition_sexp) == 5

    def test_eval_subtraction(self, subtraction_sexp):
        assert l_eval(subtraction_sexp) == 1
