from definitions.jump import Jump
from definitions.variable import Number


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


def cond_eq(self, a, b, line):
    self.variable_to_register("c", a)
    self.variable_to_register("d", b)
    self.add_command("RESET e")
    self.add_command("RESET b")
    self.add_command("ADD b c")
    self.add_command("SUB b d")
    self.add_command("JZERO b 2")
    self.add_command("JUMP 5")
    self.add_command("SUB d c")
    self.add_command("JZERO d 2")
    self.add_command("JUMP 2")
    self.add_command("INC e")
    self.jumps.append(Jump(self.k))
    self.add_command("JZERO e ")
    self.forget_register("b")
    self.forget_register("c")
    self.forget_register("d")
    self.forget_register("e")


def cond_neq(self, a, b, line):
    self.variable_to_register("c", a)
    self.variable_to_register("d", b)
    self.add_command("RESET e")
    self.add_command("RESET b")
    self.add_command("ADD b c")
    self.add_command("SUB b d")
    self.add_command("JZERO b 2")
    self.add_command("INC e")
    self.add_command("SUB d c")
    self.add_command("JZERO d 2")
    self.add_command("INC e")
    self.jumps.append(Jump(self.k))
    self.add_command("JZERO e ")
    self.forget_register("b")
    self.forget_register("c")
    self.forget_register("d")
    self.forget_register("e")


def cond_lt(self, a, b, line):
    self.variable_to_register("c", a)
    self.variable_to_register("d", b)
    self.add_command("RESET e")
    self.add_command("ADD e d")
    self.add_command("SUB e c")
    self.jumps.append(Jump(self.k))
    self.add_command("JZERO e ")
    self.forget_register("c")
    self.forget_register("e")


def cond_gt(self, a, b, line):
    self.variable_to_register("d", a)
    self.variable_to_register("c", b)
    self.add_command("RESET e")
    self.add_command("ADD e d")
    self.add_command("SUB e c")
    self.jumps.append(Jump(self.k))
    self.add_command("JZERO e ")
    self.forget_register("c")
    self.forget_register("e")


def cond_let(self, a, b, line):
    self.variable_to_register("c", a)
    self.variable_to_register("d", b)
    self.add_command("RESET e")
    self.add_command("ADD e d")
    self.add_command("INC e")
    self.add_command("SUB e c")
    self.jumps.append(Jump(self.k))
    self.add_command("JZERO e ")
    self.forget_register("c")
    self.forget_register("e")


def cond_get(self, a, b, line):
    self.variable_to_register("d", a)
    self.variable_to_register("c", b)
    self.add_command("RESET e")
    self.add_command("ADD e d")
    self.add_command("INC e")
    self.add_command("SUB e c")
    self.jumps.append(Jump(self.k))
    self.add_command("JZERO e ")
    self.forget_register("c")
    self.forget_register("e")
