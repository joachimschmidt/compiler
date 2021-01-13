from compiler_exception import CompilerException
from register import Register
from register_utils import *
from variable import *


class CodeGenerator:
    def __init__(self, variables):
        self.variables = variables
        self.commands = []
        self.jumps = []
        self.loops = []
        self.k = 0
        self.registers = {}
        self.generate_registers()

    def generate_registers(self):
        self.registers["a"] = Register("a")
        self.registers["b"] = Register("b")
        self.registers["c"] = Register("c")
        self.registers["d"] = Register("d")
        self.registers["e"] = Register("e")
        self.registers["f"] = Register("f")

    def get_register_by_letter(self, letter):
        register = self.registers[letter]
        if isinstance(register, Register):
            return register

    def get_all_registers(self, known_only=False):
        if known_only:
            regs = [x for x, y in self.registers.items() if isinstance(x, Register) and x.known_value]
        else:
            regs = [x for x, y in self.registers.items() if isinstance(x, Register)]
        return regs

    def add_command(self, command):
        self.commands.append(command)
        self.k += 1

    def handle_error(self, error, line):
        raise CompilerException(error, line)

    def check_array_declaration(self, name, start, end, line):
        if start > end:
            self.handle_error("bad bounds in array {} -> end cannot be lower than start".format(name), line)

    def check_identifier_reference(self, name, line):
        variable = self.variables[name]
        if isinstance(variable, Array):
            self.handle_error("Bad reference to array {}".format(name), line)

    def check_array_reference_by_number(self, array, index, line):
        pass

    def check_array_reference_by_identifier(self, array, index, line):
        pass

    def set_address(self, variable):
        self.set_register_value("a", variable.memory_address)

    def save_to_memory(self, register, variable):
        self.set_address(variable)
        self.add_command("STORE {} {}".format(register, "a"))
        if isinstance(variable, Identifier):
            self.variables[variable.name].initialized = True

    def get_from_memory(self, register, variable):
        if not isinstance(variable, Array):
            if isinstance(variable, Number) and variable.saved:
                x, y = self.get_cost_and_method_of_set_register_to_value("a", variable.memory_address)
                cost, method = self.get_cost_and_method_of_set_register_to_value("b", variable.value)
                if (x + 20) > cost:
                    self.set_register_to_number(register, variable)
                    return
            self.set_address(variable)
            self.add_command("LOAD {} {}".format(register, "a"))
            if isinstance(variable, Number):
                self.registers[register].known_value = True
                self.registers[register].value = variable.value

    def set_register_value(self, letter, value):
        cost, method = self.get_cost_and_method_of_set_register_to_value(letter, value)
        #print("Setting {} to {} by {} that costs {}".format(letter, value, method, cost))
        register = self.get_register_by_letter(letter)
        ready_code = set_register_to_value(method, letter, value, self.get_all_registers(), register)
        self.k += len(ready_code)
        self.commands += ready_code
        self.registers[letter].value = value
        self.registers[letter].known_value = True

    def set_register_to_number(self, letter, number):
        self.set_register_value(letter, number.value)
        if number.is_stored and not number.saved:
            self.save_to_memory(letter, number)

    def get_cost_and_method_of_set_register_to_value(self, letter, value):
        register = self.get_register_by_letter(letter)
        registers = self.get_all_registers(known_only=True)
        return get_set_register_best_method(register, value, registers)

    def end_program(self):
        self.add_command("HALT")

    def c_assign(self, name, line):
        variable = self.variables[name]
        if isinstance(variable, Iterator):
            self.handle_error("Iterator {} modification not allowed".format(name), line)
        self.save_to_memory("b", variable)

    def c_write(self, name, line):
        variable = self.variables[name]
        self.check_initialization(variable, line)
        self.set_address(variable)
        if isinstance(variable, Number) and not variable.saved:
            self.set_register_to_number("b", variable)
        self.add_command("PUT a")

    def c_read(self, name, line):
        variable = self.variables[name]
        if isinstance(variable, Iterator):
            self.handle_error("Cannot READ to iterator {}".format(name), line)
        self.set_address(variable)
        self.add_command("GET a")
        if not isinstance(variable, Array):
            self.variables[name].initialized = True

    def c_if(self):
        pass

    def c_if_else(self):
        pass

    def c_while(self):
        pass

    def c_exit_while(self):
        pass

    def c_exit_repeat(self):
        pass

    def c_for_to(self, iterator, start, end, line):
        pass

    def c_for_down_to(self, iterator, start, end, line):
        pass

    def c_exit_for_to(self):
        pass

    def c_exit_for_down_to(self):
        pass

    def e_value(self, name, line):
        variable = self.variables[name]
        self.check_initialization(variable, line)
        if isinstance(variable, Number):
            if not variable.saved:
                self.set_register_to_number("b", variable)
                return
        self.get_from_memory("b", variable)

    def check_initialization(self, variable, line):
        if isinstance(variable, Identifier):
            if not variable.initialized:
                self.handle_error("Variable {} not initialized".format(variable.name), line)

    def e_operation(self, name_a, name_b, operation, line):
        pass

    def condition(self, name_a, name_b, condition, line):
        pass
