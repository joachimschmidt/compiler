import copy
import math

from compiler_exception import CompilerException
from jump import Jump
from loop import Loop
from register import Register
from register_utils import *
from variable import *


class CodeGenerator:
    def __init__(self, variables):
        self.commands_backup = []
        self.registers_backup = {}
        self.registers_backup_2 = {}
        self.backup_k = 0
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
        array = copy.deepcopy(self.variables[array])
        return array, index, "number"

    def check_array_reference_by_identifier(self, array, index, line):
        variable = self.variables[index]
        array = copy.deepcopy(self.variables[array])
        self.check_initialization(variable, line)
        return array, variable, "id"

    def set_address(self, variable):
        if not isinstance(variable, Array):
            self.set_register_value("a", variable.memory_address)
        else:
            if isinstance(variable.occurrences, int):
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

    def save_to_memory(self, register, variable):
        self.set_address(variable)
        self.add_command("STORE {} {}".format(register, "a"))
        if isinstance(variable, Number):
            self.variables[variable.name].saved = True
        elif isinstance(variable, Identifier):
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
        if isinstance(variable, Number):
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

    def set_register_to_number(self, letter, number, optimize=False):
        if not optimize:
            cost = self.set_register_value(letter, number.value)
            if number.is_stored and not number.saved:
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

    def c_assign(self, name, line):
        variable = self.prepare_variable(name, line)
        if isinstance(variable, Iterator):
            self.handle_error("Iterator {} modification not allowed".format(name), line)
        self.save_to_memory("b", variable)

    def c_write(self, name, line):
        variable = self.prepare_variable(name, line)
        self.check_initialization(variable, line)
        self.set_address(variable)
        if isinstance(variable, Number) and not variable.saved:
            self.set_register_to_number("b", variable)
        self.add_command("PUT a")

    def c_read(self, name, line):
        variable = self.prepare_variable(name, line)
        if isinstance(variable, Iterator):
            self.handle_error("Cannot READ to iterator {}".format(name), line)
        self.set_address(variable)
        self.add_command("GET a")
        if not isinstance(variable, Array):
            self.variables[name].initialized = True

    def c_begin_if(self):
        self.backup_registers()

    def c_if(self):
        self.commands[self.jumps[-1].k] += str(self.k - self.jumps[-1].k)
        self.jumps.pop()
        self.forget_all_registers()

    def c_if_else(self):
        self.add_command("JUMP ")
        self.restore_registers()
        self.commands[self.jumps[-1].k] += str(self.k - self.jumps[-1].k)
        self.jumps.pop()
        self.jumps.append(Jump(self.k - 1))

    def c_while(self):
        self.loops.append(Loop(self.k))
        self.forget_all_registers()

    def c_exit_while(self):
        self.add_command("JUMP {}".format(self.loops[-1].k - self.k))
        self.commands[self.jumps[-1].k] += str(self.k - self.jumps[-1].k)
        self.jumps.pop()
        self.loops.pop()

    def c_exit_repeat(self):
        self.commands.pop()
        self.jumps.pop()
        self.add_command("JZERO e 2")
        self.add_command("JUMP 2")
        self.add_command("JUMP {}".format(self.loops[-1].k - self.k))
        self.loops.pop()

    def prepare_iterator(self, iterator, start, end, line):
        i = self.variables[iterator]
        if isinstance(i, Iterator):
            if i.in_use:
                self.handle_error("Iterator {} repeated ".format(iterator), line)
            else:
                i.start = self.variables[start]
                i.end = self.variables[end]
                return i
        else:
            self.handle_error("Repeated declaration of {}".format(iterator), line)

    def c_for_to(self, iterator, start, end, line):
        i = self.prepare_iterator(iterator, start, end, line)


    def c_for_down_to(self, iterator, start, end, line):
        pass

    def c_exit_for_to(self):
        pass

    def c_exit_for_down_to(self):
        pass

    def conditions(self, name_a, name_b, operation, line):
        a, b = self.prepare_and_check_initialization(name_a, name_b, line)
        if isinstance(a, Number) and isinstance(b, Number):
            if eval("{}{}{}".format(a.value, operation, b.value)):
                self.set_register_value("e", 1)
            else:
                self.set_register_value("e", 0)
            self.remember_register("e", 0)
            self.jumps.append(Jump(self.k))
            self.add_command("JZERO e ")
        else:
            if operation == "=":
                self.cond_eq(a, b, line)
            elif operation == "!=":
                self.cond_neq(a, b, line)
            elif operation == "<":
                self.cond_lt(a, b, line)
            elif operation == ">":
                self.cond_gt(a, b, line)
            elif operation == "<=":
                self.cond_let(a, b, line)
            elif operation == ">=":
                self.cond_get(a, b, line)
            self.forget_register("e")

    def variable_to_register(self, register, variable):
        if isinstance(variable, Number):
            self.set_register_to_number(register, variable, optimize=True)
        else:
            self.get_from_memory(register, variable)

    def cond_eq(self, a, b, line):
        self.variable_to_register("b", a)
        self.variable_to_register("c", b)
        self.add_command("RESET e")
        self.add_command("RESET d")
        self.add_command("ADD d b")
        self.add_command("SUB d c")
        self.add_command("JZERO d 2")
        self.add_command("JUMP 5")
        self.add_command("SUB c b")
        self.add_command("JZERO c 2")
        self.add_command("JUMP 2")
        self.add_command("INC e")
        self.jumps.append(Jump(self.k))
        self.add_command("JZERO e ")
        self.forget_register("b")
        self.forget_register("c")
        self.forget_register("d")
        self.forget_register("e")

    def cond_neq(self, a, b, line):
        self.variable_to_register("b", a)
        self.variable_to_register("c", b)
        self.add_command("RESET e")
        self.add_command("RESET d")
        self.add_command("ADD d b")
        self.add_command("SUB d c")
        self.add_command("JZERO d 2")
        self.add_command("INC e")
        self.add_command("SUB c b")
        self.add_command("JZERO c 2")
        self.add_command("INC e")
        self.jumps.append(Jump(self.k))
        self.add_command("JZERO e ")
        self.forget_register("b")
        self.forget_register("c")
        self.forget_register("d")
        self.forget_register("e")

    def cond_lt(self, a, b, line):
        self.variable_to_register("b", a)
        self.variable_to_register("e", b)
        self.add_command("SUB e b")
        self.jumps.append(Jump(self.k))
        self.add_command("JZERO e ")
        self.forget_register("b")
        self.forget_register("e")

    def cond_gt(self, a, b, line):
        self.variable_to_register("e", a)
        self.variable_to_register("b", b)
        self.add_command("SUB e b")
        self.jumps.append(Jump(self.k))
        self.add_command("JZERO e ")
        self.forget_register("b")
        self.forget_register("e")

    def cond_let(self, a, b, line):
        self.variable_to_register("b", a)
        self.variable_to_register("e", b)
        self.add_command("INC e")
        self.add_command("SUB e b")
        self.jumps.append(Jump(self.k))
        self.add_command("JZERO e ")
        self.forget_register("b")
        self.forget_register("e")

    def cond_get(self, a, b, line):
        self.variable_to_register("e", a)
        self.variable_to_register("b", b)
        self.add_command("INC e")
        self.add_command("SUB e b")
        self.jumps.append(Jump(self.k))
        self.add_command("JZERO e ")
        self.forget_register("b")
        self.forget_register("e")

    def prepare_and_check_initialization(self, name_a, name_b, line):
        a = self.prepare_variable(name_a, line)
        b = self.prepare_variable(name_b, line)
        self.check_initialization(a, line)
        self.check_initialization(b, line)
        return a, b

    def e_value(self, name, line):
        variable = self.prepare_variable(name, line)
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

    def forget_register(self, letter):
        self.registers[letter].known_value = False

    def forget_all_registers(self):
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

    def e_operation(self, name_a, name_b, operation, line):
        a, b = self.prepare_and_check_initialization(name_a, name_b, line)
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
            self.create_savepoint()
            result = a.value + b.value
            cost_const = self.set_register_value("b", result)
            self.load_savepoint()
            cost_alt1 = self.set_register_to_number("b", a)
            cost_alt1 += self.set_register_to_number("c", b)
            cost_alt1 += 5
            self.load_savepoint()
            cost_alt2 = self.set_register_to_number("b", b)
            cost_alt2 += self.set_register_to_number("c", a)
            cost_alt2 += 5
            self.load_savepoint()
            if a.saved and b.saved:
                cost_alt3 = self.set_register_value("a", a.memory_address)
                self.get_from_memory("b", a)
                cost_alt3 += 20
                cost_alt3 += self.set_register_value("a", b.memory_address)
                self.get_from_memory("c", b)
                cost_alt3 += 25
                self.load_savepoint()
                cost_alt4 = self.set_register_value("a", a.memory_address)
                self.get_from_memory("b", a)
                cost_alt4 += self.set_register_to_number("b", b)
                cost_alt4 += 25
                self.load_savepoint()
                cost_alt5 = self.set_register_value("a", b.memory_address)
                self.get_from_memory("b", b)
                cost_alt5 += self.set_register_to_number("c", a)
                cost_alt5 += 25
                self.load_savepoint()
                if cost_const < cost_alt1 and cost_const < cost_alt2 and cost_const < cost_alt3 and cost_const < cost_alt4 and cost_const < cost_alt5:
                    self.set_register_value("b", result)
                else:
                    if cost_alt1 < cost_alt2 and cost_alt1 < cost_alt3 and cost_alt1 < cost_alt4 and cost_alt1 < cost_alt5:
                        self.set_register_to_number("b", a)
                        self.set_register_to_number("c", b)
                    elif cost_alt2 < cost_alt1 and cost_alt2 < cost_alt3 and cost_alt2 < cost_alt4 and cost_alt2 < cost_alt5:
                        self.set_register_to_number("b", b)
                        self.set_register_to_number("c", a)
                    elif cost_alt3 < cost_alt1 and cost_alt3 < cost_alt2 and cost_alt3 < cost_alt4 and cost_alt3 < cost_alt5:
                        self.get_from_memory("b", a)
                        self.get_from_memory("c", b)
                    elif cost_alt4 < cost_alt1 and cost_alt4 < cost_alt2 and cost_alt4 < cost_alt3 and cost_alt4 < cost_alt5:
                        self.get_from_memory("b", a)
                        self.set_register_to_number("c", b)
                    else:
                        self.get_from_memory("b", b)
                        self.set_register_to_number("c", a)
                    self.add_command("ADD b c")
            elif a.saved:
                cost_alt3 = self.set_register_value("a", a.memory_address)
                self.get_from_memory("b", a)
                cost_alt3 += self.set_register_to_number("b", b)
                cost_alt3 += 25
                self.load_savepoint()
                if cost_const < cost_alt1 and cost_const < cost_alt2 and cost_const < cost_alt3:
                    self.set_register_value("b", result)
                else:
                    if cost_alt1 < cost_alt2 and cost_alt1 < cost_alt3:
                        self.set_register_to_number("b", a)
                        self.set_register_to_number("c", b)
                    elif cost_alt2 < cost_alt1 and cost_alt2 < cost_alt3:
                        self.set_register_to_number("b", b)
                        self.set_register_to_number("c", a)
                    else:
                        self.get_from_memory("b", a)
                        self.set_register_to_number("c", b)
                    self.add_command("ADD b c")
            elif b.saved:
                cost_alt3 = self.set_register_value("a", b.memory_address)
                self.get_from_memory("b", b)
                cost_alt3 += self.set_register_to_number("c", a)
                cost_alt3 += 25
                self.load_savepoint()
                if cost_const < cost_alt1 and cost_const < cost_alt2 and cost_const < cost_alt3:
                    self.set_register_value("b", result)
                else:
                    if cost_alt1 < cost_alt2 and cost_alt1 < cost_alt3:
                        self.set_register_to_number("b", a)
                        self.set_register_to_number("c", b)
                    elif cost_alt2 < cost_alt1 and cost_alt2 < cost_alt3:
                        self.set_register_to_number("b", b)
                        self.set_register_to_number("c", a)
                    else:
                        self.get_from_memory("b", b)
                        self.set_register_to_number("c", a)
                    self.add_command("ADD b c")
            else:
                if cost_const < cost_alt1 and cost_const < cost_alt2:
                    self.set_register_value("b", result)
                else:
                    if cost_alt1 < cost_alt2:
                        self.set_register_to_number("b", a)
                        self.set_register_to_number("c", b)
                    else:
                        self.set_register_to_number("b", b)
                        self.set_register_to_number("c", a)
                    self.add_command("ADD b c")
            self.remember_register("b", result)
        elif isinstance(a, Number):
            self.create_savepoint()
            const1 = self.set_register_value("a", b.memory_address)
            self.get_from_memory("b", b)
            const1 += 25
            const1 += self.set_register_to_number("c", a)
            self.load_savepoint()
            const2 = self.set_register_value("a", b.memory_address)
            self.get_from_memory("c", b)
            const2 += 25
            const2 += self.set_register_to_number("b", a)
            self.load_savepoint()
            alt1 = self.set_register_value("a", b.memory_address)
            alt1 += 20 + a.value
            self.load_savepoint()
            if const1 < const2 and const1 < alt1:
                self.get_from_memory("b", b)
                self.set_register_to_number("c", a)
                self.add_command("ADD b c")
            elif const2 < const1 and const2 < alt1:
                self.get_from_memory("c", b)
                self.set_register_to_number("b", a)
                self.add_command("ADD b c")
            else:
                self.get_from_memory("b", b)
                for x in range(a.value):
                    self.add_command("INC b")
            self.forget_register("b")
        elif isinstance(b, Number):
            self.create_savepoint()
            const1 = self.set_register_value("a", a.memory_address)
            self.get_from_memory("b", a)
            const1 += 25
            const1 += self.set_register_to_number("c", b)
            self.load_savepoint()
            const2 = self.set_register_value("a", a.memory_address)
            self.get_from_memory("c", a)
            const2 += 25
            const2 += self.set_register_to_number("b", b)
            self.load_savepoint()
            alt1 = self.set_register_value("a", a.memory_address)
            alt1 += 20 + b.value
            self.load_savepoint()
            if const1 < const2 and const1 < alt1:
                self.get_from_memory("b", a)
                self.set_register_to_number("c", b)
                self.add_command("ADD b c")
            elif const2 < const1 and const2 < alt1:
                self.get_from_memory("c", a)
                self.set_register_to_number("b", b)
                self.add_command("ADD b c")
            else:
                self.get_from_memory("b", a)
                for x in range(b.value):
                    self.add_command("INC b")
            self.forget_register("b")
        else:
            self.create_savepoint()
            cost1 = self.set_register_value("a", a.memory_address)
            cost1 += self.set_register_value("a", b.memory_address)
            cost1 += 5
            self.load_savepoint()
            cost2 = self.set_register_value("a", b.memory_address)
            cost2 += self.set_register_value("a", a.memory_address)
            cost2 += 5
            self.load_savepoint()
            if cost1 < cost2:
                self.get_from_memory("b", a)
                self.get_from_memory("c", b)
            else:
                self.get_from_memory("b", b)
                self.get_from_memory("c", a)
            self.add_command("ADD b c")
            self.forget_register("b")

    def e_sub(self, a, b, line):
        if isinstance(a, Number) and isinstance(b, Number):
            self.create_savepoint()
            result = max(0, a.value - b.value)
            cost_const = self.set_register_value("b", result)
            self.load_savepoint()
            cost_alt1 = self.set_register_to_number("b", a)
            cost_alt1 += self.set_register_to_number("c", b)
            cost_alt1 += 5
            self.load_savepoint()
            if a.saved and b.saved:
                cost_alt3 = self.set_register_value("a", a.memory_address)
                self.get_from_memory("b", a)
                cost_alt3 += 20
                cost_alt3 += self.set_register_value("a", b.memory_address)
                self.get_from_memory("c", b)
                cost_alt3 += 25
                self.load_savepoint()
                cost_alt4 = self.set_register_value("a", a.memory_address)
                self.get_from_memory("b", a)
                cost_alt4 += self.set_register_to_number("c", b)
                cost_alt4 += 25
                self.load_savepoint()
                cost_alt5 = self.set_register_value("a", b.memory_address)
                self.get_from_memory("c", b)
                cost_alt5 += self.set_register_to_number("b", a)
                cost_alt5 += 25
                self.load_savepoint()
                if cost_const < cost_alt1 and cost_const < cost_alt3 and cost_const < cost_alt4 and cost_const < cost_alt5:
                    self.set_register_value("b", result)
                else:
                    if cost_alt1 < cost_alt3 and cost_alt1 < cost_alt4 and cost_alt1 < cost_alt5:
                        self.set_register_to_number("b", a)
                        self.set_register_to_number("c", b)
                    elif cost_alt3 < cost_alt1 and cost_alt3 < cost_alt4 and cost_alt3 < cost_alt5:
                        self.get_from_memory("b", a)
                        self.get_from_memory("c", b)
                    elif cost_alt4 < cost_alt1 and cost_alt4 < cost_alt3 and cost_alt4 < cost_alt5:
                        self.get_from_memory("b", a)
                        self.set_register_to_number("c", b)
                    else:
                        self.get_from_memory("c", b)
                        self.set_register_to_number("b", a)
                    self.add_command("SUB b c")
            elif a.saved:
                cost_alt3 = self.set_register_value("a", a.memory_address)
                self.get_from_memory("b", a)
                cost_alt3 += self.set_register_to_number("b", b)
                cost_alt3 += 25
                self.load_savepoint()
                if cost_const < cost_alt1 and cost_const < cost_alt3:
                    self.set_register_value("b", result)
                else:
                    if cost_alt1 < cost_alt3:
                        self.set_register_to_number("b", a)
                        self.set_register_to_number("c", b)
                    else:
                        self.get_from_memory("b", a)
                        self.set_register_to_number("c", b)
                    self.add_command("SUB b c")
            elif b.saved:
                cost_alt3 = self.set_register_value("a", b.memory_address)
                self.get_from_memory("c", b)
                cost_alt3 += self.set_register_to_number("b", a)
                cost_alt3 += 25
                self.load_savepoint()
                if cost_const < cost_alt1 and cost_const < cost_alt3:
                    self.set_register_value("b", result)
                else:
                    if cost_alt1 < cost_alt3:
                        self.set_register_to_number("b", a)
                        self.set_register_to_number("c", b)
                    else:
                        self.get_from_memory("c", b)
                        self.set_register_to_number("b", a)
                    self.add_command("SUB b c")
            else:
                if cost_const < cost_alt1:
                    self.set_register_value("b", result)
                else:
                    self.set_register_to_number("b", a)
                    self.set_register_to_number("c", b)
                    self.add_command("SUB b c")
            self.remember_register("b", result)
        elif isinstance(a, Number):
            self.get_from_memory("c", b)
            self.set_register_to_number("b", a)
            self.add_command("SUB b c")
            self.forget_register("b")
        elif isinstance(b, Number):
            self.get_from_memory("b", a)
            self.set_register_to_number("c", b)
            self.add_command("SUB b c")
            self.forget_register("b")
        else:
            self.get_from_memory("b", a)
            self.get_from_memory("c", b)
            self.add_command("SUB b c")
            self.forget_register("b")

    def e_mul(self, a, b, line):
        if isinstance(a, Number) and isinstance(b, Number):
            result = a.value * b.value
            self.set_register_value("b", result)
            return
        elif isinstance(a, Number):
            if a.value == 0:
                self.set_register_value("b", 0)
                return
            elif a.value == 1:
                self.get_from_memory("b", b)
                return
            elif a.value & (a.value - 1) == 0:
                power = int(math.log2(a.value))
                self.get_from_memory("b", b)
                for i in range(power):
                    self.add_command("SHL b")
                self.forget_register("b")
                return
            else:
                self.get_from_memory("d", b)
                self.set_register_to_number("c", a)
        elif isinstance(b, Number):
            if b.value == 0:
                self.set_register_value("b", 0)
                return
            elif b.value == 1:
                self.get_from_memory("b", a)
                return
            elif b.value & (b.value - 1) == 0:
                power = int(math.log2(b.value))
                self.get_from_memory("b", a)
                for i in range(power):
                    self.add_command("SHL b")
                self.forget_register("b")
                return
            else:
                self.get_from_memory("c", a)
                self.set_register_to_number("d", b)
        else:
            self.get_from_memory("c", a)
            self.get_from_memory("d", b)
        self.add_command("RESET b")
        self.add_command("ADD b d")
        self.add_command("SUB b c")
        self.add_command("JZERO b 10")
        self.add_command("RESET b")
        self.add_command("JODD c 2")
        self.add_command("JUMP 2")
        self.add_command("ADD b d")
        self.add_command("SHL d")
        self.add_command("SHR c")
        self.add_command("JZERO c 2")
        self.add_command("JUMP -6")
        self.add_command("JUMP 8")
        self.add_command("JODD d 2")
        self.add_command("JUMP 2")
        self.add_command("ADD b c")
        self.add_command("SHL c")
        self.add_command("SHR d")
        self.add_command("JZERO d 2")
        self.add_command("JUMP -6")
        self.forget_register("b")
        self.forget_register("c")
        self.forget_register("d")

    def e_div(self, a, b, line):
        if isinstance(a, Number) and isinstance(b, Number):
            if b.value == 0:
                result = 0
            else:
                result = int(a.value / b.value)
            self.set_register_value("b", result)
            return
        elif isinstance(a, Number):
            if a.value == 0:
                self.set_register_value("b", 0)
                return
            else:
                self.get_from_memory("c", b)
                self.set_register_to_number("d", a)
        elif isinstance(b, Number):
            if b.value == 0:
                self.set_register_value("b", 0)
                return
            elif b.value == 1:
                self.get_from_memory("b", a)
                return
            elif b.value & (b.value - 1) == 0:
                power = int(math.log2(b.value))
                self.get_from_memory("b", a)
                for i in range(power):
                    self.add_command("SHR b")
                return
            else:
                self.get_from_memory("d", a)
                self.set_register_to_number("c", b)
        else:
            self.get_from_memory("d", a)
            self.get_from_memory("c", b)
        self.add_command("RESET b")
        self.add_command("JZERO c 26")
        self.insert_div_code()

    def e_mod(self, a, b, line):
        if isinstance(a, Number) and isinstance(b, Number):
            if b.value == 0:
                result = 0
            else:
                result = int(a.value % b.value)
            self.set_register_value("b", result)
            return
        elif isinstance(a, Number):
            if a.value == 0:
                self.set_register_value("b", 0)
                return
            else:
                self.get_from_memory("c", b)
                self.set_register_to_number("d", a)
        elif isinstance(b, Number):
            if b.value == 0 or b.value == 1:
                self.set_register_value("b", 0)
                return
            else:
                self.get_from_memory("d", a)
                self.set_register_to_number("c", b)
        else:
            self.get_from_memory("d", a)
            self.get_from_memory("c", b)
        self.add_command("JZERO c 27")
        self.insert_div_code()
        self.add_command("JUMP 2")
        self.add_command("RESET d")
        self.add_command("RESET b")
        self.add_command("ADD b d")

    def insert_div_code(self):
        self.add_command("RESET e")
        self.add_command("ADD e c")
        self.add_command("RESET b")
        self.add_command("ADD b e")
        self.add_command("SUB b d")
        self.add_command("JZERO b 2")
        self.add_command("JUMP 3")
        self.add_command("SHL e")
        self.add_command("JUMP -6")
        self.add_command("RESET b")
        self.add_command("RESET f")
        self.add_command("ADD f e")
        self.add_command("SUB f d")
        self.add_command("JZERO f 4")
        self.add_command("SHL b")
        self.add_command("SHR e")
        self.add_command("JUMP 5")
        self.add_command("SHL b")
        self.add_command("INC b")
        self.add_command("SUB d e")
        self.add_command("SHR e")
        self.add_command("RESET f")
        self.add_command("ADD f c")
        self.add_command("SUB f e")
        self.add_command("JZERO f -14")
        self.forget_register("b")
        self.forget_register("c")
        self.forget_register("d")
        self.forget_register("e")
        self.forget_register("f")

    def create_savepoint(self):
        self.backup_k = self.k
        self.commands_backup = copy.deepcopy(self.commands)
        self.registers_backup = copy.deepcopy(self.registers)

    def load_savepoint(self):
        self.registers = copy.deepcopy(self.registers_backup)
        self.commands = copy.deepcopy(self.commands_backup)
        self.k = self.backup_k
