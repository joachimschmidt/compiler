class CodeGenerator:
    def __init__(self, variables):
        self.commands_backup = []
        self.registers_backup = {}
        self.variables_backup = {}
        self.registers_backup_2 = {}
        self.backup_k = 0
        self.variables = variables
        self.commands = []
        self.jumps = []
        self.loops = []
        self.k = 0
        self.registers = {}
        self.generate_registers()
        self.save_numbers_from_loop()

    from ._conds import conditions, cond_gt, cond_lt, cond_eq, cond_get, cond_let, cond_neq
    from ._commands import c_write, c_read, c_assign
    from ._utils import check_array_declaration, check_array_reference_by_identifier, check_array_reference_by_number, \
        check_identifier_reference, get_cost_and_method_of_set_register_to_value, add_command, get_all_registers, \
        set_address, set_register_value, end_program, save_to_memory, handle_error, generate_registers, \
        set_register_to_number, get_from_memory, get_register_by_letter, prepare_variable, remember_register, \
        restore_registers, load_savepoint, forget_everything, backup_registers, forget_register, create_savepoint, \
        check_initialization, variable_to_register, prepare_and_check_initialization, save_numbers_from_loop
    from ._loops import prepare_iterator, c_exit_for_down_to, c_exit_for_to, c_exit_repeat, c_exit_while, c_if_else, \
        dismiss_iterator, c_while, c_if, c_for_to, c_begin_if, c_for_down_to
    from ._operations import e_operation, e_value
    from ._add import e_add
    from ._sub import e_sub
    from ._mul import e_mul
    from ._div_and_mod import e_div, e_mod, insert_div_code
