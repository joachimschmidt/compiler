from definitions.variable import *


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
