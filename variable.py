class Variable:
    def __init__(self, name, memory_address):
        self.name = name
        self.memory_address = memory_address
        self.occurrences = 0


class Number(Variable):
    def __init__(self, name, value, memory_address):
        self.value = value
        self.in_write = False
        self.is_stored = False
        super().__init__(name, memory_address)


class Iterator(Variable):
    def __init__(self, name, memory_address):
        self.in_use = False
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
