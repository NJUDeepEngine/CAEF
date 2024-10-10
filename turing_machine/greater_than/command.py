import re

r"""
Standard Pattern:
1. The first line describes the current TM stape state. Examples like:
    - GREATER_THAN, q0, [HEAD1] 1235[HEAD2] 1234 [OUTPUT]
    - GREATER_THAN, q1,  [HEAD1]1235 [HEAD2]1234 [OUTPUT]False
    - GREATER_THAN, q1,  1[HEAD1]235 1[HEAD2]234 [OUTPUT]False
    - GREATER_THAN, q1,  123[HEAD1]5 123[HEAD2]4 [OUTPUT]False
    - GREATER_THAN, q1,  1235[HEAD1] 1234[HEAD2] [OUTPUT]True
    - GREATER_THAN, qH,  1235[HEAD1] 1234[HEAD2] True
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

class GreaterThanTMCommandGenerator:
    def __init__(self):
        self.q0_token = 'q0'
        self.q1_token = 'q1'
        self.qH_token = 'qH'

        self.h1_token = '[HEAD1]'
        self.h2_token = '[HEAD2]'
        self.output_token = '[OUTPUT]'
        self.cmd_token = 'CMD'
        self.true_token = 'True'
        self.false_token = 'False'

        self.right_token = 'RIGHT'
        self.left_token = 'LEFT'

        self.q0_cmd_template = '{cmd_token} {h1_token} {right_token}, {h2_token} {right_token}, {output_token} {false_token}, {q1_token}'
        self.q1_2_q1_cmd_template = '{cmd_token} {h1_token} {right_token}, {h2_token} {right_token}, {output_act}{q1_token}'
        self.q1_2_qH_cmd_template = '{cmd_token} {output_act}{output_token}, {qH_token}'

    def get_q0_cmd(self):
        return self.q0_cmd_template.format(cmd_token=self.cmd_token,
                                            h1_token=self.h1_token,
                                            h2_token=self.h2_token,
                                            right_token=self.right_token,
                                            output_token=self.output_token,
                                            false_token=self.false_token,
                                            q1_token=self.q1_token)

    
    def get_q1_cmd(self, next_state, output_act=None):

        def _format_output_act(output_token, output_act):
            if output_act == None:
                return ''
            output_act = str(output_act)
            return f'{output_token} {output_act}, '

        if next_state == 'q1':
            return self.q1_2_q1_cmd_template.format(cmd_token=self.cmd_token,
                                                    h1_token=self.h1_token,
                                                    h2_token=self.h2_token,
                                                    right_token=self.right_token,
                                                    output_act=_format_output_act(self.output_token, output_act),
                                                    q1_token=self.q1_token)
        elif next_state == 'qH':
            return self.q1_2_qH_cmd_template.format(cmd_token=self.cmd_token,
                                                    output_act=_format_output_act(self.output_token, output_act),
                                                    output_token=self.output_token,
                                                    qH_token=self.qH_token)
        else:
            raise ValueError(f'Invalid next state: {next_state}')
        
if __name__ == '__main__':
    generator = GreaterThanTMCommandGenerator()
    # q0 test
    q0_str = 'CMD [HEAD1] RIGHT, [HEAD2] RIGHT, [OUTPUT] False, q1'
    q0_gen = generator.get_q0_cmd()
    assert q0_str == q0_gen, f'Expect {q0_str}, Got {q0_gen}'

    # q1 to q1 test case_1
    q1_str = 'CMD [HEAD1] RIGHT, [HEAD2] RIGHT, [OUTPUT] False, q1'
    q1_gen = generator.get_q1_cmd('q1', False)
    assert q1_str == q1_gen, f'Expect {q1_str}, Got {q1_gen}'

    # q1 to q1 test case_2
    q1_str = 'CMD [HEAD1] RIGHT, [HEAD2] RIGHT, q1'
    q1_gen = generator.get_q1_cmd('q1')
    assert q1_str == q1_gen, f'Expect {q1_str}, Got {q1_gen}'

    # q1 to qH test case_1
    qH_str = 'CMD [OUTPUT], qH'
    qH_gen = generator.get_q1_cmd('qH')
    assert qH_str == qH_gen, f'Expect {qH_str}, Got {qH_gen}'

    # q1 to qH test case_2
    qH_str = 'CMD [OUTPUT] False, [OUTPUT], qH'
    qH_gen = generator.get_q1_cmd('qH', False)
    assert qH_str == qH_gen, f'Expect {qH_str}, Got {qH_gen}'

