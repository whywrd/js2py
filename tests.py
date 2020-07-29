import unittest
from js2py import js2py


class AssignmentTests(unittest.TestCase):

    def test_empty(self):
        self.assertEqual({'a': 1}, js2py('', {'a': 1}))

    def test_assign_new(self):
        self.assertRaises(Exception, {'a': 1}, js2py('a = 1', {}))

    def test_assign_existing(self):
        self.assertEqual({'a': 1}, js2py('a = 1', {'a': 0}))


class MathTests(unittest.TestCase):

    def test_scalar_addition(self):
        self.assertEqual({'a': 3}, js2py('a = 1 + 2', {'a': 0}))

    def test_mixed_addition(self):
        self.assertEqual({'a': 2}, js2py('a = a + 1', {'a': 1}))

    def test_variable_addition(self):
        self.assertEqual({'a': 3, 'b': 2}, js2py('a = a + b', {'a': 1, 'b': 2}))

    def test_subtraction(self):
        self.assertEqual({'a': -1, 'b': 2}, js2py('a = a - b', {'a': 1, 'b': 2}))

    def test_with_properties(self):
        self.assertEqual({'a': {'x': -1}}, js2py('a.x = a.x - 1', {'a': {'x': 0}}))


class BooleanTests(unittest.TestCase):

    def test_and(self):
        with self.subTest('false and true'):
            self.assertEqual({'a': False}, js2py('a = a && true', {'a': False}))
        with self.subTest('true and true'):
            self.assertEqual({'a': True}, js2py('a = a && true', {'a': True}))

    def test_or(self):
        with self.subTest('false or true'):
            self.assertEqual({'a': True}, js2py('a = a || true', {'a': False}))
        with self.subTest('true or true'):
            self.assertEqual({'a': True}, js2py('a = a || true', {'a': True}))
        with self.subTest('false or false'):
            self.assertEqual({'a': False}, js2py('a = a || false', {'a': False}))


class IfElseTests(unittest.TestCase):

    def test_if(self):
        params = [['if (a>3) { a = 0}', {'a': 4}, {'a': 0}],
                  ['if (a>3) { a = 0}', {'a': 3}, {'a': 3}],
                  ['if (a>3 && b == 1) { a = 0}', {'a': 4, 'b': 1}, {'a': 0, 'b': 1}],
                  ['if (a>3 && b == 1) { a = 0}', {'a': 4, 'b': 2}, {'a': 4, 'b': 2}],
                  ['if (a>3 || b == 1) { a = 0}', {'a': 3, 'b': 1}, {'a': 0, 'b': 1}],
                  ['if (b == 1){ if (a > 3) { a = 0}}', {'a': 4, 'b': 1}, {'a': 0, 'b': 1}],
                  ['if (b == 1){ if (a > 3) { a = 0}}', {'a': 3, 'b': 1}, {'a': 3, 'b': 1}]]
        for p in params:
            with self.subTest(js=p[0], context=p[1], expected=p[2]):
                self.assertEqual(p[2], js2py(p[0], p[1]))

    def test_else(self):
        params = [['if (a>3) { a = 0} else { a = 1}', {'a': 4}, {'a': 0}],
                  ['if (a>3) { a = 0} else { a = 1}', {'a': 3}, {'a': 1}],
                  ['if (a>3) { a = 0} else { if (a == 3) {a = 2}}', {'a': 3}, {'a': 2}]]
        for p in params:
            with self.subTest(js=p[0], context=p[1], expected=p[2]):
                self.assertEqual(p[2], js2py(p[0], p[1]))


class StringTests(unittest.TestCase):

    def test_string(self):
        params = [['a = "x"', {'a': 'b'}, {'a': 'x'}],
                  ['if (a == "x") { a = "y"}', {'a': 'x'}, {'a': 'y'}],
                  ['if (a == "x") { a = "y"}', {'a': 'm'}, {'a': 'm'}],
                  ['if (a == "x") { a = "y"} else { a = "z"}', {'a': "b"}, {'a': "z"}],
                  ['if (a == "x") { a = "y"} else { a = "z"}', {'a': "x"}, {'a': "y"}]]
        for p in params:
            with self.subTest(js=p[0], context=p[1], expected=p[2]):
                self.assertEqual(p[2], js2py(p[0], p[1]))
