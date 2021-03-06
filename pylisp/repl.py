from __future__ import unicode_literals

import readline

from utils import Colors, parens_balanced


# TODO: http://pymotw.com/2/readline/
# Use readline for completing function names
readline.parse_and_bind('tab: complete')
readline.parse_and_bind('set editing-mode emacs')


def global_parse_and_eval(expr):
    from environments import global_env
    from read import parse

    return global_env.eval(parse(expr))


def read_loop():
    from environments import global_env
    from read import parse
    try:
        readline.read_history_file('.pylisp_history')
    except IOError:
        pass
    count = 1
    complete_expr = []
    indent = 0
    while True:
        try:
            prompt = ((Colors.red('[{}]'.format(count)) + ' > ') if not
                      complete_expr else '...   ' + '  ' * indent)
            try:
                expr = raw_input(prompt)
            except EOFError:
                break
            if not expr:
                continue
            # Complete sexp, or multi-line entry?
            complete_expr.append(expr)
            balanced, indent = parens_balanced(complete_expr)
            if balanced:
                # Complete sexp, try to eval
                try:
                    expr = ' '.join(complete_expr)
                    complete_expr = []
                    ret = global_env.eval(parse(expr))
                except Exception, e:                    # pylint: disable=W0703
                    print 'Error: {}'.format(e)
                    continue
                print Colors.green('[{}]'.format(count)) + ' {}'.format(ret)
                print
                count += 1
            else:
                # Incomplete sexp, still building
                continue
        except KeyboardInterrupt:
            print 'KeyboardInterrupt'
            continue
    print
    readline.write_history_file('.pylisp_history')
