import os
import unittest

from compiler import Compiler


class BauerTests(unittest.TestCase):
    def test_compiler(self):
        for i, file in enumerate(os.listdir("tests_bauer")):
            with self.subTest(i=i):
                compiler = Compiler("tests_bauer/{}".format(file), "out.mr")
                compiler.read_from_file()
                compiler.compile()
                self.assertTrue(compiler.write_to_file())


class GotfrydTests(unittest.TestCase):
    def test_compiler(self):
        for i, file in enumerate(os.listdir("tests_gotfryd")):
            with self.subTest(i=i):
                compiler = Compiler("tests_gotfryd/{}".format(file), "out.mr")
                compiler.read_from_file()
                compiler.compile()
                self.assertTrue(compiler.write_to_file())


class GebalaTests(unittest.TestCase):
    def test_compiler(self):
        for i, file in enumerate(os.listdir("tests_gebala")):
            with self.subTest(i=i):
                compiler = Compiler("tests_gebala/{}".format(file), "out.mr")
                compiler.read_from_file()
                compiler.compile()
                self.assertTrue(compiler.write_to_file())


class ErrorTests(unittest.TestCase):
    def test_compiler(self):
        for i, file in enumerate(os.listdir("tests_bad")):
            with self.subTest(i=i):
                compiler = Compiler("tests_bad/{}".format(file), "out.mr")
                compiler.read_from_file()
                compiler.compile()
                self.assertFalse(compiler.write_to_file())


if __name__ == '__main__':
    unittest.main()
