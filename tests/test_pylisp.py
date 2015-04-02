import pytest

from pylisp import tokenize, parse, l_eval, Symbol, Procedure


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

    def test_eval_true(self, true_sexp):
        assert l_eval(parse(true_sexp)) == True

    def test_eval_false(self, false_sexp):
        assert l_eval(parse(false_sexp)) == None   # Not False

    def test_factorial(self, factorial_sexp):
        # Define fact
        l_eval(parse(factorial_sexp))
        assert l_eval(parse('(fact 6)')) == 720

    def test_fibonacci(self, fibonacci_sexp):
        # Define fib
        l_eval(parse(fibonacci_sexp))
        assert l_eval(parse('(fib 0)')) == 0
        assert l_eval(parse('(fib 1)')) == 1
        assert l_eval(parse('(fib 2)')) == 1
        assert l_eval(parse('(fib 3)')) == 2
        assert l_eval(parse('(fib 4)')) == 3
        assert l_eval(parse('(fib 5)')) == 5


class TestBuiltins(object):
    def test_and(self):
        assert l_eval(parse('(and)')) == True
        assert l_eval(parse('(and True True)')) == True
        assert l_eval(parse('(and True None)')) == None
        assert l_eval(parse('(and None)')) == None
        assert l_eval(parse('(and (= 2 2) (> 2 1))')) == True
        assert l_eval(parse('(and (= 2 2) (< 2 1))')) == None
        assert l_eval(parse("(and 1 2 'c '(f g))")) == l_eval(parse("'(f g)"))

    def test_or(self):
        assert l_eval(parse('(or)')) == None
        assert l_eval(parse('(or True True)')) == True
        assert l_eval(parse('(or True None)')) == True
        assert l_eval(parse('(or None)')) == None
        assert l_eval(parse('(or (= 2 2) (> 2 1))')) == True
        assert l_eval(parse('(or (= 2 2) (< 2 1))')) == True
        assert l_eval(parse("(or 1 2 'c '(f g))")) == 1

    def test_quote(self):
        ret = l_eval(parse('(quote (x y z))'))
        assert len(ret) == 3
        assert all(isinstance(x, Symbol) for x in ret)
        assert [x.value for x in ret] == ['x', 'y', 'z']
        assert l_eval(parse("'(x y z)")) == l_eval(parse('(quote (x y z))'))

    def test_lambda(self):
        fn = l_eval(parse('(lambda (x y) (* x y))'))
        assert isinstance(fn, Procedure)

    def test_define(self):
        fn = l_eval(parse('(define poop (lambda (x y) (* x y)))'))
        assert isinstance(fn, Symbol)
        assert fn.value == 'poop'
        assert l_eval(parse('(poop 8 7)')) == 56

    def test_cond(self):
        sexp = '''(define condfun (lambda (x)
                    (cond ((< x 10) (* x 7))
                          ((> x 10) (/ x 7))
                          (True 7))))
        '''
        l_eval(parse(sexp))
        assert l_eval(parse('(condfun 2)')) == 14
        assert l_eval(parse('(condfun 3)')) == 21
        assert l_eval(parse('(condfun 14)')) == 2
        assert l_eval(parse('(condfun 21)')) == 3
        assert l_eval(parse('(condfun 10)')) == 7

    def test_let(self):
        l_eval(parse('(define x 10)'))
        assert (l_eval(parse('x'))) == 10
        assert l_eval(parse('(let ((x 22)) x)')) == 22
        assert (l_eval(parse('x'))) == 10

    def test_closure(self):
        l_eval(parse('''(define closure_func
                          (let ((x 10))
                            (lambda (y) (^ x y))))'''))
        assert l_eval(parse('(closure_func 1)')) == 10
        assert l_eval(parse('(closure_func 2)')) == 100
        # External defines don't affect value of x inside closure
        l_eval(parse('(define x 20)'))
        assert l_eval(parse('(closure_func 1)')) == 10
        assert l_eval(parse('(closure_func 2)')) == 100
        assert l_eval(parse('x')) == 20

    def test_one_arg_map(self, fibonacci_sexp):
        l_eval(parse(fibonacci_sexp))
        assert (l_eval(parse(
            "(map fib '(0 1 2 3 4 5 6 7 8 9 10))")) ==
                [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 65])

    def test_two_arg_map(self):
        assert (l_eval(parse(
            "(map (lambda (x y) (* x y)) '(1 2 3) '(9 20 7))")) == [9, 40, 21])
