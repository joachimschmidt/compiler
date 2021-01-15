class Variable:
    def __init__(self, name, memory_address):
        self.name = name
        self.memory_address = memory_address
        self.occurrences = 0

    def __str__(self):
        return str(self.name)


class Number(Variable):
    def __init__(self, name, value, memory_address):
        self.value = value
        self.in_write = False
        self.saved = False
        self.is_stored = False
        super().__init__(name, memory_address)

    def __str__(self):
        return "Number {} storable:{} saved:{}".format(self.name, self.is_stored, self.saved)


class Iterator(Variable):
    def __init__(self, name, memory_address):
        self.in_use = False
        self.end = None
        self.start = None
        super().__init__(name, memory_address)


class Array(Variable):
    def __init__(self, name, start, end, memory_address):
        self.start = start
        self.end = end
        self.references = []
        super().__init__(name, memory_address)


class Identifier(Variable):
    def __init__(self, name, memory_address):
        self.initialized = False
        super().__init__(name, memory_address)
