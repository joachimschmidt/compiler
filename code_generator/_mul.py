import math

from variable import Number


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