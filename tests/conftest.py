import pytest


@pytest.fixture
def addition_sexp():
    return '(+ 2 3)'


@pytest.fixture
def subtraction_sexp():
    return '(- 3 2)'


@pytest.fixture
def true_sexp():
    return '(= 7 7)'


@pytest.fixture
def false_sexp():
    return '(= 8 7)'


@pytest.fixture
def factorial_sexp():
    # fact is a default proc, so we define an identical fact2
    return '''(define fact2 (lambda (x)
                (if (< x 2) x
                  (* x (fact (- x 1))))))'''


@pytest.fixture
def fibonacci_sexp():
    # fib is a default proc, so we define an identical fib2
    return '''(define fib2 (lambda (x)
                (if (< x 2) x
                   (+ (fib (- x 1)) (fib (- x 2))))))'''
