import pytest

from pylisp import tokenize, parse, Symbol, Procedure, global_parse_and_eval
from pylisp.environments import reset_global_env


class PylispTestCase(object):
    def setup_method(self, _method):
        reset_global_env()


class TestTokenize(PylispTestCase):
    def test_tokenize_addition(self, addition_sexp):
        assert tokenize(addition_sexp) == ['(', '+', '2', '3', ')']

    def test_tokenize_subtraction(self, subtraction_sexp):
        assert tokenize(subtraction_sexp) == ['(', '-', '3', '2', ')']

    def test_tokenize_fibonacci(self, fibonacci_sexp):
        assert len(tokenize(fibonacci_sexp)) == 38


class TestParse(PylispTestCase):
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


class TestEval(PylispTestCase):
    def test_eval_addition(self, addition_sexp):
        assert global_parse_and_eval(addition_sexp) == 5

    def test_eval_subtraction(self, subtraction_sexp):
        assert global_parse_and_eval(subtraction_sexp) == 1

    def test_eval_true(self, true_sexp):
        assert global_parse_and_eval(true_sexp) == True

    def test_eval_false(self, false_sexp):
        assert global_parse_and_eval(false_sexp) == None   # Not False

    def test_factorial(self, factorial_sexp):
        # Define fact
        global_parse_and_eval(factorial_sexp)
        assert global_parse_and_eval('(fact2 6)') == 720

    def test_env_not_recycled_part_1(self):
        global_parse_and_eval('(define junk_fun (lambda (x) (* 2 x)))')
        assert global_parse_and_eval('(junk_fun 4)') == 8

    def test_env_not_recycled_part_2(self):
        with pytest.raises(ValueError):
            global_parse_and_eval('(junk_fun 4)')

    def test_fibonacci(self, fibonacci_sexp):
        # Define fib
        global_parse_and_eval(fibonacci_sexp)
        assert global_parse_and_eval('(fib2 0)') == 0
        assert global_parse_and_eval('(fib2 1)') == 1
        assert global_parse_and_eval('(fib2 2)') == 1
        assert global_parse_and_eval('(fib2 3)') == 2
        assert global_parse_and_eval('(fib2 4)') == 3
        assert global_parse_and_eval('(fib2 5)') == 5

    @pytest.mark.xfail
    @pytest.mark.timeout(2)
    def test_fast_fibonacci(self, fibonacci_sexp):
        global_parse_and_eval(fibonacci_sexp)
        assert global_parse_and_eval('(fib2 50)') == 0


class TestEnvironments(PylispTestCase):
    def test_std_procs(self):
        assert global_parse_and_eval('(fact 6)') == 720
        assert global_parse_and_eval('(fib 6)') == 8


class TestBuiltins(PylispTestCase):
    def test_and(self):
        assert global_parse_and_eval('(and)') == True
        assert global_parse_and_eval('(and True True)') == True
        assert global_parse_and_eval('(and True None)') == None
        assert global_parse_and_eval('(and None)') == None
        assert global_parse_and_eval('(and (= 2 2) (> 2 1))') == True
        assert global_parse_and_eval('(and (= 2 2) (< 2 1))') == None
        assert (global_parse_and_eval("(and 1 2 'c '(f g))") ==
                global_parse_and_eval("'(f g)"))

    def test_or(self):
        assert global_parse_and_eval('(or)') == None
        assert global_parse_and_eval('(or True True)') == True
        assert global_parse_and_eval('(or True None)') == True
        assert global_parse_and_eval('(or None)') == None
        assert global_parse_and_eval('(or (= 2 2) (> 2 1))') == True
        assert global_parse_and_eval('(or (= 2 2) (< 2 1))') == True
        assert global_parse_and_eval("(or 1 2 'c '(f g))") == 1

    def test_quote(self):
        ret = global_parse_and_eval('(quote (x y z))')
        assert len(ret) == 3
        assert all(isinstance(x, Symbol) for x in ret)
        assert [x.value for x in ret] == ['x', 'y', 'z']
        assert (global_parse_and_eval("'(x y z)") ==
                global_parse_and_eval('(quote (x y z))'))

    def test_lambda(self):
        fn = global_parse_and_eval('(lambda (x y) (* x y))')
        assert isinstance(fn, Procedure)

    def test_define(self):
        fn = global_parse_and_eval('(define poop (lambda (x y) (* x y)))')
        assert isinstance(fn, Symbol)
        assert fn.value == 'poop'
        assert global_parse_and_eval('(poop 8 7)') == 56

    def test_define_works_only_once(self):
        global_parse_and_eval('(define poop (lambda (x y) (* x y)))')
        with pytest.raises(Exception):
            global_parse_and_eval('(define poop (lambda (x y) (* x y)))')

    def test_set(self):
        with pytest.raises(ValueError):
            global_parse_and_eval('x')
        with pytest.raises(ValueError):
            global_parse_and_eval("(set 'x 7)")
        global_parse_and_eval('(define x 7)')
        assert global_parse_and_eval('(= x 7)') == True
        global_parse_and_eval("(set 'x 8)")
        assert global_parse_and_eval('(= x 8)') == True

    def test_cond(self):
        sexp = '''(define condfun (lambda (x)
                    (cond ((< x 10) (* x 7))
                          ((> x 10) (/ x 7))
                          (True 7))))
        '''
        global_parse_and_eval(sexp)
        assert global_parse_and_eval('(condfun 2)') == 14
        assert global_parse_and_eval('(condfun 3)') == 21
        assert global_parse_and_eval('(condfun 14)') == 2
        assert global_parse_and_eval('(condfun 21)') == 3
        assert global_parse_and_eval('(condfun 10)') == 7

    def test_let(self):
        global_parse_and_eval('(define x 10)')
        assert global_parse_and_eval('x') == 10
        assert global_parse_and_eval('(let ((x 22)) x)') == 22
        assert global_parse_and_eval('(let ((x 22) (y 11)) (* x y))') == 242
        assert global_parse_and_eval('x') == 10

    def test_let_no_body(self):
        assert global_parse_and_eval('(let ((x 10)))') == None

    def test_let_forms(self):
        assert global_parse_and_eval('(let ()) 7') == 7

    def test_seq(self):
        assert (global_parse_and_eval('(seq 10)') ==
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        assert global_parse_and_eval('(seq 5 10)') == [5, 6, 7, 8, 9]

    def test_closure(self):
        global_parse_and_eval('''(define closure_func
                          (let ((x 10))
                            (lambda (y) (^ x y))))''')
        assert global_parse_and_eval('(closure_func 1)') == 10
        assert global_parse_and_eval('(closure_func 2)') == 100
        # External defines don't affect value of x inside closure
        global_parse_and_eval('(define x 20)')
        assert global_parse_and_eval('(closure_func 1)') == 10
        assert global_parse_and_eval('(closure_func 2)') == 100
        assert global_parse_and_eval('x') == 20

    def test_one_arg_map(self, fibonacci_sexp):
        global_parse_and_eval(fibonacci_sexp)
        assert (global_parse_and_eval("(map fib2 '(0 1 2 3 4 5 6 7 8 9 10))")
                == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55])

    def test_two_arg_map(self):
        assert (global_parse_and_eval(
            "(map (lambda (x y) (* x y)) '(1 2 3) '(9 20 7))") == [9, 40, 21])
