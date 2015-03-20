import pytest

from pylisp import tokenize, parse, l_eval, Symbol


class TestTokenize(object):
    def test_tokenize_addition(self, addition_sexp):
        assert tokenize(addition_sexp) == ['(', '+', '2', '3', ')']

    def test_tokenize_subtraction(self, subtraction_sexp):
        assert tokenize(subtraction_sexp) == ['(', '-', '3', '2', ')']


class TestParse(object):
    def test_parse_addition(self, addition_sexp):
        parsed = parse(addition_sexp)
        assert parsed[1:] == [2, 3]
        assert isinstance(parsed[0], Symbol)
        assert parsed[0].value == '+'

    def test_parse_subtraction(self, subtraction_sexp):
        parsed = parse(subtraction_sexp)
        assert parsed[1:] == [3, 2]
        assert isinstance(parsed[0], Symbol)
        assert parsed[0].value == '-'

    def test_parse_too_many_close(self):
        with pytest.raises(SyntaxError):
            parse('())')


class TestEval(object):
    def test_eval_addition(self, addition_sexp):
        assert l_eval(parse(addition_sexp)) == 5

    def test_eval_subtraction(self, subtraction_sexp):
        assert l_eval(parse(subtraction_sexp)) == 1

    def test_factorial(self, factorial_sexp):
        assert l_eval(parse(factorial_sexp)) == 720
