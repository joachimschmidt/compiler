from definitions.variable import Number


def e_sub(self, a, b, line):
    if isinstance(a, Number) and isinstance(b, Number):
        result = max(0, a.value - b.value)
        self.set_register_value("b", result)
        self.remember_register("b", result)
    elif isinstance(a, Number):
        self.get_from_memory("d", b)
        self.set_register_to_number("b", a)
        self.add_command("SUB b d")
        self.forget_register("b")
    elif isinstance(b, Number):
        self.get_from_memory("b", a)
        self.set_register_to_number("d", b)
        self.add_command("SUB b d")
        self.forget_register("b")
    else:
        self.get_from_memory("b", a)
        self.get_from_memory("d", b)
        self.add_command("SUB b d")
        self.forget_register("b")
