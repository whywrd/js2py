from ast import AST, Module
from typing import Dict, Any
from parser import js2py_parser


def transform(js: str) -> AST:
    """
    Turn JS code (as a string) and transform it into a Python AST
    """
    nodes = js2py_parser.parse(js)
    if nodes:
        body = [nodes]
    else:
        body = []
    return Module(body=body)


def js2py(js: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform and run JS code to Python and run it in a provided context.
    Return a copy of the context post execution (execution might alter the context).
    """
    new_context = context.copy()
    ast = transform(js)
    code = compile(ast, filename='<ast>', mode='exec')
    exec(code, new_context)
    # __builtins__ is automatically added to the context on execution
    del new_context['__builtins__']
    return new_context
