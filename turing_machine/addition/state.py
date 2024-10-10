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
    - ADD, qc,  345[HEAD1] 678[HEAD2] [C]1 914[OUTPUT]
2. The second line describes the command to execute according to the current state. Examples like:
    - CMD: [C] 0, [HEAD1] R, [HEAD2] R, q1
    - CMD: [OUTPUT] 9, [OUTPUT] R, qC
    - CMD: [OUTPUT] 4, [OUTPUT] R, qC
    - CMD: [C], 1 [HEAD1] R, [HEAD2] R, q1

"""

class TMStateGenerator():
    def __init__(self):
        self.q0_token = 'q0'
        self.q1_token = 'q1'
        self.qH_token = 'qH'

        self.h1_token = '[HEAD1]'
        self.h2_token = '[HEAD2]'
        self.c_token = '[C]'
        self.output_token = '[OUTPUT]'
        self.separator = '|'

        self.q0_tape_state_template = '{operator}, {q0_token}, {h1_token} {op1}{h2_token} {op2} {c_token} {output_token}'
        self.q1_tape_state_template = '{operator}, {q1_token},  {l_op1}{h1_token}{r_op1} {l_op2}{h2_token}{r_op2} {c_token}{carry_out} {output}{output_token}'
        self.qC_tape_state_template = '{operator}, {qC_token},  {l_op1}{h1_token}{r_op1} {l_op2}{h2_token}{r_op2} {c_token}{carry_out} {output}{output_token}'
        self.qH_tape_state_template = '{operator}, {qH_token},  {op1}{h1_token} {op2}{h2_token} {c_token}{carry_out} {output}'

    def get_q0_state(self, operator, operand1, operand2):
        operand1 = str(operand1)
        operand2 = str(operand2)
        separator = self.separator
        if len(separator) > 0:
            operand1 = separator + separator.join(operand1)
            operand2 = separator + separator.join(operand2)
        return self.q0_tape_state_template.format(operator=operator,
                                            h1_token=self.h1_token,
                                            h2_token=self.h2_token,
                                            c_token=self.c_token,
                                            output_token=self.output_token,
                                            op1=operand1,
                                            op2=operand2,
                                            q0_token=self.q0_token)
    
    def get_q1_state(self, operator, operand1, operand2, head1_pos, head2_pos, carry_out, output):
        operand1 = str(operand1)
        operand2 = str(operand2)
        carry_out = str(carry_out)
        output = str(output)
        
        l_op1 = operand1[:head1_pos]
        r_op1 = operand1[head1_pos:]
        l_op2 = operand2[:head2_pos]
        r_op2 = operand2[head2_pos:]

        separator = self.separator
        if len(separator) > 0:
            l_op1 = separator + separator.join(l_op1) if len(l_op1) > 0 else ''
            r_op1 = separator + separator.join(r_op1) if len(r_op1) > 0 else ''
            l_op2 = separator + separator.join(l_op2) if len(l_op2) > 0 else ''
            r_op2 = separator + separator.join(r_op2) if len(r_op2) > 0 else ''
            output = separator + separator.join(output) if len(output) > 0 else ''

        return self.q1_tape_state_template.format(operator=operator,
                                                    h1_token=self.h1_token,
                                                    h2_token=self.h2_token,
                                                    c_token=self.c_token,
                                                    output_token=self.output_token,
                                                    l_op1=l_op1,
                                                    r_op1=r_op1,
                                                    l_op2=l_op2,
                                                    r_op2=r_op2,
                                                    carry_out=carry_out,
                                                    output=output,
                                                    q1_token=self.q1_token)

    def get_qH_state(self, operator, operand1, operand2, carry_out, output):
        operand1 = str(operand1)
        operand2 = str(operand2)
        carry_out = str(carry_out)
        output = str(output)

        separator = self.separator
        if len(separator) > 0:
            operand1 = separator + separator.join(operand1)
            operand2 = separator + separator.join(operand2)
            output = separator + separator.join(output)
        
        return self.qH_tape_state_template.format(operator=operator,
                                                  h1_token=self.h1_token,
                                                  h2_token=self.h2_token,
                                                  c_token=self.c_token,
                                                  output_token=self.output_token,
                                                  op1=operand1,
                                                  op2=operand2,
                                                  carry_out=carry_out,
                                                  output=output,
                                                  qH_token=self.qH_token)    

if __name__ == '__main__':
    generator = TMStateGenerator()
    generator.separator = ''
    # q0 test
    q0_str = 'ADD, q0, [HEAD1] 345[HEAD2] 678 [C] [OUTPUT]'
    operator = 'ADD'
    operand1 = 345
    operand2 = 678
    q0_str_gen = generator.get_q0_state(operator, operand1, operand2)
    assert q0_str == q0_str_gen, f'Expected: {q0_str}, Got: {q0_str_gen}'

    # q1 test
    q1_str = 'ADD, q1,  34[HEAD1]5 67[HEAD2]8 [C]1 91[OUTPUT]'
    operator = 'ADD'
    operand1 = 345
    operand2 = 678
    head1_pos = 2
    head2_pos = 2
    carry_out = 1
    output = 91
    q1_str_gen = generator.get_q1_state(operator, operand1, operand2, head1_pos, head2_pos, carry_out, output)
    assert q1_str == q1_str_gen, f'Expected: {q1_str}, Got: {q1_str_gen}'

    # qH test
    qH_str = 'ADD, qH,  345[HEAD1] 678[HEAD2] [C]1 9141'
    operator = 'ADD'
    operand1 = 345
    operand2 = 678
    carry_out = 1
    output = 9141
    qH_str_gen = generator.get_qH_state(operator, operand1, operand2, carry_out, output)
    assert qH_str == qH_str_gen, f'Expected: {qH_str}, Got: {qH_str_gen}'



