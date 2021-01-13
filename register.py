class Register:
    def __init__(self, letter):
        self.letter = letter
        self.known_value = False
        self.value = None

    def __str__(self):
        return "{}: value: {}".format(self.letter, self.value)
