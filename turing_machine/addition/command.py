import re

r""" Turing Machine(TM) utils for LLM.

States:
    - `q0`: Initial state
    - `q1`: Reading digits and adding
    - `qC`: Handling carry
    - `qH`: Halt state

Transition Rules
1. Start at `q0`, set carry `c` to 0 and move to `q1`.
2. In `q1`, read digits from both numbers and carry `c`:
   - If reading `a` from number 1 and `b` from number 2:
     - Write `(a+b+c)%10` and move to `qC`.
   - Else if reading `a` from number 1 or `a` from number 2:
     - Write `(a+c)%10` and move to `qC`.
3. In `qC`, handle carry:
   - Set carry `c` to 1 if `(a+b+c) >= 10`, else set carry `c` to 0.
   - Move to `q1`.
4. Repeat until all digits are processed.
5. If at the end, there’s a carry, write it and move to `qH`.

Standard Pattern:
1. The first line describes the current TM stape state. Examples like:
    - ADD, q0, [HEAD1] 345[HEAD2] 678 [C] [OUTPUT]
    - ADD, q1,  [HEAD1]345 [HEAD2]678 [C]0 [OUTPUT]
    - ADD, q1,  34[HEAD1]5 67[HEAD2]8 [C]1 91[OUTPUT]
2. The second line describes the command to execute according to the current state. Examples like:
    - CMD: [C] 0, [HEAD1] R, [HEAD2] R, q1
    - CMD: [C] 0, [OUTPUT] 9, [OUTPUT] R, [HEAD1] R, [HEAD2] R, q1
    - CMD: [C] 1, [OUTPUT] 4, [OUTPUT] R, [HEAD1] R, [HEAD2] R, q1

"""

class TMCommandGenerator():
    def __init__(self):
        self.q0_token = 'q0'
        self.q1_token = 'q1'
        self.qH_token = 'qH'

        self.h1_token = '[HEAD1]'
        self.h2_token = '[HEAD2]'
        self.c_token = '[C]'
        self.output_token = '[OUTPUT]'
        self.cmd_token = 'CMD'

        self.right_token = 'RIGHT'
        self.left_token = 'LEFT'

        self.q0_cmd_template = '{cmd_token}: {c_token} 0, {h1_token} {right_token}, {h2_token} {right_token}, {q1_token}'
        self.q1_2_q1_cmd_template = '{cmd_token}: {c_token} {carry_out}, {output_token} {output}, {output_token} {right_token}, {h1_act}{h2_act}{q1_token}'
        self.q1_2_qH_cmd_template = '{cmd_token}: {output_token} {output}, {output_token}, {c_token}, {qH_token}'

    def get_q0_cmd(self):
        return self.q0_cmd_template.format(cmd_token=self.cmd_token,
                                           c_token=self.c_token,
                                           h1_token=self.h1_token,
                                           right_token=self.right_token,
                                           h2_token=self.h2_token,
                                           q1_token=self.q1_token)
    
    def get_q1_cmd(self, output, next_state, carry_out, h1_r, h2_r):
        if next_state == 'q1':
            h1_act = h2_act = ''
            if h1_r:
                h1_act = f'{self.h1_token} {self.right_token}, '
            if h2_r:
                h2_act = f'{self.h2_token} {self.right_token}, '
            return self.q1_2_q1_cmd_template.format(cmd_token=self.cmd_token,
                                                    c_token=self.c_token,
                                                    carry_out=carry_out,
                                                    output_token=self.output_token,
                                                    output=output,
                                                    right_token=self.right_token,
                                                    h1_act=h1_act,
                                                    h2_act=h2_act,
                                                    q1_token=self.q1_token)
        elif next_state == 'qH':
            return self.q1_2_qH_cmd_template.format(cmd_token=self.cmd_token,
                                                    output_token=self.output_token,
                                                    output=output,
                                                    right_token=self.right_token,
                                                    qH_token=self.qH_token,
                                                    c_token=self.c_token)
        else:
            raise ValueError(f'Invalid next state: {next_state}')
    
if __name__ == "__main__":
    cmd_gen = TMCommandGenerator()
    # q0 test
    q0_str = 'CMD: [C] 0, [HEAD1] RIGHT, [HEAD2] RIGHT, q1'
    qo_str_gen = cmd_gen.get_q0_cmd()
    assert q0_str == qo_str_gen, f"Expected: {q0_str}, Got: {qo_str_gen}"

    # q1 to q1 test
    q1_str = 'CMD: [C] 0, [OUTPUT] 9, [OUTPUT] RIGHT, [HEAD1] RIGHT, [HEAD2] RIGHT, q1'
    q1_str_gen = cmd_gen.get_q1_cmd(9, 'q1', 0, True, True)
    assert q1_str == q1_str_gen, f"Expected: {q1_str}, Got: {q1_str_gen}"

    # q1 to qH test
    q1_str = 'CMD: [OUTPUT] 1, [OUTPUT], [C], qH'
    q1_str_gen = cmd_gen.get_q1_cmd(1, 'qH', 0, False, False)
    assert q1_str == q1_str_gen, f"Expected: {q1_str}, Got: {q1_str_gen}"