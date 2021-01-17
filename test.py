import csv
import os
import unittest

from compiler import Compiler

cost_full = []


def stop_test_run(self):
    csv_columns = ['name', 'cost']
    costs_file = open("costs/full.csv", "w")
    writer = csv.DictWriter(costs_file, csv_columns)
    writer.writeheader()
    for data in cost_full:
        writer.writerow(data)
    costs_file.close()


setattr(unittest.TestResult, 'stopTestRun', stop_test_run)


class BauerTests(unittest.TestCase):
    def test_compiler(self):
        costs = []
        files = [f for f in os.listdir("tests_bauer") if os.path.isfile(os.path.join("tests_bauer", f))]
        for i, file in enumerate(files):
            with self.subTest(i=i):
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
                    correct = corrects[i]
                    os.system("echo \"{}\" | ./maszyna-wirtualna-cln-test out.mr > out.txt".format(" ".join(data_set)))
                    result_file = open("out.txt", "r")
                    result = result_file.read().split()
                    result_file.close()
                    cost = int(result[-1])
                    costs.append({"name": file, "cost": cost})
                    result.pop()
                    self.assertEqual(result, correct)
        sum_of_costs = 0
        for cost in costs:
            sum_of_costs += cost["cost"]
        csv_columns = ['name', 'cost']
        costs_file1 = open("costs/bauer.csv", "w")
        writer = csv.DictWriter(costs_file1, csv_columns)
        writer.writeheader()
        for data in costs:
            writer.writerow(data)
        costs_file1.close()
        cost_full.append({"name": "bauer", "cost": sum_of_costs})


class SchmidtTests(unittest.TestCase):
    def test_compiler(self):
        costs = []
        files = [f for f in os.listdir("tests_schmidt") if os.path.isfile(os.path.join("tests_schmidt", f))]
        for i, file in enumerate(files):
            with self.subTest(i=i):
                compiler = Compiler("tests_schmidt/{}".format(file), "out.mr")
                compiler.read_from_file()
                compiler.compile()
                self.assertTrue(compiler.write_to_file())
                inputs_file = open("tests_schmidt/in/{}".format(file), "r")
                inputs = inputs_file.read().split("X")
                inputs_file.close()
                inputs = [x.strip().split() for x in inputs]
                corrects_file = open("tests_schmidt/correct/{}".format(file), "r")
                corrects = corrects_file.read().split("X")
                corrects_file.close()
                corrects = [x.strip().split() for x in corrects]
                for i, data_set in enumerate(inputs):
                    correct = corrects[i]
                    os.system("echo \"{}\" | ./maszyna-wirtualna-cln-test out.mr > out.txt".format(" ".join(data_set)))
                    result_file = open("out.txt", "r")
                    result = result_file.read().split()
                    result_file.close()
                    cost = int(result[-1])
                    costs.append({"name": file, "cost": cost})
                    result.pop()
                    self.assertEqual(result, correct)
        sum_of_costs = 0
        for cost in costs:
            sum_of_costs += cost["cost"]
        csv_columns = ['name', 'cost']
        costs_file1 = open("costs/schmidt.csv", "w")
        writer = csv.DictWriter(costs_file1, csv_columns)
        writer.writeheader()
        for data in costs:
            writer.writerow(data)
        costs_file1.close()
        cost_full.append({"name": "schmidt", "cost": sum_of_costs})


class GotfrydTests(unittest.TestCase):
    def test_compiler(self):
        costs = []
        files = [f for f in os.listdir("tests_gotfryd") if os.path.isfile(os.path.join("tests_gotfryd", f))]
        for i, file in enumerate(files):
            with self.subTest(i=i):
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
                    cost = int(result[-1])
                    costs.append({"name": file, "cost": cost})
                    result.pop()
                    self.assertEqual(result, correct)
        sum_of_costs = 0
        for cost in costs:
            sum_of_costs += cost["cost"]
        csv_columns = ['name', 'cost']
        costs_file1 = open("costs/gotfryd.csv", "w")
        writer = csv.DictWriter(costs_file1, csv_columns)
        writer.writeheader()
        for data in costs:
            writer.writerow(data)
        costs_file1.close()
        cost_full.append({"name": "gotfryd", "cost": sum_of_costs})


class GebalaTests(unittest.TestCase):
    def test_compiler(self):
        costs = []
        files = [f for f in os.listdir("tests_gebala") if os.path.isfile(os.path.join("tests_gebala", f))]
        for i, file in enumerate(files):
            with self.subTest(i=i):
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
                    cost = int(result[-1])
                    costs.append({"name": file,"cost":cost})
                    result.pop()
                    self.assertEqual(result, correct)
        sum_of_costs = 0
        for  cost in costs:
            sum_of_costs += cost["cost"]
        csv_columns = ['name', 'cost']
        costs_file1 = open("costs/gebala.csv", "w")
        writer = csv.DictWriter(costs_file1, csv_columns)
        writer.writeheader()
        for data in costs:
            writer.writerow(data)
        costs_file1.close()
        cost_full.append({"name":"gebala","cost":sum_of_costs})


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
