import re

r"""
Standard Pattern:
1. The first line describes the current TM stape state. Examples like:
    - REFLECTION, q0, [HEAD1] 9999[HEAD2] 1234 [OUTPUT]
    - REFLECTION, q1,  [HEAD1]9999 [HEAD2]1234 [OUTPUT]
    - REFLECTION, q1,  9[HEAD1]999 1[HEAD2]234 8[OUTPUT]
    - REFLECTION, q1,  9999[HEAD1] 1234[HEAD2] 8765[OUTPUT]
    - REFLECTION, qH,  9999[HEAD1] 1234[HEAD2] 8765
2. The second line describes the command to execute according to the current state. Examples like:
    - CMD [HEAD1] R, [HEAD2] R, q1
    - CMD [HEAD1] R, [HEAD2] R, [OUTPUT] 8, [OUTPUT] RIGHT, q1
    - CMD [HEAD1] R, [HEAD2] R, [OUTPUT] 7, [OUTPUT] RIGHT, q1
    - CMD [OUTPUT], qH
    - No command to execute. Halt state.
"""

class ReflectionTMCommandGenerator:
    def __init__(self):
        self.q0_token = 'q0'
        self.q1_token = 'q1'
        self.q2_token = 'q2'
        self.qH_token = 'qH'

        self.h1_token = '[HEAD1]'
        self.h2_token = '[HEAD2]'
        self.output_token = '[OUTPUT]'
        self.cmd_token = 'CMD'

        self.right_token = 'RIGHT'
        self.left_token = 'LEFT'

        # Machine will halt when it reaches qH, so there is no qH_cmd_template.
        self.q0_cmd_template = '{cmd_token} {h1_token} {right_token}, {h2_token} {right_token}, {q1_token}'
        self.q1_2_q1_cmd_template = '{cmd_token} {h1_act}{h2_act}{output_token} {output}, {output_token} {right_token}, {q1_token}'
        self.q1_2_q2_cmd_template = '{cmd_token} {q2_token}'
        self.q2_2_q2_cmd_template = '{cmd_token} {output_token} {left_token}, {q2_token}'
        self.q1_2_qH_cmd_template = '{cmd_token} {output_token}, {qH_token}'

    def get_q0_cmd(self):
        return self.q0_cmd_template.format(cmd_token=self.cmd_token,
                                           h1_token=self.h1_token,
                                           h2_token=self.h2_token,
                                           right_token=self.right_token,
                                           q1_token=self.q1_token)

    def get_q1_cmd(self, output, next_state, h1_r=True, h2_r=True):
        if next_state == 'q1':
            h1_act = h2_act = ''
            if h1_r:
                h1_act = f'{self.h1_token} {self.right_token}, '
            if h2_r:
                h2_act = f'{self.h2_token} {self.right_token}, '
            return self.q1_2_q1_cmd_template.format(cmd_token=self.cmd_token,
                                                    h1_act=h1_act,
                                                    h2_act=h2_act,
                                                    output_token=self.output_token,
                                                    output=output,
                                                    right_token=self.right_token,
                                                    q1_token=self.q1_token)
        elif next_state == 'q2':
            return self.q1_2_q2_cmd_template.format(cmd_token=self.cmd_token,
                                                    q2_token=self.q2_token)
        else:
            raise ValueError(f'Invalid next state: {next_state}')
        
    def get_q2_cmd(self, next_state):
        if next_state == 'q2':
            return self.q2_2_q2_cmd_template.format(cmd_token=self.cmd_token,
                                                    output_token=self.output_token,
                                                    left_token=self.left_token,
                                                    q2_token=self.q2_token)
        elif next_state == 'qH':
            return self.q1_2_qH_cmd_template.format(cmd_token=self.cmd_token,
                                                    output_token=self.output_token,
                                                    qH_token=self.qH_token)
        else:
            raise ValueError(f'Invalid next state: {next_state}')
        

if __name__ == '__main__':
    generator = ReflectionTMCommandGenerator()
    # q0 test
    q0_str = 'CMD [HEAD1] RIGHT, [HEAD2] RIGHT, q1'
    q0_gen = generator.get_q0_cmd()
    assert q0_str == q0_gen, f'Expect {q0_str}, Got {q0_gen}'

    # q1 to q1 test
    q1_str = 'CMD [HEAD1] RIGHT, [HEAD2] RIGHT, [OUTPUT] 8, [OUTPUT] RIGHT, q1'
    q1_gen = generator.get_q1_cmd(8, 'q1')
    assert q1_str == q1_gen, f'Expect {q1_str}, Got {q1_gen}'

    # q1 to qH test
    qH_str = 'CMD [OUTPUT], qH'
    qH_gen = generator.get_q1_cmd(1, 'qH')
    assert qH_str == qH_gen, f'Expect {qH_str}, Got {qH_gen}'