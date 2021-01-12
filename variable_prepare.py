from variable import *


class VariablePrepare:
    def __init__(self, variables):
        self.variables = variables

    def print_variables(self):
        for name, variable in self.variables.items():
            print("Variable {} memoryindex {} with {} occurrences".format(name, variable.memory_address,
                                                                          variable.occurrences))

    def get_optimized_variables(self):
        memory_index = 0
        self.variables = dict(sorted(self.variables.items(), key=lambda item: item[1].occurrences, reverse=True))
        optimized_variables = {}
        arrays = {}
        identifiers = {}
        numbers = {}
        for name, variable in self.variables.items():
            if isinstance(variable, Identifier):
                identifiers[name] = variable
            elif isinstance(variable, Number):
                if variable.in_write or (variable.occurrences > 1 and variable.value > 100):
                    variable.is_stored = True
                    identifiers[name] = variable
                else:
                    numbers[name] = variable
            elif isinstance(variable, Array):
                arrays[name] = variable
            elif isinstance(variable, Iterator):
                variable.memory_address = memory_index
                memory_index += 1
                optimized_variables[name] = variable

        for name, identifier in identifiers.items():
            identifier.memory_address = memory_index
            memory_index += 1
            optimized_variables[name] = identifier

        for name, array in arrays.items():
            array.memory_address = memory_index
            size = array.end - array.start + 1
            memory_index += size
            optimized_variables[name] = array
        for name, number in numbers.items():
            optimized_variables[name] = number
        self.variables = optimized_variables
        self.print_variables()
