from variable import Number


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
            if cost_const <= cost_alt1 and cost_const <= cost_alt2 and cost_const <= cost_alt3 and cost_const <= cost_alt4 and cost_const <= cost_alt5:
                self.set_register_value("b", result)
            else:
                if cost_alt1 <= cost_alt2 and cost_alt1 <= cost_alt3 and cost_alt1 <= cost_alt4 and cost_alt1 <= cost_alt5:
                    self.set_register_to_number("b", a)
                    self.set_register_to_number("c", b)
                elif cost_alt2 <= cost_alt1 and cost_alt2 <= cost_alt3 and cost_alt2 <= cost_alt4 and cost_alt2 <= cost_alt5:
                    self.set_register_to_number("b", b)
                    self.set_register_to_number("c", a)
                elif cost_alt3 <= cost_alt1 and cost_alt3 <= cost_alt2 and cost_alt3 <= cost_alt4 and cost_alt3 <= cost_alt5:
                    self.get_from_memory("b", a)
                    self.get_from_memory("c", b)
                elif cost_alt4 <= cost_alt1 and cost_alt4 <= cost_alt2 and cost_alt4 <= cost_alt3 and cost_alt4 <= cost_alt5:
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
            if cost_const <= cost_alt1 and cost_const <= cost_alt2 and cost_const <= cost_alt3:
                self.set_register_value("b", result)
            else:
                if cost_alt1 <= cost_alt2 and cost_alt1 <= cost_alt3:
                    self.set_register_to_number("b", a)
                    self.set_register_to_number("c", b)
                elif cost_alt2 <= cost_alt1 and cost_alt2 <= cost_alt3:
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
            if cost_const <= cost_alt1 and cost_const <= cost_alt2 and cost_const <= cost_alt3:
                self.set_register_value("b", result)
            else:
                if cost_alt1 <= cost_alt2 and cost_alt1 <= cost_alt3:
                    self.set_register_to_number("b", a)
                    self.set_register_to_number("c", b)
                elif cost_alt2 <= cost_alt1 and cost_alt2 <= cost_alt3:
                    self.set_register_to_number("b", b)
                    self.set_register_to_number("c", a)
                else:
                    self.get_from_memory("b", b)
                    self.set_register_to_number("c", a)
                self.add_command("ADD b c")
        else:
            if cost_const <= cost_alt1 and cost_const <= cost_alt2:
                self.set_register_value("b", result)
            else:
                if cost_alt1 <= cost_alt2:
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
        if const1 <= const2 and const1 <= alt1:
            self.get_from_memory("b", b)
            self.set_register_to_number("c", a)
            self.add_command("ADD b c")
        elif const2 <= const1 and const2 <= alt1:
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
        if const1 <= const2 and const1 <= alt1:
            self.get_from_memory("b", a)
            self.set_register_to_number("c", b)
            self.add_command("ADD b c")
        elif const2 <= const1 and const2 <= alt1:
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
        if cost1 <= cost2:
            self.get_from_memory("b", a)
            self.get_from_memory("c", b)
        else:
            self.get_from_memory("b", b)
            self.get_from_memory("c", a)
        self.add_command("ADD b c")
        self.forget_register("b")