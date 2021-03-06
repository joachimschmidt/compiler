from definitions.variable import *
from register_utils import cost_of_set_const


class VariablePrepare:
    def __init__(self, variables):
        self.variables = variables

    def print_variables(self):
        for name, variable in self.variables.items():
            print("Variable {} memoryindex {} with {} occurrences and in loop: {}".format(name, variable.memory_address,
                                                                                          variable.occurrences,
                                                                                          variable.in_loop))

    def calculate_optimized_variables(self):
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
                if variable.in_write or (variable.occurrences > 1 and cost_of_set_const(variable.value) > 30) or (
                        cost_of_set_const(variable.value) > 25 and
                        variable.in_loop):
                    variable.is_stored = True
                    identifiers[name] = variable
                else:
                    numbers[name] = variable
            elif isinstance(variable, Array):
                size = variable.end - variable.start + 1
                if size < 4:
                    identifiers[name] = variable
                else:
                    arrays[name] = variable
            elif isinstance(variable, Iterator):
                identifiers[name] = variable

        for name, identifier in identifiers.items():
            if isinstance(identifier, Iterator):
                identifier.memory_address = memory_index
                memory_index += 2
                optimized_variables[name] = identifier
            elif isinstance(identifier, Array):
                identifier.memory_address = memory_index
                size = identifier.end - identifier.start + 1
                memory_index += size
                optimized_variables[name] = identifier
            else:
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

    def get_variables(self):
        return self.variables

    def get_optimized_variables(self):
        self.calculate_optimized_variables()
        return self.variables
