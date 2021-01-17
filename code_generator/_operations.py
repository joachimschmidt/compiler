from definitions.variable import Number


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


def e_value(self, name, line):
    variable = self.prepare_variable(name, line)
    self.check_initialization(variable, line)
    if isinstance(variable, Number):
        if not variable.saved:
            self.set_register_to_number("b", variable)
            return
    self.get_from_memory("b", variable)
