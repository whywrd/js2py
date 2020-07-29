from ply import lex, yacc
import ast
import re

"""
Lexer and parser implementation. The parser outputs a python AST which
can be compiled and executed.

Documentation for lexers and parsers in python can be found here:
http://dabeaz.com/ply/ply.html
"""

# Tokens that input strings are compared against.
# All valid syntax must be constructable from these tokens.
tokens = ('ID',
          'ASSIGN',
          'NUMBER',
          'PLUS',
          'MINUS',
          'GTHAN',
          'EQUALTO',
          'AND',
          'OR',
          'LPAREN',
          'RPAREN',
          'LBRACE',
          'RBRACE',
          'SUBSCRIPT',
          'TRUE',
          'FALSE',
          'STR',
          'ID',
          'IF',
          'ELSE')

# regular expression rules for simple tokens
t_PLUS = r'\+'
t_MINUS = r'\-'
t_ASSIGN = '='
t_GTHAN = r'\>'
t_EQUALTO = r'=='
t_LBRACE = '{'
t_RBRACE = '}'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_AND = r'\&\&'
t_OR = r'\|\|'
t_TRUE = 'true'
t_FALSE = 'false'
t_SUBSCRIPT = r'\.'
t_IF = 'if'
t_ELSE = 'else'

# Words with special meanings. If these weren't reserved
# they would be consumed by the ID re
reserved = {
    'true': 'TRUE',
    'false': 'FALSE',
    'if': 'IF',
    'else': 'ELSE'
}


# Regular expression rules with some logic
# Need to make sure ID does not consume reserved words
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t


def t_NUMBER(t):
    r'\d+'
    t.type = 'NUMBER'
    t.value = int(t.value)
    return t


def t_STR(t):
    r'\"[^\"]*\"'
    p = re.compile('\"([^\"]*)\"')
    r = re.search(p, t.value)
    t.type = 'STR'
    t.value = r.group(1)
    return t


# characters to ignore (tabs and spaces)
t_ignore = ' \t'


def p_expression_assignment(p):
    'expression : ID ASSIGN expression'
    p[0] = ast.Assign(targets=[ast.Name(id=p[1], ctx=ast.Store(), lineno=p.lineno(1), col_offset=p.lexpos(1))],
                      value=p[3],
                      lineno=p.lineno(1), col_offset=p.lexpos(1))


def p_expression_if(p):
    'expression : IF LPAREN expression RPAREN LBRACE expression RBRACE'
    p[0] = ast.If(test=p[3],
                  body=[p[6]],
                  orelse=[],
                  lineno=p.lineno(1),
                  col_offset=p.lexpos(1))


def p_expression_if_else(p):
    'expression : IF LPAREN expression RPAREN LBRACE expression RBRACE ELSE LBRACE expression RBRACE'
    p[0] = ast.If(test=p[3],
                  body=[p[6]],
                  orelse=[p[10]],
                  lineno=p.lineno(1),
                  col_offset=p.lexpos(1))


def p_store_subscript(p):
    'expression : ID SUBSCRIPT ID ASSIGN expression'
    target0 = ast.Subscript(value=ast.Name(id=p[1], ctx=ast.Load(), lineno=p.lineno(1), col_offset=p.lexpos(1)),
                            slice=ast.Index(value=ast.Str(s=p[3], lineno=p.lineno(3), col_offset=p.lexpos(3))),
                            ctx=ast.Store(),
                            lineno=p.lineno(1), col_offset=p.lexpos(1))
    p[0] = ast.Assign(targets=[target0],
                      value=p[5],
                      ctx=ast.Store(),
                      lineno=p.lineno(5), col_offset=p.lexpos(5))


def p_load_subscript(p):
    'expression : ID SUBSCRIPT ID'
    p[0] = ast.Subscript(value=ast.Name(id=p[1], ctx=ast.Load(), lineno=p.lineno(1), col_offset=p.lexpos(1)),
                         slice=ast.Index(value=ast.Str(s=p[3], lineno=p.lineno(3), col_offset=p.lexpos(3))),
                         ctx=ast.Load(),
                         lineno=p.lineno(1), col_offset=p.lexpos(1))


def p_expression_plus(p):
    'expression : expression PLUS term'
    p[0] = ast.BinOp(p[1],
                     ast.Add(lineno=p.lineno(2), col_offset=p.lexpos(2)),
                     p[3],
                     lineno=p.lineno(1), col_offset=p.lexpos(1))


def p_expression_minus(p):
    'expression : expression MINUS term'
    p[0] = ast.BinOp(p[1],
                     ast.Sub(lineno=p.lineno(2), col_offset=p.lexpos(2)),
                     p[3],
                     lineno=p.lineno(1), col_offset=p.lexpos(1))


def p_expression_gthan(p):
    'expression : expression GTHAN term'
    p[0] = ast.Compare(left=p[1],
                       ops=[ast.Gt()],
                       comparators=[p[3]],
                       lineno=p.lineno(1), col_offset=p.lexpos(1))


def p_expression_equal_to(p):
    'expression : expression EQUALTO term'
    p[0] = ast.Compare(left=p[1],
                       ops=[ast.Eq()],
                       comparators=[p[3]],
                       lineno=p.lineno(1), col_offset=p.lexpos(1))


def p_expression_and(p):
    'expression : expression AND term'
    p[0] = ast.BoolOp(op=ast.And(),
                      values=[p[1], p[3]],
                      lineno=p.lineno(1), col_offset=p.lexpos(1))


def p_expression_or(p):
    'expression : expression OR term'
    p[0] = ast.BoolOp(op=ast.Or(),
                      values=[p[1], p[3]],
                      lineno=p.lineno(1), col_offset=p.lexpos(1))


def p_expression_term(p):
    'expression : term'
    p[0] = p[1]


def p_term_factor(p):
    'term : factor'
    p[0] = p[1]


def p_term_id(p):
    'term : ID'
    p[0] = ast.Name(id=p[1], ctx=ast.Load(), lineno=p.lineno(1), col_offset=p.lexpos(1))


def p_factor_num(p):
    'factor : NUMBER'
    p[0] = ast.Num(n=p[1], lineno=p.lineno(1), col_offset=p.lexpos(1))


def p_factor_true(p):
    'factor : TRUE'
    p[0] = ast.NameConstant(value=True, lineno=p.lineno(1), col_offset=p.lexpos(1))


def p_factor_false(p):
    'factor : FALSE'
    p[0] = ast.NameConstant(value=False, lineno=p.lineno(1), col_offset=p.lexpos(1))


def p_factor_str(p):
    'factor : STR'
    p[0] = ast.Str(s=p[1], lineno=p.lineno(1), col_offset=p.lexpos(1))


def p_factor_scope(p):
    'factor : LBRACE expression RBRACE'
    p[0] = p[2]


def p_factor_expr(p):
    'factor : LPAREN expression RPAREN'
    p[0] = p[2]


# construct the lexer and parser
js2py_lexer = lex.lex()
js2py_parser = yacc.yacc()
