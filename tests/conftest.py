import pytest


@pytest.fixture
def addition_sexp():
    return '(+ 2 3)'

@pytest.fixture
def subtraction_sexp():
    return '(- 3 2)'

@pytest.fixture
def factorial_sexp():
    return '(- 3 2)'

@pytest.fixture
def true_sexp():
    return '(= 7 7)'

@pytest.fixture
def false_sexp():
    return '(= 8 7)'
