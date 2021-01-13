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
            regs = [x for y, x in self.registers.items() if isinstance(x, Register) and x.known_value]
        else:
            regs = [x for y, x in self.registers.items() if isinstance(x, Register)]
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
        if isinstance(variable, Number):
            self.variables[variable.name].saved = True
        elif isinstance(variable, Identifier):
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
            else:
                self.registers[register].known_value = False

    def set_register_value(self, letter, value):
        cost, method = self.get_cost_and_method_of_set_register_to_value(letter, value)
        print("Setting {} to {} by {} that costs {}".format(letter, value, method, cost))
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

    def get_cost_and_method_of_set_register_to_value(self, letter, value, cost_only=False):
        register = self.get_register_by_letter(letter)
        registers = self.get_all_registers(known_only=True)
        if not cost_only:
            return get_set_register_best_method(register, value, registers)
        x, y = get_set_register_best_method(register, value, registers)
        return x

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
        a = self.variables[name_a]
        b = self.variables[name_b]
        self.check_initialization(a, line)
        self.check_initialization(b, line)
        if operation == "+":
            self.e_add(a, b, line)
        elif operation == "-":
            self.e_sub(a, b, line)
        elif operation == "*":
            self.e_mul(a, b, line)
        elif operation == "/":
            self.e_div(a, b, line)
        elif operation == "%":
            self.e_mod(a, b, line)

    def e_add(self, a, b, line):
        if isinstance(a, Number) and isinstance(b, Number):
            result = a.value + b.value
            cost_const = self.get_cost_and_method_of_set_register_to_value("b", result, cost_only=True)
            cost_alt1 = self.get_cost_and_method_of_set_register_to_value("b", a.value, cost_only=True)
            cost_alt1 += self.get_cost_and_method_of_set_register_to_value("c", b.value, cost_only=True)
            cost_alt1 += 5
            cost_alt2 = self.get_cost_and_method_of_set_register_to_value("b", b.value, cost_only=True)
            cost_alt2 += self.get_cost_and_method_of_set_register_to_value("c", a.value, cost_only=True)
            cost_alt2 += 5
            if a.saved and b.saved:
                cost_alt3 = self.get_cost_and_method_of_set_register_to_value("a", a.memory_address, cost_only=True)
                cost_alt3 += 20
                cost_alt3 += self.get_cost_and_method_of_set_register_to_value("a", b.memory_address, cost_only=True)
                cost_alt3 += 25
                cost_alt4 = self.get_cost_and_method_of_set_register_to_value("a", a.memory_address, cost_only=True)
                cost_alt4 += self.get_cost_and_method_of_set_register_to_value("b", b.value, cost_only=True)
                cost_alt4 += 25
                cost_alt5 = self.get_cost_and_method_of_set_register_to_value("a", b.memory_address, cost_only=True)
                cost_alt5 += self.get_cost_and_method_of_set_register_to_value("c", a.value, cost_only=True)
                cost_alt5 += 25
                if cost_const < cost_alt1 and cost_const < cost_alt2 and cost_const < cost_alt3 and cost_const < cost_alt4 and cost_const < cost_alt5:
                    self.set_register_value("b", result)
                else:
                    if cost_alt1 < cost_alt2 and cost_alt1 < cost_alt3 and cost_alt1 < cost_alt4 and cost_alt1 < cost_alt5:
                        self.set_register_value("b", a.value)
                        self.set_register_value("c", b.value)
                    elif cost_alt2 < cost_alt1 and cost_alt2 < cost_alt3 and cost_alt2 < cost_alt4 and cost_alt2 < cost_alt5:
                        self.set_register_value("b", b.value)
                        self.set_register_value("c", a.value)
                    elif cost_alt3 < cost_alt1 and cost_alt3 < cost_alt2 and cost_alt3 < cost_alt4 and cost_alt3 < cost_alt5:
                        self.get_from_memory("b", a)
                        self.get_from_memory("c", b)
                    elif cost_alt4 < cost_alt1 and cost_alt4 < cost_alt2 and cost_alt4 < cost_alt3 and cost_alt4 < cost_alt5:
                        self.get_from_memory("b", a)
                        self.set_register_value("c", b.value)
                    else:
                        self.get_from_memory("b", b)
                        self.set_register_value("c", a.value)
                    self.registers["b"].value = result
                    self.add_command("ADD b c")
            elif a.saved:
                cost_alt3 = self.get_cost_and_method_of_set_register_to_value("a", a.memory_address, cost_only=True)
                cost_alt3 += self.get_cost_and_method_of_set_register_to_value("b", b.value, cost_only=True)
                cost_alt3 += 25
                if cost_const < cost_alt1 and cost_const < cost_alt2 and cost_const < cost_alt3:
                    self.set_register_value("b", result)
                else:
                    if cost_alt1 < cost_alt2 and cost_alt1 < cost_alt3:
                        self.set_register_value("b", a.value)
                        self.set_register_value("c", b.value)
                    elif cost_alt2 < cost_alt1 and cost_alt2 < cost_alt3:
                        self.set_register_value("b", b.value)
                        self.set_register_value("c", a.value)
                    else:
                        self.get_from_memory("b", a)
                        self.set_register_value("c", b)
                    self.registers["b"].value = result
                    self.add_command("ADD b c")
            elif b.saved:
                cost_alt3 = self.get_cost_and_method_of_set_register_to_value("a", b.memory_address, cost_only=True)
                cost_alt3 += self.get_cost_and_method_of_set_register_to_value("c", a.value, cost_only=True)
                cost_alt3 += 25
                if cost_const < cost_alt1 and cost_const < cost_alt2 and cost_const < cost_alt3:
                    self.set_register_value("b", result)
                else:
                    if cost_alt1 < cost_alt2 and cost_alt1 < cost_alt3:
                        self.set_register_value("b", a.value)
                        self.set_register_value("c", b.value)
                    elif cost_alt2 < cost_alt1 and cost_alt2 < cost_alt3:
                        self.set_register_value("b", b.value)
                        self.set_register_value("c", a.value)
                    else:
                        self.get_from_memory("b", b)
                        self.set_register_value("c", a)
                    self.registers["b"].value = result
                    self.add_command("ADD b c")
            else:
                if cost_const < cost_alt1 and cost_const < cost_alt2:
                    self.set_register_value("b", result)
                else:
                    if cost_alt1 < cost_alt2:
                        self.set_register_value("b", a.value)
                        self.set_register_value("c", b.value)
                    else:
                        self.set_register_value("b", b.value)
                        self.set_register_value("c", a.value)
                    self.registers["b"].value = result
                    self.add_command("ADD b c")

        elif isinstance(a, Number):
            pass

    def e_sub(self, name_a, name_b, line):
        pass

    def e_mul(self, name_a, name_b, line):
        pass

    def e_div(self, name_a, name_b, line):
        pass

    def e_mod(self, name_a, name_b, line):
        pass
