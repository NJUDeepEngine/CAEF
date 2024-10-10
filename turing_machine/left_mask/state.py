r"""
Standard Pattern:
1. The first line describes the current TM stape state. Examples like:
    - LEFT_MASK, q0, [HEAD] 45321 [OUTPUT]
    - LEFT_MASK, q1,  [HEAD]45321 [OUTPUT]
    - LEFT_MASK, q1,  4[HEAD]5321 4[OUTPUT]
    - LEFT_MASK, q1,  45321[HEAD] 45321[OUTPUT]
    - LEFT_MASK, qH,  45321[HEAD] 4543
2. The second line describes the command to execute according to the current state. Examples like:
    - CMD [HEAD] R, q1
    - CMD [HEAD] R, [OUTPUT] 4, [OUTPUT] RIGHT, q1
    - CMD [HEAD] R, [OUTPUT] 5, [OUTPUT] RIGHT, q1
    - CMD [OUTPUT] LEFT, [OUTPUT] 0, qH
    - No command to execute. Halt state.
"""

class TMStateGenerator:
    def __init__(self):
        self.q0_token = 'q0'
        self.q1_token = 'q1'
        self.q2_token = 'q2'
        self.qH_token = 'qH'

        self.h_token = '[HEAD]'
        self.output_token = '[OUTPUT]'
        self.separator = '|'
        self.operator = 'LEFT_MASK'

        self.q0_state_template = '{operator}, {q0_token}, {h_token} {op} {output_token}'
        self.q1_state_template = '{operator}, {q1_token},  {l_op}{h_token}{r_op} {output}{output_token}'
        self.q2_state_template = '{operator}, {q2_token},  {op}{h_token} {output}{output_token}'
        self.qH_state_template = '{operator}, {qH_token},  {op}{h_token} {output}'

    def get_q0_state(self, op):
        op = str(op)
        separator = self.separator
        if len(separator) > 0:
            op = separator + separator.join(op)

        return self.q0_state_template.format(operator=self.operator,
                                            h_token=self.h_token,
                                            output_token=self.output_token,
                                            op=op,
                                            q0_token=self.q0_token)
    
    def get_q1_state(self, op, head_pos, output):
        op = str(op)
        output = str(output)
        
        l_op = op[:head_pos]
        r_op = op[head_pos:]

        separator = self.separator
        if len(separator) > 0:
            l_op = separator + separator.join(l_op) if len(l_op) > 0 else ''
            r_op = separator + separator.join(r_op) if len(r_op) > 0 else ''
            output = separator + separator.join(output) if len(output) > 0 else ''

        return self.q1_state_template.format(operator=self.operator,
                                            h_token=self.h_token,
                                            output_token=self.output_token,
                                            l_op=l_op,
                                            r_op=r_op,
                                            output=output,
                                            q1_token=self.q1_token)
    
    def get_q2_state(self, op, output):
        op = str(op)
        output = str(output)

        separator = self.separator
        if len(separator) > 0:
            op = separator + separator.join(op)
            output = separator + separator.join(output) if len(output) > 0 else ''

        return self.q2_state_template.format(operator=self.operator,
                                            q2_token=self.q2_token,
                                            h_token=self.h_token,
                                            output_token=self.output_token,
                                            op=op,
                                            output=output)
    
    def get_qH_state(self, op, output):
        op = str(op)
        output = str(output)

        separator = self.separator
        if len(separator) > 0:
            op = separator + separator.join(op)
            output = separator + separator.join(output) if len(output) > 0 else '0'

        return self.qH_state_template.format(operator=self.operator,
                                            h_token=self.h_token,
                                            output_token=self.output_token,
                                            op=op,
                                            output=output,
                                            qH_token=self.qH_token)


if __name__ == '__main__':
    state_gen = TMStateGenerator()
    state_gen.separator = ''

    # q0 test
    q0_str = 'LEFT_MASK, q0, [HEAD] 45321 [OUTPUT]'
    q0_gen = state_gen.get_q0_state(45321)
    assert q0_gen == q0_str, f'Expected: {q0_str}, Got: {q0_gen}'

    # q1 test
    q1_str = 'LEFT_MASK, q1,  4[HEAD]5321 4[OUTPUT]'
    q1_gen = state_gen.get_q1_state(45321, 1, 4)
    assert q1_gen == q1_str, f'Expected: {q1_str}, Got: {q1_gen}'

    # qH test
    qH_str = 'LEFT_MASK, qH,  45321[HEAD] 4532'
    qH_gen = state_gen.get_qH_state(45321, 4532)
    assert qH_gen == qH_str, f'Expected: {qH_str}, Got: {qH_gen}'
