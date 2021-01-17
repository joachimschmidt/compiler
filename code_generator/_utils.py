import copy

from compiler_exception import CompilerException
from register import Register
from register_utils import set_register_to_value, get_set_register_best_method
from variable import *


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
    array = copy.deepcopy(self.variables[array])
    return array, index, "number"


def check_array_reference_by_identifier(self, array, index, line):
    variable = self.variables[index]
    array = copy.deepcopy(self.variables[array])
    self.check_initialization(variable, line)
    if isinstance(variable,Identifier) and variable.known_value:
        return array, variable.value, "number"
    else:
        return array, variable, "id"


def set_address(self, variable):
    if not isinstance(variable, Array):
        self.set_register_value("a", variable.memory_address)
    else:
        if isinstance(variable.occurrences, int) :
            value = variable.memory_address + variable.occurrences - variable.start
            self.set_register_value("a", value)
        else:
            self.get_from_memory("e", variable.occurrences)
            self.set_register_value("a", variable.memory_address)
            self.add_command("ADD a e")
            self.forget_register("a")
            self.set_register_value("e", variable.start)
            self.add_command("SUB a e")
            self.forget_register("a")


def save_to_memory(self, register, variable, iterator_end=False):
    self.set_address(variable)
    self.add_command("STORE {} {}".format(register, "a"))
    if isinstance(variable, Number) and not iterator_end:
        self.variables[variable.name].saved = True
    elif isinstance(variable, Identifier):
        if self.registers[register].known_value:
            self.variables[variable.name].known_value = True
            self.variables[variable.name].value = self.registers[register].value
        else:
            self.variables[variable.name].known_value = False
        self.variables[variable.name].initialized = True


def get_from_memory(self, register, variable):
    if isinstance(variable, Number) and variable.saved:
        x, y = self.get_cost_and_method_of_set_register_to_value("a", variable.memory_address)
        cost, method = self.get_cost_and_method_of_set_register_to_value("b", variable.value)
        if (x + 20) > cost:
            self.set_register_to_number(register, variable)
            return
    self.set_address(variable)
    self.add_command("LOAD {} {}".format(register, "a"))
    if isinstance(variable, Number) or (isinstance(variable, Identifier) and variable.known_value):
        self.remember_register(register, variable.value)
    else:
        self.forget_register(register)


def set_register_value(self, letter, value):
    cost, method = self.get_cost_and_method_of_set_register_to_value(letter, value)
    # print("Setting {} to {} by {} that costs {}".format(letter, value, method, cost))
    register = self.get_register_by_letter(letter)
    ready_code = set_register_to_value(method, letter, value, self.get_all_registers(), register)
    self.k += len(ready_code)
    self.commands += ready_code
    self.remember_register(letter, value)
    return cost


def save_numbers_from_loop(self):
    for name, var in self.variables.items():
        if isinstance(var, Number) and var.is_stored and var.in_loop:
            set_register_value(self, "b", var.value)
            save_to_memory(self, "b", var)


def set_register_to_number(self, letter, number, optimize=False):
    if not optimize:
        cost = self.set_register_value(letter, number.value)
        if number.is_stored and not number.saved and len(self.loops) == 0:
            self.save_to_memory(letter, number)
        return cost
    else:
        if number.saved:
            x, y = self.get_cost_and_method_of_set_register_to_value("a", number.memory_address)
            cost, method = self.get_cost_and_method_of_set_register_to_value(letter, number.value)
            if (x + 20) > cost:
                return self.set_register_to_number(letter, number)
            self.get_from_memory(letter, number)
        else:
            return self.set_register_to_number(letter, number)


def get_cost_and_method_of_set_register_to_value(self, letter, value, cost_only=False):
    register = self.get_register_by_letter(letter)
    registers = self.get_all_registers(known_only=True)
    if not cost_only:
        return get_set_register_best_method(register, value, registers)
    x, y = get_set_register_best_method(register, value, registers)
    return x


def end_program(self):
    self.add_command("HALT")


def create_savepoint(self):
    self.backup_k = self.k
    self.commands_backup = copy.deepcopy(self.commands)
    self.registers_backup = copy.deepcopy(self.registers)
    self.variables_backup = copy.deepcopy(self.variables)


def load_savepoint(self):
    self.registers = copy.deepcopy(self.registers_backup)
    self.commands = copy.deepcopy(self.commands_backup)
    self.variables = copy.deepcopy(self.variables_backup)
    self.k = self.backup_k


def prepare_variable(self, var, line):
    if isinstance(var, tuple):
        a = var[0]
        if isinstance(a, Array):
            a.occurrences = var[1]
        else:
            self.handle_error("Bad variable reference", line)
    else:
        a = self.variables[var]
    return a


def check_initialization(self, variable, line):
    if isinstance(variable, Identifier):
        if not variable.initialized:
            self.handle_error("Variable {} not initialized".format(variable.name), line)
    if isinstance(variable, Iterator):
        if not variable.in_use:
            self.handle_error(
                "Variable {} was an iterator but this reference is outside the loop".format(variable.name), line)


def forget_register(self, letter):
    self.registers[letter].known_value = False


def forget_everything(self):
    forget_registers(self)
    forget_variables(self)


def forget_variables(self):
    for name, var in self.variables.items():
        if isinstance(var, Identifier):
            self.variables[name].known_value = False


def forget_registers(self):
    self.forget_register("a")
    self.forget_register("b")
    self.forget_register("c")
    self.forget_register("d")
    self.forget_register("e")
    self.forget_register("f")


def backup_registers(self):
    self.registers_backup_2 = copy.deepcopy(self.registers)


def restore_registers(self):
    self.registers = copy.deepcopy(self.registers_backup_2)


def remember_register(self, letter, value):
    self.registers[letter].known_value = True
    self.registers[letter].value = value


def variable_to_register(self, register, variable):
    if isinstance(variable, Number):
        self.set_register_to_number(register, variable, optimize=True)
    elif isinstance(variable, Identifier) and variable.known_value:
        variable = Number(variable.value, variable.value, variable.memory_address)
        variable.saved = True
        variable.is_stored = True
        self.set_register_to_number(register, variable, optimize=True)
    else:
        self.get_from_memory(register, variable)


def prepare_and_check_initialization(self, name_a, name_b, line):
    a = self.prepare_variable(name_a, line)
    b = self.prepare_variable(name_b, line)
    if isinstance(a, Identifier) and a.known_value:
        a = Number(a.value, a.value, a.memory_address)
        a.is_stored = True
        a.saved = True
        if isinstance(b, Identifier) and b.known_value:
            b = Number(b.value, b.value, b.memory_address)
            b.is_stored = True
            b.saved = True
    self.check_initialization(a, line)
    self.check_initialization(b, line)
    return a, b
