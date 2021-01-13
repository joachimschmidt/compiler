def cost_of_set_const(value):
    cost = 1
    binary = get_binary(value)
    for i in range(len(binary)):
        if binary[i] == "1":
            cost += 1
        if i < len(binary) - 1:
            cost += 1
    return cost


def cost_of_set_by_steps(start, goal):
    diff = abs(goal - start)
    return diff


def cost_of_set_by_copy_and_steps(goal, copy_value):
    diff = abs(goal - copy_value)
    cost = 6
    cost += diff
    return cost


def cost_of_set_by_add_to_base(goal, copy_value):
    base = goal - copy_value
    cost = cost_of_set_const(base) + 5
    return cost


def cost_of_set_by_add_and_steps(start, goal, copy_value):
    start_result = start + copy_value
    diff = abs(goal - start_result)
    cost = diff + 5
    return cost


def cost_of_set_by_steps_and_sub(start, goal, copy_value):
    start_result = start - copy_value
    diff = abs(goal - start_result)
    cost = diff + 5
    return cost


def get_binary(value):
    return str(bin(value).replace('0b', ''))


def set_register_to_value(method, letter, value, registers, register):
    if method == "nothing":
        return []
    x = method.split(" ")
    if x[0] == "const":
        return set_register_to_const(letter, value)
    if x[0] == "steps":
        return set_register_by_steps(letter, register, value)
    if x[0] == "addsteps":
        help_register = find_correct_register(x[1], registers)
        return set_register_by_add_and_steps(register, letter, help_register, value)
    if x[0] == "substeps":
        help_register = find_correct_register(x[1], registers)
        return set_register_by_sub_and_steps(register, letter, help_register, value)
    if x[0] == "baseadd":
        help_register = find_correct_register(x[1], registers)
        return set_register_by_base_and_add(letter, help_register, value)
    if x[0] == "copysteps":
        help_register = find_correct_register(x[1], registers)
        return set_register_by_copy_and_steps(letter, help_register, value)


def find_correct_register(letter, registers):
    for reg in registers:
        if reg.letter == letter:
            return reg


def set_register_by_base_and_add(letter, help_register, value):
    commands = ["RESET " + letter]
    base = value - help_register.value
    commands += set_register_to_const(letter, base)
    commands.append("ADD {} {}".format(letter, help_register.letter))
    return commands


def set_register_by_copy_and_steps(letter, help_register, value):
    commands = ["RESET " + letter,
                "ADD {} {}".format(letter, help_register.letter)]
    diff = abs(value - help_register.value)
    if value > help_register.value:
        command = "INC " + letter
    else:
        command = "DEC " + letter
    for i in range(diff):
        commands.append(command)
    return commands


def set_register_by_add_and_steps(register, letter, help_register, value):
    commands = ["ADD {} {}".format(letter, help_register.letter)]
    start_result = register.value + help_register.value
    diff = abs(value - start_result)
    if value > start_result:
        command = "INC " + letter
    else:
        command = "DEC " + letter
    for i in range(diff):
        commands.append(command)
    return commands


def set_register_by_sub_and_steps(register, letter, help_register, value):
    commands = ["SUB {} {}".format(register.letter, help_register.letter)]
    start_result = register.value - help_register.value
    diff = abs(value - start_result)
    if value > start_result:
        command = "INC " + letter
    else:
        command = "DEC " + letter
    for i in range(diff):
        commands.append(command)
    return commands


def set_register_by_steps(letter, register, value):
    diff = abs(register.value - value)
    commands = []
    if register.value > value:
        command = "DEC " + letter
    else:
        command = "INC " + letter
    for i in range(diff):
        commands.append(command)
    return commands


def set_register_to_const(letter, const):
    commands = ["RESET " + letter]
    binary = str(bin(const).replace('0b', ''))
    for i in range(len(binary)):
        if binary[i] == "1":
            commands.append("INC " + letter)
        if i < len(binary) - 1:
            commands.append("SHL " + letter)
    return commands


def get_set_register_best_method(reg, value, all_register):
    min_cost = cost_of_set_const(value)
    current_method = "const"
    if reg.known_value:
        if reg.value != value:
            by_steps = cost_of_set_by_steps(reg.value, value)
            if by_steps < min_cost:
                min_cost = by_steps
                current_method = "steps"
            for register in all_register:
                add_and_steps = cost_of_set_by_add_and_steps(reg.value, value, register.value)
                if add_and_steps < min_cost:
                    min_cost = add_and_steps
                    current_method = "addsteps " + register.letter
            for register in all_register:
                if register.letter != reg.letter and register.value < reg.value:
                    sub_and_steps = cost_of_set_by_steps_and_sub(reg.value, value, register.value)
                    if sub_and_steps < min_cost:
                        min_cost = sub_and_steps
                        current_method = "substeps " + register.letter
        else:
            min_cost = 0
            current_method = "nothing"
    for register in all_register:
        if register.letter != reg.letter:
            base_and_add = cost_of_set_by_add_to_base(value, register.value)
            if base_and_add < min_cost:
                min_cost = base_and_add
                current_method = "baseadd " + register.letter
    for register in all_register:
        if register.letter != reg.letter:
            copy_and_steps = cost_of_set_by_copy_and_steps(value, register.value)
            if copy_and_steps < min_cost:
                min_cost = copy_and_steps
                current_method = "copysteps " + register.letter
    return min_cost, current_method
