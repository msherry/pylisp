[![Build Status](https://travis-ci.org/msherry/pylisp.svg?branch=master)](https://travis-ci.org/msherry/pylisp)
# pylisp
The obligatory Lisp-in-Python project. Trying not to steal too much from Norvig's implementation.

```lisp
[1] > (define fact
...     (lambda (x)
...       (cond ((<= x 2) x)
...         (True (* x (fact (- x 1)))))))
[1] fact

[2] > (fact 6)
[2] 720
```
