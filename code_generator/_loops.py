import copy

from jump import Jump
from loop import Loop
from variable import Iterator, Number


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
    self.forget_all_registers()


def c_exit_repeat(self):
    self.commands.pop()
    self.k -= 1
    self.jumps.pop()
    self.add_command("JZERO e 2")
    self.add_command("JUMP 2")
    self.add_command("JUMP {}".format(self.loops[-1].k - self.k))
    self.loops.pop()
    self.forget_all_registers()


def prepare_iterator(self, iterator, start, end, line):
    i = self.variables[iterator]
    if isinstance(i, Iterator):
        if i.in_use:
            self.handle_error("Iterator {} repeated ".format(iterator), line)
        else:
            start_variable = self.prepare_variable(start, line)
            end_variable = self.prepare_variable(end, line)
            self.check_initialization(start_variable, line)
            self.check_initialization(end_variable, line)
            i.start = start_variable
            i.end = end_variable
            i.in_use = True
            self.variable_to_register("f", i.start)
            self.variable_to_register("c", i.end)
            i.end = copy.deepcopy(i.end)
            i.end.memory_address = i.memory_address + 1
            if isinstance(i.end, Number):
                cost = self.get_cost_and_method_of_set_register_to_value("a", i.end.memory_address, cost_only=True)
                cost += 20
                self.backup_registers()
                self.forget_all_registers()
                cost2 = self.get_cost_and_method_of_set_register_to_value("c", i.end.value, cost_only=True)
                self.restore_registers()
                if cost < cost2:
                    self.save_to_memory("f", i)
                    self.save_to_memory("c", i.end, iterator_end=True)
                    i.end.is_stored = True
                    i.end.saved = True
                else:
                    self.save_to_memory("f", i)
                    i.end.is_stored = False
                    i.end.saved = False
            else:
                self.save_to_memory("f", i)
                self.save_to_memory("c", i.end)
            self.loops.append(Loop(self.k, i))
            return i
    else:
        self.handle_error("Repeated declaration of {}".format(iterator), line)


def dismiss_iterator(self, i):
    self.variables[i.name].in_use = False


def c_for_to(self, iterator, start, end, line):
    self.prepare_iterator(iterator, start, end, line)
    self.add_command("INC c")
    self.add_command("SUB c f")
    self.jumps.append(Jump(self.k))
    self.add_command("JZERO c ")
    self.forget_all_registers()


def c_for_down_to(self, iterator, start, end, line):
    self.prepare_iterator(iterator, start, end, line)
    self.add_command("INC f")
    self.add_command("SUB f c")
    self.jumps.append(Jump(self.k))
    self.add_command("JZERO f ")
    self.forget_all_registers()


def c_exit_for_to(self):
    i = self.loops[-1].iterator
    self.variable_to_register("f", i)
    self.variable_to_register("c", i.end)
    self.add_command("INC f")
    self.add_command("INC c")
    self.add_command("SUB c f")
    self.jumps.append(Jump(self.k))
    self.add_command("JZERO c ")
    self.save_to_memory("f", i)
    self.add_command("JUMP {}".format(self.jumps[-2].k - self.k + 1))
    self.commands[self.jumps[-1].k] += str(self.k - self.jumps[-1].k)
    self.jumps.pop()
    self.commands[self.jumps[-1].k] += str(self.k - self.jumps[-1].k)
    self.jumps.pop()
    self.loops.pop()
    self.dismiss_iterator(i)
    self.forget_all_registers()


def c_exit_for_down_to(self):
    i = self.loops[-1].iterator
    self.variable_to_register("f", i)
    self.variable_to_register("c", i.end)
    self.jumps.append(Jump(self.k))
    self.add_command("JZERO f ")
    self.add_command("DEC f")
    self.save_to_memory("f", i)
    self.add_command("INC f")
    self.add_command("SUB f c")
    self.jumps.append(Jump(self.k))
    self.add_command("JZERO f ")
    self.add_command("JUMP {}".format(self.jumps[-3].k - self.k + 1))
    self.commands[self.jumps[-1].k] += str(self.k - self.jumps[-1].k)
    self.jumps.pop()
    self.commands[self.jumps[-1].k] += str(self.k - self.jumps[-1].k)
    self.jumps.pop()
    self.commands[self.jumps[-1].k] += str(self.k - self.jumps[-1].k)
    self.jumps.pop()
    self.loops.pop()
    self.dismiss_iterator(i)
    self.forget_all_registers()