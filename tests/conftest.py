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
                  (* x (fact2 (- x 1))))))'''


@pytest.fixture
def fibonacci_sexp():
    # fib is a default proc, so we define an identical fib2
    return '''(define fib2 (lambda (x)
                (if (< x 2) x
                   (+ (fib2 (- x 1)) (fib2 (- x 2))))))'''


@pytest.fixture
def memoized_fib_sexp():
    return '''(let ((memo (make-hash-table)))
                (define memo-fib (lambda (x)
                  (if (gethash x memo)
                    (gethash x memo)
                    (set (gethash x memo)
                      (if (< x 2) x
                        (+ (memo-fib (- x 1)) (fib (- x 2)))))))))'''


def memoize_sexp():
    return """(defmacro memoize (func)
                '(lambda (x)
                  (let (( memo (make-hash-table)))
                     (if (gethash x 'memo) (gethash x 'memo)
                       (setf (gethash x 'memo) (func x))))))) """
