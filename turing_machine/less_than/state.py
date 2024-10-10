import re

r"""
Standard Pattern:
1. The first line describes the current TM stape state. Examples like:
    - LESS_THAN, q0, [HEAD1] 1235[HEAD2] 1234 [OUTPUT]
    - LESS_THAN, q1,  [HEAD1]1235 [HEAD2]1234 [OUTPUT]False
    - LESS_THAN, q1,  1[HEAD1]235 1[HEAD2]234 [OUTPUT]False
    - LESS_THAN, q1,  123[HEAD1]5 123[HEAD2]4 [OUTPUT]False
    - LESS_THAN, q1,  1235[HEAD1] 1234[HEAD2] [OUTPUT]True
    - LESS_THAN, qH,  1235[HEAD1] 1234[HEAD2] True
2. The second line describes the command to execute according to the current state. Examples like:
    - CMD [HEAD1] R, [HEAD2] R, [OUTPUT] False, q1
    - CMD [HEAD1] R, [HEAD2] R, q1
    - CMD [HEAD1] R, [HEAD2] R, q1
    - CMD [HEAD1] R, [HEAD2] R, [OUTPUT] True, q1
    - CMD [OUTPUT], qH
    - No command to execute. Halt state.

Algorithm:
- if d1 > d2, [OUTPUT] True
- if d1 == d2, hold
- if d1 < d2, [OUTPUT] False
"""

class LessThanTMStateGenerator:
    def __init__(self):
        self.q0_token = 'q0'
        self.q1_token = 'q1'
        self.qH_token = 'qH'

        self.h1_token = '[HEAD1]'
        self.h2_token = '[HEAD2]'
        self.output_token = '[OUTPUT]'
        self.separator = '|'
        self.operator = 'LESS_THAN'

        self.q0_tape_state_template = '{operator}, {q0_token}, {h1_token} {op1}{h2_token} {op2} {output_token}'
        self.q1_tape_state_template = '{operator}, {q1_token},  {l_op1}{h1_token}{r_op1} {l_op2}{h2_token}{r_op2} {output_token}{output}'
        self.qH_tape_state_template = '{operator}, {qH_token},  {l_op1}{h1_token}{r_op1} {l_op2}{h2_token}{r_op2} {output}'

    def get_q0_state(self, op1, op2):
        op1 = str(op1)
        op2 = str(op2)
        separator = self.separator
        if len(separator) > 0:
            op1 = separator + separator.join(op1)
            op2 = separator + separator.join(op2)

        return self.q0_tape_state_template.format(operator=self.operator,
                                            h1_token=self.h1_token,
                                            h2_token=self.h2_token,
                                            op1=op1,
                                            op2=op2,
                                            output_token=self.output_token,
                                            q0_token=self.q0_token)
    
    def get_q1_state(self, op1, op2, head1_pos, head2_pos, output):
        op1 = str(op1)
        op2 = str(op2)
        output = str(output)

        l_op1 = op1[:head1_pos]
        r_op1 = op1[head1_pos:]
        l_op2 = op2[:head2_pos]
        r_op2 = op2[head2_pos:]

        separator = self.separator
        if len(separator) > 0:
            l_op1 = separator + separator.join(l_op1) if len(l_op1) > 0 else ''
            r_op1 = separator + separator.join(r_op1) if len(r_op1) > 0 else ''
            l_op2 = separator + separator.join(l_op2) if len(l_op2) > 0 else ''
            r_op2 = separator + separator.join(r_op2) if len(r_op2) > 0 else ''

        return self.q1_tape_state_template.format(operator=self.operator,
                                            q1_token=self.q1_token,
                                            h1_token=self.h1_token,
                                            h2_token=self.h2_token,
                                            l_op1=l_op1,
                                            r_op1=r_op1,
                                            l_op2=l_op2,
                                            r_op2=r_op2,
                                            output_token=self.output_token,
                                            output=output)
    
    def get_qH_state(self, op1, op2, head1_pos, head2_pos, output):
        op1 = str(op1)
        op2 = str(op2)
        output = str(output)

        l_op1 = op1[:head1_pos]
        r_op1 = op1[head1_pos:]
        l_op2 = op2[:head2_pos]
        r_op2 = op2[head2_pos:]

        separator = self.separator
        if len(separator) > 0:
            l_op1 = separator + separator.join(l_op1) if len(l_op1) > 0 else ''
            r_op1 = separator + separator.join(r_op1) if len(r_op1) > 0 else ''
            l_op2 = separator + separator.join(l_op2) if len(l_op2) > 0 else ''
            r_op2 = separator + separator.join(r_op2) if len(r_op2) > 0 else ''

        return self.qH_tape_state_template.format(operator=self.operator,
                                            qH_token=self.qH_token,
                                            h1_token=self.h1_token,
                                            h2_token=self.h2_token,
                                            l_op1=l_op1,
                                            r_op1=r_op1,
                                            l_op2=l_op2,
                                            r_op2=r_op2,
                                            output=output)
    
if __name__ == '__main__':
    generator = LessThanTMStateGenerator()
    generator.separator = ''
    # q0 test
    q0_str = 'LESS_THAN, q0, [HEAD1] 1234[HEAD2] 1234 [OUTPUT]'
    op1 = 1234
    op2 = 1234
    q0_gen = generator.get_q0_state(op1, op2)
    assert q0_str == q0_gen, f'Expected: {q0_str}, Got: {q0_gen}'

    # q1 test
    q1_str = 'LESS_THAN, q1,  12[HEAD1]34 12[HEAD2]34 [OUTPUT]False'
    op1 = 1234
    op2 = 1234
    head1_pos = 2
    head2_pos = 2
    output = False
    q1_gen = generator.get_q1_state(op1, op2, head1_pos, head2_pos, output)
    assert q1_str == q1_gen, f'Expected: {q1_str}, Got: {q1_gen}'

    # qH test
    qH_str = 'LESS_THAN, qH,  1234[HEAD1] 1234[HEAD2] False'
    op1 = 1234
    op2 = 1234
    output = False
    qH_gen = generator.get_qH_state(op1, op2, 4, 4, output)
    assert qH_str == qH_gen, f'Expected: {qH_str}, Got: {qH_gen}'