from variable import Number


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
            if cost_const <= cost_alt1 and cost_const <= cost_alt3 and cost_const <= cost_alt4 and cost_const <= cost_alt5:
                self.set_register_value("b", result)
            else:
                if cost_alt1 <= cost_alt3 and cost_alt1 <= cost_alt4 and cost_alt1 <= cost_alt5:
                    self.set_register_to_number("b", a)
                    self.set_register_to_number("c", b)
                elif cost_alt3 <= cost_alt1 and cost_alt3 <= cost_alt4 and cost_alt3 <= cost_alt5:
                    self.get_from_memory("b", a)
                    self.get_from_memory("c", b)
                elif cost_alt4 <= cost_alt1 and cost_alt4 <= cost_alt3 and cost_alt4 <= cost_alt5:
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
            if cost_const <= cost_alt1 and cost_const <= cost_alt3:
                self.set_register_value("b", result)
            else:
                if cost_alt1 <= cost_alt3:
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
            if cost_const <= cost_alt1 and cost_const <= cost_alt3:
                self.set_register_value("b", result)
            else:
                if cost_alt1 <= cost_alt3:
                    self.set_register_to_number("b", a)
                    self.set_register_to_number("c", b)
                else:
                    self.get_from_memory("c", b)
                    self.set_register_to_number("b", a)
                self.add_command("SUB b c")
        else:
            if cost_const <= cost_alt1:
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
