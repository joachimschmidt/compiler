import math

from variable import Number


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