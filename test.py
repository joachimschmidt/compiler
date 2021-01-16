import os
import unittest

from compiler import Compiler


class BauerTests(unittest.TestCase):
    def test_compiler(self):
        files = [f for f in os.listdir("tests_bauer") if os.path.isfile(os.path.join("tests_bauer", f))]
        for i, file in enumerate(files):
            with self.subTest(i=i):
                #print("i: {} file: tests_bauer/{}".format(i, file))
                cost = 0
                compiler = Compiler("tests_bauer/{}".format(file), "out.mr")
                compiler.read_from_file()
                compiler.compile()
                self.assertTrue(compiler.write_to_file())
                inputs_file = open("tests_bauer/in/{}".format(file), "r")
                inputs = inputs_file.read().split("X")
                inputs_file.close()
                inputs = [x.strip().split() for x in inputs]
                corrects_file = open("tests_bauer/correct/{}".format(file), "r")
                corrects = corrects_file.read().split("X")
                corrects_file.close()
                corrects = [x.strip().split() for x in corrects]
                for i, data_set in enumerate(inputs):
                    #print(data_set)
                    correct = corrects[i]
                    os.system("echo \"{}\" | ./maszyna-wirtualna-cln-test out.mr > out.txt".format(" ".join(data_set)))
                    result_file = open("out.txt", "r")
                    result = result_file.read().split()
                    result_file.close()
                    cost += int(result[-1])
                    result.pop()
                    #print(result)
                    #print(correct)
                    self.assertEqual(result, correct)


class GotfrydTests(unittest.TestCase):
    def test_compiler(self):
        files = [f for f in os.listdir("tests_gotfryd") if os.path.isfile(os.path.join("tests_gotfryd", f))]
        for i, file in enumerate(files):
            with self.subTest(i=i):
                cost = 0
                compiler = Compiler("tests_gotfryd/{}".format(file), "out.mr")
                compiler.read_from_file()
                compiler.compile()
                self.assertTrue(compiler.write_to_file())
                inputs_file = open("tests_gotfryd/in/{}".format(file), "r")
                inputs = inputs_file.read().split("X")
                inputs_file.close()
                inputs = [x.strip().split() for x in inputs]
                corrects_file = open("tests_gotfryd/correct/{}".format(file), "r")
                corrects = corrects_file.read().split("X")
                corrects_file.close()
                corrects = [x.strip().split() for x in corrects]
                for i, data_set in enumerate(inputs):
                    correct = corrects[i]
                    os.system("echo \"{}\" | ./maszyna-wirtualna-cln-test out.mr > out.txt".format(" ".join(data_set)))
                    result_file = open("out.txt", "r")
                    result = result_file.read().split()
                    result_file.close()
                    cost += int(result[-1])
                    result.pop()
                    self.assertEqual(result, correct)


class GebalaTests(unittest.TestCase):
    def test_compiler(self):
        files = [f for f in os.listdir("tests_gebala") if os.path.isfile(os.path.join("tests_gebala", f))]
        for i, file in enumerate(files):
            with self.subTest(i=i):
                cost = 0
                compiler = Compiler("tests_gebala/{}".format(file), "out.mr")
                compiler.read_from_file()
                compiler.compile()
                self.assertTrue(compiler.write_to_file())
                inputs_file = open("tests_gebala/in/{}".format(file), "r")
                inputs = inputs_file.read().split("X")
                inputs_file.close()
                inputs = [x.strip().split() for x in inputs]
                corrects_file = open("tests_gebala/correct/{}".format(file), "r")
                corrects = corrects_file.read().split("X")
                corrects_file.close()
                corrects = [x.strip().split() for x in corrects]
                for i, data_set in enumerate(inputs):
                    correct = corrects[i]
                    os.system("echo \"{}\" | ./maszyna-wirtualna-cln-test out.mr > out.txt".format(" ".join(data_set)))
                    result_file = open("out.txt", "r")
                    result = result_file.read().split()
                    result_file.close()
                    cost += int(result[-1])
                    result.pop()
                    self.assertEqual(result, correct)


class CrazyHajdukTests(unittest.TestCase):
    def test_compiler(self):
        for i, file in enumerate(os.listdir("tests_crazy")):
            with self.subTest(i=i):
                compiler = Compiler("tests_crazy/{}".format(file), "out.mr")
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
