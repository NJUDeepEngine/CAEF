# Warning: change these templates with caution.

uniform_qH_cmd = 'No command to execute. Halt state.'

add = dict(
    q0_state_template = '{operator}, {q0_token}, {h1_token} {op1}{h2_token} {op2} {c_token} {output_token}',
    q0_cmd_template = '{cmd_token}: {c_token} 0, {h1_token} {right_token}, {h2_token} {right_token}, {q1_token}',
)

reflection = dict(
    q0_state_template = '{operator}, {q0_token}, {h1_token} {op1}{h2_token} {op2} {output_token}',
    q0_cmd_template = '{cmd_token} {h1_token} {right_token}, {h2_token} {right_token}, {q1_token}',
)

left_mask = dict(
    q0_state_template = '{operator}, {q0_token}, {h_token} {op} {output_token}',
    q0_cmd_template = '{cmd_token} {h_token} {right_token}, {q1_token}',
)

sub = dict(
    q0_state_template = '{operator}, {q0_token}, {h1_token}{op1} {h2_token}{op2} ',
    q0_cmd_template = '{cmd_token} {q1_token}'
)

greater_than = dict(
    q0_state_template = '{operator}, {q0_token}, {h1_token} {op1}{h2_token} {op2} {output_token}',
    q0_cmd_template = '{cmd_token} {h1_token} {right_token}, {h2_token} {right_token}, {output_token} {false_token}, {q1_token}',
)

less_than = dict(
    q0_state_template = '{operator}, {q0_token}, {h1_token} {op1}{h2_token} {op2} {output_token}',
    q0_cmd_template = '{cmd_token} {h1_token} {right_token}, {h2_token} {right_token}, {output_token} {false_token}, {q1_token}',
)

equal = dict(
    q0_state_template = '{operator}, {q0_token}, {h1_token} {op1}{h2_token} {op2} {output_token}',
    q0_cmd_template = '{cmd_token} {h1_token} {right_token}, {h2_token} {right_token}, {output_token} {true_token}, {q1_token}',
)

mul = dict(
    q0_state_template = '{operator}, {q0_token}, {h1_token}{op1} {h2_token}{op2} {count_token}{count} {output_token}',
    q0_cmd_template = '{cmd_token} {count_token} 1, {output_token}{output}, {q1_token}',
)

div = dict(
    q0_state_template = '{operator}, {q0_token}, {h1_token}{op1} {h2_token}{op2} {count_token} {output_token}',
    q0_cmd_template = '{cmd_token} {count_token}{count}, {output_token} 0, {q1_token}',
)

templates = {
    'add': add,
    'reflection': reflection,
    'left_mask': left_mask,
    'sub': sub,
    'equal': equal,
    'greater_than': greater_than,
    'less_than': less_than,
    'mul': mul,
    'div': div,
}